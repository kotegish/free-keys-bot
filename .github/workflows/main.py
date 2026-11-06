import feedparser
import requests
import os
from datetime import datetime, timezone, timedelta

# Берем данные из настроек GitHub (секретов)
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

SOURCES = [
    {"name": "r/SteamGiveaways", "url": "https://www.reddit.com/r/steamgiveaways/hot.rss?limit=15"},
    {"name": "r/FreeGameFindings", "url": "https://www.reddit.com/r/FreeGameFindings/hot.rss?limit=15"},
    {"name": "GamerPower", "url": "https://www.gamerpower.com/feed"}
]

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, json=data, timeout=10)
        print("✅ Уведомление отправлено в Telegram!")
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")

def check_keys():
    print("🔍 Начинаю проверку...")
    now = datetime.now(timezone.utc)
    time_threshold = now - timedelta(hours=2) # Ищем только свежие раздачи (за последние 2 часа)
    
    for source in SOURCES:
        try:
            feed = feedparser.parse(source['url'])
            for entry in feed.entries:
                title_lower = entry.title.lower()
                
                # Фильтр на ключи и бесплатные игры
                if any(word in title_lower for word in ['key', 'keys', 'steam', 'epic', 'gog', '100%']):
                    if not any(bad in title_lower for bad in ['weekend', 'beta', 'survey', 'task']):
                        
                        # Проверяем дату публикации
                        # Формат даты в RSS обычно: "Mon, 07 Nov 2024 10:00:00 GMT"
                        pub_date = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                        
                        if pub_date > time_threshold:
                            message = (
                                f"🔥 <b>НОВАЯ РАЗДАЧА!</b>\n\n"
                                f"🎮 <b>{entry.title}</b>\n"
                                f"📌 Источник: {source['name']}\n"
                                f"🔗 <a href='{entry.link}'>Забрать ключ</a>"
                            )
                            print(f"Найдено: {entry.title}")
                            send_telegram_message(message)
                            
        except Exception as e:
            print(f"Ошибка с {source['name']}: {e}")

if __name__ == "__main__":
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Ошибка: Не настроены переменные окружения Telegram!")
    else:
        check_keys()
