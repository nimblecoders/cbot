import pandas as pd
import numpy as np
from datetime import datetime
import pytz

# --- CONFIG ---
SYMBOLS = ["BTCUSD", "ETHUSD", "SOLUSD", "XRPUSD", "BNBUSD"]

SL_PCT = 0.005
TP_PCT = 0.01

INITIAL_BALANCE = 10000
RISK_PER_TRADE = 0.02  # 2%

IST = pytz.timezone("Asia/Kolkata")


# --- LOAD DATA ---
def load_data(symbol):
    # Expect CSV: timestamp,open,high,low,close,volume
    df = pd.read_csv(f"data/{symbol}.csv")
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df


# --- CAMARILLA ---
def camarilla(df):
    df['r3'] = np.nan
    df['s3'] = np.nan

    df['date'] = df['timestamp'].dt.date

    for d in df['date'].unique():
        day_df = df[df['date'] == d]
        prev_day = df[df['date'] < d]

        if prev_day.empty:
            continue

        prev = prev_day.iloc[-1]

        h, l, c = prev['high'], prev['low'], prev['close']

        r3 = c + (h - l) * 1.1 / 4
        s3 = c - (h - l) * 1.1 / 4

        df.loc[df['date'] == d, 'r3'] = r3
        df.loc[df['date'] == d, 's3'] = s3

    return df


# --- SIGNAL ---
def breakout(prev_close, curr_close, level, side):
    pct = abs(curr_close - level) / level
    if pct < 0.001:
        return False

    if side == "buy":
        return prev_close <= level and curr_close > level
    else:
        return prev_close >= level and curr_close < level


def candle_strength(row):
    return abs(row['close'] - row['open']) / row['open']


# --- BACKTEST ---
def run_backtest():
    balance = INITIAL_BALANCE
    trades = []

    trade_count_day = 0
    current_day = None

    for symbol in SYMBOLS:
        df = load_data(symbol)
        df = camarilla(df)

        position = None

        for i in range(2, len(df)):
            row = df.iloc[i]
            prev = df.iloc[i - 1]

            day = row['timestamp'].date()

            # Reset daily trade count
            if current_day != day:
                current_day = day
                trade_count_day = 0

            if pd.isna(row['r3']):
                continue

            # ENTRY
            if position is None and trade_count_day < 2:

                if candle_strength(row) < 0.0015:
                    continue

                if breakout(prev['close'], row['close'], row['r3'], "buy"):
                    side = "buy"
                elif breakout(prev['close'], row['close'], row['s3'], "sell"):
                    side = "sell"
                else:
                    continue

                entry = row['close']

                sl = entry * (1 - SL_PCT if side == "buy" else 1 + SL_PCT)
                tp = entry * (1 + TP_PCT if side == "buy" else 1 - TP_PCT)

                risk_amt = balance * RISK_PER_TRADE
                qty = risk_amt / abs(entry - sl)

                position = {
                    "side": side,
                    "entry": entry,
                    "sl": sl,
                    "tp": tp,
                    "qty": qty
                }

                trade_count_day += 1

            # EXIT
            elif position:
                price = row['close']

                if position['side'] == "buy":
                    if price <= position['sl']:
                        pnl = (position['sl'] - position['entry']) * position['qty']
                        balance += pnl
                        trades.append(pnl)
                        position = None

                    elif price >= position['tp']:
                        pnl = (position['tp'] - position['entry']) * position['qty']
                        balance += pnl
                        trades.append(pnl)
                        position = None

                else:
                    if price >= position['sl']:
                        pnl = (position['entry'] - position['sl']) * position['qty']
                        balance += pnl
                        trades.append(pnl)
                        position = None

                    elif price <= position['tp']:
                        pnl = (position['entry'] - position['tp']) * position['qty']
                        balance += pnl
                        trades.append(pnl)
                        position = None

    return trades, balance


# --- REPORT ---
def report(trades, balance):
    wins = [t for t in trades if t > 0]
    losses = [t for t in trades if t < 0]

    print("\n===== BACKTEST RESULT =====")
    print("Final Balance:", round(balance, 2))
    print("Total Trades:", len(trades))
    print("Win Rate:", round(len(wins)/len(trades)*100, 2) if trades else 0)
    print("Avg Win:", round(np.mean(wins), 2) if wins else 0)
    print("Avg Loss:", round(np.mean(losses), 2) if losses else 0)
    print("===========================\n")


if __name__ == "__main__":
    trades, balance = run_backtest()
    report(trades, balance)
