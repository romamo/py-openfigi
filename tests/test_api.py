import json
from typing import Any

import pytest
import requests
from pydantic_market_data.models import AssetClass, Security, SecurityQuery

from openfigi.api import OpenFIGIDataSource, _apply_filters
from openfigi.client import OpenFIGIClient
from openfigi.models import IdType, MarketSector

APPLE = {
    "figi": "BBG000B9XRY4",
    "name": "APPLE INC",
    "ticker": "AAPL",
    "exchCode": "US",
    "marketSector": "Equity",
    "securityType": "Common Stock",
}


class CannedClient(OpenFIGIClient):
    """Answers every POST with one canned JSON body and records the payloads."""

    def __init__(self, body: Any) -> None:
        super().__init__()
        self.content = json.dumps(body).encode()
        self.payloads: list[Any] = []

    def post(self, path: str, json: Any = None, **kwargs: Any) -> requests.Response:
        self.payloads.append(json)
        response = requests.Response()
        response.status_code = 200
        response._content = self.content
        return response


@pytest.mark.parametrize(
    ("asset_class", "sector"),
    [
        (AssetClass.CASH, MarketSector.MONEY_MARKET),
        (AssetClass.FX, MarketSector.CURRENCY),
        (AssetClass.INDEX, MarketSector.INDEX),
        (AssetClass.COMMODITY, MarketSector.COMMODITY),
        (AssetClass.EQUITY, None),
        (AssetClass.FIXED_INCOME, None),
        (None, None),
    ],
)
def test_mapping_job_sends_sector_only_for_single_sector_asset_class(
    asset_class: AssetClass | None, sector: MarketSector | None
):
    ds = OpenFIGIDataSource(client=OpenFIGIClient())
    query = SecurityQuery(symbol="X", asset_class=asset_class)
    assert ds._build_job(IdType.TICKER, "X", query).marketSecDes == sector


def test_asset_class_filter_matches_exactly():
    equity = Security(symbol="A", name="A", asset_class=AssetClass.EQUITY)
    fixed_income = Security(symbol="B", name="B", asset_class=AssetClass.FIXED_INCOME)
    query = SecurityQuery(description="x", asset_class=AssetClass.EQUITY)
    assert _apply_filters([equity, fixed_income], query) == [equity]


def test_isin_lookup_carries_isin_on_results():
    ds = OpenFIGIDataSource(client=CannedClient([{"data": [APPLE]}]))
    results, total = ds.resolve_candidates(SecurityQuery(isin="US0378331005"))
    assert total == 1
    assert str(results[0].isin) == "US0378331005"


def test_symbol_lookup_leaves_isin_empty():
    ds = OpenFIGIDataSource(client=CannedClient([{"data": [APPLE]}]))
    results, _ = ds.resolve_candidates(SecurityQuery(symbol="AAPL"))
    assert results[0].isin is None
