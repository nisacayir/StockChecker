import tkinter as tk
from tkinter import ttk, messagebox
import pickle
import os
from datetime import datetime
import time
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.common.exceptions import WebDriverException


class StockCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Stok Takip Sistemi")
        self.root.geometry("800x700")

        # Kontrol değişkenleri
        self.monitoring = False
        self.last_stock_status = None

        #model yüklemek icin
        self.load_model()

        #container duzeni
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        #yazi tipi boyutu
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Helvetica', 14, 'bold'))

        #baslık
        title_label = ttk.Label(main_frame, text="Stok Takip ve Bildirim Sistemi", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        #design sadece frame icin
        settings_frame = ttk.LabelFrame(main_frame, text="Ayarlar", padding="10")
        settings_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        #url yazma butonu
        ttk.Label(settings_frame, text="Ürün URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.url_entry = ttk.Entry(settings_frame, width=60)
        self.url_entry.grid(row=0, column=1, sticky=tk.W, pady=5)

        #gonderen alan mail islemleri
        ttk.Label(settings_frame, text="Gönderen Email:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.sender_email = ttk.Entry(settings_frame, width=40)
        self.sender_email.grid(row=1, column=1, sticky=tk.W, pady=5)

        ttk.Label(settings_frame, text="Email Şifresi:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.email_password = ttk.Entry(settings_frame, width=40, show="*")
        self.email_password.grid(row=2, column=1, sticky=tk.W, pady=5)

        ttk.Label(settings_frame, text="Alıcı Email:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.receiver_email = ttk.Entry(settings_frame, width=40)
        self.receiver_email.grid(row=3, column=1, sticky=tk.W, pady=5)

        #kontrol araligina bakmak icin
        ttk.Label(settings_frame, text="Kontrol Aralığı (dk):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.check_interval = ttk.Spinbox(settings_frame, from_=1, to=60, width=5)
        self.check_interval.grid(row=4, column=1, sticky=tk.W, pady=5)
        self.check_interval.set(5) #simdilik bes dk ayarli

        #butonlar icin
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        self.start_button = ttk.Button(button_frame, text="Takibi Başlat", command=self.start_monitoring)
        self.start_button.grid(row=0, column=0, padx=5)

        self.stop_button = ttk.Button(button_frame, text="Takibi Durdur", command=self.stop_monitoring,
                                      state='disabled')
        self.stop_button.grid(row=0, column=1, padx=5)

        #status basladı var yok bekle
        self.status_var = tk.StringVar(value="Durum: Bekleniyor")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=3, column=0, columnspan=2, pady=5)

        #log kaydı icin
        log_frame = ttk.LabelFrame(main_frame, text="İşlem Kayıtları", padding="10")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        self.log_text = tk.Text(log_frame, height=15, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E))

        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text.configure(yscrollcommand=scrollbar.set)

    def load_model(self):
        """Model ve vektörleştiriciyi yükler"""
        try:
            model_path = "models/stock_availability_model.pkl"
            vectorizer_path = "models/stock_vectorizer.pkl"

            with open(model_path, "rb") as model_file:
                self.model = pickle.load(model_file)

            with open(vectorizer_path, "rb") as vectorizer_file:
                self.vectorizer = pickle.load(vectorizer_file)
        except Exception as e:
            messagebox.showerror("Hata", f"Model yükleme hatası: {str(e)}")
            self.root.destroy()

    def send_email(self, subject, message):
        """Email gönderme fonksiyonu"""
        try:
            msg = MIMEMultipart()
            msg["From"] = self.sender_email.get()
            msg["To"] = self.receiver_email.get()
            msg["Subject"] = subject

            msg.attach(MIMEText(message, "plain"))

            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(self.sender_email.get(), self.email_password.get())
                server.send_message(msg)

            self.log(f"Email gönderildi: {subject}")
            return True
        except Exception as e:
            self.log(f"Email gönderimi başarısız: {str(e)}")
            return False

    def get_html(self, url):
        """URL'den HTML içeriğini çeker"""
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service) #eğer scraperden  html veri cekemezse burada sorun cıkarrrrr
            driver.get(url)
            html = driver.page_source
            driver.quit()
            return html
        except Exception as e:
            self.log(f"HTML çekme hatası: {str(e)}")
            return None

    def check_stock(self):
        """Stok durumunu kontrol eder"""
        url = self.url_entry.get().strip()
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

    def log(self, message):
        """Log mesajı ekler"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.insert("1.0", f"[{timestamp}] {message}\n")

    def monitor_stock(self):
        """Stok durumunu periyodik olarak kontrol eder"""
        while self.monitoring:
            try:
                current_status = self.check_stock()

                if current_status is not None:
                    status_text = "Stokta" if current_status == 1 else "Stokta Değil"
                    self.log(f"Mevcut durum: {status_text}")

                    if self.last_stock_status is not None and current_status != self.last_stock_status:
                        if current_status == 1:
                            subject = "Stok Durumu Değişti - STOKTA!"
                            message = f"Ürün stoğa girdi!\nURL: {self.url_entry.get()}"
                            self.send_email(subject, message)

                    self.last_stock_status = current_status

                interval = int(self.check_interval.get()) * 60
                for i in range(interval, 0, -1):
                    if not self.monitoring:
                        break
                    self.status_var.set(f"Durum: Sonraki kontrol {i} saniye sonra")
                    time.sleep(1)

            except Exception as e:
                self.log(f"Hata oluştu: {str(e)}")
                time.sleep(60)  # hata olustugunda 1 dakika bekle ve olana bak tekrar devam et

    def start_monitoring(self):
        """Takibi başlatır"""
        if not all([
            self.url_entry.get().strip(),
            self.sender_email.get().strip(),
            self.email_password.get().strip(),
            self.receiver_email.get().strip()
        ]):
            messagebox.showwarning("Uyarı", "Lütfen tüm alanları doldurun!")
            return

        self.monitoring = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.log("Stok takibi başlatıldı")

        #bir thread oluşturur ve takibe başlıyor
        self.monitor_thread = threading.Thread(target=self.monitor_stock)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Takibi durdurur"""
        self.monitoring = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_var.set("Durum: Durduruldu")
        self.log("Stok takibi durduruldu")


def main():
    root = tk.Tk()
    app = StockCheckerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()