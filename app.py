from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime
import os
import requests

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# ======================= TELEGRAM =======================
TELEGRAM_BOT_TOKEN = "8471702170:AAFHrxWvoFlvY0inyJly939kbSG372ykhMI"
TELEGRAM_CHAT_ID = 1618931059  # ID мастера, которому приходят заявки

def send_telegram_message(text, photo_bytes=None):
    """
    Отправка уведомления в Telegram мастеру.
    Если передано photo_bytes, отправляем фото с подписью.
    """
    try:
        if photo_bytes:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
            files = {"photo": ("tattoo.jpg", photo_bytes)}
            data = {"chat_id": TELEGRAM_CHAT_ID, "caption": text, "parse_mode": "HTML"}
            r = requests.post(url, data=data, files=files)
            print("Telegram response (photo):", r.json())
        else:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
            r = requests.post(url, data=payload)
            print("Telegram response (text):", r.json())
    except Exception as e:
        print("Ошибка при отправке Telegram:", e)

# ======================= ИНИЦИАЛИЗАЦИЯ БАЗ =======================
def init_db():
    conn = sqlite3.connect('booking.db')
    c = conn.cursor()

    # Таблица записей на тату
    c.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            contact TEXT,
            photo BLOB,
            date_created TEXT
        )
    ''')

    # Таблица отзывов
    c.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            message TEXT,
            date_created TEXT
        )
    ''')

    conn.commit()
    conn.close()

init_db()

# ======================= ГЛАВНАЯ =======================
@app.route("/")
def home():
    conn = sqlite3.connect('booking.db')
    c = conn.cursor()
    # Получаем последние 3 отзыва
    c.execute("SELECT name, message, date_created FROM reviews ORDER BY id DESC LIMIT 3")
    reviews = [{"name": row[0], "message": row[1], "date": row[2]} for row in c.fetchall()]
    conn.close()
    return render_template("index.html", reviews=reviews)

# ======================= СТРАНИЦА ВСЕХ ОТЗЫВОВ =======================
@app.route("/reviews_page")
def reviews_page():
    conn = sqlite3.connect('booking.db')
    c = conn.cursor()
    c.execute("SELECT id, name, message, date_created FROM reviews ORDER BY id DESC")
    reviews = [{"id": row[0], "name": row[1], "message": row[2], "date": row[3]} for row in c.fetchall()]
    conn.close()
    return render_template("reviews.html", reviews=reviews)

# ======================= ОБРАБОТКА ЗАПИСИ НА ТАТУ =======================
@app.route("/book", methods=["POST"])
def book():
    name = request.form.get('name')
    phone = request.form.get('phone')
    contact = request.form.get('contact')
    photo = request.files.get('tattoo_photo')
    photo_bytes = photo.read() if photo else None

    # Сохраняем запись в БД
    conn = sqlite3.connect('booking.db')
    c = conn.cursor()
    c.execute(
        "INSERT INTO bookings (name, phone, contact, photo, date_created) VALUES (?, ?, ?, ?, ?)",
        (name, phone, contact, photo_bytes, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()

    # Формируем сообщение для мастера
    msg = f"📌 <b>Новая запись на тату</b>:\nИмя: {name}\nТелефон: {phone}\nКонтакт: {contact}\nДата: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    send_telegram_message(msg, photo_bytes)

    return jsonify({'success': True})

# ======================= AJAX: ДОБАВЛЕНИЕ ОТЗЫВА =======================
@app.route("/add_review", methods=["POST"])
def add_review():
    name = request.form.get('name')
    message = request.form.get('text')

    if not name or not message:
        return jsonify({'success': False, 'message': 'Все поля обязательны'})

    date_created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect('booking.db')
    c = conn.cursor()
    c.execute(
        "INSERT INTO reviews (name, message, date_created) VALUES (?, ?, ?)",
        (name, message, date_created)
    )
    review_id = c.lastrowid
    conn.commit()
    conn.close()

    return jsonify({
        'success': True,
        'review': {
            'id': review_id,
            'name': name,
            'message': message,
            'date_created': date_created
        }
    })

# ======================= ЗАПУСК =======================
if __name__ == "__main__":
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run()

