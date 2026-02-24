from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from datetime import datetime
import yfinance as yf

app = FastAPI()

# ✅ CHANGE THIS if needed
SYMBOL = "CONNPLEX"

# ✅ CORS (Allow all for now)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # For testing. Later restrict to your domain.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

session = requests.Session()
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}


@app.get("/")
def root():
    return {"status": "API running"}


# 🔹 Primary Method (NSE)
def fetch_stock_nse(symbol):
    try:
        session.get("https://www.nseindia.com", headers=HEADERS, timeout=5)
        url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
        response = session.get(url, headers=HEADERS, timeout=5)

        if response.status_code != 200:
            return None

        data = response.json()

        if "priceInfo" not in data:
            return None

        price_data = data["priceInfo"]

        return {
            "symbol": f"{symbol}",
            "price": price_data.get("lastPrice"),
            "open": price_data.get("open"),
            "high": price_data.get("intraDayHighLow", {}).get("max"),
            "low": price_data.get("intraDayHighLow", {}).get("min"),
            "prev_close": price_data.get("previousClose"),
            "change": price_data.get("change"),
            "change_percent": round(price_data.get("pChange", 0), 2),
            "vwap": data.get("securityWiseDP", {}).get("vwap"),
        }

    except Exception:
        return None


# 🔹 Fallback Method (Yahoo Finance - more stable on cloud)
def fetch_stock_yfinance(symbol):
    try:
        ticker = yf.Ticker(symbol + ".NS")
        info = ticker.info

        return {
            "symbol": symbol,
            "price": info.get("regularMarketPrice"),
            "open": info.get("regularMarketOpen"),
            "high": info.get("regularMarketDayHigh"),
            "low": info.get("regularMarketDayLow"),
            "prev_close": info.get("regularMarketPreviousClose"),
            "change": info.get("regularMarketChange"),
            "change_percent": info.get("regularMarketChangePercent"),
            "vwap": None,
        }

    except Exception:
        return None


def fetch_stock(symbol):
    # Try NSE first
    data = fetch_stock_nse(symbol)

    if data:
        return data

    # Fallback to Yahoo
    data = fetch_stock_yfinance(symbol)

    if data:
        return data

    # Final safe fallback
    return {
        "symbol": symbol,
        "price": 0,
        "open": 0,
        "high": 0,
        "low": 0,
        "prev_close": 0,
        "change": 0,
        "change_percent": 0,
        "vwap": 0,
        "error": "Data temporarily unavailable"
    }


def fetch_index_data():
    try:
        return {
            "nifty": yf.Ticker("^NSEI").info.get("regularMarketPrice"),
            "sensex": yf.Ticker("^BSESN").info.get("regularMarketPrice"),
        }
    except Exception:
        return {"nifty": None, "sensex": None}


@app.get("/data")
def get_stock_data():
    return {
        "stock": fetch_stock(SYMBOL),
        "index": fetch_index_data(),
        "timestamp": datetime.now().strftime("%d-%b-%Y %H:%M:%S IST")
    }
