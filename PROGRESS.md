# PROGRESS.md — 포켓몬 도감(스칼렛/바이올렛) 진행 상황

마지막 업데이트: 2026-09-02 (3차)

## 현재 상태

**실제 앱이 배포되어 사용 가능합니다.**

🔗 https://lee-young-hyun.github.io/pokemon-dex-sv/app/index.html

- 파르데아 도감(본편) 400종 전체 크롤링 완료, 실패 0건
- 검색+자동완성, 상세정보(타입/진화/기술/입수처), 이미지, 기술 세부정보 툴팁까지 동작
- PWA로 등록되어 있어 모바일 브라우저에서 "홈 화면에 추가"로 앱처럼 사용 가능 (APK는 불필요하다고 판단, 미생성)
- GitHub 저장소(공개): https://github.com/Lee-Young-Hyun/pokemon-dex-sv

## 완료된 것 (기획 → 크롤러 → 실제 앱 순)

### 기획
- `PRD.md` 작성 및 확정 (DLC 포함, 기술머신 포함)
- 언어: Python(크롤러) + 순수 HTML/CSS/JS(앱)

### 크롤링 소스 (실제 검증 후 확정)
- ~~포켓몬 위키(Fandom) 한국어판~~ → Cloudflare 봇 차단으로 폐기
- ~~나무위키~~ → 입수 방법이 구조화되어 있지 않아 폐기
- **PokeAPI**: 도감번호·한글이름·타입·진화조건·기술(레벨업+TM+세부정보)·한글 기술 설명(8세대까지 공식 로컬라이징 텍스트, 세대 간 거의 안 바뀜)
- **Bulbapedia**: "Game locations" 표에서 스칼렛/바이올렛 본편+DLC 입수 지역

### 크롤러 모듈 (`pokemon-dex-sv/crawler/`, TDD, 테스트 32개 전부 통과)

| 모듈 | 내용 |
|---|---|
| `pokeapi_client.py` | 도감번호·한글이름·타입·진화조건·기술(레벨업/TM)·기술 한글명+세부정보(위력/명중/PP/분류/설명)·진화체인·기본폼(default_variety_name)·이미지URL |
| `bulbapedia_scraper.py` | "Game locations" 표 위치 찾기, 본편·DLC 지역명 추출, 메타 링크 필터링, 지역명 한글 번역 |
| `build_pokedex.py` | 위 조각 조립(오케스트레이션), Bulbapedia URL 생성(파라독스/재앙의 네 몸 예외 처리 포함), 진화 출처 한글화 |
| `http_client.py` | `RateLimitedFetcher` — 요청 간 딜레이, URL 캐시, HTTP 에러 시 예외 |
| `crawl_runner.py` | `crawl_species_list` — 하나 실패해도 계속 진행 + 실패 로그 |
| `run_paldea_crawl.py` | 파르데아 400종 전체 크롤링 실행 스크립트 |
| `repair_broken_locations.py` | 문제 있는 레코드만 재수집(전체 재크롤링 없이) |
| `backfill_move_details.py` | 기존 데이터에 기술 세부정보만 추가 수집(Bulbapedia 재요청 없이) |

### 발견하고 고친 버그들 (전부 TDD로 재현 → 수정 → 검증)
- PokeAPI 폼 포켓몬 404 (바스컬린 등) → 기본 폼(`default_variety_name`)으로 조회
- Bulbapedia 파라독스 포켓몬 URL 404 (great-tusk → Great_Tusk, 단어별 대문자화)
- 재앙의 네 몸(우행/파오젠/딩루/이유이) URL 404 → 예외 표로 처리 (진짜 하이픈 포함 이름)
- 지역폼(유노바/히스이 등) 72종의 입수정보에 메타 링크("Evolution", "Pokémon HOME" 등) 오염 → 필터링
- 진화로만 얻는 포켓몬(나로테 등)의 입수 출처가 영문 종 이름("Sprigatito에서 진화")으로 나오던 것 → 같은 레코드의 진화 정보를 재사용해 한글화("나오하에서 진화")
- 모바일 가로 스크롤 — "총 400종" 표시가 검색창 flex 줄 안에서 넘치던 게 원인, 구조 분리로 근본 해결
- 진화 체인이 화면 폭에 따라 어중간하게 줄바꿈되던 것 → 항상 세로 스택으로 고정
- 기술 세부정보 툴팁이 아예 안 열리던 버그 → `.tooltip-backdrop`에 무조건 `display:flex`를 줘서 `hidden` 속성을 무력화(항상 전체화면을 덮어 클릭을 가로챔)했던 게 원인, `:not([hidden])`으로 수정

### 실제 앱 (`pokemon-dex-sv/app/`)
- `index.html` / `style.css` / `app.js` / `data.js`(400종 데이터, 약 5MB) / `manifest.json` / `sw.js` / `icons/`
- 기능: 한글 검색+자동완성, 상세정보(타입/진화 체인/레벨업+TM 기술/입수처), 공식 아트워크 이미지, 진화 전/후 이름 클릭 이동, **기술 이름 클릭 시 위력/명중률/PP/분류/타입/한글 설명 팝업** (배경 클릭·Esc·닫기 버튼으로 닫힘)
- PWA(manifest+서비스워커) 등록 완료, GitHub Pages로 배포 중

## TODO — 아직 크롤링/반영 안 한 항목

1. **DLC(키타카미·블루베리) 신규 포켓몬** — 지금은 파르데아 본편 400종만 있음. 키타카미(200종)·블루베리(243종) 도감에서 본편과 안 겹치는 신규/복귀종은 아직 크롤링 안 함 (합치면 약 264종 추가, 시간이 오래 걸려서 이번엔 본편만 먼저 하기로 결정했었음).
2. **DLC 세부 지역명 한글 번역** — Kitakami Road, Apple Hills, Oni Mountain 등 키타카미 지역명이 아직 영문. 공식 한글 명칭을 확신할 수 없어 의도적으로 미번역 상태(틀린 이름을 넣는 것보다 안전하다고 판단).
3. **진화 아이템 한글명 매핑 확장** — 기본 스톤류(번개의돌 등) 10개만 등록됨. 그 외 특수 진화 아이템(용의비늘, 사랑스러운부적, 왕의징표 등)은 매핑에 없어 영문 그대로 노출될 수 있음.
4. **폼 체인지 변형** — 로토무(가전제품 폼), 알크레미(맛 종류), 비비용(무늬) 등은 기본 폼만 크롤링됨. 대체 폼 정보는 없음.
5. **스탯(종족값)·특성(어빌리티)·알 기술** — PRD상 P2(향후 고려사항)로 분류되어 애초에 이번 범위 밖.

## 재개하는 방법

```
PROGRESS.md 보고 이어서 하자. [TODO 항목]부터 시작해줘.
```

테스트 실행 확인:
```bash
cd pokemon-dex-sv
python -m pytest crawler/ -v
```

앱 재배포(데이터 갱신 후):
```bash
git add -A && git commit -m "..." && git push origin main
```
GitHub Pages가 자동으로 다시 빌드합니다(보통 1~2분).
