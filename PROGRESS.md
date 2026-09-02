# PROGRESS.md — 포켓몬 도감(스칼렛/바이올렛) 진행 상황

마지막 업데이트: 2026-09-02

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

## 아직 안 한 것 (우선순위 순)

1. **지역명·아이템명 한글 번역 매핑** ← 지금 시작하는 작업
   - Bulbapedia 지역명(팔데아/키타카미/블루베리, 개수 한정) 영→한 매핑 테이블
   - 진화 아이템명(thunder-stone 등) 영→한 매핑 테이블
2. **파르데아 도감 전체 목록 확보 + 전체 순회 실행**
   - PokeAPI pokedex 엔드포인트에서 전체 목록(DLC 포함) 가져오기
   - `crawl_species_list`로 전체 실행 → 결과를 JSON/CSV로 저장 (PRD 요구사항 3,4)
3. **엔지니어링 open question 실제 검증**
   - 폼 체인지 포켓몬 등 예외 케이스가 실제로 파서를 깨는지 확인, 필요하면 예외 처리 보강

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
