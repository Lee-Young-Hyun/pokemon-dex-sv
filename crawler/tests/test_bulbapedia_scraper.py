from pathlib import Path

from crawler.bulbapedia_scraper import extract_sv_locations, translate_locations

FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture_html(filename: str) -> str:
    with open(FIXTURES / filename, encoding="utf-8") as f:
        return f.read()


def test_extract_sv_locations_splits_base_game_and_dlc():
    table_html = load_fixture_html("bulbapedia_pikachu_locations_table.html")

    result = extract_sv_locations(table_html)

    assert result["base_game"] == [
        "South Province (Area Two)",
        "South Province (Area Four)",
        "Artazon",
        "East Province (Area One)",
        "West Province (Area Three)",
        "Tera Raid Battle",
        "List of 2★ Tera Raid Battles (Paldea)",
        "List of 3★ Tera Raid Battles (Paldea)",
    ]
    assert result["dlc"] == [
        "Kitakami Road",
        "Apple Hills",
        "Oni Mountain",
        "Wistful Fields",
        "Paradise Barrens",
        "Kitakami Wilds",
        "Timeless Woods",
    ]
    # 이 포켓몬과 무관한 다른 게임(Legends: Z-A 등) 정보는 섞이지 않는다
    assert "Vert Sector 8" not in result["base_game"]
    assert "Vert Sector 8" not in result["dlc"]


def test_extract_sv_locations_recognizes_evolve_only_acquisition():
    # 나로테(floragato)처럼 야생에 없고 진화로만 얻는 포켓몬은
    # 표 안에 지역명이 아니라 "Evolve <이전 진화형>" 문장이 들어있다.
    table_html = load_fixture_html("bulbapedia_floragato_locations_table.html")

    result = extract_sv_locations(table_html)

    assert result["base_game"] == ["Sprigatito에서 진화"]
    assert result["dlc"] == []


def test_translate_locations_converts_known_names_to_korean():
    raw = {
        "base_game": ["South Province (Area Two)", "Artazon", "Tera Raid Battle"],
        "dlc": ["Kitakami Road"],  # 매핑 표에 없는 이름 -> 번역 실패해도 원문 유지
    }

    result = translate_locations(raw)

    assert result == {
        "base_game": ["남부지방 2번 구역", "아르타존", "테라레이드 배틀"],
        "dlc": ["Kitakami Road"],
    }
