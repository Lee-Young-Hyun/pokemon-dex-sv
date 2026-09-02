"""Bulbapedia 포켓몬 페이지의 'Game locations' 표에서 스칼렛/바이올렛 입수 방법을 추출한다."""

from bs4 import BeautifulSoup

# 표의 각 행은 <th>(게임 제목) 뒤에 <td>(지역 목록)가 온다.
# th가 여러 개 연속으로 나오다 td 하나로 묶이는 경우(스칼렛/바이올렛에서 동일 지역)와
# th 하나(colspan=2)에 td 하나가 바로 오는 경우(DLC 등) 둘 다 있어, "보류 중인 제목 목록"을
# 유지하다가 td를 만나면 한꺼번에 소비하는 방식으로 처리한다.
BASE_GAME_TITLE = "Pokémon Scarlet and Violet"
DLC_TITLE = "The Hidden Treasure of Area Zero"

# 확인된(자신 있는) 지역명·명칭만 담는다. DLC(키타카미) 세부 지역명처럼 공식 한글 명칭을
# 확신할 수 없는 이름은 표에 넣지 않고 원문(영문)을 그대로 둔다 - 틀린 이름을 사실처럼
# 내보내는 것보다, 확인 전까지 영문으로 남겨두는 쪽이 안전하다.
LOCATION_NAME_KO = {
    "South Province (Area Two)": "남부지방 2번 구역",
    "South Province (Area Four)": "남부지방 4번 구역",
    "East Province (Area One)": "동부지방 1번 구역",
    "West Province (Area Three)": "서부지방 3번 구역",
    "Artazon": "아르타존",
    "Tera Raid Battle": "테라레이드 배틀",
    "List of 2★ Tera Raid Battles (Paldea)": "테라레이드 배틀(2성)",
    "List of 3★ Tera Raid Battles (Paldea)": "테라레이드 배틀(3성)",
}


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


def translate_locations(locations: dict) -> dict:
    """extract_sv_locations 결과의 영문 지역명을 한글로 바꾼다.

    매핑 표(LOCATION_NAME_KO)에 없는 이름은 번역하지 않고 원문을 그대로 남긴다.
    """
    return {
        "base_game": [LOCATION_NAME_KO.get(name, name) for name in locations["base_game"]],
        "dlc": [LOCATION_NAME_KO.get(name, name) for name in locations["dlc"]],
    }
