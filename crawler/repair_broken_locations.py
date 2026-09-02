"""전체 재크롤링 없이, sv_locations에 메타 링크가 섞인 깨진 레코드만 다시 받아온다.

species_list_paldea.json과 data/pokedex_paldea.json이 크롤링 당시 실패 없이
1:1로 정렬되어 있다는 전제(둘 다 400개, 순서 동일)로 동작한다.
"""

import json
import sys
from pathlib import Path

from crawler.build_pokedex import build_pokemon_record
from crawler.http_client import RateLimitedFetcher

PROJECT_ROOT = Path(__file__).parent.parent
SPECIES_LIST_PATH = Path(__file__).parent / "species_list_paldea.json"
DATA_PATH = PROJECT_ROOT / "data" / "pokedex_paldea.json"

SUSPICIOUS_KEYWORDS = [
    "Evolution",
    "Pokémon HOME",
    "Pokémon Legends",
    "(type)",
    "Form )",
    "Form)",
    "Evolve ",
]


def _is_english_evolve_from(loc: str) -> bool:
    # "Sprigatito에서 진화"처럼 접두어가 한글이 아니면(영문 종 이름 그대로 남았으면) 의심.
    if not loc.endswith("에서 진화"):
        return False
    prefix = loc[: -len("에서 진화")]
    return not any("가" <= ch <= "힣" for ch in prefix)  # 한글 완성형 범위


def is_suspicious(record: dict) -> bool:
    all_locs = record["sv_locations"]["base_game"] + record["sv_locations"]["dlc"]
    if any(kw in loc for loc in all_locs for kw in SUSPICIOUS_KEYWORDS):
        return True
    return any(_is_english_evolve_from(loc) for loc in all_locs)


def main() -> None:
    with open(SPECIES_LIST_PATH, encoding="utf-8") as f:
        species_list = json.load(f)
    with open(DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)

    if len(species_list) != len(data):
        print("species_list와 data 길이가 다릅니다 - 인덱스 정렬을 신뢰할 수 없어 중단합니다.")
        sys.exit(1)

    broken_indices = [i for i, r in enumerate(data) if is_suspicious(r)]
    print(f"깨진 레코드 {len(broken_indices)}개 발견, 다시 받아옵니다.")

    fetcher = RateLimitedFetcher(delay_seconds=0.35)
    fixed, still_broken = 0, []

    for n, i in enumerate(broken_indices, 1):
        name_en = species_list[i]
        try:
            new_record = build_pokemon_record(name_en, fetcher)
        except Exception as e:
            print(f"[{n}/{len(broken_indices)}] {name_en} 재수집 실패: {e}", flush=True)
            still_broken.append(name_en)
            continue

        if is_suspicious(new_record):
            print(f"[{n}/{len(broken_indices)}] {name_en} -> {new_record['name_ko']} (여전히 의심스러움)", flush=True)
            still_broken.append(name_en)
        else:
            print(f"[{n}/{len(broken_indices)}] {name_en} -> {new_record['name_ko']} (수정됨)", flush=True)
            fixed += 1

        data[i] = new_record

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n완료: {fixed}개 수정, {len(still_broken)}개는 여전히 의심스러움: {still_broken}")


if __name__ == "__main__":
    main()
