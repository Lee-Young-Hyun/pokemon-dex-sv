# PROGRESS.md — 포켓몬 도감(스칼렛/바이올렛) 진행 상황

마지막 업데이트: 2026-09-02 (2차)

## 지금까지 완료된 것

### 기획
- `PRD.md` 작성 및 확정 (Open Questions 해소: DLC 포함, 기술머신 포함)
- 선정 기능: **초기 데이터 수집 스크립트(크롤링)** — 트랙1(가벼운 TDD)로 진행 중
- 언어: Python으로 통일

### 크롤링 소스 (실제 검증 후 확정)
- ~~포켓몬 위키(Fandom) 한국어판~~ → Cloudflare 봇 차단으로 접근 불가, 폐기
- ~~나무위키~~ → 접근은 되지만 "입수 방법"이 구조화되어 있지 않음(스토리/트리비아 위주), 폐기
- **PokeAPI**: 도감번호·한글이름·타입·진화조건·기술(레벨업+TM) — 구조화된 JSON, 안정적
- **Bulbapedia**: "Game locations" 표에서 스칼렛/바이올렛 본편+DLC 입수 지역 — 접근·구조 모두 확인됨

### 구현 (TDD, 테스트 15개 전부 통과)
프로젝트 위치: `pokemon-dex-sv/` (C4P 폴더 하위, 별도 git 저장소, 브랜치 `main`)

| 모듈 | 내용 |
|---|---|
| `crawler/pokeapi_client.py` | 도감번호·한글이름·타입·진화조건·기술(레벨업/TM)·기술한글명·진화체인 펼치기 |
| `crawler/bulbapedia_scraper.py` | 페이지에서 "Game locations" 표 찾기 + 스칼렛/바이올렛 본편·DLC 지역명 추출 |
| `crawler/http_client.py` | `RateLimitedFetcher` — 요청 간 딜레이, HTTP 에러 시 예외 |
| `crawler/crawl_runner.py` | `crawl_species_list` — 하나 실패해도 계속 진행 + 실패 로그 |
| `crawler/build_pokedex.py` | 위 조각을 조립하는 오케스트레이션 (자체 단위테스트는 없음, 대신 실제 네트워크로 종단간 검증) |

### 종단간 검증
피카츄 1마리를 실제 PokeAPI + Bulbapedia로 크롤링해서 `data/pikachu.json`(gitignore 처리, 로컬에만 있음) 생성 확인:
- 타입/진화/레벨업기술(20개)/TM기술(47개) 모두 한글로 정상 추출됨
- 스칼렛/바이올렛 본편 지역 8개, DLC 지역 7개 정상 구분 추출됨
- **단, 지역명(South Province 등)과 아이템명(thunder-stone 등)은 아직 영문** — 다음 작업

## 2차 세션에서 완료된 것

1. **지역명·아이템명 한글 번역 매핑** ✅ — 팔데아 본편 지역명(남부/동부/서부지방, 아르타존 등)·진화 아이템명(번개의돌 등) 번역. DLC(키타카미) 세부 지역명은 확신 없어 영문 유지(의도적).
2. **파르데아 도감 전체 목록 확보 + 전체 순회 실행** ✅ — PokeAPI `paldea` 도감(400종)에서 목록 확보, `crawl_species_list`로 전체 실행. `data/pokedex_paldea.json`에 저장 (gitignore 처리, 로컬에만 존재 — 필요시 `python -m crawler.run_paldea_crawl`로 재생성).
   - **400/400 성공, 실패 0건.** 실행 중 발견한 버그들:
     - PokeAPI 폼 포켓몬 404 (바스컬린 등) → `default_variety_name`으로 수정
     - Bulbapedia 파라독스 포켓몬 URL 404 (great-tusk → Great_Tusk) → 단어별 대문자화로 수정
     - 재앙의 네 몸(우행/파오젠/딩루/이유이) URL 404 → `BULBAPEDIA_TITLE_OVERRIDES` 예외 처리
     - 지역폼(유노바/히스이 등) 포켓몬 72종의 입수정보에 메타 링크("Evolution", "Pokémon HOME" 등) 오염 → `NON_LOCATION_TITLES` 필터로 수정, `repair_broken_locations.py`로 전체 재크롤링 없이 해당 72종만 다시 받아서 복구
3. **엔지니어링 open question 검증** ✅ — 위 폼 체인지/예외 케이스들이 실제로 파서를 깼음을 확인, 전부 TDD로 수정 완료 (테스트 28개)

## 이번 세션에서 새로 추가된 범위 (PRD에 없던 요청)

- **실제 앱 구현**: `app/` 폴더에 검색+자동완성+상세정보(타입/진화/기술/입수처) 웹앱 완성 (index.html/style.css/app.js/data.js). 이미지 표시(공식 아트워크 URL 직접 연결), 진화 전/후 클릭 이동 지원.
- **모바일(APK) 요청**: 사용자가 갤럭시 S25에서 쓸 APK를 요청 → PWA→APK 변환 방식으로 진행 합의. `manifest.json`, `sw.js`, 아이콘까지 준비 완료. **다음 단계(GitHub Pages 호스팅)는 저장소를 공개로 전환/공개 URL 노출이 필요해 사용자 확인 대기 중.**

## 아직 안 한 것 (우선순위 순)

1. **GitHub Pages 호스팅 + PWABuilder로 APK 변환** — 사용자 확인 필요 (공개 호스팅 동의 여부)
2. **실제 앱을 브라우저에서 시각적으로 직접 확인** — 이 세션엔 브라우저 자동화 도구가 없어 코드 검토로만 검증함, 사용자가 직접 열어서 확인 권장

## 재개하는 방법

```
어제 하다 만거 진행해줘. PROGRESS.md 보고 이어서 하자.
```

또는 특정 항목 지정:
```
PROGRESS.md 보고 이어서 하자. 지역명 한글 번역 매핑부터 시작해줘.
```

테스트 실행 확인:
```bash
cd pokemon-dex-sv
python -m pytest crawler/ -v
```
