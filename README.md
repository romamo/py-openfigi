# py-openfigi

Python client for the [OpenFIGI API](https://www.openfigi.com/api) — map ISINs, tickers, CUSIPs and other identifiers to FIGI codes, and search or filter securities.

## Installation

```bash
pip install py-openfigi
```

## Usage

### Python API

```python
from openfigi import OpenFIGIDataSource, MappingJob, IdType

ds = OpenFIGIDataSource()  # set OPENFIGI_API_KEY env var for higher rate limits

# Resolve by ISIN
security = ds.resolve_query(isin="US0378331005")

# Bulk map identifiers
results = ds.map_identifiers([
    MappingJob(idType=IdType.ID_ISIN, idValue="US0378331005"),
    MappingJob(idType=IdType.TICKER, idValue="AAPL", exchCode="US"),
])

# Search by keyword
items = ds.search("Apple")
```

### CLI

```
openfigi lookup --isin US0378331005
openfigi lookup --symbol AAPL --exchange US --format json
openfigi lookup --desc "Apple" --limit 5
```

## Configuration

| Env var             | Description                                   |
|---------------------|-----------------------------------------------|
| `OPENFIGI_API_KEY`  | Optional API key for higher rate limits       |

## License

MIT
