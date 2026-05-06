from __future__ import annotations

import json
import logging
import sys

from pydantic import Field
from pydantic_market_data.cli_models import (
    CLASS,
    CURR,
    EXCHANGE,
    ISIN,
    LIMIT,
    NAME,
    SYMBOL,
    GlobalArgs,
)
from pydantic_market_data.models import SecurityQuery

from ..api import OpenFIGIDataSource, _apply_filters

logger = logging.getLogger(__name__)


class LookupArgs(GlobalArgs):
    """Lookup a security symbol"""

    figi: str | None = Field(None, description="FIGI identifier")
    isin: ISIN | None = Field(None, description="ISIN code to search for")
    symbol: SYMBOL | None = Field(None, description="Security symbol (ticker)")
    desc: NAME | None = Field(None, description="Security name or description")
    exchange: EXCHANGE | None = Field(None, description="Exchange code (e.g. US, L, GY)")
    currency: CURR | None = Field(None, description="Currency code (e.g. USD, EUR, GBP)")
    asset_class: CLASS | None = Field(None, description="Asset class (Equity, Commodity, etc.)")
    limit: LIMIT = Field(LIMIT(1), description="Maximum number of results to return")


class LookupCommand(LookupArgs):
    """Look up a security via OpenFIGI"""

    def cli_cmd(self) -> None:
        ds = OpenFIGIDataSource()

        if not (self.figi or self.isin or self.symbol or self.desc):
            logger.error("Provide --figi, --isin, --symbol, or --desc")
            sys.exit(1)

        if self.figi or self.isin or self.symbol:
            criteria = SecurityQuery(
                figi=self.figi,
                isin=self.isin,
                symbol=self.symbol,
                exchange=self.exchange,
                currency=self.currency,
                asset_class=self.asset_class,
            )
            result = ds.resolve(criteria)
            if not result:
                logger.error("Security not found")
                sys.exit(1)
            results = [result]
        else:
            criteria = SecurityQuery(
                exchange=self.exchange,
                currency=self.currency,
                asset_class=self.asset_class,
            )
            results = _apply_filters(ds.search(self.desc), criteria)  # type: ignore[arg-type]

        results = results[: self.limit]

        if not results:
            logger.error("Security not found")
            sys.exit(1)

        if self.format == "json":
            print(json.dumps([r.model_dump(mode="json") for r in results], indent=2))
        else:
            for r in results:
                print(r.symbol)
