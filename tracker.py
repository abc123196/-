import os
import datetime as dt
from zoneinfo import ZoneInfo

import requests
import yfinance as yf

TOKEN = os.environ["TG_TOKEN"]
CHAT_ID = os.environ["TG_CHAT_ID"]

# ===== 每季手動更新這裡（沒資料就留 "-"）=====
DATA = {
    "2308": {
        "name": "台達電",
        "ticker": "2308.TW",
        "metrics": {
            "AI資料中心相關營收": {"2024": "-", "2025": "-", "2026": "-", "觀察": "占比是否持續上升"},
            "毛利率": {"2024": "-", "2025": "-", "2026": "-", "觀察": "產品組合改善"},
            "資本支出+自由現金流": {"2024": "-", "2025": "-", "2026": "-", "觀察": "FCF是否為正"},
        },
    },
    "3017": {
        "name": "奇鋐",
        "ticker": "3017.TW",
        "metrics": {
            "AI Server/液冷相關營收": {"2024": "-", "2025": "-", "2026": "-", "觀察": "液冷滲透率"},
            "毛利率": {"2024": "-", "2025": "-", "2026": "-", "觀察": "是否維持"},
            "客戶集中度+產能擴張": {"2024": "-", "2025": "-", "2026": "-", "觀察": "前大客戶占比、新廠進度"},
        },
    },
    "3711": {
        "name": "日月光投控",
        "ticker": "3711.TW",
        "metrics": {
            "先進封裝營收": {"2024": "-", "2025": "-", "2026": "-", "觀察": "是否達成目標"},
            "先進封裝毛利率": {"2024": "-", "2025": "-", "2026": "-", "觀察": "與整體毛利率差距"},
            "資本支出+自由現金流": {"2024": "-", "2025": "-", "2026": "-", "觀察": "資本支出效益"},
        },
    },
}
# ===========================================


def get_quote(ticker):
    """回傳 (最新收盤價, 漲跌幅%, PE)，抓不到就回傳 None。"""
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="7d")["Close"].dropna()
        last, prev = float(hist.iloc[-1]), float(hist.iloc[-2])
        pct = (last - prev) / prev * 100
        try:
            pe = t.info.get("trailingPE")
        except Exception:
            pe = None
        return last, pct, pe
    except Exception:
        return None, None, None


def build_daily(now):
    lines = [f"📈 開盤簡報 {now:%m/%d}（前一交易日收盤）"]
    for code, d in DATA.items():
        price, pct, _ = get_quote(d["ticker"])
        if price is None:
            lines.append(f"{code} {d['name']}：資料取得失敗")
            continue
        icon = "🔺" if pct > 0 else "🔻" if pct < 0 else "➖"
        lines.append(f"{icon} {code} {d['name']}  {price:.1f}（{pct:+.2f}%）")
    return "\n".join(lines)


def build_full():
    lines = ["📊 每週投資追蹤表"]
    for code, d in DATA.items():
        price, _, pe = get_quote(d["ticker"])
        price_text = f"{price:.1f}" if price is not None else "-"
        pe_text = f"{pe:.1f}" if pe else "-"
        lines.append(f"\n【{code} {d['name']}】股價 {price_text}｜PE {pe_text}")
        for metric, v in d["metrics"].items():
            lines.append(
                f"• {metric}\n"
                f"  2024: {v['2024']} ｜ 2025: {v['2025']} ｜ 2026: {v['2026']}\n"
                f"  👀 {v['觀察']}"
            )
    return "\n".join(lines)


def send(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    r = requests.post(url, data={"chat_id": CHAT_ID, "text": text}, timeout=30)
    r.raise_for_status()


if __name__ == "__main__":
    now = dt.datetime.now(ZoneInfo("Asia/Taipei"))
    send(build_daily(now))
    # 週一（或設定環境變數 FULL=1）多送一份完整季度表
    if now.weekday() == 0 or os.environ.get("FULL") == "1":
        send(build_full())
