from flask import Flask, render_template, request, redirect, url_for, jsonify
import threading
import time
from datetime import datetime
import pickle
import os
import logging
import requests
from bs4 import BeautifulSoup
import qrcode
from io import BytesIO
import base64
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(
    filename='stock_monitor.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

# Configuration
class Config:
    TELEGRAM_BOT_TOKEN = '7913485634:AAEwEGddqVxVvq-32qKFLTYueCZ1SL-KWpA'
    TELEGRAM_CHAT_ID = '7706289153'
    CHECK_INTERVAL = 600  # 10 minutes in seconds
    MODEL_PATH = "models/stock_availability_model.pkl"
    VECTORIZER_PATH = "models/stock_vectorizer.pkl"

# Stock checker class
class StockChecker:
    def __init__(self):
        self.load_models()
        self.monitoring_threads = {}
        self.monitoring_status = {}

    def load_models(self):
        """Load the ML models"""
        try:
            with open(Config.MODEL_PATH, "rb") as model_file:
                self.model = pickle.load(model_file)
            with open(Config.VECTORIZER_PATH, "rb") as vectorizer_file:
                self.vectorizer = pickle.load(vectorizer_file)
        except Exception as e:
            logging.error(f"Error loading models: {str(e)}")
            raise

    def get_html(self, url):
        """Fetch HTML content from URL"""
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service)
            driver.get(url)
            html = driver.page_source
            driver.quit()
            return html
        except Exception as e:
            logging.error(f"Error fetching HTML: {str(e)}")
            return None

    def check_stock(self, url):
        """Check stock status for given URL"""
        html = self.get_html(url)
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

                X = self.vectorizer.transform([features])
                prediction = self.model.predict(X)[0]
                probability = self.model.predict_proba(X)[0]
                confidence = max(probability) * 100

                if confidence > max_confidence:
                    stock_status = prediction
                    max_confidence = confidence

        return stock_status

    def monitor_stock(self, url, notify_callback):
        """Monitor stock status continuously"""
        last_status = None
        while self.monitoring_status.get(url, False):
            try:
                current_status = self.check_stock(url)
                if current_status is not None:
                    if last_status is not None and current_status != last_status:
                        notify_callback(url, current_status)
                    last_status = current_status
                time.sleep(Config.CHECK_INTERVAL)
            except Exception as e:
                logging.error(f"Error in monitoring thread: {str(e)}")
                time.sleep(60)  # Wait 1 minute before retrying

    def start_monitoring(self, url, notify_callback):
        """Start monitoring a URL"""
        if url not in self.monitoring_threads or not self.monitoring_threads[url].is_alive():
            self.monitoring_status[url] = True
            thread = threading.Thread(
                target=self.monitor_stock,
                args=(url, notify_callback),
                daemon=True
            )
            self.monitoring_threads[url] = thread
            thread.start()
            logging.info(f"Started monitoring: {url}")

    def stop_monitoring(self, url):
        """Stop monitoring a URL"""
        if url in self.monitoring_status:
            self.monitoring_status[url] = False
            logging.info(f"Stopped monitoring: {url}")

# Notification handlers
class NotificationHandler:
    @staticmethod
    def send_telegram_message(message):
        """Send message via Telegram"""
        url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': Config.TELEGRAM_CHAT_ID,
            'text': message
        }
        try:
            response = requests.post(url, data=payload)
            return response.json()
        except Exception as e:
            logging.error(f"Error sending Telegram message: {str(e)}")
            return None

    @staticmethod
    def generate_qr_code(data):
        """Generate QR code for Telegram bot"""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()

# Initialize stock checker
stock_checker = StockChecker()

# Route handlers
@app.route('/', methods=['GET', 'POST'])
def index():
    """Handle main page requests"""
    if request.method == 'POST':
        url = request.form.get('url')
        if url:
            stock_status = stock_checker.check_stock(url)
            status_text = "Stokta" if stock_status == 1 else "Stokta Değil"
            qr_code = NotificationHandler.generate_qr_code("https://t.me/your_telegram_bot")
            return render_template('index.html', status=status_text, qr_code=qr_code, url=url)
    return render_template('index.html')

@app.route('/api/monitor', methods=['POST'])
def start_monitoring():
    """API endpoint to start monitoring"""
    data = request.get_json()
    url = data.get('url')
    if url:
        def notify_callback(url, status):
            status_text = "Stokta" if status == 1 else "Stokta Değil"
            message = f"Ürün stok durumu değişti: {status_text}\nURL: {url}"
            NotificationHandler.send_telegram_message(message)

        stock_checker.start_monitoring(url, notify_callback)
        return jsonify({'status': 'success', 'message': 'Monitoring started'})
    return jsonify({'status': 'error', 'message': 'URL required'}), 400

@app.route('/api/stop-monitor', methods=['POST'])
def stop_monitoring():
    """API endpoint to stop monitoring"""
    data = request.get_json()
    url = data.get('url')
    if url:
        stock_checker.stop_monitoring(url)
        return jsonify({'status': 'success', 'message': 'Monitoring stopped'})
    return jsonify({'status': 'error', 'message': 'URL required'}), 400

if __name__ == '__main__':
    app.run(debug=True)