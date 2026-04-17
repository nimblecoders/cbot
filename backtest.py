import pandas as pd
import numpy as np
from datetime import datetime
import pytz

import config
cfg = config.load_config()

INITIAL_BALANCE = 100
RISK_PER_TRADE = 0.02
IST = pytz.timezone("Asia/Kolkata")


# --- LOAD DATA ---
def load_data(symbol):
    df = pd.read_csv(f"{cfg.data_dir}/{symbol}.csv")
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

    for symbol in cfg.trading.symbols:
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

                if candle_strength(row) < cfg.trading.candle_strength_min:
                    continue

                if breakout(prev['close'], row['close'], row['r3'], "buy"):
                    side = "buy"
                elif breakout(prev['close'], row['close'], row['s3'], "sell"):
                    side = "sell"
                else:
                    continue

                entry = row['close']

                sl = entry * (1 - cfg.trading.sl_pct if side == "buy" else 1 + cfg.trading.sl_pct)
                tp = entry * (1 + cfg.trading.tp_pct if side == "buy" else 1 - cfg.trading.tp_pct)

                risk_amt = balance * RISK_PER_TRADE
                qty = risk_amt / abs(entry - sl)

                position = {
                    "side": side,
                    "entry": entry,
                    "sl": sl,
                    "tp": tp,
                    "qty": qty,
                    "symbol": symbol,
                    "entry_date": day
                }

                trade_count_day += 1

            # EXIT
            elif position:
                price = row['close']

                exit_date = row['timestamp'].date()

                if position['side'] == "buy":
                    if price <= position['sl']:
                        pnl = (position['sl'] - position['entry']) * position['qty']
                        balance += pnl
                        trades.append({
                            'symbol': position['symbol'],
                            'side': position['side'],
                            'entry_date': position['entry_date'],
                            'exit_date': exit_date,
                            'pnl': pnl,
                            'win': pnl > 0
                        })
                        position = None

                    elif price >= position['tp']:
                        pnl = (position['tp'] - position['entry']) * position['qty']
                        balance += pnl
                        trades.append({
                            'symbol': position['symbol'],
                            'side': position['side'],
                            'entry_date': position['entry_date'],
                            'exit_date': exit_date,
                            'pnl': pnl,
                            'win': pnl > 0
                        })
                        position = None

                else:
                    if price >= position['sl']:
                        pnl = (position['entry'] - position['sl']) * position['qty']
                        balance += pnl
                        trades.append({
                            'symbol': position['symbol'],
                            'side': position['side'],
                            'entry_date': position['entry_date'],
                            'exit_date': exit_date,
                            'pnl': pnl,
                            'win': pnl > 0
                        })
                        position = None

                    elif price <= position['tp']:
                        pnl = (position['entry'] - position['tp']) * position['qty']
                        balance += pnl
                        trades.append({
                            'symbol': position['symbol'],
                            'side': position['side'],
                            'entry_date': position['entry_date'],
                            'exit_date': exit_date,
                            'pnl': pnl,
                            'win': pnl > 0
                        })
                        position = None

    return trades, balance


# --- REPORT ---
def report(trades, balance):
    pnl_values = [t['pnl'] for t in trades]
    wins = [p for p in pnl_values if p > 0]
    losses = [p for p in pnl_values if p < 0]

    print("\n===== BACKTEST RESULT =====")
    print("Final Balance:", round(balance, 2))
    print("Total Trades:", len(trades))
    print("Win Rate:", round(len(wins)/len(trades)*100, 2) if trades else 0)
    print("Avg Win:", round(np.mean(wins), 2) if wins else 0)
    print("Avg Loss:", round(np.mean(losses), 2) if losses else 0)
    print("===========================\n")


def run_experiments():
    """Run parameter sweeps for optimization."""
    results = []
    
    # Test different SL/TP ratios
    for sl_pct in [0.003, 0.005, 0.007]:
        for tp_pct in [0.008, 0.01, 0.012]:
            cfg.trading.sl_pct = sl_pct
            cfg.trading.tp_pct = tp_pct
            
            trades, balance = run_backtest()
            win_rate = len([t for t in trades if t['win']]) / len(trades) * 100 if trades else 0
            
            results.append({
                'sl_pct': sl_pct,
                'tp_pct': tp_pct,
                'balance': balance,
                'win_rate': win_rate,
                'trades': len(trades)
            })
            print(f"SL:{sl_pct:.1%} TP:{tp_pct:.1%} → Balance: ${balance:.2f} Win: {win_rate:.1f}%")
    
    # Best result
    best = max(results, key=lambda x: x['balance'])
    print(f"\n🏆 BEST: SL:{best['sl_pct']:.1%} TP:{best['tp_pct']:.1%}")
    print(f"Balance: ${best['balance']:.2f} | Win Rate: {best['win_rate']:.1f}%")
    
    return results, best


if __name__ == "__main__":
    print("=== BASELINE ===")
    trades, balance = run_backtest()
    report(trades, balance)
    
    print("\n=== OPTIMIZATION ===")
    experiments, best = run_experiments()
    print("\nOptimization complete!")
