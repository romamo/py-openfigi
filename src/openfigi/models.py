from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class IdType(str, Enum):
    ID_ISIN = "ID_ISIN"
    ID_BB_GLOBAL = "ID_BB_GLOBAL"
    ID_BB_UNIQUE = "ID_BB_UNIQUE"
    ID_SEDOL = "ID_SEDOL"
    ID_CUSIP = "ID_CUSIP"
    ID_COMMON = "ID_COMMON"
    ID_WERTPAPIER = "ID_WERTPAPIER"
    ID_BB = "ID_BB"
    ID_ITALY = "ID_ITALY"
    ID_EXCH_SYMBOL = "ID_EXCH_SYMBOL"
    ID_FULL_EXCHANGE_SYMBOL = "ID_FULL_EXCHANGE_SYMBOL"
    ID_DUTCH = "ID_DUTCH"
    ID_VALOREN = "ID_VALOREN"
    ID_CUSIP_8_CHR = "ID_CUSIP_8_CHR"
    OCC_SYMBOL = "OCC_SYMBOL"
    UNIQUE_ID_FUT_OPT = "UNIQUE_ID_FUT_OPT"
    OPRA_SYMBOL = "OPRA_SYMBOL"
    TICKER = "TICKER"
    BASE_TICKER = "BASE_TICKER"
    ID_CINS = "ID_CINS"
    ID_SHORT_CODE = "ID_SHORT_CODE"
    ID_BB_SEC_NUM_DES = "ID_BB_SEC_NUM_DES"


class MarketSector(str, Enum):
    COMMODITY = "Comdty"
    CORPORATE = "Corp"
    CURRENCY = "Curncy"
    EQUITY = "Equity"
    GOVERNMENT = "Govt"
    INDEX = "Index"
    MORTGAGE = "Mtge"
    MONEY_MARKET = "M-Mkt"
    MUNICIPAL = "Muni"
    PREFERRED = "Pfd"


class OptionType(str, Enum):
    CALL = "Call"
    PUT = "Put"


class MappingJob(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    idType: IdType
    idValue: str | float
    exchCode: str | None = None
    micCode: str | None = None
    currency: str | None = None
    marketSecDes: MarketSector | None = None
    securityType: str | None = None
    securityType2: str | None = None
    includeUnlistedEquities: bool | None = None
    optionType: OptionType | None = None
    strike: list[float | None] | None = None
    contractSize: list[float | None] | None = None
    coupon: list[float | None] | None = None
    expiration: list[str | None] | None = None
    maturity: list[str | None] | None = None
    stateCode: str | None = None


class _FIGIBase(BaseModel):
    figi: str
    name: str | None = None
    ticker: str | None = None
    exchCode: str | None = None
    compositeFIGI: str | None = None
    shareClassFIGI: str | None = None
    securityType: str | None = None
    marketSector: str | None = None
    securityType2: str | None = None
    securityDescription: str | None = None


class FIGIResult(_FIGIBase):
    metadata: str | None = None


class SearchItem(_FIGIBase):
    pass


class MappingResult(BaseModel):
    data: list[FIGIResult] | None = None
    error: str | None = None


class SearchRequest(BaseModel):
    query: str
    exchCode: str | None = None
    micCode: str | None = None
    currency: str | None = None
    marketSecDes: MarketSector | None = None
    securityType: str | None = None
    securityType2: str | None = None
    optionType: OptionType | None = None
    includeUnlistedEquities: bool | None = None
    start: str | None = None


class _PaginatedResponse(BaseModel):
    data: list[SearchItem] = Field(default_factory=list)
    next: str | None = None


class SearchResponse(_PaginatedResponse):
    pass


class FilterRequest(BaseModel):
    query: str | None = None
    exchCode: str | None = None
    micCode: str | None = None
    currency: str | None = None
    marketSecDes: MarketSector | None = None
    securityType: str | None = None
    securityType2: str | None = None
    optionType: OptionType | None = None
    includeUnlistedEquities: bool | None = None
    start: str | None = None


class FilterResponse(_PaginatedResponse):
    total: int | None = None
