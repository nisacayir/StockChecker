from flask import Flask, render_template, request, redirect, url_for
import threading
import time
import logging
import requests
import scraper
from bs4 import BeautifulSoup
import pickle

app = Flask(__name__)

# Loglama ayarları
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s %(message)s')

# WebDriver yönetimi
driver = None
monitoring = False
last_stock_status = None

# Telegram bot ayarları
TELEGRAM_BOT_TOKEN = 'a'
TELEGRAM_CHAT_ID = 'a'

# Model ve vektörleştirici şey .
with open("models/stock_availability_model.pkl", "rb") as model_file:
    model = pickle.load(model_file)

with open("models/stock_vectorizer.pkl", "rb") as vectorizer_file:
    vectorizer = pickle.load(vectorizer_file)

# Telegram mesajı
def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            logging.info(f"Telegram mesajı gönderildi: {message}")
        else:
            logging.error(f"Telegram mesajı gönderilemedi: {response.text}")
    except Exception as e:
        logging.error(f"Telegram mesajı gönderilirken hata oluştu: {e}")

# Stok durumu kontrolü
def check_stock(url):
    try:
        html = scraper.get_html(driver, url)
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")
        elements = soup.find_all(True)
        stock_status = None
        max_confidence = 0

        for element in elements:
            text = element.get_text().strip()
            if text and ("stok" in text.lower() or "tükendi" in text.lower()):
                features = {
                    "text_length": len(text),
                    "tag_name": element.name,
                    "class_count": len(element.get("class", [])),
                    "contains_stok": 1 if "stok" in text.lower() else 0,
                    "contains_var": 1 if "var" in text.lower() else 0,
                    "contains_yok": 1 if "yok" in text.lower() or "tükendi" in text.lower() else 0,
                    "contains_number": 1 if any(char.isdigit() for char in text) else 0,
                }

                X = vectorizer.transform([features])
                prediction = model.predict(X)[0]
                probability = model.predict_proba(X)[0]
                confidence = max(probability) * 100

                if confidence > max_confidence:
                    stock_status = prediction
                    max_confidence = confidence

        return stock_status
    except Exception as e:
        logging.error(f"Stok kontrolünde hata oluştu: {e}")
        return None

# Stok izleme fonksiyonu
def monitor_stock(url):
    global monitoring, last_stock_status
    while monitoring:
        try:
            current_status = check_stock(url)
            if current_status is not None and current_status != last_stock_status:
                message = f"Stok durumu değişti: {'Stokta' if current_status == 1 else 'Stokta Değil'}\nURL: {url}"
                send_telegram_message(message)
                last_stock_status = current_status

            time.sleep(600)  # 10 dakika
        except Exception as e:
            logging.error(f"Stok izleme sırasında hata: {e}")
            time.sleep(60)

# Ana sayfa
@app.route('/', methods=['GET', 'POST'])
def index():
    global monitoring, driver
    if request.method == 'POST':
        url = request.form['url']
        if not monitoring:
            monitoring = True
            if driver is None:
                driver = scraper.init_driver()
            threading.Thread(target=monitor_stock, args=(url,), daemon=True).start()
        return redirect(url_for('index'))
    return render_template('index.html', monitoring=monitoring)

@app.teardown_appcontext
def teardown(exception):
    global driver
    if driver:
        scraper.close_driver(driver)
        driver = None

if __name__ == '__main__':
    app.run(debug=True)