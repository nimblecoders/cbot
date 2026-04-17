import time
import pandas as pd
from datetime import datetime, timedelta
import pytz
import os

import config
from helpers.binance_helper import get_5m_candles, get_current_price
from helpers.email_helper import send_new_trade_alert, send_sl_hit_alert
from helpers.delta_helper import place_market_order, place_stop_loss, exit_position
from helpers.camarilla_helper import load_daily_levels

from delta_rest_client import DeltaRestClient

cfg = config.load_config()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

# --- CONFIG ---
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

BASE_URL = "https://api.india.delta.exchange"

SYMBOLS = ["BTCUSD", "ETHUSD", "SOLUSD", "XRPUSD", "BNBUSD"]

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


camarilla_levels = None


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
            global camarilla_levels
            camarilla_levels = load_daily_levels()

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
                    df = get_5m_candles(sym, 3)

                    prev_close = df['close'].iloc[-2]
                    curr_close = df['close'].iloc[-1]

                    if candle_strength(df) < 0.0015:
                        continue

                    r3, s3 = camarilla_levels[sym]

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

                    delta_helper.place_market_order(sym, side)

                    position = Position(sym, side, curr_close)

                    send_new_trade_alert(sym, side, curr_close, position.sl, position.tp, cfg.trading.order_size, PRODUCT_MAP[sym], 'R3' if side == 'buy' else 'S3')

                    place_stop_loss(sym, side, position.sl)

                    limiter.record()
                    last_trade_time = now
                    break

            # --- MANAGEMENT ---
            else:
                sym = position.symbol
                pid = PRODUCT_MAP[sym]

                price = get_current_price(sym)
                position.update(price)

                if price <= position.sl if position.side == "buy" else price >= position.sl:
                    print(f"Exit {position.side.upper()} SL")
                    exit_position(sym, position.side)
                    send_sl_hit_alert(sym, position.side, position.entry, price)
                    position = None

            time.sleep(20)

        except Exception as e:
            print("ERROR:", e)
            time.sleep(5)


if __name__ == "__main__":
    run()
