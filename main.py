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

# 🔹 SESSION (IMPORTANT)
session = requests.Session()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json",
    "Referer": "https://www.nseindia.com/",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
}

# 🔹 CACHE
cache_data = None
cache_time = 0
CACHE_TTL = 10  # seconds


@app.get("/")
def root():
    return {"status": "API running 🚀"}


# 🔹 NSE FETCH (ANTI-BLOCK VERSION)
def fetch_stock():
    try:
        # ✅ Step 1: Get cookies from NSE homepage
        home = session.get(
            "https://www.nseindia.com",
            headers=HEADERS,
            timeout=5
        )

        cookies = home.cookies

        # ✅ Step 2: Call actual API with cookies
        url = f"https://www.nseindia.com/api/quote-equity?symbol={SYMBOL}"

        res = session.get(
            url,
            headers=HEADERS,
            cookies=cookies,
            timeout=5
        )

        print("STATUS:", res.status_code)

        data = res.json()

        print("RESPONSE KEYS:", data.keys())

        # ❌ If blocked or empty
        if "priceInfo" not in data:
            print("❌ BLOCKED / EMPTY RESPONSE")
            print(data)
            return None

        price_data = data["priceInfo"]

        high = price_data.get("intraDayHighLow", {}).get("max")
        low = price_data.get("intraDayHighLow", {}).get("min")
        price = price_data.get("lastPrice")

        # ✅ Correct VWAP (SME works here)
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
            "last_update": data.get("metadata", {}).get("lastUpdateTime"),
            "source": "NSE"
        }

    except Exception as e:
        print("❌ ERROR:", str(e))
        return None


# 🔹 MAIN API (WITH CACHE)
@app.get("/data")
def get_data():
    global cache_data, cache_time

    now = time.time()

    # ✅ Return cached response
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
