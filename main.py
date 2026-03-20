from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from datetime import datetime
import time

app = FastAPI()

# 🔹 CONFIG
SYMBOL = "CONNPLEX"
DISPLAY_NAME = "CONNPLEX CINEMAS LTD - NSE SME"

# 🔹 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 SESSION
session = requests.Session()

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Referer": "https://www.nseindia.com/",
    "Accept-Language": "en-US,en;q=0.9",
}

# 🔹 CACHE (VERY IMPORTANT for memory)
cache_data = None
cache_time = 0
CACHE_TTL = 10  # seconds


# 🔹 INIT NSE SESSION
def init_nse():
    try:
        session.get("https://www.nseindia.com", headers=HEADERS, timeout=5)
    except:
        pass


# 🔹 FETCH STOCK (SME SAFE)
def fetch_stock():
    try:
        init_nse()

        url = f"https://www.nseindia.com/api/quote-equity?symbol={SYMBOL}"
        res = session.get(url, headers=HEADERS, timeout=5)

        print("STATUS:", res.status_code)

        if res.status_code != 200:
            print("❌ NSE FAILED")
            return None

        data = res.json()

        if "priceInfo" not in data:
            print("❌ priceInfo missing")
            return None

        price_data = data["priceInfo"]

        high = price_data.get("intraDayHighLow", {}).get("max")
        low = price_data.get("intraDayHighLow", {}).get("min")
        price = price_data.get("lastPrice")

        # ✅ CORRECT VWAP (works for SME)
        vwap = price_data.get("vwap")

        return {
            "symbol": DISPLAY_NAME,
            "price": price,
            "open": price_data.get("open"),
            "high": high,
            "low": low,
            "prev_close": price_data.get("previousClose"),
            "change": price_data.get("change"),
            "change_percent": round(price_data.get("pChange", 0), 2),
            "vwap": vwap,
            "timestamp": data.get("metadata", {}).get("lastUpdateTime"),
            "source": "NSE"
        }

    except Exception as e:
        print("❌ ERROR:", e)
        return None


@app.get("/")
def root():
    return {"status": "API running 🚀"}


# 🔹 MAIN ENDPOINT WITH CACHE
@app.get("/data")
def get_data():
    global cache_data, cache_time

    now = time.time()

    # ✅ Return cached response (reduces memory + API load)
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
