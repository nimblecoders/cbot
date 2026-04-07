import time
import pandas as pd
from datetime import datetime, timedelta
import pytz
import os

from delta_rest_client import DeltaRestClient

# --- CONFIG ---
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

BASE_URL = "https://api.india.delta.exchange"

SYMBOLS = ["BTCUSD", "ETHUSD", "SOLUSD", "XRPUSD", "BNBUSD"]

PRODUCT_MAP = {
    "BTCUSD": 27,
    "ETHUSD": 28,
    "SOLUSD": 29,
    "XRPUSD": 30,
    "BNBUSD": 31
}

ORDER_SIZE = 1
SL_PCT = 0.005
TP_PCT = 0.01

IST = pytz.timezone("Asia/Kolkata")

client = DeltaRestClient(BASE_URL, API_KEY, API_SECRET)

# --- TRADE LIMITER ---
class TradeLimiter:
    def __init__(self):
        self.count = 0
        self.day = self.today()

    def today(self):
        return datetime.now(IST).date()

    def reset(self):
        if self.today() != self.day:
            self.day = self.today()
            self.count = 0

    def can_trade(self):
        self.reset()
        return self.count < 2

    def record(self):
        self.count += 1


# --- POSITION ---
class Position:
    def __init__(self, symbol, side, entry):
        self.symbol = symbol
        self.side = side
        self.entry = entry
        self.sl = entry * (1 - SL_PCT if side == "buy" else 1 + SL_PCT)
        self.tp = entry * (1 + TP_PCT if side == "buy" else 1 - TP_PCT)
        self.trailing = False

    def update(self, price):
        if self.side == "buy":
            if not self.trailing and price >= self.tp:
                self.trailing = True
                self.sl = self.entry
            elif self.trailing:
                self.sl = max(self.sl, price * (1 - SL_PCT))
        else:
            if not self.trailing and price <= self.tp:
                self.trailing = True
                self.sl = self.entry
            elif self.trailing:
                self.sl = min(self.sl, price * (1 + SL_PCT))


# --- GLOBAL STATE ---
camarilla = {}
current_day = None
last_trade_time = None


# --- HELPERS ---
def load_levels():
    global camarilla, current_day

    today = datetime.now(IST).date()
    if current_day == today:
        return

    camarilla = {}

    for sym in SYMBOLS:
        df = pd.DataFrame(client.get_candles(sym, "1d", limit=2))
        prev = df.iloc[-2]

        h, l, c = float(prev['high']), float(prev['low']), float(prev['close'])

        r3 = c + (h - l) * 1.1 / 4
        s3 = c - (h - l) * 1.1 / 4

        camarilla[sym] = (r3, s3)

    current_day = today
    print("Camarilla updated")


def valid_breakout(prev_close, curr_close, level, side):
    breakout_pct = abs(curr_close - level) / level

    if breakout_pct < 0.001:  # 0.1% filter
        return False

    if side == "buy":
        return prev_close <= level and curr_close > level
    else:
        return prev_close >= level and curr_close < level


def candle_strength(df):
    o = float(df.iloc[-1]['open'])
    c = float(df.iloc[-1]['close'])
    return abs(c - o) / o


def get_price(symbol):
    df = client.get_candles(symbol, "5m", limit=1)
    return float(df[0]['close'])


def place_market(pid, side):
    return client.place_order(
        product_id=pid,
        size=ORDER_SIZE,
        side=side,
        order_type="market"
    )


def place_sl(pid, side, price):
    sl_side = "sell" if side == "buy" else "buy"
    return client.place_stop_order(
        product_id=pid,
        size=ORDER_SIZE,
        side=sl_side,
        stop_price=str(price),
        order_type="market"
    )


# --- MAIN ---
def run():
    global last_trade_time

    limiter = TradeLimiter()
    position = None

    while True:
        try:
            load_levels()

            now = datetime.now(IST)

            # run only on 5m close
            if now.minute % 5 != 0:
                time.sleep(15)
                continue

            # cooldown
            if last_trade_time and now - last_trade_time < timedelta(minutes=15):
                print("Cooldown active")
                time.sleep(30)
                continue

            # --- ENTRY ---
            if position is None:
                for sym in SYMBOLS:
                    df = pd.DataFrame(client.get_candles(sym, "5m", limit=3))

                    prev_close = float(df.iloc[-2]['close'])
                    curr_close = float(df.iloc[-1]['close'])

                    if candle_strength(df) < 0.0015:
                        continue

                    r3, s3 = camarilla[sym]

                    if valid_breakout(prev_close, curr_close, r3, "buy"):
                        side = "buy"
                    elif valid_breakout(prev_close, curr_close, s3, "sell"):
                        side = "sell"
                    else:
                        continue

                    if not limiter.can_trade():
                        print("Trade limit reached")
                        break

                    pid = PRODUCT_MAP[sym]

                    print(f"TRADE {sym} {side}")

                    place_market(pid, side)

                    position = Position(sym, side, curr_close)

                    place_sl(pid, side, position.sl)

                    limiter.record()
                    last_trade_time = now
                    break

            # --- MANAGEMENT ---
            else:
                sym = position.symbol
                pid = PRODUCT_MAP[sym]

                price = get_price(sym)
                position.update(price)

                if position.side == "buy" and price <= position.sl:
                    place_market(pid, "sell")
                    print("Exit BUY SL")
                    position = None

                elif position.side == "sell" and price >= position.sl:
                    place_market(pid, "buy")
                    print("Exit SELL SL")
                    position = None

            time.sleep(20)

        except Exception as e:
            print("ERROR:", e)
            time.sleep(5)


if __name__ == "__main__":
    run()
