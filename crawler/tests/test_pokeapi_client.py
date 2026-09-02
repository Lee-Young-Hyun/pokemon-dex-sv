import json
from pathlib import Path

from crawler.pokeapi_client import (
    extract_basic_info,
    extract_types,
    format_evolution_condition,
    extract_moves,
    extract_move_name_ko,
    extract_evolution_chain,
)

FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(filename: str) -> dict:
    with open(FIXTURES / filename, encoding="utf-8") as f:
        return json.load(f)


def test_extract_basic_info_returns_korean_name_and_dex_number():
    species_data = load_fixture("pikachu_species.json")

    result = extract_basic_info(species_data)

    assert result["dex_number"] == 25
    assert result["name_ko"] == "피카츄"


def test_extract_types_returns_korean_type_names_in_order():
    pokemon_data = load_fixture("pikachu_pokemon.json")

    result = extract_types(pokemon_data)

    assert result == ["전기"]


def test_format_evolution_condition_for_level_up():
    detail = {"trigger": {"name": "level-up"}, "min_level": 16, "min_happiness": None, "item": None}

    assert format_evolution_condition(detail) == "레벨 16 이상"


def test_format_evolution_condition_for_friendship():
    detail = {"trigger": {"name": "level-up"}, "min_level": None, "min_happiness": 220, "item": None}

    assert format_evolution_condition(detail) == "친밀도 220 이상"


def test_format_evolution_condition_for_item_use():
    detail = {
        "trigger": {"name": "use-item"},
        "min_level": None,
        "min_happiness": None,
        "item": {"name": "thunder-stone"},
    }

    assert format_evolution_condition(detail) == "아이템(번개의돌) 사용"


def test_format_evolution_condition_for_unknown_item_keeps_english_name():
    detail = {
        "trigger": {"name": "use-item"},
        "min_level": None,
        "min_happiness": None,
        "item": {"name": "some-未知-item"},
    }

    # 매핑 표에 없는 아이템은 번역 실패해도 원문 이름을 그대로 보여준다
    assert format_evolution_condition(detail) == "아이템(some-未知-item) 사용"


def test_extract_moves_splits_level_up_and_machine_for_scarlet_violet():
    pokemon_data = load_fixture("pikachu_pokemon.json")

    result = extract_moves(pokemon_data, version_group="scarlet-violet")

    # 레벨업 기술은 레벨 오름차순으로 정렬되고, 레벨 1 기술이 여럿 포함된다
    assert result["level_up"][0] == {"move": "tail-whip", "level": 1}
    assert all(
        result["level_up"][i]["level"] <= result["level_up"][i + 1]["level"]
        for i in range(len(result["level_up"]) - 1)
    )
    assert len(result["level_up"]) == 20

    # 기술머신 기술은 이름순으로 정렬된 문자열 리스트
    assert result["machine"][0] == "agility"
    assert "thunderbolt" in result["machine"]
    assert len(result["machine"]) == 47


def test_extract_move_name_ko_returns_korean_move_name():
    move_data = load_fixture("move_thunderbolt.json")

    assert extract_move_name_ko(move_data) == "10만볼트"


def test_extract_evolution_chain_returns_ordered_edges_with_conditions():
    chain_data = load_fixture("evolution_chain_10.json")

    edges = extract_evolution_chain(chain_data)

    assert edges == [
        {"from": "pichu", "to": "pikachu", "condition": "친밀도 220 이상"},
        {"from": "pikachu", "to": "raichu", "condition": "아이템(번개의돌) 사용"},
    ]
