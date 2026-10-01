from __future__ import annotations

from dataclasses import dataclass

import requests
from pydantic import ValidationError
from pydantic_market_data.models import AssetClass, Security, SecurityQuery
from treaty import Ctx, Exit, Flag, ParseError, RequiresAny

from ..api import OpenFIGIDataSource

IDENTIFIERS = RequiresAny(("figi", "isin", "symbol", "desc"))
# OpenFIGI rate limits reset per minute; used when a 429 carries no Retry-After header
_RATE_LIMIT_WAIT_MS = 60_000


@dataclass(frozen=True, slots=True)
class LookupArgs:
    figi: str | None = Flag(default=None, description="FIGI identifier")
    isin: str | None = Flag(default=None, description="ISIN code")
    symbol: str | None = Flag(default=None, description="Security symbol (ticker)")
    desc: str | None = Flag(default=None, description="Security name or description")
    exchange: str | None = Flag(default=None, description="Exchange code (e.g. FP, LN)")
    currency: str | None = Flag(default=None, description="Currency code (e.g. USD, EUR)")
    asset_class: AssetClass | None = Flag(default=None, description="Asset class")

    def __post_init__(self) -> None:
        try:
            self.query()
        except ValidationError as exc:
            raise ParseError.combine(
                [
                    ParseError(err["msg"], context={"field": str(err["loc"][0])})
                    for err in exc.errors()
                ]
            ) from exc

    def query(self) -> SecurityQuery:
        return SecurityQuery(
            figi=self.figi,
            isin=self.isin,
            symbol=self.symbol,
            description=self.desc,
            exchange=self.exchange,
            currency=self.currency,
            asset_class=self.asset_class,
        )


def lookup(args: LookupArgs, ctx: Ctx) -> list[Security]:
    ds = OpenFIGIDataSource()
    try:
        results, _ = ds.resolve_candidates(args.query())
    except requests.HTTPError as exc:
        raise _http_error(exc) from exc
    except requests.Timeout as exc:
        raise Exit.TIMEOUT(f"OpenFIGI did not answer in time: {exc}") from exc
    except requests.ConnectionError as exc:
        raise Exit.UNAVAILABLE(f"Cannot reach OpenFIGI: {exc}") from exc

    if not results:
        raise Exit.NOT_FOUND("Security not found")
    return results


def _http_error(exc: requests.HTTPError) -> Exception:
    status = exc.response.status_code
    if status in (401, 403):
        return Exit.AUTH_REQUIRED(
            f"OpenFIGI rejected the API key (HTTP {status})",
            fix_required="OPENFIGI_API_KEY must be a valid OpenFIGI API key, or unset",
        )
    if status == 429:
        retry_after = exc.response.headers.get("Retry-After", "")
        wait_ms = int(retry_after) * 1000 if retry_after.isdigit() else _RATE_LIMIT_WAIT_MS
        return Exit.RATE_LIMITED(
            "OpenFIGI rate limit exceeded",
            retry_after_ms=wait_ms,
            suggestion="wait and retry, or set OPENFIGI_API_KEY for a higher limit",
        )
    if status >= 500:
        return Exit.UNAVAILABLE(f"OpenFIGI returned HTTP {status}")
    return exc
