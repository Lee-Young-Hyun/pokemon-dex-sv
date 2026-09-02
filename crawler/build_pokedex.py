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
    extract_basic_info,
    extract_evolution_chain,
    extract_move_name_ko,
    extract_moves,
    extract_types,
)

POKEAPI_BASE = "https://pokeapi.co/api/v2"


def _bulbapedia_url(name_en: str) -> str:
    # PokeAPI 슬러그(예: "pikachu")를 Bulbapedia 문서 제목(예: "Pikachu_(Pokémon)")으로 바꾼다.
    return f"https://bulbapedia.bulbagarden.net/wiki/{name_en.capitalize()}_(Pok%C3%A9mon)"


def build_pokemon_record(name_en: str, fetcher) -> dict:
    """PokeAPI 슬러그(name_en) 하나에 대해 도감 레코드를 만든다."""
    species = fetcher.get_json(f"{POKEAPI_BASE}/pokemon-species/{name_en}")
    pokemon = fetcher.get_json(f"{POKEAPI_BASE}/pokemon/{name_en}")

    basic = extract_basic_info(species)
    types_ko = extract_types(pokemon)
    moves = extract_moves(pokemon)

    move_names_ko: dict[str, str] = {}
    for slug in [m["move"] for m in moves["level_up"]] + moves["machine"]:
        if slug not in move_names_ko:
            move_json = fetcher.get_json(f"{POKEAPI_BASE}/move/{slug}")
            move_names_ko[slug] = extract_move_name_ko(move_json)

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

    full_page_html = fetcher.get_html(_bulbapedia_url(name_en))
    table_html = find_locations_table_html(full_page_html)
    sv_locations_raw = extract_sv_locations(table_html) if table_html else {"base_game": [], "dlc": []}
    sv_locations = translate_locations(sv_locations_raw)

    return {
        "dex_number": basic["dex_number"],
        "name_ko": basic["name_ko"],
        "types": types_ko,
        "evolution": evolution_ko,
        "moves": {
            "level_up": [
                {"move": move_names_ko[m["move"]], "level": m["level"]}
                for m in moves["level_up"]
            ],
            "machine": [move_names_ko[m] for m in moves["machine"]],
        },
        "sv_locations": sv_locations,
    }
