import json
from pathlib import Path

from crawler.pokeapi_client import (
    extract_basic_info,
    extract_types,
    format_evolution_condition,
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

    assert format_evolution_condition(detail) == "아이템(thunder-stone) 사용"
