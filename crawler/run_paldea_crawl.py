"""파르데아 도감(본편 400종)을 실제로 크롤링해서 data/pokedex_paldea.json에 저장한다.

사용법:
    python -m crawler.run_paldea_crawl              # 전체 400종
    python -m crawler.run_paldea_crawl --limit 5     # 앞 5종만 (동작 확인용)
"""

import argparse
import json
import sys
import time
from pathlib import Path

from crawler.build_pokedex import build_pokemon_record
from crawler.crawl_runner import crawl_species_list
from crawler.http_client import RateLimitedFetcher

PROJECT_ROOT = Path(__file__).parent.parent
SPECIES_LIST_PATH = Path(__file__).parent / "species_list_paldea.json"
OUTPUT_PATH = PROJECT_ROOT / "data" / "pokedex_paldea.json"
FAILURES_PATH = PROJECT_ROOT / "data" / "pokedex_paldea_failures.json"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="앞에서부터 N종만 크롤링(테스트용)")
    parser.add_argument("--delay", type=float, default=0.4, help="요청 사이 딜레이(초)")
    args = parser.parse_args()

    with open(SPECIES_LIST_PATH, encoding="utf-8") as f:
        names = json.load(f)
    if args.limit:
        names = names[: args.limit]

    fetcher = RateLimitedFetcher(delay_seconds=args.delay)
    done_count = 0
    total = len(names)
    start = time.monotonic()

    def build_and_report(name: str) -> dict:
        nonlocal done_count
        record = build_pokemon_record(name, fetcher)
        done_count += 1
        elapsed = time.monotonic() - start
        print(
            f"[{done_count}/{total}] {name} -> {record['name_ko']} "
            f"(경과 {elapsed:.0f}초)",
            flush=True,
        )
        return record

    successes, failures = crawl_species_list(names, build_and_report)

    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(successes, f, ensure_ascii=False, indent=2)
    with open(FAILURES_PATH, "w", encoding="utf-8") as f:
        json.dump(failures, f, ensure_ascii=False, indent=2)

    print(f"\n완료: 성공 {len(successes)}건, 실패 {len(failures)}건", flush=True)
    if failures:
        print("실패 목록:", [f["name"] for f in failures], flush=True)


if __name__ == "__main__":
    sys.exit(main())
