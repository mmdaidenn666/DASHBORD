"""
GOYIMIX - Social Network Application
Version: 1.0.0
Author: GOYIMIX Team
Description: A modern social networking platform for Gen Z and Alpha users
"""

import os
import uuid
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps
from threading import Thread
import time

from flask import Flask, render_template_string, request, redirect, url_for, flash, session, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.utils import secure_filename
from sqlalchemy import func, desc, asc
from sqlalchemy.orm import sessionmaker

# ====================================================================================================
# APPLICATION CONFIGURATION
# ====================================================================================================

# ایجاد اپ Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///goyimix.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'pool_timeout': 900,
    'max_overflow': 0,
    'pool_size': 20,
    'echo': False
}
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

# ایجاد پوشه‌ها اگر وجود نداشته باشند
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)
os.makedirs('static/images', exist_ok=True)
os.makedirs('logs', exist_ok=True)

# ابزارها
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# ====================================================================================================
# LOGGING SYSTEM
# ====================================================================================================

import logging
from logging.handlers import RotatingFileHandler

# تنظیم لاگ‌نویسی
handler = RotatingFileHandler('logs/goyimix.log', maxBytes=10000000, backupCount=5)
handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

# ====================================================================================================
# DATABASE MODELS
# ====================================================================================================

class User(UserMixin, db.Model):
    """
    مدل کاربران
    """
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False, index=True)
    name = db.Column(db.String(150))
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    bio = db.Column(db.Text)
    interests = db.Column(db.Text)
    city = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    profile_pic = db.Column(db.String(200), default='default.png')
    show_in_home = db.Column(db.Boolean, default=True)
    is_online = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # روابط
    chats_sent = db.relationship('Chat', foreign_keys='Chat.user_id', backref='sender', lazy='dynamic')
    chats_received = db.relationship('Chat', foreign_keys='Chat.partner_id', backref='receiver', lazy='dynamic')
    messages_sent = db.relationship('Message', foreign_keys='Message.sender_id', backref='message_sender', lazy='dynamic')
    messages_received = db.relationship('Message', foreign_keys='Message.receiver_id', backref='message_receiver', lazy='dynamic')
    notifications_sent = db.relationship('Notification', foreign_keys='Notification.sender_id', backref='notification_sender', lazy='dynamic')
    notifications_received = db.relationship('Notification', foreign_keys='Notification.user_id', backref='notification_receiver', lazy='dynamic')
    likes_given = db.relationship('Like', foreign_keys='Like.user_id', backref='liker', lazy='dynamic')
    likes_received = db.relationship('Like', foreign_keys='Like.liked_user_id', backref='liked', lazy='dynamic')
    blocks_given = db.relationship('Block', foreign_keys='Block.blocker_id', backref='blocker', lazy='dynamic')
    blocks_received = db.relationship('Block', foreign_keys='Block.blocked_id', backref='blocked', lazy='dynamic')
    reports_made = db.relationship('Report', foreign_keys='Report.reporter_id', backref='reporter', lazy='dynamic')
    reports_received = db.relationship('Report', foreign_keys='Report.reported_user_id', backref='reported', lazy='dynamic')
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='commenter', lazy='dynamic')
    reactions = db.relationship('Reaction', backref='reactor', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def get_unread_notifications_count(self):
        """دریافت تعداد اعلانات خوانده نشده"""
        return Notification.query.filter_by(user_id=self.id, is_read=False).count()
    
    def get_unread_messages_count(self):
        """دریافت تعداد پیام‌های خوانده نشده"""
        return Message.query.filter_by(receiver_id=self.id, is_read=False).count()
    
    def get_friends_count(self):
        """دریافت تعداد دوستان"""
        return Chat.query.filter(
            (Chat.user_id == self.id) | (Chat.partner_id == self.id)
        ).count()
    
    def get_posts_count(self):
        """دریافت تعداد پست‌ها"""
        return Post.query.filter_by(user_id=self.id).count()
    
    def get_likes_count(self):
        """دریافت تعداد لایک‌ها"""
        return Like.query.filter_by(liked_user_id=self.id).count()
    
    def is_blocked_by(self, user_id):
        """بررسی بلاک بودن توسط کاربر"""
        return Block.query.filter_by(
            blocker_id=user_id,
            blocked_id=self.id
        ).first() is not None
    
    def has_blocked(self, user_id):
        """بررسی بلاک کردن کاربر"""
        return Block.query.filter_by(
            blocker_id=self.id,
            blocked_id=user_id
        ).first() is not None
    
    def is_friend_with(self, user_id):
        """بررسی دوست بودن با کاربر"""
        return Chat.query.filter(
            ((Chat.user_id == self.id) & (Chat.partner_id == user_id)) |
            ((Chat.user_id == user_id) & (Chat.partner_id == self.id))
        ).first() is not None
    
    def get_mutual_friends_count(self, user_id):
        """دریافت تعداد دوستان مشترک"""
        my_friends = set([chat.partner_id if chat.user_id == self.id else chat.user_id 
                         for chat in self.chats_sent.union(self.chats_received).all()])
        other_friends = set([chat.partner_id if chat.user_id == user_id else chat.user_id 
                            for chat in User.query.get(user_id).chats_sent.union(
                                User.query.get(user_id).chats_received).all()])
        return len(my_friends.intersection(other_friends))
    
    def update_last_seen(self):
        """بروزرسانی زمان آخرین فعالیت"""
        self.last_seen = datetime.utcnow()
        db.session.commit()
    
    def get_online_status(self):
        """دریافت وضعیت آنلاین بودن"""
        if not self.is_online:
            return 'آفلاین'
        if datetime.utcnow() - self.last_seen < timedelta(minutes=5):
            return 'آنلاین'
        return 'آفلاین'
    
    def get_profile_completeness(self):
        """دریافت درصد تکمیل پروفایل"""
        total_fields = 7
        completed_fields = 0
        
        if self.name:
            completed_fields += 1
        if self.bio:
            completed_fields += 1
        if self.interests:
            completed_fields += 1
        if self.city:
            completed_fields += 1
        if self.age:
            completed_fields += 1
        if self.gender:
            completed_fields += 1
        if self.profile_pic and self.profile_pic != 'default.png':
            completed_fields += 1
            
        return int((completed_fields / total_fields) * 100)

class Chat(db.Model):
    """
    مدل چت‌ها
    """
    __tablename__ = 'chat'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    partner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # روابط
    messages = db.relationship('Message', backref='chat', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Chat {self.id}>'
    
    def get_unread_messages_count(self, user_id):
        """دریافت تعداد پیام‌های خوانده نشده برای کاربر"""
        return Message.query.filter_by(
            chat_id=self.id,
            receiver_id=user_id,
            is_read=False
        ).count()
    
    def get_last_message(self):
        """دریافت آخرین پیام"""
        return Message.query.filter_by(chat_id=self.id).order_by(desc(Message.timestamp)).first()
    
    def mark_as_read(self, user_id):
        """علامت‌گذاری چت به عنوان خوانده شده"""
        messages = Message.query.filter_by(
            chat_id=self.id,
            receiver_id=user_id,
            is_read=False
        ).all()
        for message in messages:
            message.is_read = True
        db.session.commit()

class Message(db.Model):
    """
    مدل پیام‌ها
    """
    __tablename__ = 'message'
    
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='text')  # text, image, video, voice, file, sticker
    file_path = db.Column(db.String(200))
    file_name = db.Column(db.String(200))
    file_size = db.Column(db.Integer)
    is_read = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<Message {self.id}>'
    
    def get_time_formatted(self):
        """دریافت زمان به صورت فرمت‌شده"""
        now = datetime.utcnow()
        diff = now - self.timestamp
        
        if diff.days > 0:
            return f"{diff.days} روز پیش"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} ساعت پیش"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} دقیقه پیش"
        else:
            return "لحظاتی پیش"
    
    def is_recent(self):
        """بررسی اخیر بودن پیام"""
        return datetime.utcnow() - self.timestamp < timedelta(hours=1)

class Notification(db.Model):
    """
    مدل اعلانات
    """
    __tablename__ = 'notification'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # like, chat_request, message, follow, comment, mention
    related_id = db.Column(db.Integer)  # ID مرتبط با نوع اعلان
    is_read = db.Column(db.Boolean, default=False, index=True)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Notification {self.id}>'
    
    def get_time_formatted(self):
        """دریافت زمان به صورت فرمت‌شده"""
        now = datetime.utcnow()
        diff = now - self.created_at
        
        if diff.days > 0:
            return f"{diff.days} روز پیش"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} ساعت پیش"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} دقیقه پیش"
        else:
            return "لحظاتی پیش"
    
    def mark_as_read(self):
        """علامت‌گذاری اعلان به عنوان خوانده شده"""
        self.is_read = True
        self.updated_at = datetime.utcnow()
        db.session.commit()

class Block(db.Model):
    """
    مدل بلاک کردن کاربران
    """
    __tablename__ = 'block'
    
    id = db.Column(db.Integer, primary_key=True)
    blocker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    blocked_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    reason = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Block {self.id}>'

class Like(db.Model):
    """
    مدل لایک‌ها
    """
    __tablename__ = 'like'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    liked_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Like {self.id}>'

class Report(db.Model):
    """
    مدل گزارش‌ها
    """
    __tablename__ = 'report'
    
    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    reported_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    report_type = db.Column(db.String(50), nullable=False)  # spam, harassment, inappropriate_content, fake_profile
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, reviewed, resolved, dismissed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    resolved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __repr__(self):
        return f'<Report {self.id}>'

class Post(db.Model):
    """
    مدل پست‌ها
    """
    __tablename__ = 'post'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    media_type = db.Column(db.String(20))  # text, image, video
    media_url = db.Column(db.String(200))
    privacy = db.Column(db.String(20), default='public')  # public, friends, private
    likes_count = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    shares_count = db.Column(db.Integer, default=0)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # روابط
    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    reactions = db.relationship('Reaction', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Post {self.id}>'
    
    def get_time_formatted(self):
        """دریافت زمان به صورت فرمت‌شده"""
        now = datetime.utcnow()
        diff = now - self.created_at
        
        if diff.days > 0:
            return f"{diff.days} روز پیش"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} ساعت پیش"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} دقیقه پیش"
        else:
            return "لحظاتی پیش"

class Comment(db.Model):
    """
    مدل کامنت‌ها
    """
    __tablename__ = 'comment'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    likes_count = db.Column(db.Integer, default=0)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # روابط
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    reactions = db.relationship('Reaction', backref='comment', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Comment {self.id}>'

class Reaction(db.Model):
    """
    مدل ری‌اکشن‌ها (لایک، عشق، خنده، غم، تعجب، خشم)
    """
    __tablename__ = 'reaction'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    reaction_type = db.Column(db.String(20), nullable=False)  # like, love, laugh, sad, wow, angry
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Reaction {self.id}>'

class FriendRequest(db.Model):
    """
    مدل درخواست‌های دوستی
    """
    __tablename__ = 'friend_request'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected, blocked
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<FriendRequest {self.id}>'

class ActivityLog(db.Model):
    """
    مدل لاگ فعالیت‌ها
    """
    __tablename__ = 'activity_log'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ActivityLog {self.id}>'

# ====================================================================================================
# USER LOADER
# ====================================================================================================

@login_manager.user_loader
def load_user(user_id):
    """بارگذاری کاربر برای Flask-Login"""
    try:
        return User.query.get(int(user_id))
    except Exception as e:
        app.logger.error(f"Error loading user {user_id}: {str(e)}")
        return None

# ====================================================================================================
# UTILITY FUNCTIONS
# ====================================================================================================

def log_activity(user_id, action, details=None, request=None):
    """لاگ کردن فعالیت کاربر"""
    try:
        activity = ActivityLog(
            user_id=user_id,
            action=action,
            details=json.dumps(details) if details else None,
            ip_address=request.remote_addr if request else None,
            user_agent=request.headers.get('User-Agent') if request else None
        )
        db.session.add(activity)
        db.session.commit()
    except Exception as e:
        app.logger.error(f"Error logging activity: {str(e)}")
        db.session.rollback()

def generate_unique_filename(filename):
    """تولید نام فایل منحصر به فرد"""
    name, ext = os.path.splitext(filename)
    unique_name = f"{uuid.uuid4().hex}_{int(time.time())}{ext}"
    return secure_filename(unique_name)

def allowed_file(filename):
    """بررسی مجاز بودن نوع فایل"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi', 'webm', 'mp3', 'wav', 'ogg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_username(username):
    """اعتبارسنجی نام کاربری"""
    if len(username) < 3 or len(username) > 30:
        return False, "نام کاربری باید بین 3 تا 30 کاراکتر باشد"
    
    if not username.replace('_', '').replace('-', '').isalnum():
        return False, "نام کاربری فقط می‌تواند شامل حروف، اعداد، خط تیره و زیرخط باشد"
    
    if User.query.filter_by(username=username).first():
        return False, "این نام کاربری قبلاً استفاده شده است"
    
    return True, "نام کاربری معتبر است"

def validate_password(password):
    """اعتبارسنجی رمز عبور"""
    if len(password) < 6:
        return False, "رمز عبور باید حداقل 6 کاراکتر باشد"
    
    if len(password) > 128:
        return False, "رمز عبور باید حداکثر 128 کاراکتر باشد"
    
    return True, "رمز عبور معتبر است"

def hash_password(password):
    """هش کردن رمز عبور"""
    return bcrypt.generate_password_hash(password).decode('utf-8')

def check_password(hashed_password, password):
    """بررسی رمز عبور"""
    return bcrypt.check_password_hash(hashed_password, password)

def send_notification(user_id, sender_id, message, notification_type, related_id=None):
    """ارسال اعلان"""
    try:
        notification = Notification(
            user_id=user_id,
            sender_id=sender_id,
            message=message,
            type=notification_type,
            related_id=related_id
        )
        db.session.add(notification)
        db.session.commit()
        
        # ارسال اعلان لحظه‌ای اگر کاربر آنلاین باشد
        socketio.emit('new_notification', {
            'user_id': user_id,
            'message': message,
            'type': notification_type,
            'timestamp': datetime.utcnow().isoformat()
        }, room=f'user_{user_id}')
        
        return notification
    except Exception as e:
        app.logger.error(f"Error sending notification: {str(e)}")
        db.session.rollback()
        return None

def get_user_stats(user_id):
    """دریافت آمار کاربر"""
    user = User.query.get(user_id)
    if not user:
        return None
    
    stats = {
        'friends_count': user.get_friends_count(),
        'posts_count': user.get_posts_count(),
        'likes_count': user.get_likes_count(),
        'unread_notifications': user.get_unread_notifications_count(),
        'unread_messages': user.get_unread_messages_count(),
        'profile_completeness': user.get_profile_completeness(),
        'online_status': user.get_online_status()
    }
    
    return stats

def get_trending_users(limit=10):
    """دریافت کاربران پرطرفدار"""
    trending = db.session.query(
        User,
        func.count(Like.id).label('likes_count')
    ).join(
        Like, Like.liked_user_id == User.id
    ).group_by(
        User.id
    ).order_by(
        desc('likes_count')
    ).limit(limit).all()
    
    return [user for user, likes_count in trending]

def get_suggested_users(current_user_id, limit=5):
    """دریافت کاربران پیشنهادی"""
    # کاربرانی که با دوستان مشترک دارند
    suggested = db.session.query(
        User,
        func.count(Chat.id).label('mutual_friends')
    ).join(
        Chat, 
        ((Chat.user_id == User.id) & (Chat.partner_id.in_(
            db.session.query(Chat.partner_id).filter(Chat.user_id == current_user_id)
        ))) |
        ((Chat.partner_id == User.id) & (Chat.user_id.in_(
            db.session.query(Chat.partner_id).filter(Chat.user_id == current_user_id)
        )))
    ).filter(
        User.id != current_user_id,
        ~User.id.in_(db.session.query(Block.blocked_id).filter(Block.blocker_id == current_user_id))
    ).group_by(
        User.id
    ).order_by(
        desc('mutual_friends')
    ).limit(limit).all()
    
    return [user for user, mutual_friends in suggested]

# ====================================================================================================
# SOCKET.IO EVENTS
# ====================================================================================================

@socketio.on('connect')
def handle_connect():
    """اتصال کاربر به Socket.IO"""
    if current_user.is_authenticated:
        # به اتاق کاربر بپیوند
        join_room(f'user_{current_user.id}')
        
        # به‌روزرسانی وضعیت آنلاین بودن
        current_user.is_online = True
        current_user.update_last_seen()
        
        # اطلاع دیگر کاربران از آنلاین شدن
        socketio.emit('user_online', {
            'user_id': current_user.id,
            'username': current_user.username
        }, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    """قطع اتصال کاربر از Socket.IO"""
    if current_user.is_authenticated:
        # به‌روزرسانی وضعیت آفلاین بودن
        current_user.is_online = False
        db.session.commit()
        
        # اطلاع دیگر کاربران از آفلاین شدن
        socketio.emit('user_offline', {
            'user_id': current_user.id,
            'username': current_user.username
        }, broadcast=True)

@socketio.on('send_message')
def handle_send_message(data):
    """دریافت و ارسال پیام لحظه‌ای"""
    if not current_user.is_authenticated:
        return
    
    try:
        chat_id = data.get('chat_id')
        content = data.get('content', '').strip()
        
        if not content or len(content) > 1000:
            return
        
        # پیدا کردن چت
        chat = Chat.query.get(chat_id)
        if not chat:
            return
        
        # بررسی دسترسی به چت
        if current_user.id not in [chat.user_id, chat.partner_id]:
            return
        
        # تعیین گیرنده
        receiver_id = chat.partner_id if current_user.id == chat.user_id else chat.user_id
        
        # بررسی بلاک بودن
        if Block.query.filter_by(
            blocker_id=receiver_id,
            blocked_id=current_user.id
        ).first():
            return
        
        # ایجاد پیام
        message = Message(
            chat_id=chat_id,
            sender_id=current_user.id,
            receiver_id=receiver_id,
            content=content,
            message_type='text'
        )
        db.session.add(message)
        db.session.commit()
        
        # ارسال پیام به هر دو طرف
        message_data = {
            'id': message.id,
            'sender_id': message.sender_id,
            'receiver_id': message.receiver_id,
            'content': message.content,
            'timestamp': message.timestamp.isoformat(),
            'is_read': message.is_read,
            'time_formatted': message.get_time_formatted()
        }
        
        # ارسال به فرستنده
        socketio.emit('receive_message', message_data, room=f'user_{current_user.id}')
        
        # ارسال به گیرنده
        socketio.emit('receive_message', message_data, room=f'user_{receiver_id}')
        
        # به‌روزرسانی چت
        chat.updated_at = datetime.utcnow()
        db.session.commit()
        
    except Exception as e:
        app.logger.error(f"Error handling send_message: {str(e)}")
        db.session.rollback()

@socketio.on('typing')
def handle_typing(data):
    """دریافت وضعیت تایپ کردن"""
    if not current_user.is_authenticated:
        return
    
    try:
        chat_id = data.get('chat_id')
        is_typing = data.get('is_typing', False)
        
        # پیدا کردن چت
        chat = Chat.query.get(chat_id)
        if not chat:
            return
        
        # بررسی دسترسی به چت
        if current_user.id not in [chat.user_id, chat.partner_id]:
            return
        
        # تعیین گیرنده
        receiver_id = chat.partner_id if current_user.id == chat.user_id else chat.user_id
        
        # ارسال وضعیت تایپ به گیرنده
        socketio.emit('typing_status', {
            'user_id': current_user.id,
            'username': current_user.username,
            'is_typing': is_typing,
            'chat_id': chat_id
        }, room=f'user_{receiver_id}')
        
    except Exception as e:
        app.logger.error(f"Error handling typing: {str(e)}")

@socketio.on('mark_as_read')
def handle_mark_as_read(data):
    """علامت‌گذاری پیام‌ها به عنوان خوانده شده"""
    if not current_user.is_authenticated:
        return
    
    try:
        chat_id = data.get('chat_id')
        
        # پیدا کردن چت
        chat = Chat.query.get(chat_id)
        if not chat:
            return
        
        # بررسی دسترسی به چت
        if current_user.id not in [chat.user_id, chat.partner_id]:
            return
        
        # علامت‌گذاری پیام‌ها به عنوان خوانده شده
        messages = Message.query.filter_by(
            chat_id=chat_id,
            receiver_id=current_user.id,
            is_read=False
        ).all()
        
        for message in messages:
            message.is_read = True
        
        db.session.commit()
        
        # ارسال به‌روزرسانی به هر دو طرف
        socketio.emit('messages_read', {
            'chat_id': chat_id,
            'user_id': current_user.id
        }, room=f'user_{current_user.id}')
        
        receiver_id = chat.partner_id if current_user.id == chat.user_id else chat.user_id
        socketio.emit('messages_read', {
            'chat_id': chat_id,
            'user_id': current_user.id
        }, room=f'user_{receiver_id}')
        
    except Exception as e:
        app.logger.error(f"Error handling mark_as_read: {str(e)}")
        db.session.rollback()

# ====================================================================================================
# DECORATORS
# ====================================================================================================

def admin_required(f):
    """دکوراتور برای صفحات مدیریت"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        # اینجا می‌توانید بررسی نقش مدیر را اضافه کنید
        return f(*args, **kwargs)
    return decorated_function

def online_required(f):
    """دکوراتور برای بررسی آنلاین بودن کاربر"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            current_user.update_last_seen()
        return f(*args, **kwargs)
    return decorated_function

# ====================================================================================================
# ROUTES
# ====================================================================================================

@app.route('/')
def index():
    """صفحه اصلی"""
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return redirect(url_for('register'))

@app.route('/register', methods=['GET', 'POST'])
@online_required
def register():
    """صفحه ثبت‌نام"""
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            confirm = request.form.get('confirm', '')
            age = request.form.get('age', '')
            gender = request.form.get('gender', '')
            city = request.form.get('city', '')
            name = request.form.get('name', '').strip()
            bio = request.form.get('bio', '').strip()
            interests = request.form.get('interests', '').strip()

            # اعتبارسنجی ورودی‌ها
            if not username:
                flash("نام کاربری الزامی است", "error")
                return render_template_string(REGISTER_TEMPLATE, cities=CITIES)

            # اضافه کردن @ به ابتدای نام کاربری
            if not username.startswith('@'):
                username = '@' + username

            # بررسی نام کاربری
            is_valid, message = validate_username(username)
            if not is_valid:
                flash(message, "error")
                return render_template_string(REGISTER_TEMPLATE, cities=CITIES)

            # بررسی رمز عبور
            is_valid, message = validate_password(password)
            if not is_valid:
                flash(message, "error")
                return render_template_string(REGISTER_TEMPLATE, cities=CITIES)

            if password != confirm:
                flash("رمز عبور مطابقت ندارد", "error")
                return render_template_string(REGISTER_TEMPLATE, cities=CITIES)

            if not age or not age.isdigit() or int(age) < 12 or int(age) > 80:
                flash("سن باید بین 12 تا 80 سال باشد", "error")
                return render_template_string(REGISTER_TEMPLATE, cities=CITIES)

            if not gender:
                flash("جنسیت الزامی است", "error")
                return render_template_string(REGISTER_TEMPLATE, cities=CITIES)

            if not city:
                flash("شهر الزامی است", "error")
                return render_template_string(REGISTER_TEMPLATE, cities=CITIES)

            # هش کردن رمز عبور
            hashed_password = hash_password(password)
            
            # ایجاد کاربر
            user = User(
                username=username,
                name=name,
                age=int(age),
                gender=gender,
                bio=bio,
                interests=interests,
                city=city,
                password=hashed_password,
                profile_pic='default.png'
            )
            db.session.add(user)
            db.session.commit()
            
            # لاگ فعالیت
            log_activity(user.id, 'register', {'ip': request.remote_addr}, request)
            
            # ورود خودکار کاربر
            login_user(user)
            
            # اعلان خوش‌آمدگویی
            send_notification(user.id, None, "🎉 به گویمیکس خوش آمدید!", "welcome")
            
            flash("🎉 خوش آمدید به گویمیکس", "success")
            return redirect(url_for('home'))
            
        except Exception as e:
            app.logger.error(f"Registration error: {str(e)}")
            db.session.rollback()
            flash("خطا در ثبت‌نام. لطفاً دوباره تلاش کنید", "error")
            return render_template_string(REGISTER_TEMPLATE, cities=CITIES)

    return render_template_string(REGISTER_TEMPLATE, cities=CITIES)

@app.route('/login', methods=['GET', 'POST'])
@online_required
def login():
    """صفحه ورود"""
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            
            if not username or not password:
                flash("نام کاربری و رمز عبور الزامی است", "error")
                return render_template_string(LOGIN_TEMPLATE)
            
            # پیدا کردن کاربر
            user = User.query.filter_by(username=username).first()
            if not user:
                flash("نام کاربری یا رمز اشتباه است", "error")
                return render_template_string(LOGIN_TEMPLATE)
            
            # بررسی رمز عبور
            if not check_password(user.password, password):
                flash("نام کاربری یا رمز اشتباه است", "error")
                return render_template_string(LOGIN_TEMPLATE)
            
            # ورود کاربر
            login_user(user)
            
            # به‌روزرسانی وضعیت آنلاین بودن
            user.is_online = True
            user.update_last_seen()
            db.session.commit()
            
            # لاگ فعالیت
            log_activity(user.id, 'login', {'ip': request.remote_addr}, request)
            
            return redirect(url_for('home'))
            
        except Exception as e:
            app.logger.error(f"Login error: {str(e)}")
            flash("خطا در ورود. لطفاً دوباره تلاش کنید", "error")
            return render_template_string(LOGIN_TEMPLATE)
    
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/home')
@login_required
@online_required
def home():
    """صفحه خانه"""
    try:
        # دریافت فیلترها از session
        filters = session.get('home_filters', {
            'same_age': False,
            'same_gender': False,
            'opposite_gender': False,
            'same_city': False
        })
        
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
        
        users = query.limit(50).all()
        
        # دریافت تعداد لایک‌ها برای هر کاربر
        for user in users:
            like_count = Like.query.filter_by(liked_user_id=user.id).count()
            user.like_count = like_count
        
        # دریافت تعداد اعلانات خوانده نشده
        unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        
        # دریافت آمار کاربر
        user_stats = get_user_stats(current_user.id)
        
        return render_template_string(HOME_TEMPLATE, 
                                    users=users, 
                                    filters=filters, 
                                    unread_count=unread_count,
                                    user_stats=user_stats)
    except Exception as e:
        app.logger.error(f"Home page error: {str(e)}")
        flash("خطا در بارگذاری صفحه", "error")
        return redirect(url_for('home'))

@app.route('/home_filters', methods=['POST'])
@login_required
def home_filters():
    """به‌روزرسانی فیلترهای صفحه خانه"""
    try:
        # به‌روزرسانی فیلترها
        filters = {
            'same_age': 'same_age' in request.form,
            'same_gender': 'same_gender' in request.form,
            'opposite_gender': 'opposite_gender' in request.form,
            'same_city': 'same_city' in request.form
        }
        session['home_filters'] = filters
        return redirect(url_for('home'))
    except Exception as e:
        app.logger.error(f"Home filters error: {str(e)}")
        flash("خطا در به‌روزرسانی فیلترها", "error")
        return redirect(url_for('home'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
@online_required
def profile():
    """صفحه پروفایل"""
    if request.method == 'POST':
        try:
            current_user.name = request.form.get('name', '').strip()
            current_user.bio = request.form.get('bio', '').strip()
            current_user.interests = request.form.get('interests', '').strip()
            current_user.city = request.form.get('city', '')
            current_user.show_in_home = 'show' in request.form
            
            # به‌روزرسانی سن و جنسیت
            age = request.form.get('age', '')
            if age and age.isdigit() and 12 <= int(age) <= 80:
                current_user.age = int(age)
            
            gender = request.form.get('gender', '')
            if gender:
                current_user.gender = gender
            
            db.session.commit()
            
            # لاگ فعالیت
            log_activity(current_user.id, 'update_profile', None, request)
            
            flash("پروفایل به‌روز شد", "success")
        except Exception as e:
            app.logger.error(f"Profile update error: {str(e)}")
            db.session.rollback()
            flash("خطا در به‌روزرسانی پروفایل", "error")
    
    # دریافت تعداد اعلانات خوانده نشده
    unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    
    # دریافت آمار کاربر
    user_stats = get_user_stats(current_user.id)
    
    return render_template_string(PROFILE_TEMPLATE, 
                                user=current_user, 
                                cities=CITIES, 
                                unread_count=unread_count,
                                user_stats=user_stats)

@app.route('/profile/<int:user_id>')
@login_required
@online_required
def view_profile(user_id):
    """مشاهده پروفایل کاربر دیگر"""
    try:
        user = User.query.get_or_404(user_id)
        
        # بررسی بلاک بودن
        if user.has_blocked(current_user.id) or user.is_blocked_by(current_user.id):
            flash("شما نمی‌توانید این پروفایل را مشاهده کنید", "error")
            return redirect(url_for('home'))
        
        # دریافت تعداد لایک‌ها
        like_count = Like.query.filter_by(liked_user_id=user_id).count()
        
        # بررسی لایک شده بودن
        is_liked = Like.query.filter_by(
            user_id=current_user.id,
            liked_user_id=user_id
        ).first() is not None
        
        # بررسی دوست بودن
        is_friend = current_user.is_friend_with(user_id)
        
        # دریافت تعداد اعلانات خوانده نشده
        unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        
        # دریافت آمار کاربر
        user_stats = get_user_stats(current_user.id)
        
        return render_template_string(VIEW_PROFILE_TEMPLATE,
                                    user=user,
                                    like_count=like_count,
                                    is_liked=is_liked,
                                    is_friend=is_friend,
                                    unread_count=unread_count,
                                    user_stats=user_stats)
    except Exception as e:
        app.logger.error(f"View profile error: {str(e)}")
        flash("خطا در بارگذاری پروفایل", "error")
        return redirect(url_for('home'))

@app.route('/like/<int:user_id>', methods=['POST'])
@login_required
def like_user(user_id):
    """لایک کردن کاربر"""
    try:
        target_user = User.query.get_or_404(user_id)
        
        # بررسی بلاک بودن
        if target_user.has_blocked(current_user.id) or target_user.is_blocked_by(current_user.id):
            return jsonify({'error': 'دسترسی مجاز نیست'}), 403
        
        # بررسی اینکه قبلاً لایک شده یا نه
        existing_like = Like.query.filter_by(
            user_id=current_user.id,
            liked_user_id=user_id
        ).first()
        
        if existing_like:
            # حذف لایک
            db.session.delete(existing_like)
            db.session.commit()
            return jsonify({'liked': False})
        else:
            # اضافه کردن لایک
            like = Like(user_id=current_user.id, liked_user_id=user_id)
            db.session.add(like)
            
            # ایجاد اعلان برای کاربر لایک‌شده
            send_notification(
                user_id=user_id,
                sender_id=current_user.id,
                message=f"کاربر {current_user.username} شما را لایک کرد",
                notification_type="like"
            )
            
            db.session.commit()
            return jsonify({'liked': True})
    except Exception as e:
        app.logger.error(f"Like user error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'خطا در انجام عملیات'}), 500

@app.route('/notifications')
@login_required
@online_required
def notifications():
    """صفحه اعلانات"""
    try:
        # دریافت اعلانات کاربر
        notifications = Notification.query.filter_by(user_id=current_user.id)\
                                         .order_by(desc(Notification.created_at))\
                                         .limit(50).all()
        
        # پاک کردن اعلان‌های جدید
        for notif in notifications:
            if not notif.is_read:
                notif.is_read = True
        db.session.commit()
        
        # دریافت تعداد اعلانات خوانده نشده
        unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        
        # دریافت آمار کاربر
        user_stats = get_user_stats(current_user.id)
        
        return render_template_string(NOTIFICATIONS_TEMPLATE, 
                                    notifications=notifications, 
                                    unread_count=unread_count,
                                    user_stats=user_stats)
    except Exception as e:
        app.logger.error(f"Notifications error: {str(e)}")
        flash("خطا در بارگذاری اعلانات", "error")
        return redirect(url_for('home'))

@app.route('/search', methods=['GET', 'POST'])
@login_required
@online_required
def search():
    """صفحه جستجو"""
    results = []
    if request.method == 'POST':
        try:
            q = request.form.get('query', '').strip()
            if q:
                if q.startswith('@'):
                    results = User.query.filter(User.username.like(f"%{q[1:]}%"))\
                                        .filter(User.show_in_home == True)\
                                        .limit(50).all()
                else:
                    results = User.query.filter(User.name.like(f"%{q}%"))\
                                       .filter(User.show_in_home == True)\
                                       .limit(50).all()
            
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
            app.logger.error(f"Search error: {str(e)}")
            flash("خطا در جستجو", "error")
    
    # دریافت تعداد اعلانات خوانده نشده
    unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    
    # دریافت آمار کاربر
    user_stats = get_user_stats(current_user.id)
    
    return render_template_string(SEARCH_TEMPLATE, 
                                 results=results, 
                                 unread_count=unread_count,
                                 user_stats=user_stats)

@app.route('/chat')
@login_required
@online_required
def chat_list():
    """صفحه لیست چت‌ها"""
    try:
        # دریافت چت‌های کاربر
        chats = Chat.query.filter(
            (Chat.user_id == current_user.id) | (Chat.partner_id == current_user.id)
        ).order_by(desc(Chat.updated_at)).limit(50).all()
        
        # اضافه کردن اطلاعات طرف مقابل
        chat_data = []
        for chat in chats:
            partner_id = chat.partner_id if chat.user_id == current_user.id else chat.user_id
            partner = User.query.get(partner_id)
            if partner:
                # آخرین پیام
                last_message = Message.query.filter_by(chat_id=chat.id)\
                                           .order_by(desc(Message.timestamp))\
                                           .first()
                # تعداد پیام‌های خوانده نشده
                unread_count = Message.query.filter_by(
                    chat_id=chat.id,
                    receiver_id=current_user.id,
                    is_read=False
                ).count()
                
                chat_data.append({
                    'chat': chat,
                    'partner': partner,
                    'last_message': last_message,
                    'unread_count': unread_count
                })
        
        # دریافت تعداد اعلانات خوانده نشده
        unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        
        # دریافت آمار کاربر
        user_stats = get_user_stats(current_user.id)
        
        return render_template_string(CHAT_LIST_TEMPLATE, 
                                     chat_data=chat_data, 
                                     unread_count=unread_count,
                                     user_stats=user_stats)
    except Exception as e:
        app.logger.error(f"Chat list error: {str(e)}")
        flash("خطا در بارگذاری چت‌ها", "error")
        return redirect(url_for('home'))

@app.route('/chat/<int:partner_id>', methods=['GET', 'POST'])
@login_required
@online_required
def chat_room(partner_id):
    """صفحه چت با کاربر"""
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
            content = request.form.get('message', '').strip()
            if content:
                msg = Message(
                    chat_id=chat.id,
                    sender_id=current_user.id,
                    receiver_id=partner_id,
                    content=content
                )
                db.session.add(msg)
                db.session.commit()
                
                # ایجاد اعلان برای طرف مقابل
                send_notification(
                    user_id=partner_id,
                    sender_id=current_user.id,
                    message=f"پیام جدید از {current_user.username}",
                    notification_type="message"
                )
                
                return jsonify({'success': True})
        
        # دریافت پیام‌ها
        messages = Message.query.filter_by(chat_id=chat.id)\
                               .order_by(asc(Message.timestamp))\
                               .limit(100).all()
        
        # علامت‌گذاری پیام‌ها به عنوان خوانده شده
        for message in messages:
            if message.receiver_id == current_user.id and not message.is_read:
                message.is_read = True
        db.session.commit()
        
        # دریافت تعداد اعلانات خوانده نشده
        unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        
        # دریافت آمار کاربر
        user_stats = get_user_stats(current_user.id)
        
        return render_template_string(CHAT_ROOM_TEMPLATE, 
                                     partner=partner, 
                                     messages=messages, 
                                     chat=chat, 
                                     unread_count=unread_count,
                                     user_stats=user_stats)
    except Exception as e:
        app.logger.error(f"Chat room error: {str(e)}")
        flash("خطا در بارگذاری چت", "error")
        return redirect(url_for('chat_list'))

@app.route('/delete_chat/<int:partner_id>', methods=['POST'])
@login_required
def delete_chat(partner_id):
    """حذف چت"""
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
            return jsonify({'success': True})
        else:
            return jsonify({'success': False})
    except Exception as e:
        app.logger.error(f"Delete chat error: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False})

@app.route('/block_user/<int:user_id>', methods=['POST'])
@login_required
def block_user(user_id):
    """بلاک کردن کاربر"""
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
            send_notification(
                user_id=user_id,
                sender_id=current_user.id,
                message=f"کاربر {current_user.username} شما را بلاک کرده است",
                notification_type="block"
            )
            
            db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        app.logger.error(f"Block user error: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False})

@app.route('/unblock_user/<int:user_id>', methods=['POST'])
@login_required
def unblock_user(user_id):
    """رفع بلاک کردن کاربر"""
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
            send_notification(
                user_id=user_id,
                sender_id=current_user.id,
                message=f"کاربر {current_user.username} شما را از بلاک خارج کرده است",
                notification_type="unblock"
            )
            
            db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        app.logger.error(f"Unblock user error: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False})

@app.route('/notification_count')
@login_required
def notification_count():
    """دریافت تعداد اعلانات خوانده نشده"""
    try:
        count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        return jsonify({'count': count})
    except Exception as e:
        app.logger.error(f"Notification count error: {str(e)}")
        return jsonify({'count': 0})

@app.route('/logout')
@login_required
def logout():
    """خروج از حساب"""
    try:
        # به‌روزرسانی وضعیت آفلاین بودن
        current_user.is_online = False
        db.session.commit()
        
        # لاگ فعالیت
        log_activity(current_user.id, 'logout', None, request)
        
        logout_user()
        flash("با موفقیت از حساب خارج شدید", "success")
    except Exception as e:
        app.logger.error(f"Logout error: {str(e)}")
    
    return redirect(url_for('login'))

# ====================================================================================================
# STATIC FILE SERVING
# ====================================================================================================

@app.route('/static/<path:filename>')
def static_files(filename):
    """سرویس فایل‌های استاتیک"""
    return send_from_directory('static', filename)

# ====================================================================================================
# CONSTANTS AND DATA
# ====================================================================================================

# لیست شهرها
CITIES = [
    "شهرک صدرا", "شهرک گلستان", "معالی آباد", "شهرک کشن", "شهرک مهدیه",
    "شهرک زینبیه", "شهرک بعثت", "شهرک والفجر", "شهرک صنعتی عفیف آباد",
    "کوی امام رضا", "شهرک گویم", "شهرک بزین", "شهرک رحمت آباد", "شهرک خورشید",
    "شهرک سلامت", "شهرک فرهنگیان", "کوی زاگرس", "کوی پاسداران", "شهرک عرفان",
    "شهرک هنرستان"
]

# ====================================================================================================
# CSS STYLES
# ====================================================================================================

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

# ====================================================================================================
# JAVASCRIPT SCRIPTS
# ====================================================================================================

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
function previewImage(input, previewId) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            const preview = document.getElementById(previewId);
            preview.src = e.target.result;
            preview.style.display = 'block';
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

// بستن منوها با کلیک روی صفحه
document.addEventListener('click', function(event) {
    const dropdowns = document.querySelectorAll('[id^="dropdown-"]');
    const fileOptions = document.getElementById('file-options');
    
    dropdowns.forEach(dropdown => {
        if (!dropdown.contains(event.target) && !event.target.closest('.dropdown-btn')) {
            dropdown.style.display = 'none';
        }
    });
    
    if (fileOptions && !fileOptions.contains(event.target) && !event.target.closest('.file-btn')) {
        fileOptions.style.display = 'none';
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

# ====================================================================================================
# HTML TEMPLATES
# ====================================================================================================

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
                    </label>
                    <input type="file" id="profile_pic" name="profile_pic" accept="image/*" 
                           onchange="previewImage(this, 'profile-preview')" style="display: none;">
                    <img id="profile-preview" src="" 
                         alt="پیش‌نمایش پروفایل" 
                         style="width: 100px; height: 100px; border-radius: 50%; object-fit: cover; display: none; margin: 0 auto 20px;">
                </div>
                
                <input type="text" name="name" placeholder="نام (اختیاری)">
                <input type="text" name="username" placeholder="@نام کاربری (اجباری)" required>
                
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
            <!-- فیلترها -->
            <form method="post" action="{{ url_for('home_filters') }}" style="margin-bottom: 20px;">
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
                        <button onclick="location.href='{{ url_for('chat_room', partner_id=user.id) }}'" 
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
            </label>
            <input type="file" id="profile_pic" name="profile_pic" accept="image/*" 
                   onchange="previewImage(this, 'profile-preview')" style="display: none;">
            <img id="profile-preview" src="" 
                 alt="پیش‌نمایش پروفایل" 
                 style="width: 120px; height: 120px; border-radius: 50%; object-fit: cover; display: none; margin: 0 auto 20px;">
        </div>
        
        <div style="max-width: 500px; margin: 0 auto; background: var(--card-bg); padding: 20px; border-radius: 15px; border: 1px solid var(--neon-purple);">
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
                        <span>{{ user.username }}</span>
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
            
            <div style="margin-top: 30px; text-align: center;">
                <button onclick="location.href='{{ url_for('logout') }}'" 
                        class="neon-btn" 
                        style="background: linear-gradient(90deg, #ff6b6b, #ff8e8e); width: 100%; margin-bottom: 10px;">
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

VIEW_PROFILE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>پروفایل {{ user.name or user.username }} - GOYIMIX | گویمیکس</title>
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
            <img src="/static/uploads/{{ user.profile_pic }}" 
                 alt="پروفایل" 
                 class="profile-avatar">
        </div>
        
        <div style="max-width: 500px; margin: 0 auto; background: var(--card-bg); padding: 20px; border-radius: 15px; border: 1px solid var(--neon-purple);">
            <div style="margin-bottom: 15px;">
                <label style="display: flex; justify-content: space-between; align-items: center;">
                    <span>نام:</span>
                    <span>{{ user.name or user.username }}</span>
                </label>
            </div>
            
            <div style="margin-bottom: 15px;">
                <label style="display: flex; justify-content: space-between; align-items: center;">
                    <span>نام کاربری:</span>
                    <span>{{ user.username }}</span>
                </label>
            </div>
            
            <div style="margin-bottom: 15px;">
                <label style="display: flex; justify-content: space-between; align-items: center;">
                    <span>سن:</span>
                    <span>{{ user.age }} سال</span>
                </label>
            </div>
            
            <div style="margin-bottom: 15px;">
                <label style="display: flex; justify-content: space-between; align-items: center;">
                    <span>جنسیت:</span>
                    <span>{{ user.gender }}</span>
                </label>
            </div>
            
            {% if user.bio %}
            <div style="margin-bottom: 15px;">
                <label style="display: flex; justify-content: space-between; align-items: center;">
                    <span>بیو:</span>
                    <span>{{ user.bio }}</span>
                </label>
            </div>
            {% endif %}
            
            {% if user.interests %}
            <div style="margin-bottom: 15px;">
                <label style="display: flex; justify-content: space-between; align-items: center;">
                    <span>علاقه‌مندی‌ها:</span>
                    <span>{{ user.interests }}</span>
                </label>
            </div>
            {% endif %}
            
            <div style="margin-bottom: 15px;">
                <label style="display: flex; justify-content: space-between; align-items: center;">
                    <span>شهر:</span>
                    <span>{{ user.city }}</span>
                </label>
            </div>
            
            <div style="margin-bottom: 15px;">
                <label style="display: flex; justify-content: space-between; align-items: center;">
                    <span>تعداد لایک‌ها:</span>
                    <span>{{ like_count }}</span>
                </label>
            </div>
            
            <div style="margin-top: 20px; display: flex; gap: 10px;">
                <button onclick="likeUser({{ user.id }}, this)" 
                        style="background: #ff6b6b; color: white; flex: 1;"
                        data-likes="{{ like_count }}">
                    {% if is_liked %}
                        ❤️ {{ like_count }}
                    {% else %}
                        🤍 {{ like_count }}
                    {% endif %}
                </button>
                <button onclick="location.href='{{ url_for('chat_room', partner_id=user.id) }}'" 
                        style="background: #9B5DE5; color: white; flex: 1;">
                    💬 چت
                </button>
            </div>
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
                        <button style="background: #666; color: white; padding: 5px 10px; border: none; border-radius: 5px; font-size: 12px;">
                            ❌ رد
                        </button>
                        <button style="background: var(--neon-pink); color: white; padding: 5px 10px; border: none; border-radius: 5px; font-size: 12px;">
                            🚫 بلاک
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
                        {% if data.unread_count > 0 %}
                        <span style="background: var(--neon-pink); color: white; border-radius: 50%; padding: 2px 8px; font-size: 12px;">
                            {{ data.unread_count }}
                        </span>
                        {% endif %}
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
                <div>
                    <h3 style="margin: 0;">{{ partner.name or partner.username }}</h3>
                    <p style="margin: 0; font-size: 14px; color: #aaa;">{{ partner.username }}</p>
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

# ====================================================================================================
# MAIN APPLICATION STARTUP
# ====================================================================================================

if __name__ == '__main__':
    # ایجاد دیتابیس
    with app.app_context():
        try:
            db.create_all()
            app.logger.info("Database tables created successfully")
        except Exception as e:
            app.logger.error(f"Error creating database tables: {str(e)}")
    
    # اجرای اپلیکیشن
    app.logger.info("Starting GOYIMIX application...")
    socketio.run(app, debug=False, port=5000, host='0.0.0.0', allow_unsafe_werkzeug=True)