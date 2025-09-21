from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify, flash
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import json
import time
from datetime import datetime

app = Flask(__name__)
app.secret_key = "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2"
socketio = SocketIO(app)

# مسیر دیتابیس
DB_PATH = "goyomix.db"

# ثابت‌ها
CITIES = [
    "شهرک صدرا", "شهرک گلستان", "معالی آباد", "شهرک کشن", "شهرک مهدیه",
    "شهرک زینبیه", "شهرک بعثت", "شهرک والفجر", "شهرک صنعتی عفیف آباد",
    "کوی امام رضا", "شهرک گویم", "شهرک بزین", "شهرک رحمت آباد", "شهرک خورشید",
    "شهرک سلامت", "شهرک فرهنگیان", "کوی زاگرس", "کوی پاسداران", "شهرک عرفان",
    "شهرک هنرستان"
]

# ===================== ایجاد دیتابیس =====================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            name TEXT,
            age INTEGER,
            gender TEXT,
            bio TEXT,
            interests TEXT,
            city TEXT,
            password_hash TEXT NOT NULL,
            avatar TEXT,
            visible INTEGER DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_user INTEGER,
            to_user INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user1 INTEGER,
            user2 INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            sender_id INTEGER,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT,
            content TEXT,
            from_user INTEGER,
            status TEXT DEFAULT 'unread',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

# ===================== توابع کمکی =====================
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_user_by_id(user_id):
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return user

def get_user_by_username(username):
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return user

def get_notifications(user_id):
    conn = get_db()
    notifications = conn.execute('''
        SELECT n.*, u.username as from_username 
        FROM notifications n 
        JOIN users u ON n.from_user = u.id 
        WHERE n.user_id = ? 
        ORDER BY n.created_at DESC
    ''', (user_id,)).fetchall()
    conn.close()
    return notifications

def create_notification(user_id, notif_type, content, from_user):
    conn = get_db()
    conn.execute('''
        INSERT INTO notifications (user_id, type, content, from_user) 
        VALUES (?, ?, ?, ?)
    ''', (user_id, notif_type, content, from_user))
    conn.commit()
    conn.close()

def get_chat_id(user1_id, user2_id):
    conn = get_db()
    chat = conn.execute('''
        SELECT id FROM chats 
        WHERE (user1 = ? AND user2 = ?) OR (user1 = ? AND user2 = ?)
    ''', (user1_id, user2_id, user2_id, user1_id)).fetchone()
    
    if chat:
        return chat['id']
    
    conn.execute('''
        INSERT INTO chats (user1, user2) VALUES (?, ?)
    ''', (user1_id, user2_id))
    conn.commit()
    
    chat_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    conn.close()
    return chat_id

def get_messages(chat_id):
    conn = get_db()
    messages = conn.execute('''
        SELECT m.*, u.username as sender_username 
        FROM messages m 
        JOIN users u ON m.sender_id = u.id 
        WHERE m.chat_id = ? 
        ORDER BY m.timestamp ASC
    ''', (chat_id,)).fetchall()
    conn.close()
    return messages

def get_chats(user_id):
    conn = get_db()
    chats = conn.execute('''
        SELECT c.*, u1.username as user1_username, u2.username as user2_username,
               u1.avatar as user1_avatar, u2.avatar as user2_avatar
        FROM chats c
        JOIN users u1 ON c.user1 = u1.id
        JOIN users u2 ON c.user2 = u2.id
        WHERE c.user1 = ? OR c.user2 = ?
        ORDER BY c.created_at DESC
    ''', (user_id, user_id)).fetchall()
    conn.close()
    return chats

def get_profiles_for_home(user_id, filters=None):
    conn = get_db()
    user = get_user_by_id(user_id)
    
    query = '''
        SELECT * FROM users 
        WHERE id != ? AND visible = 1
    '''
    params = [user_id]
    
    if filters:
        if filters.get('age_range'):
            query += ' AND age BETWEEN ? AND ?'
            params.extend(filters['age_range'])
        
        if filters.get('gender'):
            query += ' AND gender = ?'
            params.append(filters['gender'])
        
        if filters.get('city'):
            query += ' AND city = ?'
            params.append(filters['city'])
    
    query += ' ORDER BY RANDOM() LIMIT 20'
    
    profiles = conn.execute(query, params).fetchall()
    conn.close()
    return profiles

# ===================== روت‌های اصلی =====================
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        name = request.form.get('name', '').strip()
        age = request.form.get('age')
        gender = request.form.get('gender')
        bio = request.form.get('bio', '').strip()
        interests = request.form.get('interests', '').strip()
        city = request.form.get('city')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # اعتبارسنجی
        if not username or not age or not gender or not city or not password:
            return render_template_string(SIGNUP_TEMPLATE, cities=CITIES, error="تمام فیلدهای اجباری را پر کنید")
        
        if password != confirm_password:
            return render_template_string(SIGNUP_TEMPLATE, cities=CITIES, error="رمز عبور و تکرار آن مطابقت ندارند")
        
        conn = get_db()
        try:
            password_hash = generate_password_hash(password)
            conn.execute('''
                INSERT INTO users (username, name, age, gender, bio, interests, city, password_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, name, int(age), gender, bio, interests, city, password_hash))
            conn.commit()
            return render_template_string(SUCCESS_TEMPLATE, message="ثبت‌نام با موفقیت انجام شد! وارد شوید")
        except sqlite3.IntegrityError:
            return render_template_string(SIGNUP_TEMPLATE, cities=CITIES, error="این نام کاربری قبلاً استفاده شده")
        finally:
            conn.close()
    
    return render_template_string(SIGNUP_TEMPLATE, cities=CITIES)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password')
        
        if not username or not password:
            return render_template_string(LOGIN_TEMPLATE, error="نام کاربری و رمز عبور را وارد کنید")
        
        user = get_user_by_username(username)
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
        else:
            return render_template_string(LOGIN_TEMPLATE, error="نام کاربری یا رمز اشتباه است")
    
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = get_user_by_id(session['user_id'])
    filters = session.get('filters', {})
    profiles = get_profiles_for_home(session['user_id'], filters)
    
    # بررسی اعلان‌های جدید
    conn = get_db()
    unread_count = conn.execute('''
        SELECT COUNT(*) FROM notifications 
        WHERE user_id = ? AND status = 'unread'
    ''', (session['user_id'],)).fetchone()[0]
    conn.close()
    
    return render_template_string(DASHBOARD_TEMPLATE, user=user, profiles=profiles, unread_count=unread_count)

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = get_user_by_id(session['user_id'])
    return render_template_string(PROFILE_TEMPLATE, user=user, CITIES=CITIES)

@app.route('/profile/edit', methods=['POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    name = request.form.get('name', '').strip()
    bio = request.form.get('bio', '').strip()
    interests = request.form.get('interests', '').strip()
    city = request.form.get('city')
    visible = request.form.get('visible') == 'on'
    
    conn = get_db()
    conn.execute('''
        UPDATE users 
        SET name = ?, bio = ?, interests = ?, city = ?, visible = ?
        WHERE id = ?
    ''', (name, bio, interests, city, 1 if visible else 0, session['user_id']))
    conn.commit()
    conn.close()
    
    return render_template_string(SUCCESS_TEMPLATE, message="پروفایل با موفقیت به‌روزرسانی شد")

@app.route('/profile/change_password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    user = get_user_by_id(session['user_id'])
    
    if not check_password_hash(user['password_hash'], current_password):
        return render_template_string(ERROR_TEMPLATE, message="رمز عبور فعلی اشتباه است")
    
    if new_password != confirm_password:
        return render_template_string(ERROR_TEMPLATE, message="رمز عبور جدید و تکرار آن مطابقت ندارند")
    
    conn = get_db()
    conn.execute('''
        UPDATE users 
        SET password_hash = ? 
        WHERE id = ?
    ''', (generate_password_hash(new_password), session['user_id']))
    conn.commit()
    conn.close()
    
    return render_template_string(SUCCESS_TEMPLATE, message="رمز عبور با موفقیت تغییر کرد")

@app.route('/profile/delete', methods=['POST'])
def delete_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    
    user = get_user_by_id(session['user_id'])
    
    if password != confirm_password:
        return render_template_string(ERROR_TEMPLATE, message="رمز عبور و تکرار آن مطابقت ندارند")
    
    if not check_password_hash(user['password_hash'], password):
        return render_template_string(ERROR_TEMPLATE, message="رمز عبور اشتباه است")
    
    conn = get_db()
    conn.execute('DELETE FROM users WHERE id = ?', (session['user_id'],))
    conn.execute('DELETE FROM likes WHERE from_user = ? OR to_user = ?', (session['user_id'], session['user_id']))
    conn.execute('DELETE FROM notifications WHERE user_id = ? OR from_user = ?', (session['user_id'], session['user_id']))
    conn.commit()
    conn.close()
    
    session.clear()
    return render_template_string(SUCCESS_TEMPLATE, message="حساب کاربری شما با موفقیت حذف شد")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/search')
def search():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    query = request.args.get('q', '').strip()
    results = []
    
    if query:
        conn = get_db()
        if query.startswith('@'):
            # جستجو بر اساس نام کاربری
            results = conn.execute('''
                SELECT * FROM users 
                WHERE username LIKE ? AND id != ?
                ORDER BY username
            ''', (f'%{query[1:]}%', session['user_id'])).fetchall()
        else:
            # جستجو بر اساس نام
            results = conn.execute('''
                SELECT * FROM users 
                WHERE name LIKE ? AND id != ?
                ORDER BY name
            ''', (f'%{query}%', session['user_id'])).fetchall()
        conn.close()
    
    return render_template_string(SEARCH_TEMPLATE, results=results, query=query)

@app.route('/chat')
def chat():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = get_user_by_id(session['user_id'])
    chats = get_chats(session['user_id'])
    
    return render_template_string(CHAT_TEMPLATE, user=user, chats=chats)

@app.route('/chat/<int:other_user_id>')
def chat_room(other_user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # بررسی وجود چت یا ایجاد آن
    chat_id = get_chat_id(session['user_id'], other_user_id)
    messages = get_messages(chat_id)
    
    # اطلاعات کاربر مقابل
    conn = get_db()
    other_user = conn.execute('SELECT * FROM users WHERE id = ?', (other_user_id,)).fetchone()
    conn.close()
    
    return render_template_string(CHAT_ROOM_TEMPLATE, 
                                chat_id=chat_id, 
                                other_user=other_user, 
                                messages=messages,
                                user=get_user_by_id(session['user_id']))

@app.route('/notifications')
def notifications():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    notifs = get_notifications(session['user_id'])
    
    # علامت‌گذاری اعلان‌ها به عنوان خوانده شده
    conn = get_db()
    conn.execute('''
        UPDATE notifications 
        SET status = 'read' 
        WHERE user_id = ?
    ''', (session['user_id'],))
    conn.commit()
    conn.close()
    
    return render_template_string(NOTIFICATIONS_TEMPLATE, notifications=notifs)

@app.route('/like/<int:to_user_id>', methods=['POST'])
def like_user(to_user_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    from_user_id = session['user_id']
    
    conn = get_db()
    
    # بررسی وجود لایک قبلی
    existing = conn.execute('''
        SELECT id FROM likes 
        WHERE from_user = ? AND to_user = ?
    ''', (from_user_id, to_user_id)).fetchone()
    
    if existing:
        # حذف لایک
        conn.execute('DELETE FROM likes WHERE id = ?', (existing['id'],))
        conn.execute('DELETE FROM notifications WHERE type = "like" AND from_user = ? AND user_id = ?', 
                    (from_user_id, to_user_id))
        conn.commit()
        conn.close()
        return jsonify({'liked': False})
    else:
        # اضافه کردن لایک
        conn.execute('''
            INSERT INTO likes (from_user, to_user) VALUES (?, ?)
        ''', (from_user_id, to_user_id))
        
        # ایجاد اعلان
        from_user = conn.execute('SELECT username FROM users WHERE id = ?', (from_user_id,)).fetchone()
        content = f"کاربر @{from_user['username']} شما را لایک کرد"
        conn.execute('''
            INSERT INTO notifications (user_id, type, content, from_user) 
            VALUES (?, ?, ?, ?)
        ''', (to_user_id, 'like', content, from_user_id))
        
        conn.commit()
        conn.close()
        return jsonify({'liked': True})

@app.route('/filters', methods=['POST'])
def update_filters():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    filters = {
        'age_range': request.json.get('age_range'),
        'gender': request.json.get('gender'),
        'city': request.json.get('city')
    }
    
    session['filters'] = filters
    return jsonify({'success': True})

# ===================== SocketIO Handlers =====================
@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)

@socketio.on('leave')
def on_leave(data):
    room = data['room']
    leave_room(room)

@socketio.on('send_message')
def handle_message(data):
    if 'user_id' not in session:
        return
    
    chat_id = data['chat_id']
    message = data['message']
    sender_id = session['user_id']
    
    # ذخیره پیام در دیتابیس
    conn = get_db()
    conn.execute('''
        INSERT INTO messages (chat_id, sender_id, message) 
        VALUES (?, ?, ?)
    ''', (chat_id, sender_id, message))
    conn.commit()
    conn.close()
    
    # ارسال پیام به اتاق
    emit('receive_message', {
        'message': message,
        'sender_id': sender_id,
        'timestamp': datetime.now().strftime('%H:%M')
    }, room=chat_id)

# ===================== تمپلیت‌ها =====================

BASE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}GOYIMIX | گویمیکس{% endblock %}</title>
    <style>
        /* متغیرهای رنگ */
        :root {
            --bg-dark: #121212;
            --primary-gradient: linear-gradient(90deg, #9B5DE5, #00F5D4);
            --neon-pink: #F15BB5;
            --neon-turquoise: #00F5D4;
            --neon-purple: #9B5DE5;
            --white: #FFFFFF;
            --light-gray: #E0E0E0;
            --dark-gray: #222222;
            --medium-gray: #444444;
        }

        /* استایل کلی */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Tahoma', 'Arial', sans-serif;
            background-color: var(--bg-dark);
            color: var(--white);
            direction: rtl;
            line-height: 1.6;
        }

        .container {
            max-width: 100%;
            margin: 0 auto;
            padding: 0 16px;
        }

        /* پیام‌های خطا و موفقیت */
        .message {
            padding: 15px;
            margin: 20px 0;
            border-radius: 8px;
            text-align: center;
            font-weight: 500;
        }

        .error {
            background: #ff4757;
            color: white;
        }

        .success {
            background: #2ed573;
            color: white;
        }

        /* صفحه احراز هویت */
        .auth-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 40px 20px;
        }

        .auth-header {
            text-align: center;
            margin-bottom: 30px;
        }

        .auth-header h1 {
            font-size: 24px;
            font-weight: 700;
            background: var(--primary-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .avatar-upload {
            text-align: center;
            margin-bottom: 20px;
        }

        .avatar-placeholder {
            width: 100px;
            height: 100px;
            border-radius: 50%;
            background: var(--dark-gray);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32px;
            margin: 0 auto 15px;
            border: 2px dashed var(--neon-turquoise);
        }

        .avatar-label {
            color: var(--neon-turquoise);
            cursor: pointer;
            font-size: 14px;
        }

        .auth-form {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .input-group {
            position: relative;
            display: flex;
            align-items: center;
        }

        .input-prefix {
            position: absolute;
            right: 15px;
            color: var(--neon-turquoise);
            font-weight: 500;
        }

        .auth-input {
            width: 100%;
            padding: 15px;
            background: var(--dark-gray);
            border: 1px solid var(--medium-gray);
            border-radius: 12px;
            color: var(--white);
            font-size: 16px;
            transition: all 0.3s ease;
        }

        .auth-input.with-prefix {
            padding-right: 40px;
        }

        .auth-input:focus {
            outline: none;
            border-color: var(--neon-turquoise);
            box-shadow: 0 0 0 2px rgba(0, 245, 212, 0.2);
        }

        .auth-input::placeholder {
            color: var(--light-gray);
        }

        .auth-button {
            background: var(--primary-gradient);
            color: var(--bg-dark);
            border: none;
            padding: 15px;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s ease;
            margin-top: 10px;
        }

        .auth-button:hover {
            transform: translateY(-2px);
        }

        .auth-footer {
            text-align: center;
            margin-top: 20px;
        }

        .auth-footer a {
            color: var(--neon-turquoise);
            text-decoration: none;
        }

        .auth-footer a:hover {
            text-decoration: underline;
        }

        /* داشبورد */
        .dashboard-container {
            padding-bottom: 80px;
        }

        .dashboard-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 0;
            border-bottom: 1px solid var(--medium-gray);
        }

        .header-center h1 {
            font-size: 20px;
            font-weight: 700;
            background: var(--primary-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .notification-icon {
            position: relative;
            font-size: 24px;
            color: var(--white);
        }

        .notification-badge {
            position: absolute;
            top: -8px;
            right: -8px;
            background: var(--neon-pink);
            color: var(--white);
            border-radius: 50%;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: 600;
        }

        .filters-section {
            padding: 20px 0;
        }

        .filter-chips {
            display: flex;
            gap: 10px;
            overflow-x: auto;
            padding: 0 16px;
        }

        .filter-chip {
            background: var(--dark-gray);
            color: var(--light-gray);
            border: none;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px;
            cursor: pointer;
            white-space: nowrap;
            transition: all 0.3s ease;
        }

        .filter-chip.active,
        .filter-chip:hover {
            background: var(--neon-purple);
            color: var(--white);
        }

        .profiles-grid {
            display: grid;
            gap: 20px;
            padding: 0 16px 20px;
        }

        .profile-card {
            background: var(--dark-gray);
            border-radius: 16px;
            padding: 20px;
            display: flex;
            gap: 15px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }

        .profile-avatar {
            flex-shrink: 0;
        }

        .profile-avatar img,
        .default-avatar {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            object-fit: cover;
            background: var(--medium-gray);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
        }

        .profile-info {
            flex: 1;
            min-width: 0;
        }

        .profile-info h3 {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 5px;
            color: var(--white);
        }

        .profile-info p {
            font-size: 14px;
            color: var(--light-gray);
            margin-bottom: 3px;
        }

        .profile-bio {
            margin-top: 10px;
            font-size: 13px;
            color: var(--light-gray);
            line-height: 1.4;
        }

        .profile-actions {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .like-button,
        .chat-button {
            background: none;
            border: none;
            font-size: 20px;
            cursor: pointer;
            padding: 5px;
            border-radius: 50%;
            transition: all 0.2s ease;
        }

        .like-button:hover,
        .chat-button:hover {
            background: rgba(255,255,255,0.1);
            transform: scale(1.1);
        }

        /* نوار پایین */
        .bottom-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: var(--dark-gray);
            display: flex;
            justify-content: space-around;
            padding: 12px 0;
            border-top: 1px solid var(--medium-gray);
        }

        .nav-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            text-decoration: none;
            color: var(--light-gray);
            font-size: 12px;
            transition: all 0.2s ease;
        }

        .nav-item.active {
            color: var(--neon-turquoise);
        }

        .nav-icon {
            font-size: 20px;
            margin-bottom: 4px;
        }

        /* پروفایل */
        .profile-container {
            padding: 20px 16px;
            max-width: 500px;
            margin: 0 auto;
        }

        .profile-header {
            text-align: center;
            margin-bottom: 30px;
        }

        .profile-header h1 {
            font-size: 24px;
            font-weight: 700;
            background: var(--primary-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .profile-form {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .profile-avatar-section {
            text-align: center;
            margin-bottom: 20px;
        }

        .profile-avatar img,
        .default-avatar {
            width: 100px;
            height: 100px;
            border-radius: 50%;
            object-fit: cover;
            background: var(--medium-gray);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32px;
            margin: 0 auto 15px;
        }

        .change-avatar-btn {
            background: var(--dark-gray);
            color: var(--neon-turquoise);
            border: 1px solid var(--neon-turquoise);
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .change-avatar-btn:hover {
            background: var(--neon-turquoise);
            color: var(--bg-dark);
        }

        .form-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .form-group label {
            font-size: 14px;
            color: var(--light-gray);
            font-weight: 500;
        }

        .profile-input {
            width: 100%;
            padding: 12px 15px;
            background: var(--dark-gray);
            border: 1px solid var(--medium-gray);
            border-radius: 10px;
            color: var(--white);
            font-size: 15px;
            transition: all 0.3s ease;
        }

        .profile-input:focus {
            outline: none;
            border-color: var(--neon-turquoise);
            box-shadow: 0 0 0 2px rgba(0, 245, 212, 0.2);
        }

        .profile-input.readonly {
            background: var(--medium-gray);
            color: var(--light-gray);
        }

        .checkbox-group {
            margin-top: 10px;
        }

        .checkbox-label {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 15px;
            color: var(--light-gray);
            cursor: pointer;
        }

        .checkbox-label input {
            width: 18px;
            height: 18px;
        }

        .profile-button {
            background: var(--primary-gradient);
            color: var(--bg-dark);
            border: none;
            padding: 15px;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s ease;
            margin-top: 10px;
        }

        .profile-button:hover {
            transform: translateY(-2px);
        }

        .profile-actions {
            margin-top: 30px;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .profile-action-btn {
            background: var(--dark-gray);
            color: var(--white);
            border: 1px solid var(--medium-gray);
            padding: 12px;
            border-radius: 10px;
            font-size: 15px;
            text-align: center;
            text-decoration: none;
            transition: all 0.2s ease;
        }

        .profile-action-btn:hover {
            background: var(--medium-gray);
        }

        .profile-action-btn.danger {
            color: #ff6b6b;
            border-color: #ff6b6b;
        }

        .profile-action-btn.danger:hover {
            background: rgba(255, 107, 107, 0.1);
        }

        /* مودال‌ها */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.8);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }

        .modal-content {
            background: var(--bg-dark);
            border-radius: 16px;
            padding: 25px;
            width: 90%;
            max-width: 400px;
            position: relative;
            border: 1px solid var(--medium-gray);
        }

        .close {
            position: absolute;
            top: 15px;
            left: 15px;
            font-size: 24px;
            color: var(--light-gray);
            cursor: pointer;
            transition: color 0.2s ease;
        }

        .close:hover {
            color: var(--white);
        }

        .modal-content h2 {
            text-align: center;
            margin-bottom: 20px;
            font-size: 20px;
            color: var(--white);
        }

        .modal-content p {
            text-align: center;
            margin-bottom: 20px;
            color: var(--light-gray);
            line-height: 1.5;
        }

        .modal-input {
            width: 100%;
            padding: 12px 15px;
            background: var(--dark-gray);
            border: 1px solid var(--medium-gray);
            border-radius: 10px;
            color: var(--white);
            font-size: 15px;
            margin-bottom: 15px;
            transition: all 0.3s ease;
        }

        .modal-input:focus {
            outline: none;
            border-color: var(--neon-turquoise);
            box-shadow: 0 0 0 2px rgba(0, 245, 212, 0.2);
        }

        .modal-button {
            width: 100%;
            background: var(--primary-gradient);
            color: var(--bg-dark);
            border: none;
            padding: 12px;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s ease;
        }

        .modal-button:hover {
            transform: translateY(-2px);
        }

        .modal-button.danger {
            background: #ff6b6b;
            color: var(--white);
        }

        /* جستجو */
        .search-container {
            padding-bottom: 80px;
        }

        .search-header {
            text-align: center;
            padding: 20px 0;
            border-bottom: 1px solid var(--medium-gray);
        }

        .search-header h1 {
            font-size: 20px;
            font-weight: 700;
            background: var(--primary-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .search-form {
            padding: 20px 16px;
        }

        .search-input-container {
            position: relative;
            display: flex;
            align-items: center;
        }

        .search-input {
            width: 100%;
            padding: 15px 50px 15px 20px;
            background: var(--dark-gray);
            border: 1px solid var(--medium-gray);
            border-radius: 12px;
            color: var(--white);
            font-size: 16px;
            transition: all 0.3s ease;
        }

        .search-input:focus {
            outline: none;
            border-color: var(--neon-turquoise);
            box-shadow: 0 0 0 2px rgba(0, 245, 212, 0.2);
        }

        .search-button {
            position: absolute;
            left: 15px;
            background: none;
            border: none;
            font-size: 20px;
            color: var(--neon-turquoise);
            cursor: pointer;
            transition: transform 0.2s ease;
        }

        .search-button:hover {
            transform: scale(1.1);
        }

        .search-results {
            padding: 0 16px;
        }

        .search-result-card {
            background: var(--dark-gray);
            border-radius: 16px;
            padding: 20px;
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }

        .result-avatar {
            flex-shrink: 0;
        }

        .result-avatar img,
        .default-avatar {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            object-fit: cover;
            background: var(--medium-gray);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
        }

        .result-info {
            flex: 1;
            min-width: 0;
        }

        .result-info h3 {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 5px;
            color: var(--white);
        }

        .result-info p {
            font-size: 13px;
            color: var(--light-gray);
            margin-bottom: 2px;
        }

        .result-actions {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .action-button {
            background: none;
            border: none;
            font-size: 18px;
            cursor: pointer;
            padding: 4px;
            border-radius: 50%;
            transition: all 0.2s ease;
        }

        .action-button:hover {
            background: rgba(255,255,255,0.1);
            transform: scale(1.1);
        }

        .no-results {
            text-align: center;
            padding: 40px 20px;
            color: var(--light-gray);
        }

        /* چت */
        .chat-container {
            padding-bottom: 80px;
        }

        .chat-header {
            text-align: center;
            padding: 20px 0;
            border-bottom: 1px solid var(--medium-gray);
        }

        .chat-header h1 {
            font-size: 20px;
            font-weight: 700;
            background: var(--primary-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .chat-list {
            padding: 20px 16px;
        }

        .chat-item {
            display: flex;
            gap: 15px;
            padding: 15px;
            background: var(--dark-gray);
            border-radius: 12px;
            margin-bottom: 15px;
            cursor: pointer;
            transition: all 0.2s ease;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }

        .chat-item:hover {
            background: var(--medium-gray);
            transform: translateY(-2px);
        }

        .chat-avatar {
            flex-shrink: 0;
        }

        .chat-avatar img,
        .default-avatar {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            object-fit: cover;
            background: var(--medium-gray);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
        }

        .chat-info {
            flex: 1;
            min-width: 0;
        }

        .chat-info h3 {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 5px;
            color: var(--white);
        }

        .chat-info p {
            font-size: 14px;
            color: var(--light-gray);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .chat-time {
            display: flex;
            align-items: center;
            color: var(--light-gray);
            font-size: 12px;
        }

        .no-chats {
            text-align: center;
            padding: 40px 20px;
            color: var(--light-gray);
        }

        /* اتاق چت */
        .chat-room-container {
            display: flex;
            flex-direction: column;
            height: 100vh;
            max-width: 100%;
        }

        .chat-room-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 15px 16px;
            background: var(--dark-gray);
            border-bottom: 1px solid var(--medium-gray);
            flex-shrink: 0;
        }

        .back-button {
            background: none;
            border: none;
            font-size: 20px;
            color: var(--neon-turquoise);
            cursor: pointer;
            padding: 5px;
            border-radius: 50%;
            transition: all 0.2s ease;
        }

        .back-button:hover {
            background: rgba(0, 245, 212, 0.1);
        }

        .chat-partner-info {
            display: flex;
            align-items: center;
            gap: 12px;
            flex: 1;
            min-width: 0;
        }

        .partner-avatar {
            flex-shrink: 0;
        }

        .partner-avatar img,
        .default-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            object-fit: cover;
            background: var(--medium-gray);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
        }

        .partner-name {
            min-width: 0;
        }

        .partner-name h3 {
            font-size: 16px;
            font-weight: 600;
            color: var(--white);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .partner-name p {
            font-size: 13px;
            color: var(--light-gray);
        }

        .chat-actions {
            display: flex;
            gap: 10px;
        }

        .chat-actions .action-button {
            background: none;
            border: none;
            font-size: 18px;
            color: var(--light-gray);
            cursor: pointer;
            padding: 5px;
            border-radius: 50%;
            transition: all 0.2s ease;
        }

        .chat-actions .action-button:hover {
            color: var(--white);
            background: rgba(255,255,255,0.1);
        }

        .messages-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px 16px;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .message {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 18px;
            font-size: 15px;
            line-height: 1.4;
            position: relative;
        }

        .message.sent {
            align-self: flex-end;
            background: var(--neon-purple);
            color: var(--white);
            border-bottom-right-radius: 4px;
        }

        .message.received {
            align-self: flex-start;
            background: var(--dark-gray);
            color: var(--white);
            border-bottom-left-radius: 4px;
        }

        .message-time {
            font-size: 11px;
            color: var(--light-gray);
            margin-top: 5px;
            text-align: right;
        }

        .message-input-container {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 15px 16px;
            background: var(--dark-gray);
            border-top: 1px solid var(--medium-gray);
            flex-shrink: 0;
        }

        .message-input-tools {
            display: flex;
            gap: 8px;
        }

        .tool-button {
            background: none;
            border: none;
            font-size: 18px;
            color: var(--light-gray);
            cursor: pointer;
            padding: 8px;
            border-radius: 50%;
            transition: all 0.2s ease;
        }

        .tool-button:hover {
            color: var(--white);
            background: rgba(255,255,255,0.1);
        }

        .message-input {
            flex: 1;
            padding: 12px 15px;
            background: var(--medium-gray);
            border: 1px solid var(--dark-gray);
            border-radius: 20px;
            color: var(--white);
            font-size: 15px;
            transition: all 0.3s ease;
        }

        .message-input:focus {
            outline: none;
            border-color: var(--neon-turquoise);
            box-shadow: 0 0 0 2px rgba(0, 245, 212, 0.2);
        }

        .send-button {
            background: var(--neon-turquoise);
            border: none;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            color: var(--bg-dark);
            font-size: 18px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
        }

        .send-button:hover {
            transform: scale(1.05);
        }

        /* اعلان‌ها */
        .notifications-container {
            padding-bottom: 80px;
        }

        .notifications-header {
            text-align: center;
            padding: 20px 0;
            border-bottom: 1px solid var(--medium-gray);
        }

        .notifications-header h1 {
            font-size: 20px;
            font-weight: 700;
            background: var(--primary-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .notifications-list {
            padding: 20px 16px;
        }

        .notification-card {
            background: var(--dark-gray);
            border-radius: 16px;
            padding: 20px;
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }

        .notification-icon {
            flex-shrink: 0;
            font-size: 24px;
        }

        .notification-content {
            flex: 1;
            min-width: 0;
        }

        .notification-content p {
            font-size: 15px;
            color: var(--white);
            margin-bottom: 8px;
            line-height: 1.4;
        }

        .notification-time {
            font-size: 12px;
            color: var(--light-gray);
        }

        .notification-actions {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .notification-actions .action-button {
            background: none;
            border: none;
            font-size: 16px;
            cursor: pointer;
            padding: 4px;
            border-radius: 50%;
            transition: all 0.2s ease;
        }

        .notification-actions .action-button:hover {
            background: rgba(255,255,255,0.1);
            transform: scale(1.1);
        }

        .notification-actions .accept:hover {
            color: #2ed573;
        }

        .notification-actions .reject:hover {
            color: #ff4757;
        }

        .notification-actions .block:hover {
            color: #ffa502;
        }

        .no-notifications {
            text-align: center;
            padding: 40px 20px;
            color: var(--light-gray);
        }

        /* رسپانسیو */
        @media (max-width: 480px) {
            .container {
                padding: 0 12px;
            }
            
            .auth-container {
                padding: 30px 15px;
            }
            
            .auth-header h1 {
                font-size: 20px;
            }
            
            .profile-card {
                padding: 15px;
            }
            
            .profile-avatar img,
            .default-avatar {
                width: 50px;
                height: 50px;
                font-size: 20px;
            }
            
            .profile-info h3 {
                font-size: 16px;
            }
            
            .message {
                max-width: 80%;
            }
            
            .bottom-nav {
                padding: 8px 0;
            }
            
            .nav-icon {
                font-size: 18px;
            }
            
            .nav-label {
                font-size: 11px;
            }
        }

        /* انیمیشن‌ها */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .profile-card,
        .chat-item,
        .notification-card,
        .search-result-card {
            animation: fadeIn 0.3s ease-out;
        }

        /* افکت Glow */
        .auth-button,
        .send-button,
        .modal-button {
            box-shadow: 0 0 15px rgba(155, 93, 229, 0.5);
        }

        .like-button:hover,
        .chat-button:hover,
        .action-button:hover,
        .tool-button:hover {
            box-shadow: 0 0 10px rgba(241, 91, 181, 0.3);
        }

        .notification-badge {
            box-shadow: 0 0 8px rgba(241, 91, 181, 0.6);
        }
    </style>
</head>
<body>
    <div class="container">
        {% if error %}
            <div class="message error">{{ error }}</div>
        {% endif %}
        {% if success %}
            <div class="message success">{{ success }}</div>
        {% endif %}
        {% block content %}{% endblock %}
    </div>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script>
        {% block scripts %}{% endblock %}
    </script>
</body>
</html>
'''

SIGNUP_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
<div class="auth-container">
    <div class="auth-header">
        <h1>خوش آمدید به گویمیکس | GOYIMIX</h1>
    </div>
    
    <form method="POST" class="auth-form">
        <div class="avatar-upload">
            <div class="avatar-placeholder">➕</div>
            <input type="file" id="avatar" name="avatar" accept="image/*" style="display: none;">
            <label for="avatar" class="avatar-label">انتخاب عکس پروفایل</label>
        </div>
        
        <input type="text" name="name" placeholder="نام (اختیاری)" class="auth-input">
        
        <div class="input-group">
            <span class="input-prefix">@</span>
            <input type="text" name="username" placeholder="نام کاربری" required class="auth-input with-prefix">
        </div>
        
        <input type="number" name="age" placeholder="سن" min="12" max="80" required class="auth-input">
        
        <select name="gender" required class="auth-input">
            <option value="">جنسیت</option>
            <option value="پسر">پسر</option>
            <option value="دختر">دختر</option>
            <option value="دیگر">دیگر</option>
        </select>
        
        <textarea name="bio" placeholder="بیو (اختیاری)" class="auth-input" rows="3"></textarea>
        
        <input type="text" name="interests" placeholder="علاقه‌مندی‌ها (اختیاری)" class="auth-input">
        
        <select name="city" required class="auth-input">
            <option value="">انتخاب شهر</option>
            {% for city in cities %}
                <option value="{{ city }}">{{ city }}</option>
            {% endfor %}
        </select>
        
        <input type="password" name="password" placeholder="رمز عبور" required class="auth-input">
        <input type="password" name="confirm_password" placeholder="تکرار رمز عبور" required class="auth-input">
        
        <button type="submit" class="auth-button">ثبت‌نام</button>
    </form>
    
    <div class="auth-footer">
        <p>حساب دارید؟ <a href="/login">وارد شوید</a></p>
    </div>
</div>
''')

LOGIN_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
<div class="auth-container">
    <div class="auth-header">
        <h1>دوباره خوش آمدید</h1>
    </div>
    
    <form method="POST" class="auth-form">
        <input type="text" name="username" placeholder="نام کاربری یا نام" required class="auth-input">
        <input type="password" name="password" placeholder="رمز عبور" required class="auth-input">
        <button type="submit" class="auth-button">ورود</button>
    </form>
    
    <div class="auth-footer">
        <p>اگر حسابی ندارید؟ <a href="/signup">ثبت‌نام کنید</a></p>
    </div>
</div>
''')

DASHBOARD_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
<div class="dashboard-container">
    <!-- هدر -->
    <div class="dashboard-header">
        <div class="header-center">
            <h1>GOYIMIX | گویمیکس</h1>
        </div>
        <div class="header-left">
            <a href="/notifications" class="notification-icon">
                🔔
                {% if unread_count > 0 %}
                    <span class="notification-badge">{{ unread_count }}</span>
                {% endif %}
            </a>
        </div>
    </div>
    
    <!-- فیلترها -->
    <div class="filters-section">
        <div class="filter-chips">
            <button class="filter-chip active">همه</button>
            <button class="filter-chip">هم‌سن</button>
            <button class="filter-chip">هم‌جنسیت</button>
            <button class="filter-chip">هم‌شهر</button>
        </div>
    </div>
    
    <!-- پروفایل‌ها -->
    <div class="profiles-grid">
        {% for profile in profiles %}
        <div class="profile-card">
            <div class="profile-avatar">
                {% if profile.avatar %}
                    <img src="{{ profile.avatar }}" alt="{{ profile.username }}">
                {% else %}
                    <div class="default-avatar">
                        {% if profile.gender == 'دختر' %}🧕{% else %}🧑‍💼{% endif %}
                    </div>
                {% endif %}
            </div>
            <div class="profile-info">
                <h3>{{ profile.name or profile.username }}</h3>
                <p>@{{ profile.username }}</p>
                <p>{{ profile.age }} سال | {{ profile.city }}</p>
                {% if profile.bio %}
                    <p class="profile-bio">{{ profile.bio }}</p>
                {% endif %}
            </div>
            <div class="profile-actions">
                <button class="like-button" onclick="likeUser({{ profile.id }})">❤️</button>
                <button class="chat-button" onclick="startChat({{ profile.id }})">💬</button>
            </div>
        </div>
        {% endfor %}
    </div>
    
    <!-- نوار پایین -->
    <div class="bottom-nav">
        <a href="/profile" class="nav-item">
            <span class="nav-icon">👤</span>
            <span class="nav-label">پروفایل</span>
        </a>
        <a href="/dashboard" class="nav-item active">
            <span class="nav-icon">🏠</span>
            <span class="nav-label">خانه</span>
        </a>
        <a href="/search" class="nav-item">
            <span class="nav-icon">🔍</span>
            <span class="nav-label">جستجو</span>
        </a>
        <a href="/chat" class="nav-item">
            <span class="nav-icon">💬</span>
            <span class="nav-label">چت</span>
        </a>
    </div>
</div>
''').replace('{% block scripts %}{% endblock %}', '''
<script>
    function likeUser(userId) {
        fetch(`/like/${userId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            const button = event.target;
            if (data.liked) {
                button.innerHTML = '❤️';
                button.style.color = '#F15BB5';
            } else {
                button.innerHTML = '🤍';
                button.style.color = '#FFFFFF';
            }
        });
    }
    
    function startChat(userId) {
        window.location.href = `/chat/${userId}`;
    }
</script>
''')

PROFILE_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
<div class="profile-container">
    <div class="profile-header">
        <h1>پروفایل شما</h1>
    </div>
    
    <form method="POST" action="/profile/edit" class="profile-form">
        <div class="profile-avatar-section">
            <div class="profile-avatar">
                {% if user.avatar %}
                    <img src="{{ user.avatar }}" alt="{{ user.username }}">
                {% else %}
                    <div class="default-avatar">
                        {% if user.gender == 'دختر' %}🧕{% else %}🧑‍💼{% endif %}
                    </div>
                {% endif %}
            </div>
            <button type="button" class="change-avatar-btn">تغییر عکس</button>
        </div>
        
        <div class="form-group">
            <label>نام:</label>
            <input type="text" name="name" value="{{ user.name or '' }}" class="profile-input">
        </div>
        
        <div class="form-group">
            <label>@نام کاربری:</label>
            <input type="text" value="@{{ user.username }}" readonly class="profile-input readonly">
        </div>
        
        <div class="form-group">
            <label>سن:</label>
            <input type="number" value="{{ user.age }}" readonly class="profile-input readonly">
        </div>
        
        <div class="form-group">
            <label>جنسیت:</label>
            <input type="text" value="{{ user.gender }}" readonly class="profile-input readonly">
        </div>
        
        <div class="form-group">
            <label>شهر:</label>
            <select name="city" class="profile-input">
                {% for city in CITIES %}
                    <option value="{{ city }}" {% if city == user.city %}selected{% endif %}>{{ city }}</option>
                {% endfor %}
            </select>
        </div>
        
        <div class="form-group">
            <label>بیو:</label>
            <textarea name="bio" class="profile-input" rows="3">{{ user.bio or '' }}</textarea>
        </div>
        
        <div class="form-group">
            <label>علاقه‌مندی‌ها:</label>
            <input type="text" name="interests" value="{{ user.interests or '' }}" class="profile-input">
        </div>
        
        <div class="form-group checkbox-group">
            <label class="checkbox-label">
                <input type="checkbox" name="visible" {% if user.visible %}checked{% endif %}>
                نمایش پروفایل در خانه
            </label>
        </div>
        
        <button type="submit" class="profile-button">ذخیره تغییرات</button>
    </form>
    
    <div class="profile-actions">
        <button class="profile-action-btn" onclick="showChangePassword()">تغییر رمز عبور</button>
        <button class="profile-action-btn danger" onclick="showDeleteAccount()">حذف حساب</button>
        <a href="/logout" class="profile-action-btn">خروج از حساب</a>
    </div>
</div>

<!-- مودال تغییر رمز عبور -->
<div id="changePasswordModal" class="modal">
    <div class="modal-content">
        <span class="close" onclick="closeModal('changePasswordModal')">&times;</span>
        <h2>تغییر رمز عبور</h2>
        <form method="POST" action="/profile/change_password">
            <input type="password" name="current_password" placeholder="رمز عبور فعلی" required class="modal-input">
            <input type="password" name="new_password" placeholder="رمز عبور جدید" required class="modal-input">
            <input type="password" name="confirm_password" placeholder="تکرار رمز عبور جدید" required class="modal-input">
            <button type="submit" class="modal-button">تغییر رمز</button>
        </form>
    </div>
</div>

<!-- مودال حذف حساب -->
<div id="deleteAccountModal" class="modal">
    <div class="modal-content">
        <span class="close" onclick="closeModal('deleteAccountModal')">&times;</span>
        <h2>حذف حساب کاربری</h2>
        <p>آیا مطمئنید؟ این عمل غیرقابل بازگشت است.</p>
        <form method="POST" action="/profile/delete">
            <input type="password" name="password" placeholder="رمز عبور" required class="modal-input">
            <input type="password" name="confirm_password" placeholder="تکرار رمز عبور" required class="modal-input">
            <button type="submit" class="modal-button danger">تأیید حذف</button>
        </form>
    </div>
</div>
''').replace('{% block scripts %}{% endblock %}', '''
<script>
    function showChangePassword() {
        document.getElementById('changePasswordModal').style.display = 'block';
    }
    
    function showDeleteAccount() {
        document.getElementById('deleteAccountModal').style.display = 'block';
    }
    
    function closeModal(modalId) {
        document.getElementById(modalId).style.display = 'none';
    }
    
    // بستن مودال با کلیک خارج از آن
    window.onclick = function(event) {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = 'none';
        }
    }
</script>
''')

SEARCH_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
<div class="search-container">
    <div class="search-header">
        <h1>جستجو</h1>
    </div>
    
    <form method="GET" class="search-form">
        <div class="search-input-container">
            <input type="text" name="q" value="{{ query or '' }}" placeholder="جستجو بر اساس نام یا @نام‌کاربری" class="search-input">
            <button type="submit" class="search-button">🔍</button>
        </div>
    </form>
    
    {% if query %}
        <div class="search-results">
            {% if results %}
                {% for user in results %}
                <div class="search-result-card">
                    <div class="result-avatar">
                        {% if user.avatar %}
                            <img src="{{ user.avatar }}" alt="{{ user.username }}">
                        {% else %}
                            <div class="default-avatar">
                                {% if user.gender == 'دختر' %}🧕{% else %}🧑‍💼{% endif %}
                            </div>
                        {% endif %}
                    </div>
                    <div class="result-info">
                        <h3>{{ user.name or user.username }}</h3>
                        <p>@{{ user.username }}</p>
                        <p>{{ user.age }} سال | {{ user.city }}</p>
                    </div>
                    <div class="result-actions">
                        <button class="action-button" onclick="likeUser({{ user.id }})">❤️</button>
                        <button class="action-button" onclick="startChat({{ user.id }})">💬</button>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <div class="no-results">
                    <p>موردی یافت نشد</p>
                </div>
            {% endif %}
        </div>
    {% endif %}
    
    <!-- نوار پایین -->
    <div class="bottom-nav">
        <a href="/profile" class="nav-item">
            <span class="nav-icon">👤</span>
            <span class="nav-label">پروفایل</span>
        </a>
        <a href="/dashboard" class="nav-item">
            <span class="nav-icon">🏠</span>
            <span class="nav-label">خانه</span>
        </a>
        <a href="/search" class="nav-item active">
            <span class="nav-icon">🔍</span>
            <span class="nav-label">جستجو</span>
        </a>
        <a href="/chat" class="nav-item">
            <span class="nav-icon">💬</span>
            <span class="nav-label">چت</span>
        </a>
    </div>
</div>
''').replace('{% block scripts %}{% endblock %}', '''
<script>
    function likeUser(userId) {
        fetch(`/like/${userId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            const button = event.target;
            if (data.liked) {
                button.innerHTML = '❤️';
                button.style.color = '#F15BB5';
            } else {
                button.innerHTML = '🤍';
                button.style.color = '#FFFFFF';
            }
        });
    }
    
    function startChat(userId) {
        window.location.href = `/chat/${userId}`;
    }
</script>
''')

CHAT_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
<div class="chat-container">
    <div class="chat-header">
        <h1>چت‌ها</h1>
    </div>
    
    <div class="chat-list">
        {% if chats %}
            {% for chat in chats %}
            <div class="chat-item" onclick="openChat({{ chat.user1 == user.id and chat.user2 or chat.user1 }})">
                <div class="chat-avatar">
                    {% if (chat.user1 == user.id and chat.user2_avatar) or (chat.user2 == user.id and chat.user1_avatar) %}
                        <img src="{{ chat.user1 == user.id and chat.user2_avatar or chat.user1_avatar }}" alt="avatar">
                    {% else %}
                        <div class="default-avatar">
                            {% if (chat.user1 == user.id and chat.user2_gender == 'دختر') or (chat.user2 == user.id and chat.user1_gender == 'دختر') %}🧕{% else %}🧑‍💼{% endif %}
                        </div>
                    {% endif %}
                </div>
                <div class="chat-info">
                    <h3>{{ chat.user1 == user.id and chat.user2_username or chat.user1_username }}</h3>
                    <p>آخرین پیام...</p>
                </div>
                <div class="chat-time">
                    <span>۱۰:۳۰</span>
                </div>
            </div>
            {% endfor %}
        {% else %}
            <div class="no-chats">
                <p>هنوز چتی ندارید</p>
            </div>
        {% endif %}
    </div>
    
    <!-- نوار پایین -->
    <div class="bottom-nav">
        <a href="/profile" class="nav-item">
            <span class="nav-icon">👤</span>
            <span class="nav-label">پروفایل</span>
        </a>
        <a href="/dashboard" class="nav-item">
            <span class="nav-icon">🏠</span>
            <span class="nav-label">خانه</span>
        </a>
        <a href="/search" class="nav-item">
            <span class="nav-icon">🔍</span>
            <span class="nav-label">جستجو</span>
        </a>
        <a href="/chat" class="nav-item active">
            <span class="nav-icon">💬</span>
            <span class="nav-label">چت</span>
        </a>
    </div>
</div>
''').replace('{% block scripts %}{% endblock %}', '''
<script>
    function openChat(userId) {
        window.location.href = `/chat/${userId}`;
    }
</script>
''')

CHAT_ROOM_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
<div class="chat-room-container">
    <!-- هدر چت -->
    <div class="chat-room-header">
        <button class="back-button" onclick="window.location.href='/chat'">←</button>
        <div class="chat-partner-info">
            <div class="partner-avatar">
                {% if other_user.avatar %}
                    <img src="{{ other_user.avatar }}" alt="{{ other_user.username }}">
                {% else %}
                    <div class="default-avatar">
                        {% if other_user.gender == 'دختر' %}🧕{% else %}🧑‍💼{% endif %}
                    </div>
                {% endif %}
            </div>
            <div class="partner-name">
                <h3>{{ other_user.name or other_user.username }}</h3>
                <p>@{{ other_user.username }}</p>
            </div>
        </div>
        <div class="chat-actions">
            <button class="action-button">📌</button>
            <button class="action-button">🗑️</button>
        </div>
    </div>
    
    <!-- پیام‌ها -->
    <div class="messages-container" id="messagesContainer">
        {% for message in messages %}
        <div class="message {% if message.sender_id == user.id %}sent{% else %}received{% endif %}">
            <div class="message-content">
                {{ message.message }}
            </div>
            <div class="message-time">
                {{ message.timestamp.strftime('%H:%M') if message.timestamp else 'الآن' }}
            </div>
        </div>
        {% endfor %}
    </div>
    
    <!-- ارسال پیام -->
    <div class="message-input-container">
        <div class="message-input-tools">
            <button class="tool-button">📷</button>
            <button class="tool-button">🎤</button>
            <button class="tool-button">😀</button>
        </div>
        <input type="text" id="messageInput" placeholder="پیام خود را بنویسید..." class="message-input">
        <button class="send-button" onclick="sendMessage()">➤</button>
    </div>
</div>
''').replace('{% block scripts %}{% endblock %}', '''
<script>
    const socket = io();
    const chatId = {{ chat_id }};
    const userId = {{ user.id }};
    
    // پیوستن به اتاق چت
    socket.emit('join', {room: chatId});
    
    // دریافت پیام
    socket.on('receive_message', function(data) {
        const messagesContainer = document.getElementById('messagesContainer');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${data.sender_id == userId ? 'sent' : 'received'}`;
        messageDiv.innerHTML = `
            <div class="message-content">${data.message}</div>
            <div class="message-time">${data.timestamp}</div>
        `;
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    });
    
    // ارسال پیام
    function sendMessage() {
        const input = document.getElementById('messageInput');
        const message = input.value.trim();
        
        if (message) {
            socket.emit('send_message', {
                chat_id: chatId,
                message: message
            });
            input.value = '';
        }
    }
    
    // ارسال با Enter
    document.getElementById('messageInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    // اسکرول به آخرین پیام
    document.addEventListener('DOMContentLoaded', function() {
        const messagesContainer = document.getElementById('messagesContainer');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    });
</script>
''')

NOTIFICATIONS_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
<div class="notifications-container">
    <div class="notifications-header">
        <h1>اعلان‌ها</h1>
    </div>
    
    <div class="notifications-list">
        {% if notifications %}
            {% for notification in notifications %}
            <div class="notification-card">
                <div class="notification-icon">
                    {% if notification.type == 'like' %}❤️
                    {% elif notification.type == 'chat_request' %}💬
                    {% elif notification.type == 'message' %}✉️
                    {% else %}🔔{% endif %}
                </div>
                <div class="notification-content">
                    <p>{{ notification.content }}</p>
                    <span class="notification-time">{{ notification.created_at.strftime('%Y/%m/%d %H:%M') }}</span>
                </div>
                <div class="notification-actions">
                    <button class="action-button accept">✅</button>
                    <button class="action-button reject">❌</button>
                    <button class="action-button block">🚫</button>
                </div>
            </div>
            {% endfor %}
        {% else %}
            <div class="no-notifications">
                <p>اعلانی وجود ندارد</p>
            </div>
        {% endif %}
    </div>
    
    <!-- نوار پایین -->
    <div class="bottom-nav">
        <a href="/profile" class="nav-item">
            <span class="nav-icon">👤</span>
            <span class="nav-label">پروفایل</span>
        </a>
        <a href="/dashboard" class="nav-item">
            <span class="nav-icon">🏠</span>
            <span class="nav-label">خانه</span>
        </a>
        <a href="/search" class="nav-item">
            <span class="nav-icon">🔍</span>
            <span class="nav-label">جستجو</span>
        </a>
        <a href="/chat" class="nav-item">
            <span class="nav-icon">💬</span>
            <span class="nav-label">چت</span>
        </a>
    </div>
</div>
''')

SUCCESS_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
<div class="auth-container">
    <div class="auth-header">
        <h1>🎉 {{ message }}</h1>
    </div>
    <div class="auth-footer">
        <a href="/login">ورود به حساب</a>
    </div>
</div>
''')

ERROR_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
<div class="auth-container">
    <div class="auth-header">
        <h1>❌ {{ message }}</h1>
    </div>
    <div class="auth-footer">
        <a href="javascript:history.back()">بازگشت</a>
    </div>
</div>
''')

# ===================== اجرای اپلیکیشن =====================
if __name__ == '__main__':
    init_db()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)