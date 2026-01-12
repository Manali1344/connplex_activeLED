from fastapi import FastAPI
import requests
from datetime import datetime
import yfinance as yf

app = FastAPI()

SYMBOL = "CONNPLEX"

session = requests.Session()
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

def fetch_stock(symbol):
    try:
        session.get("https://www.nseindia.com", headers=HEADERS, timeout=5)
        url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
        response = session.get(url, headers=HEADERS, timeout=5)
        data = response.json()

        price_data = data["priceInfo"]
        return {
            "symbol": f"{symbol} CINEMAS LTD",
            "price": price_data["lastPrice"],
            "open": price_data["open"],
            "high": price_data["intraDayHighLow"]["max"],
            "low": price_data["intraDayHighLow"]["min"],
            "prev_close": price_data["previousClose"],
            "change": price_data["change"],
            "change_percent": round(price_data["pChange"], 2),
            "vwap": data.get("securityWiseDP", {}).get("vwap", price_data["lastPrice"]),
        }
    except Exception:
        return None

def fetch_index_data():
    try:
        nifty = yf.Ticker("^NSEI").info.get("regularMarketPrice")
        sensex = yf.Ticker("^BSESN").info.get("regularMarketPrice")
        return {"nifty": nifty, "sensex": sensex}
    except:
        return {"nifty": None, "sensex": None}

@app.get("/data")
def get_stock_data():
    stock = fetch_stock(SYMBOL)
    index_data = fetch_index_data()

    return {
        "stock": stock,
        "index": index_data,
        "timestamp": datetime.now().strftime("%d-%b-%Y %H:%M:%S IST")
    }
