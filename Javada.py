from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    national_code = db.Column(db.String(20), unique=True, nullable=False)
    student_number = db.Column(db.String(20))
    father_phone = db.Column(db.String(20))
    mother_phone = db.Column(db.String(20))
    grade = db.Column(db.String(10), nullable=False)
    field = db.Column(db.String(20), nullable=False)

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.String(10), nullable=False)
    field = db.Column(db.String(20), nullable=False)
    subject = db.Column(db.String(50), nullable=False)

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_type = db.Column(db.String(20), nullable=False)
    sender_name = db.Column(db.String(200), nullable=False)
    related_name = db.Column(db.String(200))
    grade = db.Column(db.String(10))
    field = db.Column(db.String(20))
    subject = db.Column(db.String(50))
    content = db.Column(db.Text, nullable=False)

class Lab(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    images = db.Column(db.Text)
    description = db.Column(db.Text)

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    teacher_name = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    midterm1 = db.Column(db.Float)
    exam1 = db.Column(db.Float)
    midterm2 = db.Column(db.Float)
    exam2 = db.Column(db.Float)

class ReportCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    image_path = db.Column(db.String(300), nullable=False)

# HTML Templates
index_html = '''
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>دبیرستان پسرانه جوادالائمه</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: Tahoma, sans-serif; 
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: white;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .header { 
            text-align: center; 
            margin-bottom: 40px; 
            animation: fadeInDown 1s ease;
        }
        .header h1 { 
            font-size: 2.5rem; 
            background: linear-gradient(45deg, #ff00cc, #00eeff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 10px rgba(255, 0, 204, 0.5);
            margin-bottom: 10px;
        }
        .buttons-container { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 25px;
            width: 100%;
            max-width: 800px;
        }
        .btn {
            padding: 20px;
            border-radius: 15px;
            border: none;
            cursor: pointer;
            font-size: 1.2rem;
            font-weight: bold;
            text-align: center;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
        }
        .btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(45deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
            z-index: 1;
        }
        .btn span { position: relative; z-index: 2; }
        .btn:hover { transform: translateY(-8px) scale(1.02); box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4); }
        .btn:active { transform: scale(0.98); }
        .admin-btn { background: linear-gradient(45deg, #ff00cc, #ff0066); }
        .teacher-btn { background: linear-gradient(45deg, #00eeff, #0066ff); }
        .parent-btn { background: linear-gradient(45deg, #ffcc00, #ff6600); }
        .student-btn { background: linear-gradient(45deg, #00ff99, #00cc66); }
        .footer { margin-top: 40px; text-align: center; color: rgba(255,255,255,0.6); }
        @keyframes fadeInDown {
            from { opacity: 0; transform: translateY(-30px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>به سایت رسمی دبیرستان پسرانه جوادالائمه خوش آمدید</h1>
    </div>
    <div class="buttons-container">
        <button class="btn admin-btn" onclick="location.href='/admin-login'"><span>ورود مدیران<br>این بخش فقط برای مدیران است</span></button>
        <button class="btn teacher-btn" onclick="location.href='#'"><span>ورود معلمان<br>این بخش فقط برای معلمان است</span></button>
        <button class="btn parent-btn" onclick="location.href='#'"><span>ورود والدین<br>این بخش فقط برای والدین است</span></button>
        <button class="btn student-btn" onclick="location.href='#'"><span>ورود دانش آموزان<br>این بخش فقط برای دانش آموزان است</span></button>
    </div>
    <div class="footer">
        <p>سازنده : محمدرضا محمدی دانش آموز دبیرستان جوادالائمه (رشته ریاضی)</p>
    </div>
</body>
</html>
'''

admin_login_html = '''
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ورود مدیران</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: Tahoma, sans-serif; 
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: white;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .form-container {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            width: 100%;
            max-width: 400px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            animation: bounceIn 0.6s ease;
        }
        .form-container h2 {
            text-align: center;
            margin-bottom: 25px;
            background: linear-gradient(45deg, #ff00cc, #00eeff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
        }
        input, select {
            width: 100%;
            padding: 12px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            background: rgba(0, 0, 0, 0.2);
            color: white;
            font-size: 1rem;
            transition: all 0.3s;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #00eeff;
            box-shadow: 0 0 10px rgba(0, 238, 255, 0.5);
            transform: scale(1.02);
        }
        .btn {
            width: 100%;
            padding: 14px;
            border-radius: 10px;
            border: none;
            background: linear-gradient(45deg, #ff00cc, #ff0066);
            color: white;
            font-size: 1.1rem;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn:hover { transform: translateY(-3px); box-shadow: 0 5px 15px rgba(255, 0, 102, 0.4); }
        .error {
            color: #ff4444;
            background: rgba(255, 0, 0, 0.2);
            padding: 10px;
            border-radius: 8px;
            margin-top: 10px;
            text-align: center;
        }
        .back-btn {
            position: absolute;
            top: 20px;
            left: 20px;
            background: rgba(255, 255, 255, 0.1);
            border: none;
            color: white;
            padding: 10px 15px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 1.2rem;
        }
        .footer { margin-top: 30px; text-align: center; color: rgba(255,255,255,0.6); }
        @keyframes bounceIn {
            from { opacity: 0; transform: scale(0.8); }
            to { opacity: 1; transform: scale(1); }
        }
    </style>
</head>
<body>
    <button class="back-btn" onclick="location.href='/'">←</button>
    <div class="form-container">
        <h2>ورود مدیران</h2>
        <form method="POST">
            <div class="form-group">
                <label>نام</label>
                <input type="text" name="first_name" required>
            </div>
            <div class="form-group">
                <label>نام خانوادگی</label>
                <input type="text" name="last_name" required>
            </div>
            <div class="form-group">
                <label>مرتبه</label>
                <select name="role" required>
                    <option value="مدیر">مدیر</option>
                    <option value="ناظم">ناظم</option>
                    <option value="معاون">معاون</option>
                    <option value="مشاور">مشاور</option>
                </select>
            </div>
            <div class="form-group">
                <label>رمز</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit" class="btn">ورود</button>
            {% if error %}
                <div class="error">{{ error }}</div>
            {% endif %}
        </form>
    </div>
    <div class="footer">
        <p>سازنده : محمدرضا محمدی دانش آموز دبیرستان جوادالائمه (رشته ریاضی)</p>
    </div>
</body>
</html>
'''

admin_dashboard_html = '''
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>درگاه مدیران</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: Tahoma, sans-serif; 
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: white;
            min-height: 100vh;
            padding-top: 70px;
            padding-bottom: 60px;
        }
        .header {
            position: fixed;
            top: 0;
            width: 100%;
            background: rgba(0, 0, 0, 0.3);
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 100;
        }
        .menu-btn {
            background: none;
            border: none;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
        }
        .menu-container {
            position: fixed;
            top: 0;
            right: 0;
            width: 300px;
            height: 100%;
            background: rgba(30, 30, 60, 0.95);
            backdrop-filter: blur(10px);
            transform: translateX(100%);
            transition: transform 0.3s ease;
            z-index: 200;
            padding: 60px 20px 20px;
        }
        .menu-container.active {
            transform: translateX(0);
        }
        .menu-item {
            display: block;
            padding: 15px;
            margin: 10px 0;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            color: white;
            text-decoration: none;
            text-align: center;
            font-weight: bold;
            transition: all 0.3s;
        }
        .menu-item:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        .overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 150;
            display: none;
        }
        .overlay.active {
            display: block;
        }
        .dashboard-title {
            text-align: center;
            margin: 20px 0;
            background: linear-gradient(45deg, #ff00cc, #00eeff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 1.8rem;
        }
        .buttons-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }
        .btn {
            padding: 25px 15px;
            border-radius: 15px;
            border: none;
            cursor: pointer;
            font-size: 1.1rem;
            font-weight: bold;
            text-align: center;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
            color: white;
        }
        .btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(45deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
            z-index: 1;
        }
        .btn span { position: relative; z-index: 2; }
        .btn:hover { transform: translateY(-8px) scale(1.02); box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4); }
        .btn:active { transform: scale(0.98); }
        .students-btn { background: linear-gradient(45deg, #ff00cc, #ff0066); }
        .teachers-btn { background: linear-gradient(45deg, #00eeff, #0066ff); }
        .reports-parent-btn { background: linear-gradient(45deg, #ffcc00, #ff6600); }
        .reports-teacher-btn { background: linear-gradient(45deg, #00ff99, #00cc66); }
        .reports-student-btn { background: linear-gradient(45deg, #ff9900, #cc6600); }
        .lab-btn { background: linear-gradient(45deg, #9966ff, #6600cc); }
        .grades-btn { background: linear-gradient(45deg, #ff66cc, #cc0099); }
        .cards-btn { background: linear-gradient(45deg, #66ffcc, #00cc99); }
        .footer { position: fixed; bottom: 0; width: 100%; text-align: center; color: rgba(255,255,255,0.6); padding: 10px; background: rgba(0,0,0,0.3); }
    </style>
</head>
<body>
    <div class="header">
        <button class="menu-btn" id="menuBtn">☰</button>
        <h2>درگاه مدیران</h2>
    </div>
    
    <div class="menu-container" id="menuContainer">
        <a href="/admin-dashboard" class="menu-item">صفحه اصلی</a>
        <a href="/profile" class="menu-item">پروفایل</a>
        <a href="#" class="menu-item">اعلانات</a>
    </div>
    
    <div class="overlay" id="overlay"></div>
    
    <h1 class="dashboard-title">خوش آمدید، {{ admin_name }} ({{ admin_role }})</h1>
    
    <div class="buttons-container">
        <button class="btn students-btn" onclick="location.href='/manage-students'"><span>مدیریت دانش آموزان</span></button>
        <button class="btn teachers-btn" onclick="location.href='/manage-teachers'"><span>مدیریت معلمان</span></button>
        <button class="btn reports-parent-btn" onclick="location.href='/manage-reports/parent'"><span>گزارشات والدین</span></button>
        <button class="btn reports-teacher-btn" onclick="location.href='/manage-reports/teacher'"><span>گزارشات معلمان</span></button>
        <button class="btn reports-student-btn" onclick="location.href='/manage-reports/student'"><span>گزارشات دانش آموزان</span></button>
        <button class="btn lab-btn" onclick="location.href='/manage-lab'"><span>مدیریت آزمایشگاه</span></button>
        <button class="btn grades-btn" onclick="location.href='/manage-grades'"><span>مدیریت نمرات</span></button>
        <button class="btn cards-btn" onclick="location.href='/manage-report-cards'"><span>مدیریت کارنامه</span></button>
    </div>
    
    <div class="footer">
        <p>سازنده : محمدرضا محمدی دانش آموز دبیرستان جوادالائمه (رشته ریاضی)</p>
    </div>
    
    <script>
        document.getElementById('menuBtn').addEventListener('click', function() {
            const menu = document.getElementById('menuContainer');
            const overlay = document.getElementById('overlay');
            menu.classList.toggle('active');
            overlay.classList.toggle('active');
        });
        
        document.getElementById('overlay').addEventListener('click', function() {
            document.getElementById('menuContainer').classList.remove('active');
            this.classList.remove('active');
        });
    </script>
</body>
</html>
'''

manage_students_html = '''
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مدیریت دانش آموزان</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: Tahoma, sans-serif; 
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: white;
            min-height: 100vh;
            padding-top: 70px;
            padding-bottom: 60px;
        }
        .header {
            position: fixed;
            top: 0;
            width: 100%;
            background: rgba(0, 0, 0, 0.3);
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 100;
        }
        .menu-btn {
            background: none;
            border: none;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
        }
        .menu-container {
            position: fixed;
            top: 0;
            right: 0;
            width: 300px;
            height: 100%;
            background: rgba(30, 30, 60, 0.95);
            backdrop-filter: blur(10px);
            transform: translateX(100%);
            transition: transform 0.3s ease;
            z-index: 200;
            padding: 60px 20px 20px;
        }
        .menu-container.active {
            transform: translateX(0);
        }
        .menu-item {
            display: block;
            padding: 15px;
            margin: 10px 0;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            color: white;
            text-decoration: none;
            text-align: center;
            font-weight: bold;
            transition: all 0.3s;
        }
        .menu-item:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        .overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 150;
            display: none;
        }
        .overlay.active {
            display: block;
        }
        .section-title {
            text-align: center;
            margin: 20px 0;
            background: linear-gradient(45deg, #ff00cc, #00eeff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 1.8rem;
        }
        .grade-buttons {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin: 20px 0;
            flex-wrap: wrap;
        }
        .btn {
            padding: 15px 25px;
            border-radius: 10px;
            border: none;
            cursor: pointer;
            font-size: 1rem;
            font-weight: bold;
            text-align: center;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
            color: white;
        }
        .btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(45deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
            z-index: 1;
        }
        .btn span { position: relative; z-index: 2; }
        .btn:hover { transform: translateY(-5px) scale(1.05); box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4); }
        .btn:active { transform: scale(0.98); }
        .grade-btn { background: linear-gradient(45deg, #ff00cc, #ff0066); }
        .field-btn { background: linear-gradient(45deg, #00eeff, #0066ff); }
        .students-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .student-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 15px;
            margin: 15px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s;
            cursor: pointer;
        }
        .student-card:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-3px);
        }
        .student-info {
            flex: 1;
        }
        .student-name {
            font-weight: bold;
            font-size: 1.1rem;
        }
        .student-national {
            color: #aaa;
            font-size: 0.9rem;
        }
        .student-actions {
            display: flex;
            gap: 10px;
        }
        .action-btn {
            width: 35px;
            height: 35px;
            border-radius: 50%;
            border: none;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s;
        }
        .edit-btn { background: #ffcc00; color: black; }
        .delete-btn { background: #ff4444; color: white; }
        .add-btn {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            border: none;
            background: #00eeff;
            color: black;
            font-size: 2rem;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
            transition: all 0.3s;
        }
        .add-btn:hover {
            transform: scale(1.1);
            box-shadow: 0 8px 20px rgba(0, 238, 255, 0.5);
        }
        .search-container {
            display: flex;
            justify-content: center;
            margin: 20px 0;
            padding: 0 20px;
        }
        .search-box {
            width: 100%;
            max-width: 500px;
            padding: 12px 15px;
            border-radius: 30px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            background: rgba(0, 0, 0, 0.2);
            color: white;
            font-size: 1rem;
        }
        .search-btn {
            margin-right: 10px;
            padding: 12px 20px;
            border-radius: 30px;
            border: none;
            background: #00eeff;
            color: black;
            font-weight: bold;
            cursor: pointer;
        }
        .footer { position: fixed; bottom: 0; width: 100%; text-align: center; color: rgba(255,255,255,0.6); padding: 10px; background: rgba(0,0,0,0.3); }
    </style>
</head>
<body>
    <div class="header">
        <button class="menu-btn" id="menuBtn">☰</button>
        <h2>مدیریت دانش آموزان</h2>
    </div>
    
    <div class="menu-container" id="menuContainer">
        <a href="/admin-dashboard" class="menu-item">صفحه اصلی</a>
        <a href="/profile" class="menu-item">پروفایل</a>
        <a href="#" class="menu-item">اعلانات</a>
    </div>
    
    <div class="overlay" id="overlay"></div>
    
    <h1 class="section-title">پایه‌ها</h1>
    <div class="grade-buttons">
        <button class="btn grade-btn" onclick="location.href='/students/دهم/ریاضی'"><span>پایه دهم</span></button>
        <button class="btn grade-btn" onclick="location.href='/students/یازدهم/ریاضی'"><span>پایه یازدهم</span></button>
        <button class="btn grade-btn" onclick="location.href='/students/دوازدهم/ریاضی'"><span>پایه دوازدهم</span></button>
    </div>
    
    <div class="footer">
        <p>سازنده : محمدرضا محمدی دانش آموز دبیرستان جوادالائمه (رشته ریاضی)</p>
    </div>
    
    <script>
        document.getElementById('menuBtn').addEventListener('click', function() {
            const menu = document.getElementById('menuContainer');
            const overlay = document.getElementById('overlay');
            menu.classList.toggle('active');
            overlay.classList.toggle('active');
        });
        
        document.getElementById('overlay').addEventListener('click', function() {
            document.getElementById('menuContainer').classList.remove('active');
            this.classList.remove('active');
        });
    </script>
</body>
</html>
'''

students_list_html = '''
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>دانش آموزان {{ grade }} {{ field }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: Tahoma, sans-serif; 
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: white;
            min-height: 100vh;
            padding-top: 70px;
            padding-bottom: 60px;
        }
        .header {
            position: fixed;
            top: 0;
            width: 100%;
            background: rgba(0, 0, 0, 0.3);
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 100;
        }
        .menu-btn {
            background: none;
            border: none;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
        }
        .menu-container {
            position: fixed;
            top: 0;
            right: 0;
            width: 300px;
            height: 100%;
            background: rgba(30, 30, 60, 0.95);
            backdrop-filter: blur(10px);
            transform: translateX(100%);
            transition: transform 0.3s ease;
            z-index: 200;
            padding: 60px 20px 20px;
        }
        .menu-container.active {
            transform: translateX(0);
        }
        .menu-item {
            display: block;
            padding: 15px;
            margin: 10px 0;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            color: white;
            text-decoration: none;
            text-align: center;
            font-weight: bold;
            transition: all 0.3s;
        }
        .menu-item:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        .overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 150;
            display: none;
        }
        .overlay.active {
            display: block;
        }
        .section-title {
            text-align: center;
            margin: 20px 0;
            background: linear-gradient(45deg, #ff00cc, #00eeff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 1.8rem;
        }
        .field-buttons {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin: 20px 0;
            flex-wrap: wrap;
        }
        .btn {
            padding: 15px 25px;
            border-radius: 10px;
            border: none;
            cursor: pointer;
            font-size: 1rem;
            font-weight: bold;
            text-align: center;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
            color: white;
        }
        .btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(45deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
            z-index: 1;
        }
        .btn span { position: relative; z-index: 2; }
        .btn:hover { transform: translateY(-5px) scale(1.05); box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4); }
        .btn:active { transform: scale(0.98); }
        .field-btn { background: linear-gradient(45deg, #ff00cc, #ff0066); }
        .students-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .student-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 15px;
            margin: 15px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s;
            cursor: pointer;
        }
        .student-card:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-3px);
        }
        .student-info {
            flex: 1;
        }
        .student-name {
            font-weight: bold;
            font-size: 1.1rem;
        }
        .student-national {
            color: #aaa;
            font-size: 0.9rem;
        }
        .student-actions {
            display: flex;
            gap: 10px;
        }
        .action-btn {
            width: 35px;
            height: 35px;
            border-radius: 50%;
            border: none;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s;
        }
        .edit-btn { background: #ffcc00; color: black; }
        .delete-btn { background: #ff4444; color: white; }
        .add-btn {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            border: none;
            background: #00eeff;
            color: black;
            font-size: 2rem;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
            transition: all 0.3s;
        }
        .add-btn:hover {
            transform: scale(1.1);
            box-shadow: 0 8px 20px rgba(0, 238, 255, 0.5);
        }
        .search-container {
            display: flex;
            justify-content: center;
            margin: 20px 0;
            padding: 0 20px;
        }
        .search-box {
            width: 100%;
            max-width: 500px;
            padding: 12px 15px;
            border-radius: 30px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            background: rgba(0, 0, 0, 0.2);
            color: white;
            font-size: 1rem;
        }
        .search-btn {
            margin-right: 10px;
            padding: 12px 20px;
            border-radius: 30px;
            border: none;
            background: #00eeff;
            color: black;
            font-weight: bold;
            cursor: pointer;
        }
        .footer { position: fixed; bottom: 0; width: 100%; text-align: center; color: rgba(255,255,255,0.6); padding: 10px; background: rgba(0,0,0,0.3); }
    </style>
</head>
<body>
    <div class="header">
        <button class="menu-btn" id="menuBtn">☰</button>
        <h2>دانش آموزان {{ grade }} {{ field }}</h2>
    </div>
    
    <div class="menu-container" id="menuContainer">
        <a href="/admin-dashboard" class="menu-item">صفحه اصلی</a>
        <a href="/profile" class="menu-item">پروفایل</a>
        <a href="#" class="menu-item">اعلانات</a>
    </div>
    
    <div class="overlay" id="overlay"></div>
    
    <h1 class="section-title">رشته‌ها</h1>
    <div class="field-buttons">
        <button class="btn field-btn" onclick="location.href='/students/{{ grade }}/ریاضی'"><span>ریاضی</span></button>
        <button class="btn field-btn" onclick="location.href='/students/{{ grade }}/تجربی'"><span>تجربی</span></button>
        <button class="btn field-btn" onclick="location.href='/students/{{ grade }}/انسانی'"><span>انسانی</span></button>
    </div>
    
    <div class="search-container">
        <input type="text" class="search-box" placeholder="جستجوی نام، نام خانوادگی یا کد ملی...">
        <button class="search-btn">جستجو</button>
    </div>
    
    <div class="students-container">
        {% for student in students %}
        <div class="student-card" onclick="location.href='/view-student/{{ student.id }}'">
            <div class="student-info">
                <div class="student-name">{{ student.first_name }} {{ student.last_name }}</div>
                <div class="student-national">{{ student.national_code }}</div>
            </div>
            <div class="student-actions">
                <button class="action-btn edit-btn" onclick="event.stopPropagation(); editStudent({{ student.id }})">✎</button>
                <button class="action-btn delete-btn" onclick="event.stopPropagation(); deleteStudent({{ student.id }})">🗑</button>
            </div>
        </div>
        {% endfor %}
    </div>
    
    <button class="add-btn" onclick="showAddForm()">+</button>
    
    <div id="addForm" style="display:none; position:fixed; top:50%; left:50%; transform:translate(-50%,-50%); background:rgba(0,0,0,0.8); padding:20px; border-radius:10px; z-index:300; width:90%; max-width:500px;">
        <h3>افزودن دانش آموز</h3>
        <form id="studentForm">
            <div style="margin-bottom:15px;">
                <label>نام دانش آموز (اجباری)</label>
                <input type="text" name="first_name" required style="width:100%; padding:10px; border-radius:5px; border:1px solid #555; background:rgba(0,0,0,0.5); color:white;">
            </div>
            <div style="margin-bottom:15px;">
                <label>نام خانوادگی دانش آموز (اجباری)</label>
                <input type="text" name="last_name" required style="width:100%; padding:10px; border-radius:5px; border:1px solid #555; background:rgba(0,0,0,0.5); color:white;">
            </div>
            <div style="margin-bottom:15px;">
                <label>کد ملی دانش آموز (اجباری)</label>
                <input type="text" name="national_code" required style="width:100%; padding:10px; border-radius:5px; border:1px solid #555; background:rgba(0,0,0,0.5); color:white;">
            </div>
            <div style="margin-bottom:15px;">
                <label>شماره دانش آموز (اختیاری)</label>
                <input type="text" name="student_number" style="width:100%; padding:10px; border-radius:5px; border:1px solid #555; background:rgba(0,0,0,0.5); color:white;">
            </div>
            <div style="margin-bottom:15px;">
                <label>شماره پدر (اختیاری)</label>
                <input type="text" name="father_phone" style="width:100%; padding:10px; border-radius:5px; border:1px solid #555; background:rgba(0,0,0,0.5); color:white;">
            </div>
            <div style="margin-bottom:15px;">
                <label>شماره مادر (اختیاری)</label>
                <input type="text" name="mother_phone" style="width:100%; padding:10px; border-radius:5px; border:1px solid #555; background:rgba(0,0,0,0.5); color:white;">
            </div>
            <div style="display:flex; justify-content:space-between;">
                <button type="button" onclick="hideAddForm()">انصراف</button>
                <button type="submit">تایید</button>
            </div>
        </form>
    </div>
    
    <div class="footer">
        <p>سازنده : محمدرضا محمدی دانش آموز دبیرستان جوادالائمه (رشته ریاضی)</p>
    </div>
    
    <script>
        document.getElementById('menuBtn').addEventListener('click', function() {
            const menu = document.getElementById('menuContainer');
            const overlay = document.getElementById('overlay');
            menu.classList.toggle('active');
            overlay.classList.toggle('active');
        });
        
        document.getElementById('overlay').addEventListener('click', function() {
            document.getElementById('menuContainer').classList.remove('active');
            this.classList.remove('active');
        });
        
        function showAddForm() {
            document.getElementById('addForm').style.display = 'block';
            document.getElementById('studentForm').onsubmit = function(e) {
                e.preventDefault();
                const formData = new FormData(this);
                fetch('/add-student/{{ grade }}/{{ field }}', {
                    method: 'POST',
                    body: new URLSearchParams(new FormData(this))
                })
                .then(response => response.json())
                .then(data => {
                    if(data.success) {
                        alert('دانش آموز با موفقیت اضافه شد');
                        location.reload();
                    } else {
                        alert(data.message);
                    }
                });
            };
        }
        
        function hideAddForm() {
            document.getElementById('addForm').style.display = 'none';
        }
        
        function deleteStudent(id) {
            if(confirm('آیا مطمئن هستید می‌خواهید اطلاعات دانش آموز را پاک کنید؟')) {
                fetch('/delete-student/' + id)
                .then(response => response.json())
                .then(data => {
                    if(data.success) location.reload();
                });
            }
        }
        
        function editStudent(id) {
            alert('ویرایش دانش آموز ' + id);
            // در نسخه کامل این قسمت اجرا می‌شود
        }
    </script>
</body>
</html>
'''

# Routes
@app.route('/')
def index():
    return render_template_string(index_html)

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        role = request.form['role']
        password = request.form['password']
        
        if password != 'dabirestan012345':
            return render_template_string(admin_login_html, error='رمز عبور اشتباه است')
        
        admin = Admin(first_name=first_name, last_name=last_name, role=role, password=password)
        db.session.add(admin)
        db.session.commit()
        session['admin_id'] = admin.id
        session['admin_name'] = f"{first_name} {last_name}"
        session['admin_role'] = role
        return redirect(url_for('admin_dashboard'))
    
    return render_template_string(admin_login_html)

@app.route('/admin-dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    return render_template_string(admin_dashboard_html, admin_name=session['admin_name'], admin_role=session['admin_role'])

@app.route('/manage-students')
def manage_students():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    return render_template_string(manage_students_html)

@app.route('/students/<grade>/<field>')
def students_list(grade, field):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    students = Student.query.filter_by(grade=grade, field=field).all()
    return render_template_string(students_list_html, students=students, grade=grade, field=field)

@app.route('/add-student/<grade>/<field>', methods=['POST'])
def add_student(grade, field):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    national_code = request.form['national_code']
    student_number = request.form.get('student_number', '')
    father_phone = request.form.get('father_phone', '')
    mother_phone = request.form.get('mother_phone', '')
    
    if Student.query.filter_by(national_code=national_code).first():
        return jsonify(success=False, message='دانش‌آموز با این کد ملی وجود دارد')
    
    student = Student(
        first_name=first_name,
        last_name=last_name,
        national_code=national_code,
        student_number=student_number,
        father_phone=father_phone,
        mother_phone=mother_phone,
        grade=grade,
        field=field
    )
    db.session.add(student)
    db.session.commit()
    return jsonify(success=True)

@app.route('/delete-student/<int:student_id>')
def delete_student(student_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    return jsonify(success=True)

@app.route('/view-student/<int:student_id>')
def view_student(student_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    student = Student.query.get_or_404(student_id)
    return f'''
    <div style="background:linear-gradient(135deg, #0f0c29, #302b63, #24243e); color:white; min-height:100vh; padding:20px;">
        <h1 style="text-align:center; background:linear-gradient(45deg, #ff00cc, #00eeff); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">اطلاعات دانش آموز</h1>
        <div style="max-width:600px; margin:0 auto; background:rgba(255,255,255,0.1); padding:20px; border-radius:10px;">
            <p><strong>نام دانش آموز:</strong> {student.first_name}</p>
            <p><strong>نام خانوادگی دانش آموز:</strong> {student.last_name}</p>
            <p><strong>کد ملی دانش آموز:</strong> {student.national_code}</p>
            <p><strong>شماره دانش آموز:</strong> {student.student_number or 'ثبت نشده'}</p>
            <p><strong>شماره پدر:</strong> {student.father_phone or 'ثبت نشده'}</p>
            <p><strong>شماره مادر:</strong> {student.mother_phone or 'ثبت نشده'}</p>
            <button onclick="history.back()" style="padding:10px 20px; background:#00eeff; color:black; border:none; border-radius:5px; cursor:pointer;">بازگشت</button>
        </div>
        <div style="position:fixed; bottom:0; width:100%; text-align:center; color:rgba(255,255,255,0.6); padding:10px; background:rgba(0,0,0,0.3);">
            <p>سازنده : محمدرضا محمدی دانش آموز دبیرستان جوادالائمه (رشته ریاضی)</p>
        </div>
    </div>
    '''

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Initialize DB
def create_tables():
    with app.app_context():
        db.create_all()
        # Add default admin if not exists
        if not Admin.query.first():
            admin = Admin(
                first_name='مدیر',
                last_name='اصلی',
                role='مدیر',
                password='dabirestan012345'
            )
            db.session.add(admin)
            db.session.commit()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))  # استفاده از پورت 10000 در صورت عدم وجود متغیر PORT
    app.run(host='0.0.0.0', port=port, debug=True)