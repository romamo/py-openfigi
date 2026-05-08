# Resolve Workflow

`OpenFIGIDataSource.resolve(criteria: SecurityQuery) -> Security | None`

Resolves a `SecurityQuery` to a single `Security` using a two-phase approach.

---

## Phase 1 — API Query

A single primary identifier is selected by strict priority and sent to the OpenFIGI API:

| Priority | Field | API endpoint | `idType` |
|---|---|---|---|
| 1 | `figi` | `/v3/mapping` | `ID_BB_GLOBAL` |
| 2 | `isin` | `/v3/mapping` | `ID_ISIN` |
| 3 | `symbol` | `/v3/mapping` | `TICKER` |
| 4 | `description` | `/v3/search` | — |

For all mapping-job cases (`figi`, `isin`, `symbol`), the supplementary fields are embedded in the job as API-level constraints:

| Field | `MappingJob` field |
|---|---|
| `currency` | `MappingJob.currency` |
| `exchange` | `MappingJob.exchCode` |
| `asset_class` | `MappingJob.marketSecDes` |

**FIGI caveat:** a FIGI already uniquely identifies one listing. Adding `currency` or `exchange` constraints that do not match that listing causes the API to return zero results.

**ISIN:** one ISIN maps to many listings across different exchanges and currencies — supplementary filters are essential for disambiguation.

---

## Phase 2 — Post-API Filtering

After the API returns candidates, `_apply_filters` narrows them down:

| Field | Filter logic |
|---|---|
| `exchange` | Substring match on `Security.exchange` (case-insensitive) |
| `asset_class` | Substring match on `Security.asset_class` (case-insensitive) |
| `symbol` | Exact match on `Security.symbol` (case-insensitive); **skipped when `figi` is set** |

**`symbol`** is skipped for FIGI lookups because the query symbol may differ from the listing's actual ticker — FIGI already uniquely identifies the listing.

**`currency`** is applied only at Phase 1 (API constraint). The mapping response does not return currency, so it is not available as a post-filter. The `Security` returned contains only values provided by the API.

`resolve` returns the first surviving candidate, or `None` if none remain. When more than one candidate survives, a `DEBUG` message is logged.

---

## Example Combinations

All three resolve to the same security (`compositeFIGI = BBG00N8SFJC8`):

```python
# figi wins (priority 1); currency=EUR narrows the API query; symbol is skipped as a post-filter
SecurityQuery(isin="LU1900066033", figi="BBG00N8SFJD7", symbol="LSMCd", currency="EUR")

# isin wins (priority 2); symbol=CHIP and currency=EUR narrow the 66 EUR candidates
SecurityQuery(isin="LU1900066033", symbol="CHIP", currency="EUR")

# figi only; no supplementary filters
SecurityQuery(figi="BBG00N8SFJD7")
```
