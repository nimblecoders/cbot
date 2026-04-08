# 📊 Camarilla Crypto Trading Bot (Educational Project)

## ⚠️ Disclaimer

This project is created strictly for **educational and learning purposes only**.

* ❌ This is **NOT production-ready software**
* ❌ This is **NOT financial advice**
* ❌ This project is **under active development and testing**

---

## 🚫 Risk Warning

Trading cryptocurrencies involves significant financial risk.

By using this repository, you acknowledge that:

* You may incur **partial or total loss of capital**
* Market conditions can change rapidly and unpredictably
* No guarantees of profitability are provided

---

## 🛑 Liability Disclaimer

* The **author(s)** of this repository are **NOT responsible** for any financial losses
* The **contributors** are **NOT liable** for misuse of this code
* This repository should **NOT be used for

# ⚙️ Setup & Installation Guide

This guide walks you through setting up and running the Camarilla Crypto Bot for **educational purposes only**.

---

## 📦 Prerequisites

Ensure you have the following installed:

* Python **3.10+**
* Docker (optional but recommended)
* Git
* A Delta Exchange account (for API keys)

---

## 🔑 Step 1: Get API Credentials

1. Log in to your Delta Exchange account
2. Navigate to API Management
3. Create a new API key
4. Copy:

   * `API_KEY`
   * `API_SECRET`

⚠️ **Never share your API credentials**

---

## 📁 Step 2: Clone Repository

```bash
git clone <your-repo-url>
cd project
```

---

## 🧾 Step 3: Create Environment File

Create a `.env` file in the root directory:

```env
API_KEY=your_api_key_here
API_SECRET=your_api_secret_here
```

---

## 🐍 Step 4: Install Dependencies (Local Setup)

```bash
pip install -r requirements.txt
```

---

## ▶️ Step 5: Run Trading Bot

```bash
python app.py
```

---

## 📊 Step 6: Run Backtesting

Make sure historical data exists in `/data` folder.

```bash
python backtest.py
```

---

## 🐳 Step 7: Run with Docker (Recommended)

### Build Image

```bash
docker build -t crypto-bot .
```

---

### Run Bot

```bash
docker run -d --env-file .env --name bot crypto-bot
```

---

### Run Backtest in Docker

```bash
docker run --env-file .env crypto-bot python backtest.py
```

---

## 🔄 Step 8: Auto Restart (Important)

Run container with restart policy:

```bash
docker run -d --restart=always --env-file .env crypto-bot
```

---

## 📂 Step 9: Data Setup for Backtesting

Create a `data/` folder:

```bash
mkdir data
```

Add CSV files like:

```
data/BTCUSD.csv
data/ETHUSD.csv
```

---

### CSV Format (Required)

```csv
timestamp,open,high,low,close,volume
2024-01-01 00:00:00,42000,42100,41950,42050,123
```

---

## 🧪 Step 10: Verify Everything

* Bot runs without errors
* API connection works
* Backtest outputs results

---

## ⚠️ Final Notes

* Start with **small or zero capital**
* Validate strategy using backtesting first
* Monitor logs continuously
* This project is **not production safe**

---



# 🐳 Docker Compose Setup Guide

This guide explains how to run the Camarilla Crypto Bot and Backtesting system using **Docker Compose**.

---

## 📦 Overview

The project uses Docker Compose to manage two services:

* **trading-bot** → Runs the live strategy (app.py)
* **backtest** → Runs backtesting (backtest.py) on demand

---

## 📁 Project Structure

```bash
project/
│── app.py
│── backtest.py
│── Dockerfile
│── docker-compose.yml
│── requirements.txt
│── .env
│── data/
│── logs/
```

---

## ⚙️ Prerequisites

Make sure you have:

* Docker installed
* Docker Compose installed (v2+)
* API credentials from Delta Exchange

---

## 🔑 Step 1: Configure Environment

Create a `.env` file:

```env
API_KEY=your_api_key_here
API_SECRET=your_api_secret_here
```

---

## 📊 Step 2: Prepare Backtesting Data (Optional)

Create a data folder:

```bash
mkdir data
```

Add CSV files:

```bash
data/BTCUSD.csv
data/ETHUSD.csv
```

### CSV Format

```csv
timestamp,open,high,low,close,volume
2024-01-01 00:00:00,42000,42100,41950,42050,123
```

---

## 🚀 Step 3: Build Containers

```bash
docker compose build
```

---

## ▶️ Step 4: Run Trading Bot

```bash
docker compose up -d trading-bot
```

* Runs in background
* Auto-restarts on failure

---

## 📈 Step 5: Run Backtesting

```bash
docker compose --profile backtest up backtest
```

* Runs once and exits
* Prints results in terminal

---

## 🛑 Step 6: Stop Services

```bash
docker compose down
```

---

## 🔄 Step 7: Rebuild After Changes

```bash
docker compose up --build -d
```

---

## 📜 Logs

View bot logs:

```bash
docker logs -f camarilla-bot
```

---

## 🔧 Optional Improvements

* Add persistent logging in `/logs`
* Add monitoring tools (Grafana, Prometheus)
* Add alert system (Telegram)

---

## ⚠️ Important Notes

* Ensure correct **PRODUCT_ID mapping**
* Verify symbol names (BTCUSD, ETHUSD, etc.)
* Always test with **backtesting before live run**
* Use small capital if testing live

---

## 🧪 Development Workflow

1. Modify code
2. Rebuild container
3. Test using backtest
4. Deploy bot

---

## 🚨 Disclaimer

* This project is for **educational purposes only**
* Not intended for production use
* No responsibility for financial losses

---

## 📌 Next Steps

* Add WebSocket for real-time trading
* Improve backtesting accuracy
* Add trade analytics dashboard

---

