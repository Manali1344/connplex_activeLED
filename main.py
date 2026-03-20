def fetch_stock():
    try:
        # 🔥 Step 1: Get cookies (VERY IMPORTANT)
        home = session.get(
            "https://www.nseindia.com",
            headers=HEADERS,
            timeout=5
        )

        cookies = home.cookies

        # 🔥 Step 2: Use same cookies for API call
        url = f"https://www.nseindia.com/api/quote-equity?symbol={SYMBOL}"

        res = session.get(
            url,
            headers=HEADERS,
            cookies=cookies,
            timeout=5
        )

        print("STATUS:", res.status_code)

        data = res.json()

        # 🔍 DEBUG
        print("KEYS:", data.keys())

        if "priceInfo" not in data:
            print("❌ BLOCKED or EMPTY RESPONSE")
            print(data)
            return None

        price_data = data["priceInfo"]

        high = price_data.get("intraDayHighLow", {}).get("max")
        low = price_data.get("intraDayHighLow", {}).get("min")
        price = price_data.get("lastPrice")

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
            "source": "NSE"
        }

    except Exception as e:
        print("❌ ERROR:", e)
        return None
