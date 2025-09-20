from flask import Flask, render_template_string, request, redirect, url_for, flash, session, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import uuid

# ایجاد اپ Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///goyimix.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# ایجاد پوشه‌ها اگر وجود نداشته باشند
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ابزارها
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# لیست شهرها
CITIES = [
    "شهرک صدرا", "شهرک گلستان", "معالی آباد", "شهرک کشن", "شهرک مهدیه",
    "شهرک زینبیه", "شهرک بعثت", "شهرک والفجر", "شهرک صنعتی عفیف آباد",
    "کوی امام رضا", "شهرک گویم", "شهرک بزین", "شهرک رحمت آباد", "شهرک خورشید",
    "شهرک سلامت", "شهرک فرهنگیان", "کوی زاگرس", "کوی پاسداران", "شهرک عرفان",
    "شهرک هنرستان"
]

# مدل‌ها
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    name = db.Column(db.String(150))
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    bio = db.Column(db.Text)
    interests = db.Column(db.Text)
    city = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    profile_pic = db.Column(db.String(200), default='default.png')
    show_in_home = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    partner_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Chat {self.id}>'

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    sender_id = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='text')  # text, image, video, voice, file
    file_path = db.Column(db.String(200))
    is_read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Message {self.id}>'

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    sender_id = db.Column(db.Integer)  # کاربری که اعلان را ایجاد کرده
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # like, chat_request, message, block, unblock
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Notification {self.id}>'

class Block(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blocker_id = db.Column(db.Integer, nullable=False)
    blocked_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Block {self.id}>'

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    liked_user_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Like {self.id}>'

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except:
        return None

# استایل CSS مشترک
CSS_STYLE = '''
<style>
/* استایل کلی */
:root {
    --bg-dark: #121212;
    --primary-gradient: linear-gradient(90deg, #9B5DE5, #00F5D4);
    --neon-pink: #F15BB5;
    --white: #FFFFFF;
    --light-gray: #E0E0E0;
    --card-bg: #1e1e1e;
    --neon-blue: #00F5D4;
    --neon-purple: #9B5DE5;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    background-color: var(--bg-dark);
    color: var(--white);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    direction: rtl;
    text-align: right;
    padding: 20px;
    min-height: 100vh;
    padding-bottom: 80px;
}

/* لینک‌ها */
a {
    color: var(--neon-blue);
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

/* فرم‌ها */
form {
    max-width: 500px;
    margin: 0 auto;
}

input, select, textarea {
    width: 100%;
    padding: 12px;
    margin: 10px 0;
    border-radius: 10px;
    border: 2px solid transparent;
    background: var(--card-bg);
    color: var(--white);
    font-size: 16px;
}

input:focus, select:focus, textarea:focus {
    outline: none;
    border-color: var(--neon-purple);
    box-shadow: 0 0 10px var(--neon-purple);
}

button {
    background: var(--primary-gradient);
    color: #000;
    border: none;
    padding: 12px 24px;
    border-radius: 10px;
    font-weight: bold;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.3s ease;
    margin: 10px 0;
    box-shadow: 0 0 15px rgba(155, 93, 229, 0.5);
}

button:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 20px rgba(155, 93, 229, 0.8);
}

/* پیام‌ها */
.flash-messages {
    margin: 20px 0;
}

.success {
    color: var(--neon-blue);
    background: rgba(0, 245, 212, 0.1);
    padding: 10px;
    border-radius: 5px;
    border-left: 4px solid var(--neon-blue);
}

.error {
    color: var(--neon-pink);
    background: rgba(241, 91, 181, 0.1);
    padding: 10px;
    border-radius: 5px;
    border-left: 4px solid var(--neon-pink);
}

.info {
    color: var(--light-gray);
    background: rgba(224, 224, 224, 0.1);
    padding: 10px;
    border-radius: 5px;
    border-left: 4px solid var(--light-gray);
}

/* کارت‌ها */
.profile-card {
    background: var(--card-bg);
    border-radius: 15px;
    padding: 20px;
    margin: 15px 0;
    display: flex;
    align-items: center;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
    transition: transform 0.3s ease;
    border: 1px solid transparent;
}

.profile-card:hover {
    transform: translateY(-5px);
    border: 1px solid var(--neon-purple);
}

.profile-card img {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    object-fit: cover;
    margin-left: 15px;
    border: 2px solid var(--neon-purple);
}

.profile-info {
    flex: 1;
}

.profile-info h3 {
    margin: 0 0 5px 0;
    color: var(--neon-blue);
}

.profile-info p {
    margin: 2px 0;
    color: var(--light-gray);
    font-size: 14px;
}

.profile-actions {
    display: flex;
    gap: 10px;
}

.profile-actions button {
    padding: 8px 15px;
    font-size: 14px;
    border-radius: 8px;
}

/* نوار پایین */
.bottom-nav {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: var(--card-bg);
    display: flex;
    justify-content: space-around;
    padding: 15px 0;
    border-top: 1px solid #333;
    z-index: 1000;
}

.nav-item {
    text-align: center;
    color: var(--light-gray);
    text-decoration: none;
    font-size: 12px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 5px;
}

.nav-item.active {
    color: var(--neon-blue);
}

.nav-item i {
    font-size: 20px;
}

/* فیلترها */
.filters {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin: 20px 0;
    justify-content: center;
}

.filter-btn {
    background: var(--card-bg);
    color: var(--light-gray);
    border: 1px solid #333;
    padding: 8px 15px;
    border-radius: 20px;
    cursor: pointer;
    transition: all 0.3s ease;
    font-size: 14px;
}

.filter-btn.active {
    background: var(--neon-blue);
    color: #000;
    border-color: var(--neon-blue);
    box-shadow: 0 0 10px var(--neon-blue);
}

/* چت */
.chat-messages {
    margin: 20px 0;
    max-height: 60vh;
    overflow-y: auto;
    padding: 10px;
}

.message {
    padding: 10px 15px;
    margin: 10px 0;
    border-radius: 15px;
    max-width: 80%;
    word-wrap: break-word;
    position: relative;
}

.message.me {
    background: var(--neon-purple);
    color: #000;
    margin-left: auto;
}

.message.them {
    background: var(--card-bg);
    margin-right: auto;
}

.message-tick {
    position: absolute;
    bottom: 2px;
    left: 5px;
    font-size: 12px;
    color: #666;
}

.message-tick.read {
    color: var(--neon-blue);
}

.chat-input {
    position: fixed;
    bottom: 70px;
    left: 0;
    right: 0;
    background: var(--bg-dark);
    padding: 15px;
    border-top: 1px solid #333;
    display: flex;
    gap: 10px;
    align-items: center;
}

.chat-input input {
    flex: 1;
    margin: 0;
}

.chat-input button {
    padding: 10px 15px;
    margin: 0;
}

/* اعلانات */
.notification {
    background: var(--card-bg);
    padding: 15px;
    margin: 10px 0;
    border-radius: 10px;
    border-right: 4px solid var(--neon-purple);
}

.notification.unread {
    border-right-color: var(--neon-blue);
    background: rgba(0, 245, 212, 0.1);
}

/* هدر */
.header {
    text-align: center;
    margin-bottom: 30px;
}

.header h1 {
    background: var(--primary-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.5em;
    margin-bottom: 10px;
}

.header h2 {
    color: var(--neon-blue);
    margin-bottom: 20px;
}

/* دکمه‌های نئونی */
.neon-btn {
    background: var(--primary-gradient);
    color: #000;
    border: none;
    padding: 12px 24px;
    border-radius: 10px;
    font-weight: bold;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 0 15px rgba(155, 93, 229, 0.5);
}

.neon-btn:hover {
    transform: translateY(-3px);
    box-shadow: 0 5px 20px rgba(155, 93, 229, 0.8);
}

/* عکس پروفایل بزرگ */
.profile-avatar {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    object-fit: cover;
    border: 3px solid var(--neon-purple);
    margin: 0 auto 20px;
    display: block;
    box-shadow: 0 0 20px var(--neon-purple);
    cursor: pointer;
}

/* دایره اضافه کردن عکس */
.add-photo-circle {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    background: var(--card-bg);
    margin: 20px auto;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 40px;
    color: var(--neon-blue);
    border: 2px dashed var(--neon-blue);
    cursor: pointer;
    transition: all 0.3s ease;
}

.add-photo-circle:hover {
    transform: scale(1.05);
    box-shadow: 0 0 20px var(--neon-blue);
}

/* سوییچ */
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
    background: var(--primary-gradient);
}

input:checked + .slider:before {
    transform: translateX(26px);
}

/* زنگوله اعلان */
.notification-bell {
    position: relative;
    font-size: 24px;
    color: var(--neon-blue);
}

.notification-badge {
    position: absolute;
    top: -5px;
    right: -5px;
    background: var(--neon-pink);
    color: white;
    border-radius: 50%;
    width: 20px;
    height: 20px;
    font-size: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* فرم ورود/ثبت‌نام */
.auth-form {
    max-width: 400px;
    margin: 0 auto;
    background: var(--card-bg);
    padding: 30px;
    border-radius: 15px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    border: 1px solid var(--neon-purple);
}

.auth-form input, .auth-form select, .auth-form textarea {
    background: #2a2a2a;
    border: 1px solid #333;
}

.auth-form button {
    width: 100%;
    margin-top: 20px;
}

/* اسکرول برای صفحات با محتوای زیاد */
.scrollable-content {
    max-height: calc(100vh - 150px);
    overflow-y: auto;
    padding-bottom: 80px;
}

/* منوی سه نقطه */
.dropdown-menu {
    position: absolute;
    top: 40px;
    right: 10px;
    background: var(--card-bg);
    border: 1px solid #333;
    border-radius: 10px;
    padding: 10px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
    z-index: 1000;
    min-width: 150px;
}

.dropdown-menu button {
    display: block;
    width: 100%;
    text-align: right;
    padding: 8px;
    margin: 5px 0;
    background: none;
    border: none;
    color: var(--white);
    cursor: pointer;
}

.dropdown-menu button:hover {
    background: rgba(155, 93, 229, 0.2);
}

/* لیست فایل‌ها */
.file-options {
    position: absolute;
    bottom: 70px;
    right: 10px;
    background: var(--card-bg);
    border: 1px solid #333;
    border-radius: 10px;
    padding: 10px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
    z-index: 1000;
    min-width: 150px;
}

.file-options button {
    display: block;
    width: 100%;
    text-align: right;
    padding: 8px;
    margin: 5px 0;
    background: none;
    border: none;
    color: var(--white);
    cursor: pointer;
}

.file-options button:hover {
    background: rgba(155, 93, 229, 0.2);
}

/* پیام حذف چت */
.delete-chat-modal {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: var(--card-bg);
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    z-index: 2000;
    text-align: center;
    border: 1px solid var(--neon-purple);
}

.delete-chat-modal button {
    margin: 10px 5px;
    padding: 8px 15px;
}

/* پیام بلاک */
.blocked-message {
    text-align: center;
    color: var(--neon-pink);
    padding: 20px;
    margin: 20px 0;
    border: 1px solid var(--neon-pink);
    border-radius: 10px;
}

/* فیلد فرم با خط نئونی */
.form-field {
    border: 1px solid var(--neon-purple);
    border-radius: 10px;
    padding: 15px;
    margin: 15px 0;
    box-shadow: 0 0 10px rgba(155, 93, 229, 0.3);
}

/* فیلترهای جستجو */
.search-filters {
    position: relative;
    display: inline-block;
    margin-bottom: 20px;
}

.filter-dropdown {
    background: var(--card-bg);
    border: 1px solid #333;
    border-radius: 10px;
    padding: 15px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
    z-index: 1000;
    min-width: 200px;
}

.filter-dropdown label {
    display: block;
    margin: 10px 0;
    cursor: pointer;
}

.filter-dropdown input[type="checkbox"] {
    margin-left: 10px;
}

/*_RESPONSIVE*/
@media (max-width: 768px) {
    body {
        padding: 15px;
        padding-bottom: 80px;
    }
    
    .profile-card {
        flex-direction: column;
        text-align: center;
    }
    
    .profile-card img {
        margin: 0 0 15px 0;
    }
    
    .profile-actions {
        margin-top: 15px;
    }
    
    .chat-input {
        padding: 10px;
    }
    
    .chat-input input {
        padding: 10px;
    }
    
    .chat-input button {
        padding: 10px 15px;
    }
    
    .header h1 {
        font-size: 2em;
    }
    
    .scrollable-content {
        max-height: calc(100vh - 120px);
    }
}
</style>
'''

# اسکریپت‌های JavaScript مشترک
JS_SCRIPT = '''
<script>
// تابع برای لایک کردن کاربر
function likeUser(userId, button) {
    fetch(`/like/${userId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.liked) {
            const likeCount = parseInt(button.getAttribute('data-likes') || '0') + 1;
            button.innerHTML = '❤️ ' + likeCount;
            button.setAttribute('data-likes', likeCount);
            button.style.color = '#ff6b6b';
        } else {
            const likeCount = parseInt(button.getAttribute('data-likes') || '1') - 1;
            button.innerHTML = '🤍 ' + likeCount;
            button.setAttribute('data-likes', likeCount);
            button.style.color = '#ffffff';
        }
    })
    .catch(error => console.error('Error:', error));
}

// تابع برای درخواست چت
function requestChat(userId) {
    fetch(`/request_chat/${userId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('درخواست چت ارسال شد');
        }
    })
    .catch(error => console.error('Error:', error));
}

// تابع برای ارسال پیام
function sendMessage(form) {
    const formData = new FormData(form);
    const message = formData.get('message');
    
    if (!message.trim()) return false;
    
    fetch(form.action, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // پاک کردن فیلد ورودی
            form.querySelector('input[name="message"]').value = '';
            
            // اضافه کردن پیام به صفحه
            const messagesDiv = document.getElementById('messages');
            const newMessage = document.createElement('div');
            newMessage.className = 'message me';
            newMessage.innerHTML = message + '<span class="message-tick">✓</span>';
            messagesDiv.appendChild(newMessage);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
    })
    .catch(error => console.error('Error:', error));
    
    return false;
}

// تابع برای نمایش/پنهان کردن رمز عبور
function togglePassword(inputId, button) {
    const passwordInput = document.getElementById(inputId);
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        button.textContent = '🙈';
    } else {
        passwordInput.type = 'password';
        button.textContent = '👁️';
    }
}

// تابع برای پیش‌نمایش عکس
function previewImage(input, previewId, circleId) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            const preview = document.getElementById(previewId);
            preview.src = e.target.result;
            preview.style.display = 'block';
            // پنهان کردن دایره اضافه کردن عکس
            const circle = document.getElementById(circleId);
            if (circle) circle.style.display = 'none';
        }
        
        reader.readAsDataURL(input.files[0]);
    }
}

// تابع برای بروزرسانی تعداد اعلانات
function updateNotificationCount() {
    fetch('/notification_count')
    .then(response => response.json())
    .then(data => {
        const badge = document.getElementById('notification-badge');
        if (badge) {
            if (data.count > 0) {
                badge.style.display = 'flex';
                badge.textContent = data.count > 9 ? '9+' : data.count;
            } else {
                badge.style.display = 'none';
            }
        }
    });
}

// تابع برای نمایش/پنهان کردن منوی سه نقطه
function toggleDropdown(chatId) {
    const dropdown = document.getElementById('dropdown-' + chatId);
    const allDropdowns = document.querySelectorAll('[id^="dropdown-"]');
    
    // بستن همه منوها
    allDropdowns.forEach(d => {
        if (d !== dropdown) d.style.display = 'none';
    });
    
    // تغییر وضعیت منوی فعلی
    dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
}

// تابع برای نمایش/پنهان کردن گزینه‌های فایل
function toggleFileOptions() {
    const options = document.getElementById('file-options');
    options.style.display = options.style.display === 'block' ? 'none' : 'block';
}

// تابع برای نمایش مودال حذف چت
function showDeleteChatModal(partnerId) {
    const modal = document.createElement('div');
    modal.className = 'delete-chat-modal';
    modal.innerHTML = `
        <h3>آیا مطمئنید؟</h3>
        <p>این چت حذف شود؟</p>
        <div>
            <button onclick="deleteChat(${partnerId}, false)" style="background: var(--neon-blue);">فقط برای من</button>
            <button onclick="deleteChat(${partnerId}, true)" style="background: var(--neon-pink);">برای هر دو</button>
            <button onclick="this.parentElement.parentElement.remove()" style="background: #666;">لغو</button>
        </div>
    `;
    document.body.appendChild(modal);
}

// تابع برای حذف چت
function deleteChat(partnerId, forBoth) {
    fetch(`/delete_chat/${partnerId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({for_both: forBoth})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.href = '/chat';
        }
    })
    .catch(error => console.error('Error:', error));
}

// تابع برای بلاک کردن کاربر
function blockUser(userId) {
    fetch(`/block_user/${userId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('کاربر بلاک شد');
            location.reload();
        }
    })
    .catch(error => console.error('Error:', error));
}

// تابع برای رفع بلاک کردن کاربر
function unblockUser(userId) {
    fetch(`/unblock_user/${userId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('بلاک کاربر رفع شد');
            location.reload();
        }
    })
    .catch(error => console.error('Error:', error));
}

// تابع برای نمایش/پنهان کردن فیلترهای جستجو
function toggleSearchFilters() {
    const filters = document.getElementById('search-filters');
    filters.style.display = filters.style.display === 'block' ? 'none' : 'block';
}

// بستن منوها با کلیک روی صفحه
document.addEventListener('click', function(event) {
    const dropdowns = document.querySelectorAll('[id^="dropdown-"]');
    const fileOptions = document.getElementById('file-options');
    const searchFilters = document.getElementById('search-filters');
    
    dropdowns.forEach(dropdown => {
        if (!dropdown.contains(event.target) && !event.target.closest('.dropdown-btn')) {
            dropdown.style.display = 'none';
        }
    });
    
    if (fileOptions && !fileOptions.contains(event.target) && !event.target.closest('.file-btn')) {
        fileOptions.style.display = 'none';
    }
    
    if (searchFilters && !searchFilters.contains(event.target) && !event.target.closest('.search-filters-btn')) {
        searchFilters.style.display = 'none';
    }
});

// اجرای اسکریپت‌ها بعد از بارگذاری صفحه
document.addEventListener('DOMContentLoaded', function() {
    // اسکرول به آخرین پیام در چت
    const messagesDiv = document.getElementById('messages');
    if (messagesDiv) {
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
    
    // اضافه کردن event listener برای فرم‌های چت
    const chatForms = document.querySelectorAll('.chat-form');
    chatForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            sendMessage(this);
        });
    });
    
    // بروزرسانی تعداد اعلانات
    updateNotificationCount();
    
    // بروزرسانی دوره‌ای تعداد اعلانات
    setInterval(updateNotificationCount, 30000);
});
</script>
'''

# روت‌ها
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return redirect(url_for('register'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password = request.form.get('password')
            confirm = request.form.get('confirm')
            age = request.form.get('age')
            gender = request.form.get('gender')
            city = request.form.get('city')
            name = request.form.get('name', '')
            bio = request.form.get('bio', '')
            interests = request.form.get('interests', '')

            # اضافه کردن @ به ابتدای نام کاربری
            if not username.startswith('@'):
                username = '@' + username

            # بررسی تکراری بودن نام کاربری
            if User.query.filter_by(username=username).first():
                flash("این نام کاربری قبلاً استفاده شده", "error")
                return render_template_string(REGISTER_TEMPLATE, cities=CITIES)

            # بررسی تطابق رمز عبور
            if password != confirm:
                flash("رمز عبور مطابقت ندارد", "error")
                return render_template_string(REGISTER_TEMPLATE, cities=CITIES)

            # آپلود عکس پروفایل
            profile_pic = 'default.png'
            if 'profile_pic' in request.files:
                file = request.files['profile_pic']
                if file and file.filename != '':
                    filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    profile_pic = filename
            else:
                # انتخاب عکس پیش‌فرض بر اساس جنسیت
                if gender == 'پسر':
                    profile_pic = 'default_male.png'
                elif gender == 'دختر':
                    profile_pic = 'default_female.png'
                else:
                    profile_pic = 'default.png'

            # هش کردن رمز عبور
            hashed = bcrypt.generate_password_hash(password).decode('utf-8')
            
            # ایجاد کاربر
            user = User(
                username=username,
                name=name,
                age=int(age),
                gender=gender,
                bio=bio,
                interests=interests,
                city=city,
                password=hashed,
                profile_pic=profile_pic
            )
            db.session.add(user)
            db.session.commit()
            
            flash("🎉 خوش آمدید به گویمیکس", "success")
            return redirect(url_for('home'))
        except Exception as e:
            flash("خطا در ثبت‌نام. لطفاً دوباره تلاش کنید", "error")
            return render_template_string(REGISTER_TEMPLATE, cities=CITIES)

    return render_template_string(REGISTER_TEMPLATE, cities=CITIES)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password = request.form.get('password')
            user = User.query.filter_by(username=username).first()
            if user and bcrypt.check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('home'))
            else:
                flash("نام کاربری یا رمز اشتباه است", "error")
        except Exception as e:
            flash("خطا در ورود. لطفاً دوباره تلاش کنید", "error")
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/home')
@login_required
def home():
    try:
        # اعمال فیلترها
        query = User.query.filter(User.id != current_user.id, User.show_in_home == True)
        users = query.all()
        
        # دریافت تعداد لایک‌ها برای هر کاربر
        for user in users:
            like_count = Like.query.filter_by(liked_user_id=user.id).count()
            user.like_count = like_count
        
        # دریافت تعداد اعلانات خوانده نشده
        unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        return render_template_string(HOME_TEMPLATE, users=users, unread_count=unread_count)
    except Exception as e:
        flash("خطا در بارگذاری صفحه", "error")
        return redirect(url_for('home'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        try:
            current_user.name = request.form.get('name', '')
            current_user.bio = request.form.get('bio', '')
            current_user.interests = request.form.get('interests', '')
            current_user.city = request.form.get('city', '')
            current_user.show_in_home = 'show' in request.form
            
            # آپلود عکس جدید
            if 'profile_pic' in request.files:
                file = request.files['profile_pic']
                if file and file.filename != '':
                    # حذف عکس قبلی اگر دیفالت نباشد
                    if current_user.profile_pic not in ['default.png', 'default_male.png', 'default_female.png']:
                        old_path = os.path.join(app.config['UPLOAD_FOLDER'], current_user.profile_pic)
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    
                    filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    current_user.profile_pic = filename
            
            db.session.commit()
            flash("پروفایل به‌روز شد", "success")
        except Exception as e:
            flash("خطا در به‌روزرسانی پروفایل", "error")
    
    # دریافت تعداد اعلانات خوانده نشده
    unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return render_template_string(PROFILE_TEMPLATE, user=current_user, cities=CITIES, unread_count=unread_count)

@app.route('/notifications')
@login_required
def notifications():
    try:
        # دریافت اعلانات کاربر
        notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
        
        # پاک کردن اعلان‌های جدید
        for notif in notifications:
            notif.is_read = True
        db.session.commit()
        
        # دریافت تعداد اعلانات خوانده نشده
        unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        return render_template_string(NOTIFICATIONS_TEMPLATE, notifications=notifications, unread_count=unread_count)
    except Exception as e:
        flash("خطا در بارگذاری اعلانات", "error")
        return redirect(url_for('home'))

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    results = []
    if request.method == 'POST':
        try:
            q = request.form.get('query', '').strip()
            if q:
                if q.startswith('@'):
                    results = User.query.filter(User.username.like(f"%{q[1:]}%")).all()
                else:
                    results = User.query.filter(User.name.like(f"%{q}%")).all()
            
            # فیلتر کردن کاربرانی که نمایش در خانه غیرفعال کرده‌اند
            results = [user for user in results if user.show_in_home]
            
            # دریافت فیلترهای جستجو
            same_age = 'same_age' in request.form
            same_city = 'same_city' in request.form
            same_gender = 'same_gender' in request.form
            opposite_gender = 'opposite_gender' in request.form
            
            # اعمال فیلترها
            if same_age:
                results = [user for user in results if user.age == current_user.age]
            
            if same_city:
                results = [user for user in results if user.city == current_user.city]
            
            if same_gender:
                results = [user for user in results if user.gender == current_user.gender]
            
            if opposite_gender:
                opposite_genders = {'پسر': 'دختر', 'دختر': 'پسر', 'دیگر': 'دیگر'}
                results = [user for user in results if user.gender == opposite_genders.get(current_user.gender, 'دیگر')]
            
            # دریافت تعداد لایک‌ها برای هر کاربر
            for user in results:
                like_count = Like.query.filter_by(liked_user_id=user.id).count()
                user.like_count = like_count
                
        except Exception as e:
            flash("خطا در جستجو", "error")
    
    # دریافت تعداد اعلانات خوانده نشده
    unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return render_template_string(SEARCH_TEMPLATE, results=results, unread_count=unread_count)

@app.route('/chat')
@login_required
def chat_list():
    try:
        # دریافت چت‌های کاربر
        chats = Chat.query.filter(
            (Chat.user_id == current_user.id) | (Chat.partner_id == current_user.id)
        ).all()
        
        # اضافه کردن اطلاعات طرف مقابل
        chat_data = []
        for chat in chats:
            partner_id = chat.partner_id if chat.user_id == current_user.id else chat.user_id
            partner = User.query.get(partner_id)
            if partner:
                # آخرین پیام
                last_message = Message.query.filter_by(chat_id=chat.id).order_by(Message.timestamp.desc()).first()
                chat_data.append({
                    'chat': chat,
                    'partner': partner,
                    'last_message': last_message
                })
        
        # دریافت تعداد اعلانات خوانده نشده
        unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        return render_template_string(CHAT_LIST_TEMPLATE, chat_data=chat_data, unread_count=unread_count)
    except Exception as e:
        flash("خطا در بارگذاری چت‌ها", "error")
        return redirect(url_for('home'))

@app.route('/chat/<int:partner_id>', methods=['GET', 'POST'])
@login_required
def chat_room(partner_id):
    try:
        partner = User.query.get_or_404(partner_id)
        
        # بررسی بلاک بودن
        is_blocked = Block.query.filter(
            ((Block.blocker_id == current_user.id) & (Block.blocked_id == partner_id)) |
            ((Block.blocker_id == partner_id) & (Block.blocked_id == current_user.id))
        ).first()
        
        if is_blocked:
            flash("این کاربر شما را بلاک کرده است", "error")
            return redirect(url_for('chat_list'))
        
        # پیدا کردن یا ایجاد چت
        chat = Chat.query.filter(
            ((Chat.user_id == current_user.id) & (Chat.partner_id == partner_id)) |
            ((Chat.user_id == partner_id) & (Chat.partner_id == current_user.id))
        ).first()
        
        if not chat:
            chat = Chat(user_id=current_user.id, partner_id=partner_id)
            db.session.add(chat)
            db.session.commit()
        
        if request.method == 'POST':
            content = request.form.get('message')
            if content:
                msg = Message(chat_id=chat.id, sender_id=current_user.id, content=content)
                db.session.add(msg)
                db.session.commit()
                
                # ایجاد اعلان برای طرف مقابل
                notification = Notification(
                    user_id=partner_id,
                    sender_id=current_user.id,
                    message=f"پیام جدید از {current_user.username}",
                    type="message"
                )
                db.session.add(notification)
                db.session.commit()
                
                return jsonify(success=True)
        
        # دریافت پیام‌ها
        messages = Message.query.filter_by(chat_id=chat.id).order_by(Message.timestamp.asc()).all()
        
        # علامت‌گذاری پیام‌ها به عنوان خوانده شده
        for message in messages:
            if message.sender_id != current_user.id and not message.is_read:
                message.is_read = True
        db.session.commit()
        
        # دریافت تعداد اعلانات خوانده نشده
        unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        return render_template_string(CHAT_ROOM_TEMPLATE, partner=partner, messages=messages, chat=chat, unread_count=unread_count)
    except Exception as e:
        flash("خطا در بارگذاری چت", "error")
        return redirect(url_for('chat_list'))

@app.route('/delete_chat/<int:partner_id>', methods=['POST'])
@login_required
def delete_chat(partner_id):
    try:
        data = request.get_json()
        for_both = data.get('for_both', False)
        
        chat = Chat.query.filter(
            ((Chat.user_id == current_user.id) & (Chat.partner_id == partner_id)) |
            ((Chat.user_id == partner_id) & (Chat.partner_id == current_user.id))
        ).first()
        
        if chat:
            if for_both:
                # حذف برای هر دو
                Message.query.filter_by(chat_id=chat.id).delete()
                db.session.delete(chat)
            else:
                # حذف فقط برای خود کاربر فعلی
                Message.query.filter_by(chat_id=chat.id, sender_id=current_user.id).delete()
            db.session.commit()
            return jsonify(success=True)
        else:
            return jsonify(success=False)
    except Exception as e:
        return jsonify(success=False)

@app.route('/like/<int:user_id>', methods=['POST'])
@login_required
def like_user(user_id):
    try:
        target_user = User.query.get_or_404(user_id)
        
        # بررسی اینکه قبلاً لایک شده یا نه
        existing_like = Like.query.filter_by(
            user_id=current_user.id,
            liked_user_id=user_id
        ).first()
        
        if existing_like:
            # حذف لایک
            db.session.delete(existing_like)
            db.session.commit()
            return jsonify(liked=False)
        else:
            # اضافه کردن لایک
            like = Like(user_id=current_user.id, liked_user_id=user_id)
            db.session.add(like)
            
            # ایجاد اعلان برای کاربر لایک‌شده
            notification = Notification(
                user_id=user_id,
                sender_id=current_user.id,
                message=f"کاربر {current_user.username} شما را لایک کرد",
                type="like"
            )
            db.session.add(notification)
            
            db.session.commit()
            return jsonify(liked=True)
    except Exception as e:
        return jsonify(liked=False)

@app.route('/request_chat/<int:user_id>', methods=['POST'])
@login_required
def request_chat(user_id):
    try:
        target_user = User.query.get_or_404(user_id)
        
        # ایجاد اعلان درخواست چت
        notification = Notification(
            user_id=user_id,
            sender_id=current_user.id,
            message=f"کاربر {current_user.username} درخواست چت داده",
            type="chat_request"
        )
        db.session.add(notification)
        db.session.commit()
        
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False)

@app.route('/block_user/<int:user_id>', methods=['POST'])
@login_required
def block_user(user_id):
    try:
        # بررسی اینکه قبلاً بلاک شده یا نه
        existing_block = Block.query.filter_by(
            blocker_id=current_user.id,
            blocked_id=user_id
        ).first()
        
        if not existing_block:
            # بلاک کردن کاربر
            block = Block(blocker_id=current_user.id, blocked_id=user_id)
            db.session.add(block)
            
            # ایجاد اعلان برای کاربر بلاک‌شده
            notification = Notification(
                user_id=user_id,
                sender_id=current_user.id,
                message=f"کاربر {current_user.username} شما را بلاک کرده است",
                type="block"
            )
            db.session.add(notification)
            
            db.session.commit()
        
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False)

@app.route('/unblock_user/<int:user_id>', methods=['POST'])
@login_required
def unblock_user(user_id):
    try:
        # پیدا کردن بلاک
        block = Block.query.filter_by(
            blocker_id=current_user.id,
            blocked_id=user_id
        ).first()
        
        if block:
            # رفع بلاک کردن کاربر
            db.session.delete(block)
            
            # ایجاد اعلان برای کاربر رفع‌بلاک‌شده
            notification = Notification(
                user_id=user_id,
                sender_id=current_user.id,
                message=f"کاربر {current_user.username} شما را از بلاک خارج کرده است",
                type="unblock"
            )
            db.session.add(notification)
            
            db.session.commit()
        
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False)

@app.route('/notification_count')
@login_required
def notification_count():
    try:
        count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        return jsonify(count=count)
    except Exception as e:
        return jsonify(count=0)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# سرویس فایل‌های استاتیک
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

# تمپلیت‌ها
REGISTER_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ثبت‌نام - GOYIMIX | گویمیکس</title>
''' + CSS_STYLE + '''
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    <div class="header">
        <h1>GOYIMIX | گویمیکس</h1>
        <h2>خوش آمدید به گویمیکس | GOYIMIX</h2>
    </div>
    
    <div class="flash-messages">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
    </div>
    
    <main>
        <div class="auth-form">
            <form method="post" enctype="multipart/form-data">
                <div style="text-align: center;">
                    <label for="profile_pic" style="cursor: pointer;">
                        <div class="add-photo-circle" id="photo-circle">
                            +
                        </div>
                        <img id="profile-preview" src="" 
                             alt="پیش‌نمایش پروفایل" 
                             style="width: 100px; height: 100px; border-radius: 50%; object-fit: cover; display: none; margin: 0 auto 20px;">
                    </label>
                    <input type="file" id="profile_pic" name="profile_pic" accept="image/*" 
                           onchange="previewImage(this, 'profile-preview', 'photo-circle')" style="display: none;">
                </div>
                
                <input type="text" name="name" placeholder="نام (اختیاری)">
                <input type="text" name="username" placeholder="نام کاربری (اجباری)" required>
                
                <select name="age" required>
                    <option value="">سن (اجباری)</option>
                    {% for age in range(12, 81) %}
                    <option value="{{ age }}">{{ age }} سال</option>
                    {% endfor %}
                </select>
                
                <select name="gender" required>
                    <option value="">جنسیت (اجباری)</option>
                    <option value="پسر">پسر</option>
                    <option value="دختر">دختر</option>
                    <option value="دیگر">دیگر</option>
                </select>
                
                <textarea name="bio" placeholder="بیو (اختیاری)"></textarea>
                <textarea name="interests" placeholder="علاقه‌مندی‌ها (اختیاری)"></textarea>
                
                <select name="city" required>
                    <option value="">شهر (اجباری)</option>
                    {% for city in cities %}
                    <option value="{{ city }}">{{ city }}</option>
                    {% endfor %}
                </select>
                
                <div style="position: relative;">
                    <input type="password" id="password" name="password" placeholder="رمز عبور (اجباری)" required>
                    <span onclick="togglePassword('password', this)" 
                          style="position: absolute; left: 10px; top: 50%; transform: translateY(-50%); cursor: pointer;">
                        👁️
                    </span>
                </div>
                
                <div style="position: relative;">
                    <input type="password" id="confirm" name="confirm" placeholder="تکرار رمز عبور (اجباری)" required>
                    <span onclick="togglePassword('confirm', this)" 
                          style="position: absolute; left: 10px; top: 50%; transform: translateY(-50%); cursor: pointer;">
                        👁️
                    </span>
                </div>
                
                <button type="submit" class="neon-btn">ثبت‌نام</button>
            </form>
            
            <p style="text-align: center; margin-top: 20px;">
                <a href="{{ url_for('login') }}">حساب دارید؟ وارد شوید</a>
            </p>
        </div>
    </main>
''' + JS_SCRIPT + '''
</body>
</html>
'''

LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ورود - GOYIMIX | گویمیکس</title>
''' + CSS_STYLE + '''
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    <div class="header">
        <h1>GOYIMIX | گویمیکس</h1>
        <h2>دوباره خوش آمدید</h2>
    </div>
    
    <div class="flash-messages">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
    </div>
    
    <main>
        <div class="auth-form">
            <form method="post">
                <input type="text" name="username" placeholder="نام کاربری یا نام" required>
                
                <div style="position: relative;">
                    <input type="password" id="password" name="password" placeholder="رمز عبور" required>
                    <span onclick="togglePassword('password', this)" 
                          style="position: absolute; left: 10px; top: 50%; transform: translateY(-50%); cursor: pointer;">
                        👁️
                    </span>
                </div>
                
                <button type="submit" class="neon-btn">ورود</button>
            </form>
            
            <p style="text-align: center; margin-top: 20px;">
                <a href="{{ url_for('register') }}">اگر حسابی ندارید؟ ثبت‌نام کنید</a>
            </p>
        </div>
    </main>
''' + JS_SCRIPT + '''
</body>
</html>
'''

HOME_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>خانه - GOYIMIX | گویمیکس</title>
''' + CSS_STYLE + '''
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    <div class="header">
        <h1>GOYIMIX | گویمیکس</h1>
    </div>
    
    <div class="flash-messages">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
    </div>
    
    <main class="scrollable-content">
        <div class="home-page">
            <!-- لیست پروفایل‌ها -->
            {% if users %}
                {% for user in users %}
                <div class="profile-card">
                    <img src="/static/uploads/{{ user.profile_pic }}" 
                         alt="{{ user.name or user.username }}">
                    <div class="profile-info">
                        <h3>{{ user.name or user.username }}</h3>
                        <p>{{ user.username }}</p>
                        <p>{{ user.age }} سال، {{ user.gender }}، {{ user.city }}</p>
                        {% if user.bio %}
                        <p>{{ user.bio[:50] }}{% if user.bio|length > 50 %}...{% endif %}</p>
                        {% endif %}
                    </div>
                    <div class="profile-actions">
                        {% set like_count = user.like_count or 0 %}
                        <button onclick="likeUser({{ user.id }}, this)" 
                                style="background: #ff6b6b; color: white;"
                                data-likes="{{ like_count }}">
                            {% if Like.query.filter_by(user_id=current_user.id, liked_user_id=user.id).first() %}
                                ❤️ {{ like_count }}
                            {% else %}
                                🤍 {{ like_count }}
                            {% endif %}
                        </button>
                        <button onclick="requestChat({{ user.id }})" 
                                style="background: #9B5DE5; color: white;">
                            💬
                        </button>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <div style="text-align: center; margin: 50px 0; color: #E0E0E0;">
                    <i class="fas fa-user-friends" style="font-size: 48px; margin-bottom: 15px;"></i>
                    <p>پروفایلی یافت نشد</p>
                </div>
            {% endif %}
        </div>
    </main>
    
    <nav class="bottom-nav">
        <a href="{{ url_for('profile') }}" class="nav-item">
            <i class="fas fa-user"></i>
            <span>پروفایل</span>
        </a>
        <a href="{{ url_for('home') }}" class="nav-item active">
            <i class="fas fa-home"></i>
            <span>خانه</span>
        </a>
        <a href="{{ url_for('search') }}" class="nav-item">
            <i class="fas fa-search"></i>
            <span>جستجو</span>
        </a>
        <a href="{{ url_for('chat_list') }}" class="nav-item">
            <i class="fas fa-comments"></i>
            <span>چت</span>
        </a>
        <a href="{{ url_for('notifications') }}" class="nav-item">
            <div style="position: relative;">
                <i class="fas fa-bell"></i>
                {% if unread_count > 0 %}
                <span id="notification-badge" class="notification-badge">{{ unread_count if unread_count <= 9 else '9+' }}</span>
                {% endif %}
            </div>
            <span>اعلان‌ها</span>
        </a>
    </nav>
''' + JS_SCRIPT + '''
</body>
</html>
'''

PROFILE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>پروفایل - GOYIMIX | گویمیکس</title>
''' + CSS_STYLE + '''
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    <div class="header">
        <h1>GOYIMIX | گویمیکس</h1>
    </div>
    
    <div class="flash-messages">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
    </div>
    
    <main class="scrollable-content">
        <div style="text-align: center; margin: 20px 0;">
            <label for="profile_pic" style="cursor: pointer;">
                <img src="/static/uploads/{{ user.profile_pic }}" 
                     alt="پروفایل" 
                     class="profile-avatar">
                <img id="profile-preview" src="" 
                     alt="پیش‌نمایش پروفایل" 
                     style="width: 120px; height: 120px; border-radius: 50%; object-fit: cover; display: none; margin: 0 auto 20px;">
            </label>
            <input type="file" id="profile_pic" name="profile_pic" accept="image/*" 
                   onchange="previewImage(this, 'profile-preview', 'profile-avatar')" style="display: none;">
        </div>
        
        <div class="form-field">
            <form method="post" enctype="multipart/form-data">
                <div style="margin-bottom: 15px;">
                    <label style="display: flex; justify-content: space-between; align-items: center;">
                        <span>نام:</span>
                        <input type="text" name="name" value="{{ user.name or '' }}" style="width: 70%;">
                    </label>
                </div>
                
                <div style="margin-bottom: 15px;">
                    <label style="display: flex; justify-content: space-between; align-items: center;">
                        <span>نام کاربری:</span>
                        <input type="text" name="username" value="{{ user.username }}" style="width: 70%;">
                    </label>
                </div>
                
                <div style="margin-bottom: 15px;">
                    <label style="display: flex; justify-content: space-between; align-items: center;">
                        <span>سن:</span>
                        <select name="age" style="width: 70%;">
                            {% for age in range(12, 81) %}
                            <option value="{{ age }}" {% if user.age == age %}selected{% endif %}>
                                {{ age }} سال
                            </option>
                            {% endfor %}
                        </select>
                    </label>
                </div>
                
                <div style="margin-bottom: 15px;">
                    <label style="display: flex; justify-content: space-between; align-items: center;">
                        <span>جنسیت:</span>
                        <select name="gender" style="width: 70%;">
                            <option value="پسر" {% if user.gender == 'پسر' %}selected{% endif %}>پسر</option>
                            <option value="دختر" {% if user.gender == 'دختر' %}selected{% endif %}>دختر</option>
                            <option value="دیگر" {% if user.gender == 'دیگر' %}selected{% endif %}>دیگر</option>
                        </select>
                    </label>
                </div>
                
                <div style="margin-bottom: 15px;">
                    <label style="display: flex; justify-content: space-between; align-items: center;">
                        <span>بیو:</span>
                        <textarea name="bio" style="width: 70%; height: 60px;">{{ user.bio or '' }}</textarea>
                    </label>
                </div>
                
                <div style="margin-bottom: 15px;">
                    <label style="display: flex; justify-content: space-between; align-items: center;">
                        <span>علاقه‌مندی‌ها:</span>
                        <textarea name="interests" style="width: 70%; height: 60px;">{{ user.interests or '' }}</textarea>
                    </label>
                </div>
                
                <div style="margin-bottom: 15px;">
                    <label style="display: flex; justify-content: space-between; align-items: center;">
                        <span>شهر:</span>
                        <select name="city" style="width: 70%;">
                            {% for city in cities %}
                            <option value="{{ city }}" {% if user.city == city %}selected{% endif %}>
                                {{ city }}
                            </option>
                            {% endfor %}
                        </select>
                    </label>
                </div>
                
                <div style="margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between;">
                    <span>نمایش پروفایل در خانه:</span>
                    <label class="switch">
                        <input type="checkbox" name="show" {% if user.show_in_home %}checked{% endif %}>
                        <span class="slider"></span>
                    </label>
                </div>
                
                <button type="submit" class="neon-btn" style="width: 100%;">ذخیره تغییرات</button>
            </form>
        </div>
        
        <div style="margin-top: 30px; text-align: center;">
            <button onclick="location.href='{{ url_for('logout') }}'" 
                    class="neon-btn" 
                    style="background: linear-gradient(90deg, #ff6b6b, #ff8e8e); width: 100%; margin-bottom: 10px;">
                خروج از حساب
            </button>
        </div>
    </main>
    
    <nav class="bottom-nav">
        <a href="{{ url_for('profile') }}" class="nav-item active">
            <i class="fas fa-user"></i>
            <span>پروفایل</span>
        </a>
        <a href="{{ url_for('home') }}" class="nav-item">
            <i class="fas fa-home"></i>
            <span>خانه</span>
        </a>
        <a href="{{ url_for('search') }}" class="nav-item">
            <i class="fas fa-search"></i>
            <span>جستجو</span>
        </a>
        <a href="{{ url_for('chat_list') }}" class="nav-item">
            <i class="fas fa-comments"></i>
            <span>چت</span>
        </a>
        <a href="{{ url_for('notifications') }}" class="nav-item">
            <div style="position: relative;">
                <i class="fas fa-bell"></i>
                {% if unread_count > 0 %}
                <span id="notification-badge" class="notification-badge">{{ unread_count if unread_count <= 9 else '9+' }}</span>
                {% endif %}
            </div>
            <span>اعلان‌ها</span>
        </a>
    </nav>
''' + JS_SCRIPT + '''
</body>
</html>
'''

NOTIFICATIONS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>اعلانات - GOYIMIX | گویمیکس</title>
''' + CSS_STYLE + '''
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    <div class="header">
        <h1>GOYIMIX | گویمیکس</h1>
        <h2>اعلانات</h2>
    </div>
    
    <div class="flash-messages">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
    </div>
    
    <main class="scrollable-content">
        <div class="notifications-page">
            {% if notifications %}
                {% for notif in notifications %}
                <div class="notification {% if not notif.is_read %}unread{% endif %}">
                    <p>{{ notif.message }}</p>
                    <small style="color: #aaa;">{{ notif.created_at.strftime('%Y/%m/%d %H:%M') }}</small>
                    {% if notif.type == 'chat_request' %}
                    <div style="margin-top: 10px; display: flex; gap: 10px;">
                        <button onclick="location.href='{{ url_for('chat_room', partner_id=notif.sender_id) }}'" 
                                style="background: var(--neon-blue); color: #000; padding: 5px 10px; border: none; border-radius: 5px; font-size: 12px;">
                            ✅ قبول
                        </button>
                    </div>
                    {% endif %}
                </div>
                {% endfor %}
            {% else %}
                <div style="text-align: center; margin: 50px 0; color: #E0E0E0;">
                    <i class="fas fa-bell-slash" style="font-size: 48px; margin-bottom: 15px;"></i>
                    <p>اعلانی وجود ندارد</p>
                </div>
            {% endif %}
        </div>
    </main>
    
    <nav class="bottom-nav">
        <a href="{{ url_for('profile') }}" class="nav-item">
            <i class="fas fa-user"></i>
            <span>پروفایل</span>
        </a>
        <a href="{{ url_for('home') }}" class="nav-item">
            <i class="fas fa-home"></i>
            <span>خانه</span>
        </a>
        <a href="{{ url_for('search') }}" class="nav-item">
            <i class="fas fa-search"></i>
            <span>جستجو</span>
        </a>
        <a href="{{ url_for('chat_list') }}" class="nav-item">
            <i class="fas fa-comments"></i>
            <span>چت</span>
        </a>
        <a href="{{ url_for('notifications') }}" class="nav-item active">
            <div style="position: relative;">
                <i class="fas fa-bell"></i>
                {% if unread_count > 0 %}
                <span id="notification-badge" class="notification-badge">{{ unread_count if unread_count <= 9 else '9+' }}</span>
                {% endif %}
            </div>
            <span>اعلان‌ها</span>
        </a>
    </nav>
''' + JS_SCRIPT + '''
</body>
</html>
'''

SEARCH_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>جستجو - GOYIMIX | گویمیکس</title>
''' + CSS_STYLE + '''
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    <div class="header">
        <h1>GOYIMIX | گویمیکس</h1>
        <h2>جستجوی کاربران</h2>
    </div>
    
    <div class="flash-messages">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
    </div>
    
    <main class="scrollable-content">
        <div class="search-page">
            <form method="post" style="margin-bottom: 30px;">
                <div style="display: flex; gap: 10px; align-items: center;">
                    <input type="text" name="query" placeholder="نام یا نام کاربری" required style="flex: 1;">
                    <button type="button" class="search-filters-btn" onclick="toggleSearchFilters()" 
                            style="background: var(--neon-purple); color: #000; border: none; padding: 12px; border-radius: 10px; cursor: pointer;">
                        ⚙️
                    </button>
                    <button type="submit" class="neon-btn">
                        <i class="fas fa-search"></i>
                    </button>
                </div>
                
                <div id="search-filters" class="filter-dropdown" style="display: none; margin-top: 10px;">
                    <label>
                        <input type="checkbox" name="same_age" value="1"> هم‌سن
                    </label>
                    <label>
                        <input type="checkbox" name="same_city" value="1"> هم‌شهر
                    </label>
                    <label>
                        <input type="checkbox" name="same_gender" value="1"> هم‌جنسیت
                    </label>
                    <label>
                        <input type="checkbox" name="opposite_gender" value="1"> ناهم‌جنسیت
                    </label>
                </div>
            </form>
            
            {% if results %}
                {% for user in results %}
                <div class="profile-card">
                    <img src="/static/uploads/{{ user.profile_pic }}" 
                         alt="{{ user.name or user.username }}">
                    <div class="profile-info">
                        <h3>{{ user.name or user.username }}</h3>
                        <p>{{ user.username }}</p>
                        <p>{{ user.age }} سال، {{ user.gender }}، {{ user.city }}</p>
                    </div>
                    <div class="profile-actions">
                        <button onclick="location.href='{{ url_for('chat_room', partner_id=user.id) }}'">
                            💬
                        </button>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                {% if request.method == 'POST' %}
                <div style="text-align: center; margin: 50px 0; color: #E0E0E0;">
                    <i class="fas fa-search" style="font-size: 48px; margin-bottom: 15px;"></i>
                    <p>نتیجه‌ای یافت نشد</p>
                </div>
                {% endif %}
            {% endif %}
        </div>
    </main>
    
    <nav class="bottom-nav">
        <a href="{{ url_for('profile') }}" class="nav-item">
            <i class="fas fa-user"></i>
            <span>پروفایل</span>
        </a>
        <a href="{{ url_for('home') }}" class="nav-item">
            <i class="fas fa-home"></i>
            <span>خانه</span>
        </a>
        <a href="{{ url_for('search') }}" class="nav-item active">
            <i class="fas fa-search"></i>
            <span>جستجو</span>
        </a>
        <a href="{{ url_for('chat_list') }}" class="nav-item">
            <i class="fas fa-comments"></i>
            <span>چت</span>
        </a>
        <a href="{{ url_for('notifications') }}" class="nav-item">
            <div style="position: relative;">
                <i class="fas fa-bell"></i>
                {% if unread_count > 0 %}
                <span id="notification-badge" class="notification-badge">{{ unread_count if unread_count <= 9 else '9+' }}</span>
                {% endif %}
            </div>
            <span>اعلان‌ها</span>
        </a>
    </nav>
''' + JS_SCRIPT + '''
</body>
</html>
'''

CHAT_LIST_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>چت‌ها - GOYIMIX | گویمیکس</title>
''' + CSS_STYLE + '''
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    <div class="header">
        <h1>GOYIMIX | گویمیکس</h1>
        <h2>چت‌های من</h2>
    </div>
    
    <div class="flash-messages">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
    </div>
    
    <main class="scrollable-content">
        <div class="chat-list-page">
            {% if chat_data %}
                {% for data in chat_data %}
                <div class="profile-card" 
                     onclick="location.href='{{ url_for('chat_room', partner_id=data.partner.id) }}'"
                     style="cursor: pointer;">
                    <img src="/static/uploads/{{ data.partner.profile_pic }}" 
                         alt="{{ data.partner.name or data.partner.username }}">
                    <div class="profile-info">
                        <h3>{{ data.partner.name or data.partner.username }}</h3>
                        <p>{{ data.partner.username }}</p>
                        {% if data.last_message %}
                        <p style="color: #aaa; font-size: 14px;">
                            {{ data.last_message.content[:30] }}{% if data.last_message.content|length > 30 %}...{% endif %}
                        </p>
                        {% endif %}
                    </div>
                    <div class="profile-actions">
                        <button class="dropdown-btn" onclick="event.stopPropagation(); toggleDropdown({{ data.chat.id }})" 
                                style="background: none; border: none; color: var(--neon-blue); font-size: 20px;">
                            ⋮
                        </button>
                        <div id="dropdown-{{ data.chat.id }}" class="dropdown-menu" style="display: none;">
                            <button onclick="showDeleteChatModal({{ data.partner.id }})">حذف چت</button>
                            <button onclick="blockUser({{ data.partner.id }})">بلاک کردن</button>
                        </div>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <div style="text-align: center; margin: 50px 0; color: #E0E0E0;">
                    <i class="fas fa-comments" style="font-size: 48px; margin-bottom: 15px;"></i>
                    <p>چتی وجود ندارد</p>
                </div>
            {% endif %}
        </div>
    </main>
    
    <nav class="bottom-nav">
        <a href="{{ url_for('profile') }}" class="nav-item">
            <i class="fas fa-user"></i>
            <span>پروفایل</span>
        </a>
        <a href="{{ url_for('home') }}" class="nav-item">
            <i class="fas fa-home"></i>
            <span>خانه</span>
        </a>
        <a href="{{ url_for('search') }}" class="nav-item">
            <i class="fas fa-search"></i>
            <span>جستجو</span>
        </a>
        <a href="{{ url_for('chat_list') }}" class="nav-item active">
            <i class="fas fa-comments"></i>
            <span>چت</span>
        </a>
        <a href="{{ url_for('notifications') }}" class="nav-item">
            <div style="position: relative;">
                <i class="fas fa-bell"></i>
                {% if unread_count > 0 %}
                <span id="notification-badge" class="notification-badge">{{ unread_count if unread_count <= 9 else '9+' }}</span>
                {% endif %}
            </div>
            <span>اعلان‌ها</span>
        </a>
    </nav>
''' + JS_SCRIPT + '''
</body>
</html>
'''

CHAT_ROOM_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>چت با {{ partner.name or partner.username }} - GOYIMIX | گویمیکس</title>
''' + CSS_STYLE + '''
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    <div class="header">
        <h1>GOYIMIX | گویمیکس</h1>
    </div>
    
    <div class="flash-messages">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
    </div>
    
    <main>
        <div class="chat-room-page">
            <div style="display: flex; align-items: center; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid #333;">
                <button onclick="location.href='{{ url_for('chat_list') }}'" style="background: none; border: none; color: #00F5D4; font-size: 20px; margin-left: 15px;">
                    ←
                </button>
                <img src="/static/uploads/{{ partner.profile_pic }}" 
                     alt="{{ partner.name or partner.username }}"
                     style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover; margin-left: 10px;">
                <div style="flex: 1;">
                    <h3 style="margin: 0;">{{ partner.name or partner.username }}</h3>
                    <p style="margin: 0; font-size: 14px; color: #aaa;">{{ partner.username }}</p>
                </div>
                <button class="dropdown-btn" onclick="toggleDropdown('chat')" 
                        style="background: none; border: none; color: var(--neon-blue); font-size: 20px;">
                    ⋮
                </button>
                <div id="dropdown-chat" class="dropdown-menu" style="display: none;">
                    <button onclick="showDeleteChatModal({{ partner.id }})">حذف چت</button>
                    <button onclick="blockUser({{ partner.id }})">بلاک کردن</button>
                </div>
            </div>
            
            <div id="messages" class="chat-messages">
                {% for message in messages %}
                <div class="message {% if message.sender_id == current_user.id %}me{% else %}them{% endif %}">
                    {{ message.content }}
                    <span class="message-tick {% if message.is_read %}read{% endif %}">✓</span>
                </div>
                {% endfor %}
            </div>
            
            <div class="chat-input">
                <button class="file-btn" onclick="toggleFileOptions()" 
                        style="background: none; border: none; color: var(--neon-blue); font-size: 20px;">
                    📎
                </button>
                <div id="file-options" class="file-options" style="display: none;">
                    <button>ارسال عکس</button>
                    <button>ارسال ویدیو</button>
                    <button>دوربین</button>
                    <button>ارسال فایل</button>
                </div>
                <input type="text" name="message" placeholder="پیام..." required>
                <button class="neon-btn" style="padding: 10px 15px; margin: 0;">
                    <i class="fas fa-paper-plane"></i>
                </button>
            </div>
        </div>
    </main>
    
    <script>
        // اسکرول به آخرین پیام
        const messagesDiv = document.getElementById('messages');
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
        
        // تابع ارسال پیام
        function sendMessage(form) {
            const formData = new FormData(form);
            const message = formData.get('message');
            
            if (!message.trim()) return false;
            
            fetch('', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    form.querySelector('input[name="message"]').value = '';
                    
                    const newMessage = document.createElement('div');
                    newMessage.className = 'message me';
                    newMessage.innerHTML = message + '<span class="message-tick">✓</span>';
                    messagesDiv.appendChild(newMessage);
                    messagesDiv.scrollTop = messagesDiv.scrollHeight;
                }
            })
            .catch(error => console.error('Error:', error));
            
            return false;
        }
        
        // بروزرسانی خودکار پیام‌ها
        setInterval(function() {
            fetch(window.location.href)
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const newMessages = doc.getElementById('messages');
                if (newMessages) {
                    document.getElementById('messages').innerHTML = newMessages.innerHTML;
                    document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;
                }
            });
        }, 3000);
    </script>
''' + JS_SCRIPT + '''
</body>
</html>
'''

if __name__ == '__main__':
    # ایجاد دیتابیس
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            print(f"خطا در ایجاد دیتابیس: {e}")
    app.run(debug=True, port=5000, host='0.0.0.0')