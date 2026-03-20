from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import yfinance as yf
import time

app = FastAPI()

SYMBOL = "CONNPLEX.NS"
DISPLAY_NAME = "CONNPLEX CINEMAS LTD"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 CACHE
cache_data = None
cache_time = 0
CACHE_TTL = 15


@app.get("/")
def root():
    return {"status": "API running 🚀"}


# 🔹 YAHOO (LIGHT VERSION)
def fetch_stock():
    try:
        ticker = yf.Ticker(SYMBOL)
        data = ticker.history(period="1d")

        if data.empty:
            return None

        latest = data.iloc[-1]

        price = round(latest["Close"], 2)
        high = round(latest["High"], 2)
        low = round(latest["Low"], 2)
        open_price = round(latest["Open"], 2)

        vwap = round((high + low + price) / 3, 2)

        return {
            "symbol": DISPLAY_NAME,
            "price": price,
            "open": open_price,
            "high": high,
            "low": low,
            "vwap": vwap,
            "source": "Yahoo"
        }

    except Exception as e:
        print("ERROR:", e)
        return None


@app.get("/data")
def get_data():
    global cache_data, cache_time

    now = time.time()

    if cache_data and (now - cache_time < CACHE_TTL):
        return cache_data

    stock = fetch_stock()

    response = {
        "stock": stock if stock else {"error": "Data unavailable"},
        "server_time": datetime.now().strftime("%d-%b-%Y %H:%M:%S IST")
    }

    cache_data = response
    cache_time = now

    return response
