from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import pickle
import os


data = [
    {"text": "Stokta Yok", "tag_name": "div", "class_count": 2, "is_stock_available": 0},
    {"text": "Stok Var", "tag_name": "span", "class_count": 1, "is_stock_available": 1},
    {"text": "Out of Stock", "tag_name": "div", "class_count": 3, "is_stock_available": 0},
    {"text": "In Stock", "tag_name": "span", "class_count": 1, "is_stock_available": 1},
    {"text": "Ürün Tükendi", "tag_name": "p", "class_count": 1, "is_stock_available": 0},
    {"text": "Mevcut Değil", "tag_name": "div", "class_count": 2, "is_stock_available": 0},
    {"text": "Hemen Al", "tag_name": "a", "class_count": 2, "is_stock_available": 1},
    {"text": "Sepete Ekle", "tag_name": "button", "class_count": 1, "is_stock_available": 1},
    {"text": "Stoklarımızda Yok", "tag_name": "div", "class_count": 2, "is_stock_available": 0},
    {"text": "Sipariş Ver", "tag_name": "span", "class_count": 1, "is_stock_available": 1},
    {"text": "Tükendi", "tag_name": "div", "class_count": 1, "is_stock_available": 0},
    {"text": "Stokta Sınırlı", "tag_name": "span", "class_count": 2, "is_stock_available": 1},
    {"text": "Son Ürün", "tag_name": "div", "class_count": 1, "is_stock_available": 1},
    {"text": "Stokta Mevcut", "tag_name": "span", "class_count": 1, "is_stock_available": 1},
    {"text": "Geçici Olarak Temin Edilemiyor", "tag_name": "div", "class_count": 3, "is_stock_available": 0},
    {"text": "Stokta Yok", "tag_name": "p", "class_count": 1, "is_stock_available": 0},
    {"text": "Stokta Var", "tag_name": "span", "class_count": 1, "is_stock_available": 1},
    {"text": "Ürün Yok", "tag_name": "div", "class_count": 2, "is_stock_available": 0},
    {"text": "Hemen Satın Al", "tag_name": "a", "class_count": 2, "is_stock_available": 1},
    {"text": "Stokta Kalmadı", "tag_name": "div", "class_count": 1, "is_stock_available": 0},
    {"text": "Stokta Mevcut Değil", "tag_name": "span", "class_count": 2, "is_stock_available": 0},
    {"text": "Stokta Sadece 2 Adet Kaldı", "tag_name": "div", "class_count": 2, "is_stock_available": 1},
    {"text": "Stokta Yok", "tag_name": "span", "class_count": 1, "is_stock_available": 0},
    {"text": "Stokta Var", "tag_name": "div", "class_count": 1, "is_stock_available": 1},
    {"text": "Ürün Stokta Yok", "tag_name": "p", "class_count": 1, "is_stock_available": 0},
    {"text": "Stokta Mevcut", "tag_name": "span", "class_count": 1, "is_stock_available": 1},
    {"text": "Stokta Sınırlı Sayıda", "tag_name": "div", "class_count": 2, "is_stock_available": 1},
    {"text": "Stokta Yok", "tag_name": "span", "class_count": 1, "is_stock_available": 0},
    {"text": "Stokta Var", "tag_name": "div", "class_count": 1, "is_stock_available": 1},
    {"text": "Ürün Tükendi", "tag_name": "p", "class_count": 1, "is_stock_available": 0},
    {"text": "Stokta Mevcut", "tag_name": "span", "class_count": 1, "is_stock_available": 1},
    {"text": "Stokta Yok", "tag_name": "div", "class_count": 2, "is_stock_available": 0},
    {"text": "Stokta Var", "tag_name": "span", "class_count": 1, "is_stock_available": 1},
    {"text": "Out of Stock", "tag_name": "div", "class_count": 3, "is_stock_available": 0},
    {"text": "In Stock", "tag_name": "span", "class_count": 1, "is_stock_available": 1},
    {"text": "Ürün Tükendi", "tag_name": "p", "class_count": 1, "is_stock_available": 0},
    {"text": "Mevcut Değil", "tag_name": "div", "class_count": 2, "is_stock_available": 0},
    {"text": "Hemen Al", "tag_name": "a", "class_count": 2, "is_stock_available": 1},
    {"text": "Sepete Ekle", "tag_name": "button", "class_count": 1, "is_stock_available": 1},
    {"text": "Stoklarımızda Yok", "tag_name": "div", "class_count": 2, "is_stock_available": 0},
    {"text": "Sipariş Ver", "tag_name": "span", "class_count": 1, "is_stock_available": 1},
    {"text": "Tükendi", "tag_name": "div", "class_count": 1, "is_stock_available": 0},
    {"text": "Stokta Sınırlı", "tag_name": "span", "class_count": 2, "is_stock_available": 1},
    {"text": "Son Ürün", "tag_name": "div", "class_count": 1, "is_stock_available": 1},
    {"text": "Stokta Mevcut", "tag_name": "span", "class_count": 1, "is_stock_available": 1},
    {"text": "Geçici Olarak Temin Edilemiyor", "tag_name": "div", "class_count": 3, "is_stock_available": 0},
    {"text": "Stokta Yok", "tag_name": "p", "class_count": 1, "is_stock_available": 0},
    {"text": "Stokta Var", "tag_name": "span", "class_count": 1, "is_stock_available": 1},
    {"text": "Ürün Yok", "tag_name": "div", "class_count": 2, "is_stock_available": 0},
    {"text": "Hemen Satın Al", "tag_name": "a", "class_count": 2, "is_stock_available": 1},
    {"text": "Stokta Kalmadı", "tag_name": "div", "class_count": 1, "is_stock_available": 0},
    {"text": "Stokta Mevcut Değil", "tag_name": "span", "class_count": 2, "is_stock_available": 0},
    {"text": "Stokta Sadece 2 Adet Kaldı", "tag_name": "div", "class_count": 2, "is_stock_available": 1},
    {"text": "Stokta Yok", "tag_name": "span", "class_count": 1, "is_stock_available": 0},
    {"text": "Stokta Var", "tag_name": "div", "class_count": 1, "is_stock_available": 1},
    {"text": "Ürün Stokta Yok", "tag_name": "p", "class_count": 1, "is_stock_available": 0},
    {"text": "Stokta Mevcut", "tag_name": "span", "class_count": 1, "is_stock_available": 1},
    {"text": "Stokta Sınırlı Sayıda", "tag_name": "div", "class_count": 2, "is_stock_available": 1},
    {"text": "Stokta Yok", "tag_name": "span", "class_count": 1, "is_stock_available": 0},
    {"text": "Stokta Var", "tag_name": "div", "class_count": 1, "is_stock_available": 1},
    {"text": "Ürün Tükendi", "tag_name": "p", "class_count": 1, "is_stock_available": 0},
    {"text": "Stokta Mevcut", "tag_name": "span", "class_count": 1, "is_stock_available": 1},
    {"text": "Stokta Yok", "tag_name": "div", "class_count": 2, "is_stock_available": 0},
    {"text": "Stokta Var", "tag_name": "span", "class_count": 1, "is_stock_available": 1},
    # Yeni eklenen "stokta var" varyasyonları
    {"text": "Stokta Mevcuttur", "tag_name": "span", "class_count": 1, "is_stock_available": 1},
    {"text": "Stokta", "tag_name": "div", "class_count": 1, "is_stock_available": 1},
    {"text": "Stoklarımızda Mevcut", "tag_name": "span", "class_count": 2, "is_stock_available": 1},
    {"text": "Ürün Stokta", "tag_name": "p", "class_count": 1, "is_stock_available": 1},
    {"text": "Stokta Bulunmaktadır", "tag_name": "div", "class_count": 2, "is_stock_available": 1},
    {"text": "Stokta Mevcut Ürün", "tag_name": "span", "class_count": 1, "is_stock_available": 1},
    {"text": "Stokta Var, Hemen Al", "tag_name": "a", "class_count": 2, "is_stock_available": 1},
    {"text": "Stokta Var, Sepete Ekle", "tag_name": "button", "class_count": 1, "is_stock_available": 1},
    {"text": "Stokta Var, Sipariş Ver", "tag_name": "span", "class_count": 1, "is_stock_available": 1},
    {"text": "Stokta Var, Hemen Satın Al", "tag_name": "a", "class_count": 2, "is_stock_available": 1},
    {"text": "Stokta Var, Son Ürün", "tag_name": "div", "class_count": 1, "is_stock_available": 1},
    {"text": "Stokta Var, Sınırlı Sayıda", "tag_name": "span", "class_count": 2, "is_stock_available": 1},
    {"text": "Stokta Var, Hemen Alın", "tag_name": "a", "class_count": 2, "is_stock_available": 1},
    {"text": "Stokta Var, Hemen Satın Alın", "tag_name": "a", "class_count": 2, "is_stock_available": 1},
    {"text": "Stokta Var, Hemen Sipariş Ver", "tag_name": "span", "class_count": 1, "is_stock_available": 1},
    {"text": "Stokta Var, Hemen Sepete Ekle", "tag_name": "button", "class_count": 1, "is_stock_available": 1},
    {"text": "Stokta Var, Hemen Alabilirsiniz", "tag_name": "span", "class_count": 1, "is_stock_available": 1},
    {"text": "Stokta Var, Hemen Satın Alabilirsiniz", "tag_name": "a", "class_count": 2, "is_stock_available": 1},
    {"text": "Stokta Var, Hemen Sipariş Verebilirsiniz", "tag_name": "span", "class_count": 1, "is_stock_available": 1},
    {"text": "Stokta Var, Hemen Sepete Ekleyebilirsiniz", "tag_name": "button", "class_count": 1, "is_stock_available": 1},
    {"text": "Stokta Var, Hemen Alın", "tag_name": "a", "class_count": 2, "is_stock_available": 1},
    {"text": "Stokta Var, Hemen Satın Alın", "tag_name": "a", "class_count": 2, "is_stock_available": 1},
    {"text": "Stokta Var, Hemen Sipariş Verin", "tag_name": "span", "class_count": 1, "is_stock_available": 1},
    {"text": "Stokta Var, Hemen Sepete Ekleyin", "tag_name": "button", "class_count": 1, "is_stock_available": 1},
    {"text": "Stokta Var, Hemen Alabilirsiniz", "tag_name": "span", "class_count": 1, "is_stock_available": 1},
    {"text": "Stokta Var, Hemen Satın Alabilirsiniz", "tag_name": "a", "class_count": 2, "is_stock_available": 1},
    {"text": "Stokta Var, Hemen Sipariş Verebilirsiniz", "tag_name": "span", "class_count": 1, "is_stock_available": 1},
    {"text": "Stokta Var, Hemen Sepete Ekleyebilirsiniz", "tag_name": "button", "class_count": 1, "is_stock_available": 1},
    {"text": "Stokta Var, Hemen Alın", "tag_name": "a", "class_count": 2, "is_stock_available": 1},
    {"text": "Stokta Var, Hemen Satın Alın", "tag_name": "a", "class_count": 2, "is_stock_available": 1},
    {"text": "Stokta Var, Hemen Sipariş Verin", "tag_name": "span", "class_count": 1, "is_stock_available": 1},
    {"text": "Stokta Var, Hemen Sepete Ekleyin", "tag_name": "button", "class_count": 1, "is_stock_available": 1},
    {"text": "Stokta Var, Hemen Alabilirsiniz", "tag_name": "span", "class_count": 1, "is_stock_available": 1},
    {"text": "Stokta Var, Hemen Satın Alabilirsiniz", "tag_name": "a", "class_count": 2, "is_stock_available": 1},
    {"text": "Stokta Var, Hemen Sipariş Verebilirsiniz", "tag_name": "span", "class_count": 1, "is_stock_available": 1},
    {"text": "Stokta Var, Hemen Sepete Ekleyebilirsiniz", "tag_name": "button", "class_count": 1, "is_stock_available": 1},
    {"text": "Stokta Var, Hemen Alın", "tag_name": "a", "class_count": 2, "is_stock_available": 1},
    {"text": "Stokta Var, Hemen Satın Alın", "tag_name": "a", "class_count": 2, "is_stock_available": 1},
    {"text": "Stokta Var, Hemen Sipariş Verin", "tag_name": "span", "class_count": 1, "is_stock_available": 1}
    ]

# Özellik çıkarımı
def extract_features(row):
    text = row["text"].lower()
    return {
        "text_length": len(text),
        "tag_name": row["tag_name"],
        "class_count": row["class_count"],
        "contains_stok": 1 if "stok" in text else 0,
        "contains_var": 1 if "var" in text else 0,
        "contains_yok": 1 if "yok" in text or "tükendi" in text else 0,
        "contains_number": 1 if any(char.isdigit() for char in text) else 0,
    }

def extract_features(row):
    text = row["text"].lower()
    return {
        "text_length": len(text),
        "tag_name": row["tag_name"],
        "class_count": row["class_count"],
        "contains_stok": 1 if "stok" in text else 0,
        "contains_var": 1 if "var" in text else 0,
        "contains_yok": 1 if "yok" in text or "tükendi" in text else 0,
        "contains_number": 1 if any(char.isdigit() for char in text) else 0,
    }


#etiketleri hazırlama
features = [extract_features(d) for d in data]
labels = [d["is_stock_available"] for d in data]

#vektörleştirme
vectorizer = DictVectorizer(sparse=False)
X = vectorizer.fit_transform(features)

# Veri setini eğitim ve test olarak ayır
X_train, X_test, y_train, y_test = train_test_split(X, labels, test_size=0.2, random_state=42)

# modeli yeniden eğit
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# performans değerlendirme
y_pred = model.predict(X_test)
print("Doğruluk (Accuracy):", accuracy_score(y_test, y_pred))
print("Sınıflandırma Raporu:\n", classification_report(y_test, y_pred))


# modeli ve vektörleştiriciyi kaydet
def save_to_pickle(file_path, obj):
    try:
        with open(file_path, "wb") as file:
            pickle.dump(obj, file)
        print(f"{file_path} başarıyla kaydedildi.")
    except Exception as e:
        print(f"Bir hata oluştu: {e}")


# model ve vektörleştirici kaydetme işlemleri
os.makedirs("models", exist_ok=True)
model_path = "models/stock_availability_model.pkl"
vectorizer_path = "models/stock_vectorizer.pkl"

save_to_pickle(model_path, model)
save_to_pickle(vectorizer_path, vectorizer)

print("Model ve vektörleştirici başarıyla eğitildi ve kaydedildi!")