import os
import smtplib
from datetime import datetime
import pytz
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

IST = pytz.timezone("Asia/Kolkata")

# Env vars
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO = os.getenv("EMAIL_TO")
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")


def send_email(subject: str, body: str) -> bool:
    """Send email if full config present."""
    if not (API_KEY and API_SECRET and EMAIL_USER and EMAIL_PASS and EMAIL_TO):
        print("Trading or email config missing, skipping...")
        return False
    
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_TO
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, EMAIL_TO, msg.as_string())
        print("✅ Email sent!")
        return True
    except Exception as e:
        print(f"❌ Email error: {e}")
        return False


def format_trade_alert(symbol: str, side: str, entry: float, sl: float, tp: float, 
                      size: float = 1, extra: str = "", time_str: Optional[str] = None) -> str:
    """Format new trade details."""
    ts = time_str or datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')
    return f"""🚀 NEW TRADE: {symbol} {side.upper()}
Entry: ~${entry:.4f} | SL: ${sl:.4f} | TP: ${tp:.4f}
Size: {size} | Time: {ts}
{extra}"""


def send_new_trade_alert(symbol: str, side: str, entry: float, sl: float, tp: float, 
                        size: int = 1, pid: int = 0, level: str = "") -> bool:
    """Send new trade email."""
    extra = f"PID: {pid} | Level: {level}"
    body = format_trade_alert(symbol, side, entry, sl, tp, size, extra)
    return send_email(f"🚀 TRADE: {symbol} {side.upper()}", body)


def send_sl_hit_alert(symbol: str, side: str, entry: float, exit_price: float) -> bool:
    """Send SL hit email."""
    body = f"""💥 SL HIT: {symbol} {side.upper()}
Entry: ${entry:.4f} | Exit: ~${exit_price:.4f}
P&L: Negative (SL) | Time: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')}"""
    return send_email(f"💥 SL: {symbol} {side.upper()}", body)


def send_tp_hit_alert(symbol: str, side: str, entry: float, tp_price: float) -> bool:
    """Send TP hit (pre-trailing) email."""
    body = f"""🎯 TP HIT: {symbol} {side.upper()}
Entry: ${entry:.4f} | TP: ${tp_price:.4f}
Trailing SL now active | Time: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')}"""
    return send_email(f"🎯 TP REACHED: {symbol}", body)
