# app.py DeltaRestClient.get_ohlc Fix

**Plan (Approved):**
- Replace get_ohlc with Binance /klines API (free, public)
- Add binance_ohlc(symbol_binance, interval, limit) function
- Map SYMBOLS to Binance: BTCUSDT, ETHUSDT, SOLUSDT, XRPUSDT, BNBUSDT
- Update load_levels(), get_price(), signals loop
- Delta client only for place_order/stop_order

**Steps (Complete):**
- [x] Step 1: Added binance_ohlc and updated load_levels()
- [x] Step 2: Updated get_price()
- [x] Step 3: Updated signal loop
- [x] Step 4: Tested `python app.py` - "Camarilla updated (Binance data)" success, no get_ohlc errors

**Why Binance data:** Free public OHLC API (no auth), accurate crypto prices. Delta Exchange client kept for LIVE TRADING ORDERS only. Set `export API_KEY=xxx API_SECRET=yyy` to enable actual trades on Delta India.

**Status:** ✅ Fixed! App runs, uses Binance for signals/Camarilla, Delta for orders.


