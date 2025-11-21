# MT5 API Server Documentation

Base URL: `http://localhost:8000` (or your public URL)

## Authentication & Connection

### Initialize Connection
**POST** `/connect`

Initializes the MT5 terminal connection and logs in.

**Request Body** (`application/json`):
```json
{
  "login": 12345678,       // Optional: MT5 Login ID
  "password": "pass",      // Optional: MT5 Password
  "server": "Broker-Server", // Optional: Broker Server Name
  "path": "C:\\..."        // Optional: Path to terminal64.exe
}
```

**Response**:
```json
{
  "status": "connected"
}
```

---

## Account Information

### Get Account Info
**GET** `/account`

Returns current account details (balance, equity, etc.).

**Response**:
```json
{
  "login": 12345678,
  "balance": 10000.0,
  "equity": 10000.0,
  "profit": 0.0,
  "margin": 0.0,
  "margin_free": 10000.0,
  "margin_level": 0.0,
  "currency": "USD",
  "server": "Broker-Server",
  "company": "Broker Name",
  "name": "Client Name"
}
```

### Get Open Positions
**GET** `/positions`

Returns a list of currently open positions.

**Response** (`Array`):
```json
[
  {
    "ticket": 123456,
    "symbol": "EURUSD",
    "type": "BUY",       // "BUY" or "SELL"
    "volume": 0.1,
    "price_open": 1.1050,
    "sl": 0.0,
    "tp": 0.0,
    "price_current": 1.1055,
    "profit": 5.0,
    "time": "2023-10-27T10:00:00",
    "comment": ""
  }
]
```

### Get Trade History
**GET** `/history`

Returns historical deals.

**Query Parameters**:
- `days` (int, default=30): Number of days to look back.

**Response** (`Array`):
```json
[
  {
    "ticket": 123455,
    "order": 1001,
    "time": "2023-10-26T15:30:00",
    "type": "BUY",
    "entry": "IN",
    "symbol": "EURUSD",
    "volume": 0.1,
    "price": 1.1000,
    "profit": 0.0,
    "commission": -0.7,
    "swap": 0.0,
    "comment": ""
  }
]
```

---

## Trading & Orders

### Place Order
**POST** `/trade/order`

Sends a trade request to the terminal.

#### Example: Market Buy Order
```json
{
  "action": 1,           // 1 = Market Deal
  "symbol": "EURUSD",
  "volume": 0.01,
  "type": 0,             // 0 = BUY
  "comment": "Market Buy"
}
```

#### Example: Market Sell Order
```json
{
  "action": 1,           // 1 = Market Deal
  "symbol": "EURUSD",
  "volume": 0.01,
  "type": 1,             // 1 = SELL
  "comment": "Market Sell"
}
```

#### Example: Pending Limit Order
```json
{
  "action": 5,           // 5 = Pending Order
  "symbol": "EURUSD",
  "volume": 0.01,
  "type": 2,             // 2 = BUY LIMIT
  "price": 1.0500,       // Target Price
  "sl": 1.0400,
  "tp": 1.0600
}
```

**Request Body Parameters**:
- `action`: 1 (Market), 5 (Pending)
- `type`: 0 (Buy), 1 (Sell), 2 (Buy Limit), 3 (Sell Limit), 4 (Buy Stop), 5 (Sell Stop)

**Response**:
```json
{
  "retcode": 10009,      // 10009 = Done
  "deal": 123457,
  "order": 123457,
  "volume": 0.1,
  "price": 1.1050,
  "comment": "Request executed"
}
```

### Check Order
**POST** `/trade/check`

Checks if an order is valid and calculates margin requirements without placing it.

**Request Body**: Same as `/trade/order`.

**Response**: Same as `/trade/order`.

### Calculate Margin
**POST** `/trade/calc_margin`

**Query Parameters**:
- `action` (int): Order type (0=BUY, 1=SELL)
- `symbol` (str): e.g., "EURUSD"
### Get Symbol Info
**GET** `/market/symbol/{symbol}`

Returns detailed specification for a symbol.

**Response**:
```json
{
  "symbol": "EURUSD",
  "digits": 5,
  "spread": 10,
  "ask": 1.1055,
  "bid": 1.1054,
  "point": 0.00001,
  "trade_tick_value": 1.0,
  "description": "Euro vs US Dollar"
  // ... other fields
}
```

### Get Latest Tick
**GET** `/market/tick/{symbol}`

Returns the latest price tick.

**Response**:
```json
{
  "time": "2023-10-27T10:05:00",
  "bid": 1.1054,
  "ask": 1.1055,
  "last": 1.1055,
  "volume": 5
}

---

## Real-time WebSockets

### Stream Positions
**URL**: `ws://localhost:8000/ws/positions`

Streams the list of open positions every 1 second.

**Message Format** (JSON Array):
```json
[
  {
    "ticket": 123456,
    "symbol": "EURUSD",
    "profit": 5.0,
    ...
  }
]
```

### Stream Price
**URL**: `ws://localhost:8000/ws/price/{symbol}`

Streams the latest tick for a specific symbol every 1 second.

**Message Format** (JSON Object):
```json
{
  "time": "2023-10-27 10:00:00",
  "bid": 1.1050,
  "ask": 1.1051,
  "last": 1.1051,
  "volume": 10
}
``````
