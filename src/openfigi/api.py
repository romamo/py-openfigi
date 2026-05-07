from __future__ import annotations

import logging

from pydantic_market_data.models import Security, SecurityQuery

from .client import OpenFIGIClient
from .models import (
    FilterRequest,
    FilterResponse,
    IdType,
    MappingJob,
    MappingResult,
    MarketSector,
    SearchRequest,
    SearchResponse,
    _FIGIBase,
)
from .settings import OpenFIGISettings

logger = logging.getLogger(__name__)

_MARKET_SECTOR_TO_ASSET_CLASS: dict[str, str] = {
    "Equity": "Equity",
    "Corp": "Corporate Bond",
    "Govt": "Government Bond",
    "Mtge": "Mortgage",
    "M-Mkt": "Money Market",
    "Muni": "Municipal Bond",
    "Index": "Index",
    "Comdty": "Commodity",
    "Curncy": "Currency",
    "Pfd": "Preferred",
}

_ASSET_CLASS_TO_MARKET_SECTOR: dict[str, MarketSector] = {
    "EQUITY": MarketSector.EQUITY,
    "STOCK": MarketSector.EQUITY,
    "CORPORATE BOND": MarketSector.CORPORATE,
    "CORP": MarketSector.CORPORATE,
    "BOND": MarketSector.CORPORATE,
    "GOVERNMENT BOND": MarketSector.GOVERNMENT,
    "GOVT": MarketSector.GOVERNMENT,
    "INDEX": MarketSector.INDEX,
    "COMMODITY": MarketSector.COMMODITY,
    "CURRENCY": MarketSector.CURRENCY,
    "PREFERRED": MarketSector.PREFERRED,
    "MORTGAGE": MarketSector.MORTGAGE,
    "MUNICIPAL BOND": MarketSector.MUNICIPAL,
    "MUNI": MarketSector.MUNICIPAL,
    "MONEY MARKET": MarketSector.MONEY_MARKET,
}


def _apply_filters(candidates: list[Security], criteria: SecurityQuery) -> list[Security]:
    filtered = candidates
    if criteria.exchange:
        ex = criteria.exchange.upper()
        filtered = [c for c in filtered if c.exchange and ex in c.exchange.upper()]
    if criteria.asset_class:
        ac = criteria.asset_class.upper()
        filtered = [c for c in filtered if c.asset_class and ac in c.asset_class.upper()]
    if criteria.symbol and not criteria.figi:
        sym = str(criteria.symbol).upper()
        filtered = [c for c in filtered if c.symbol and str(c.symbol).upper() == sym]
    return filtered


class OpenFIGIDataSource:
    def __init__(
        self,
        client: OpenFIGIClient | None = None,
        settings: OpenFIGISettings | None = None,
    ) -> None:
        cfg = settings or OpenFIGISettings()
        self.client = client or OpenFIGIClient(api_key=cfg.api_key)

    def search(self, query: str) -> list[Security]:
        """Search for securities by keyword using /v3/search."""
        req = SearchRequest(query=query)
        resp = self.client.post("/v3/search", json=req.model_dump(exclude_none=True))
        resp.raise_for_status()
        data = SearchResponse.model_validate(resp.json())
        return [self._to_security(item) for item in data.data]

    def resolve(self, criteria: SecurityQuery) -> Security | None:
        """Resolve a SecurityQuery to a single Security; see docs/resolve.md for details."""
        filtered, _ = self.resolve_candidates(criteria)
        if len(filtered) > 1:
            logger.debug("Ambiguous: %d candidates after filtering, returning first", len(filtered))
        return filtered[0] if filtered else None

    def resolve_candidates(self, criteria: SecurityQuery) -> tuple[list[Security], int]:
        """Return (filtered_candidates, total_api_count) for the given criteria.

        filtered_candidates — all results surviving Phase 2 filters, in API order.
        total_api_count    — raw candidate count returned by the API before any filtering.
        """
        job: MappingJob | None = None

        if criteria.figi:
            job = self._build_job(IdType.ID_BB_GLOBAL, str(criteria.figi), criteria)
        elif criteria.isin:
            job = self._build_job(IdType.ID_ISIN, str(criteria.isin), criteria)
        elif criteria.symbol:
            job = self._build_job(IdType.TICKER, str(criteria.symbol), criteria)
        elif criteria.description:
            all_results = self.search(criteria.description)
            return _apply_filters(all_results, criteria), len(all_results)

        if job is None:
            return [], 0

        results_raw = self.map_identifiers([job])
        result = results_raw[0]

        if result.error:
            logger.debug("Mapping error: %s", result.error)
            return [], 0
        if not result.data:
            return [], 0

        currency_str = str(criteria.currency) if criteria.currency else None
        candidates = [self._to_security(r, currency=currency_str) for r in result.data]
        return _apply_filters(candidates, criteria), len(candidates)

    def map_identifiers(self, jobs: list[MappingJob]) -> list[MappingResult]:
        """Bulk map identifiers via /v3/mapping. Returns one result per job."""
        payload = [job.model_dump(exclude_none=True) for job in jobs]
        resp = self.client.post("/v3/mapping", json=payload)
        resp.raise_for_status()
        return [MappingResult.model_validate(item) for item in resp.json()]

    def filter_securities(self, request: FilterRequest) -> FilterResponse:
        """Alphabetically-sorted search with result counts via /v3/filter."""
        resp = self.client.post("/v3/filter", json=request.model_dump(exclude_none=True))
        resp.raise_for_status()
        return FilterResponse.model_validate(resp.json())

    def get_enum_values(self, key: str) -> list[str]:
        """Retrieve valid enum values for a mapping field (e.g. 'exchCode', 'currency')."""
        resp = self.client.get(f"/v3/mapping/values/{key}")
        resp.raise_for_status()
        return resp.json()  # type: ignore[no-any-return]

    def _build_job(self, id_type: IdType, id_value: str, criteria: SecurityQuery) -> MappingJob:
        return MappingJob(
            idType=id_type,
            idValue=id_value,
            exchCode=criteria.exchange,
            currency=str(criteria.currency) if criteria.currency else None,
            marketSecDes=_resolve_market_sector(criteria.asset_class),
        )

    def _to_security(self, item: _FIGIBase, currency: str | None = None) -> Security:
        asset_class = _MARKET_SECTOR_TO_ASSET_CLASS.get(item.marketSector or "")
        symbol = item.ticker or item.compositeFIGI or item.figi
        figi_val = item.compositeFIGI or item.figi
        return Security(
            symbol=symbol,
            name=item.name or item.figi,
            exchange=item.exchCode,
            asset_class=asset_class,
            figi=figi_val,
            currency=currency,
        )


def _resolve_market_sector(asset_class: str | None) -> MarketSector | None:
    if not asset_class:
        return None
    ac = asset_class.upper()
    for key, sector in _ASSET_CLASS_TO_MARKET_SECTOR.items():
        if key in ac:
            return sector
    return None
