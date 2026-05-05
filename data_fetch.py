import requests
import pandas as pd
from datetime import datetime, timedelta

BASE_URL = "https://api.finmindtrade.com/api/v4/data"

def get_taiex_data():
    today = datetime.today()
    start = (today - timedelta(days=60)).strftime("%Y-%m-%d")

    params = {
        "dataset": "TaiwanStockPrice",
        "data_id": "TAIEX",
        "start_date": start,
    }

    res = requests.get(BASE_URL, params=params)
    data = res.json()["data"]

    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    # ===== 技術指標 =====
    df["ma20"] = df["close"].rolling(20).mean()
    df["vol_ma20"] = df["Trading_Volume"].rolling(20).mean()

    latest = df.iloc[-1]

    return {
        "taiex_close": float(latest["close"]),
        "ma20": float(round(latest["ma20"], 2)),
        "volume": float(latest["Trading_Volume"]),
        "volume_ma20": float(round(latest["vol_ma20"], 2)),
        "price_vs_ma": "above" if latest["close"] > latest["ma20"] else "below"
    }

# ===== 匯率 =====
def get_usdtwd():
    url = "https://api.exchangerate.host/timeseries"
    params = {
        "start_date": "2026-04-01",
        "end_date": datetime.today().strftime("%Y-%m-%d"),
        "base": "USD",
        "symbols": "TWD"
    }

    res = requests.get(url, params=params)
    data = res.json()["rates"]

    df = pd.DataFrame(data).T
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()

    latest = df.iloc[-1]["TWD"]
    prev3 = df.iloc[-3]["TWD"]

    trend = "appreciating" if latest < prev3 else "depreciating"

    return {
        "usd_twd": float(round(latest, 2)),
        "usd_twd_trend": trend
    }

# ===== 外資（先用簡化版，之後可升級）=====
def get_foreign():
    return {
        "foreign_net_buy": -12000,
        "foreign_streak": "sell_3d"
    }

# ===== 整合 =====
def build_dataset():
    data = {}

    try:
        data.update(get_taiex_data())
        data.update(get_usdtwd())
        data.update(get_foreign())
    except Exception as e:
        data["error"] = str(e)

    return data
