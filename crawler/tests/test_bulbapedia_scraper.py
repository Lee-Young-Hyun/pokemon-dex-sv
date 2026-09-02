from pathlib import Path

from crawler.bulbapedia_scraper import extract_sv_locations

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
