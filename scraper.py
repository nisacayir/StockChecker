from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


# HTML çekme fonksiyonu
def get_html(url):
    # WebDriverManager ile `ChromeDriver` otomatik ayarlanıyor
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.get(url)  # Belirtilen URL'e gidiliyor
    html = driver.page_source  # Sayfanın kaynak kodları alınıyor
    driver.quit()  # Tarayıcı kapatılıyor
    return html


# HTML'i parse etme fonksiyonu
def parse_html(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.find_all(True)  # Tüm HTML etiketlerini döndürür

# if __name__ == "__main__":
#     # Test URL'si
#     test_url = "https://www.pt.com.tr/macbook-pro-14-inc-m3-8cpu-10gpu-16gb-512gb-uzay-grisi-z1c8000k7"
#     html_content = get_html(test_url)  # URL içeriği çekiliyor
#     elements = parse_html(html_content)  # Çekilen içeriğin HTML analizi yapılıyor

#     for element in elements[:10]:  # İlk 10 elementi yazdırıyoruz
#         print(f"Tag: {element.name}, Text: {element.text.strip()}")