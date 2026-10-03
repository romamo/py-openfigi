from pathlib import Path

import pytest
import requests
from pydantic_market_data.models import SecurityQuery
from treaty import CliExit
from urllib3.exceptions import MaxRetryError, NewConnectionError, ReadTimeoutError

from openfigi.api import OpenFIGIDataSource
from openfigi.cli import app
from openfigi.client import OpenFIGIClient
from openfigi.commands.lookup import _connection_error, _http_error
from openfigi.models import IdType


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


def test_client_uses_given_proxy_and_ca_bundle_only():
    client = OpenFIGIClient(
        proxy="http://proxy.example:3128", ca_bundle=Path("/tmp/ca.pem"), trust_env=False
    )
    assert client.session.proxies == {"https": "http://proxy.example:3128"}
    assert client.session.verify == "/tmp/ca.pem"
    assert client.session.trust_env is False


def test_client_reads_environment_by_default():
    client = OpenFIGIClient()
    assert client.session.proxies == {}
    assert client.session.trust_env is True


@pytest.mark.parametrize(
    ("currency", "expected"),
    [("GBp", "GBp"), ("GBX", "GBp"), ("ZAc", "ZAr"), ("ILA", "ILs"), ("gbp", "GBP"), (None, None)],
)
def test_mapping_job_uses_openfigi_currency_spelling(currency: str | None, expected: str | None):
    ds = OpenFIGIDataSource(client=OpenFIGIClient())
    job = ds._build_job(IdType.TICKER, "VOD", SecurityQuery(symbol="VOD", currency=currency))
    assert job.currency == expected


def _connection_failure(reason: Exception) -> requests.ConnectionError:
    return requests.ConnectionError(MaxRetryError(None, "/v3/mapping", reason))


def test_read_timeout_after_retries_is_timeout():
    # requests wraps a read timeout that exhausted the retries in ConnectionError, not Timeout
    exit_ = _connection_error(_connection_failure(ReadTimeoutError(None, "/", "Read timed out")))
    assert isinstance(exit_, CliExit)
    assert exit_.code == "TIMEOUT"


def test_refused_connection_is_unavailable():
    exit_ = _connection_error(_connection_failure(NewConnectionError(None, "refused")))
    assert isinstance(exit_, CliExit)
    assert exit_.code == "UNAVAILABLE"
