
import requests
import pandas as pd
import pandas_ta as ta
from aiogram import Bot, Dispatcher, executor, types
import asyncio

# --- CONFIG ---
import os
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SYMBOL = "BTC-USDT-SWAP"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# --- OKX API ---
def get_ohlcv(inst_id=SYMBOL, bar="1h", limit=150):
    url = "https://www.okx.com/api/v5/market/candles"
    params = {"instId": inst_id, "bar": bar, "limit": limit}
    r = requests.get(url, params=params)
    data = r.json()
    if data["code"] == '0':
        df = pd.DataFrame(data["data"], columns=["ts", "open", "high", "low", "close", "volume", *_])
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = df[col].astype(float)
        df = df.iloc[::-1]  # flip order
        return df
    return None

# --- Volume Profile ---
def volume_profile(df, price_step=50):
    df["bin"] = (df["close"] // price_step) * price_step
    vol_bins = df.groupby("bin")["volume"].sum().reset_index()
    vol_bins = vol_bins.sort_values("volume", ascending=False)
    poc = vol_bins.iloc[0]["bin"]
    value_area = vol_bins.head(int(len(vol_bins)*0.3))["bin"].values
    return poc, value_area

# --- Indicators & Analysis ---
def prepare_indicators(df):
    df["rsi"] = ta.rsi(df["close"], length=14)
    df["ema20"] = ta.ema(df["close"], length=20)
    df["ema50"] = ta.ema(df["close"], length=50)
    df["atr"] = ta.atr(df["high"], df["low"], df["close"], length=14)
    return df

def generate_signal(df):
    last = df.iloc[-1]
    previous = df.iloc[-2]
    poc, value_area = volume_profile(df)

    signal = None
    if (
        last["rsi"] < 30 and
        last["close"] > last["ema20"] > last["ema50"] and
        last["volume"] > df["volume"].rolling(20).mean().iloc[-1] * 1.5 and
        last["close"] >= poc and last["close"] <= poc + 100
    ):
        entry = last["close"]
        sl = entry - last["atr"] * 1.2
        tp = entry + (entry - sl) * 3
        signal = {
            "type": "LONG",
            "entry": entry,
            "stop_loss": sl,
            "take_profit": tp,
            "leverage": 5,
            "poc": poc
        }

    elif (
        last["rsi"] > 70 and
        last["close"] < last["ema20"] < last["ema50"] and
        last["volume"] > df["volume"].rolling(20).mean().iloc[-1] * 1.5 and
        last["close"] <= poc and last["close"] >= poc - 100
    ):
        entry = last["close"]
        sl = entry + last["atr"] * 1.2
        tp = entry - (sl - entry) * 3
        signal = {
            "type": "SHORT",
            "entry": entry,
            "stop_loss": sl,
            "take_profit": tp,
            "leverage": 5,
            "poc": poc
        }
    return signal

# --- Telegram Bot ---
@dp.message_handler(commands=["signal"])
async def signal_handler(message: types.Message):
    df = get_ohlcv()
    df = prepare_indicators(df)
    signal = generate_signal(df)

    if signal:
        text = (
            f"📊 Сигнал: {signal['type']}\n"
            f"💰 Вход: {signal['entry']:.2f}\n"
            f"❌ Стоп-лосс: {signal['stop_loss']:.2f}\n"
            f"✅ Тейк-профит: {signal['take_profit']:.2f}\n"
            f"📍 POC: {signal['poc']:.2f}\n"
            f"📈 Плечо: {signal['leverage']}x"
        )
    else:
        text = "🚫 Нет сигнала сейчас (не подтверждён всеми индикаторами)."

    await bot.send_message(CHAT_ID, text)

if __name__ == "__main__":
    executor.start_polling(dp)
