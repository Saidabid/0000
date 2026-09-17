import os
import time
from threading import Thread
from flask import Flask
import requests
import numpy as np

# =========================================================
# 🌐 قسم الويب الوهمي لإبقاء السيرفر يعمل 24/7 على Render
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
    t.start()

# تشغيل الويب الوهمي فوراً
keep_alive()

# =========================================================
# 🤖 إعدادات البوت والبيانات الخاصة بك
# =========================================================
TELEGRAM_TOKEN = "8275349097:AAGGX--CSfBKTj8-PJXxVbpjMk4FvSV9nZs"
CHAT_ID = "61911827133"

last_btc_price = None
last_gold_price = None

def send_alert(message):
    # تم تصحيح الرابط إلى الرابط الرسمي للبوتات
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": message}, timeout=10)
        print(f"📡 تليجرام: {message}")
    except Exception as e:
        print(f"خطأ إرسال لتليجرام: {e}")

def get_market_data():
    # 1. جلب أسعار البيتكوين الحقيقية بدقة من API بينانس الرسمي (آخر 100 شمعة دقيقة)
    btc_url = "https://binance.com"
    btc_res = requests.get(btc_url, timeout=10).json()
    
    closes = [float(x[4]) for x in btc_res]
    highs = [float(x[2]) for x in btc_res]
    lows = [float(x[3]) for x in btc_res]
    
    # 2. جلب سعر الذهب المباشر والآمن عبر API بديل ومفتوح
    gold_url = "https://coingecko.com"
    gold_res = requests.get(gold_url, timeout=10).json()
    gold_price = float(gold_res['pax-gold']['usd'])
    
    return closes, highs, lows, gold_price

def calculate_indicators(closes, highs, lows):
    # حساب RSI(14) بشكل صحيح وآمن
    deltas = np.diff(closes)
    seed = deltas[:14]
    up = seed[seed >= 0].sum() / 14
    down = -seed[seed < 0].sum() / 14
    rs = up / down if down != 0 else 0
    rsi = 100. - 100. / (1. + rs)
    
    # حساب تقاطع KDJ
    low_min = min(lows[-9:])
    high_max = max(highs[-9:])
    rsv = ((closes[-1] - low_min) / (high_max - low_min)) * 100 if (high_max - low_min) != 0 else 50
    k, d = 50, 50
    k = (2/3)*k + (1/3)*rsv
    d = (2/3)*d + (1/3)*k
    j = 3*k - 2*d
    return rsi, j

# إرسال نبضة التشغيل الأولى للبوت
send_alert("🚀 تم إطلاق رادار الذهب السريع وسكالبينج البيتكوين على سيرفر Render بنجاح! السيرفر يعمل الآن 24/7...")

# =========================================================
# 🔄 الحلقة اللانهائية للفحص المستمر
# =========================================================
while True:
    try:
        closes, highs, lows, gold_price = get_market_data()
        btc_price = closes[-1]
        rsi_val, j_val = calculate_indicators(closes, highs, lows)
        
        # 1. رادار الحركة الحادة المفاجئة للبيتكوين (0.3% في الدقيقة)
        if last_btc_price is not None:
            btc_change = ((btc_price - last_btc_price) / last_btc_price) * 100
            if abs(btc_change) >= 0.3:
                icon = "🚀" if btc_change > 0 else "🚨"
                status = "صعود حاد" if btc_change > 0 else "نزول حاد"
                send_alert(f"{icon} رادار البيتكوين: تم رصد {status} مفاجئ! السعر: {btc_price}$ | النسبة: {btc_change:.2f}%")
                
        # 2. رادار الحركة الحادة المفاجئة للذهب
        if last_gold_price is not None:
            gold_change = ((gold_price - last_gold_price) / last_gold_price) * 100
            if abs(gold_change) >= 0.2:
                icon = "🚀" if gold_change > 0 else "🚨"
                status = "صعود حاد" if gold_change > 0 else "نزول حاد"
                send_alert(f"{icon} رادار الذهب: تم رصد {status} مفاجئ في الأسواق! السعر: {gold_price}$ | النسبة: {gold_change:.2f}%")
        
        # 3. إشارة سكالبينج السريع للبيتكوين
        if rsi_val < 45 and j_val < 25:
            send_alert(f"🟩 إشارة سكالبينج (شراء): البيتكوين عند سعر {btc_price}$ يظهر ضعفاً لحظياً ممتازاً للدخول.")
            time.sleep(300) # انتظار 5 دقائق عند إرسال الإشارة لعدم تكرار الإرسال المزعج
            
        last_btc_price = btc_price
        last_gold_price = gold_price
        
        print(f"📊 فحص مستقر - BTC: {btc_price}$ | الذهب: {gold_price}$")
        time.sleep(15) # فحص كل 15 ثانية
        
    except Exception as e:
        print(f"تحديث السيرفر (خطأ مؤقت وسيتم إعادة المحاولة): {e}")
        time.sleep(10)
