from __future__ import annotations

import agentyper
from pydantic import ValidationError
from pydantic_market_data.models import SecurityQuery

from ..api import OpenFIGIDataSource


def lookup(
    figi: str | None = agentyper.Option(None, "--figi", help="FIGI identifier"),
    isin: str | None = agentyper.Option(None, "--isin", help="ISIN code"),
    symbol: str | None = agentyper.Option(None, "--symbol", help="Security symbol (ticker)"),
    desc: str | None = agentyper.Option(None, "--desc", help="Security name or description"),
    exchange: str | None = agentyper.Option(None, "--exchange", help="Exchange code (e.g. FP, LN)"),
    currency: str | None = agentyper.Option(
        None, "--currency", help="Currency code (e.g. USD, EUR)"
    ),
    asset_class: str | None = agentyper.Option(
        None, "--asset-class", help="Asset class (Equity, Commodity, etc.)"
    ),
    limit: int = agentyper.Option(1, "--limit", help="Maximum number of results to return"),
) -> None:
    """Look up a security via OpenFIGI."""
    ds = OpenFIGIDataSource()

    if not (figi or isin or symbol or desc):
        agentyper.exit_error(
            "Provide --figi, --isin, --symbol, or --desc",
            code=agentyper.ExitCode.ARG_ERROR,
        )

    try:
        criteria = SecurityQuery(
            figi=figi,
            isin=isin,
            symbol=symbol,
            description=desc,
            exchange=exchange,
            currency=currency,
            asset_class=asset_class,
        )
    except ValidationError as exc:
        agentyper.format_pydantic_error(exc)

    results, total = ds.resolve_candidates(criteria)
    results = results[:limit]

    if not results:
        agentyper.exit_error("Security not found", code=agentyper.ExitCode.NOT_FOUND)

    num_results = len(results)
    is_partial = num_results < total
    agentyper.set_pagination(
        total=total,
        returned=num_results,
        truncated=is_partial,
        has_more=is_partial,
    )
    agentyper.output([r.model_dump(mode="json") for r in results])
