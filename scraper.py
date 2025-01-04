from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import logging

# Loglama ayarları
logging.basicConfig(filename='scraper.log', level=logging.INFO, format='%(asctime)s %(message)s')

# WebDriver'ı başlatma (headless modda)
def init_driver():
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Tarayıcı penceresini açmadan çalıştır
        chrome_options.add_argument("--disable-gpu")  # GPU kullanımını devre dışı bırak
        chrome_options.add_argument("--no-sandbox")  # Sandbox modunu devre dışı bırak

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logging.info("WebDriver başarıyla başlatıldı.")
        return driver
    except Exception as e:
        logging.error(f"WebDriver başlatılırken hata oluştu: {e}")
        return None

# HTML çekme fonksiyonu
def get_html(driver, url):
    try:
        driver.get(url)  # Belirtilen URL'e gidiliyor
        # Sayfanın tamamen yüklenmesini bekleyin (örneğin, body etiketinin görünmesini bekleyin)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        html = driver.page_source  # Sayfanın kaynak kodları alınıyor
        logging.info(f"URL başarıyla çekildi: {url}")
        return html
    except Exception as e:
        logging.error(f"Hata oluştu: {e} - URL: {url}")
        return None

# HTML'i parse etme fonksiyonu
def parse_html(html):
    try:
        soup = BeautifulSoup(html, "html.parser")
        elements = soup.find_all(["div", "span", "p"])  # Sadece div, span ve p etiketlerini döndürür
        logging.info("HTML başarıyla parse edildi.")
        return elements
    except Exception as e:
        logging.error(f"HTML parse edilirken hata oluştu: {e}")
        return None

# WebDriver'ı kapatma fonksiyonu
def close_driver(driver):
    try:
        driver.quit()
        logging.info("WebDriver başarıyla kapatıldı.")
    except Exception as e:
        logging.error(f"WebDriver kapatılırken hata oluştu: {e}")



# if __name__ == "__main__":
#     # Test URL'si
#     test_url = "https://www.pt.com.tr/macbook-pro-14-inc-m3-8cpu-10gpu-16gb-512gb-uzay-grisi-z1c8000k7"
#     html_content = get_html(test_url)  # URL içeriği çekiliyor
#     elements = parse_html(html_content)  # Çekilen içeriğin HTML analizi yapılıyor

#     for element in elements[:10]:  # İlk 10 elementi yazdırıyoruz
#         print(f"Tag: {element.name}, Text: {element.text.strip()}")