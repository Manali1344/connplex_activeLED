from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from datetime import datetime
import time

app = FastAPI()

SYMBOL = "TCS"
DISPLAY_NAME = "TCS LTD - NSE"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

session = requests.Session()

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Referer": "https://www.nseindia.com/",
}

# 🔹 CACHE
cache_data = None
cache_time = 0
CACHE_TTL = 10  # seconds


def init_nse():
    try:
        session.get("https://www.nseindia.com", headers=HEADERS, timeout=5)
    except:
        pass


def fetch_stock():
    try:
        init_nse()

        url = f"https://www.nseindia.com/api/quote-equity?symbol={SYMBOL}"
        res = session.get(url, headers=HEADERS, timeout=5)

        if res.status_code != 200:
            return None

        data = res.json()
        price_data = data.get("priceInfo", {})

        high = price_data.get("intraDayHighLow", {}).get("max")
        low = price_data.get("intraDayHighLow", {}).get("min")
        price = price_data.get("lastPrice")

        vwap = None
        if high and low and price:
            vwap = round((high + low + price) / 3, 2)

        return {
            "symbol": DISPLAY_NAME,
            "price": price,
            "open": price_data.get("open"),
            "high": high,
            "low": low,
            "prev_close": price_data.get("previousClose"),
            "change": price_data.get("change"),
            "change_percent": price_data.get("pChange"),
            "vwap": vwap,
        }

    except Exception as e:
        print("Error:", e)
        return None


@app.get("/data")
def get_data():
    global cache_data, cache_time

    now = time.time()

    # ✅ Return cached data
    if cache_data and (now - cache_time < CACHE_TTL):
        return cache_data

    stock = fetch_stock()

    response = {
        "stock": stock if stock else {"error": "Data unavailable"},
        "timestamp": datetime.now().strftime("%d-%b-%Y %H:%M:%S IST")
    }

    cache_data = response
    cache_time = now

    return response
