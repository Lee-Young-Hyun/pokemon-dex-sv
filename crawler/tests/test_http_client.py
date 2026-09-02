import time

import pytest

from crawler.http_client import RateLimitedFetcher


class FakeResponse:
    def __init__(self, json_data=None, text_data="", status_code=200):
        self._json_data = json_data
        self.text = text_data
        self.status_code = status_code

    def json(self):
        return self._json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class FakeSession:
    def __init__(self, response):
        self._response = response
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append(url)
        return self._response


def test_get_json_returns_parsed_json_from_response():
    session = FakeSession(FakeResponse(json_data={"name": "pikachu"}))
    fetcher = RateLimitedFetcher(delay_seconds=0, session=session)

    result = fetcher.get_json("https://pokeapi.co/api/v2/pokemon/pikachu")

    assert result == {"name": "pikachu"}
    assert session.calls == ["https://pokeapi.co/api/v2/pokemon/pikachu"]


def test_get_json_raises_when_response_has_error_status():
    session = FakeSession(FakeResponse(status_code=404))
    fetcher = RateLimitedFetcher(delay_seconds=0, session=session)

    with pytest.raises(RuntimeError):
        fetcher.get_json("https://pokeapi.co/api/v2/pokemon/no-such-pokemon")


def test_get_json_caches_by_url_and_skips_second_network_call():
    session = FakeSession(FakeResponse(json_data={"name": "tackle"}))
    fetcher = RateLimitedFetcher(delay_seconds=0, session=session)

    first = fetcher.get_json("https://pokeapi.co/api/v2/move/tackle")
    second = fetcher.get_json("https://pokeapi.co/api/v2/move/tackle")

    assert first == second == {"name": "tackle"}
    assert session.calls == ["https://pokeapi.co/api/v2/move/tackle"]  # 한 번만 호출됨


def test_rate_limiting_enforces_minimum_delay_between_requests():
    session = FakeSession(FakeResponse(json_data={}))
    fetcher = RateLimitedFetcher(delay_seconds=0.05, session=session)

    start = time.perf_counter()
    fetcher.get_json("https://example.com/1")
    fetcher.get_json("https://example.com/2")
    elapsed = time.perf_counter() - start

    assert elapsed >= 0.05


def test_cached_url_does_not_incur_rate_limit_delay():
    session = FakeSession(FakeResponse(json_data={}))
    fetcher = RateLimitedFetcher(delay_seconds=0.2, session=session)

    fetcher.get_json("https://example.com/1")  # 첫 호출: 딜레이 대상 아님(직전 요청 없음)

    start = time.perf_counter()
    fetcher.get_json("https://example.com/1")  # 캐시 적중: 딜레이 없이 즉시 반환
    elapsed = time.perf_counter() - start

    assert elapsed < 0.1
