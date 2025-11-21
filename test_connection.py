import MetaTrader5 as mt5
from config import Config
import time

def test_connection():
    print("Testing MT5 Connection...")
    print(f"Path: {Config.MT5_PATH}")
    
    if not mt5.initialize(path=Config.MT5_PATH):
        print("initialize() failed, error code =", mt5.last_error())
        return

    print("MT5 Initialized")
    
    # Attempt login if credentials are set
    if Config.MT5_LOGIN and Config.MT5_PASSWORD and Config.MT5_SERVER:
        print(f"Attempting login to {Config.MT5_LOGIN} on {Config.MT5_SERVER}...")
        authorized = mt5.login(Config.MT5_LOGIN, password=Config.MT5_PASSWORD, server=Config.MT5_SERVER)
        if authorized:
            print("Login Successful")
            info = mt5.account_info()
            if info:
                print(f"Balance: {info.balance}")
                print(f"Equity: {info.equity}")
            else:
                print("Failed to get account info")
        else:
            print("Login Failed, error code =", mt5.last_error())
    else:
        print("Skipping login (credentials not fully set in .env)")

    mt5.shutdown()
    print("Test Complete")

if __name__ == "__main__":
    test_connection()
