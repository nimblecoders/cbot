import pandas as pd
import requests
from typing import Dict

BINANCE_MAP: Dict[str, str] = {
    "BTCUSD": "BTCUSDT",
    "ETHUSD": "ETHUSDT", 
    "SOLUSD": "SOLUSDT",
    "XRPUSD": "XRPUSDT",
    "BNBUSD": "BNBUSDT"
}


def get_binance_symbol(symbol: str) -> str:
    """Get Binance equivalent symbol."""
    if symbol not in BINANCE_MAP:
        raise ValueError(f"Unknown symbol: {symbol}")
    return BINANCE_MAP[symbol]


def fetch_ohlc(symbol_binance: str, interval: str = "5m", limit: int = 3) -> pd.DataFrame:
    """Fetch OHLCV from Binance API."""
    url = "https://api.binance.com/api/v3/klines"
    params = {'symbol': symbol_binance, 'interval': interval, 'limit': limit}
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    data = response.json()
    df = pd.DataFrame(data, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_volume', 'trades', 'taker_buy_base',
        'taker_buy_quote', 'ignore'
    ])
    
    numeric_cols = ['open', 'high', 'low', 'close', 'volume']
    df[numeric_cols] = df[numeric_cols].astype(float)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    return df


def get_5m_candles(symbol: str, limit: int = 3) -> pd.DataFrame:
    """Get recent 5m candles for symbol."""
    bsym = get_binance_symbol(symbol)
    return fetch_ohlc(bsym, "5m", limit)


def get_current_price(symbol: str) -> float:
    """Get latest price from 5m candle."""
    df = get_5m_candles(symbol, 1)
    return float(df['close'].iloc[-1])
