
import time
import requests
import numpy as np

# الرموز والمعرفات الخاصة بالبوت الأخضر السريع
TELEGRAM_TOKEN = "8275349097:AAGGX--CSfBKTj8-PJXxVbpjMk4FvSV9nZs"
CHAT_ID = "61911827133"

last_btc_price = None
last_gold_price = None

def send_alert(message):
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": message})
        print(f"📡 تليجرام: {message}")
    except Exception as e:
        print(f"خطأ إرسال: {e}")

def get_market_data():
    # سحب قراءات البيتكوين من بينانس
    btc_url = "https://binance.vision"
    btc_data = requests.get(btc_url).json()
    closes = [float(x) for x in btc_data]
    highs = [float(x) for x in btc_data]
    lows = [float(x) for x in btc_data]
    
    # سحب أسعار الذهب الفورية
    gold_url = "https://yahoo.com"
    headers = {'User-Agent': 'Mozilla/5.0'}
    gold_data = requests.get(gold_url, headers=headers).json()
    gold_price = float(gold_data['chart']['result']['meta']['regularMarketPrice'])
    
    return closes, highs, lows, gold_price

def calculate_indicators(closes, highs, lows):
    # حساب RSI(14)
    deltas = np.diff(closes)
    seed = deltas[:15]
    up = seed[seed >= 0].sum() / 14
    down = -seed[seed < 0].sum() / 14
    rs = up / down if down != 0 else 0
    rsi = 100. - 100. / (1. + rs)
    
    # حساب تقاطع KDJ اللحظي السريع
    low_min = min(lows[-9:])
    high_max = max(highs[-9:])
    rsv = ((closes[-1] - low_min) / (high_max - low_min)) * 100 if (high_max - low_min) != 0 else 50
    k, d = 50, 50
    k = (2/3)*k + (1/3)*rsv
    d = (2/3)*d + (1/3)*k
    j = 3*k - 2*d
    return rsi, j

# إرسال نبضة التشغيل الأولى للبوت الأخضر
send_alert("🚀 تم إطلاق رادار الذهب السريع وسكالبينج البيتكوين على سيرفر Render بنجاح! السيرفر يعمل الآن 24/7...")

while True:
    try:
        closes, highs, lows, gold_price = get_market_data()
        btc_price = closes[-1]
        rsi_val, j_val = calculate_indicators(closes, highs, lows)
        
        # 1. رادار الحركة الحادة المفاجئة (0.3% في الدقيقة)
        if last_btc_price is not None:
            btc_change = ((btc_price - last_btc_price) / last_btc_price) * 100
            if abs(btc_change) >= 0.3:
                icon = "🚀" if btc_change > 0 else "🚨"
                status = "صعود حاد" if btc_change > 0 else "نزول حاد"
                send_alert(f"{icon} رادار البيتكوين: تم رصد {status} مفاجئ! السعر: {btc_price}$ | النسبة: {btc_change:.2f}%")
                
        if last_gold_price is not None:
            gold_change = ((gold_price - last_gold_price) / last_gold_price) * 100
            if abs(gold_change) >= 0.2:  # حركة الذهب أبطأ، تم ضبط الحساسية لـ 0.2% ليلتقط الانفجارات الذهبية
                icon = "🚀" if gold_change > 0 else "🚨"
                status = "صعود حاد" if gold_change > 0 else "نزول حاد"
                send_alert(f"{icon} رادار الذهب: تم رصد {status} مفاجئ في الأسواق! السعر: {gold_price}$ | النسبة: {gold_change:.2f}%")
        
        # 2. استراتيجية السكالبينج السريع للبيتكوين (أكثر حساسية)
        if rsi_val < 45 and j_val < 25:
            send_alert(f"🟩 إشارة سكالبينج (شراء): البيتكوين عند سعر {btc_price}$ يظهر ضعفاً لحظياً ممتازاً للدخول.")
            time.sleep(300)
            
        last_btc_price = btc_price
        last_gold_price = gold_price
        
        print(f"📊 فحص مستقر - BTC: {btc_price}$ | الذهب: {gold_price}$")
        time.sleep(15)  # فحص مستمر كل 15 ثانية صامتاً
    except Exception as e:
        print(f"تحديث السيرفر: {e}")
        time.sleep(10)
