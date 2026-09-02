"""이미 크롤링된 400종 데이터에 move_details(위력/명중률/PP/분류/타입/설명)를 채워 넣는다.

Bulbapedia는 다시 건드리지 않는다 - PokeAPI(species+pokemon+move)만 다시 조회하면
되므로 전체 재크롤링보다 훨씬 가볍다. species_list_paldea.json과 data가 크롤링
당시 실패 없이 1:1로 정렬되어 있다는 전제로 동작한다.
"""

import json
import sys
from pathlib import Path

from crawler.http_client import RateLimitedFetcher
from crawler.pokeapi_client import (
    default_variety_name,
    extract_move_details,
    extract_move_name_ko,
    extract_moves,
)

POKEAPI_BASE = "https://pokeapi.co/api/v2"
PROJECT_ROOT = Path(__file__).parent.parent
SPECIES_LIST_PATH = Path(__file__).parent / "species_list_paldea.json"
DATA_PATH = PROJECT_ROOT / "data" / "pokedex_paldea.json"


def main() -> None:
    with open(SPECIES_LIST_PATH, encoding="utf-8") as f:
        species_list = json.load(f)
    with open(DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)

    if len(species_list) != len(data):
        print("species_list와 data 길이가 다릅니다 - 인덱스 정렬을 신뢰할 수 없어 중단합니다.")
        sys.exit(1)

    fetcher = RateLimitedFetcher(delay_seconds=0.3)
    move_names_ko: dict[str, str] = {}
    move_details_ko: dict[str, dict] = {}
    failures = []

    for i, name_en in enumerate(species_list, 1):
        try:
            species = fetcher.get_json(f"{POKEAPI_BASE}/pokemon-species/{name_en}")
            variety_name = default_variety_name(species)
            pokemon = fetcher.get_json(f"{POKEAPI_BASE}/pokemon/{variety_name}")
            moves = extract_moves(pokemon)

            all_slugs = [m["move"] for m in moves["level_up"]] + moves["machine"]
            for slug in all_slugs:
                if slug not in move_names_ko:
                    move_json = fetcher.get_json(f"{POKEAPI_BASE}/move/{slug}")
                    name_ko = extract_move_name_ko(move_json)
                    move_names_ko[slug] = name_ko
                    move_details_ko[name_ko] = extract_move_details(move_json)

            data[i - 1]["move_details"] = {
                move_names_ko[slug]: move_details_ko[move_names_ko[slug]] for slug in all_slugs
            }
            print(f"[{i}/{len(species_list)}] {name_en} 완료", flush=True)
        except Exception as e:
            print(f"[{i}/{len(species_list)}] {name_en} 실패: {e}", flush=True)
            failures.append(name_en)

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n완료. 고유 기술 {len(move_names_ko)}개 수집. 실패: {failures}")


if __name__ == "__main__":
    main()
