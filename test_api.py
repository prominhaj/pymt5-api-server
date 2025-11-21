import requests
import time
import sys

BASE_URL = "http://localhost:8000"

def test_endpoint(method, endpoint, data=None, expected_status=200):
    url = f"{BASE_URL}{endpoint}"
    print(f"Testing {method} {endpoint}...", end=" ")
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        if response.status_code == expected_status:
            print("OK")
            return response.json()
        else:
            print(f"FAILED (Status: {response.status_code})")
            print(response.text)
            return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None

def run_tests():
    # Wait for server to be up
    print("Waiting for server...")
    for _ in range(5):
        try:
            requests.get(f"{BASE_URL}/docs")
            break
        except:
            time.sleep(1)
    
    # 1. Account Info
    account = test_endpoint("GET", "/account")
    if account:
        print(f"  Account: {account.get('login')} | Balance: {account.get('balance')}")

    # 2. Positions
    positions = test_endpoint("GET", "/positions")
    if positions is not None:
        print(f"  Positions count: {len(positions)}")

    # 3. History
    history = test_endpoint("GET", "/history?days=1")
    if history is not None:
        print(f"  History count (last 1 day): {len(history)}")

    # 4. Symbol Info (Try USDRUB)
    symbol = "USDRUB"
    sym_info = test_endpoint("GET", f"/market/symbol/{symbol}")
    if sym_info:
        print(f"  Symbol {symbol}: Bid={sym_info.get('bid')}, Ask={sym_info.get('ask')}")
    else:
        # Try another symbol if EURUSD fails, or just ignore
        pass

    # 5. Calc Margin
    margin_req = {
        "action": 0, # BUY
        "symbol": "USDRUB",
        "volume": 1.0,
        "price": 1.1000
    }
    # Note: calc_margin is a POST in my implementation but takes query params in the function signature?
    # Let's check main.py implementation.
    # @app.post("/trade/calc_margin")
    # async def calc_margin(action: int, symbol: str, volume: float, price: float):
    # FastAPI will expect these as query params if not specified as Body.
    # Let's try sending as query params.
    
    print(f"Testing POST /trade/calc_margin...", end=" ")
    try:
        response = requests.post(f"{BASE_URL}/trade/calc_margin", params=margin_req)
        if response.status_code == 200:
            print("OK")
            print(f"  Margin: {response.json().get('margin')}")
        else:
            print(f"FAILED (Status: {response.status_code})")
            print(response.text)
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    run_tests()
