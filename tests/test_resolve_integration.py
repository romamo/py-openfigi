import pytest
from pydantic_market_data.models import SecurityQuery

from openfigi import OpenFIGIDataSource

# BBG00N8SFJD7 is the listing-level FIGI (Paris/FP, EUR-denominated).
# _to_security stores compositeFIGI, so the resolved Security carries BBG00N8SFJC8.
_LISTING_FIGI = "BBG00N8SFJD7"
_COMPOSITE_FIGI = "BBG00N8SFJC8"
_ISIN = "LU1900066033"

_QUERIES = [
    pytest.param(
        SecurityQuery(isin=_ISIN, figi=_LISTING_FIGI, symbol="LSMCd", currency="EUR"),
        id="figi+isin+symbol+currency",
    ),
    pytest.param(
        SecurityQuery(isin=_ISIN, symbol="CHIP", currency="EUR"),
        id="isin+symbol+currency",
    ),
    pytest.param(
        SecurityQuery(figi=_LISTING_FIGI),
        id="figi-only",
    ),
]


@pytest.fixture(scope="module")
def ds() -> OpenFIGIDataSource:
    return OpenFIGIDataSource()


@pytest.mark.integration
@pytest.mark.parametrize("criteria", _QUERIES)
def test_resolve_same_security(ds: OpenFIGIDataSource, criteria: SecurityQuery) -> None:
    result = ds.resolve(criteria)
    assert result is not None, f"resolve() returned None for {criteria}"
    assert result.figi == _COMPOSITE_FIGI, f"expected figi={_COMPOSITE_FIGI}, got {result.figi}"
