from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime, timedelta
from typing import List, Optional

from mt5_handler import mt5_handler
from websocket_manager import manager
from models import (
    ConnectRequest, ConnectResponse, AccountInfo, Position, TradeDeal,
    OrderRequest, OrderResult, SymbolInfo, Tick
)

app = FastAPI()

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    if not mt5_handler.initialize():
        print("Failed to initialize MT5")

# --- REST Endpoints ---

@app.post("/connect", response_model=ConnectResponse)
async def connect(request: ConnectRequest):
    if request.path:
        if not mt5_handler.initialize(request.path):
             raise HTTPException(status_code=500, detail="Failed to initialize MT5")
    
    authorized = mt5_handler.login(request.login, request.password, request.server)
    if authorized:
        return ConnectResponse(status="connected")
    else:
        raise HTTPException(status_code=401, detail="Login failed")

@app.get("/account", response_model=AccountInfo)
async def get_account_info():
    info = await mt5_handler.get_account_info()
    if info:
        return info
    raise HTTPException(status_code=500, detail="Failed to get account info")

@app.get("/positions", response_model=List[Position])
async def get_positions():
    return await mt5_handler.get_positions()

@app.get("/history", response_model=List[TradeDeal])
async def get_history(days: int = Query(30, ge=1)):
    to_date = datetime.now()
    from_date = to_date - timedelta(days=days)
    return await mt5_handler.get_history(from_date, to_date)

@app.post("/trade/order", response_model=OrderResult)
async def place_order(order: OrderRequest):
    request = order.dict(exclude_none=True)
    result = await mt5_handler.order_send(request)
    if result:
        return result._asdict()
    raise HTTPException(status_code=500, detail="Order failed")

@app.post("/trade/check", response_model=OrderResult)
async def check_order(order: OrderRequest):
    request = order.dict(exclude_none=True)
    result = await mt5_handler.order_check(request)
    if result:
        return result._asdict()
    raise HTTPException(status_code=500, detail="Order check failed")

@app.post("/trade/calc_margin")
async def calc_margin(action: int, symbol: str, volume: float, price: float):
    margin = await mt5_handler.order_calc_margin(action, symbol, volume, price)
    if margin is not None:
        return {"margin": margin}
    raise HTTPException(status_code=500, detail="Failed to calculate margin")

@app.get("/market/symbol/{symbol}", response_model=dict)
async def get_symbol_info(symbol: str):
    info = await mt5_handler.get_symbol_info(symbol)
    if info:
        return info
    raise HTTPException(status_code=404, detail="Symbol not found")

@app.get("/market/tick/{symbol}", response_model=Tick)
async def get_symbol_tick(symbol: str):
    tick = await mt5_handler.get_symbol_tick(symbol)
    if tick:
        return tick
    raise HTTPException(status_code=404, detail="Tick not found")

# --- WebSocket Endpoints ---

@app.websocket("/ws/positions")
async def websocket_endpoint_positions(websocket: WebSocket):
    print("WS: New connection request for positions")
    await manager.connect_positions(websocket)
    try:
        while True:
            await websocket.receive_text() # Keep connection open
    except WebSocketDisconnect:
        print("WS: Disconnected positions")
        manager.disconnect_positions(websocket)
    except Exception as e:
        print(f"WS Error positions: {e}")

@app.websocket("/ws/price/{symbol}")
async def websocket_endpoint_price(websocket: WebSocket, symbol: str):
    print(f"WS: New connection request for price {symbol}")
    await manager.connect_price(websocket, symbol)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        print(f"WS: Disconnected price {symbol}")
        manager.disconnect_price(websocket, symbol)
    except Exception as e:
        print(f"WS Error price {symbol}: {e}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
