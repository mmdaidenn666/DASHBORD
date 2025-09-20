import os
import sqlite3
import hashlib
import json
from datetime import datetime
from flask import Flask, request, session, redirect, url_for, make_response, jsonify, render_template_string, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.utils import secure_filename
import base64
import random
import eventlet

eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static', exist_ok=True)

# Default profile pics (base64 placeholders, in real use save images)
DEFAULT_MALE = 'default_male.png'  # Assume you have these files
DEFAULT_FEMALE = 'default_female.png'
DEFAULT_OTHER = 'default_other.png'

# Database initialization
def init_db():
    conn = sqlite3.connect('goyimix.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  name TEXT,
                  password_hash TEXT NOT NULL,
                  age INTEGER NOT NULL,
                  gender TEXT NOT NULL,
                  bio TEXT,
                  interests TEXT,
                  city TEXT NOT NULL,
                  profile_pic TEXT,
                  show_profile BOOLEAN DEFAULT 1)''')
    c.execute('''CREATE TABLE IF NOT EXISTS likes
                 (liker_id INTEGER,
                  liked_id INTEGER,
                  PRIMARY KEY (liker_id, liked_id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS chat_requests
                 (requester_id INTEGER,
                  target_id INTEGER,
                  status TEXT DEFAULT 'pending',  -- pending, accepted, rejected, blocked
                  PRIMARY KEY (requester_id, target_id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS chats
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user1_id INTEGER,
                  user2_id INTEGER,
                  UNIQUE(user1_id, user2_id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  chat_id INTEGER,
                  sender_id INTEGER,
                  content TEXT,
                  type TEXT DEFAULT 'text',  -- text, image, voice, sticker
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS notifications
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  content TEXT,
                  type TEXT,
                  from_user_id INTEGER,
                  read BOOLEAN DEFAULT 0,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS blocks
                 (blocker_id INTEGER,
                  blocked_id INTEGER,
                  PRIMARY KEY (blocker_id, blocked_id))''')
    conn.commit()
    conn.close()

init_db()

# Helper functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_current_user_id():
    return session.get('user_id')

def get_user_by_id(user_id):
    conn = sqlite3.connect('goyimix.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    if user:
        return {
            'id': user[0],
            'username': user[1],
            'name': user[2],
            'age': user[4],
            'gender': user[5],
            'bio': user[6],
            'interests': user[7],
            'city': user[8],
            'profile_pic': user[9],
            'show_profile': user[10]
        }
    return None

def notify(user_id, content, ntype, from_user_id=None):
    conn = sqlite3.connect('goyimix.db')
    c = conn.cursor()
    c.execute('INSERT INTO notifications (user_id, content, type, from_user_id) VALUES (?, ?, ?, ?)', (user_id, content, ntype, from_user_id))
    conn.commit()
    notif_id = c.lastrowid
    conn.close()
    socketio.emit('new_notification', {'user_id': user_id, 'content': content, 'type': ntype, 'from_user_id': from_user_id, 'id': notif_id})
    # For push, would need web-push, but omit for now

def has_unread_notifications(user_id):
    conn = sqlite3.connect('goyimix.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM notifications WHERE user_id = ? AND read = 0', (user_id,))
    count = c.fetchone()[0]
    conn.close()
    return count > 0

def get_like_count(user_id):
    conn = sqlite3.connect('goyimix.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM likes WHERE liked_id = ?', (user_id,))
    count = c.fetchone()[0]
    conn.close()
    return count

def is_liked(liker_id, liked_id):
    conn = sqlite3.connect('goyimix.db')
    c = conn.cursor()
    c.execute('SELECT * FROM likes WHERE liker_id = ? AND liked_id = ?', (liker_id, liked_id))
    like = c.fetchone()
    conn.close()
    return like is not None

def is_blocked(blocker_id, blocked_id):
    conn = sqlite3.connect('goyimix.db')
    c = conn.cursor()
    c.execute('SELECT * FROM blocks WHERE blocker_id = ? AND blocked_id = ?', (blocker_id, blocked_id))
    block = c.fetchone()
    conn.close()
    return block is not None

def get_chat_id(user1, user2):
    conn = sqlite3.connect('goyimix.db')
    c = conn.cursor()
    c.execute('SELECT id FROM chats WHERE (user1_id = ? AND user2_id = ?) OR (user1_id = ? AND user2_id = ?)', (user1, user2, user2, user1))
    chat = c.fetchone()
    if not chat:
        c.execute('INSERT INTO chats (user1_id, user2_id) VALUES (?, ?)', (min(user1, user2), max(user1, user2)))
        conn.commit()
        chat_id = c.lastrowid
    else:
        chat_id = chat[0]
    conn.close()
    return chat_id

# HTML templates
BASE_CSS = '''
body { background: #121212; color: #FFFFFF; font-family: sans-serif; margin: 0; padding: 0; }
.container { max-width: 600px; margin: auto; padding: 20px; }
input, select, textarea { width: 100%; padding: 10px; margin: 10px 0; background: #E0E0E0; border: none; border-radius: 5px; color: #121212; }
button { background: linear-gradient(#9B5DE5, #00F5D4); color: #121212; padding: 10px 20px; border: none; border-radius: 20px; box-shadow: 0 0 10px #F15BB5; cursor: pointer; transition: all 0.3s; }
button:hover { box-shadow: 0 0 20px #F15BB5; }
a { color: #F15BB5; text-decoration: none; }
.profile-pic { width: 100px; height: 100px; border-radius: 50%; object-fit: cover; }
.card { background: #1E1E1E; padding: 15px; margin: 10px 0; border-radius: 10px; box-shadow: 0 0 5px #00F5D4; }
.filter-btn { background: #E0E0E0; color: #121212; border-radius: 20px; padding: 5px 15px; margin: 5px; }
.active-filter { background: #00F5D4; color: #121212; }
.heart { cursor: pointer; font-size: 24px; }
.red-heart { color: red; }
.header { text-align: center; position: relative; padding: 10px; }
.notifications { position: absolute; left: 10px; top: 10px; font-size: 24px; }
.notification-dot { background: red; border-radius: 50%; width: 10px; height: 10px; display: inline-block; position: absolute; top: 0; right: -5px; }
.navbar { position: fixed; bottom: 0; width: 100%; background: #121212; display: flex; justify-content: space-around; padding: 10px 0; border-top: 1px solid #E0E0E0; }
.nav-item { text-align: center; color: #E0E0E0; font-size: 20px; }
.active { border: 2px solid gray; border-radius: 10px; padding: 5px; }
.chat-list-item { display: flex; align-items: center; }
.chat-messages { height: 400px; overflow-y: scroll; }
.my-message { text-align: right; background: #00F5D4; color: #121212; padding: 10px; margin: 5px; border-radius: 10px; }
.other-message { text-align: left; background: #E0E0E0; color: #121212; padding: 10px; margin: 5px; border-radius: 10px; }
'''

REGISTER_HTML = '''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ثبت‌نام - GOYIMIX</title>
    <style>''' + BASE_CSS + '''</style>
</head>
<body>
    <div class="container">
        <h1>خوش آمدید به گویمیکس | GOYIMIX</h1>
        <form method="POST" enctype="multipart/form-data">
            <div class="profile-pic-container">
                <img id="profilePreview" src="/static/default_other.png" class="profile-pic" onclick="document.getElementById('profile_pic').click();">
                <input type="file" id="profile_pic" name="profile_pic" accept="image/*" style="display:none;" onchange="previewProfilePic(event)">
            </div>
            <input type="text" name="name" placeholder="نام (اختیاری)">
            <input type="text" name="username" placeholder="نام کاربری (با @ شروع شود)" required>
            <select name="age" required>
                {% for i in range(12, 81) %}
                <option value="{{i}}">{{i}} سال</option>
                {% endfor %}
            </select>
            <select name="gender" required onchange="updateDefaultPic(this.value)">
                <option value="پسر">پسر</option>
                <option value="دختر">دختر</option>
                <option value="دیگر">دیگر</option>
            </select>
            <textarea name="bio" placeholder="بیو (اختیاری)"></textarea>
            <textarea name="interests" placeholder="علاقه‌مندی‌ها (اختیاری)"></textarea>
            <select name="city" required>
                {% for city in cities %}
                <option value="{{city}}">{{city}}</option>
                {% endfor %}
            </select>
            <input type="password" name="password" placeholder="رمز عبور" required>
            <input type="password" name="confirm_password" placeholder="تکرار رمز عبور" required>
            <button type="submit">ثبت‌نام</button>
        </form>
        <p><a href="/login">حساب دارید؟ وارد شوید</a></p>
        {% if error %}<p style="color: red;">{{error}}</p>{% endif %}
    </div>
    <script>
        function previewProfilePic(event) {
            var reader = new FileReader();
            reader.onload = function() {
                document.getElementById('profilePreview').src = reader.result;
            }
            reader.readAsDataURL(event.target.files[0]);
        }
        function updateDefaultPic(gender) {
            var src = '/static/default_other.png';
            if (gender === 'پسر') src = '/static/default_male.png';
            else if (gender === 'دختر') src = '/static/default_female.png';
            document.getElementById('profilePreview').src = src;
        }
    </script>
</body>
</html>
'''

LOGIN_HTML = '''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ورود - GOYIMIX</title>
    <style>''' + BASE_CSS + '''</style>
</head>
<body>
    <div class="container">
        <h1>دوباره خوش آمدید</h1>
        <form method="POST">
            <input type="text" name="username_or_name" placeholder="نام یا نام کاربری" required>
            <input type="password" name="password" placeholder="رمز عبور" required>
            <button type="submit">ورود</button>
        </form>
        <p><a href="/register">حساب ندارید؟ ثبت‌نام کنید</a></p>
        {% if error %}<p style="color: red;">{{error}}</p>{% endif %}
    </div>
</body>
</html>
'''

DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GOYIMIX</title>
    <style>''' + BASE_CSS + '''</style>
    <script src="/socket.io/socket.io.js"></script>
    <script>
        var socket = io();
        socket.on('connect', function() {
            socket.emit('join_user', {user_id: {{current_user_id}}});
        });
        socket.on('new_notification', function(data) {
            if (data.user_id == {{current_user_id}}) {
                // Update notification dot
                document.getElementById('notif-dot').style.display = 'inline-block';
            }
        });
    </script>
</head>
<body>
    <div class="header">
        <h1>GOYIMIX | گویمیکس</h1>
        <div class="notifications">
            <a href="/notifications">🔔</a>
            <span id="notif-dot" class="notification-dot" style="display: {% if has_unread %}block{% else %}none{% endif %};"></span>
        </div>
    </div>
    <div class="container content">
        {{content | safe}}
    </div>
    <div class="navbar">
        <div class="nav-item {% if active == 'profile' %}active{% endif %}"><a href="/profile">👤<br>پروفایل</a></div>
        <div class="nav-item {% if active == 'home' %}active{% endif %}"><a href="/home">🏠<br>خانه</a></div>
        <div class="nav-item {% if active == 'search' %}active{% endif %}"><a href="/search">🔍<br>جستجو</a></div>
        <div class="nav-item {% if active == 'chat' %}active{% endif %}"><a href="/chat">💬<br>چت</a></div>
    </div>
</body>
</html>
'''

PROFILE_CONTENT = '''
<h2>پروفایل</h2>
<img src="{{profile_pic_url}}" class="profile-pic">
<p>نام: {{name}} <a href="/edit/name">✏️</a></p>
<p>نام کاربری: {{username}} <a href="/edit/username">✏️</a></p>
<p>سن: {{age}} <a href="/edit/age">✏️</a></p>
<p>جنسیت: {{gender}} <a href="/edit/gender">✏️</a></p>
<p>بیو: {{bio}} <a href="/edit/bio">✏️</a></p>
<p>علاقه‌مندی‌ها: {{interests}} <a href="/edit/interests">✏️</a></p>
<p>شهر: {{city}} <a href="/edit/city">✏️</a></p>
<p>رمز: ●●● <button onclick="togglePassword()">نمایش</button></p>
<div id="password" style="display:none;">{{password}}</div>
<p>نمایش پروفایل: <input type="checkbox" {% if show_profile %}checked{% endif %} onchange="toggleShowProfile(this.checked)"></p>
<a href="/logout"><button>خروج از حساب</button></a>
<a href="/delete_account"><button style="background: red;">حذف حساب</button></a>
<script>
    function togglePassword() {
        var pw = document.getElementById('password');
        pw.style.display = pw.style.display === 'none' ? 'block' : 'none';
    }
    function toggleShowProfile(checked) {
        fetch('/toggle_show_profile', {method: 'POST', body: JSON.stringify({show: checked}), headers: {'Content-Type': 'application/json'}});
    }
</script>
'''

EDIT_FIELD_HTML = '''
<h2>ویرایش {{field}}</h2>
<form method="POST">
    {% if field == 'profile_pic' %}
    <input type="file" name="profile_pic" accept="image/*">
    {% elif field == 'age' %}
    <select name="value">
        {% for i in range(12,81) %}
        <option value="{{i}}">{{i}}</option>
        {% endfor %}
    </select>
    {% elif field == 'gender' %}
    <select name="value">
        <option value="پسر">پسر</option>
        <option value="دختر">دختر</option>
        <option value="دیگر">دیگر</option>
    </select>
    {% elif field == 'city' %}
    <select name="value">
        {% for city in cities %}
        <option value="{{city}}">{{city}}</option>
        {% endfor %}
    </select>
    {% elif field == 'bio' or field == 'interests' %}
    <textarea name="value"></textarea>
    {% else %}
    <input type="text" name="value">
    {% endif %}
    <button type="submit">ذخیره</button>
</form>
'''

HOME_CONTENT = '''
<h2>خانه</h2>
<div class="filters">
    <button class="filter-btn {% if same_age %}active-filter{% endif %}" onclick="toggleFilter('same_age')">هم سن</button>
    <button class="filter-btn {% if same_gender %}active-filter{% endif %}" onclick="toggleFilter('same_gender')">هم جنسیت</button>
    <button class="filter-btn {% if opposite_gender %}active-filter{% endif %}" onclick="toggleFilter('opposite_gender')">ناهم جنسیت</button>
    <button class="filter-btn {% if same_city %}active-filter{% endif %}" onclick="toggleFilter('same_city')">هم شهر</button>
</div>
<div class="profiles">
    {% for profile in profiles %}
    <div class="card">
        <img src="{{profile.profile_pic_url}}" class="profile-pic" style="float: right;">
        <h3>{{profile.name}}</h3>
        <p>{{profile.username}}</p>
        <p>سن: {{profile.age}}</p>
        <p>جنسیت: {{profile.gender}}</p>
        <p>بیو: {{profile.bio}}</p>
        <p>شهر: {{profile.city}}</p>
        <span class="heart {% if profile.liked %}red-heart{% endif %}" onclick="toggleLike({{profile.id}})">{{ '❤️' if profile.liked else '♡' }}</span> {{profile.like_count}}
        <button onclick="requestChat({{profile.id}})">💬 چت</button>
    </div>
    {% endfor %}
</div>
<script>
    function toggleFilter(filter) {
        let url = new URL(window.location.href);
        if (url.searchParams.has(filter)) {
            url.searchParams.delete(filter);
        } else {
            url.searchParams.set(filter, '1');
        }
        window.location.href = url;
    }
    function toggleLike(userId) {
        fetch(`/like/${userId}`, {method: 'POST'}).then(() => location.reload());
    }
    function requestChat(userId) {
        fetch(`/request_chat/${userId}`, {method: 'POST'}).then(() => alert('درخواست ارسال شد'));
    }
</script>
'''

SEARCH_CONTENT = '''
<h2>جستجو</h2>
<form method="GET">
    <input type="text" name="q" placeholder="نام یا @نام کاربری">
    <button type="submit">🔍</button>
</form>
<div class="profiles">
    {% for profile in profiles %}
    <div class="card">
        <!-- similar to home card -->
        <img src="{{profile.profile_pic_url}}" class="profile-pic" style="float: right;">
        <h3>{{profile.name}}</h3>
        <p>{{profile.username}}</p>
        <p>سن: {{profile.age}}</p>
        <p>جنسیت: {{profile.gender}}</p>
        <p>بیو: {{profile.bio}}</p>
        <p>شهر: {{profile.city}}</p>
        <span class="heart {% if profile.liked %}red-heart{% endif %}" onclick="toggleLike({{profile.id}})">{{ '❤️' if profile.liked else '♡' }}</span> {{profile.like_count}}
        <button onclick="requestChat({{profile.id}})">💬 چت</button>
    </div>
    {% endfor %}
</div>
<script>
    // similar scripts
</script>
'''

NOTIFICATIONS_CONTENT = '''
<h2>اعلان‌ها</h2>
<div class="notifications-list">
    {% for notif in notifications %}
    <div class="card">
        <p>{{notif.content}}</p>
        <p>{{notif.timestamp}}</p>
        {% if notif.type == 'chat_request' %}
        <button onclick="acceptChat({{notif.from_user_id}})">✅ قبول</button>
        <button onclick="rejectChat({{notif.from_user_id}})">❌ رد</button>
        <button onclick="blockUser({{notif.from_user_id}})">🚫 بلاک</button>
        {% endif %}
    </div>
    {% endfor %}
</div>
<script>
    fetch('/mark_notifications_read', {method: 'POST'});
    function acceptChat(fromId) {
        fetch(`/accept_chat/${fromId}`, {method: 'POST'}).then(() => location.reload());
    }
    function rejectChat(fromId) {
        fetch(`/reject_chat/${fromId}`, {method: 'POST'}).then(() => location.reload());
    }
    function blockUser(fromId) {
        fetch(`/block/${fromId}`, {method: 'POST'}).then(() => location.reload());
    }
</script>
'''

CHAT_LIST_CONTENT = '''
<h2>چت‌ها</h2>
<div class="chat-list">
    {% for chat in chats %}
    <div class="card chat-list-item">
        <img src="{{chat.other_profile_pic}}" class="profile-pic">
        <div>
            <h3>{{chat.other_name}} ({{chat.other_username}})</h3>
            <p>آخرین پیام: {{chat.last_message}}</p>
            <p>{{chat.time}}</p>
        </div>
        <a href="/chat/{{chat.chat_id}}">ورود</a>
        <button onclick="deleteChat({{chat.chat_id}})">حذف</button>
    </div>
    {% endfor %}
</div>
<script>
    function deleteChat(chatId) {
        if (confirm('مطمئن هستید؟')) {
            fetch(`/delete_chat/${chatId}`, {method: 'POST'}).then(() => location.reload());
        }
    }
</script>
'''

CHAT_ROOM_HTML = '''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>چت - GOYIMIX</title>
    <style>''' + BASE_CSS + '''</style>
    <script src="/socket.io/socket.io.js"></script>
    <script>
        var socket = io();
        var chatId = {{chat_id}};
        socket.on('connect', function() {
            socket.emit('join_chat', {chat_id: chatId});
        });
        socket.on('new_message', function(data) {
            if (data.chat_id == chatId) {
                var msgDiv = document.createElement('div');
                msgDiv.className = data.sender_id == {{current_user_id}} ? 'my-message' : 'other-message';
                if (data.type == 'text') {
                    msgDiv.innerText = data.content;
                } else if (data.type == 'image') {
                    var img = document.createElement('img');
                    img.src = data.content;
                    msgDiv.appendChild(img);
                } // add for voice, sticker
                document.getElementById('messages').appendChild(msgDiv);
                document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;
            }
        });
        function sendMessage() {
            var content = document.getElementById('message_input').value;
            socket.emit('send_message', {chat_id: chatId, content: content, type: 'text'});
            document.getElementById('message_input').value = '';
        }
        // Add functions for image, voice, sticker upload
        function sendImage(event) {
            var file = event.target.files[0];
            var reader = new FileReader();
            reader.onload = function() {
                socket.emit('send_message', {chat_id: chatId, content: reader.result, type: 'image'});
            }
            reader.readAsDataURL(file);
        }
    </script>
</head>
<body>
    <div class="header">
        <a href="/chat">←</a>
        <img src="{{other_profile_pic}}" class="profile-pic small">
        <h3>{{other_name}} ({{other_username}})</h3>
    </div>
    <div class="chat-messages" id="messages">
        {% for msg in messages %}
        <div class="{{ 'my-message' if msg.sender_id == current_user_id else 'other-message' }}">
            {% if msg.type == 'text' %}
            {{msg.content}}
            {% elif msg.type == 'image' %}
            <img src="{{msg.content}}">
            {% endif %}
            <p>{{msg.timestamp}}</p>
        </div>
        {% endfor %}
    </div>
    <div class="chat-input">
        <input type="text" id="message_input" placeholder="پیام...">
        <button onclick="sendMessage()">ارسال</button>
        <input type="file" id="image_upload" accept="image/*" style="display:none;" onchange="sendImage(event)">
        <button onclick="document.getElementById('image_upload').click()">📷</button>
        <!-- add for voice 🎤, sticker 😀 -->
    </div>
</body>
</html>
'''

DELETE_ACCOUNT_HTML = '''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>حذف حساب - GOYIMIX</title>
    <style>''' + BASE_CSS + '''</style>
</head>
<body>
    <div class="container">
        <h2>آیا از حذف حساب مطمئن هستید؟</h2>
        <form method="POST">
            <input type="checkbox" name="confirm" id="confirm" required>
            <label for="confirm">تایید</label>
            <input type="password" name="password" placeholder="رمز عبور" required>
            <input type="password" name="confirm_password" placeholder="تکرار رمز عبور" required>
            <button type="submit" disabled id="delete_btn">حذف</button>
        </form>
        {% if error %}<p style="color: red;">{{error}}</p>{% endif %}
    </div>
    <script>
        document.getElementById('confirm').addEventListener('change', function() {
            document.getElementById('delete_btn').disabled = !this.checked;
        });
    </script>
</body>
</html>
'''

# Routes
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/', methods=['GET'])
def index():
    if get_current_user_id():
        return redirect('/home')
    return redirect('/register')

@app.route('/register', methods=['GET', 'POST'])
def register():
    cities = ["شهرک صدرا", "شهرک گلستان", "معالی آباد", "شهرک کشن", "شهرک مهدیه", "شهرک زینبیه", "شهرک بعثت", "شهرک والفجر", "شهرک صنعتی عفیف آباد", "کوی امام رضا", "شهرک گویم", "شهرک بزین", "شهرک رحمت آباد", "شهرک خورشید", "شهرک سلامت", "شهرک فرهنگیان", "کوی زاگرس", "کوی پاسداران", "شهرک عرفان", "شهرک هنرستان"]
    error = None
    if request.method == 'POST':
        data = request.form
        username = data['username']
        if not username.startswith('@'):
            username = '@' + username
        if data['password'] != data['confirm_password']:
            error = 'رمزها مطابقت ندارند'
        else:
            conn = sqlite3.connect('goyimix.db')
            c = conn.cursor()
            try:
                profile_pic = None
                if 'profile_pic' in request.files and request.files['profile_pic'].filename != '':
                    file = request.files['profile_pic']
                    filename = secure_filename(str(random.randint(0,1000000)) + '_' + file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    profile_pic = '/static/uploads/' + filename
                if not profile_pic:
                    if data['gender'] == 'پسر':
                        profile_pic = '/static/' + DEFAULT_MALE
                    elif data['gender'] == 'دختر':
                        profile_pic = '/static/' + DEFAULT_FEMALE
                    else:
                        profile_pic = '/static/' + DEFAULT_OTHER
                password_hash = hash_password(data['password'])
                c.execute('INSERT INTO users (username, name, password_hash, age, gender, bio, interests, city, profile_pic) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                          (username, data.get('name'), password_hash, int(data['age']), data['gender'], data.get('bio'), data.get('interests'), data['city'], profile_pic))
                conn.commit()
                user_id = c.lastrowid
                session['user_id'] = user_id
                # Notify matching users
                current_user = get_user_by_id(user_id)
                opposite = 'دختر' if current_user['gender'] == 'پسر' else 'پسر' if current_user['gender'] == 'دختر' else None
                if opposite:
                    c.execute('SELECT id FROM users WHERE age = ? AND city = ? AND gender = ? AND id != ?', (current_user['age'], current_user['city'], opposite, user_id))
                    matches = c.fetchall()
                    for m in matches:
                        notify(m[0], f'کاربر جدید {username} با سن و شهر شما ثبت‌نام کرد', 'new_user', user_id)
                conn.close()
                return redirect('/home')
            except sqlite3.IntegrityError:
                error = 'نام کاربری تکراری است'
            finally:
                conn.close()
    html = REGISTER_HTML.replace('{% for i in range(12, 81) %}', '').replace('{% endfor %}', '').replace('<option value="{{i}}">{{i}} سال</option>', ''.join(f'<option value="{i}">{i} سال</option>' for i in range(12,81)))
    html = html.replace('{% for city in cities %}', '').replace('{% endfor %}', '').replace('<option value="{{city}}">{{city}}</option>', ''.join(f'<option value="{c}">{c}</option>' for c in cities))
    if error:
        html = html.replace('{% if error %}<p style="color: red;">{{error}}</p>{% endif %}', f'<p style="color: red;">{error}</p>')
    else:
        html = html.replace('{% if error %}<p style="color: red;">{{error}}</p>{% endif %}', '')
    return html

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        data = request.form
        username_or_name = data['username_or_name']
        password_hash = hash_password(data['password'])
        conn = sqlite3.connect('goyimix.db')
        c = conn.cursor()
        c.execute('SELECT id, password_hash FROM users WHERE username = ? OR name = ?', (username_or_name, username_or_name))
        user = c.fetchone()
        conn.close()
        if user and user[1] == password_hash:
            session['user_id'] = user[0]
            return redirect('/home')
        error = 'نام کاربری یا رمز اشتباه است'
    html = LOGIN_HTML
    if error:
        html = html.replace('{% if error %}<p style="color: red;">{{error}}</p>{% endif %}', f'<p style="color: red;">{error}</p>')
    else:
        html = html.replace('{% if error %}<p style="color: red;">{{error}}</p>{% endif %}', '')
    return html

@app.route('/logout')
def logout():
    session.pop('user_id')
    return redirect('/login')

@app.route('/delete_account', methods=['GET', 'POST'])
def delete_account():
    if not get_current_user_id():
        return redirect('/login')
    error = None
    if request.method == 'POST':
        data = request.form
        if 'confirm' not in data:
            error = 'تایید لازم است'
        elif data['password'] != data['confirm_password']:
            error = 'رمزها مطابقت ندارند'
        else:
            password_hash = hash_password(data['password'])
            conn = sqlite3.connect('goyimix.db')
            c = conn.cursor()
            c.execute('SELECT password_hash FROM users WHERE id = ?', (get_current_user_id(),))
            user = c.fetchone()
            if user and user[0] == password_hash:
                user_id = get_current_user_id()
                c.execute('DELETE FROM users WHERE id = ?', (user_id,))
                c.execute('DELETE FROM likes WHERE liker_id = ? OR liked_id = ?', (user_id, user_id))
                c.execute('DELETE FROM chat_requests WHERE requester_id = ? OR target_id = ?', (user_id, user_id))
                c.execute('DELETE FROM chats WHERE user1_id = ? OR user2_id = ?', (user_id, user_id))
                c.execute('DELETE FROM messages WHERE sender_id = ?', (user_id,))
                c.execute('DELETE FROM notifications WHERE user_id = ? OR from_user_id = ?', (user_id, user_id))
                c.execute('DELETE FROM blocks WHERE blocker_id = ? OR blocked_id = ?', (user_id, user_id))
                conn.commit()
                conn.close()
                session.pop('user_id')
                return redirect('/register')
            else:
                error = 'رمز اشتباه است'
            conn.close()
    html = DELETE_ACCOUNT_HTML
    if error:
        html = html.replace('{% if error %}<p style="color: red;">{{error}}</p>{% endif %}', f'<p style="color: red;">{error}</p>')
    else:
        html = html.replace('{% if error %}<p style="color: red;">{{error}}</p>{% endif %}', '')
    return html

@app.route('/profile', methods=['GET'])
def profile():
    if not get_current_user_id():
        return redirect('/login')
    user = get_user_by_id(get_current_user_id())
    content = PROFILE_CONTENT.replace('{{profile_pic_url}}', user['profile_pic'])
    content = content.replace('{{name}}', user['name'] or '')
    content = content.replace('{{username}}', user['username'])
    content = content.replace('{{age}}', str(user['age']))
    content = content.replace('{{gender}}', user['gender'])
    content = content.replace('{{bio}}', user['bio'] or '')
    content = content.replace('{{interests}}', user['interests'] or '')
    content = content.replace('{{city}}', user['city'])
    content = content.replace('{{show_profile}}', '1' if user['show_profile'] else '0')
    # Password not shown, but for display, assume we don't store plain, but for this, skip real show
    content = content.replace('{{password}}', '******')  # Don't show real
    html = DASHBOARD_HTML.replace('{{content | safe}}', content)
    html = html.replace('{{active}}', 'profile')
    html = html.replace('{{has_unread}}', '1' if has_unread_notifications(get_current_user_id()) else '0')
    html = html.replace('{{current_user_id}}', str(get_current_user_id()))
    return html

@app.route('/edit/<field>', methods=['GET', 'POST'])
def edit_field(field):
    if not get_current_user_id():
        return redirect('/login')
    cities = ["شهرک صدرا", "شهرک گلستان", "معالی آباد", "شهرک کشن", "شهرک مهدیه", "شهرک زینبیه", "شهرک بعثت", "شهرک والفجر", "شهرک صنعتی عفیف آباد", "کوی امام رضا", "شهرک گویم", "شهرک بزین", "شهرک رحمت آباد", "شهرک خورشید", "شهرک سلامت", "شهرک فرهنگیان", "کوی زاگرس", "کوی پاسداران", "شهرک عرفان", "شهرک هنرستان"]
    if request.method == 'POST':
        value = request.form['value']
        if field == 'profile_pic':
            if 'profile_pic' in request.files:
                file = request.files['profile_pic']
                if file.filename != '':
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    value = '/static/uploads/' + filename
            field = 'profile_pic'
        elif field == 'username':
            if not value.startswith('@'):
                value = '@' + value
            conn = sqlite3.connect('goyimix.db')
            c = conn.cursor()
            try:
                c.execute('UPDATE users SET username = ? WHERE id = ?', (value, get_current_user_id()))
                conn.commit()
            except sqlite3.IntegrityError:
                return 'نام کاربری تکراری'
            conn.close()
            return redirect('/profile')
        elif field == 'age':
            value = int(value)
        # Update DB
        conn = sqlite3.connect('goyimix.db')
        c = conn.cursor()
        c.execute(f'UPDATE users SET {field} = ? WHERE id = ?', (value, get_current_user_id()))
        conn.commit()
        conn.close()
        return redirect('/profile')
    html = EDIT_FIELD_HTML.replace('{{field}}', field)
    if field == 'age':
        html = html.replace('{% for i in range(12,81) %}', '').replace('{% endfor %}', '').replace('<option value="{{i}}">{{i}}</option>', ''.join(f'<option value="{i}">{i}</option>' for i in range(12,81)))
    if field == 'city':
        html = html.replace('{% for city in cities %}', '').replace('{% endfor %}', '').replace('<option value="{{city}}">{{city}}</option>', ''.join(f'<option value="{c}">{c}</option>' for c in cities))
    return html

@app.route('/toggle_show_profile', methods=['POST'])
def toggle_show_profile():
    if not get_current_user_id():
        return jsonify({'error': 'unauthorized'}), 401
    data = request.json
    show = 1 if data['show'] else 0
    conn = sqlite3.connect('goyimix.db')
    c = conn.cursor()
    c.execute('UPDATE users SET show_profile = ? WHERE id = ?', (show, get_current_user_id()))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/home', methods=['GET'])
def home():
    if not get_current_user_id():
        return redirect('/login')
    current_user = get_user_by_id(get_current_user_id())
    same_age = 'same_age' in request.args
    same_gender = 'same_gender' in request.args
    opposite_gender = 'opposite_gender' in request.args
    same_city = 'same_city' in request.args
    conn = sqlite3.connect('goyimix.db')
    c = conn.cursor()
    query = 'SELECT * FROM users WHERE id != ? AND show_profile = 1'
    params = [get_current_user_id()]
    if same_age:
        query += ' AND age = ?'
        params.append(current_user['age'])
    if same_gender:
        query += ' AND gender = ?'
        params.append(current_user['gender'])
    if opposite_gender:
        opp = 'دختر' if current_user['gender'] == 'پسر' else 'پسر' if current_user['gender'] == 'دختر' else 'دیگر'
        query += ' AND gender = ?'
        params.append(opp)
    if same_city:
        query += ' AND city = ?'
        params.append(current_user['city'])
    c.execute(query, params)
    users = c.fetchall()
    conn.close()
    profiles = []
    for u in users:
        prof = {
            'id': u[0],
            'name': u[2] or '',
            'username': u[1],
            'age': u[4],
            'gender': u[5],
            'bio': u[6] or '',
            'city': u[8],
            'profile_pic_url': u[9],
            'liked': is_liked(get_current_user_id(), u[0]),
            'like_count': get_like_count(u[0])
        }
        profiles.append(prof)
    content = HOME_CONTENT.replace('{% if same_age %}active-filter{% endif %}', 'active-filter' if same_age else '')
    content = content.replace('{% if same_gender %}active-filter{% endif %}', 'active-filter' if same_gender else '')
    content = content.replace('{% if opposite_gender %}active-filter{% endif %}', 'active-filter' if opposite_gender else '')
    content = content.replace('{% if same_city %}active-filter{% endif %}', 'active-filter' if same_city else '')
    card_html = ''
    for p in profiles:
        card = '<div class="card"> <img src="{{profile_pic_url}}" class="profile-pic" style="float: right;"> <h3>{{name}}</h3> <p>{{username}}</p> <p>سن: {{age}}</p> <p>جنسیت: {{gender}}</p> <p>بیو: {{bio}}</p> <p>شهر: {{city}}</p> <span class="heart {{red if liked}} " onclick="toggleLike({{id}})">{{heart}}</span> {{like_count}} <button onclick="requestChat({{id}})">💬 چت</button> </div>'
        card = card.replace('{{profile_pic_url}}', p['profile_pic_url'])
        card = card.replace('{{name}}', p['name'])
        card = card.replace('{{username}}', p['username'])
        card = card.replace('{{age}}', str(p['age']))
        card = card.replace('{{gender}}', p['gender'])
        card = card.replace('{{bio}}', p['bio'])
        card = card.replace('{{city}}', p['city'])
        card = card.replace('{{red if liked}}', 'red-heart' if p['liked'] else '')
        card = card.replace('{{heart}}', '❤️' if p['liked'] else '♡')
        card = card.replace('{{like_count}}', str(p['like_count']))
        card = card.replace('{{id}}', str(p['id']))
        card_html += card
    content = content.replace('{% for profile in profiles %}', '').replace('{% endfor %}', '').replace('<div class="card">...</div>', card_html)
    html = DASHBOARD_HTML.replace('{{content | safe}}', content)
    html = html.replace('{{active}}', 'home')
    html = html.replace('{{has_unread}}', '1' if has_unread_notifications(get_current_user_id()) else '0')
    html = html.replace('{{current_user_id}}', str(get_current_user_id()))
    return html

@app.route('/like/<int:user_id>', methods=['POST'])
def like(user_id):
    if not get_current_user_id():
        return jsonify({'error': 'unauthorized'}), 401
    conn = sqlite3.connect('goyimix.db')
    c = conn.cursor()
    if is_liked(get_current_user_id(), user_id):
        c.execute('DELETE FROM likes WHERE liker_id = ? AND liked_id = ?', (get_current_user_id(), user_id))
        # Delete notification if exists
        c.execute('DELETE FROM notifications WHERE type = ? AND from_user_id = ? AND user_id = ?', ('like', get_current_user_id(), user_id))
    else:
        c.execute('INSERT OR IGNORE INTO likes (liker_id, liked_id) VALUES (?, ?)', (get_current_user_id(), user_id))
        current_username = get_user_by_id(get_current_user_id())['username']
        notify(user_id, f'کاربر {current_username} پروفایل شما را لایک کرد', 'like', get_current_user_id())
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/request_chat/<int:user_id>', methods=['POST'])
def request_chat(user_id):
    if not get_current_user_id():
        return jsonify({'error': 'unauthorized'}), 401
    if is_blocked(user_id, get_current_user_id()):
        return jsonify({'error': 'blocked'}), 403
    conn = sqlite3.connect('goyimix.db')
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO chat_requests (requester_id, target_id, status) VALUES (?, ?, ?)', (get_current_user_id(), user_id, 'pending'))
    conn.commit()
    conn.close()
    current_username = get_user_by_id(get_current_user_id())['username']
    notify(user_id, f'کاربر {current_username} درخواست چت داد', 'chat_request', get_current_user_id())
    return jsonify({'success': True})

@app.route('/accept_chat/<int:from_id>', methods=['POST'])
def accept_chat(from_id):
    if not get_current_user_id():
        return jsonify({'error': 'unauthorized'}), 401
    conn = sqlite3.connect('goyimix.db')
    c = conn.cursor()
    c.execute('UPDATE chat_requests SET status = ? WHERE requester_id = ? AND target_id = ?', ('accepted', from_id, get_current_user_id()))
    conn.commit()
    conn.close()
    chat_id = get_chat_id(get_current_user_id(), from_id)
    notify(from_id, 'درخواست چت شما پذیرفته شد', 'chat_accepted', get_current_user_id())
    return jsonify({'success': True})

@app.route('/reject_chat/<int:from_id>', methods=['POST'])
def reject_chat(from_id):
    if not get_current_user_id():
        return jsonify({'error': 'unauthorized'}), 401
    conn = sqlite3.connect('goyimix.db')
    c = conn.cursor()
    c.execute('UPDATE chat_requests SET status = ? WHERE requester_id = ? AND target_id = ?', ('rejected', from_id, get_current_user_id()))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/block/<int:user_id>', methods=['POST'])
def block(user_id):
    if not get_current_user_id():
        return jsonify({'error': 'unauthorized'}), 401
    conn = sqlite3.connect('goyimix.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO blocks (blocker_id, blocked_id) VALUES (?, ?)', (get_current_user_id(), user_id))
    c.execute('DELETE FROM chat_requests WHERE (requester_id = ? AND target_id = ?) OR (requester_id = ? AND target_id = ?)', (get_current_user_id(), user_id, user_id, get_current_user_id()))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/search', methods=['GET'])
def search():
    if not get_current_user_id():
        return redirect('/login')
    q = request.args.get('q', '')
    conn = sqlite3.connect('goyimix.db')
    c = conn.cursor()
    if q.startswith('@'):
        c.execute('SELECT * FROM users WHERE username LIKE ? AND show_profile = 1 AND id != ?', ('%' + q + '%', get_current_user_id()))
    else:
        c.execute('SELECT * FROM users WHERE name LIKE ? AND show_profile = 1 AND id != ?', ('%' + q + '%', get_current_user_id()))
    users = c.fetchall()
    conn.close()
    profiles = []  # similar to home
    for u in users:
        prof = {
            'id': u[0],
            'name': u[2] or '',
            'username': u[1],
            'age': u[4],
            'gender': u[5],
            'bio': u[6] or '',
            'city': u[8],
            'profile_pic_url': u[9],
            'liked': is_liked(get_current_user_id(), u[0]),
            'like_count': get_like_count(u[0])
        }
        profiles.append(prof)
    content = SEARCH_CONTENT
    card_html = ''
    for p in profiles:
        # same as home
        card = '<div class="card"> <img src="{{profile_pic_url}}" class="profile-pic" style="float: right;"> <h3>{{name}}</h3> <p>{{username}}</p> <p>سن: {{age}}</p> <p>جنسیت: {{gender}}</p> <p>بیو: {{bio}}</p> <p>شهر: {{city}}</p> <span class="heart {{red if liked}} " onclick="toggleLike({{id}})">{{heart}}</span> {{like_count}} <button onclick="requestChat({{id}})">💬 چت</button> </div>'
        card = card.replace('{{profile_pic_url}}', p['profile_pic_url'])
        card = card.replace('{{name}}', p['name'])
        card = card.replace('{{username}}', p['username'])
        card = card.replace('{{age}}', str(p['age']))
        card = card.replace('{{gender}}', p['gender'])
        card = card.replace('{{bio}}', p['bio'])
        card = card.replace('{{city}}', p['city'])
        card = card.replace('{{red if liked}}', 'red-heart' if p['liked'] else '')
        card = card.replace('{{heart}}', '❤️' if p['liked'] else '♡')
        card = card.replace('{{like_count}}', str(p['like_count']))
        card = card.replace('{{id}}', str(p['id']))
        card_html += card
    content = content.replace('{% for profile in profiles %}', '').replace('{% endfor %}', '').replace('<div class="card">...</div>', card_html)
    html = DASHBOARD_HTML.replace('{{content | safe}}', content)
    html = html.replace('{{active}}', 'search')
    html = html.replace('{{has_unread}}', '1' if has_unread_notifications(get_current_user_id()) else '0')
    html = html.replace('{{current_user_id}}', str(get_current_user_id()))
    return html

@app.route('/notifications', methods=['GET'])
def notifications():
    if not get_current_user_id():
        return redirect('/login')
    conn = sqlite3.connect('goyimix.db')
    c = conn.cursor()
    c.execute('SELECT * FROM notifications WHERE user_id = ? ORDER BY timestamp DESC', (get_current_user_id(),))
    notifs = c.fetchall()
    conn.close()
    notif_list = []
    for n in notifs:
        notif = {
            'id': n[0],
            'content': n[2],
            'type': n[3],
            'from_user_id': n[4],
            'timestamp': n[6]
        }
        notif_list.append(notif)
    content = NOTIFICATIONS_CONTENT
    card_html = ''
    for n in notif_list:
        card = '<div class="card"> <p>{{content}}</p> <p>{{timestamp}}</p> '
        if n['type'] == 'chat_request':
            card += '<button onclick="acceptChat({{from_user_id}})">✅ قبول</button> <button onclick="rejectChat({{from_user_id}})">❌ رد</button> <button onclick="blockUser({{from_user_id}})">🚫 بلاک</button>'
        card += '</div>'
        card = card.replace('{{content}}', n['content'])
        card = card.replace('{{timestamp}}', n['timestamp'])
        card = card.replace('{{from_user_id}}', str(n['from_user_id']))
        card_html += card
    content = content.replace('{% for notif in notifications %}', '').replace('{% endif %}', '').replace('{% endfor %}', '').replace('<div class="card">...</div>', card_html)
    html = DASHBOARD_HTML.replace('{{content | safe}}', content)
    html = html.replace('{{active}}', '')
    html = html.replace('{{has_unread}}', '1' if has_unread_notifications(get_current_user_id()) else '0')
    html = html.replace('{{current_user_id}}', str(get_current_user_id()))
    return html

@app.route('/mark_notifications_read', methods=['POST'])
def mark_notifications_read():
    if not get_current_user_id():
        return jsonify({'error': 'unauthorized'}), 401
    conn = sqlite3.connect('goyimix.db')
    c = conn.cursor()
    c.execute('UPDATE notifications SET read = 1 WHERE user_id = ?', (get_current_user_id(),))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/chat', methods=['GET'])
def chat_list():
    if not get_current_user_id():
        return redirect('/login')
    conn = sqlite3.connect('goyimix.db')
    c = conn.cursor()
    c.execute('SELECT * FROM chats WHERE user1_id = ? OR user2_id = ?', (get_current_user_id(), get_current_user_id()))
    chat_rows = c.fetchall()
    chats = []
    for row in chat_rows:
        chat_id = row[0]
        other_id = row[2] if row[1] == get_current_user_id() else row[1]
        other = get_user_by_id(other_id)
        c.execute('SELECT content, timestamp FROM messages WHERE chat_id = ? ORDER BY timestamp DESC LIMIT 1', (chat_id,))
        last_msg = c.fetchone()
        chats.append({
            'chat_id': chat_id,
            'other_name': other['name'],
            'other_username': other['username'],
            'other_profile_pic': other['profile_pic'],
            'last_message': last_msg[0] if last_msg else '',
            'time': last_msg[1] if last_msg else ''
        })
    conn.close()
    content = CHAT_LIST_CONTENT
    item_html = ''
    for ch in chats:
        item = '<div class="card chat-list-item"> <img src="{{other_profile_pic}}" class="profile-pic"> <div> <h3>{{other_name}} ({{other_username}})</h3> <p>آخرین پیام: {{last_message}}</p> <p>{{time}}</p> </div> <a href="/chat/{{chat_id}}">ورود</a> <button onclick="deleteChat({{chat_id}})">حذف</button> </div>'
        item = item.replace('{{other_profile_pic}}', ch['other_profile_pic'])
        item = item.replace('{{other_name}}', ch['other_name'])
        item = item.replace('{{other_username}}', ch['other_username'])
        item = item.replace('{{last_message}}', ch['last_message'])
        item = item.replace('{{time}}', ch['time'])
        item = item.replace('{{chat_id}}', str(ch['chat_id']))
        item_html += item
    content = content.replace('{% for chat in chats %}', '').replace('{% endfor %}', '').replace('<div class="card chat-list-item">...</div>', item_html)
    html = DASHBOARD_HTML.replace('{{content | safe}}', content)
    html = html.replace('{{active}}', 'chat')
    html = html.replace('{{has_unread}}', '1' if has_unread_notifications(get_current_user_id()) else '0')
    html = html.replace('{{current_user_id}}', str(get_current_user_id()))
    return html

@app.route('/chat/<int:chat_id>', methods=['GET'])
def chat_room(chat_id):
    if not get_current_user_id():
        return redirect('/login')
    conn = sqlite3.connect('goyimix.db')
    c = conn.cursor()
    c.execute('SELECT user1_id, user2_id FROM chats WHERE id = ?', (chat_id,))
    chat = c.fetchone()
    if not chat or (get_current_user_id() not in (chat[0], chat[1])):
        return 'Access denied', 403
    other_id = chat[1] if chat[0] == get_current_user_id() else chat[0]
    other = get_user_by_id(other_id)
    c.execute('SELECT sender_id, content, type, timestamp FROM messages WHERE chat_id = ? ORDER BY timestamp ASC', (chat_id,))
    msgs = c.fetchall()
    conn.close()
    messages = []
    for m in msgs:
        messages.append({
            'sender_id': m[0],
            'content': m[1],
            'type': m[2],
            'timestamp': m[3]
        })
    html = CHAT_ROOM_HTML.replace('{{chat_id}}', str(chat_id))
    html = html.replace('{{other_profile_pic}}', other['profile_pic'])
    html = html.replace('{{other_name}}', other['name'])
    html = html.replace('{{other_username}}', other['username'])
    html = html.replace('{{current_user_id}}', str(get_current_user_id()))
    msg_html = ''
    for msg in messages:
        cls = 'my-message' if msg['sender_id'] == get_current_user_id() else 'other-message'
        inner = msg['content'] if msg['type'] == 'text' else f'<img src="{msg["content"]}">' if msg['type'] == 'image' else ''
        msg_html += f'<div class="{cls}">{inner} <p>{msg["timestamp"]}</p></div>'
    html = html.replace('{% for msg in messages %}', '').replace('{% if msg.sender_id == current_user_id %}my-message{% else %}other-message{% endif %}', '').replace('{% if msg.type == "text" %}{{msg.content}}{% elif msg.type == "image" %}<img src="{{msg.content}}">{% endif %}', msg_html).replace('{% endfor %}', '')
    return html

@app.route('/delete_chat/<int:chat_id>', methods=['POST'])
def delete_chat(chat_id):
    if not get_current_user_id():
        return jsonify({'error': 'unauthorized'}), 401
    conn = sqlite3.connect('goyimix.db')
    c = conn.cursor()
    c.execute('DELETE FROM chats WHERE id = ?', (chat_id,))
    c.execute('DELETE FROM messages WHERE chat_id = ?', (chat_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# SocketIO events
@socketio.on('join_user')
def join_user(data):
    join_room(f'user_{data["user_id"]}')

@socketio.on('join_chat')
def join_chat(data):
    join_room(f'chat_{data["chat_id"]}')

@socketio.on('leave_chat')
def leave_chat(data):
    leave_room(f'chat_{data["chat_id"]}')

@socketio.on('send_message')
def send_message(data):
    chat_id = data['chat_id']
    sender_id = get_current_user_id()
    content = data['content']
    mtype = data['type']
    conn = sqlite3.connect('goyimix.db')
    c = conn.cursor()
    c.execute('INSERT INTO messages (chat_id, sender_id, content, type) VALUES (?, ?, ?, ?)', (chat_id, sender_id, content, mtype))
    conn.commit()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn.close()
    emit('new_message', {'chat_id': chat_id, 'sender_id': sender_id, 'content': content, 'type': mtype, 'timestamp': timestamp}, room=f'chat_{chat_id}')
    # Notify other user
    conn = sqlite3.connect('goyimix.db')
    c = conn.cursor()
    c.execute('SELECT user1_id, user2_id FROM chats WHERE id = ?', (chat_id,))
    chat = c.fetchone()
    other_id = chat[1] if chat[0] == sender_id else chat[0]
    conn.close()
    current_username = get_user_by_id(sender_id)['username']
    notify(other_id, f'پیام جدید از {current_username}', 'new_message', sender_id)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)