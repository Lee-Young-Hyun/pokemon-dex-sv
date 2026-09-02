from crawler.crawl_runner import crawl_species_list


def test_crawl_species_list_continues_after_a_failure_and_logs_it():
    def build_fn(name: str) -> dict:
        if name == "bad-species":
            raise ValueError("페이지 구조가 예상과 다름")
        return {"name": name}

    successes, failures = crawl_species_list(
        ["pikachu", "bad-species", "eevee"], build_fn
    )

    assert successes == [{"name": "pikachu"}, {"name": "eevee"}]
    assert failures == [{"name": "bad-species", "error": "페이지 구조가 예상과 다름"}]
