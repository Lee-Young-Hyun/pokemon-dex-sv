from pathlib import Path

from crawler.bulbapedia_scraper import find_locations_table_html, extract_sv_locations

FIXTURES = Path(__file__).parent / "fixtures"


def test_find_locations_table_html_locates_table_inside_full_page():
    table_html = (FIXTURES / "bulbapedia_pikachu_locations_table.html").read_text(encoding="utf-8")
    full_page_html = f"""
    <html><body>
    <h1>Pikachu</h1>
    <p>이 포켓몬과 관련 없는 다른 섹션 내용...</p>
    <table class="roundy"><tr><td>관련 없는 다른 표</td></tr></table>
    <h2>Game locations</h2>
    {table_html}
    <p>표 다음에 이어지는 다른 섹션...</p>
    </body></html>
    """

    found = find_locations_table_html(full_page_html)

    assert found is not None
    # 찾은 표를 그대로 extract_sv_locations에 넣었을 때 기존 결과와 동일해야 한다
    result = extract_sv_locations(found)
    assert result["base_game"][0] == "South Province (Area Two)"
    assert "Kitakami Road" in result["dlc"]


def test_find_locations_table_html_returns_none_when_not_present():
    full_page_html = "<html><body><p>스칼렛/바이올렛과 무관한 페이지</p></body></html>"

    assert find_locations_table_html(full_page_html) is None
