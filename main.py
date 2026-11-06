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
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            print("✅ Уведомление отправлено в Telegram!")
        else:
            print(f"❌ Ошибка Telegram: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Ошибка сети: {e}")

def check_keys():
    print("🔍 Начинаю проверку источников...")
    now = datetime.now(timezone.utc)
    time_threshold = now - timedelta(hours=3) # Ищем раздачи за последние 3 часа
    
    found_any = False
    for source in SOURCES:
        try:
            feed = feedparser.parse(source['url'])
            for entry in feed.entries:
                title_lower = entry.title.lower()
                
                # Фильтр на ключи и бесплатные игры
                if any(word in title_lower for word in ['key', 'keys', 'steam', 'epic', 'gog', '100%']):
                    if not any(bad in title_lower for bad in ['weekend', 'beta', 'survey', 'task']):
                        
                        # Проверяем дату публикации
                        pub_date = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                        
                        if pub_date > time_threshold:
                            message = (
                                f"🔥 <b>НОВАЯ РАЗДАЧА!</b>\n\n"
                                f"🎮 <b>{entry.title}</b>\n"
                                f"📌 Источник: {source['name']}\n"
                                f"🔗 <a href='{entry.link}'>Забрать ключ</a>"
                            )
                            print(f"🎯 Найдено: {entry.title}")
                            send_telegram_message(message)
                            found_any = True
                            
        except Exception as e:
            print(f"⚠️ Ошибка с {source['name']}: {e}")
            
    if not found_any:
        print("😴 Новых ключей за последние 3 часа не найдено.")

if __name__ == "__main__":
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ ОШИБКА: Не настроены переменные TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID в Secrets!")
    else:
        check_keys()
