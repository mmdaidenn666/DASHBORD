from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2"
DATABASE = 'goyimix.db'

# تابع اتصال به دیتابیس
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ساخت جداول
def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                name TEXT,
                age INTEGER,
                gender TEXT,
                bio TEXT,
                city TEXT,
                password TEXT NOT NULL,
                profile_pic TEXT,
                visible INTEGER DEFAULT 1
            )
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user1 INTEGER,
                user2 INTEGER,
                FOREIGN KEY (user1) REFERENCES users(id),
                FOREIGN KEY (user2) REFERENCES users(id)
            )
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                sender_id INTEGER,
                message TEXT,
                timestamp TEXT,
                FOREIGN KEY (chat_id) REFERENCES chats(id)
            )
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS likes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                liker_id INTEGER,
                liked_id INTEGER,
                FOREIGN KEY (liker_id) REFERENCES users(id),
                FOREIGN KEY (liked_id) REFERENCES users(id)
            )
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                message TEXT,
                type TEXT,
                related_id INTEGER,
                seen INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        db.commit()

# صفحه ثبت‌نام
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm']
        age = request.form['age']
        gender = request.form['gender']
        city = request.form['city']
        name = request.form.get('name', '')
        bio = request.form.get('bio', '')
        interests = request.form.get('interests', '')

        if password != confirm:
            return render_template_string(REGISTER_TEMPLATE, error="رمز عبور مطابقت ندارد.", cities=CITIES)
        if not username or not password or not age or not gender or not city:
            return render_template_string(REGISTER_TEMPLATE, error="لطفاً فیلدهای اجباری را پر کنید.", cities=CITIES)

        db = get_db()
        try:
            db.execute('''
                INSERT INTO users (username, name, age, gender, bio, city, password)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (username, name, age, gender, bio, city, password))
            db.commit()
            return render_template_string(WELCOME_TEMPLATE)
        except sqlite3.IntegrityError:
            return render_template_string(REGISTER_TEMPLATE, error="این نام کاربری قبلاً استفاده شده.", cities=CITIES)
    
    return render_template_string(REGISTER_TEMPLATE, cities=CITIES)

# صفحه ورود
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        if user:
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
        else:
            return render_template_string(LOGIN_TEMPLATE, error="نام کاربری یا رمز اشتباه است.")
    return render_template_string(LOGIN_TEMPLATE)

# داشبورد
@app.route('/')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template_string(DASHBOARD_TEMPLATE)

# پروفایل
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    return render_template_string(PROFILE_TEMPLATE, user=user)

# ویرایش پروفایل
@app.route('/edit_profile', methods=['POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    db.execute('''
        UPDATE users SET name=?, age=?, gender=?, bio=?, city=?, password=?
        WHERE id=?
    ''', (
        request.form.get('name'),
        request.form.get('age'),
        request.form.get('gender'),
        request.form.get('bio'),
        request.form.get('city'),
        request.form.get('password'),
        session['user_id']
    ))
    db.commit()
    return redirect(url_for('profile'))

# خانه - لیست پروفایل‌ها
@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    filters = request.args.getlist('filter')
    query = 'SELECT * FROM users WHERE id != ?'
    params = [session['user_id']]
    if 'هم‌سن' in filters:
        query += ' AND age = ?'
        params.append(user['age'])
    if 'هم‌جنسیت' in filters:
        query += ' AND gender = ?'
        params.append(user['gender'])
    if 'ناهم‌جنسیت' in filters:
        opposite = 'دختر' if user['gender'] == 'پسر' else 'پسر'
        query += ' AND gender = ?'
        params.append(opposite)
    if 'هم‌شهر' in filters:
        query += ' AND city = ?'
        params.append(user['city'])
    profiles = db.execute(query, params).fetchall()
    return render_template_string(HOME_TEMPLATE, profiles=profiles)

# لایک
@app.route('/like/<int:user_id>')
def like(user_id):
    db = get_db()
    existing = db.execute('SELECT * FROM likes WHERE liker_id = ? AND liked_id = ?', (session['user_id'], user_id)).fetchone()
    if existing:
        db.execute('DELETE FROM likes WHERE id = ?', (existing['id'],))
        db.execute('DELETE FROM notifications WHERE user_id = ? AND related_id = ? AND type = "like"', (user_id, session['user_id']))
    else:
        db.execute('INSERT INTO likes (liker_id, liked_id) VALUES (?, ?)', (session['user_id'], user_id))
        db.execute('INSERT INTO notifications (user_id, message, type, related_id) VALUES (?, ?, ?, ?)',
                   (user_id, f"کاربر شما را لایک کرد", "like", session['user_id']))
    db.commit()
    return jsonify(success=True)

# اعلان‌ها
@app.route('/notifications')
def notifications():
    db = get_db()
    notifs = db.execute('SELECT * FROM notifications WHERE user_id = ? ORDER BY id DESC', (session['user_id'],)).fetchall()
    db.execute('UPDATE notifications SET seen = 1 WHERE user_id = ?', (session['user_id'],))
    db.commit()
    return render_template_string(NOTIFICATIONS_TEMPLATE, notifications=notifs)

# چت
@app.route('/chat')
def chat_list():
    db = get_db()
    chats = db.execute('''
        SELECT c.id, u.username, u.name, u.profile_pic,
               (SELECT message FROM messages WHERE chat_id = c.id ORDER BY id DESC LIMIT 1) AS last_message
        FROM chats c
        JOIN users u ON (u.id = c.user1 OR u.id = c.user2) AND u.id != ?
        WHERE c.user1 = ? OR c.user2 = ?
    ''', (session['user_id'], session['user_id'], session['user_id'])).fetchall()
    return render_template_string(CHAT_LIST_TEMPLATE, chats=chats)

# چت خصوصی
@app.route('/chat/<int:chat_id>')
def chat_room(chat_id):
    db = get_db()
    chat = db.execute('SELECT * FROM chats WHERE id = ?', (chat_id,)).fetchone()
    if not chat or (chat['user1'] != session['user_id'] and chat['user2'] != session['user_id']):
        return "چت یافت نشد", 404
    messages = db.execute('SELECT * FROM messages WHERE chat_id = ? ORDER BY id', (chat_id,)).fetchall()
    other_user_id = chat['user1'] if chat['user2'] == session['user_id'] else chat['user2']
    other_user = db.execute('SELECT * FROM users WHERE id = ?', (other_user_id,)).fetchone()
    return render_template_string(CHAT_ROOM_TEMPLATE, chat_id=chat_id, messages=messages, other_user=other_user)

# ارسال پیام
@app.route('/send_message/<int:chat_id>', methods=['POST'])
def send_message(chat_id):
    message = request.form['message']
    db = get_db()
    db.execute('INSERT INTO messages (chat_id, sender_id, message, timestamp) VALUES (?, ?, ?, ?)',
               (chat_id, session['user_id'], message, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    db.commit()
    return '', 204

# جستجو
@app.route('/search')
def search():
    query = request.args.get('q', '')
    db = get_db()
    if query.startswith('@'):
        users = db.execute('SELECT * FROM users WHERE username LIKE ?', (f"{query[1:]}%",)).fetchall()
    else:
        users = db.execute('SELECT * FROM users WHERE name LIKE ?', (f"{query}%",)).fetchall()
    return render_template_string(SEARCH_TEMPLATE, users=users)

# خروج
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

# حذف چت
@app.route('/delete_chat/<int:chat_id>')
def delete_chat(chat_id):
    db = get_db()
    db.execute('DELETE FROM messages WHERE chat_id = ?', (chat_id,))
    db.execute('DELETE FROM chats WHERE id = ?', (chat_id,))
    db.commit()
    return redirect(url_for('chat_list'))

# حذف حساب
@app.route('/delete_account', methods=['POST'])
def delete_account():
    password = request.form['password']
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ? AND password = ?', (session['user_id'], password)).fetchone()
    if user:
        db.execute('DELETE FROM users WHERE id = ?', (session['user_id'],))
        db.commit()
        session.pop('user_id', None)
        return redirect(url_for('register'))
    return "رمز اشتباه است."

# متغیرهای کمکی
CITIES = [
    "شهرک صدرا", "شهرک گلستان", "معالی آباد", "شهرک کشن", "شهرک مهدیه",
    "شهرک زینبیه", "شهرک بعثت", "شهرک والفجر", "شهرک صنعتی عفیف آباد",
    "کوی امام رضا", "شهرک گویم", "شهرک بزین", "شهرک رحمت آباد", "شهرک خورشید",
    "شهرک سلامت", "شهرک فرهنگیان", "کوی زاگرس", "کوی پاسداران", "شهرک عرفان",
    "شهرک هنرستان"
]

# تمپلیت‌ها
REGISTER_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ثبت‌نام - گویمیکس</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #121212;
            color: #FFFFFF;
            margin: 0;
            padding: 20px;
            direction: rtl;
        }
        .container {
            max-width: 500px;
            margin: 0 auto;
            background: rgba(30, 30, 30, 0.8);
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 0 20px rgba(155, 93, 229, 0.3);
        }
        h1 {
            text-align: center;
            color: #00F5D4;
            margin-bottom: 30px;
            font-size: 24px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #E0E0E0;
        }
        input, select, textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #9B5DE5;
            border-radius: 8px;
            background: #1E1E1E;
            color: #FFFFFF;
            font-size: 16px;
            box-sizing: border-box;
        }
        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: #00F5D4;
            box-shadow: 0 0 10px rgba(0, 245, 212, 0.5);
        }
        .btn {
            background: linear-gradient(45deg, #9B5DE5, #00F5D4);
            color: #121212;
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            width: 100%;
            margin-top: 10px;
            box-shadow: 0 0 15px rgba(155, 93, 229, 0.5);
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(155, 93, 229, 0.7);
        }
        .error {
            color: #F15BB5;
            text-align: center;
            margin-bottom: 20px;
        }
        .login-link {
            text-align: center;
            margin-top: 20px;
            color: #E0E0E0;
        }
        .login-link a {
            color: #00F5D4;
            text-decoration: none;
        }
        .login-link a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>خوش آمدید به گویمیکس | GOYIMIX</h1>
        
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        
        <form method="POST">
            <div class="form-group">
                <label for="name">نام (اختیاری):</label>
                <input type="text" id="name" name="name">
            </div>
            
            <div class="form-group">
                <label for="username">نام کاربری *@:</label>
                <input type="text" id="username" name="username" required>
            </div>
            
            <div class="form-group">
                <label for="age">سن *:</label>
                <select id="age" name="age" required>
                    <option value="">انتخاب سن</option>
                    {% for i in range(12, 81) %}
                    <option value="{{ i }}">{{ i }} سال</option>
                    {% endfor %}
                </select>
            </div>
            
            <div class="form-group">
                <label for="gender">جنسیت *:</label>
                <select id="gender" name="gender" required>
                    <option value="">انتخاب جنسیت</option>
                    <option value="پسر">پسر</option>
                    <option value="دختر">دختر</option>
                    <option value="دیگر">دیگر</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="bio">بیو (اختیاری):</label>
                <textarea id="bio" name="bio" rows="3"></textarea>
            </div>
            
            <div class="form-group">
                <label for="city">شهر *:</label>
                <select id="city" name="city" required>
                    <option value="">انتخاب شهر</option>
                    {% for city in cities %}
                    <option value="{{ city }}">{{ city }}</option>
                    {% endfor %}
                </select>
            </div>
            
            <div class="form-group">
                <label for="password">رمز عبور *:</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <div class="form-group">
                <label for="confirm">تکرار رمز عبور *:</label>
                <input type="password" id="confirm" name="confirm" required>
            </div>
            
            <button type="submit" class="btn">ثبت‌نام</button>
        </form>
        
        <div class="login-link">
            <p>حساب دارید؟ <a href="/login">وارد شوید</a></p>
        </div>
    </div>
</body>
</html>
'''

LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ورود - گویمیکس</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #121212;
            color: #FFFFFF;
            margin: 0;
            padding: 20px;
            direction: rtl;
        }
        .container {
            max-width: 400px;
            margin: 0 auto;
            background: rgba(30, 30, 30, 0.8);
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 0 20px rgba(155, 93, 229, 0.3);
        }
        h1 {
            text-align: center;
            color: #00F5D4;
            margin-bottom: 30px;
            font-size: 24px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #E0E0E0;
        }
        input {
            width: 100%;
            padding: 12px;
            border: 2px solid #9B5DE5;
            border-radius: 8px;
            background: #1E1E1E;
            color: #FFFFFF;
            font-size: 16px;
            box-sizing: border-box;
        }
        input:focus {
            outline: none;
            border-color: #00F5D4;
            box-shadow: 0 0 10px rgba(0, 245, 212, 0.5);
        }
        .btn {
            background: linear-gradient(45deg, #9B5DE5, #00F5D4);
            color: #121212;
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            width: 100%;
            margin-top: 10px;
            box-shadow: 0 0 15px rgba(155, 93, 229, 0.5);
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(155, 93, 229, 0.7);
        }
        .error {
            color: #F15BB5;
            text-align: center;
            margin-bottom: 20px;
        }
        .register-link {
            text-align: center;
            margin-top: 20px;
            color: #E0E0E0;
        }
        .register-link a {
            color: #00F5D4;
            text-decoration: none;
        }
        .register-link a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>دوباره خوش آمدید</h1>
        
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        
        <form method="POST">
            <div class="form-group">
                <label for="username">نام کاربری یا نام:</label>
                <input type="text" id="username" name="username" required>
            </div>
            
            <div class="form-group">
                <label for="password">رمز عبور:</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <button type="submit" class="btn">ورود</button>
        </form>
        
        <div class="register-link">
            <p>اگر حسابی ندارید؟ <a href="/register">ثبت‌نام کنید</a></p>
        </div>
    </div>
</body>
</html>
'''

DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>داشبورد - گویمیکس</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #121212;
            color: #FFFFFF;
            margin: 0;
            padding: 0;
            direction: rtl;
        }
        .header {
            background: rgba(30, 30, 30, 0.9);
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
        }
        .logo {
            font-size: 20px;
            font-weight: bold;
            color: #00F5D4;
            text-shadow: 0 0 10px rgba(0, 245, 212, 0.5);
        }
        .notification {
            position: relative;
            font-size: 24px;
            cursor: pointer;
        }
        .notification-badge {
            position: absolute;
            top: -5px;
            right: -5px;
            background: #F15BB5;
            color: white;
            border-radius: 50%;
            width: 18px;
            height: 18px;
            font-size: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .bottom-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(30, 30, 30, 0.95);
            display: flex;
            justify-content: space-around;
            padding: 10px 0;
            border-top: 1px solid #333;
        }
        .nav-item {
            text-align: center;
            color: #E0E0E0;
            text-decoration: none;
            font-size: 12px;
        }
        .nav-item.active {
            color: #00F5D4;
            text-shadow: 0 0 5px rgba(0, 245, 212, 0.5);
        }
        .nav-icon {
            font-size: 24px;
            display: block;
            margin-bottom: 5px;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">GOYIMIX | گویمیکس</div>
        <div class="notification">
            🔔
            <div class="notification-badge">🔴</div>
        </div>
    </div>
    
    <div style="padding: 20px; text-align: center;">
        <h2>به گویمیکس خوش آمدید!</h2>
        <p>از منوی پایین برای حرکت استفاده کنید</p>
    </div>
    
    <div class="bottom-nav">
        <a href="/profile" class="nav-item">
            <span class="nav-icon">👤</span>
            <span>پروفایل</span>
        </a>
        <a href="/home" class="nav-item active">
            <span class="nav-icon">🏠</span>
            <span>خانه</span>
        </a>
        <a href="/search" class="nav-item">
            <span class="nav-icon">🔍</span>
            <span>جستجو</span>
        </a>
        <a href="/chat" class="nav-item">
            <span class="nav-icon">💬</span>
            <span>چت</span>
        </a>
    </div>
</body>
</html>
'''

PROFILE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>پروفایل - گویمیکس</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #121212;
            color: #FFFFFF;
            margin: 0;
            padding: 0;
            direction: rtl;
        }
        .header {
            background: rgba(30, 30, 30, 0.9);
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
        }
        .logo {
            font-size: 20px;
            font-weight: bold;
            color: #00F5D4;
            text-shadow: 0 0 10px rgba(0, 245, 212, 0.5);
        }
        .container {
            padding: 20px;
            max-width: 600px;
            margin: 0 auto;
        }
        .profile-header {
            text-align: center;
            margin-bottom: 30px;
        }
        .profile-pic {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            background: #333;
            margin: 0 auto 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 48px;
            border: 3px solid #9B5DE5;
        }
        .profile-info {
            background: rgba(30, 30, 30, 0.8);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
        }
        .info-item {
            margin-bottom: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .info-label {
            color: #E0E0E0;
            font-weight: bold;
        }
        .info-value {
            color: #00F5D4;
        }
        .edit-btn {
            background: #9B5DE5;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 5px;
            cursor: pointer;
        }
        .switch {
            position: relative;
            display: inline-block;
            width: 60px;
            height: 34px;
        }
        .switch input {
            opacity: 0;
            width: 0;
            height: 0;
        }
        .slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #ccc;
            transition: .4s;
            border-radius: 34px;
        }
        .slider:before {
            position: absolute;
            content: "";
            height: 26px;
            width: 26px;
            left: 4px;
            bottom: 4px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }
        input:checked + .slider {
            background-color: #00F5D4;
        }
        input:checked + .slider:before {
            transform: translateX(26px);
        }
        .btn {
            background: linear-gradient(45deg, #9B5DE5, #00F5D4);
            color: #121212;
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            width: 100%;
            margin-top: 10px;
            box-shadow: 0 0 15px rgba(155, 93, 229, 0.5);
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(155, 93, 229, 0.7);
        }
        .danger-btn {
            background: linear-gradient(45deg, #F15BB5, #9B5DE5);
        }
        .bottom-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(30, 30, 30, 0.95);
            display: flex;
            justify-content: space-around;
            padding: 10px 0;
            border-top: 1px solid #333;
        }
        .nav-item {
            text-align: center;
            color: #E0E0E0;
            text-decoration: none;
            font-size: 12px;
        }
        .nav-item.active {
            color: #00F5D4;
            text-shadow: 0 0 5px rgba(0, 245, 212, 0.5);
        }
        .nav-icon {
            font-size: 24px;
            display: block;
            margin-bottom: 5px;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">GOYIMIX | گویمیکس</div>
        <div class="notification">🔔</div>
    </div>
    
    <div class="container">
        <div class="profile-header">
            <div class="profile-pic">👤</div>
            <h2>{{ user.name or 'بدون نام' }}</h2>
            <p>@{{ user.username }}</p>
        </div>
        
        <div class="profile-info">
            <div class="info-item">
                <span class="info-label">سن:</span>
                <span class="info-value">{{ user.age }} سال</span>
            </div>
            <div class="info-item">
                <span class="info-label">جنسیت:</span>
                <span class="info-value">{{ user.gender }}</span>
            </div>
            <div class="info-item">
                <span class="info-label">بیو:</span>
                <span class="info-value">{{ user.bio or 'بدون بیو' }}</span>
            </div>
            <div class="info-item">
                <span class="info-label">شهر:</span>
                <span class="info-value">{{ user.city }}</span>
            </div>
            <div class="info-item">
                <span class="info-label">رمز عبور:</span>
                <span class="info-value">●●●●●●●●</span>
            </div>
        </div>
        
        <form method="POST" action="/edit_profile">
            <div class="profile-info">
                <div class="info-item">
                    <span class="info-label">نام:</span>
                    <input type="text" name="name" value="{{ user.name or '' }}" style="background: #1E1E1E; color: white; border: 1px solid #9B5DE5; padding: 5px; border-radius: 5px;">
                </div>
                <div class="info-item">
                    <span class="info-label">سن:</span>
                    <input type="number" name="age" value="{{ user.age }}" style="background: #1E1E1E; color: white; border: 1px solid #9B5DE5; padding: 5px; border-radius: 5px;">
                </div>
                <div class="info-item">
                    <span class="info-label">جنسیت:</span>
                    <select name="gender" style="background: #1E1E1E; color: white; border: 1px solid #9B5DE5; padding: 5px; border-radius: 5px;">
                        <option value="پسر" {% if user.gender == 'پسر' %}selected{% endif %}>پسر</option>
                        <option value="دختر" {% if user.gender == 'دختر' %}selected{% endif %}>دختر</option>
                        <option value="دیگر" {% if user.gender == 'دیگر' %}selected{% endif %}>دیگر</option>
                    </select>
                </div>
                <div class="info-item">
                    <span class="info-label">بیو:</span>
                    <textarea name="bio" style="background: #1E1E1E; color: white; border: 1px solid #9B5DE5; padding: 5px; border-radius: 5px;">{{ user.bio or '' }}</textarea>
                </div>
                <div class="info-item">
                    <span class="info-label">شهر:</span>
                    <select name="city" style="background: #1E1E1E; color: white; border: 1px solid #9B5DE5; padding: 5px; border-radius: 5px;">
                        {% for city in [
                            "شهرک صدرا", "شهرک گلستان", "معالی آباد", "شهرک کشن", "شهرک مهدیه",
                            "شهرک زینبیه", "شهرک بعثت", "شهرک والفجر", "شهرک صنعتی عفیف آباد",
                            "کوی امام رضا", "شهرک گویم", "شهرک بزین", "شهرک رحمت آباد", "شهرک خورشید",
                            "شهرک سلامت", "شهرک فرهنگیان", "کوی زاگرس", "کوی پاسداران", "شهرک عرفان",
                            "شهرک هنرستان"
                        ] %}
                        <option value="{{ city }}" {% if user.city == city %}selected{% endif %}>{{ city }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="info-item">
                    <span class="info-label">رمز عبور:</span>
                    <input type="password" name="password" value="{{ user.password }}" style="background: #1E1E1E; color: white; border: 1px solid #9B5DE5; padding: 5px; border-radius: 5px;">
                </div>
            </div>
            <button type="submit" class="btn">ذخیره تغییرات</button>
        </form>
        
        <div style="margin: 20px 0;">
            <label class="info-label">نمایش پروفایل در خانه:</label>
            <label class="switch">
                <input type="checkbox" {% if user.visible == 1 %}checked{% endif %}>
                <span class="slider"></span>
            </label>
        </div>
        
        <a href="/logout" class="btn">خروج از حساب</a>
        <button class="btn danger-btn" onclick="confirmDelete()">حذف حساب</button>
    </div>
    
    <div class="bottom-nav">
        <a href="/profile" class="nav-item active">
            <span class="nav-icon">👤</span>
            <span>پروفایل</span>
        </a>
        <a href="/home" class="nav-item">
            <span class="nav-icon">🏠</span>
            <span>خانه</span>
        </a>
        <a href="/search" class="nav-item">
            <span class="nav-icon">🔍</span>
            <span>جستجو</span>
        </a>
        <a href="/chat" class="nav-item">
            <span class="nav-icon">💬</span>
            <span>چت</span>
        </a>
    </div>
    
    <script>
        function confirmDelete() {
            if(confirm("آیا مطمئنید؟")) {
                const password = prompt("رمز عبور خود را وارد کنید:");
                if(password) {
                    fetch('/delete_account', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                        },
                        body: 'password=' + encodeURIComponent(password)
                    }).then(response => {
                        if(response.ok) {
                            window.location.href = '/register';
                        } else {
                            alert('رمز اشتباه است.');
                        }
                    });
                }
            }
        }
    </script>
</body>
</html>
'''

HOME_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>خانه - گویمیکس</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #121212;
            color: #FFFFFF;
            margin: 0;
            padding: 0;
            direction: rtl;
        }
        .header {
            background: rgba(30, 30, 30, 0.9);
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
        }
        .logo {
            font-size: 20px;
            font-weight: bold;
            color: #00F5D4;
            text-shadow: 0 0 10px rgba(0, 245, 212, 0.5);
        }
        .filters {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            padding: 15px;
            background: rgba(30, 30, 30, 0.8);
            margin-bottom: 20px;
        }
        .filter-btn {
            background: #333;
            color: #E0E0E0;
            border: none;
            padding: 8px 15px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 14px;
        }
        .filter-btn.active {
            background: #00F5D4;
            color: #121212;
            box-shadow: 0 0 10px rgba(0, 245, 212, 0.5);
        }
        .profile-card {
            background: rgba(30, 30, 30, 0.8);
            margin: 15px;
            padding: 20px;
            border-radius: 15px;
            display: flex;
            align-items: center;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
        }
        .profile-pic {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: #333;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            margin-left: 15px;
            border: 2px solid #9B5DE5;
        }
        .profile-info {
            flex: 1;
        }
        .profile-name {
            font-weight: bold;
            color: #00F5D4;
            margin-bottom: 5px;
        }
        .profile-username {
            color: #9B5DE5;
            font-size: 14px;
            margin-bottom: 5px;
        }
        .profile-details {
            color: #E0E0E0;
            font-size: 14px;
        }
        .profile-actions {
            display: flex;
            gap: 10px;
        }
        .action-btn {
            background: rgba(155, 93, 229, 0.3);
            border: none;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            color: white;
            font-size: 18px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .action-btn.like.liked {
            background: #F15BB5;
            box-shadow: 0 0 10px rgba(241, 91, 181, 0.5);
        }
        .bottom-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(30, 30, 30, 0.95);
            display: flex;
            justify-content: space-around;
            padding: 10px 0;
            border-top: 1px solid #333;
        }
        .nav-item {
            text-align: center;
            color: #E0E0E0;
            text-decoration: none;
            font-size: 12px;
        }
        .nav-item.active {
            color: #00F5D4;
            text-shadow: 0 0 5px rgba(0, 245, 212, 0.5);
        }
        .nav-icon {
            font-size: 24px;
            display: block;
            margin-bottom: 5px;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">GOYIMIX | گویمیکس</div>
        <div class="notification">🔔</div>
    </div>
    
    <div class="filters">
        <button class="filter-btn" onclick="toggleFilter('هم‌سن')">هم‌سن</button>
        <button class="filter-btn" onclick="toggleFilter('هم‌جنسیت')">هم‌جنسیت</button>
        <button class="filter-btn" onclick="toggleFilter('ناهم‌جنسیت')">ناهم‌جنسیت</button>
        <button class="filter-btn" onclick="toggleFilter('هم‌شهر')">هم‌شهر</button>
    </div>
    
    <div id="profiles-container">
        {% for profile in profiles %}
        <div class="profile-card">
            <div class="profile-pic">👤</div>
            <div class="profile-info">
                <div class="profile-name">{{ profile.name or 'بدون نام' }}</div>
                <div class="profile-username">@{{ profile.username }}</div>
                <div class="profile-details">{{ profile.age }} سال | {{ profile.gender }} | {{ profile.city }}</div>
                <div class="profile-details">{{ profile.bio or 'بدون بیو' }}</div>
            </div>
            <div class="profile-actions">
                <button class="action-btn like" onclick="toggleLike({{ profile.id }})">❤️</button>
                <button class="action-btn" onclick="startChat({{ profile.id }})">💬</button>
            </div>
        </div>
        {% endfor %}
    </div>
    
    <div class="bottom-nav">
        <a href="/profile" class="nav-item">
            <span class="nav-icon">👤</span>
            <span>پروفایل</span>
        </a>
        <a href="/home" class="nav-item active">
            <span class="nav-icon">🏠</span>
            <span>خانه</span>
        </a>
        <a href="/search" class="nav-item">
            <span class="nav-icon">🔍</span>
            <span>جستجو</span>
        </a>
        <a href="/chat" class="nav-item">
            <span class="nav-icon">💬</span>
            <span>چت</span>
        </a>
    </div>
    
    <script>
        function toggleFilter(filter) {
            const btn = event.target;
            btn.classList.toggle('active');
            updateFilters();
        }
        
        function updateFilters() {
            const activeFilters = [];
            document.querySelectorAll('.filter-btn.active').forEach(btn => {
                activeFilters.push(btn.textContent);
            });
            
            const url = new URL(window.location);
            url.searchParams.delete('filter');
            activeFilters.forEach(filter => {
                url.searchParams.append('filter', filter);
            });
            window.location.href = url.toString();
        }
        
        function toggleLike(userId) {
            const btn = event.target;
            fetch(`/like/${userId}`)
                .then(response => response.json())
                .then(data => {
                    if(data.success) {
                        btn.classList.toggle('liked');
                    }
                });
        }
        
        function startChat(userId) {
            // در اینجا می‌توانید منطق شروع چت را اضافه کنید
            alert('شروع چت با کاربر ' + userId);
        }
    </script>
</body>
</html>
'''

NOTIFICATIONS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>اعلان‌ها - گویمیکس</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #121212;
            color: #FFFFFF;
            margin: 0;
            padding: 0;
            direction: rtl;
        }
        .header {
            background: rgba(30, 30, 30, 0.9);
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
        }
        .logo {
            font-size: 20px;
            font-weight: bold;
            color: #00F5D4;
            text-shadow: 0 0 10px rgba(0, 245, 212, 0.5);
        }
        .container {
            padding: 20px;
        }
        .notification-card {
            background: rgba(30, 30, 30, 0.8);
            margin-bottom: 15px;
            padding: 15px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
        }
        .notification-icon {
            font-size: 24px;
            margin-left: 15px;
        }
        .notification-content {
            flex: 1;
        }
        .notification-message {
            margin-bottom: 5px;
        }
        .notification-time {
            color: #999;
            font-size: 12px;
        }
        .notification-actions {
            display: flex;
            gap: 10px;
        }
        .action-btn {
            background: rgba(155, 93, 229, 0.3);
            border: none;
            padding: 5px 10px;
            border-radius: 5px;
            color: white;
            cursor: pointer;
            font-size: 14px;
        }
        .action-btn.accept {
            background: #00F5D4;
        }
        .action-btn.reject {
            background: #F15BB5;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">اعلان‌ها</div>
        <div class="notification">🔔</div>
    </div>
    
    <div class="container">
        {% for notif in notifications %}
        <div class="notification-card">
            <div class="notification-icon">
                {% if notif.type == 'like' %}❤️{% elif notif.type == 'chat' %}💬{% else %}✉️{% endif %}
            </div>
            <div class="notification-content">
                <div class="notification-message">{{ notif.message }}</div>
                <div class="notification-time">{{ notif.timestamp or 'اکنون' }}</div>
            </div>
            <div class="notification-actions">
                <button class="action-btn accept">✅</button>
                <button class="action-btn reject">❌</button>
                <button class="action-btn" style="background: #9B5DE5;">🚫</button>
            </div>
        </div>
        {% endfor %}
    </div>
</body>
</html>
'''

CHAT_LIST_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>چت‌ها - گویمیکس</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #121212;
            color: #FFFFFF;
            margin: 0;
            padding: 0;
            direction: rtl;
        }
        .header {
            background: rgba(30, 30, 30, 0.9);
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
        }
        .logo {
            font-size: 20px;
            font-weight: bold;
            color: #00F5D4;
            text-shadow: 0 0 10px rgba(0, 245, 212, 0.5);
        }
        .container {
            padding: 20px;
        }
        .chat-card {
            background: rgba(30, 30, 30, 0.8);
            margin-bottom: 15px;
            padding: 15px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
            cursor: pointer;
        }
        .chat-pic {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: #333;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            margin-left: 15px;
            border: 2px solid #9B5DE5;
        }
        .chat-info {
            flex: 1;
        }
        .chat-name {
            font-weight: bold;
            color: #00F5D4;
            margin-bottom: 5px;
        }
        .chat-username {
            color: #9B5DE5;
            font-size: 14px;
            margin-bottom: 5px;
        }
        .chat-last-message {
            color: #E0E0E0;
            font-size: 14px;
        }
        .chat-time {
            color: #999;
            font-size: 12px;
        }
        .delete-btn {
            background: #F15BB5;
            border: none;
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            cursor: pointer;
            margin-right: 10px;
        }
        .bottom-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(30, 30, 30, 0.95);
            display: flex;
            justify-content: space-around;
            padding: 10px 0;
            border-top: 1px solid #333;
        }
        .nav-item {
            text-align: center;
            color: #E0E0E0;
            text-decoration: none;
            font-size: 12px;
        }
        .nav-item.active {
            color: #00F5D4;
            text-shadow: 0 0 5px rgba(0, 245, 212, 0.5);
        }
        .nav-icon {
            font-size: 24px;
            display: block;
            margin-bottom: 5px;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">چت‌ها</div>
        <div class="notification">🔔</div>
    </div>
    
    <div class="container">
        {% for chat in chats %}
        <div class="chat-card">
            <div class="chat-pic">👤</div>
            <div class="chat-info" onclick="window.location.href='/chat/{{ chat.id }}'">
                <div class="chat-name">{{ chat.name or 'بدون نام' }}</div>
                <div class="chat-username">@{{ chat.username }}</div>
                <div class="chat-last-message">{{ chat.last_message or 'بدون پیام' }}</div>
            </div>
            <button class="delete-btn" onclick="deleteChat({{ chat.id }})">حذف</button>
        </div>
        {% endfor %}
    </div>
    
    <div class="bottom-nav">
        <a href="/profile" class="nav-item">
            <span class="nav-icon">👤</span>
            <span>پروفایل</span>
        </a>
        <a href="/home" class="nav-item">
            <span class="nav-icon">🏠</span>
            <span>خانه</span>
        </a>
        <a href="/search" class="nav-item">
            <span class="nav-icon">🔍</span>
            <span>جستجو</span>
        </a>
        <a href="/chat" class="nav-item active">
            <span class="nav-icon">💬</span>
            <span>چت</span>
        </a>
    </div>
    
    <script>
        function deleteChat(chatId) {
            if(confirm('آیا مطمئنید که می‌خواهید این چت را حذف کنید؟')) {
                window.location.href = `/delete_chat/${chatId}`;
            }
        }
    </script>
</body>
</html>
'''

CHAT_ROOM_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>چت - گویمیکس</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #121212;
            color: #FFFFFF;
            margin: 0;
            padding: 0;
            direction: rtl;
        }
        .header {
            background: rgba(30, 30, 30, 0.9);
            padding: 15px 20px;
            display: flex;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
        }
        .back-btn {
            background: none;
            border: none;
            color: #00F5D4;
            font-size: 24px;
            cursor: pointer;
            margin-left: 15px;
        }
        .chat-pic {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #333;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            margin-left: 15px;
            border: 2px solid #9B5DE5;
        }
        .chat-info {
            flex: 1;
        }
        .chat-name {
            font-weight: bold;
            color: #00F5D4;
        }
        .chat-username {
            color: #9B5DE5;
            font-size: 14px;
        }
        .messages-container {
            padding: 20px;
            height: calc(100vh - 150px);
            overflow-y: auto;
        }
        .message {
            margin-bottom: 15px;
            max-width: 70%;
            padding: 10px 15px;
            border-radius: 15px;
            word-wrap: break-word;
        }
        .received {
            background: rgba(50, 50, 50, 0.8);
            align-self: flex-start;
            margin-left: auto;
        }
        .sent {
            background: rgba(155, 93, 229, 0.3);
            align-self: flex-end;
            margin-right: auto;
        }
        .input-container {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(30, 30, 30, 0.95);
            padding: 15px;
            display: flex;
            gap: 10px;
        }
        .message-input {
            flex: 1;
            padding: 12px;
            border: 2px solid #9B5DE5;
            border-radius: 25px;
            background: #1E1E1E;
            color: #FFFFFF;
            font-size: 16px;
            outline: none;
        }
        .send-btn {
            background: linear-gradient(45deg, #9B5DE5, #00F5D4);
            color: #121212;
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            font-size: 20px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 0 15px rgba(155, 93, 229, 0.5);
        }
        .attachment-btn {
            background: rgba(155, 93, 229, 0.3);
            color: white;
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            font-size: 20px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }
    </style>
</head>
<body>
    <div class="header">
        <button class="back-btn" onclick="window.location.href='/chat'">←</button>
        <div class="chat-pic">👤</div>
        <div class="chat-info">
            <div class="chat-name">{{ other_user.name or 'بدون نام' }}</div>
            <div class="chat-username">@{{ other_user.username }}</div>
        </div>
    </div>
    
    <div class="messages-container" id="messages">
        {% for message in messages %}
        <div class="message {% if message.sender_id == session.user_id %}sent{% else %}received{% endif %}">
            {{ message.message }}
        </div>
        {% endfor %}
    </div>
    
    <div class="input-container">
        <button class="attachment-btn">📷</button>
        <input type="text" class="message-input" id="messageInput" placeholder="پیام خود را بنویسید...">
        <button class="send-btn" onclick="sendMessage()">➤</button>
    </div>
    
    <script>
        function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            if(message) {
                fetch('/send_message/{{ chat_id }}', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: 'message=' + encodeURIComponent(message)
                }).then(() => {
                    const messagesContainer = document.getElementById('messages');
                    const messageDiv = document.createElement('div');
                    messageDiv.className = 'message sent';
                    messageDiv.textContent = message;
                    messagesContainer.appendChild(messageDiv);
                    input.value = '';
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                });
            }
        }
        
        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if(e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>
'''

SEARCH_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>جستجو - گویمیکس</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #121212;
            color: #FFFFFF;
            margin: 0;
            padding: 0;
            direction: rtl;
        }
        .header {
            background: rgba(30, 30, 30, 0.9);
            padding: 15px 20px;
            display: flex;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
        }
        .search-container {
            flex: 1;
            display: flex;
        }
        .search-input {
            flex: 1;
            padding: 12px;
            border: 2px solid #9B5DE5;
            border-radius: 25px 0 0 25px;
            background: #1E1E1E;
            color: #FFFFFF;
            font-size: 16px;
            outline: none;
        }
        .search-btn {
            background: linear-gradient(45deg, #9B5DE5, #00F5D4);
            color: #121212;
            border: none;
            border-radius: 0 25px 25px 0;
            padding: 0 20px;
            font-size: 18px;
            cursor: pointer;
            box-shadow: 0 0 15px rgba(155, 93, 229, 0.5);
        }
        .results-container {
            padding: 20px;
        }
        .profile-card {
            background: rgba(30, 30, 30, 0.8);
            margin-bottom: 15px;
            padding: 15px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
        }
        .profile-pic {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: #333;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            margin-left: 15px;
            border: 2px solid #9B5DE5;
        }
        .profile-info {
            flex: 1;
        }
        .profile-name {
            font-weight: bold;
            color: #00F5D4;
            margin-bottom: 5px;
        }
        .profile-username {
            color: #9B5DE5;
            font-size: 14px;
        }
        .bottom-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(30, 30, 30, 0.95);
            display: flex;
            justify-content: space-around;
            padding: 10px 0;
            border-top: 1px solid #333;
        }
        .nav-item {
            text-align: center;
            color: #E0E0E0;
            text-decoration: none;
            font-size: 12px;
        }
        .nav-item.active {
            color: #00F5D4;
            text-shadow: 0 0 5px rgba(0, 245, 212, 0.5);
        }
        .nav-icon {
            font-size: 24px;
            display: block;
            margin-bottom: 5px;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="search-container">
            <input type="text" class="search-input" id="searchInput" placeholder="جستجو با @نام_کاربری یا نام">
            <button class="search-btn" onclick="search()">🔍</button>
        </div>
    </div>
    
    <div class="results-container" id="results">
        {% for user in users %}
        <div class="profile-card">
            <div class="profile-pic">👤</div>
            <div class="profile-info">
                <div class="profile-name">{{ user.name or 'بدون نام' }}</div>
                <div class="profile-username">@{{ user.username }}</div>
            </div>
        </div>
        {% endfor %}
    </div>
    
    <div class="bottom-nav">
        <a href="/profile" class="nav-item">
            <span class="nav-icon">👤</span>
            <span>پروفایل</span>
        </a>
        <a href="/home" class="nav-item">
            <span class="nav-icon">🏠</span>
            <span>خانه</span>
        </a>
        <a href="/search" class="nav-item active">
            <span class="nav-icon">🔍</span>
            <span>جستجو</span>
        </a>
        <a href="/chat" class="nav-item">
            <span class="nav-icon">💬</span>
            <span>چت</span>
        </a>
    </div>
    
    <script>
        function search() {
            const query = document.getElementById('searchInput').value;
            if(query) {
                window.location.href = `/search?q=${encodeURIComponent(query)}`;
            }
        }
        
        document.getElementById('searchInput').addEventListener('keypress', function(e) {
            if(e.key === 'Enter') {
                search();
            }
        });
    </script>
</body>
</html>
'''

WELCOME_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>خوش آمدید - گویمیکس</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #121212;
            color: #FFFFFF;
            margin: 0;
            padding: 0;
            direction: rtl;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
        }
        .container {
            text-align: center;
            padding: 30px;
            background: rgba(30, 30, 30, 0.8);
            border-radius: 15px;
            box-shadow: 0 0 30px rgba(155, 93, 229, 0.5);
        }
        h1 {
            color: #00F5D4;
            font-size: 36px;
            margin-bottom: 20px;
            text-shadow: 0 0 20px rgba(0, 245, 212, 0.7);
        }
        .emoji {
            font-size: 60px;
            margin-bottom: 20px;
        }
        .btn {
            background: linear-gradient(45deg, #9B5DE5, #00F5D4);
            color: #121212;
            padding: 15px 30px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 18px;
            font-weight: bold;
            text-decoration: none;
            display: inline-block;
            box-shadow: 0 0 20px rgba(155, 93, 229, 0.7);
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 25px rgba(155, 93, 229, 0.9);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="emoji">🎉</div>
        <h1>خوش آمدید به گویمیکس</h1>
        <a href="/login" class="btn">ورود به حساب</a>
    </div>
</body>
</html>
'''

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)