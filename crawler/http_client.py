"""요청 사이 딜레이를 두고 대상 사이트에 과도한 부하를 주지 않는 HTTP 클라이언트."""

import time

import requests

USER_AGENT = "pokemon-dex-sv personal project (individual, non-commercial local use)"


class RateLimitedFetcher:
    """연속된 요청 사이에 최소 delay_seconds만큼 간격을 두고 요청을 보낸다."""

    def __init__(self, delay_seconds: float = 0.3, session=None):
        self.delay_seconds = delay_seconds
        self.session = session or requests.Session()
        self._last_request_time: float | None = None

    def get_json(self, url: str) -> dict:
        response = self._get(url)
        return response.json()

    def get_html(self, url: str) -> str:
        response = self._get(url)
        return response.text

    def _get(self, url: str):
        self._wait_for_rate_limit()
        response = self.session.get(url, timeout=15, headers={"User-Agent": USER_AGENT})
        response.raise_for_status()
        return response

    def _wait_for_rate_limit(self) -> None:
        if self._last_request_time is not None:
            elapsed = time.perf_counter() - self._last_request_time
            remaining = self.delay_seconds - elapsed
            if remaining > 0:
                time.sleep(remaining)
        self._last_request_time = time.perf_counter()
