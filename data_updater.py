import pandas as pd
import requests
import argparse
from datetime import datetime, timedelta
import time

SYMBOLS = ['BTCUSD', 'ETHUSD', 'SOLUSD', 'XRPUSD', 'BNBUSD']

def fetch_klines(symbol, limit=2):
    """Fetch N daily klines from Binance API"""
    binance_symbol = symbol.replace('USD', 'USDT')
    url = "https://api.binance.com/api/v3/klines"
    params = {'symbol': binance_symbol, 'interval': '1d', 'limit': str(limit)}
    
    try:
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        klines = []
        for kline in data:
            ts_ms = int(kline[0])
            O, H, L, C, V = map(float, kline[1:6])
            klines.append((ts_ms, O, H, L, C, V))
        return klines
    except Exception as e:
        print(f"Error fetching {binance_symbol}: {e}")
        return []

def append_new_data(symbol, days):
    csv_path = f"data/{symbol}.csv"
    
    # Load existing
    try:
        df = pd.read_csv(csv_path)
        existing_dates = set(pd.to_datetime(df['timestamp']).dt.date)
        print(f"{symbol} existing rows: {len(df)}")
    except:
        df = pd.DataFrame()
        existing_dates = set()
    
    limit = days + 10  # buffer
    klines = fetch_klines(symbol, limit)
    if not klines:
        print(f"No data for {symbol}")
        return
    
    appended = 0
    for ts_ms, O, H, L, C, V in reversed(klines):  # oldest first
        new_ts = datetime.fromtimestamp(ts_ms / 1000).strftime('%Y-%m-%d 00:00:00')
        new_date = datetime.fromtimestamp(ts_ms / 1000).date()
        
        if new_date not in existing_dates:
            new_row = {
                'timestamp': new_ts,
                'open': round(O, 2),
                'high': round(H, 2),
                'low': round(L, 2),
                'close': round(C, 2),
                'volume': int(V)
            }
            new_df = pd.DataFrame([new_row])
            new_df.to_csv(csv_path, mode='a', header=False, index=False)
            existing_dates.add(new_date)
            appended += 1
            print(f"Appended {new_ts} to {csv_path}")
    
    print(f"{symbol}: appended {appended} new rows")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update crypto CSV data")
    parser.add_argument('--days', type=int, default=1, help="Days of historical data to fetch (default 1=latest)")
    args = parser.parse_args()
    
    for symbol in SYMBOLS:
        append_new_data(symbol, args.days)
        time.sleep(0.2)
    print("Update complete!")

