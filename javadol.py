from flask import Flask, render_template_string, request, session, redirect, url_for, flash
import os
from datetime import datetime
import jdatetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# داده‌های کاربران و اعلانات
users = {
    'admin': {
        'name': 'مدیر',
        'lastname': 'سیستم',
        'role': 'مدیر',
        'password': 'dabirstan012345'
    }
}

# داده‌های اعلانات
announcements = []

# داده‌های دانش آموزان
students = {
    'math_10': [],
    'science_10': [],
    'humanities_10': [],
    'math_11': [],
    'science_11': [],
    'humanities_11': [],
    'math_12': [],
    'science_12': [],
    'humanities_12': []
}

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>سایت رسمی دبیرستان پسرانه جوادالائمه</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;700&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Vazirmatn', sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            color: white;
            overflow-x: hidden;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            flex: 1;
            overflow-y: auto;
            padding-bottom: 80px;
        }
        
        .header {
            text-align: center;
            padding: 30px 0;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 15px;
            text-shadow: 0 0 20px #00eeff;
            background: linear-gradient(45deg, #ff00cc, #00eeff, #ff00cc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: fadeInDown 0.8s ease-out;
        }
        
        .welcome-text {
            font-size: 1.2rem;
            margin-bottom: 30px;
            color: #e0e0ff;
            line-height: 1.6;
            animation: fadeInUp 1s ease-out;
        }
        
        .creator-info {
            text-align: center;
            margin: 20px 0;
            padding: 15px;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            border: 1px solid rgba(255,255,255,0.2);
            animation: pulse 2s infinite;
        }
        
        .buttons-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 25px;
            margin: 40px 0;
            animation: fadeIn 1s ease-out;
        }
        
        .grid-buttons {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin: 30px 0;
        }
        
        .btn {
            padding: 20px;
            border: none;
            border-radius: 15px;
            font-size: 1.1rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
            position: relative;
            overflow: hidden;
            color: white;
            text-align: center;
            transform: translateY(0);
        }
        
        .btn:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 15px 35px rgba(0,0,0,0.4);
        }
        
        .btn:active {
            transform: translateY(-2px) scale(0.98);
        }
        
        .btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: 0.5s;
        }
        
        .btn:hover::before {
            left: 100%;
        }
        
        .btn-admin { background: linear-gradient(45deg, #ff00cc, #ff0066); }
        .btn-teacher { background: linear-gradient(45deg, #00eeff, #0066ff); }
        .btn-parent { background: linear-gradient(45deg, #ffcc00, #ff6600); }
        .btn-student { background: linear-gradient(45deg, #00ff99, #00cc66); }
        .btn-grade { background: linear-gradient(45deg, #9932cc, #4b0082); }
        .btn-field { background: linear-gradient(45deg, #ff4500, #ff8c00); }
        .btn-announcement { background: linear-gradient(45deg, #00bfff, #1e90ff); }
        .btn-students { background: linear-gradient(45deg, #32cd32, #228b22); }
        
        .form-container {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin: 20px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            animation: slideInUp 0.6s ease-out;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
        }
        
        input, select {
            width: 100%;
            padding: 15px;
            border: 2px solid rgba(255,255,255,0.2);
            border-radius: 10px;
            background: rgba(0,0,0,0.3);
            color: white;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: #00eeff;
            box-shadow: 0 0 15px rgba(0, 238, 255, 0.5);
            transform: scale(1.02);
        }
        
        .submit-btn {
            background: linear-gradient(45deg, #00eeff, #0066ff);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 1.1rem;
            cursor: pointer;
            width: 100%;
            font-weight: 500;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        
        .submit-btn:hover {
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0 10px 25px rgba(0, 238, 255, 0.4);
        }
        
        .submit-btn:active {
            transform: translateY(1px) scale(0.98);
        }
        
        .error {
            background: rgba(255, 0, 0, 0.2);
            border: 1px solid #ff4444;
            padding: 15px;
            border-radius: 10px;
            margin: 15px 0;
            text-align: center;
            animation: shake 0.5s ease-in-out;
        }
        
        .success {
            background: rgba(0, 255, 0, 0.2);
            border: 1px solid #00ff00;
            padding: 15px;
            border-radius: 10px;
            margin: 15px 0;
            text-align: center;
            animation: bounceIn 0.6s ease-out;
        }
        
        .profile-container {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin: 20px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            animation: fadeIn 0.8s ease-out;
        }
        
        .profile-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            margin: 10px 0;
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.1);
            transition: all 0.3s ease;
        }
        
        .profile-item:hover {
            background: rgba(255,255,255,0.1);
            transform: translateX(5px);
        }
        
        .edit-btn {
            background: linear-gradient(45deg, #ffcc00, #ff6600);
            border: none;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            cursor: pointer;
            color: white;
            font-weight: bold;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            box-shadow: 0 3px 10px rgba(0,0,0,0.2);
        }
        
        .edit-btn:hover {
            transform: scale(1.1) rotate(15deg);
            box-shadow: 0 5px 15px rgba(255, 102, 0, 0.4);
        }
        
        .logout-btn {
            background: linear-gradient(45deg, #ff0066, #ff00cc);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 1.1rem;
            cursor: pointer;
            width: 100%;
            font-weight: 500;
            margin-top: 20px;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        
        .logout-btn:hover {
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0 10px 25px rgba(255, 0, 102, 0.4);
        }
        
        .logout-btn:active {
            transform: translateY(1px) scale(0.98);
        }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            z-index: 1000;
            align-items: center;
            justify-content: center;
            animation: fadeIn 0.3s ease-out;
        }
        
        .modal-content {
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            padding: 30px;
            border-radius: 20px;
            text-align: center;
            max-width: 400px;
            width: 90%;
            box-shadow: 0 20px 50px rgba(0,0,0,0.5);
            animation: zoomIn 0.4s ease-out;
        }
        
        .modal-buttons {
            display: flex;
            gap: 15px;
            margin-top: 20px;
            justify-content: center;
        }
        
        .modal-btn {
            padding: 12px 25px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .modal-btn-yes {
            background: linear-gradient(45deg, #00ff99, #00cc66);
            color: white;
        }
        
        .modal-btn-no {
            background: linear-gradient(45deg, #ff0066, #ff00cc);
            color: white;
        }
        
        .modal-btn:hover {
            transform: translateY(-2px) scale(1.05);
        }
        
        .toolbar {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(0,0,0,0.9);
            backdrop-filter: blur(10px);
            display: flex;
            justify-content: space-around;
            padding: 15px;
            border-top: 2px solid rgba(255,255,255,0.1);
            z-index: 999;
        }
        
        .toolbar-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            text-decoration: none;
            color: #ccc;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            padding: 10px 20px;
            border-radius: 15px;
        }
        
        .toolbar-item.active {
            background: rgba(0, 238, 255, 0.2);
            color: #00eeff;
            box-shadow: 0 0 20px rgba(0, 238, 255, 0.3);
            transform: translateY(-5px);
        }
        
        .toolbar-item:hover {
            color: white;
            transform: translateY(-8px);
        }
        
        .toolbar-icon {
            font-size: 1.5rem;
            margin-bottom: 5px;
        }
        
        .back-btn {
            background: linear-gradient(45deg, #666666, #999999);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 10px;
            cursor: pointer;
            margin-bottom: 20px;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        
        .back-btn:hover {
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0 5px 15px rgba(102, 102, 102, 0.4);
        }
        
        .back-btn:active {
            transform: translateY(1px) scale(0.98);
        }
        
        .student-count {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 1.2rem;
            margin-bottom: 20px;
            padding: 15px;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .student-count-icon {
            font-size: 1.5rem;
        }
        
        .add-student-btn {
            position: fixed;
            bottom: 80px;
            right: 30px;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(45deg, #00eeff, #0066ff);
            border: none;
            color: white;
            font-size: 2rem;
            cursor: pointer;
            box-shadow: 0 10px 25px rgba(0, 238, 255, 0.4);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            z-index: 998;
        }
        
        .add-student-btn:hover {
            transform: translateY(-5px) scale(1.1);
            box-shadow: 0 15px 35px rgba(0, 238, 255, 0.6);
        }
        
        .add-student-btn:active {
            transform: translateY(2px) scale(0.95);
        }
        
        .students-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .student-card {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.2);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            cursor: pointer;
        }
        
        .student-card:hover {
            transform: translateY(-5px) scale(1.02);
            box-shadow: 0 10px 25px rgba(0,0,0,0.3);
            background: rgba(255,255,255,0.15);
        }
        
        .student-card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .student-name {
            font-weight: bold;
            font-size: 1.1rem;
        }
        
        .student-card-actions {
            display: flex;
            gap: 10px;
        }
        
        .card-btn {
            width: 35px;
            height: 35px;
            border-radius: 50%;
            border: none;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .edit-card-btn {
            background: linear-gradient(45deg, #ffcc00, #ff6600);
            color: white;
        }
        
        .delete-card-btn {
            background: linear-gradient(45deg, #ff0066, #ff00cc);
            color: white;
        }
        
        .card-btn:hover {
            transform: scale(1.1);
        }
        
        .student-info {
            font-size: 0.9rem;
            line-height: 1.6;
        }
        
        .student-info-item {
            margin: 5px 0;
            padding: 5px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        
        .announcements-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .announcement-card {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.2);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        
        .announcement-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        }
        
        .announcement-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .announcement-title {
            font-weight: bold;
            font-size: 1.1rem;
        }
        
        .delete-announcement-btn {
            background: linear-gradient(45deg, #ff0066, #ff00cc);
            color: white;
            border: none;
            border-radius: 50%;
            width: 35px;
            height: 35px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .delete-announcement-btn:hover {
            transform: scale(1.1);
        }
        
        .announcement-content {
            margin: 15px 0;
            line-height: 1.6;
        }
        
        .announcement-meta {
            font-size: 0.8rem;
            color: #ccc;
            text-align: left;
        }
        
        /* انیمیشن‌ها */
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes slideInUp {
            from {
                opacity: 0;
                transform: translateY(50px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes bounceIn {
            0% {
                opacity: 0;
                transform: scale(0.3);
            }
            50% {
                transform: scale(1.05);
            }
            70% {
                transform: scale(0.9);
            }
            100% {
                opacity: 1;
                transform: scale(1);
            }
        }
        
        @keyframes zoomIn {
            from {
                opacity: 0;
                transform: scale(0.5);
            }
            to {
                opacity: 1;
                transform: scale(1);
            }
        }
        
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-5px); }
            75% { transform: translateX(5px); }
        }
        
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(0, 238, 255, 0.4); }
            70% { box-shadow: 0 0 0 10px rgba(0, 238, 255, 0); }
            100% { box-shadow: 0 0 0 0 rgba(0, 238, 255, 0); }
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 1.8rem;
            }
            
            .buttons-container, .grid-buttons {
                grid-template-columns: 1fr;
            }
            
            .btn {
                padding: 15px;
                font-size: 1rem;
            }
            
            .add-student-btn {
                bottom: 100px;
                right: 20px;
                width: 50px;
                height: 50px;
                font-size: 1.5rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        {% if not session.get('logged_in') %}
            {% if request.endpoint == 'login_admin' %}
                <button class="back-btn" onclick="window.location.href='/'">← بازگشت</button>
                <div class="header">
                    <h1>ورود مدیران</h1>
                </div>
                <div class="form-container">
                    <form method="POST">
                        <div class="form-group">
                            <label for="name">نام:</label>
                            <input type="text" id="name" name="name" value="{{ request.form.name or '' }}" required>
                        </div>
                        <div class="form-group">
                            <label for="lastname">نام خانوادگی:</label>
                            <input type="text" id="lastname" name="lastname" value="{{ request.form.lastname or '' }}" required>
                        </div>
                        <div class="form-group">
                            <label for="role">مرتبه:</label>
                            <select id="role" name="role" required>
                                <option value="">انتخاب کنید</option>
                                <option value="مدیر" {{ 'selected' if request.form.role == 'مدیر' }}>مدیر</option>
                                <option value="ناظم" {{ 'selected' if request.form.role == 'ناظم' }}>ناظم</option>
                                <option value="معاون" {{ 'selected' if request.form.role == 'معاون' }}>معاون</option>
                                <option value="سرپرست" {{ 'selected' if request.form.role == 'سرپرست' }}>سرپرست</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="password">رمز ورود:</label>
                            <input type="password" id="password" name="password" required>
                        </div>
                        {% if error %}
                            <div class="error">{{ error }}</div>
                        {% endif %}
                        <button type="submit" class="submit-btn">ورود</button>
                    </form>
                </div>
            {% else %}
                <div class="header">
                    <h1>سایت رسمی دبیرستان پسرانه جوادالائمه</h1>
                </div>
                <div class="welcome-text">
                    <p>به سایت رسمی دبیرستان جوادالائمه خوش آمدید</p>
                    <p>لطفاً برای ورود، با توجه به وضعیت خود، یکی از دکمه‌های زیر را انتخاب کنید:</p>
                </div>
                <div class="buttons-container">
                    <button class="btn btn-admin" onclick="window.location.href='/login/admin'">ورود مدیران</button>
                    <button class="btn btn-teacher" onclick="alert('این بخش در حال توسعه است')">ورود معلمان</button>
                    <button class="btn btn-parent" onclick="alert('این بخش در حال توسعه است')">ورود والدین</button>
                    <button class="btn btn-student" onclick="alert('این بخش در حال توسعه است')">ورود دانش‌آموزان</button>
                </div>
                <div class="creator-info">
                    <p><strong>سازنده:</strong> محمدرضا محمدی</p>
                    <p>دانش آموز دبیرستان جوادالائمه (رشته ریاضی)</p>
                </div>
            {% endif %}
        {% else %}
            {% if page == 'profile' %}
                <button class="back-btn" onclick="window.location.href='/admin'">← بازگشت</button>
                <div class="header">
                    <h1>پروفایل کاربری</h1>
                </div>
                <div class="profile-container">
                    <div class="profile-item">
                        <span><strong>نام:</strong> {{ session.name }}</span>
                        <button class="edit-btn" onclick="editField('name', '{{ session.name }}')">✎</button>
                    </div>
                    <div class="profile-item">
                        <span><strong>نام خانوادگی:</strong> {{ session.lastname }}</span>
                        <button class="edit-btn" onclick="editField('lastname', '{{ session.lastname }}')">✎</button>
                    </div>
                    <div class="profile-item">
                        <span><strong>مرتبه:</strong> {{ session.role }}</span>
                        <button class="edit-btn" onclick="editField('role', '{{ session.role }}')">✎</button>
                    </div>
                    <div class="profile-item">
                        <span><strong>رمز ورود:</strong> ••••••••••</span>
                        <button class="edit-btn" disabled style="opacity: 0.5;">✎</button>
                    </div>
                    <button class="logout-btn" onclick="showLogoutModal()">خروج از حساب</button>
                </div>
            {% elif page == 'announcements' %}
                <button class="back-btn" onclick="window.location.href='/admin'">← بازگشت</button>
                <div class="header">
                    <h1>اعلانات</h1>
                </div>
                {% if announcements %}
                    <div class="announcements-grid">
                        {% for i, announcement in enumerate(announcements) %}
                        <div class="announcement-card">
                            <div class="announcement-header">
                                <div class="announcement-title">{{ announcement.title }}</div>
                                <button class="delete-announcement-btn" onclick="deleteAnnouncement({{ i }})">🗑️</button>
                            </div>
                            <div class="announcement-content">{{ announcement.content }}</div>
                            <div class="announcement-meta">
                                <div>تاریخ: {{ announcement.date }}</div>
                                <div>زمان: {{ announcement.time }}</div>
                                <div>بخش: {{ announcement.section }}</div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                {% else %}
                    <div class="welcome-text">
                        <p>هنوز هیچ اعلانی نیامده است</p>
                    </div>
                {% endif %}
            {% elif page == 'students' %}
                <button class="back-btn" onclick="window.location.href='/admin'">← بازگشت</button>
                <div class="header">
                    <h1>دانش آموزان</h1>
                </div>
                <div class="grid-buttons">
                    <button class="btn btn-grade" onclick="window.location.href='/admin/students/10'">پایه دهم</button>
                    <button class="btn btn-grade" onclick="window.location.href='/admin/students/11'">پایه یازدهم</button>
                    <button class="btn btn-grade" onclick="window.location.href='/admin/students/12'">پایه دوازدهم</button>
                </div>
            {% elif page == 'grade_students' %}
                <button class="back-btn" onclick="window.location.href='/admin/students'">← بازگشت</button>
                <div class="header">
                    <h1>پایه {{ grade }}</h1>
                </div>
                <div class="grid-buttons">
                    <button class="btn btn-field" onclick="window.location.href='/admin/students/{{ grade }}/math'">رشته ریاضی</button>
                    <button class="btn btn-field" onclick="window.location.href='/admin/students/{{ grade }}/science'">رشته تجربی</button>
                    <button class="btn btn-field" onclick="window.location.href='/admin/students/{{ grade }}/humanities'">رشته انسانی</button>
                </div>
            {% elif page == 'field_students' %}
                <button class="back-btn" onclick="window.location.href='/admin/students/{{ grade }}'">← بازگشت</button>
                <div class="header">
                    <h1>{{ field_name }} پایه {{ grade }}</h1>
                </div>
                <div class="student-count">
                    <span class="student-count-icon">👤</span>
                    <span>تعداد دانش آموزان: <span id="studentCount">{{ students[field_key]|length }}</span></span>
                </div>
                {% if students[field_key] %}
                    <div class="students-grid">
                        {% for i, student in enumerate(students[field_key]) %}
                        <div class="student-card" onclick="showStudentDetails({{ i }}, '{{ field_key }}')">
                            <div class="student-card-header">
                                <div class="student-name">{{ student.name }} {{ student.lastname }}</div>
                                <div class="student-card-actions">
                                    <button class="card-btn edit-card-btn" onclick="event.stopPropagation(); editStudent({{ i }}, '{{ field_key }}')">✎</button>
                                    <button class="card-btn delete-card-btn" onclick="event.stopPropagation(); deleteStudent({{ i }}, '{{ field_key }}')">🗑️</button>
                                </div>
                            </div>
                            <div class="student-info">
                                <div class="student-info-item">کد ملی: {{ student.national_id }}</div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                {% else %}
                    <div class="welcome-text">
                        <p>هنوز هیچ دانش آموزی ثبت نشده است</p>
                    </div>
                {% endif %}
                <button class="add-student-btn" onclick="showAddStudentModal()">+</button>
            {% elif page == 'student_details' %}
                <button class="back-btn" onclick="window.location.href='/admin/students/{{ grade }}/{{ field }}'">← بازگشت</button>
                <div class="header">
                    <h1>اطلاعات دانش آموز</h1>
                </div>
                <div class="profile-container">
                    {% set student = students[field_key][student_index] %}
                    <div class="profile-item">
                        <span><strong>نام:</strong> {{ student.name }}</span>
                    </div>
                    <div class="profile-item">
                        <span><strong>نام خانوادگی:</strong> {{ student.lastname }}</span>
                    </div>
                    <div class="profile-item">
                        <span><strong>کد ملی:</strong> {{ student.national_id }}</span>
                    </div>
                    <div class="profile-item">
                        <span><strong>شماره دانش آموز:</strong> {{ student.student_phone or 'ثبت نشده' }}</span>
                    </div>
                    <div class="profile-item">
                        <span><strong>شماره پدر:</strong> {{ student.father_phone or 'ثبت نشده' }}</span>
                    </div>
                    <div class="profile-item">
                        <span><strong>شماره مادر:</strong> {{ student.mother_phone or 'ثبت نشده' }}</span>
                    </div>
                </div>
            {% elif page == 'add_student' %}
                <button class="back-btn" onclick="window.location.href='/admin/students/{{ grade }}/{{ field }}'">← بازگشت</button>
                <div class="header">
                    <h1>افزودن دانش آموز</h1>
                </div>
                <div class="form-container">
                    <form method="POST" action="/admin/students/{{ grade }}/{{ field }}/add">
                        <div class="form-group">
                            <label for="name">نام دانش آموز (اجباری):</label>
                            <input type="text" id="name" name="name" value="{{ request.form.name or '' }}" required>
                        </div>
                        <div class="form-group">
                            <label for="lastname">نام خانوادگی دانش آموز (اجباری):</label>
                            <input type="text" id="lastname" name="lastname" value="{{ request.form.lastname or '' }}" required>
                        </div>
                        <div class="form-group">
                            <label for="national_id">کد ملی دانش آموز (اجباری):</label>
                            <input type="text" id="national_id" name="national_id" value="{{ request.form.national_id or '' }}" required>
                        </div>
                        <div class="form-group">
                            <label for="student_phone">شماره دانش آموز (اختیاری):</label>
                            <input type="text" id="student_phone" name="student_phone" value="{{ request.form.student_phone or '' }}">
                        </div>
                        <div class="form-group">
                            <label for="father_phone">شماره پدر (اختیاری):</label>
                            <input type="text" id="father_phone" name="father_phone" value="{{ request.form.father_phone or '' }}">
                        </div>
                        <div class="form-group">
                            <label for="mother_phone">شماره مادر (اختیاری):</label>
                            <input type="text" id="mother_phone" name="mother_phone" value="{{ request.form.mother_phone or '' }}">
                        </div>
                        {% if error %}
                            <div class="error">{{ error }}</div>
                        {% endif %}
                        <button type="submit" class="submit-btn">تایید</button>
                    </form>
                </div>
            {% elif page == 'edit_student' %}
                <button class="back-btn" onclick="window.location.href='/admin/students/{{ grade }}/{{ field }}'">← بازگشت</button>
                <div class="header">
                    <h1>ویرایش دانش آموز</h1>
                </div>
                <div class="form-container">
                    {% set student = students[field_key][student_index] %}
                    <form method="POST" action="/admin/students/{{ grade }}/{{ field }}/edit/{{ student_index }}">
                        <div class="form-group">
                            <label for="name">نام دانش آموز (اجباری):</label>
                            <input type="text" id="name" name="name" value="{{ student.name }}" required>
                        </div>
                        <div class="form-group">
                            <label for="lastname">نام خانوادگی دانش آموز (اجباری):</label>
                            <input type="text" id="lastname" name="lastname" value="{{ student.lastname }}" required>
                        </div>
                        <div class="form-group">
                            <label for="national_id">کد ملی دانش آموز (اجباری):</label>
                            <input type="text" id="national_id" name="national_id" value="{{ student.national_id }}" required>
                        </div>
                        <div class="form-group">
                            <label for="student_phone">شماره دانش آموز (اختیاری):</label>
                            <input type="text" id="student_phone" name="student_phone" value="{{ student.student_phone or '' }}">
                        </div>
                        <div class="form-group">
                            <label for="father_phone">شماره پدر (اختیاری):</label>
                            <input type="text" id="father_phone" name="father_phone" value="{{ student.father_phone or '' }}">
                        </div>
                        <div class="form-group">
                            <label for="mother_phone">شماره مادر (اختیاری):</label>
                            <input type="text" id="mother_phone" name="mother_phone" value="{{ student.mother_phone or '' }}">
                        </div>
                        {% if error %}
                            <div class="error">{{ error }}</div>
                        {% endif %}
                        <button type="submit" class="submit-btn">تایید</button>
                    </form>
                </div>
            {% else %}
                <div class="header">
                    <h1>پنل مدیریت</h1>
                    <p>به پنل مدیریت خوش آمدید</p>
                </div>
                <div class="creator-info">
                    <p><strong>سازنده:</strong> محمدرضا محمدی</p>
                    <p>دانش آموز دبیرستان جوادالائمه (رشته ریاضی)</p>
                </div>
                <div class="grid-buttons">
                    <button class="btn btn-announcement" onclick="window.location.href='/admin/announcements'">اعلانات</button>
                    <button class="btn btn-students" onclick="window.location.href='/admin/students'">دانش آموزان</button>
                </div>
            {% endif %}
        {% endif %}
    </div>
    
    {% if session.get('logged_in') %}
        <div class="toolbar">
            <a href="/admin" class="toolbar-item {{ 'active' if page not in ['profile', 'announcements', 'students', 'grade_students', 'field_students', 'student_details', 'add_student', 'edit_student'] }}">
                <div class="toolbar-icon">🏠</div>
                <span>صفحه اصلی</span>
            </a>
            <a href="/admin/profile" class="toolbar-item {{ 'active' if page == 'profile' }}">
                <div class="toolbar-icon">👤</div>
                <span>پروفایل</span>
            </a>
        </div>
    {% endif %}
    
    <!-- مودال خروج -->
    <div id="logoutModal" class="modal">
        <div class="modal-content">
            <h3>آیا مطمئن هستید می‌خواهید از حساب خارج شوید؟</h3>
            <div class="modal-buttons">
                <button class="modal-btn modal-btn-yes" onclick="logout()">بله</button>
                <button class="modal-btn modal-btn-no" onclick="closeModal('logoutModal')">خیر</button>
            </div>
        </div>
    </div>
    
    <!-- مودال حذف اعلان -->
    <div id="deleteAnnouncementModal" class="modal">
        <div class="modal-content">
            <h3>آیا مطمئن هستید می‌خواهید این اعلان را پاک کنید؟</h3>
            <div class="modal-buttons">
                <button class="modal-btn modal-btn-yes" onclick="confirmDeleteAnnouncement()">بله</button>
                <button class="modal-btn modal-btn-no" onclick="closeModal('deleteAnnouncementModal')">خیر</button>
            </div>
        </div>
    </div>
    
    <!-- مودال حذف دانش آموز -->
    <div id="deleteStudentModal" class="modal">
        <div class="modal-content">
            <h3>آیا مطمئن هستید می‌خواهید اطلاعات دانش آموز را پاک کنید؟</h3>
            <div class="modal-buttons">
                <button class="modal-btn modal-btn-yes" onclick="confirmDeleteStudent()">بله</button>
                <button class="modal-btn modal-btn-no" onclick="closeModal('deleteStudentModal')">خیر</button>
            </div>
        </div>
    </div>
    
    <script>
        let pendingDeleteIndex = -1;
        let pendingDeleteField = '';
        
        function showLogoutModal() {
            document.getElementById('logoutModal').style.display = 'flex';
        }
        
        function closeModal(modalId) {
            document.getElementById(modalId).style.display = 'none';
        }
        
        function logout() {
            window.location.href = '/logout';
        }
        
        function editField(field, currentValue) {
            const newValue = prompt('مقدار جدید را وارد کنید:', currentValue);
            if (newValue !== null && newValue !== '') {
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = '/edit_profile';
                
                const fieldInput = document.createElement('input');
                fieldInput.type = 'hidden';
                fieldInput.name = 'field';
                fieldInput.value = field;
                
                const valueInput = document.createElement('input');
                valueInput.type = 'hidden';
                valueInput.name = 'value';
                valueInput.value = newValue;
                
                form.appendChild(fieldInput);
                form.appendChild(valueInput);
                document.body.appendChild(form);
                form.submit();
            }
        }
        
        function deleteAnnouncement(index) {
            pendingDeleteIndex = index;
            document.getElementById('deleteAnnouncementModal').style.display = 'flex';
        }
        
        function confirmDeleteAnnouncement() {
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = '/admin/announcements/delete/' + pendingDeleteIndex;
            document.body.appendChild(form);
            form.submit();
        }
        
        function showAddStudentModal() {
            window.location.href = window.location.pathname + '/add';
        }
        
        function editStudent(index, field) {
            window.location.href = window.location.pathname + '/edit/' + index;
        }
        
        function deleteStudent(index, field) {
            pendingDeleteIndex = index;
            pendingDeleteField = field;
            document.getElementById('deleteStudentModal').style.display = 'flex';
        }
        
        function confirmDeleteStudent() {
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = '/admin/students/' + pendingDeleteField + '/delete/' + pendingDeleteIndex;
            document.body.appendChild(form);
            form.submit();
        }
        
        function showStudentDetails(index, field) {
            window.location.href = window.location.pathname + '/details/' + index;
        }
        
        // بستن مودال‌ها با کلیک خارج از آن‌ها
        window.onclick = function(event) {
            const modals = ['logoutModal', 'deleteAnnouncementModal', 'deleteStudentModal'];
            modals.forEach(modalId => {
                const modal = document.getElementById(modalId);
                if (event.target === modal) {
                    modal.style.display = 'none';
                }
            });
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/login/admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        name = request.form['name']
        lastname = request.form['lastname']
        role = request.form['role']
        password = request.form['password']
        
        if password == 'dabirstan012345':
            session['logged_in'] = True
            session['name'] = name
            session['lastname'] = lastname
            session['role'] = role
            return redirect('/admin')
        else:
            return render_template_string(HTML_TEMPLATE, error='رمز ورود اشتباه است', page='login')
    
    return render_template_string(HTML_TEMPLATE, page='login')

@app.route('/admin')
def admin_panel():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template_string(HTML_TEMPLATE, page='admin')

@app.route('/admin/profile')
def admin_profile():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template_string(HTML_TEMPLATE, page='profile')

@app.route('/admin/announcements')
def admin_announcements():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template_string(HTML_TEMPLATE, page='announcements', announcements=announcements)

@app.route('/admin/students')
def admin_students():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template_string(HTML_TEMPLATE, page='students')

@app.route('/admin/students/<grade>')
def grade_students(grade):
    if not session.get('logged_in'):
        return redirect('/')
    return render_template_string(HTML_TEMPLATE, page='grade_students', grade=grade)

@app.route('/admin/students/<grade>/<field>')
def field_students(grade, field):
    if not session.get('logged_in'):
        return redirect('/')
    
    field_mapping = {
        'math': 'ریاضی',
        'science': 'تجربی',
        'humanities': 'انسانی'
    }
    
    field_key = f"{field}_{grade}"
    field_name = field_mapping.get(field, field)
    
    return render_template_string(HTML_TEMPLATE, 
                                page='field_students', 
                                grade=grade, 
                                field=field, 
                                field_key=field_key, 
                                field_name=field_name,
                                students=students)

@app.route('/admin/students/<grade>/<field>/details/<int:index>')
def student_details(grade, field, index):
    if not session.get('logged_in'):
        return redirect('/')
    
    field_key = f"{field}_{grade}"
    
    if index >= len(students[field_key]):
        return redirect(f'/admin/students/{grade}/{field}')
    
    return render_template_string(HTML_TEMPLATE, 
                                page='student_details', 
                                grade=grade, 
                                field=field, 
                                field_key=field_key,
                                student_index=index,
                                students=students)

@app.route('/admin/students/<grade>/<field>/add', methods=['GET', 'POST'])
def add_student(grade, field):
    if not session.get('logged_in'):
        return redirect('/')
    
    field_key = f"{field}_{grade}"
    
    if request.method == 'POST':
        name = request.form['name']
        lastname = request.form['lastname']
        national_id = request.form['national_id']
        student_phone = request.form.get('student_phone', '')
        father_phone = request.form.get('father_phone', '')
        mother_phone = request.form.get('mother_phone', '')
        
        # بررسی فیلدهای اجباری
        if not name or not lastname or not national_id:
            return render_template_string(HTML_TEMPLATE, 
                                        page='add_student', 
                                        grade=grade, 
                                        field=field,
                                        error='فیلدهای اجباری را پر کنید')
        
        # اضافه کردن دانش آموز
        new_student = {
            'name': name,
            'lastname': lastname,
            'national_id': national_id,
            'student_phone': student_phone,
            'father_phone': father_phone,
            'mother_phone': mother_phone
        }
        
        students[field_key].append(new_student)
        
        return redirect(f'/admin/students/{grade}/{field}')
    
    return render_template_string(HTML_TEMPLATE, 
                                page='add_student', 
                                grade=grade, 
                                field=field)

@app.route('/admin/students/<grade>/<field>/edit/<int:index>', methods=['GET', 'POST'])
def edit_student(grade, field, index):
    if not session.get('logged_in'):
        return redirect('/')
    
    field_key = f"{field}_{grade}"
    
    if index >= len(students[field_key]):
        return redirect(f'/admin/students/{grade}/{field}')
    
    if request.method == 'POST':
        name = request.form['name']
        lastname = request.form['lastname']
        national_id = request.form['national_id']
        student_phone = request.form.get('student_phone', '')
        father_phone = request.form.get('father_phone', '')
        mother_phone = request.form.get('mother_phone', '')
        
        # بررسی فیلدهای اجباری
        if not name or not lastname or not national_id:
            return render_template_string(HTML_TEMPLATE, 
                                        page='edit_student', 
                                        grade=grade, 
                                        field=field,
                                        field_key=field_key,
                                        student_index=index,
                                        students=students,
                                        error='فیلدهای اجباری را پر کنید')
        
        # ویرایش دانش آموز
        students[field_key][index] = {
            'name': name,
            'lastname': lastname,
            'national_id': national_id,
            'student_phone': student_phone,
            'father_phone': father_phone,
            'mother_phone': mother_phone
        }
        
        return redirect(f'/admin/students/{grade}/{field}')
    
    return render_template_string(HTML_TEMPLATE, 
                                page='edit_student', 
                                grade=grade, 
                                field=field,
                                field_key=field_key,
                                student_index=index,
                                students=students)

@app.route('/admin/students/<field_key>/delete/<int:index>', methods=['POST'])
def delete_student(field_key, index):
    if not session.get('logged_in'):
        return redirect('/')
    
    if index < len(students[field_key]):
        students[field_key].pop(index)
    
    # استخراج grade و field از field_key
    parts = field_key.split('_')
    field = parts[0]
    grade = parts[1]
    
    return redirect(f'/admin/students/{grade}/{field}')

@app.route('/edit_profile', methods=['POST'])
def edit_profile():
    if not session.get('logged_in'):
        return redirect('/')
    
    field = request.form['field']
    value = request.form['value']
    
    if field in ['name', 'lastname', 'role']:
        session[field] = value
    
    return redirect('/admin/profile')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)