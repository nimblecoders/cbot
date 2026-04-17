from typing import Dict
from datetime import date
import pandas as pd
from .binance_helper import get_binance_symbol, fetch_ohlc
from typing import List


SYMBOLS = ["BTCUSD", "ETHUSD", "SOLUSD", "XRPUSD", "BNBUSD"]


def calculate_camarilla(prev_high: float, prev_low: float, prev_close: float) -> tuple[float, float]:
    """Calculate R3/S3 Camarilla levels."""
    range_hl = prev_high - prev_low
    r3 = prev_close + range_hl * 1.1 / 4
    s3 = prev_close - range_hl * 1.1 / 4
    return r3, s3


def load_daily_levels() -> Dict[str, tuple[float, float]]:
    """Load current day's R3/S3 levels for all symbols from 1d data."""
    levels = {}
    
    for sym in SYMBOLS:
        try:
            bsym = get_binance_symbol(sym)
            df = fetch_ohlc(bsym, "1d", 2)
            prev_day = df.iloc[-2]  # Previous complete day
            
            h, l, c = prev_day['high'], prev_day['low'], prev_day['close']
            r3, s3 = calculate_camarilla(h, l, c)
            levels[sym] = (r3, s3)
            
        except Exception as e:
            print(f"Error loading levels for {sym}: {e}")
    
    print(f"📊 Camarilla levels loaded for {len(levels)} symbols")
    return levels


def get_level(symbol: str, levels: Dict[str, tuple[float, float]]) -> tuple[float, float]:
    """Get R3/S3 for symbol."""
    return levels.get(symbol, (0, 0))
