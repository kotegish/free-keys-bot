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
    {"name": "GamerPower", "url": "https://www.gamerpower.com/feed"},
    {"name": "Humble Bundle", "url": "https://www.humblebundle.com/rss"},
    {"name": "Fanatical", "url": "https://www.fanatical.com/en/rss"},
    {"name": "IndieGala", "url": "https://www.indiegala.com/rss"}
]

GOOD_WORDS = ['key', 'keys', 'steam', 'epic', 'gog', '100%', 'bundle', 'humble', 'fanatical', 'indiegala', 'free', 'giveaway']
BAD_WORDS = ['weekend', 'beta', 'survey', 'task', 'dlc', 'soundtrack', 'ost', 'season pass', 'expansion']

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
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
    print("🔍 Начинаю проверку источников (включая бандлы)...")
    now = datetime.now(timezone.utc)
    time_threshold = now - timedelta(hours=3) # Ищем раздачи за последние 3 часа
    
    found_any = False
    for source in SOURCES:
        try:
            feed = feedparser.parse(source['url'])
            for entry in feed.entries:
                title_lower = entry.title.lower()
                
                has_good_word = any(word in title_lower for word in GOOD_WORDS)
                has_bad_word = any(bad in title_lower for bad in BAD_WORDS)
                
                if has_good_word and not has_bad_word:
                    try:
                        pub_date = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                    except (TypeError, AttributeError):
                        pub_date = now 
                    
                    if pub_date > time_threshold:
                        message = (
                            f"🔥 <b>НОВАЯ РАЗДАЧА / БАНДЛ!</b>\n\n"
                            f"🎮 <b>{entry.title}</b>\n"
                            f"📌 Источник: {source['name']}\n"
                            f"🔗 <a href='{entry.link}'>Забрать / Подробнее</a>"
                        )
                        print(f"🎯 Найдено: {entry.title}")
                        send_telegram_message(message)
                        found_any = True
                        
        except Exception as e:
            print(f"⚠️ Ошибка с {source['name']}: {e}")
            
    if not found_any:
        print("😴 Новых ключей или бандлов за последние 3 часа не найдено.")

if __name__ == "__main__":
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ ОШИБКА: Не настроены переменные TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID в Secrets!")
    else:
        check_keys()
