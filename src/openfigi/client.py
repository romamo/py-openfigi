from __future__ import annotations

from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class OpenFIGIClient:
    BASE_URL = "https://api.openfigi.com"

    def __init__(self, api_key: str | None = None):
        self.session = requests.Session()
        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if api_key:
            headers["X-OPENFIGI-APIKEY"] = api_key
        self.session.headers.update(headers)

        retries = Retry(
            total=3,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("https://", adapter)

    def post(self, path: str, json: Any = None, **kwargs: Any) -> requests.Response:
        kwargs.setdefault("timeout", 30)
        return self.session.post(f"{self.BASE_URL}{path}", json=json, **kwargs)

    def get(
        self, path: str, params: dict[str, Any] | None = None, **kwargs: Any
    ) -> requests.Response:
        kwargs.setdefault("timeout", 30)
        return self.session.get(f"{self.BASE_URL}{path}", params=params, **kwargs)
