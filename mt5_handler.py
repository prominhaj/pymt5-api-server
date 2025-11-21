import MetaTrader5 as mt5
from datetime import datetime
import pandas as pd
from config import Config
import asyncio

class MT5Handler:
    def __init__(self):
        self.connected = False
        self.lock = asyncio.Lock()

    def initialize(self, path=None):
        if not path:
            path = Config.MT5_PATH
        
        if not mt5.initialize(path=path):
            print("initialize() failed, error code =", mt5.last_error())
            return False
        
        self.connected = True
        return True

    def login(self, login=None, password=None, server=None):
        if not login:
            login = Config.MT5_LOGIN
        if not password:
            password = Config.MT5_PASSWORD
        if not server:
            server = Config.MT5_SERVER
            
        authorized = mt5.login(login, password=password, server=server)
        if authorized:
            print(f"Connected to account #{login}")
        else:
            print("failed to connect at account #{}, error code: {}".format(login, mt5.last_error()))
        return authorized

    async def ensure_connected(self, login, password, server):
        # Must be called within a lock
        current_info = mt5.account_info()
        if current_info and current_info.login == login:
            return True
        
        print(f"Switching to account {login}...")
        return mt5.login(login, password=password, server=server)

    async def get_account_info(self, login=None, password=None, server=None):
        if not self.connected:
            return None
        
        async with self.lock:
            if login and password and server:
                if not await self.ensure_connected(login, password, server):
                    return None

            info = mt5.account_info()
            if info is None:
                return None
            return info._asdict()

    async def get_positions(self, login=None, password=None, server=None):
        if not self.connected:
            return []
        
        async with self.lock:
            if login and password and server:
                if not await self.ensure_connected(login, password, server):
                    return []

            positions = mt5.positions_get()
            if positions is None:
                return []
            
            result = []
            for pos in positions:
                p = pos._asdict()
                p['type'] = "BUY" if p['type'] == mt5.ORDER_TYPE_BUY else "SELL"
                p['time'] = datetime.fromtimestamp(p['time'])
                result.append(p)
            return result

    async def get_history(self, from_date, to_date, login=None, password=None, server=None):
        if not self.connected:
            return []
            
        async with self.lock:
            if login and password and server:
                if not await self.ensure_connected(login, password, server):
                    return []

            deals = mt5.history_deals_get(from_date, to_date)
            if deals is None:
                return []

            result = []
            for deal in deals:
                d = deal._asdict()
                if d['type'] == mt5.DEAL_TYPE_BUY:
                    d['type'] = "BUY"
                elif d['type'] == mt5.DEAL_TYPE_SELL:
                    d['type'] = "SELL"
                else:
                    d['type'] = str(d['type'])
                
                if d['entry'] == mt5.DEAL_ENTRY_IN:
                    d['entry'] = "IN"
                elif d['entry'] == mt5.DEAL_ENTRY_OUT:
                    d['entry'] = "OUT"
                elif d['entry'] == mt5.DEAL_ENTRY_INOUT:
                    d['entry'] = "INOUT"
                else:
                    d['entry'] = str(d['entry'])

                d['time'] = datetime.fromtimestamp(d['time'])
                result.append(d)
            return result

    def shutdown(self):
        mt5.shutdown()
        self.connected = False

    async def order_check(self, request: dict, login=None, password=None, server=None):
        if not self.connected:
            return None
        async with self.lock:
            if login and password and server:
                if not await self.ensure_connected(login, password, server):
                    return None
            return mt5.order_check(request)

    async def order_send(self, request: dict, login=None, password=None, server=None):
        if not self.connected:
            return None
        async with self.lock:
            if login and password and server:
                if not await self.ensure_connected(login, password, server):
                    return None
            return mt5.order_send(request)

    async def order_calc_margin(self, action, symbol, volume, price, login=None, password=None, server=None):
        if not self.connected:
            return None
        async with self.lock:
            if login and password and server:
                if not await self.ensure_connected(login, password, server):
                    return None
            return mt5.order_calc_margin(action, symbol, volume, price)

    async def order_calc_profit(self, action, symbol, volume, price_open, price_close, login=None, password=None, server=None):
        if not self.connected:
            return None
        async with self.lock:
            if login and password and server:
                if not await self.ensure_connected(login, password, server):
                    return None
            return mt5.order_calc_profit(action, symbol, volume, price_open, price_close)

    async def get_symbol_info(self, symbol: str, login=None, password=None, server=None):
        if not self.connected:
            return None
        async with self.lock:
            if login and password and server:
                if not await self.ensure_connected(login, password, server):
                    return None
            info = mt5.symbol_info(symbol)
            if info:
                return info._asdict()
            return None

    async def get_symbol_tick(self, symbol: str, login=None, password=None, server=None):
        if not self.connected:
            return None
        async with self.lock:
            if login and password and server:
                if not await self.ensure_connected(login, password, server):
                    return None
            tick = mt5.symbol_info_tick(symbol)
            if tick:
                t = tick._asdict()
                t['time'] = datetime.fromtimestamp(t['time'])
                return t
            return None

    async def get_terminal_info(self):
        if not self.connected:
            return None
        async with self.lock:
            info = mt5.terminal_info()
            if info:
                return info._asdict()
            return None

    async def close_position(self, ticket: int, login=None, password=None, server=None):
        if not self.connected:
            return None
        
        async with self.lock:
            if login and password and server:
                if not await self.ensure_connected(login, password, server):
                    return None
            
            # Get position details
            positions = mt5.positions_get(ticket=ticket)
            if not positions:
                return {"retcode": -1, "comment": "Position not found"}
            
            position = positions[0]
            tick = mt5.symbol_info_tick(position.symbol)
            if not tick:
                return {"retcode": -1, "comment": "Symbol tick not found"}
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "position": position.ticket,
                "symbol": position.symbol,
                "volume": position.volume,
                "type": mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
                "price": tick.bid if position.type == mt5.ORDER_TYPE_BUY else tick.ask,
                "deviation": 20,
                "magic": position.magic,
                "comment": "python script close",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            result = mt5.order_send(request)
            if result:
                return result._asdict()
            return None

    async def close_all_positions(self, login=None, password=None, server=None):
        if not self.connected:
            return []
        
        async with self.lock:
            if login and password and server:
                if not await self.ensure_connected(login, password, server):
                    return []
            
            positions = mt5.positions_get()
            if not positions:
                return []
            
            results = []
            for position in positions:
                tick = mt5.symbol_info_tick(position.symbol)
                if not tick:
                    results.append({"ticket": position.ticket, "retcode": -1, "comment": "Symbol tick not found"})
                    continue
                
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "position": position.ticket,
                    "symbol": position.symbol,
                    "volume": position.volume,
                    "type": mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
                    "price": tick.bid if position.type == mt5.ORDER_TYPE_BUY else tick.ask,
                    "deviation": 20,
                    "magic": position.magic,
                    "comment": "python script close all",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }
                
                result = mt5.order_send(request)
                if result:
                    results.append(result._asdict())
                else:
                    results.append({"ticket": position.ticket, "retcode": -1, "comment": "Order send failed"})
            
            return results

mt5_handler = MT5Handler()
