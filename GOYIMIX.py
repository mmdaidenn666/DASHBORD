from flask import Flask, render_template_string, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///goyimix.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ==================== MODELS ====================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=True)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    interests = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    profile_pic = db.Column(db.String(200), nullable=True, default='default.png')
    visible = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, nullable=False)
    user2_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, nullable=False)
    sender_id = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    message = db.Column(db.String(200), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    type = db.Column(db.String(50), default='info')  # like, chat_request, message
    sender_id = db.Column(db.Integer, nullable=True)

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    liked_user_id = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

CITIES = [
    "شهرک صدرا", "شهرک گلستان", "معالی آباد", "شهرک کشن", "شهرک مهدیه",
    "شهرک زینبیه", "شهرک بعثت", "شهرک والفجر", "شهرک صنعتی عفیف آباد",
    "کوی امام رضا", "شهرک گویم", "شهرک بزین", "شهرک رحمت آباد", "شهرک خورشید",
    "شهرک سلامت", "شهرک فرهنگیان", "کوی زاگرس", "کوی پاسداران", "شهرک عرفان",
    "شهرک هنرستان"
]

# ==================== ROUTES ====================

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('register'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        name = request.form.get('name')
        age = request.form['age']
        gender = request.form['gender']
        bio = request.form.get('bio')
        interests = request.form.get('interests')
        city = request.form['city']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if User.query.filter_by(username=username).first():
            flash("این نام کاربری قبلاً استفاده شده", "error")
            return render_template_string(REGISTER_TEMPLATE, cities=CITIES)

        if password != confirm_password:
            flash("رمز عبور مطابقت ندارد", "error")
            return render_template_string(REGISTER_TEMPLATE, cities=CITIES)

        hashed = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, name=name, age=age, gender=gender, bio=bio, interests=interests, city=city, password=hashed)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('dashboard'))

    return render_template_string(REGISTER_TEMPLATE, cities=CITIES)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter((User.username == username) | (User.name == username)).first()
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
        if 'update_profile' in request.form:
            current_user.name = request.form.get('name', current_user.name)
            current_user.bio = request.form.get('bio', current_user.bio)
            current_user.city = request.form.get('city', current_user.city)
            current_user.visible = 'visible' in request.form
            db.session.commit()
            flash("پروفایل به‌روزرسانی شد", "success")
            return redirect(url_for('profile'))
    
    # تعداد لایک‌ها
    like_count = Like.query.filter_by(liked_user_id=current_user.id).count()
    
    return render_template_string(PROFILE_TEMPLATE, like_count=like_count)

@app.route('/delete_account_request')
@login_required
def delete_account_request():
    return render_template_string(DELETE_ACCOUNT_TEMPLATE)

@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if username != current_user.username:
        flash("نام کاربری اشتباه است", "error")
        return redirect(url_for('delete_account_request'))
    
    if not bcrypt.check_password_hash(current_user.password, password):
        flash("رمز عبور اشتباه است", "error")
        return redirect(url_for('delete_account_request'))
    
    # حذف همه داده‌های مرتبط
    Like.query.filter((Like.user_id == current_user.id) | (Like.liked_user_id == current_user.id)).delete()
    Notification.query.filter_by(user_id=current_user.id).delete()
    chats = Chat.query.filter((Chat.user1_id == current_user.id) | (Chat.user2_id == current_user.id)).all()
    for chat in chats:
        Message.query.filter_by(chat_id=chat.id).delete()
        db.session.delete(chat)
    db.session.delete(current_user)
    db.session.commit()
    logout_user()
    flash("حساب شما با موفقیت حذف شد", "success")
    return redirect(url_for('register'))

@app.route('/home')
@login_required
def home():
    # دریافت فیلترها از session
    filters = session.get('filters', {})
    
    query = User.query.filter(User.id != current_user.id, User.visible == True)
    
    if filters.get('same_age'):
        query = query.filter(User.age == current_user.age)
    if filters.get('same_gender'):
        query = query.filter(User.gender == current_user.gender)
    if filters.get('opposite_gender'):
        opposite_gender = 'دختر' if current_user.gender == 'پسر' else 'پسر'
        query = query.filter(User.gender == opposite_gender)
    if filters.get('same_city'):
        query = query.filter(User.city == current_user.city)
    
    users = query.all()
    
    # بررسی لایک شدن
    liked_users = {}
    for user in users:
        liked = Like.query.filter_by(user_id=current_user.id, liked_user_id=user.id).first()
        liked_users[user.id] = liked is not None
    
    return render_template_string(HOME_TEMPLATE, users=users, filters=filters, liked_users=liked_users)

@app.route('/toggle_filter/<filter_name>')
@login_required
def toggle_filter(filter_name):
    allowed_filters = ['same_age', 'same_gender', 'opposite_gender', 'same_city']
    if filter_name in allowed_filters:
        if 'filters' not in session:
            session['filters'] = {}
        
        # جلوگیری از فعال شدن همزمان هم‌جنسیت و ناهم‌جنسیت
        if filter_name == 'same_gender' and session['filters'].get('opposite_gender'):
            session['filters']['opposite_gender'] = False
        elif filter_name == 'opposite_gender' and session['filters'].get('same_gender'):
            session['filters']['same_gender'] = False
            
        session['filters'][filter_name] = not session['filters'].get(filter_name, False)
        session.modified = True
    return redirect(url_for('home'))

@app.route('/like/<int:user_id>')
@login_required
def like(user_id):
    # بررسی وجود لایک قبلی
    existing_like = Like.query.filter_by(user_id=current_user.id, liked_user_id=user_id).first()
    
    if existing_like:
        # حذف لایک
        db.session.delete(existing_like)
        # حذف اعلان مرتبط
        Notification.query.filter_by(
            user_id=user_id,
            sender_id=current_user.id,
            type='like'
        ).delete()
        db.session.commit()
        liked = False
    else:
        # اضافه کردن لایک
        like = Like(user_id=current_user.id, liked_user_id=user_id)
        db.session.add(like)
        # ایجاد اعلان
        notif = Notification(
            user_id=user_id,
            sender_id=current_user.id,
            message=f"کاربر @{current_user.username} شما را لایک کرد",
            type='like'
        )
        db.session.add(notif)
        db.session.commit()
        liked = True
    
    # محاسبه تعداد لایک‌ها
    like_count = Like.query.filter_by(liked_user_id=user_id).count()
    
    return jsonify(success=True, liked=liked, like_count=like_count)

@app.route('/request_chat/<int:user_id>')
@login_required
def request_chat(user_id):
    notif = Notification(
        user_id=user_id,
        sender_id=current_user.id,
        message=f"کاربر @{current_user.username} درخواست چت داد",
        type='chat_request'
    )
    db.session.add(notif)
    db.session.commit()
    
    # ایجاد چت اگر وجود نداشته باشد
    existing_chat = Chat.query.filter(
        ((Chat.user1_id == current_user.id) & (Chat.user2_id == user_id)) |
        ((Chat.user1_id == user_id) & (Chat.user2_id == current_user.id))
    ).first()
    
    if not existing_chat:
        chat = Chat(user1_id=current_user.id, user2_id=user_id)
        db.session.add(chat)
        db.session.commit()
    
    return jsonify(success=True)

@app.route('/notifications')
@login_required
def notifications():
    notifs = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.timestamp.desc()).all()
    unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    for n in notifs:
        n.is_read = True
    db.session.commit()
    return render_template_string(NOTIFICATIONS_TEMPLATE, notifications=notifs, unread_count=unread_count)

@app.route('/accept_chat/<int:sender_id>')
@login_required
def accept_chat(sender_id):
    # ایجاد چت اگر وجود نداشته باشد
    existing_chat = Chat.query.filter(
        ((Chat.user1_id == current_user.id) & (Chat.user2_id == sender_id)) |
        ((Chat.user1_id == sender_id) & (Chat.user2_id == current_user.id))
    ).first()
    
    if not existing_chat:
        chat = Chat(user1_id=current_user.id, user2_id=sender_id)
        db.session.add(chat)
        db.session.commit()
    
    # حذف اعلان
    Notification.query.filter_by(
        user_id=current_user.id,
        sender_id=sender_id,
        type='chat_request'
    ).delete()
    db.session.commit()
    
    return jsonify(success=True)

@app.route('/reject_chat/<int:sender_id>')
@login_required
def reject_chat(sender_id):
    # حذف اعلان
    Notification.query.filter_by(
        user_id=current_user.id,
        sender_id=sender_id,
        type='chat_request'
    ).delete()
    db.session.commit()
    
    return jsonify(success=True)

@app.route('/block_user/<int:sender_id>')
@login_required
def block_user(sender_id):
    # حذف اعلان
    Notification.query.filter_by(
        user_id=current_user.id,
        sender_id=sender_id,
        type='chat_request'
    ).delete()
    # مسدود کردن کاربر (جلوگیری از ارسال اعلان جدید)
    db.session.commit()
    
    return jsonify(success=True)

@app.route('/search')
@login_required
def search():
    query = request.args.get('q', '')
    if query.startswith('@'):
        users = User.query.filter(User.username.like(f"%{query[1:]}%"), User.visible == True).all()
    else:
        users = User.query.filter(User.name.like(f"%{query}%"), User.visible == True).all()
    
    # بررسی لایک شدن
    liked_users = {}
    for user in users:
        liked = Like.query.filter_by(user_id=current_user.id, liked_user_id=user.id).first()
        liked_users[user.id] = liked is not None
    
    return render_template_string(SEARCH_TEMPLATE, users=users, query=query, liked_users=liked_users)

@app.route('/chat')
@login_required
def chat_list():
    chats = Chat.query.filter((Chat.user1_id == current_user.id) | (Chat.user2_id == current_user.id)).all()
    chat_users = []
    for chat in chats:
        other_id = chat.user2_id if chat.user1_id == current_user.id else chat.user1_id
        user = User.query.get(other_id)
        if user:
            # آخرین پیام
            last_message = Message.query.filter_by(chat_id=chat.id).order_by(Message.timestamp.desc()).first()
            chat_users.append({
                'user': user,
                'last_message': last_message.content if last_message else '',
                'timestamp': last_message.timestamp if last_message else chat.created_at
            })
    return render_template_string(CHAT_LIST_TEMPLATE, chat_users=chat_users)

@app.route('/chat/<int:user_id>')
@login_required
def chat(user_id):
    user = User.query.get_or_404(user_id)
    chat = Chat.query.filter(
        ((Chat.user1_id == current_user.id) & (Chat.user2_id == user_id)) |
        ((Chat.user1_id == user_id) & (Chat.user2_id == current_user.id))
    ).first_or_404()
    
    messages = Message.query.filter_by(chat_id=chat.id).order_by(Message.timestamp.asc()).all()
    return render_template_string(CHAT_TEMPLATE, user=user, messages=messages, chat_id=chat.id)

@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    chat_id = request.form['chat_id']
    content = request.form['content']
    
    message = Message(chat_id=chat_id, sender_id=current_user.id, content=content)
    db.session.add(message)
    db.session.commit()
    
    # اعلان برای طرف مقابل
    chat = Chat.query.get(chat_id)
    other_user_id = chat.user2_id if chat.user1_id == current_user.id else chat.user1_id
    notif = Notification(
        user_id=other_user_id,
        sender_id=current_user.id,
        message=f"پیام جدید از @{current_user.username}",
        type='message'
    )
    db.session.add(notif)
    db.session.commit()
    
    return jsonify(success=True)

@app.route('/delete_chat/<int:user_id>')
@login_required
def delete_chat(user_id):
    chat = Chat.query.filter(
        ((Chat.user1_id == current_user.id) & (Chat.user2_id == user_id)) |
        ((Chat.user1_id == user_id) & (Chat.user2_id == current_user.id))
    ).first()
    if chat:
        # حذف پیام‌ها
        messages = Message.query.filter_by(chat_id=chat.id).all()
        for msg in messages:
            db.session.delete(msg)
        db.session.delete(chat)
        db.session.commit()
    return redirect(url_for('chat_list'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ==================== HTML TEMPLATES ====================

BASE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}GOYIMIX{% endblock %}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: #121212;
            color: #FFFFFF;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            direction: rtl;
            text-align: right;
            padding: 20px;
            min-height: 100vh;
        }
        
        .container {
            max-width: 500px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            position: relative;
        }
        
        .header h1 {
            background: linear-gradient(90deg, #9B5DE5, #00F5D4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 24px;
            margin-bottom: 10px;
            text-shadow: 0 0 10px rgba(155, 93, 229, 0.5);
        }
        
        .back-btn {
            position: absolute;
            left: 0;
            top: 0;
            background: none;
            border: none;
            color: #00F5D4;
            font-size: 24px;
            cursor: pointer;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 5px;
            color: #E0E0E0;
        }
        
        input, select, textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #333;
            border-radius: 10px;
            background: #1E1E1E;
            color: #FFFFFF;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        
        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: #9B5DE5;
            box-shadow: 0 0 15px rgba(155, 93, 229, 0.5);
        }
        
        .btn {
            background: linear-gradient(90deg, #9B5DE5, #00F5D4);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 25px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 0 15px rgba(155, 93, 229, 0.5);
            display: block;
            width: 100%;
            margin-top: 10px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(155, 93, 229, 0.7);
        }
        
        .btn-secondary {
            background: #333;
            box-shadow: 0 0 10px rgba(255, 255, 255, 0.1);
        }
        
        .btn-secondary:hover {
            box-shadow: 0 5px 15px rgba(255, 255, 255, 0.2);
        }
        
        .btn-danger {
            background: linear-gradient(90deg, #F15BB5, #9B5DE5);
            box-shadow: 0 0 15px rgba(241, 91, 181, 0.5);
        }
        
        .error {
            color: #F15BB5;
            background: rgba(241, 91, 181, 0.1);
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            border-left: 4px solid #F15BB5;
        }
        
        .success {
            color: #00F5D4;
            background: rgba(0, 245, 212, 0.1);
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            border-left: 4px solid #00F5D4;
        }
        
        .link {
            color: #00F5D4;
            text-decoration: none;
            display: block;
            margin-top: 15px;
            text-align: center;
        }
        
        .link:hover {
            text-decoration: underline;
        }
        
        .navbar {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: #1E1E1E;
            display: flex;
            justify-content: space-around;
            padding: 15px 0;
            border-top: 1px solid #333;
            z-index: 100;
        }
        
        .nav-item {
            text-align: center;
            color: #E0E0E0;
            text-decoration: none;
            font-size: 12px;
            position: relative;
        }
        
        .nav-item.active {
            color: #00F5D4;
            text-shadow: 0 0 10px rgba(0, 245, 212, 0.5);
        }
        
        .nav-icon {
            font-size: 24px;
            display: block;
            margin-bottom: 5px;
        }
        
        .notification-badge {
            position: absolute;
            top: -5px;
            right: 50%;
            transform: translateX(50%);
            background: #F15BB5;
            color: white;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            font-size: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .card {
            background: #1E1E1E;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
            border: 1px solid #333;
        }
        
        .profile-header {
            text-align: center;
            margin-bottom: 20px;
        }
        
        .profile-pic {
            width: 100px;
            height: 100px;
            border-radius: 50%;
            object-fit: cover;
            border: 3px solid #9B5DE5;
            margin: 0 auto 15px;
            display: block;
        }
        
        .actions {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        
        .action-btn {
            flex: 1;
            padding: 10px;
            border-radius: 10px;
            border: none;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .like-btn {
            background: #333;
            color: white;
        }
        
        .like-btn.liked {
            background: #F15BB5;
            box-shadow: 0 0 15px rgba(241, 91, 181, 0.5);
        }
        
        .chat-btn {
            background: #00F5D4;
            color: black;
        }
        
        .filters {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
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
            color: black;
            box-shadow: 0 0 10px rgba(0, 245, 212, 0.5);
        }
        
        .notification-card {
            background: #1E1E1E;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
            border-left: 4px solid #00F5D4;
        }
        
        .notification-card.like {
            border-left-color: #F15BB5;
        }
        
        .notification-card.chat {
            border-left-color: #00F5D4;
        }
        
        .notification-card.message {
            border-left-color: #9B5DE5;
        }
        
        .notification-actions {
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }
        
        .notification-btn {
            padding: 5px 10px;
            border-radius: 5px;
            border: none;
            cursor: pointer;
            font-size: 12px;
        }
        
        .accept-btn {
            background: #00F5D4;
            color: black;
        }
        
        .reject-btn {
            background: #333;
            color: white;
        }
        
        .block-btn {
            background: #F15BB5;
            color: white;
        }
        
        .chat-message {
            margin-bottom: 15px;
            max-width: 80%;
        }
        
        .message-sender {
            font-weight: bold;
            font-size: 14px;
            margin-bottom: 5px;
        }
        
        .message-content {
            background: #333;
            padding: 10px;
            border-radius: 10px;
            word-wrap: break-word;
        }
        
        .message-time {
            font-size: 12px;
            color: #888;
            margin-top: 5px;
        }
        
        .message-left {
            margin-right: auto;
        }
        
        .message-right {
            margin-left: auto;
            background: linear-gradient(90deg, #9B5DE5, #00F5D4);
        }
        
        .message-right .message-content {
            background: transparent;
            color: white;
        }
        
        .chat-input {
            position: fixed;
            bottom: 70px;
            left: 0;
            right: 0;
            background: #1E1E1E;
            padding: 15px;
            border-top: 1px solid #333;
        }
        
        .chat-input form {
            display: flex;
            gap: 10px;
        }
        
        .chat-input input {
            flex: 1;
        }
        
        .chat-header {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid #333;
        }
        
        .chat-user-info {
            flex: 1;
        }
        
        .chat-user-pic {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            margin-left: 10px;
        }
        
        .delete-account-form {
            background: #1E1E1E;
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
        }
        
        .checkbox-container {
            display: flex;
            align-items: center;
            margin: 20px 0;
        }
        
        .checkbox-container input[type="checkbox"] {
            width: 20px;
            height: 20px;
            margin-left: 10px;
        }
        
        .delete-btn {
            background: linear-gradient(90deg, #F15BB5, #9B5DE5);
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .delete-btn.enabled {
            opacity: 1;
            cursor: pointer;
        }
        
        .profile-stats {
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
            text-align: center;
        }
        
        .stat-item {
            background: #333;
            padding: 15px;
            border-radius: 10px;
            flex: 1;
            margin: 0 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        {% block content %}{% endblock %}
    </div>
    
    {% block navbar %}
    {% if current_user.is_authenticated %}
    <div class="navbar">
        <a href="{{ url_for('profile') }}" class="nav-item {% if request.endpoint == 'profile' %}active{% endif %}">
            <span class="nav-icon">👤</span>
            پروفایل
        </a>
        <a href="{{ url_for('home') }}" class="nav-item {% if request.endpoint == 'home' %}active{% endif %}">
            <span class="nav-icon">🏠</span>
            خانه
        </a>
        <a href="{{ url_for('search') }}" class="nav-item {% if request.endpoint == 'search' %}active{% endif %}">
            <span class="nav-icon">🔍</span>
            جستجو
        </a>
        <a href="{{ url_for('notifications') }}" class="nav-item {% if request.endpoint == 'notifications' %}active{% endif %}">
            <span class="nav-icon">🔔</span>
            اعلان
            {% set unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count() %}
            {% if unread_count > 0 %}
                <span class="notification-badge">{{ unread_count }}</span>
            {% endif %}
        </a>
        <a href="{{ url_for('chat_list') }}" class="nav-item {% if request.endpoint == 'chat_list' %}active{% endif %}">
            <span class="nav-icon">💬</span>
            چت
        </a>
    </div>
    {% endif %}
    {% endblock %}
</body>
</html>
'''

REGISTER_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
<div class="header">
    <h1>خوش آمدید به گویمیکس | GOYIMIX</h1>
</div>

<form method="POST" enctype="multipart/form-data">
    <div style="text-align: center; margin-bottom: 20px;">
        <div style="width: 120px; height: 120px; border: 3px dashed #9B5DE5; border-radius: 50%; margin: 0 auto 15px; display: flex; align-items: center; justify-content: center; cursor: pointer;" onclick="document.getElementById('profile_pic').click()">
            <span style="font-size: 40px;">➕</span>
        </div>
        <input type="file" id="profile_pic" name="profile_pic" accept="image/*" style="display: none;">
        <p>انتخاب عکس پروفایل</p>
    </div>
    
    <div class="form-group">
        <label for="username">@نام کاربری *</label>
        <input type="text" id="username" name="username" required>
    </div>
    
    <div class="form-group">
        <label for="name">نام (اختیاری)</label>
        <input type="text" id="name" name="name">
    </div>
    
    <div class="form-group">
        <label for="age">سن *</label>
        <select id="age" name="age" required>
            <option value="">انتخاب سن</option>
            {% for i in range(12, 81) %}
                <option value="{{ i }}">{{ i }} سال</option>
            {% endfor %}
        </select>
    </div>
    
    <div class="form-group">
        <label for="gender">جنسیت *</label>
        <select id="gender" name="gender" required>
            <option value="">انتخاب جنسیت</option>
            <option value="پسر">پسر</option>
            <option value="دختر">دختر</option>
            <option value="دیگر">دیگر</option>
        </select>
    </div>
    
    <div class="form-group">
        <label for="bio">بیو (اختیاری)</label>
        <textarea id="bio" name="bio" rows="3"></textarea>
    </div>
    
    <div class="form-group">
        <label for="interests">علاقه‌مندی‌ها (اختیاری)</label>
        <input type="text" id="interests" name="interests">
    </div>
    
    <div class="form-group">
        <label for="city">شهر *</label>
        <select id="city" name="city" required>
            <option value="">انتخاب شهر</option>
            {% for city in cities %}
                <option>{{ city }}</option>
            {% endfor %}
        </select>
    </div>
    
    <div class="form-group">
        <label for="password">رمز عبور *</label>
        <input type="password" id="password" name="password" required>
    </div>
    
    <div class="form-group">
        <label for="confirm_password">تکرار رمز عبور *</label>
        <input type="password" id="confirm_password" name="confirm_password" required>
    </div>
    
    <button type="submit" class="btn">ثبت‌نام</button>
</form>

{% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
        {% for category, message in messages %}
            <div class="{{ category }}">{{ message }}</div>
        {% endfor %}
    {% endif %}
{% endwith %}

<a href="{{ url_for('login') }}" class="link">حساب دارید؟ وارد شوید</a>
''')

LOGIN_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
<div class="header">
    <h1>دوباره خوش آمدید</h1>
</div>

<form method="POST">
    <div class="form-group">
        <label for="username">نام کاربری یا نام</label>
        <input type="text" id="username" name="username" required>
    </div>
    
    <div class="form-group">
        <label for="password">رمز عبور</label>
        <input type="password" id="password" name="password" required>
    </div>
    
    <button type="submit" class="btn">ورود</button>
</form>

{% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
        {% for category, message in messages %}
            <div class="{{ category }}">{{ message }}</div>
        {% endfor %}
    {% endif %}
{% endwith %}

<a href="{{ url_for('register') }}" class="link">اگر حسابی ندارید؟ ثبت‌نام کنید</a>
''')

DASHBOARD_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
<div class="header">
    <h1>GOYIMIX | گویمیکس</h1>
</div>

<div style="text-align: center; margin: 50px 0;">
    <h2>به داشبورد خوش آمدید!</h2>
    <p>از منوی پایین برای حرکت استفاده کنید</p>
</div>
''')

PROFILE_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
<div class="header">
    <h1>پروفایل شما</h1>
</div>

<div class="card">
    <div class="profile-header">
        <img src="{{ url_for('static', filename='default.png') }}" alt="پروفایل" class="profile-pic">
        <h2>{{ current_user.name or 'بدون نام' }}</h2>
        <p>@{{ current_user.username }}</p>
    </div>
    
    <div class="profile-stats">
        <div class="stat-item">
            <div style="font-size: 24px; color: #F15BB5;">{{ like_count }}</div>
            <div>لایک</div>
        </div>
        <div class="stat-item">
            <div style="font-size: 24px; color: #00F5D4;">0</div>
            <div>دنبال‌کننده</div>
        </div>
        <div class="stat-item">
            <div style="font-size: 24px; color: #9B5DE5;">0</div>
            <div>دنبال‌شونده</div>
        </div>
    </div>
    
    <form method="POST">
        <input type="hidden" name="update_profile" value="1">
        
        <div class="form-group">
            <label for="name">نام</label>
            <input type="text" id="name" name="name" value="{{ current_user.name or '' }}">
        </div>
        
        <div class="form-group">
            <label for="bio">بیو</label>
            <textarea id="bio" name="bio" rows="3">{{ current_user.bio or '' }}</textarea>
        </div>
        
        <div class="form-group">
            <label for="city">شهر</label>
            <select id="city" name="city">
                {% for city in CITIES %}
                    <option value="{{ city }}" {% if city == current_user.city %}selected{% endif %}>{{ city }}</option>
                {% endfor %}
            </select>
        </div>
        
        <div class="form-group">
            <label>
                <input type="checkbox" name="visible" {% if current_user.visible %}checked{% endif %}>
                نمایش پروفایل در خانه
            </label>
        </div>
        
        <button type="submit" class="btn">ذخیره تغییرات</button>
    </form>
    
    <div style="margin-top: 30px;">
        <a href="{{ url_for('logout') }}" class="btn btn-secondary">خروج از حساب</a>
        
        <a href="{{ url_for('delete_account_request') }}" class="btn btn-danger" style="margin-top: 10px;">حذف حساب</a>
    </div>
</div>

{% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
        {% for category, message in messages %}
            <div class="{{ category }}">{{ message }}</div>
        {% endfor %}
    {% endif %}
{% endwith %}
''')

DELETE_ACCOUNT_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
<div class="header">
    <button class="back-btn" onclick="window.location.href='{{ url_for('profile') }}'">←</button>
    <h1>حذف حساب</h1>
</div>

<div class="delete-account-form">
    <h3 style="color: #F15BB5; text-align: center; margin-bottom: 20px;">آیا مطمئنید که می‌خواهید حساب خود را حذف کنید؟</h3>
    
    <form method="POST" action="{{ url_for('delete_account') }}" id="delete-form">
        <div class="form-group">
            <label for="username">نام کاربری</label>
            <input type="text" id="username" name="username" required>
        </div>
        
        <div class="form-group">
            <label for="password">رمز عبور</label>
            <input type="password" id="password" name="password" required>
        </div>
        
        <div class="checkbox-container">
            <input type="checkbox" id="confirm-delete" onchange="toggleDeleteButton()">
            <label for="confirm-delete">بله، مطمئن هستم که می‌خواهم حساب خود را حذف کنم</label>
        </div>
        
        <button type="submit" class="btn delete-btn" id="delete-btn" disabled>تأیید حذف حساب</button>
    </form>
</div>

<script>
function toggleDeleteButton() {
    const checkbox = document.getElementById('confirm-delete');
    const button = document.getElementById('delete-btn');
    if (checkbox.checked) {
        button.classList.add('enabled');
        button.disabled = false;
    } else {
        button.classList.remove('enabled');
        button.disabled = true;
    }
}
</script>

{% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
        {% for category, message in messages %}
            <div class="{{ category }}">{{ message }}</div>
        {% endfor %}
    {% endif %}
{% endwith %}
''')

HOME_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
<div class="header">
    <h1>خانه</h1>
</div>

<div class="filters">
    <a href="{{ url_for('toggle_filter', filter_name='same_age') }}" class="filter-btn {% if filters.same_age %}active{% endif %}">هم‌سن</a>
    <a href="{{ url_for('toggle_filter', filter_name='same_gender') }}" class="filter-btn {% if filters.same_gender %}active{% endif %}">هم‌جنسیت</a>
    <a href="{{ url_for('toggle_filter', filter_name='opposite_gender') }}" class="filter-btn {% if filters.opposite_gender %}active{% endif %}">ناهم‌جنسیت</a>
    <a href="{{ url_for('toggle_filter', filter_name='same_city') }}" class="filter-btn {% if filters.same_city %}active{% endif %}">هم‌شهر</a>
</div>

{% for user in users %}
<div class="card">
    <div style="display: flex; align-items: center;">
        <img src="{{ url_for('static', filename='default.png') }}" alt="پروفایل" style="width: 60px; height: 60px; border-radius: 50%; margin-left: 15px;">
        
        <div style="flex: 1;">
            <h3>{{ user.name or 'بدون نام' }}</h3>
            <p>@{{ user.username }}</p>
            <p>{{ user.age }} سال | {{ user.gender }} | {{ user.city }}</p>
            {% if user.bio %}
                <p style="color: #888; font-size: 14px; margin-top: 5px;">{{ user.bio }}</p>
            {% endif %}
        </div>
        
        <div style="display: flex; flex-direction: column; gap: 10px;">
            <button onclick="likeUser({{ user.id }})" class="action-btn like-btn {% if liked_users[user.id] %}liked{% endif %}" id="like-{{ user.id }}">❤️</button>
            <button onclick="requestChat({{ user.id }})" class="action-btn chat-btn">💬</button>
        </div>
    </div>
</div>
{% endfor %}

<script>
function likeUser(userId) {
    fetch(`/like/${userId}`)
        .then(response => response.json())
        .then(data => {
            const btn = document.getElementById(`like-${userId}`);
            if (data.liked) {
                btn.classList.add('liked');
            } else {
                btn.classList.remove('liked');
            }
        });
}

function requestChat(userId) {
    fetch(`/request_chat/${userId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('درخواست چت ارسال شد!');
            }
        });
}
</script>
''')

NOTIFICATIONS_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
<div class="header">
    <h1>اعلان‌ها</h1>
</div>

{% for notif in notifications %}
<div class="notification-card {{ notif.type }}">
    <p>{{ notif.message }}</p>
    <small style="color: #888;">{{ notif.timestamp.strftime('%Y/%m/%d %H:%M') }}</small>
    
    {% if notif.type == 'chat_request' %}
    <div class="notification-actions">
        <button onclick="acceptChat({{ notif.sender_id }})" class="notification-btn accept-btn">✅ قبول</button>
        <button onclick="rejectChat({{ notif.sender_id }})" class="notification-btn reject-btn">❌ رد</button>
        <button onclick="blockUser({{ notif.sender_id }})" class="notification-btn block-btn">🚫 بلاک</button>
    </div>
    {% endif %}
</div>
{% endfor %}

{% if not notifications %}
<div style="text-align: center; margin: 50px 0; color: #888;">
    <p>اعلانی وجود ندارد</p>
</div>
{% endif %}

<script>
function acceptChat(senderId) {
    fetch(`/accept_chat/${senderId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            }
        });
}

function rejectChat(senderId) {
    fetch(`/reject_chat/${senderId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            }
        });
}

function blockUser(senderId) {
    fetch(`/block_user/${senderId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            }
        });
}
</script>
''')

SEARCH_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
<div class="header">
    <h1>جستجو</h1>
</div>

<form method="GET" style="margin-bottom: 20px;">
    <div style="display: flex; gap: 10px;">
        <input type="text" name="q" value="{{ query }}" placeholder="جستجو..." style="flex: 1;">
        <button type="submit" class="btn" style="width: auto; padding: 12px 20px;">🔍</button>
    </div>
</form>

{% for user in users %}
<div class="card">
    <div style="display: flex; align-items: center;">
        <img src="{{ url_for('static', filename='default.png') }}" alt="پروفایل" style="width: 60px; height: 60px; border-radius: 50%; margin-left: 15px;">
        
        <div style="flex: 1;">
            <h3>{{ user.name or 'بدون نام' }}</h3>
            <p>@{{ user.username }}</p>
            <p>{{ user.age }} سال | {{ user.gender }} | {{ user.city }}</p>
            {% if user.bio %}
                <p style="color: #888; font-size: 14px; margin-top: 5px;">{{ user.bio }}</p>
            {% endif %}
        </div>
        
        <div style="display: flex; flex-direction: column; gap: 10px;">
            <button onclick="likeUser({{ user.id }})" class="action-btn like-btn {% if liked_users[user.id] %}liked{% endif %}" id="like-{{ user.id }}">❤️</button>
            <button onclick="requestChat({{ user.id }})" class="action-btn chat-btn">💬</button>
        </div>
    </div>
</div>
{% endfor %}

<script>
function likeUser(userId) {
    fetch(`/like/${userId}`)
        .then(response => response.json())
        .then(data => {
            const btn = document.getElementById(`like-${userId}`);
            if (data.liked) {
                btn.classList.add('liked');
            } else {
                btn.classList.remove('liked');
            }
        });
}

function requestChat(userId) {
    fetch(`/request_chat/${userId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('درخواست چت ارسال شد!');
            }
        });
}
</script>
''')

CHAT_LIST_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
<div class="header">
    <h1>چت‌ها</h1>
</div>

{% for chat_user in chat_users %}
<div class="card" style="display: flex; align-items: center;">
    <img src="{{ url_for('static', filename='default.png') }}" alt="پروفایل" style="width: 50px; height: 50px; border-radius: 50%; margin-left: 15px;">
    
    <div style="flex: 1;">
        <h3>{{ chat_user.user.name or 'بدون نام' }}</h3>
        <p>@{{ chat_user.user.username }}</p>
        {% if chat_user.last_message %}
            <p style="color: #888; font-size: 14px; margin-top: 5px;">{{ chat_user.last_message[:30] }}{% if chat_user.last_message|length > 30 %}...{% endif %}</p>
        {% endif %}
    </div>
    
    <div style="text-align: left;">
        <a href="{{ url_for('chat', user_id=chat_user.user.id) }}" class="btn" style="padding: 8px 15px; font-size: 14px; margin-bottom: 10px;">باز کردن</a>
        <a href="{{ url_for('delete_chat', user_id=chat_user.user.id) }}" class="btn" style="padding: 8px 15px; font-size: 14px; background: #F15BB5;">حذف</a>
    </div>
</div>
{% endfor %}

{% if not chat_users %}
<div style="text-align: center; margin: 50px 0; color: #888;">
    <p>چتی وجود ندارد</p>
</div>
{% endif %}
''')

CHAT_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
<div class="chat-header">
    <button class="back-btn" onclick="window.location.href='{{ url_for('chat_list') }}'">←</button>
    <div class="chat-user-info">
        <h3>{{ user.name or 'بدون نام' }}</h3>
        <p>@{{ user.username }}</p>
    </div>
    <img src="{{ url_for('static', filename='default.png') }}" alt="پروفایل" class="chat-user-pic">
</div>

<div id="messages" style="margin-bottom: 100px;">
    {% for message in messages %}
        <div class="chat-message {% if message.sender_id == current_user.id %}message-right{% else %}message-left{% endif %}">
            <div class="message-content">
                {{ message.content }}
            </div>
            <div class="message-time">{{ message.timestamp.strftime('%H:%M') }}</div>
        </div>
    {% endfor %}
</div>

<div class="chat-input">
    <form id="message-form">
        <input type="hidden" id="chat_id" value="{{ chat_id }}">
        <input type="text" id="content" placeholder="پیام خود را بنویسید..." required>
        <button type="submit" class="btn" style="width: auto; padding: 12px 20px;">ارسال</button>
    </form>
</div>

<script>
document.getElementById('message-form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const chatId = document.getElementById('chat_id').value;
    const content = document.getElementById('content').value;
    
    fetch('/send_message', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `chat_id=${chatId}&content=${encodeURIComponent(content)}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('content').value = '';
            location.reload();
        }
    });
});
</script>
''')

# ==================== RUN ====================

if __name__ == '__main__':
    if not os.path.exists('goyimix.db'):
        with app.app_context():
            db.create_all()
    app.run(debug=True, host='0.0.0.0', port=8000)