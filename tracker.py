import os
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


def get_price(ticker):
    try:
        t = yf.Ticker(ticker)
        price = t.fast_info["last_price"]
        pe = t.info.get("trailingPE")
        pe_text = f"{pe:.1f}" if pe else "-"
        return f"{price:.1f}", pe_text
    except Exception:
        return "-", "-"


def build_message():
    lines = ["📊 投資追蹤表"]
    for code, d in DATA.items():
        price, pe = get_price(d["ticker"])
        lines.append(f"\n【{code} {d['name']}】股價 {price}｜PE {pe}")
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
    send(build_message())
