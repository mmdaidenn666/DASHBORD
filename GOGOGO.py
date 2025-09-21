from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify, flash
from flask_socketio import SocketIO, emit, join_room
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import json
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2')
app.config['SECRET_KEY'] = app.secret_key

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# ========== مدل‌های داده (برای نمونه — در پروژه واقعی از DB استفاده شود) ==========
users = {}  # {username: user_data}
notifications = {}  # {username: [notif1, notif2, ...]}
chats = {}  # {chat_id: {messages: [...], participants: [user1, user2]}}
user_chats = {}  # {username: [chat_id1, chat_id2, ...]}

CITIES = [
    "شهرک صدرا", "شهرک گلستان", "معالی آباد", "شهرک کشن", "شهرک مهدیه",
    "شهرک زینبیه", "شهرک بعثت", "شهرک والفجر", "شهرک صنعتی عفیف آباد",
    "کوی امام رضا", "شهرک گویم", "شهرک بزین", "شهرک رحمت آباد", "شهرک خورشید",
    "شهرک سلامت", "شهرک فرهنگیان", "کوی زاگرس", "کوی پاسداران", "شهرک عرفان",
    "شهرک هنرستان"
]

# ========== ابزارک‌ها ==========
def get_user(username):
    return users.get(username)

def create_chat_id(user1, user2):
    return "-".join(sorted([user1, user2]))

def add_notification(target_user, msg, type="info", from_user=None):
    notif = {
        "id": str(uuid.uuid4()),
        "msg": msg,
        "type": type,
        "from_user": from_user,
        "read": False
    }
    if target_user not in notifications:
        notifications[target_user] = []
    notifications[target_user].append(notif)
    # Emit to client if online
    socketio.emit('new_notification', notif, room=target_user)

# ========== BASE TEMPLATE ==========
BASE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}GOYIMIX | گویمیکس{% endblock %}</title>
    <style>
        :root {
            --bg: #121212;
            --primary-gradient: linear-gradient(135deg, #9B5DE5, #00F5D4);
            --pink-neon: #F15BB5;
            --white: #FFFFFF;
            --light-gray: #E0E0E0;
            --glow: 0 0 10px var(--pink-neon), 0 0 20px rgba(241, 91, 181, 0.5);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Vazirmatn', 'Segoe UI', sans-serif;
        }

        body {
            background-color: var(--bg);
            color: var(--white);
            min-height: 100vh;
            direction: rtl;
            padding-bottom: 70px;
        }

        h1, h2, h3, h4, h5 {
            font-weight: 700;
        }

        .btn, button, .glow-btn {
            background: var(--primary-gradient);
            border: none;
            color: white;
            padding: 12px 24px;
            border-radius: 50px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 0 5px rgba(155, 93, 229, 0.5);
        }

        .btn:hover, button:hover, .glow-btn:hover {
            box-shadow: var(--glow);
            transform: translateY(-2px);
        }

        input, select, textarea {
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            color: var(--white);
            padding: 12px;
            border-radius: 12px;
            width: 100%;
            margin: 8px 0;
            transition: all 0.3s;
        }

        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: var(--pink-neon);
            box-shadow: 0 0 8px rgba(241, 91, 181, 0.5);
        }

        .avatar {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            background: var(--primary-gradient);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 48px;
            cursor: pointer;
            margin: 20px auto;
            box-shadow: var(--glow);
            transition: all 0.3s;
        }

        .avatar:hover {
            transform: scale(1.05);
        }

        .card {
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 16px;
            margin: 12px 0;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            transition: all 0.3s;
        }

        .card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 16px rgba(0,0,0,0.4);
        }

        .filter-btn {
            background: rgba(255,255,255,0.1);
            border: 2px solid var(--light-gray);
            color: var(--light-gray);
            padding: 8px 16px;
            border-radius: 20px;
            margin: 4px;
            cursor: pointer;
            transition: all 0.3s;
        }

        .filter-btn.active {
            background: var(--primary-gradient);
            border-color: transparent;
            color: white;
            box-shadow: var(--glow);
        }

        .bottom-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            display: flex;
            justify-content: space-around;
            background: rgba(18,18,18,0.9);
            padding: 12px 0;
            backdrop-filter: blur(10px);
            z-index: 1000;
        }

        .bottom-nav a {
            display: flex;
            flex-direction: column;
            align-items: center;
            color: var(--light-gray);
            text-decoration: none;
            font-size: 10px;
            transition: all 0.3s;
        }

        .bottom-nav a.active {
            color: var(--white);
            font-weight: bold;
        }

        .bottom-nav a i {
            font-size: 24px;
            margin-bottom: 4px;
        }

        .notification-dot {
            position: absolute;
            top: -5px;
            right: -5px;
            width: 10px;
            height: 10px;
            background: red;
            border-radius: 50%;
        }

        .message {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 18px;
            margin: 8px 0;
            word-wrap: break-word;
        }

        .message.received {
            background: rgba(255,255,255,0.1);
            align-self: flex-start;
            border-bottom-left-radius: 4px;
        }

        .message.sent {
            background: var(--pink-neon);
            align-self: flex-end;
            border-bottom-right-radius: 4px;
            margin-left: auto;
        }

        .chat-container {
            display: flex;
            flex-direction: column;
            height: calc(100vh - 140px);
        }

        .messages-box {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            display: flex;
            flex-direction: column;
        }

        .message-input {
            display: flex;
            padding: 12px;
            background: rgba(0,0,0,0.3);
            border-top: 1px solid rgba(255,255,255,0.1);
        }

        .message-input input {
            flex: 1;
            background: rgba(255,255,255,0.1);
            border: none;
            color: white;
            padding: 12px;
            border-radius: 20px;
            margin-right: 8px;
        }

        .message-input button {
            padding: 12px 20px;
        }

        .password-container {
            position: relative;
        }

        .toggle-password {
            position: absolute;
            left: 12px;
            top: 50%;
            transform: translateY(-50%);
            background: none;
            border: none;
            color: var(--light-gray);
            cursor: pointer;
        }

        @media (max-width: 768px) {
            .container {
                padding: 16px;
            }
        }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.2/socket.io.min.js"></script>
</head>
<body>
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div style="background: {{ 'red' if category=='error' else '#00F5D4' }}; padding: 10px; text-align: center; margin: 10px;">
                    {{ message }}
                </div>
            {% endfor %}
        {% endif %}
    {% endwith %}

    <div class="container">
        {% block content %}{% endblock %}
    </div>

    {% if 'username' in session %}
    <div class="bottom-nav">
        <a href="{{ url_for('profile') }}" class="{% if request.endpoint == 'profile' %}active{% endif %}">
            <i class="fa fa-user"></i>
            <span>پروفایل</span>
        </a>
        <a href="{{ url_for('dashboard') }}" class="{% if request.endpoint == 'dashboard' %}active{% endif %}">
            <i class="fa fa-home"></i>
            <span>خانه</span>
        </a>
        <a href="{{ url_for('search') }}" class="{% if request.endpoint == 'search' %}active{% endif %}">
            <i class="fa fa-search"></i>
            <span>جستجو</span>
        </a>
        <a href="{{ url_for('view_notifications') }}" class="nav-bell {% if request.endpoint == 'view_notifications' %}active{% endif %}">
            <i class="fa fa-bell"></i>
            <span>اعلان‌ها</span>
            {% if notifications.get(session['username'], []) | selectattr('read', 'equalto', false) | list | length > 0 %}
                <div class="notification-dot" id="notification-dot"></div>
            {% endif %}
        </a>
    </div>
    {% endif %}

    <script>
        window.currentUser = "{{ session.username if 'username' in session else '' }}";
    </script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            if (Notification.permission !== "granted") {
                Notification.requestPermission();
            }

            const socket = io();

            socket.on('connect', function() {
                console.log('Connected to server');
            });

            socket.on('new_notification', function(notif) {
                showNotification(notif.msg);
                updateNotificationDot();
            });

            socket.on('receive_message', function(data) {
                if (window.currentChatId === data.chat_id) {
                    appendMessage(data.message);
                }
            });

            socket.on('like', function(data) {
            });

            socket.on('unlike', function(data) {
            });

            socket.on('chat_request_sent', function(data) {
                showToast("درخواست چت ارسال شد");
            });

            socket.on('chat_accepted', function(data) {
                if (window.location.pathname.includes('/chat/')) {
                    showToast("چت پذیرفته شد!");
                }
            });

            document.querySelectorAll('.btn-like').forEach(btn => {
                btn.addEventListener('click', function() {
                    const username = this.dataset.username;
                    socket.emit('like_user', {username: username});
                    const icon = this.querySelector('i');
                    if (icon.classList.contains('fa-heart')) {
                        icon.classList.remove('fa-heart');
                        icon.classList.add('fa-heart-o');
                    } else {
                        icon.classList.remove('fa-heart-o');
                        icon.classList.add('fa-heart');
                    }
                });
            });

            document.querySelectorAll('.btn-chat-request').forEach(btn => {
                btn.addEventListener('click', function() {
                    const username = this.dataset.username;
                    socket.emit('request_chat', {username: username});
                });
            });

            if (document.getElementById('message-form')) {
                const form = document.getElementById('message-form');
                form.addEventListener('submit', function(e) {
                    e.preventDefault();
                    const input = document.getElementById('message-input');
                    const text = input.value.trim();
                    if (text) {
                        const now = new Date();
                        const timeStr = `${now.getHours()}:${String(now.getMinutes()).padStart(2, '0')}`;
                        socket.emit('send_message', {
                            chat_id: window.currentChatId,
                            text: text,
                            timestamp: timeStr
                        });
                        input.value = '';
                    }
                });
            }

            const deleteChatBtn = document.getElementById('delete-chat-btn');
            if (deleteChatBtn) {
                deleteChatBtn.addEventListener('click', function() {
                    if (confirm("آیا مطمئنید می‌خواهید این چت را حذف کنید؟")) {
                        fetch(`/delete_chat/${window.currentChatId}`, {
                            method: 'POST'
                        })
                        .then(res => res.json())
                        .then(data => {
                            if (data.success) {
                                window.location.href = '/dashboard';
                            }
                        });
                    }
                });
            }

            document.querySelectorAll('.btn-accept').forEach(btn => {
                btn.addEventListener('click', function() {
                    const fromUser = this.dataset.from;
                    socket.emit('accept_chat', {from_user: fromUser});
                    this.closest('.card').remove();
                });
            });

            document.querySelectorAll('.btn-reject').forEach(btn => {
                btn.addEventListener('click', function() {
                    const fromUser = this.dataset.from;
                    socket.emit('reject_chat', {from_user: fromUser});
                    this.closest('.card').remove();
                });
            });

            document.querySelectorAll('.toggle-password').forEach(btn => {
                btn.addEventListener('click', function() {
                    const input = this.nextElementSibling;
                    if (input.type === 'password') {
                        input.type = 'text';
                        this.innerHTML = '🙈';
                    } else {
                        input.type = 'password';
                        this.innerHTML = '👁️';
                    }
                });
            });

            document.querySelectorAll('.filter-btn').forEach(btn => {
                btn.addEventListener('click', function() {
                    this.classList.toggle('active');
                    applyFilters();
                });
            });

            function applyFilters() {
                const filters = [];
                document.querySelectorAll('.filter-btn.active').forEach(btn => {
                    filters.push(btn.dataset.filter);
                });
                let url = '/home?';
                filters.forEach(f => {
                    url += `${f}=1&`;
                });
                window.location.href = url;
            }

            function showNotification(message) {
                if (Notification.permission === "granted") {
                    new Notification("GOYIMIX", {
                        body: message,
                        icon: "/static/favicon.ico"
                    });
                }
            }

            function updateNotificationDot() {
                fetch('/notifications')
                .then(res => res.text())
                .then(html => {
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, 'text/html');
                    const count = doc.querySelectorAll('.notification-item:not(.read)').length;
                    const dot = document.getElementById('notification-dot');
                    if (count > 0) {
                        if (!dot) {
                            const bell = document.querySelector('.nav-bell');
                            const newDot = document.createElement('div');
                            newDot.id = 'notification-dot';
                            newDot.className = 'notification-dot';
                            bell.appendChild(newDot);
                        }
                    } else if (dot) {
                        dot.remove();
                    }
                });
            }

            function showToast(message) {
                const toast = document.createElement('div');
                toast.className = 'toast';
                toast.textContent = message;
                document.body.appendChild(toast);
                setTimeout(() => {
                    toast.remove();
                }, 3000);
            }

            function appendMessage(msg) {
                const box = document.querySelector('.messages-box');
                const div = document.createElement('div');
                div.className = `message ${msg.from === window.currentUser ? 'sent' : 'received'}`;
                div.textContent = msg.text;
                box.appendChild(div);
                box.scrollTop = box.scrollHeight;
            }
        });
    </script>
    {% block scripts %}{% endblock %}
</body>
</html>
'''

# ========== REGISTER TEMPLATE ==========
REGISTER_TEMPLATE = '''
{% extends "base.html" %}
{% block content %}
<div style="text-align: center; padding: 20px;">
    <h2>خوش آمدید به گویمیکس | GOYIMIX</h2>
    <div class="avatar" id="avatar-preview" onclick="document.getElementById('avatar-input').click()">
        🧑‍💼
    </div>
    <input type="file" id="avatar-input" accept="image/*" style="display:none" onchange="previewAvatar(event)">
    
    <form id="register-form">
        <input type="text" name="name" placeholder="نام (اختیاری)">
        <input type="text" name="username" placeholder="@نام کاربری" required>
        <select name="age" required>
            {% for i in range(12, 81) %}
                <option value="{{ i }}">{{ i }} سال</option>
            {% endfor %}
        </select>
        <select name="gender" required>
            <option value="پسر">پسر</option>
            <option value="دختر">دختر</option>
            <option value="دیگر">دیگر</option>
        </select>
        <textarea name="bio" placeholder="بیو (اختیاری)"></textarea>
        <input type="text" name="interests" placeholder="علاقه‌مندی‌ها (اختیاری)">
        <select name="city" required>
            {% for city in cities %}
                <option value="{{ city }}">{{ city }}</option>
            {% endfor %}
        </select>
        <input type="password" name="password" placeholder="رمز عبور" required>
        <input type="password" name="confirm_password" placeholder="تکرار رمز عبور" required>
        <button type="submit" class="btn">ثبت‌نام</button>
    </form>
    <p style="margin-top: 20px;">حساب دارید؟ <a href="{{ url_for('login') }}">وارد شوید</a></p>
</div>

<script>
document.getElementById('register-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    const data = Object.fromEntries(formData);
    if (data.password !== data.confirm_password) {
        alert("رمز عبور و تکرار آن مطابقت ندارند");
        return;
    }
    const res = await fetch('/register', {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {'Content-Type': 'application/json'}
    });
    const result = await res.json();
    if (result.error) {
        alert(result.error);
    } else {
        alert(result.message);
        window.location.href = '/dashboard';
    }
});

function previewAvatar(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('avatar-preview').innerHTML = `<img src="${e.target.result}" style="width:100%;height:100%;border-radius:50%">`;
        }
        reader.readAsDataURL(file);
    }
}
</script>
{% endblock %}
'''

# ========== LOGIN TEMPLATE ==========
LOGIN_TEMPLATE = '''
{% extends "base.html" %}
{% block content %}
<div style="text-align: center; padding: 40px 20px;">
    <h2>دوباره خوش آمدید</h2>
    <form method="POST" style="max-width: 400px; margin: 0 auto;">
        <input type="text" name="identifier" placeholder="نام کاربری یا نام" required>
        <input type="password" name="password" placeholder="رمز عبور" required>
        <button type="submit" class="btn">ورود</button>
    </form>
    <p style="margin-top: 20px;">اگر حسابی ندارید؟ <a href="{{ url_for('register') }}">ثبت‌نام کنید</a></p>
</div>
{% endblock %}
'''

# ========== DASHBOARD TEMPLATE ==========
DASHBOARD_TEMPLATE = '''
{% extends "base.html" %}
{% block content %}
<div style="text-align: center; padding: 40px 20px;">
    <h2>داشبورد</h2>
    <p>خوش آمدید، {{ user.name or user.username }}!</p>
    <a href="{{ url_for('home') }}" class="btn" style="display: inline-block; margin-top: 20px;">رفتن به خانه</a>
</div>
{% endblock %}
'''

# ========== PROFILE TEMPLATE ==========
PROFILE_TEMPLATE = '''
{% extends "base.html" %}
{% block content %}
<div style="padding: 20px;">
    <h2>پروفایل شما</h2>
    <div style="text-align: center; margin: 20px 0;">
        <div class="avatar">{{ user.avatar }}</div>
    </div>

    <div class="card">
        <p><strong>نام:</strong> {{ user.name or "—" }} <span style="float: left; cursor: pointer;" onclick="editField('name', '{{ user.name or '' }}')">✏️</span></p>
        <p><strong>نام کاربری:</strong> @{{ user.username }} <span style="float: left; cursor: pointer;" onclick="editField('username', '{{ user.username }}')">✏️</span></p>
        <p><strong>سن:</strong> {{ user.age }} <span style="float: left; cursor: pointer;" onclick="editField('age', '{{ user.age }}')">✏️</span></p>
        <p><strong>جنسیت:</strong> {{ user.gender }} <span style="float: left; cursor: pointer;" onclick="editField('gender', '{{ user.gender }}')">✏️</span></p>
        <p><strong>بیو:</strong> {{ user.bio or "—" }} <span style="float: left; cursor: pointer;" onclick="editField('bio', '{{ user.bio or '' }}')">✏️</span></p>
        <p><strong>شهر:</strong> {{ user.city }} <span style="float: left; cursor: pointer;" onclick="editField('city', '{{ user.city }}')">✏️</span></p>
        <div class="password-container">
            <strong>رمز عبور:</strong> ●●●●●●
            <button type="button" class="toggle-password">👁️</button>
            <input type="password" id="password-field" value="●●●●●●" disabled style="margin-right: 40px; width: 200px;">
            <span style="float: left; cursor: pointer;" onclick="editField('password', '')">✏️</span>
        </div>
    </div>

    <div style="margin: 20px 0; text-align: center;">
        <label style="display: block; margin-bottom: 10px;">نمایش پروفایل در خانه</label>
        <label class="switch">
            <input type="checkbox" id="show-profile-toggle" {{ "checked" if user.show_in_home else "" }} onchange="toggleShowInHome()">
            <span class="slider"></span>
        </label>
    </div>

    <div style="text-align: center; margin: 30px 0;">
        <button class="btn" style="margin: 5px;" onclick="logout()">خروج از حساب</button>
        <button class="btn" style="margin: 5px; background: red;" onclick="deleteAccount()">حذف حساب</button>
    </div>
</div>

<script>
function editField(field, currentValue) {
    let newValue;
    if (field === 'password') {
        const oldPass = prompt("رمز فعلی خود را وارد کنید:");
        if (!oldPass) return;
        newValue = prompt("رمز جدید را وارد کنید:");
        if (!newValue) return;
        fetch('/profile', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({field: field, value: newValue, old_password: oldPass})
        })
        .then(r => r.json())
        .then(d => {
            if (d.success) {
                alert("با موفقیت به‌روز شد");
                location.reload();
            } else {
                alert(d.error);
            }
        });
    } else if (field === 'age') {
        newValue = prompt("سن جدید:", currentValue);
        if (newValue && !isNaN(newValue)) {
            saveField(field, newValue);
        }
    } else if (field === 'gender') {
        newValue = prompt("جنسیت جدید (پسر/دختر/دیگر):", currentValue);
        if (newValue) saveField(field, newValue);
    } else {
        newValue = prompt(`مقدار جدید برای ${field}:`, currentValue);
        if (newValue !== null) saveField(field, newValue);
    }
}

function saveField(field, value) {
    fetch('/profile', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({field: field, value: value})
    })
    .then(r => r.json())
    .then(d => {
        if (d.success) {
            alert("با موفقیت به‌روز شد");
            location.reload();
        } else {
            alert(d.error);
        }
    });
}

function toggleShowInHome() {
    const val = document.getElementById('show-profile-toggle').checked;
    saveField('show_in_home', val);
}

function logout() {
    fetch('/logout', {method: 'GET'}).then(() => window.location.href = '/login');
}

function deleteAccount() {
    if (!confirm("آیا مطمئنید؟ این عمل غیرقابل بازگشت است!")) return;
    const pass = prompt("رمز عبور خود را برای تأیید وارد کنید:");
    if (!pass) return;
    fetch('/delete_account', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({password: pass})
    })
    .then(r => r.json())
    .then(d => {
        if (d.success) {
            alert("حساب شما حذف شد.");
            window.location.href = '/register';
        } else {
            alert(d.error);
        }
    });
}
</script>
{% endblock %}
'''

# ========== HOME TEMPLATE ==========
HOME_TEMPLATE = '''
{% extends "base.html" %}
{% block content %}
<div style="padding: 20px;">
    <h2>خانه</h2>
    <div style="margin: 20px 0; display: flex; flex-wrap: wrap; gap: 8px;">
        <button class="filter-btn {% if request.args.same_age %}active{% endif %}" data-filter="same_age">هم‌سن</button>
        <button class="filter-btn {% if request.args.same_gender %}active{% endif %}" data-filter="same_gender">هم‌جنسیت</button>
        <button class="filter-btn {% if request.args.opposite_gender %}active{% endif %}" data-filter="opposite_gender">ناهم‌جنسیت</button>
        <button class="filter-btn {% if request.args.same_city %}active{% endif %}" data-filter="same_city">هم‌شهر</button>
    </div>

    {% if users %}
        {% for u in users %}
        <div class="card" style="display: flex; align-items: center; gap: 16px;">
            <div style="font-size: 32px;">{{ u.avatar }}</div>
            <div style="flex: 1;">
                <h3>{{ u.name or u.username }}</h3>
                <p>@{{ u.username }} • {{ u.age }} سال • {{ u.gender }}</p>
                <p>{{ u.bio or "" }}</p>
                <p>📍 {{ u.city }}</p>
            </div>
            <div style="text-align: center;">
                <button class="btn btn-like" data-username="{{ u.username }}">
                    <i class="fa fa-heart-o"></i>
                </button>
                <button class="btn btn-chat-request" data-username="{{ u.username }}" style="margin-top: 8px;">
                    💬 چت
                </button>
            </div>
        </div>
        {% endfor %}
    {% else %}
        <p>کاربری یافت نشد.</p>
    {% endif %}
</div>
{% endblock %}
'''

# ========== NOTIFICATIONS TEMPLATE ==========
NOTIFICATIONS_TEMPLATE = '''
{% extends "base.html" %}
{% block content %}
<div style="padding: 20px;">
    <h2>اعلان‌ها</h2>
    {% if notifications %}
        {% for notif in notifications %}
        <div class="card notification-item {% if notif.read %}read{% endif %}">
            <p>{{ notif.msg }}</p>
            {% if notif.type == 'chat_request' %}
                <div style="margin-top: 10px;">
                    <button class="btn btn-accept" data-from="{{ notif.from_user }}">✅ قبول</button>
                    <button class="btn" style="background: gray;" data-from="{{ notif.from_user }}">❌ رد</button>
                    <button class="btn" style="background: red; margin-right: 5px;" data-from="{{ notif.from_user }}">🚫 بلاک</button>
                </div>
            {% endif %}
        </div>
        {% endfor %}
    {% else %}
        <p>اعلانی وجود ندارد.</p>
    {% endif %}
</div>
{% endblock %}
'''

# ========== SEARCH TEMPLATE ==========
SEARCH_TEMPLATE = '''
{% extends "base.html" %}
{% block content %}
<div style="padding: 20px;">
    <h2>جستجو</h2>
    <form method="GET" style="margin: 20px 0;">
        <input type="text" name="q" placeholder="جستجو بر اساس نام یا @نام کاربری" value="{{ query }}" style="width: 80%;">
        <button type="submit" style="width: 18%; padding: 12px; background: var(--primary-gradient); color: white; border: none; border-radius: 12px;">🔍</button>
    </form>

    {% if results %}
        <h3>نتایج:</h3>
        {% for u in results %}
        <div class="card" style="display: flex; align-items: center; gap: 16px;">
            <div style="font-size: 32px;">{{ u.avatar }}</div>
            <div style="flex: 1;">
                <h3>{{ u.name or u.username }}</h3>
                <p>@{{ u.username }} • {{ u.age }} سال • {{ u.gender }}</p>
                <p>{{ u.bio or "" }}</p>
                <p>📍 {{ u.city }}</p>
            </div>
            <div>
                <button class="btn btn-like" data-username="{{ u.username }}">
                    <i class="fa fa-heart-o"></i>
                </button>
                <a href="{{ url_for('chat_page', username=u.username) }}" class="btn" style="margin-top: 8px;">💬 چت</a>
            </div>
        </div>
        {% endfor %}
    {% elif query %}
        <p>کاربری یافت نشد.</p>
    {% endif %}
</div>
{% endblock %}
'''

# ========== CHAT TEMPLATE ==========
CHAT_TEMPLATE = '''
{% extends "base.html" %}
{% block content %}
<div style="padding: 20px; display: flex; flex-direction: column; height: 100vh;">
    <div style="display: flex; align-items: center; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
        <button onclick="window.history.back()" style="background: none; border: none; color: white; font-size: 24px;">←</button>
        <div style="margin: 0 10px; display: flex; align-items: center; gap: 10px;">
            <div style="font-size: 32px;">{{ target_user.avatar }}</div>
            <div>
                <h3>{{ target_user.name or target_user.username }}</h3>
                <p>@{{ target_user.username }}</p>
            </div>
        </div>
        <button id="delete-chat-btn" style="margin-right: auto; background: red; color: white; border: none; padding: 8px 16px; border-radius: 8px;">🗑️ حذف چت</button>
    </div>

    <div class="messages-box" id="messages-box">
        {% if chat_id in chats %}
            {% for msg in chats[chat_id].messages %}
            <div class="message {{ 'sent' if msg.from == session.username else 'received' }}">
                {{ msg.text }}
            </div>
            {% endfor %}
        {% endif %}
    </div>

    <form id="message-form" class="message-input">
        <input type="text" id="message-input" placeholder="پیام خود را بنویسید...">
        <button type="submit">ارسال</button>
    </form>
</div>

<script>
    window.currentChatId = "{{ chat_id }}";
</script>
{% endblock %}
'''

# ========== Routes ==========
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form['identifier']
        password = request.form['password']
        for username, user in users.items():
            if (username == identifier or user.get('name') == identifier) and check_password_hash(user['password'], password):
                session['username'] = username
                return redirect(url_for('dashboard'))
        flash("نام کاربری یا رمز اشتباه است", "error")
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data['username']
        if username in users:
            return jsonify({"error": "این نام کاربری قبلاً استفاده شده"}), 400
        password = generate_password_hash(data['password'])
        gender = data['gender']
        default_avatar = "🧑‍💼" if gender == "پسر" else "🧕"
        avatar = data.get('avatar', default_avatar)
        user = {
            "name": data.get('name', ''),
            "username": username,
            "age": int(data['age']),
            "gender": gender,
            "bio": data.get('bio', ''),
            "interests": data.get('interests', ''),
            "city": data['city'],
            "password": password,
            "avatar": avatar,
            "show_in_home": True
        }
        users[username] = user
        session['username'] = username
        return jsonify({"success": True, "message": "🎉 خوش آمدید به گویمیکس"})
    return render_template_string(REGISTER_TEMPLATE, cities=CITIES)

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template_string(DASHBOARD_TEMPLATE, user=users[session['username']])

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    user = users[username]
    if request.method == 'POST':
        data = request.get_json()
        field = data['field']
        value = data['value']
        if field == "password":
            if not check_password_hash(user['password'], data['old_password']):
                return jsonify({"error": "رمز فعلی اشتباه است"}), 400
            user['password'] = generate_password_hash(value)
        elif field == "show_in_home":
            user['show_in_home'] = value
        else:
            user[field] = value
        return jsonify({"success": True})
    return render_template_string(PROFILE_TEMPLATE, user=user)

@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    current_user = users[session['username']]
    same_age = request.args.get('same_age') == '1'
    same_gender = request.args.get('same_gender') == '1'
    opposite_gender = request.args.get('opposite_gender') == '1'
    same_city = request.args.get('same_city') == '1'

    filtered_users = []
    for u in users.values():
        if u['username'] == current_user['username']: continue
        if not u.get('show_in_home', True): continue
        if same_age and u['age'] != current_user['age']: continue
        if same_gender and u['gender'] != current_user['gender']: continue
        if opposite_gender and u['gender'] == current_user['gender']: continue
        if same_city and u['city'] != current_user['city']: continue
        filtered_users.append(u)
    return render_template_string(HOME_TEMPLATE, users=filtered_users, current_user=current_user)

@app.route('/notifications')
def view_notifications():
    if 'username' not in session:
        return redirect(url_for('login'))
    user_notifs = notifications.get(session['username'], [])
    for n in user_notifs:
        n['read'] = True
    return render_template_string(NOTIFICATIONS_TEMPLATE, notifications=user_notifs)

@app.route('/search')
def search():
    if 'username' not in session:
        return redirect(url_for('login'))
    query = request.args.get('q', '').strip()
    results = []
    if query:
        if query.startswith('@'):
            username = query[1:]
            if username in users:
                results.append(users[username])
        else:
            for u in users.values():
                if query.lower() in u.get('name', '').lower():
                    results.append(u)
    return render_template_string(SEARCH_TEMPLATE, results=results, query=query)

@app.route('/chat/<username>')
def chat_page(username):
    if 'username' not in session:
        return redirect(url_for('login'))
    if username not in users:
        return "کاربر یافت نشد", 404
    current_user = session['username']
    chat_id = create_chat_id(current_user, username)
    if chat_id not in chats:
        chats[chat_id] = {"messages": [], "participants": [current_user, username]}
    if current_user not in user_chats:
        user_chats[current_user] = []
    if chat_id not in user_chats[current_user]:
        user_chats[current_user].append(chat_id)
    return render_template_string(CHAT_TEMPLATE, target_user=users[username], chat_id=chat_id)

@app.route('/delete_chat/<chat_id>', methods=['POST'])
def delete_chat(chat_id):
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    username = session['username']
    if chat_id in user_chats.get(username, []):
        user_chats[username].remove(chat_id)
        return jsonify({"success": True})
    return jsonify({"error": "Chat not found"}), 404

@app.route('/delete_account', methods=['POST'])
def delete_account():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    username = session['username']
    data = request.get_json()
    if not check_password_hash(users[username]['password'], data['password']):
        return jsonify({"error": "رمز عبور اشتباه است"}), 400
    del users[username]
    if username in notifications:
        del notifications[username]
    if username in user_chats:
        for chat_id in user_chats[username][:]:
            if chat_id in chats:
                del chats[chat_id]
        del user_chats[username]
    session.pop('username', None)
    return jsonify({"success": True})

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# ========== Socket.IO ==========
@socketio.on('connect')
def handle_connect():
    if 'username' in session:
        join_room(session['username'])

@socketio.on('send_message')
def handle_message(data):
    chat_id = data['chat_id']
    message = {
        "id": str(uuid.uuid4()),
        "from": session['username'],
        "text": data['text'],
        "timestamp": data.get('timestamp', "الان")
    }
    if chat_id in chats:
        chats[chat_id]['messages'].append(message)
        for user in chats[chat_id]['participants']:
            emit('receive_message', {"chat_id": chat_id, "message": message}, room=user)

@socketio.on('like_user')
def handle_like(data):
    target_user = data['username']
    from_user = session['username']
    key = f"like_{from_user}_{target_user}"
    if not hasattr(app, 'likes'):
        app.likes = {}
    if key in app.likes:
        del app.likes[key]
        if target_user in notifications:
            notifications[target_user] = [n for n in notifications[target_user] if not (n.get('from_user') == from_user and n['type'] == 'like')]
        emit('unlike', {"target": target_user}, room=from_user)
    else:
        app.likes[key] = True
        msg = f"کاربر @{from_user} شما را لایک کرد"
        add_notification(target_user, msg, "like", from_user)
        emit('like', {"target": target_user}, room=from_user)

@socketio.on('request_chat')
def handle_chat_request(data):
    target_user = data['username']
    from_user = session['username']
    msg = f"کاربر @{from_user} درخواست چت داده"
    add_notification(target_user, msg, "chat_request", from_user)
    emit('chat_request_sent', {"target": target_user}, room=from_user)

@socketio.on('accept_chat')
def handle_accept_chat(data):
    requester = data['from_user']
    accepter = session['username']
    chat_id = create_chat_id(requester, accepter)
    if chat_id not in chats:
        chats[chat_id] = {"messages": [], "participants": [requester, accepter]}
    for user in [requester, accepter]:
        if user not in user_chats:
            user_chats[user] = []
        if chat_id not in user_chats[user]:
            user_chats[user].append(chat_id)
    if accepter in notifications:
        notifications[accepter] = [n for n in notifications[accepter] if not (n.get('from_user') == requester and n['type'] == 'chat_request')]
    emit('chat_accepted', {"chat_id": chat_id}, room=requester)
    emit('chat_accepted', {"chat_id": chat_id}, room=accepter)

@socketio.on('reject_chat')
def handle_reject_chat(data):
    requester = data['from_user']
    rejecter = session['username']
    if rejecter in notifications:
        notifications[rejecter] = [n for n in notifications[rejecter] if not (n.get('from_user') == requester and n['type'] == 'chat_request')]
    emit('chat_rejected', {}, room=requester)

@app.route('/api/chats')
def get_chats():
    if 'username' not in session:
        return jsonify([]), 401
    username = session['username']
    chat_list = []
    for chat_id in user_chats.get(username, []):
        if chat_id in chats:
            other_user = [u for u in chats[chat_id]['participants'] if u != username][0]
            last_msg = chats[chat_id]['messages'][-1] if chats[chat_id]['messages'] else None
            chat_list.append({
                "chat_id": chat_id,
                "other_user": users[other_user],
                "last_message": last_msg['text'] if last_msg else "",
                "timestamp": last_msg['timestamp'] if last_msg else ""
            })
    return jsonify(chat_list)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)