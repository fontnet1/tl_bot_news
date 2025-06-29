import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import time
import json
import os
#ابتدا در سایت بله یک بات جدید بسازید از آی دی botfather و بعد بات رو اجرا کنید و سپس باتی که ساختید رو به کانال خودتون در بله به عنوان ادمین اضافه کنید ، سپس پروژه رو ران کنید
BOTTOKEN = "YOUR BALE BOT TOKEN" #توکن بات که از botfather در بله گرفتید
BALE_API_URL = f"https://tapi.bale.ai/{BOTTOKEN}/sendMessage" #این بخش نیازی به تغییر نداره
CHAT_ID = "YOUR CHANNEL ID IN BALE" #نام کانال شما در بله با همین فرمت

BASE_URL = "https://www.aljazeera.com"
SENT_NEWS_FILE = "sent_news.json"

def fetch_aljazeera_news():
    url = BASE_URL
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    items = []

    for li in soup.select("ul.liveblog-timeline li.liveblog-timeline__update"):
        title_tag = li.select_one("a.liveblog-timeline__update-link h4")
        href_tag = li.select_one("a.liveblog-timeline__update-link")
        time_tag = li.select_one("span.liveblog-timeline__update-display-time")
        if title_tag and href_tag and time_tag:
            title_en = title_tag.text.strip()
            link = BASE_URL + href_tag["href"]
            time_ago = time_tag.text.strip()  # مثلا: "1m ago", "16m ago"
            items.append({"title_en": title_en, "link": link, "time_ago": time_ago})
    return items

def translate_to_persian(text):
    try:
        return GoogleTranslator(source='en', target='fa').translate(text)
    except Exception as e:
        print("ترجمه ناموفق:", e)
        return text

def send_message_to_bale(text):
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "chat_id": CHAT_ID,
        "text": text
    }
    response = requests.post(BALE_API_URL, headers=headers, json=data)
    if response.status_code == 200:
        print("پیام ارسال شد.")
    else:
        print("خطا در ارسال پیام:", response.text)

def convert_time_to_persian(time_ago):
    # تبدیل مثلا "1m ago" به "1 دقیقه پیش" و "2h ago" به "2 ساعت پیش"
    try:
        if 'm' in time_ago:
            num = time_ago.replace('m ago', '').strip()
            return f"{num} دقیقه پیش"
        elif 'h' in time_ago:
            num = time_ago.replace('h ago', '').strip()
            return f"{num} ساعت پیش"
        elif 's' in time_ago:
            num = time_ago.replace('s ago', '').strip()
            return f"{num} ثانیه پیش"
        else:
            return time_ago
    except:
        return time_ago

def format_message(item):
    translated = translate_to_persian(item["title_en"])
    persian_time = convert_time_to_persian(item["time_ago"])
    return f"🌍 منبع: الجزیره\n🕒 زمان انتشار: {persian_time}\n📰 {translated}\n🔗 {item['link']}"

def load_sent_news():
    if os.path.exists(SENT_NEWS_FILE):
        with open(SENT_NEWS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_sent_news(sent):
    with open(SENT_NEWS_FILE, "w", encoding="utf-8") as f:
        json.dump(sent, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    sent_news = load_sent_news()

    while True:
        try:
            news_items = fetch_aljazeera_news()
            new_items = [item for item in news_items if item["title_en"] not in sent_news]

            if new_items:
                for item in new_items:
                    msg = format_message(item)
                    send_message_to_bale(msg)
                    sent_news.append(item["title_en"])
                    time.sleep(1)  # تاخیر برای جلوگیری از اسپم

                save_sent_news(sent_news)
            else:
                print("خبر جدیدی نیست.")

        except Exception as e:
            print("خطا:", e)

        time.sleep(60)  # هر 60 ثانیه دوباره اجرا شود