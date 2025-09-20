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
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Message {self.id}>'

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    sender_id = db.Column(db.Integer)  # کاربری که اعلان را ایجاد کرده
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # like, chat_request, message
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Notification {self.id}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
}

button:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(155, 93, 229, 0.4);
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
}

.profile-card:hover {
    transform: translateY(-5px);
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
}

.nav-item {
    text-align: center;
    color: var(--light-gray);
    text-decoration: none;
    font-size: 12px;
}

.nav-item.active {
    color: var(--neon-blue);
}

.nav-item i {
    display: block;
    font-size: 20px;
    margin-bottom: 5px;
}

/* فیلترها */
.filters {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin: 20px 0;
}

.filter-btn {
    background: var(--card-bg);
    color: var(--light-gray);
    border: 1px solid #333;
    padding: 8px 15px;
    border-radius: 20px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.filter-btn.active {
    background: var(--neon-blue);
    color: #000;
    border-color: var(--neon-blue);
}

/* چت */
.chat-messages {
    margin: 20px 0;
    max-height: 60vh;
    overflow-y: auto;
}

.message {
    padding: 10px 15px;
    margin: 10px 0;
    border-radius: 15px;
    max-width: 80%;
    word-wrap: break-word;
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

.chat-input {
    position: fixed;
    bottom: 70px;
    left: 0;
    right: 0;
    background: var(--bg-dark);
    padding: 15px;
    border-top: 1px solid #333;
}

.chat-input form {
    display: flex;
    gap: 10px;
}

.chat-input input {
    flex: 1;
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

/*_RESPONSIVE*/
@media (max-width: 768px) {
    body {
        padding: 15px;
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
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.liked) {
            button.innerHTML = '❤️ ' + (parseInt(button.innerHTML.split(' ')[1] || 0) + 1);
            button.style.color = '#ff6b6b';
        } else {
            button.innerHTML = '🤍 ' + (parseInt(button.innerHTML.split(' ')[1] || 1) - 1);
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
            'Content-Type': 'application/json',
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
    
    if (!message.trim()) return;
    
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
            newMessage.textContent = message;
            messagesDiv.appendChild(newMessage);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
    })
    .catch(error => console.error('Error:', error));
    
    return false;
}

// تابع برای نمایش/پنهان کردن رمز عبور
function togglePassword() {
    const passwordInput = document.getElementById('password');
    const toggleBtn = document.querySelector('.toggle-password');
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleBtn.textContent = '🙈';
    } else {
        passwordInput.type = 'password';
        toggleBtn.textContent = '👁️';
    }
}

// تابع برای پیش‌نمایش عکس
function previewImage(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            const preview = document.getElementById('profile-preview');
            preview.src = e.target.result;
            preview.style.display = 'block';
        }
        
        reader.readAsDataURL(input.files[0]);
    }
}

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
});
</script>
'''

# روت‌ها
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('register'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        age = request.form.get('age')
        gender = request.form.get('gender')
        city = request.form.get('city')
        name = request.form.get('name', '')
        bio = request.form.get('bio', '')
        interests = request.form.get('interests', '')

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
        return redirect(url_for('login'))

    return render_template_string(REGISTER_TEMPLATE, cities=CITIES)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash("نام کاربری یا رمز اشتباه است", "error")
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template_string(DASHBOARD_TEMPLATE)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
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
                if current_user.profile_pic != 'default.png':
                    old_path = os.path.join(app.config['UPLOAD_FOLDER'], current_user.profile_pic)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                current_user.profile_pic = filename
        
        db.session.commit()
        flash("پروفایل به‌روز شد", "success")
    
    return render_template_string(PROFILE_TEMPLATE, user=current_user, cities=CITIES)

@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    # دریافت فیلترها از session
    filters = session.get('filters', {
        'same_age': False,
        'same_gender': False,
        'opposite_gender': False,
        'same_city': False
    })
    
    if request.method == 'POST':
        # به‌روزرسانی فیلترها
        filters = {
            'same_age': 'same_age' in request.form,
            'same_gender': 'same_gender' in request.form,
            'opposite_gender': 'opposite_gender' in request.form,
            'same_city': 'same_city' in request.form
        }
        session['filters'] = filters
    
    # اعمال فیلترها
    query = User.query.filter(User.id != current_user.id, User.show_in_home == True)
    
    if filters['same_age']:
        query = query.filter(User.age == current_user.age)
    
    if filters['same_gender']:
        query = query.filter(User.gender == current_user.gender)
    
    if filters['opposite_gender']:
        opposite_genders = {'پسر': 'دختر', 'دختر': 'پسر', 'دیگر': 'دیگر'}
        query = query.filter(User.gender == opposite_genders.get(current_user.gender, 'دیگر'))
    
    if filters['same_city']:
        query = query.filter(User.city == current_user.city)
    
    users = query.all()
    
    return render_template_string(HOME_TEMPLATE, users=users, filters=filters)

@app.route('/notifications')
@login_required
def notifications():
    # دریافت اعلانات کاربر
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    
    # پاک کردن اعلان‌های جدید
    for notif in notifications:
        notif.is_read = True
    db.session.commit()
    
    return render_template_string(NOTIFICATIONS_TEMPLATE, notifications=notifications)

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    results = []
    if request.method == 'POST':
        q = request.form.get('query', '').strip()
        if q:
            if q.startswith('@'):
                results = User.query.filter(User.username.like(f"%{q[1:]}%")).all()
            else:
                results = User.query.filter(User.name.like(f"%{q}%")).all()
    return render_template_string(SEARCH_TEMPLATE, results=results)

@app.route('/chat')
@login_required
def chat_list():
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
    
    return render_template_string(CHAT_LIST_TEMPLATE, chat_data=chat_data)

@app.route('/chat/<int:partner_id>', methods=['GET', 'POST'])
@login_required
def chat_room(partner_id):
    partner = User.query.get_or_404(partner_id)
    
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
                message=f"پیام جدید از @{current_user.username}",
                type="message"
            )
            db.session.add(notification)
            db.session.commit()
            
            return jsonify(success=True)
    
    # دریافت پیام‌ها
    messages = Message.query.filter_by(chat_id=chat.id).order_by(Message.timestamp.asc()).all()
    
    return render_template_string(CHAT_ROOM_TEMPLATE, partner=partner, messages=messages, chat=chat)

@app.route('/delete_chat/<int:partner_id>', methods=['POST'])
@login_required
def delete_chat(partner_id):
    chat = Chat.query.filter(
        ((Chat.user_id == current_user.id) & (Chat.partner_id == partner_id)) |
        ((Chat.user_id == partner_id) & (Chat.partner_id == current_user.id))
    ).first()
    
    if chat:
        # حذف پیام‌ها
        Message.query.filter_by(chat_id=chat.id).delete()
        db.session.delete(chat)
        db.session.commit()
        flash("چت با موفقیت حذف شد", "success")
    else:
        flash("چت یافت نشد", "error")
    
    return redirect(url_for('chat_list'))

@app.route('/like/<int:user_id>', methods=['POST'])
@login_required
def like_user(user_id):
    target_user = User.query.get_or_404(user_id)
    
    # بررسی اینکه قبلاً لایک شده یا نه
    existing_notif = Notification.query.filter_by(
        user_id=user_id,
        sender_id=current_user.id,
        type="like"
    ).first()
    
    if existing_notif:
        # حذف لایک
        db.session.delete(existing_notif)
        db.session.commit()
        return jsonify(liked=False)
    else:
        # اضافه کردن لایک
        notification = Notification(
            user_id=user_id,
            sender_id=current_user.id,
            message=f"کاربر @{current_user.username} شما را لایک کرد",
            type="like"
        )
        db.session.add(notification)
        db.session.commit()
        return jsonify(liked=True)

@app.route('/request_chat/<int:user_id>', methods=['POST'])
@login_required
def request_chat(user_id):
    target_user = User.query.get_or_404(user_id)
    
    # ایجاد اعلان درخواست چت
    notification = Notification(
        user_id=user_id,
        sender_id=current_user.id,
        message=f"کاربر @{current_user.username} درخواست چت داده",
        type="chat_request"
    )
    db.session.add(notification)
    db.session.commit()
    
    return jsonify(success=True)

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
        <div class="register-form">
            <h2>خوش آمدید به گویمیکس | GOYIMIX</h2>
            
            <form method="post" enctype="multipart/form-data">
                <div style="text-align: center; margin: 20px 0;">
                    <img id="profile-preview" src="/static/uploads/default.png" 
                         alt="پیش‌نمایش پروفایل" 
                         style="width: 100px; height: 100px; border-radius: 50%; object-fit: cover; display: none;">
                    <br>
                    <label for="profile_pic" class="neon-btn" style="cursor: pointer; margin-top: 10px;">
                        <i class="fas fa-camera"></i> انتخاب عکس
                    </label>
                    <input type="file" id="profile_pic" name="profile_pic" accept="image/*" 
                           onchange="previewImage(this)" style="display: none;">
                </div>
                
                <input type="text" name="name" placeholder="نام (اختیاری)">
                <input type="text" name="username" placeholder="نام کاربری (اجباری)" required>
                <input type="number" name="age" placeholder="سن (اجباری)" min="12" max="80" required>
                
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
                
                <input type="password" name="password" placeholder="رمز عبور (اجباری)" required>
                <input type="password" name="confirm" placeholder="تکرار رمز عبور (اجباری)" required>
                
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
        <div class="login-form">
            <h2>دوباره خوش آمدید</h2>
            
            <form method="post">
                <input type="text" name="username" placeholder="نام کاربری یا نام" required>
                
                <div style="position: relative;">
                    <input type="password" id="password" name="password" placeholder="رمز عبور" required>
                    <span class="toggle-password" onclick="togglePassword()" 
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

DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>داشبورد - GOYIMIX | گویمیکس</title>
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
        <div class="dashboard">
            <h2 style="text-align: center; margin-bottom: 30px;">
                خوش آمدید، {{ current_user.name or current_user.username }}!
            </h2>
            
            <div style="text-align: center; margin: 30px 0;">
                <img src="/static/uploads/{{ current_user.profile_pic }}" 
                     alt="پروفایل" 
                     style="width: 120px; height: 120px; border-radius: 50%; object-fit: cover; border: 3px solid #9B5DE5;">
            </div>
            
            <div style="display: flex; flex-direction: column; gap: 15px; max-width: 400px; margin: 0 auto;">
                <a href="{{ url_for('profile') }}" class="neon-btn" style="text-align: center;">
                    <i class="fas fa-user"></i> پروفایل من
                </a>
                <a href="{{ url_for('home') }}" class="neon-btn" style="text-align: center;">
                    <i class="fas fa-home"></i> کشف پروفایل‌ها
                </a>
                <a href="{{ url_for('search') }}" class="neon-btn" style="text-align: center;">
                    <i class="fas fa-search"></i> جستجوی کاربران
                </a>
                <a href="{{ url_for('chat_list') }}" class="neon-btn" style="text-align: center;">
                    <i class="fas fa-comments"></i> چت‌های من
                </a>
                <a href="{{ url_for('notifications') }}" class="neon-btn" style="text-align: center;">
                    <i class="fas fa-bell"></i> اعلانات
                </a>
                <a href="{{ url_for('logout') }}" class="neon-btn" style="text-align: center; background: linear-gradient(90deg, #ff6b6b, #ff8e8e);">
                    <i class="fas fa-sign-out-alt"></i> خروج از حساب
                </a>
            </div>
        </div>
    </main>
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
    
    <main>
        <div class="profile-page">
            <h2 style="text-align: center; margin-bottom: 20px;">پروفایل شما</h2>
            
            <form method="post" enctype="multipart/form-data">
                <div style="text-align: center; margin: 20px 0;">
                    <img id="profile-preview" 
                         src="/static/uploads/{{ user.profile_pic }}" 
                         alt="پروفایل" 
                         style="width: 120px; height: 120px; border-radius: 50%; object-fit: cover; border: 3px solid #9B5DE5;">
                    <br>
                    <label for="profile_pic" class="neon-btn" style="cursor: pointer; margin-top: 10px;">
                        <i class="fas fa-camera"></i> تغییر عکس
                    </label>
                    <input type="file" id="profile_pic" name="profile_pic" accept="image/*" 
                           onchange="previewImage(this)" style="display: none;">
                </div>
                
                <input type="text" name="name" value="{{ user.name or '' }}" placeholder="نام">
                <input type="text" name="username" value="{{ user.username }}" placeholder="نام کاربری" readonly>
                <input type="number" name="age" value="{{ user.age }}" placeholder="سن" readonly>
                <input type="text" name="gender" value="{{ user.gender }}" placeholder="جنسیت" readonly>
                
                <textarea name="bio" placeholder="بیو">{{ user.bio or '' }}</textarea>
                <textarea name="interests" placeholder="علاقه‌مندی‌ها">{{ user.interests or '' }}</textarea>
                
                <select name="city">
                    {% for city in cities %}
                    <option value="{{ city }}" {% if user.city == city %}selected{% endif %}>
                        {{ city }}
                    </option>
                    {% endfor %}
                </select>
                
                <label style="display: flex; align-items: center; gap: 10px; margin: 15px 0;">
                    <input type="checkbox" name="show" {% if user.show_in_home %}checked{% endif %}>
                    نمایش پروفایل در خانه
                </label>
                
                <button type="submit" class="neon-btn">ذخیره تغییرات</button>
            </form>
            
            <div style="margin-top: 30px; text-align: center;">
                <button onclick="location.href='{{ url_for('logout') }}'" 
                        class="neon-btn" 
                        style="background: linear-gradient(90deg, #ff6b6b, #ff8e8e);">
                    خروج از حساب
                </button>
            </div>
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
            <i class="fas fa-bell"></i>
            <span>اعلان‌ها</span>
        </a>
    </nav>
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
    
    <main>
        <div class="home-page">
            <h2 style="text-align: center; margin-bottom: 20px;">کشف پروفایل‌ها</h2>
            
            <!-- فیلترها -->
            <form method="post" style="margin-bottom: 20px;">
                <div class="filters">
                    <button type="submit" name="same_age" value="1" 
                            class="filter-btn {% if filters.same_age %}active{% endif %}">
                        هم‌سن
                    </button>
                    <button type="submit" name="same_gender" value="1" 
                            class="filter-btn {% if filters.same_gender %}active{% endif %}">
                        هم‌جنسیت
                    </button>
                    <button type="submit" name="opposite_gender" value="1" 
                            class="filter-btn {% if filters.opposite_gender %}active{% endif %}">
                        ناهم‌جنسیت
                    </button>
                    <button type="submit" name="same_city" value="1" 
                            class="filter-btn {% if filters.same_city %}active{% endif %}">
                        هم‌شهر
                    </button>
                </div>
            </form>
            
            <!-- لیست پروفایل‌ها -->
            {% if users %}
                {% for user in users %}
                <div class="profile-card">
                    <img src="/static/uploads/{{ user.profile_pic }}" 
                         alt="{{ user.name or user.username }}">
                    <div class="profile-info">
                        <h3>{{ user.name or user.username }}</h3>
                        <p>@{{ user.username }}</p>
                        <p>{{ user.age }} سال، {{ user.gender }}، {{ user.city }}</p>
                        {% if user.bio %}
                        <p>{{ user.bio }}</p>
                        {% endif %}
                    </div>
                    <div class="profile-actions">
                        <button onclick="likeUser({{ user.id }}, this)" 
                                style="background: #ff6b6b; color: white;">
                            🤍 0
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
            <i class="fas fa-bell"></i>
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
        <div class="notifications-page">
            <h2 style="text-align: center; margin-bottom: 20px;">اعلانات</h2>
            
            {% if notifications %}
                {% for notif in notifications %}
                <div class="notification {% if not notif.is_read %}unread{% endif %}">
                    <p>{{ notif.message }}</p>
                    <small style="color: #aaa;">{{ notif.created_at.strftime('%Y/%m/%d %H:%M') }}</small>
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
            <i class="fas fa-bell"></i>
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
        <div class="search-page">
            <h2 style="text-align: center; margin-bottom: 20px;">جستجوی کاربران</h2>
            
            <form method="post" style="margin-bottom: 30px;">
                <div style="display: flex; gap: 10px;">
                    <input type="text" name="query" placeholder="نام یا @نام کاربری" required>
                    <button type="submit" class="neon-btn">
                        <i class="fas fa-search"></i>
                    </button>
                </div>
            </form>
            
            {% if results %}
                {% for user in results %}
                <div class="profile-card">
                    <img src="/static/uploads/{{ user.profile_pic }}" 
                         alt="{{ user.name or user.username }}">
                    <div class="profile-info">
                        <h3>{{ user.name or user.username }}</h3>
                        <p>@{{ user.username }}</p>
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
            <i class="fas fa-bell"></i>
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
        <div class="chat-list-page">
            <h2 style="text-align: center; margin-bottom: 20px;">چت‌های من</h2>
            
            {% if chat_data %}
                {% for data in chat_data %}
                <div class="profile-card" 
                     onclick="location.href='{{ url_for('chat_room', partner_id=data.partner.id) }}'"
                     style="cursor: pointer;">
                    <img src="/static/uploads/{{ data.partner.profile_pic }}" 
                         alt="{{ data.partner.name or data.partner.username }}">
                    <div class="profile-info">
                        <h3>{{ data.partner.name or data.partner.username }}</h3>
                        <p>@{{ data.partner.username }}</p>
                        {% if data.last_message %}
                        <p style="color: #aaa; font-size: 14px;">
                            {{ data.last_message.content[:30] }}{% if data.last_message.content|length > 30 %}...{% endif %}
                        </p>
                        {% endif %}
                    </div>
                    <div class="profile-actions">
                        <form method="post" action="{{ url_for('delete_chat', partner_id=data.partner.id) }}"
                              style="display: inline;"
                              onsubmit="return confirm('آیا مطمئنید می‌خواهید این چت را حذف کنید؟')">
                            <button type="submit" style="background: #ff6b6b; color: white;">
                                <i class="fas fa-trash"></i>
                            </button>
                        </form>
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
            <i class="fas fa-bell"></i>
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
                <button onclick="history.back()" style="background: none; border: none; color: #00F5D4; font-size: 20px; margin-left: 15px;">
                    ←
                </button>
                <img src="/static/uploads/{{ partner.profile_pic }}" 
                     alt="{{ partner.name or partner.username }}"
                     style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover; margin-left: 10px;">
                <div>
                    <h3 style="margin: 0;">{{ partner.name or partner.username }}</h3>
                    <p style="margin: 0; font-size: 14px; color: #aaa;">@{{ partner.username }}</p>
                </div>
            </div>
            
            <div id="messages" class="chat-messages">
                {% for message in messages %}
                <div class="message {% if message.sender_id == current_user.id %}me{% else %}them{% endif %}">
                    {{ message.content }}
                </div>
                {% endfor %}
            </div>
            
            <div class="chat-input">
                <form method="post" class="chat-form" onsubmit="return sendMessage(this);">
                    <input type="text" name="message" placeholder="پیام..." required>
                    <button type="submit" class="neon-btn">
                        <i class="fas fa-paper-plane"></i>
                    </button>
                </form>
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
                    newMessage.textContent = message;
                    messagesDiv.appendChild(newMessage);
                    messagesDiv.scrollTop = messagesDiv.scrollHeight;
                }
            })
            .catch(error => console.error('Error:', error));
            
            return false;
        }
    </script>
''' + JS_SCRIPT + '''
</body>
</html>
'''

if __name__ == '__main__':
    # ایجاد دیتابیس
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000, host='0.0.0.0')