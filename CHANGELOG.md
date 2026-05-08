# Changelog

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
