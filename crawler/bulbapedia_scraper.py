"""Bulbapedia 포켓몬 페이지의 'Game locations' 표에서 스칼렛/바이올렛 입수 방법을 추출한다."""

from bs4 import BeautifulSoup

# 표의 각 행은 <th>(게임 제목) 뒤에 <td>(지역 목록)가 온다.
# th가 여러 개 연속으로 나오다 td 하나로 묶이는 경우(스칼렛/바이올렛에서 동일 지역)와
# th 하나(colspan=2)에 td 하나가 바로 오는 경우(DLC 등) 둘 다 있어, "보류 중인 제목 목록"을
# 유지하다가 td를 만나면 한꺼번에 소비하는 방식으로 처리한다.
BASE_GAME_TITLE = "Pokémon Scarlet and Violet"
DLC_TITLE = "The Hidden Treasure of Area Zero"


def find_locations_table_html(full_page_html: str) -> str | None:
    """Bulbapedia 포켓몬 페이지 전체 HTML에서 'Game locations' 표를 찾아 그 부분만 반환한다.

    스칼렛/바이올렛 헤더(<a title="Pokémon Scarlet and Violet">)를 기준으로,
    그 헤더를 담고 있는 가장 가까운 <table> 조상을 찾는다. 없으면 None.
    """
    soup = BeautifulSoup(full_page_html, "html.parser")
    header_link = soup.find("a", title=BASE_GAME_TITLE)
    if header_link is None:
        return None

    table = header_link.find_parent("table")
    if table is None:
        return None

    return str(table)


def extract_sv_locations(table_html: str) -> dict:
    """'Game locations' 표 HTML에서 스칼렛/바이올렛 본편·DLC 지역명 목록을 추출한다.

    반환값: {"base_game": [지역명, ...], "dlc": [지역명, ...]}
    다른 게임(포켓몬 레전드 Z-A 등) 행은 무시된다.
    """
    soup = BeautifulSoup(table_html, "html.parser")
    table = soup.find("table")
    # html.parser는 <table><tr>를 자동으로 <table><tbody><tr>로 보정하므로,
    # tr을 찾을 실제 루트(tbody가 있으면 tbody, 없으면 table 자신)를 먼저 정한다.
    row_root = table.find("tbody", recursive=False) or table

    result = {"base_game": [], "dlc": []}
    pending_titles: list[str] = []

    for tr in row_root.find_all("tr", recursive=False):
        for el in tr.find_all(["th", "td"], recursive=False):
            if el.name == "th":
                link = el.find("a")
                title = link["title"] if link else el.get_text(strip=True)
                pending_titles.append(title)
                continue

            locations = [a["title"] for a in el.find_all("a") if a.get("title")]
            # 스칼렛/바이올렛처럼 th가 여러 개(Scarlet, Violet)라도 같은 제목을 가리키면
            # 지역 목록은 한 번만 반영한다 (중복 방지).
            for title in set(pending_titles):
                if title == BASE_GAME_TITLE:
                    result["base_game"].extend(locations)
                elif title == DLC_TITLE:
                    result["dlc"].extend(locations)
            pending_titles = []

    return result
