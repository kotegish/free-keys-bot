import feedparser
import requests
import os
from datetime import datetime, timezone, timedelta

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

SOURCES = [
    {"name": "r/FreeGameFindings", "url": "https://www.reddit.com/r/FreeGameFindings/hot.rss?limit=15"},
    {"name": "Humble Bundle", "url": "https://www.humblebundle.com/rss"},
]

GOOD_WORDS = ['key', 'steam', 'epic', 'gog', '100%', 'bundle', 'humble', 'free', 'giveaway']
BAD_WORDS = ['weekend', 'beta', 'survey', 'task', 'dlc', 'soundtrack', 'ost']

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    response = requests.post(url, json=data, timeout=10)
    print(f"📡 Ответ от Telegram: {response.status_code} - {response.text}")

def check_keys():
    print("🔍 ТЕСТОВЫЙ ЗАПУСК (ищем за последние 48 часов)")
    now = datetime.now(timezone.utc)
    time_threshold = now - timedelta(hours=48) # Ищем за 2 дня, чтобы точно что-то найти
    
    for source in SOURCES:
        print(f"\n--- Проверяем {source['name']} ---")
        feed = feedparser.parse(source['url'])
        for entry in feed.entries[:5]: # Берем только топ-5 свежих записей
            title_lower = entry.title.lower()
            print(f"👀 Вижу запись: {entry.title}")
            
            has_good = any(word in title_lower for word in GOOD_WORDS)
            has_bad = any(bad in title_lower for bad in BAD_WORDS)
            
            if has_good and not has_bad:
                try:
                    pub_date = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                    if pub_date > time_threshold:
                        print(f"✅ ПРОХОДИТ ФИЛЬТР! Отправляем...")
                        message = f"🔥 <b>ТЕСТ: {entry.title}</b>\n📌 {source['name']}\n🔗 <a href='{entry.link}'>Ссылка</a>"
                        send_telegram_message(message)
                    else:
                        print("⏭ Пропущено: старая запись")
                except:
                    print("⏭ Пропущено: нет даты")
            else:
                print(f"⏭ Пропущено фильтром (good: {has_good}, bad: {has_bad})")

if __name__ == "__main__":
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ ОШИБКА: Нет токена или ID!")
    else:
        check_keys()
