from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ConnectRequest(BaseModel):
    login: Optional[int] = Field(None, example=274902085)
    password: Optional[str] = Field(None, example="Md@70322532$")
    server: Optional[str] = Field(None, example="Exness-MT5Trial6")
    path: Optional[str] = Field(None, example=r"C:\Program Files\MetaTrader 5 EXNESS\terminal64.exe")

class ConnectResponse(BaseModel):
    status: str
    token: Optional[str] = None

class AccountInfo(BaseModel):
    login: int
    balance: float
    equity: float
    profit: float
    margin: float
    margin_free: float
    margin_level: float
    currency: str
    server: str
    company: str
    name: str

class Position(BaseModel):
    ticket: int
    symbol: str
    type: str  # "BUY" or "SELL"
    volume: float
    price_open: float
    sl: float
    tp: float
    price_current: float
    profit: float
    time: datetime
    comment: str

class TradeDeal(BaseModel):
    ticket: int
    order: int
    time: datetime
    type: str # "BUY" or "SELL" etc
    entry: str # "IN", "OUT", "INOUT"
    symbol: str
    volume: float
    price: float
    profit: float
    commission: float
    swap: float
    comment: str

class OrderRequest(BaseModel):
    action: int
    magic: Optional[int] = 0
    order: Optional[int] = 0
    symbol: str
    volume: float
    price: Optional[float] = 0.0
    stoplimit: Optional[float] = 0.0
    sl: Optional[float] = 0.0
    tp: Optional[float] = 0.0
    deviation: Optional[int] = 20
    type: int
    type_filling: Optional[int] = 0
    type_time: Optional[int] = 0
    expiration: Optional[int] = 0
    comment: Optional[str] = ""
    position: Optional[int] = 0
    position_by: Optional[int] = 0

class OrderResult(BaseModel):
    retcode: int
    deal: int
    order: int
    volume: float
    price: float
    bid: float
    ask: float
    comment: str
    request_id: int
    retcode_external: int

class SymbolInfo(BaseModel):
    symbol: str
    currency_base: Optional[str] = None
    currency_profit: Optional[str] = None
    currency_margin: Optional[str] = None
    digits: Optional[int] = None
    spread: Optional[int] = None
    trade_mode: Optional[int] = None
    trade_calc_mode: Optional[int] = None
    ask: Optional[float] = None
    bid: Optional[float] = None
    last: Optional[float] = None
    volume_min: Optional[float] = None
    volume_max: Optional[float] = None
    volume_step: Optional[float] = None
    point: Optional[float] = None
    trade_tick_value: Optional[float] = None
    trade_tick_size: Optional[float] = None
    swap_long: Optional[float] = None
    swap_short: Optional[float] = None
    swap_mode: Optional[int] = None
    description: Optional[str] = None

    class Config:
        extra = "ignore"

class Tick(BaseModel):
    time: datetime
    bid: float
    ask: float
    last: float
    volume: int
    time_msc: int
    flags: int
    volume_real: float
