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

# Loglama ayarları
logging.basicConfig(
    filename='scraper.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

session = requests.Session()
adapter = HTTPAdapter(pool_connections=110, pool_maxsize=110)
session.mount("http://", adapter)
session.mount("https://", adapter)


# WebDriver kısmı
def init_driver():
    """
    Selenium WebDriver başlatma fonksiyonu.
    Headless modda bir Chrome WebDriver döndürür.
    """
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Tarayıcı arayüzü olmadan çalıştır
        chrome_options.add_argument("--disable-gpu")  # GPU desteğini devre dışı bırak
        chrome_options.add_argument("--no-sandbox")  # Sandbox'ı devre dışı bırak
        chrome_options.add_argument("--window-size=1920,1080")  # Tarayıcı boyutunu ayarla
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")  # User-Agent ekle

        # WebDriver'ı başlat
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logging.info("WebDriver başarıyla başlatıldı.")
        return driver
    except Exception as e:
        logging.error(f"WebDriver başlatılırken hata oluştu: {e}")
        return None


# HTML çekme
def get_html(driver, url):
    """
    Belirtilen bir URL'den HTML içeriğini alır.
    driver: Selenium WebDriver nesnesi
    url: Bir web sayfasının URL'si
    """
    if driver is None:  # Driver null kontrolü
        logging.error("Driver başlatılamadı. HTML alınamadı.")
        return None

    try:
        driver.get(url)
        time.sleep(5)  # 5 saniye bekle
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        return driver.page_source
    except TimeoutException:
        logging.error(f"Sayfa yüklenirken zaman aşımı oluştu: {url}")
        return None
    except WebDriverException as e:
        logging.error(f"WebDriver ile ilgili bir hata oluştu: {e}")
        return None
    except Exception as e:
        logging.error(f"Beklenmeyen bir hata oluştu: {e}")
        return None


# HTML parse
def parse_html(html):
    """
    Alınan HTML içeriğini parse eder ve belirtilen elementleri döndürür.
    html: Çözümlenecek HTML içeriği
    """
    if not html:
        logging.error("Parse edilecek HTML içeriği yok.")
        return None

    try:
        soup = BeautifulSoup(html, "html.parser")
        elements = soup.find_all(["div", "span", "p"])  # Sadece belirli etiketleri al
        logging.info("HTML başarıyla parse edildi.")
        return elements
    except Exception as e:
        logging.error(f"HTML parse edilirken hata oluştu: {e}")
        return None


# WebDriver'ı kapatma
def close_driver(driver):
    """
    WebDriver'ı kapatır.
    driver: Selenium WebDriver nesnesi
    """
    try:
        if driver:
            logging.info("WebDriver kapatılıyor...")
            driver.quit()
            logging.info("WebDriver başarıyla kapatıldı.")
    except Exception as e:
        logging.error(f"WebDriver kapatılırken hata oluştu: {e}")
