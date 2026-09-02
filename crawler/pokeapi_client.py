"""PokeAPI에서 받아온 JSON을 도감 레코드에 필요한 필드로 변환하는 함수들."""

# PokeAPI 타입 이름(영문)은 18종으로 고정되어 있어 정적 매핑으로 처리한다.
TYPE_NAME_KO = {
    "normal": "노말",
    "fire": "불꽃",
    "water": "물",
    "electric": "전기",
    "grass": "풀",
    "ice": "얼음",
    "fighting": "격투",
    "poison": "독",
    "ground": "땅",
    "flying": "비행",
    "psychic": "에스퍼",
    "bug": "벌레",
    "rock": "바위",
    "ghost": "고스트",
    "dragon": "드래곤",
    "dark": "악",
    "steel": "강철",
    "fairy": "페어리",
}

# 확인된 진화 아이템명만 담는다. 매핑 표에 없는 아이템은 영문 슬러그를 그대로 남긴다.
EVOLUTION_ITEM_NAME_KO = {
    "thunder-stone": "번개의돌",
    "fire-stone": "불꽃의돌",
    "water-stone": "물의돌",
    "leaf-stone": "리프의돌",
    "moon-stone": "달의돌",
    "sun-stone": "태양의돌",
    "shiny-stone": "빛의돌",
    "dusk-stone": "어둠의돌",
    "dawn-stone": "각성의돌",
    "ice-stone": "얼음의돌",
}


def _korean_name(names: list[dict]) -> str:
    """PokeAPI의 names 배열(species/move 등 공통 형태)에서 한글 이름을 뽑는다."""
    return next(n["name"] for n in names if n["language"]["name"] == "ko")


def extract_basic_info(species_data: dict) -> dict:
    """species 엔드포인트 JSON에서 도감번호와 한글 이름을 추출한다."""
    return {
        "dex_number": species_data["id"],
        "name_ko": _korean_name(species_data["names"]),
    }


def extract_move_name_ko(move_data: dict) -> str:
    """move 엔드포인트 JSON에서 한글 기술 이름을 추출한다."""
    return _korean_name(move_data["names"])


def extract_evolution_chain(chain_data: dict) -> list[dict]:
    """evolution-chain 엔드포인트 JSON을 (이전 종 -> 다음 종, 조건) 간선 리스트로 펼친다.

    종 이름은 아직 영문 슬러그(예: "pikachu")다. 한글 이름으로 바꾸는 건
    각 종의 species 데이터가 필요하므로 이 함수의 책임 밖이다 (오케스트레이션에서 처리).
    """
    edges = []

    def walk(node: dict) -> None:
        from_species = node["species"]["name"]
        for child in node["evolves_to"]:
            to_species = child["species"]["name"]
            detail = child["evolution_details"][0]
            edges.append(
                {
                    "from": from_species,
                    "to": to_species,
                    "condition": format_evolution_condition(detail),
                }
            )
            walk(child)

    walk(chain_data["chain"])
    return edges


def extract_types(pokemon_data: dict) -> list[str]:
    """pokemon 엔드포인트 JSON에서 타입을 slot 순서대로 한글 이름 리스트로 추출한다."""
    sorted_types = sorted(pokemon_data["types"], key=lambda t: t["slot"])
    return [TYPE_NAME_KO[t["type"]["name"]] for t in sorted_types]


def format_evolution_condition(detail: dict) -> str:
    """evolution_details 항목 하나를 사람이 읽을 수 있는 한글 조건 문장으로 변환한다."""
    trigger = detail["trigger"]["name"]

    if detail.get("min_happiness") is not None:
        return f"친밀도 {detail['min_happiness']} 이상"
    if detail.get("min_level") is not None:
        return f"레벨 {detail['min_level']} 이상"
    if trigger == "use-item" and detail.get("item"):
        item_name = detail["item"]["name"]
        item_name_ko = EVOLUTION_ITEM_NAME_KO.get(item_name, item_name)
        return f"아이템({item_name_ko}) 사용"

    return "조건 불명"


def extract_moves(pokemon_data: dict, version_group: str = "scarlet-violet") -> dict:
    """pokemon 엔드포인트 JSON에서 지정한 버전 그룹의 기술을 학습 방법별로 나눠 추출한다.

    반환값:
        level_up: [{"move": 기술영문슬러그, "level": 레벨}, ...] (레벨 오름차순)
        machine: [기술영문슬러그, ...] (이름순, 기술머신으로 배우는 기술)
    """
    level_up = []
    machine = set()

    for move_entry in pokemon_data["moves"]:
        move_name = move_entry["move"]["name"]
        for vgd in move_entry["version_group_details"]:
            if vgd["version_group"]["name"] != version_group:
                continue
            method = vgd["move_learn_method"]["name"]
            if method == "level-up":
                level_up.append({"move": move_name, "level": vgd["level_learned_at"]})
            elif method == "machine":
                machine.add(move_name)

    level_up.sort(key=lambda m: m["level"])
    return {"level_up": level_up, "machine": sorted(machine)}
