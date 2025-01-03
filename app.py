import logging
import pickle
import smtplib
import os  # Dosya kontrolü için os modülü
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import Flask, request, jsonify

# Flask uygulaması başlat
app = Flask(__name__)

# Logger ayarları
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Model ve vektörleştiriciyi yükleme
model_path = "stock_availability_model.pkl"
vectorizer_path = "stock_vectorizer.pkl"

# Dosyaların varlığını kontrol edin
if not os.path.exists(model_path):
    raise FileNotFoundError(
        f"'{model_path}' bulunamadı. Lütfen model dosyasının doğru yerde olduğundan veya dosya yolunun doğru yazıldığından emin olun.")

if not os.path.exists(vectorizer_path):
    raise FileNotFoundError(
        f"'{vectorizer_path}' bulunamadı. Lütfen vektörleştirici dosyasının doğru yerde olduğundan veya dosya yolunun doğru yazıldığından emin olun.")

# Dosyaları yükle
with open(model_path, "rb") as model_file:
    model = pickle.load(model_file)

with open(vectorizer_path, "rb") as vectorizer_file:
    vectorizer = pickle.load(vectorizer_file)


# Özellik çıkarma fonksiyonu
def extract_features(data):
    text = data.get("text", "").lower()
    tag_name = data.get("tag_name", "").lower()
    class_count = data.get("class_count", 0)
    return f"{text} {tag_name} {class_count}"


# Email gönderimi fonksiyonu
def send_email(subject, message, to_email):
    sender_email = "youremail@example.com"
    sender_password = "yourpassword"

    try:
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(message, "plain"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())

        logging.info(f"Email sent to {to_email}: Subject: {subject}, Message: {message}")
    except Exception as e:
        logging.error(f"Email sending failed: {str(e)}")


# Ana route: Tahmin işlemi için
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # İstekten verileri al
        data = request.json
        if not data:
            return jsonify({"error": "Geçersiz veri"}), 400

        # Özellik çıkarma ve vektörleştirme
        features = extract_features(data)
        vectorized_features = vectorizer.transform([features])

        # Tahmin yapma
        prediction = model.predict(vectorized_features)
        result = "Stokta" if prediction[0] == 1 else "Stokta değil"

        # Email gönderme
        to_email = data.get("email", "default@example.com")
        subject = "Stok Durumu"
        message = f"Ürün durumu: {result}"
        send_email(subject, message, to_email)

        # Log işlemi
        logging.info(f"Prediction requested: {data}, Result: {result}")

        return jsonify({"prediction": result})

    except Exception as e:
        error_message = str(e)
        logging.error(f"Prediction error: {error_message}")
        return jsonify({"error": error_message}), 500


# Sağlık kontrolü için basit bir route
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "API çalışıyor"})


# Logları görüntülemek için route
@app.route('/logs', methods=['GET'])
def get_logs():
    try:
        with open("app.log", "r") as log_file:
            logs = log_file.read()
        return jsonify({"logs": logs})
    except Exception as e:
        error_message = str(e)
        logging.error(f"Log read error: {error_message}")
        return jsonify({"error": error_message}), 500


# Uygulamayı başlat
if __name__ == '__main__':
    app.run(debug=True)
