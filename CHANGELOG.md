# Changelog

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
