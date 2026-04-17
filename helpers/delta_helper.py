from delta_rest_client import DeltaRestClient
import os

# Config
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
BASE_URL = "https://api.india.delta.exchange"

PRODUCT_MAP = {
    "BTCUSD": 27,
    "ETHUSD": 28,
    "SOLUSD": 29,
    "XRPUSD": 30,
    "BNBUSD": 31
}

ORDER_SIZE = 1

_client = None


def get_client():
    """Lazy init Delta client."""
    global _client
    if _client is None and API_KEY and API_SECRET:
        _client = DeltaRestClient(BASE_URL, API_KEY, API_SECRET)
    return _client


def place_market_order(symbol: str, side: str):
    """Place market order."""
    client = get_client()
    if not client:
        raise ValueError("Delta client not initialized - check API_KEY/API_SECRET")
    
    pid = PRODUCT_MAP.get(symbol)
    if not pid:
        raise ValueError(f"Unknown symbol: {symbol}")
    
    return client.place_order(
        product_id=pid,
        size=ORDER_SIZE,
        side=side,
        order_type="market"
    )


def place_stop_loss(symbol: str, side: str, stop_price: float):
    """Place SL order."""
    client = get_client()
    if not client:
        raise ValueError("Delta client not initialized")
    
    pid = PRODUCT_MAP.get(symbol)
    sl_side = "sell" if side == "buy" else "buy"
    
    return client.place_stop_order(
        product_id=pid,
        size=ORDER_SIZE,
        side=sl_side,
        stop_price=str(stop_price),
        order_type="market"
    )


def exit_position(symbol: str, position_side: str):
    """Exit current position (market order opposite side)."""
    exit_side = "sell" if position_side == "buy" else "buy"
    return place_market_order(symbol, exit_side)
