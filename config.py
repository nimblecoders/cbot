"""Central configuration for trading bot."""
import os
from typing import Dict, List, Any
from dataclasses import dataclass
from pathlib import Path

@dataclass
class TradingConfig:
    """Trading parameters."""
    symbols: List[str] = None
    order_size: float = 1.0
    sl_pct: float = 0.005
    tp_pct: float = 0.01
    max_trades_day: int = 2
    cooldown_minutes: int = 15
    candle_strength_min: float = 0.0015
    breakout_min_pct: float = 0.001
    

@dataclass
class ExchangeConfig:
    """Exchange settings."""
    delta_base_url: str = "https://api.india.delta.exchange"
    delta_product_map: Dict[str, int] = None
    binance_map: Dict[str, str] = None
    

@dataclass
class EmailConfig:
    """Email settings."""
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    email_user: str = None
    email_pass: str = None
    email_to: str = None
    

@dataclass
class AppConfig:
    """Main app config."""
    trading: TradingConfig = None
    delta: ExchangeConfig = None
    email: EmailConfig = None
    data_dir: Path = Path("data")


def load_config() -> AppConfig:
    """Load from env vars."""
    
    # Trading
    trading = TradingConfig(
        symbols=["BTCUSD", "ETHUSD", "SOLUSD", "XRPUSD", "BNBUSD"],
        order_size=float(os.getenv("ORDER_SIZE", "1")),
        sl_pct=float(os.getenv("SL_PCT", "0.003")),      # 🏆 OPTIMIZED: Backtest $339.97 (SL 0.3%)
        tp_pct=float(os.getenv("TP_PCT", "0.012")),      # 🏆 OPTIMIZED: Backtest $339.97 (TP 1.2%)
        max_trades_day=int(os.getenv("MAX_TRADES_DAY", "2")),
        cooldown_minutes=int(os.getenv("COOLDOWN_MINUTES", "15")),
        candle_strength_min=float(os.getenv("CANDLE_STRENGTH_MIN", "0.0015")),
        breakout_min_pct=float(os.getenv("BREAKOUT_MIN_PCT", "0.001"))
    )
    
    # Delta Exchange
    delta_product_map = {
        "BTCUSD": int(os.getenv("BTCUSD_PID", "27")),
        "ETHUSD": int(os.getenv("ETHUSD_PID", "28")),
        "SOLUSD": int(os.getenv("SOLUSD_PID", "29")),
        "XRPUSD": int(os.getenv("XRPUSD_PID", "30")),
        "BNBUSD": int(os.getenv("BNBUSD_PID", "31"))
    }
    
    binance_map = {
        "BTCUSD": "BTCUSDT",
        "ETHUSD": "ETHUSDT",
        "SOLUSD": "SOLUSDT",
        "XRPUSD": "XRPUSDT",
        "BNBUSD": "BNBUSDT"
    }
    
    delta = ExchangeConfig(
        delta_base_url=os.getenv("DELTA_BASE_URL", "https://api.india.delta.exchange"),
        delta_product_map=delta_product_map,
        binance_map=binance_map
    )
    
    # Email
    email = EmailConfig(
        smtp_server=os.getenv("SMTP_SERVER", "smtp.gmail.com"),
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        email_user=os.getenv("EMAIL_USER"),
        email_pass=os.getenv("EMAIL_PASS"),
        email_to=os.getenv("EMAIL_TO")
    )
    
    return AppConfig(trading=trading, delta=delta, email=email)
