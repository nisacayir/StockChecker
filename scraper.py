import os
import logging
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from contextlib import contextmanager

# Log dosyasını sil
if os.path.exists('scraper.log'):
    try:
        os.remove('scraper.log')
    except PermissionError:
        print("Log dosyası başka bir işlem tarafından kullanılıyor. Silme işlemi atlandı.")

# Loglama ayarlarına bakma
logging.basicConfig(
    filename='scraper.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

# Bağlantı havuzu ayarları
retry_strategy = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session = requests.Session()
adapter = HTTPAdapter(pool_connections=50, pool_maxsize=100, max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

# WebDriver başlatma fonksiyonu
def init_driver(retries=3):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    for attempt in range(retries):
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_page_load_timeout(30)
            logging.info("WebDriver başarıyla başlatıldı.")
            return driver
        except Exception as e:
            logging.error(f"Attempt {attempt + 1}/{retries} failed: {str(e)}")
            time.sleep(2 * (attempt + 1))
    logging.error("WebDriver başlatılamadı.")
    return None

def get_html(driver, url):
    try:
        if not driver or not driver.session_id:
            raise WebDriverException("Driver oturumu geçersiz!")
        driver.get(url)
        WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        return driver.page_source
    except TimeoutException:
        logging.error(f"Sayfa yüklenirken zaman aşımı oluştu: {url}")
    except WebDriverException as e:
        logging.error(f"WebDriver ile ilgili bir hata oluştu: {e}")
    except Exception as e:
        logging.error(f"get_html sırasında hata: {str(e)}")
    return None

def parse_html(html):
    if not html:
        logging.error("Parse edilecek HTML içeriği yok.")
        return None
    try:
        soup = BeautifulSoup(html, "html.parser")
        elements = soup.find_all(['div', 'span', 'p'])
        logging.info("HTML başarıyla parse edildi.")
        return elements
    except Exception as e:
        logging.error(f"HTML parse edilirken hata oluştu: {e}")
        return None

def close_driver(driver):
    try:
        if driver and driver.session_id:
            logging.info("WebDriver kapatılıyor...")
            driver.quit()
    except Exception as e:
        logging.error(f"WebDriver kapatılırken hata oluştu: {str(e)}")

@contextmanager
def managed_driver():
    driver = init_driver()
    try:
        yield driver
    finally:
        if driver:
            close_driver(driver)

def scrape_website(url):
    with managed_driver() as driver:
        if driver:
            html = get_html(driver, url)
            if html:
                return parse_html(html)
    return None
