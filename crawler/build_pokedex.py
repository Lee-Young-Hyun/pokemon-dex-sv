"""여러 조각(PokeAPI, Bulbapedia)에서 뽑아낸 정보를 포켓몬 1마리의 최종 레코드로 합친다.

이 파일은 이미 테스트된 순수 함수들(pokeapi_client, bulbapedia_scraper)을 조립하는
얇은 오케스트레이션 계층이라 자체 단위 테스트는 없다. 대신 실제 네트워크를 통해
피카츄 1마리를 종단간으로 돌려서 결과물을 직접 확인하는 방식으로 검증한다.
"""

from crawler.bulbapedia_scraper import (
    extract_sv_locations,
    find_locations_table_html,
    translate_locations,
)
from crawler.pokeapi_client import (
    default_variety_name,
    extract_basic_info,
    extract_evolution_chain,
    extract_image_url,
    extract_move_details,
    extract_move_name_ko,
    extract_moves,
    extract_types,
)

POKEAPI_BASE = "https://pokeapi.co/api/v2"

# PokeAPI 슬러그의 하이픈은 보통 "단어 구분"(예: "great-tusk" -> "Great Tusk")이지만,
# 재앙의 네 몸(우행/파오젠/딩루/이유이)처럼 영문 이름 자체에 진짜 하이픈이 있는
# 경우도 있다 - 이런 예외만 따로 표로 관리한다.
BULBAPEDIA_TITLE_OVERRIDES = {
    "wo-chien": "Wo-Chien",
    "chien-pao": "Chien-Pao",
    "ting-lu": "Ting-Lu",
    "chi-yu": "Chi-Yu",
}


def bulbapedia_url(name_en: str) -> str:
    """PokeAPI 슬러그를 Bulbapedia 문서 제목으로 바꾼다.

    한 단어(예: "pikachu")면 "Pikachu_(Pokémon)". 여러 단어가 하이픈으로
    이어진 이름(파라독스 포켓몬 등, 예: "great-tusk")은 단어마다 대문자로
    시작하고 밑줄로 이어 "Great_Tusk_(Pokémon)"가 된다 - 앞글자만 대문자로 바꾸면
    "Great-tusk"가 되어 실제 Bulbapedia 문서를 찾지 못한다.
    """
    if name_en in BULBAPEDIA_TITLE_OVERRIDES:
        title = BULBAPEDIA_TITLE_OVERRIDES[name_en]
    else:
        words = name_en.split("-")
        title = "_".join(w.capitalize() for w in words)
    return f"https://bulbapedia.bulbagarden.net/wiki/{title}_(Pok%C3%A9mon)"


def localize_evolve_from(locations: dict, pre_evolution_ko: str | None) -> dict:
    """"<영문 종 이름>에서 진화" 형태의 문자열을 한글 이름으로 바꾼다.

    bulbapedia_scraper는 Bulbapedia 문서에 적힌 영문 이름을 그대로 쓰므로,
    이미 같은 포켓몬의 진화 정보에서 알아낸 한글 이름(pre_evolution_ko)으로 치환한다.
    pre_evolution_ko를 모르면(None) 원문을 그대로 둔다.
    """

    def fix(loc: str) -> str:
        if pre_evolution_ko and loc.endswith("에서 진화"):
            return f"{pre_evolution_ko}에서 진화"
        return loc

    return {
        "base_game": [fix(l) for l in locations["base_game"]],
        "dlc": [fix(l) for l in locations["dlc"]],
    }


def build_pokemon_record(name_en: str, fetcher) -> dict:
    """PokeAPI 슬러그(name_en) 하나에 대해 도감 레코드를 만든다."""
    species = fetcher.get_json(f"{POKEAPI_BASE}/pokemon-species/{name_en}")
    # 도감 종 이름 그대로는 /pokemon/ 리소스가 없는 경우(바스컬린 등 폼이 있는 종)가 있어,
    # species가 가리키는 기본 폼 이름을 실제로 사용한다.
    variety_name = default_variety_name(species)
    pokemon = fetcher.get_json(f"{POKEAPI_BASE}/pokemon/{variety_name}")

    basic = extract_basic_info(species)
    types_ko = extract_types(pokemon)
    moves = extract_moves(pokemon)
    image_url = extract_image_url(pokemon)

    move_names_ko: dict[str, str] = {}
    move_details_ko: dict[str, dict] = {}  # 한글 기술명 -> 위력/명중/PP/분류/타입/설명
    for slug in [m["move"] for m in moves["level_up"]] + moves["machine"]:
        if slug not in move_names_ko:
            move_json = fetcher.get_json(f"{POKEAPI_BASE}/move/{slug}")
            name_ko = extract_move_name_ko(move_json)
            move_names_ko[slug] = name_ko
            move_details_ko[name_ko] = extract_move_details(move_json)

    evolution_chain_data = fetcher.get_json(species["evolution_chain"]["url"])
    raw_edges = extract_evolution_chain(evolution_chain_data)

    species_name_ko_cache = {name_en: basic["name_ko"]}

    def species_name_ko(slug: str) -> str:
        if slug not in species_name_ko_cache:
            sp = fetcher.get_json(f"{POKEAPI_BASE}/pokemon-species/{slug}")
            species_name_ko_cache[slug] = extract_basic_info(sp)["name_ko"]
        return species_name_ko_cache[slug]

    evolution_ko = [
        {
            "from": species_name_ko(edge["from"]),
            "to": species_name_ko(edge["to"]),
            "condition": edge["condition"],
        }
        for edge in raw_edges
    ]

    full_page_html = fetcher.get_html(bulbapedia_url(name_en))
    table_html = find_locations_table_html(full_page_html)
    sv_locations_raw = extract_sv_locations(table_html) if table_html else {"base_game": [], "dlc": []}
    sv_locations = translate_locations(sv_locations_raw)

    # sv_locations에 "<영문 종 이름>에서 진화"가 있으면, 바로 이 종의 직전 진화형
    # 한글 이름(이미 위에서 알아냈다)으로 바꾼다.
    pre_evolution_ko = next(
        (species_name_ko(edge["from"]) for edge in raw_edges if edge["to"] == name_en), None
    )
    sv_locations = localize_evolve_from(sv_locations, pre_evolution_ko)

    return {
        "dex_number": basic["dex_number"],
        "name_ko": basic["name_ko"],
        "image_url": image_url,
        "types": types_ko,
        "evolution": evolution_ko,
        "moves": {
            "level_up": [
                {"move": move_names_ko[m["move"]], "level": m["level"]}
                for m in moves["level_up"]
            ],
            "machine": [move_names_ko[m] for m in moves["machine"]],
        },
        "move_details": move_details_ko,
        "sv_locations": sv_locations,
    }
