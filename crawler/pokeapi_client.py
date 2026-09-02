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


def extract_basic_info(species_data: dict) -> dict:
    """species 엔드포인트 JSON에서 도감번호와 한글 이름을 추출한다."""
    name_ko = next(
        n["name"] for n in species_data["names"] if n["language"]["name"] == "ko"
    )
    return {
        "dex_number": species_data["id"],
        "name_ko": name_ko,
    }


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
        return f"아이템({detail['item']['name']}) 사용"

    return "조건 불명"
