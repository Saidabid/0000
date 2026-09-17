import os
import time
from threading import Thread
from flask import Flask
import requests
import numpy as np

# =========================================================
# 🌐 ويب وهمي للبوت الأول لإبقائه مستقراً على Render
# =========================================================
app = Flask('')

@app.route('/')
def home():
    return "رادار المؤشرات يعمل بنجاح في الخلفية!"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web_server)
    t.daemon = True
    t.start()

keep_alive()

# =========================================================
# ⚙️ إعدادات التليجرام والبيانات الخاصة بك
# =========================================================
TELEGRAM_TOKEN = "8783436728:AAECJm4ar7Nveec7Jfyf1KTWrYQ9BX-q6lU"
# 🌟 تم ربط قناتك العامة الجديدة هنا لإرسال التنبيهات داخلها فوراً بدون قيود
CHAT_ID = "@said_fast_radar"

last_btc_price = None
last_gold_price = None

def send_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        res = requests.post(url, json={"chat_id": CHAT_ID, "text": message}, timeout=10)
        print(f"📡 تليجرام استجابة: {res.status_code}")
    except Exception as e:
        print(f"خطأ إرسال لتليجرام: {e}")

def get_market_data():
    btc_url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=100"
    btc_res = requests.get(btc_url, timeout=10).json()

    closes = [float(candle[4]) for candle in btc_res]
    highs = [float(candle[2]) for candle in btc_res]
    lows = [float(candle[3]) for candle in btc_res]

    gold_url = "https://api.coingecko.com/api/v3/simple/price?ids=pax-gold&vs_currencies=usd" 
    gold_res = requests.get(gold_url, timeout=10).json()
    gold_price = float(gold_res['pax-gold']['usd'])

    return closes, highs, lows, gold_price

def calculate_indicators(closes, highs, lows):
    deltas = np.diff(closes)
    seed = deltas[:14]
    up = seed[seed >= 0].sum() / 14
    down = -seed[seed < 0].sum() / 14
    rs = up / down if down != 0 else 0
    rsi = 100. - 100. / (1. + rs)
    
    low_min = min(lows[-9:])
    high_max = max(highs[-9:])
    rsv = ((closes[-1] - low_min) / (high_max - low_min)) * 100 if (high_max - low_min) != 0 else 50
    k, d = 50, 50
    k = (2/3)*k + (1/3)*rsv
    d = (2/3)*d + (1/3)*k
    j = 3*k - 2*d
    return rsi, j

# إرسال الرسالة الترحيبية الأولى فور تشغيل الملف
send_alert("🚀 تم إطلاق رادار الذهب السريع وسكالبينج البيتكوين على سيرفر Render بنجاح! السيرفر يعمل الآن 24/7...")

while True:
    try:
        closes, highs, lows, gold_price = get_market_data()
        btc_price = closes[-1]
        rsi_val, j_val = calculate_indicators(closes, highs, lows)

        if last_btc_price is not None:
            btc_change = ((btc_price - last_btc_price) / last_btc_price) * 100
            if abs(btc_change) >= 0.3:
                icon = "🚀" if btc_change > 0 else "🚨"
                status = "صعود حاد" if btc_change > 0 else "نزول حاد"
                send_alert(f"{icon} رادار البيتكوين: تم رصد {status} مفاجئ! السعر: {btc_price}$ | النسبة: {btc_change:.2f}%")

        if last_gold_price is not None:
            gold_change = ((gold_price - last_gold_price) / last_gold_price) * 100
            if abs(gold_change) >= 0.2:
                icon = "🚀" if gold_change > 0 else "🚨"
                status = "صعود حاد" if gold_change > 0 else "نزول حاد"
                send_alert(f"{icon} رادار الذهب: تم رصد {status} مفاجئ في الأسواق! السعر: {gold_price}$ | النسبة: {gold_change:.2f}%")

        if rsi_val < 45 and j_val < 25:
            send_alert(f"🟩 إشارة سكالبينج (شراء): البيتكوين عند سعر {btc_price}$ يظهر ضعفاً لحظياً ممتازاً للدخول.")
            time.sleep(300)

        last_btc_price = btc_price
        last_gold_price = gold_price

        print(f"📊 فحص مستقر - BTC: {btc_price}$ | الذهب: {gold_price}$")
        time.sleep(15)

    except Exception as e:
        print(f"تحديث السيرفر: {e}")
        time.sleep(10)
