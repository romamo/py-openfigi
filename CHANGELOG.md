# Changelog

## [Unreleased]

### Changed
- **Breaking:** requires Python 3.14+ (was 3.10+)
- **Breaking:** the CLI is built on `treaty` instead of the deprecated `agentyper`. Output is treaty's envelope (`ok`, `data`, `error`, `meta`), and invalid arguments exit `2` (was `3`)
- CLI `lookup --limit` is treaty's pagination flag: `0` returns every match, and `--cursor` gets the next page. `meta.pagination.total` counts the matches after filtering, not the raw API candidates
- `OpenFIGIClient` returns the last response once retries on 429 and 5xx run out, so `raise_for_status()` raises `requests.HTTPError` with the status instead of `requests.exceptions.RetryError`
- `IdType`, `MarketSector` and `OptionType` are `StrEnum`s
- Bumped `pydantic-market-data` to `>=0.10.0`: `--currency` accepts the minor-unit codes `GBX`, `ZAC` and `ILA` (and `GBp`, `ZAc`), and `GBp` now means pence, not pounds
- CLI `lookup` declares "at least one of `--figi`, `--isin`, `--symbol`, `--desc`" as a rule, so `--help` and `--schema` show it, and returns `Security` models, so `--output-schema` carries their enums and patterns

### Added
- `OpenFIGIClient` takes `proxy`, `ca_bundle` and `trust_env` to override what `requests` reads from the environment

### Fixed
- `--currency GBp` (or `GBX`, `ZAc`, `ILA`) finds securities quoted in minor units: the mapping request sends OpenFIGI's spelling (`GBp`, `ZAr`, `ILs`), so `lookup --symbol VOD --exchange LN --currency GBp` returns Vodafone instead of "Security not found"
- `OpenFIGIDataSource.get_enum_values` returns the list of values; it returned the raw `{"values": [...]}` response despite its `list[str]` annotation
- CLI `lookup` honors `--proxy` and `--no-proxy`, which treaty advertised but the OpenFIGI client ignored; `HTTPS_PROXY`, `NO_PROXY` and `REQUESTS_CA_BUNDLE` resolve as before
- CLI `lookup` answers a rejected API key, a rate limit, a timeout, or an unreachable or failing OpenFIGI with `AUTH_REQUIRED`, `RATE_LIMITED`, `TIMEOUT` or `UNAVAILABLE` instead of a traceback and exit `1`
- CLI `lookup --limit` rejects negative values; `--limit -5` returned all but the last 5 matches, and `--limit 0` answered "Security not found"

## [0.1.5] - 2026-09-30

### Fixed
- CLI `lookup` validates its arguments before creating the OpenFIGI data source
- CLI `--asset-class` accepts the `AssetClass` values (`equity`, `fixed_income`, `commodity`, etc.) and lists them when given an invalid one; the help text suggested capitalised values (`Equity`) that were rejected

## [0.1.4] - 2026-09-30

### Changed
- `Security.asset_class` is now a `pydantic-market-data` `AssetClass` enum mapped from the OpenFIGI market sector: `Equity` and `Pfd` to `EQUITY`; `Corp`, `Govt`, `Mtge` and `Muni` to `FIXED_INCOME`; `M-Mkt` to `CASH`; `Index` to `INDEX`; `Comdty` to `COMMODITY`; `Curncy` to `FX`
- Bumped `pydantic-market-data` dependency to `>=0.4.0`

## [0.1.3] - 2026-05-08

### Added
- `security_type` field populated in resolved `Security` objects

### Changed
- `OpenFIGISettings` now ignores extra environment variables (`extra="ignore"`)
- Bumped `pydantic-market-data` dependency to 0.3.2

### Fixed
- Doc: corrected method name reference from `_pick_best` to `resolve` in `resolve.md`

## [0.1.2] - 2026-05-07

### Added
- `resolve_candidates` method for multi-job FIGI resolution
- Pagination support for search results

### Changed
- CLI migrated to `agentyper`
- `resolve` simplified by delegating to `resolve_candidates`

## [0.1.1] - 2026-05-06

### Changed
- Renamed PyPI distribution to `py-openfigi2`

## [0.1.0] - 2026-05-06

### Added
- Initial release
- `OpenFIGIDataSource` — Pydantic-based data source for the OpenFIGI API
- Mapping, search, and filter endpoints
- CLI entry point `openfigi`
- Pydantic models: `MappingJob`, `FIGIResult`, `MappingResult`, `SearchRequest`, `SearchResponse`, `FilterRequest`, `FilterResponse`
