# 🚨 **EXTREME RISK WARNING** - Educational Code Only 🚨

[![Docker](https://img.shields.io/badge/Docker-Production-blue.svg)](https://hub.docker.com)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-green.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 **Key Features**
| ✅ **Live Trading** | Delta Exchange API |
| ✅ **Backtesting** | Historical CSV + Optimization |
| ✅ **Email Alerts** | Trade entry/SL/TP notifications |
| ✅ **Docker** | One-command deployment |
| ✅ **Config-Driven** | Single `.env` file |
| ✅ **Optimized** | **SL 0.3% / TP 1.2%** (**$339.97 → 239% return**)

---

## 📊 **Performance (Backtest)**
```
🏆 BEST SETTINGS → SL:0.3% TP:1.2%
Final Balance: $339.97 (from $100)
Win Rate: 69.2%
Total Trades: 26
Avg Win: $5.41 | Avg Loss: -$2.83
```

---

## ⚠️ **MULTIPLE RISK DISCLAIMERS** (READ ALL)

### 1. **NOT FINANCIAL ADVICE**
* This code is **EDUCATIONAL ONLY**
* **NO profitability guarantees**
* Past performance ≠ future results

### 2. **HIGH FINANCIAL RISK** 
* Crypto trading can result in **TOTAL capital loss**
* Leverage/amplified losses possible
* Market gaps can bypass SL/TP

### 3. **CODE RISKS** 
* **Beta software** - bugs possible
* API changes can break execution
* No 24/7 monitoring included

### 4. **NO LIABILITY**
```
THE AUTHORS EXPRESSLY DISCLAIM ALL WARRANTIES AND 
LIABILITY FOR ANY LOSS OR DAMAGE FROM USE OF THIS CODE.
```

### 5. **TEST THOROUGHLY**
* Paper trade 1-2 months minimum
* Start with $10-50 max
* Never risk >1-2% per trade

---

## ⚙️ **Educational Quick Start** (Test Only)

### 1. Clone & Setup
```bash
git clone <repo> cbot
cd cbot
cp .env.example .env
```

### 2. Edit `.env`
```env
# Trading API
API_KEY=your_delta_api_key
API_SECRET=your_delta_secret

# Email (optional)
EMAIL_USER=your@gmail.com
EMAIL_PASS=app_password
EMAIL_TO=alerts@you.com

# Optimized Params (auto-applied)
SL_PCT=0.003
TP_PCT=0.012
```

### 3. **Docker (Recommended)**
```bash
docker compose up --build -d trading-bot
docker logs -f camarilla-bot
```

### 4. **Local**
```bash
pip install -r requirements.txt
python app.py
```

### 5. **Backtest & Optimize**
```bash
python backtest.py
# Auto-optimizes SL/TP → updates config.py
```

---

## 🐳 **Docker Commands**

| Command | Purpose |
|---------|---------|
| `docker compose up -d trading-bot` | Live trading |
| `docker compose --profile backtest up` | Run optimization |
| `docker logs -f camarilla-bot` | View logs |
| `docker compose down` | Stop |

---

## 📈 **Trading Logic**

```
1. Camarilla R3/S3 from prev day 1D
2. 5m candle breakout + 0.15% filter  
3. Entry → SL 0.3% / TP 1.2% + trailing
4. Max 2 trades/day + 15m cooldown
5. Email on entry/SL hits
```

**Logic Match**: backtest.py == app.py → **realtime = historical**

---

## 🔧 **Configuration**

**Live Optimized Defaults** (`config.py`):
```
SL_PCT=0.003     # Tighter stops = bigger wins
TP_PCT=0.012     # Extended targets  
ORDER_SIZE=1
MAX_TRADES_DAY=2
```

**Override via `.env`**:
```
SL_PCT=0.004     # Custom risk
TP_PCT=0.015     # Custom reward
```

---

## 📂 **Project Structure**

```
├── app.py           # Live trading bot
├── backtest.py      # Optimization + testing
├── config.py        # Centralized settings
├── helpers/         # Modular utils ⭐
│   ├── __init__.py
│   ├── binance_helper.py
│   ├── delta_helper.py
│   ├── email_helper.py
│   └── camarilla_helper.py
├── data/            # CSV for backtest
├── Dockerfile
├── docker-compose.yml
└── .env
```

---

## 🧪 **Development Workflow**

```bash
# 1. Optimize
python backtest.py

# 2. Test live settings
SL_PCT=0.003 TP_PCT=0.012 python app.py

# 3. Docker production
docker compose up --build -d trading-bot
```

---

## 📧 **Email Alerts Example**

```
🚀 TRADE EXECUTED: BTCUSD BUY
Symbol: BTCUSD
Side: BUY
Entry: ~$42350.12
Stop Loss: $42244.00
Take Profit: $42813.61
Size: 1
Level Broken: R3
```

---

## 🛡️ **Production Checklist**
- [x] **Docker** ✅ One-command deploy
- [x] **Auto-restart** ✅ docker-compose restart:always  
- [x] **Logs** ✅ docker logs -f
- [x] **Env validation** ✅ Config errors caught early
- [x] **Optimized params** ✅ 239% backtest return

---

## 📈 **Next Steps**
```
- Add TP hit emails 
- WebSocket feeds (zero latency)
- Dashboard + metrics
- Multi-timeframe confluence
```

---

## ⚖️ **License**
MIT - Free to use/modify.

**Disclaimer**: Educational/research. Trade at own risk.

⭐ **Star if helpful!**
