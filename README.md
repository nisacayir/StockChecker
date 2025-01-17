# Automated Stock Tracking System

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.3.2-green)
![Selenium](https://img.shields.io/badge/Selenium-4.27.1-orange)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.6.0-red)
![Telegram](https://img.shields.io/badge/Telegram-API-lightgrey)

An intelligent, Python-based **Stock Tracking System** that automates the process of monitoring product availability on e-commerce websites. The system sends **real-time notifications** via Telegram when the stock status of a tracked product changes.

---

## **Features**

- **Automatic Stock Status Detection**: Dynamically identifies stock status elements on e-commerce websites using keyword matching and machine learning.
- **Real-Time Notifications**: Sends instant alerts via Telegram when stock status changes.
- **Multi-Site Support**: Works across multiple e-commerce platforms by adapting to different website structures.
- **Machine Learning Integration**: Uses a Random Forest Classifier to improve stock status prediction accuracy.
- **User-Friendly Interface**: A clean and responsive web interface built with Flask.
- **QR Code Integration**: Easily connect to the Telegram bot using a QR code.
- **Database Support**: Stores user data, product URLs, and tracking history in an SQLite database.
- **Scalable and Customizable**: Well-documented code for easy customization and deployment on cloud platforms like Heroku, AWS, and Google Cloud.

---

## **How It Works**

1. **User Input**: The user enters the product URL in the web interface.
2. **HTML Scraping**: Selenium opens the product page and retrieves the HTML content.
3. **Stock Status Detection**: BeautifulSoup parses the HTML, and the machine learning model predicts the stock status.
4. **Notification Sending**: If the stock status changes, a notification is sent to the user via Telegram.
5. **Database Update**: The stock status is updated in the SQLite database.

---

## **Technologies Used**

- **Python**: Primary programming language
- **Flask**: Web framework for the user interface
- **Selenium**: Browser automation for web scraping
- **BeautifulSoup**: HTML parsing library
- **Scikit-learn**: Machine learning library for stock status prediction
- **SQLite**: Lightweight database for storing user data and product information
- **Telegram API**: Sends real-time notifications to users
- **QR Code Generation**: Simplifies Telegram bot setup

---

## **Installation**

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/stock-tracking-system.git
   cd stock-tracking-system
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your Telegram bot:
   - Create a bot using [BotFather](https://core.telegram.org/bots#botfather) and get the bot token
   - Replace the `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in `app.py` with your bot token and chat ID

4. Run the application:
   ```bash
   python app.py
   ```

5. Open your browser and navigate to `http://127.0.0.1:5000` to access the web interface.

---

## **Usage**

1. **Add Product URL**: Enter the product URL in the web interface and click "Start Tracking."
2. **Track Stock Status**: The system will periodically check the stock status and send notifications via Telegram.
3. **QR Code Setup**: Scan the QR code to connect to the Telegram bot and receive notifications.

---

## **Future Work**

- **Support for More E-commerce Platforms**: Add site-specific rules for additional websites.
- **Advanced Machine Learning Models**: Improve accuracy with more complex models and larger datasets.
- **Multi-User Support**: Allow multiple users to track products with individual accounts.
- **Integration with Other Messaging Platforms**: Add support for WhatsApp, Slack, or email notifications.
- **Mobile App Development**: Create a mobile app for easier access and tracking.

---

## **License**

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## **Contact**

For questions or feedback, feel free to reach out:

- **Email**: nisacayir@icloud.com
- **GitHub**: https://github.com/nisacayir
- **LinkedIn**: https://linkedin.com/in/nisacayir
