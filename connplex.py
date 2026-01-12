import tkinter as tk
import requests
import threading
import time
from datetime import datetime
import yfinance as yf


# ---------------- CONFIG ----------------
API_KEY = "WQQCVJFCU3EY9I1T"  # Replace with your Alpha Vantage API key if limited
SYMBOL = "CONNPLEX"
REFRESH_INTERVAL = 3  # seconds

session = requests.Session()
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

# ---------------- FETCH STOCK (NSE site) ----------------
def fetch_stock(symbol):
    try:
        session.get("https://www.nseindia.com", headers=HEADERS, timeout=5)
        url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
        response = session.get(url, headers=HEADERS, timeout=5)
        data = response.json()

        price_data = data["priceInfo"]
        return {
            "price": price_data["lastPrice"],
            "open": price_data["open"],
            "high": price_data["intraDayHighLow"]["max"],
            "low": price_data["intraDayHighLow"]["min"],
            "prev_close": price_data["previousClose"],
            "close": price_data["lastPrice"],
            "change": price_data["change"],
            "change_percent": f"{price_data['pChange']:.2f}%",
            "vwap": data.get("securityWiseDP", {}).get("vwap", price_data["lastPrice"]),
        }
    except Exception:
        return None


# ---------------- FETCH NIFTY & SENSEX (Alpha Vantage) ----------------
import yfinance as yf

def fetch_index_data():
    try:
        nifty = yf.Ticker("^NSEI").info.get("regularMarketPrice")
        sensex = yf.Ticker("^BSESN").info.get("regularMarketPrice")
        return {"nifty": nifty, "sensex": sensex}
    except Exception as e:
        print("yfinance error:", e)
        return {"nifty": None, "sensex": None}

  


# ---------------- UI UPDATE ----------------
def update_ui():
    while True:
        stock = fetch_stock(SYMBOL)
        index_data = fetch_index_data()

        if stock:
            lbl_symbol.config(text=f"{SYMBOL} CINEMAS LTD", fg="white")

            lbl_price.config(text=f"₹{stock['price']:.2f}")
            lbl_change.config(
                text=f"{stock['change']:+.2f} ({stock['change_percent']})",
                fg="lime" if stock['change'] > 0 else "red"
            )

            lbl_prev_close.config(text=f"{stock['prev_close']:.2f}")
            lbl_open.config(text=f"{stock['open']:.2f}")
            lbl_high.config(text=f"{stock['high']:.2f}")
            lbl_low.config(text=f"{stock['low']:.2f}")
            lbl_close.config(text=f"{stock['close']:.2f}")
            lbl_vwap.config(text=f"{stock['vwap']:.2f}")

            # NIFTY 50 and SENSEX from Alpha Vantage
            if index_data["nifty"]:
                lbl_nifty.config(text=f"{index_data['nifty']:.2f}", fg="#00ffff")
            else:
                lbl_nifty.config(text="N/A", fg="gray")

            if index_data["sensex"]:
                lbl_sensex.config(text=f"{index_data['sensex']:.2f}", fg="#00ffff")
            else:
                lbl_sensex.config(text="N/A", fg="gray")

            lbl_time.config(
                text=datetime.now().strftime("As on %d-%b-%Y %H:%M:%S IST")
            )
        else:
            lbl_symbol.config(text="CONNPLEX - No Data", fg="yellow")

        time.sleep(REFRESH_INTERVAL)


# ---------------- GUI DESIGN ----------------
root = tk.Tk()
root.title("Connplex Stock Display")
root.attributes('-fullscreen', True)  
root.configure(bg="black")

def exit_fullscreen(event=None):
    root.attributes('-fullscreen', False)
    root.state('normal')

root.bind("<Escape>", exit_fullscreen)

lbl_symbol = tk.Label(root, text="Loading...",
                      font=("Arial", 12, "bold"),
                      fg="white", bg="black")
lbl_symbol.pack(pady=(2, 0))

frame_price = tk.Frame(root, bg="black")
frame_price.pack()

lbl_price = tk.Label(frame_price, text="0.00", font=("Consolas", 22, "bold"),
                     fg="lime", bg="black")
lbl_price.pack(side="left", padx=5)

lbl_change = tk.Label(frame_price, text="+0.00 (0%)",
                      font=("Consolas", 14), fg="lime", bg="black")
lbl_change.pack(side="left", padx=10)

stats_frame = tk.Frame(root, bg="black")
stats_frame.pack(pady=2)

def make_stat(title):
    f = tk.Frame(stats_frame, bg="black")
    tk.Label(f, text=title, font=("Arial", 8, "bold"),
             fg="gray", bg="black").pack()
    val = tk.Label(f, text="0.00", font=("Consolas", 10, "bold"),
                   fg="#00ffcc", bg="black")
    val.pack()
    f.pack(side="left", padx=4)
    return val

lbl_prev_close = make_stat("PREV")
lbl_open = make_stat("OPEN")
lbl_high = make_stat("HIGH")
lbl_low = make_stat("LOW")
lbl_close = make_stat("CLOSE")
lbl_vwap = make_stat("VWAP")
lbl_nifty = make_stat("NIFTY 50")
lbl_sensex = make_stat("SENSEX")

lbl_time = tk.Label(root, text="", font=("Arial", 8),
                    fg="#888", bg="black")
lbl_time.pack(side="bottom", pady=(0, 2))

threading.Thread(target=update_ui, daemon=True).start()
root.mainloop()
