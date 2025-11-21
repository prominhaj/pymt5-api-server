from fastapi import WebSocket
from typing import List, Dict
import asyncio

class ConnectionManager:
    def __init__(self):
        # List of connections for positions updates
        self.position_connections: List[WebSocket] = []
        # Dict of symbol -> List of connections for price updates
        self.price_connections: Dict[str, List[WebSocket]] = {}

    async def connect_positions(self, websocket: WebSocket):
        await websocket.accept()
        self.position_connections.append(websocket)

    def disconnect_positions(self, websocket: WebSocket):
        if websocket in self.position_connections:
            self.position_connections.remove(websocket)

    async def broadcast_positions(self, message: str):
        for connection in self.position_connections:
            try:
                await connection.send_text(message)
            except Exception:
                # If sending fails, we might want to remove the connection
                pass

    async def connect_price(self, websocket: WebSocket, symbol: str):
        await websocket.accept()
        if symbol not in self.price_connections:
            self.price_connections[symbol] = []
        self.price_connections[symbol].append(websocket)

    def disconnect_price(self, websocket: WebSocket, symbol: str):
        if symbol in self.price_connections:
            if websocket in self.price_connections[symbol]:
                self.price_connections[symbol].remove(websocket)
            if not self.price_connections[symbol]:
                del self.price_connections[symbol]

    async def broadcast_price(self, symbol: str, message: str):
        if symbol in self.price_connections:
            for connection in self.price_connections[symbol]:
                try:
                    await connection.send_text(message)
                except Exception:
                    pass

manager = ConnectionManager()
