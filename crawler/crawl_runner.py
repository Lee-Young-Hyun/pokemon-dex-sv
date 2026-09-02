"""여러 포켓몬을 순회하며 크롤링하되, 하나가 실패해도 전체가 죽지 않고 계속 진행한다."""


def crawl_species_list(names: list[str], build_fn) -> tuple[list[dict], list[dict]]:
    """names를 순서대로 build_fn(name)에 넘겨 레코드를 만든다.

    build_fn이 예외를 던지면 그 이름은 실패 목록에 사유와 함께 남기고, 나머지는 계속 진행한다.
    반환값: (성공한 레코드 리스트, 실패 목록[{"name":..., "error":...}])
    """
    successes = []
    failures = []

    for name in names:
        try:
            successes.append(build_fn(name))
        except Exception as e:
            failures.append({"name": name, "error": str(e)})

    return successes, failures
