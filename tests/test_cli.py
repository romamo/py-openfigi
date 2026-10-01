import pytest
import requests
from treaty import CliExit

from openfigi.cli import app
from openfigi.commands.lookup import _http_error


def _http_failure(status: int, headers: dict[str, str] | None = None) -> requests.HTTPError:
    response = requests.Response()
    response.status_code = status
    response.headers.update(headers or {})
    return requests.HTTPError(f"HTTP {status}", response=response)


def test_lookup_without_identifier_is_arg_error():
    envelope = app.call("lookup", {})
    assert envelope.exit_code == 2
    assert envelope.error.message == "Pass at least one of --figi, --isin, --symbol, or --desc"


@pytest.mark.parametrize("isin", ["BAD", "US0000000000"])
def test_lookup_invalid_isin_is_arg_error(isin: str):
    envelope = app.call("lookup", {"isin": isin})
    assert envelope.exit_code == 2
    assert envelope.error.errors[0]["field"] == "isin"


def test_lookup_unknown_asset_class_is_arg_error():
    envelope = app.call("lookup", {"isin": "US0378331005", "asset_class": "nope"})
    assert envelope.exit_code == 2


def test_lookup_negative_limit_is_arg_error():
    envelope = app.call("lookup", {"isin": "US0378331005", "limit": -5})
    assert envelope.exit_code == 2


@pytest.mark.parametrize(
    ("status", "code"),
    [(401, "AUTH_REQUIRED"), (403, "AUTH_REQUIRED"), (429, "RATE_LIMITED"), (503, "UNAVAILABLE")],
)
def test_http_error_maps_to_exit_code(status: int, code: str):
    exit_ = _http_error(_http_failure(status))
    assert isinstance(exit_, CliExit)
    assert exit_.code == code


def test_rate_limit_uses_retry_after_header():
    exit_ = _http_error(_http_failure(429, {"Retry-After": "7"}))
    assert isinstance(exit_, CliExit)
    assert exit_.retry_after_ms == 7000


def test_unexpected_http_error_is_reraised():
    failure = _http_failure(400)
    assert _http_error(failure) is failure
