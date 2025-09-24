# javadol0.py

from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify
import json
import os
import hashlib

# کلید امنیتی
SECRET_KEY = "my_secret_key_2025_dabirestan"

app = Flask(__name__)
app.secret_key = SECRET_KEY

DATA_FILE = "data.json"

def load_data():
    """بارگذاری داده‌ها از فایل JSON."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"students": {}, "announcements": [], "admin": None, "teachers": []}

def save_data(data):
    """ذخیره داده‌ها در فایل JSON."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_current_user():
    """دریافت اطلاعات کاربر وارد شده (مدیر یا معلم)."""
    if 'admin_id' in session:
        data = load_data()
        admin = data.get("admin")
        if admin and admin.get("id") == session['admin_id']:
            return admin, "admin"
    if 'teacher_id' in session:
        data = load_data()
        teachers = data.get("teachers", [])
        for t in teachers:
            if t.get("id") == session['teacher_id']:
                return t, "teacher"
    return None, None

# --- ROUTES ---

@app.route("/")
def index():
    """صفحه اصلی سایت."""
    html = '''
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>دبیرستان جوادالائمه</title>
        <link href="https://v1.fontapi.ir/css/Vazirmatn" rel="stylesheet">
        <style>
            @import url('https://v1.fontapi.ir/css/Vazirmatn');
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: 'Vazirmatn', sans-serif;
                background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
                color: white;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                overflow-x: hidden;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                flex: 1;
                overflow-y: auto;
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
                animation: fadeInDown 1s ease-out;
            }
            .header h1 {
                font-size: 2.5rem;
                background: linear-gradient(to right, #ff00cc, #00eeff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-shadow: 0 0 10px rgba(255, 0, 204, 0.5), 0 0 20px rgba(0, 238, 255, 0.5);
            }
            .buttons-container {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }
            .btn {
                padding: 20px 15px;
                border-radius: 15px;
                border: none;
                color: white;
                font-size: 1.2rem;
                cursor: pointer;
                transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
                position: relative;
                overflow: hidden;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                text-align: center;
            }
            .btn::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(45deg, #ff00cc, #ff0066);
                z-index: -1;
                opacity: 0.7;
                transition: opacity 0.4s;
            }
            .btn:hover::before {
                opacity: 1;
            }
            .btn:hover {
                transform: translateY(-8px) scale(1.02);
                box-shadow: 0 8px 30px rgba(255, 255, 255, 0.2);
            }
            .btn:active {
                transform: scale(0.98);
            }
            .btn-admin::before { background: linear-gradient(45deg, #ff00cc, #ff0066); }
            .btn-teacher::before { background: linear-gradient(45deg, #00eeff, #0066ff); }
            .btn-parent::before { background: linear-gradient(45deg, #ffcc00, #ff6600); }
            .btn-student::before { background: linear-gradient(45deg, #00ff99, #00cc66); }

            .creator-info {
                text-align: center;
                margin-top: 30px;
                padding: 10px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                animation: pulse 2s infinite;
            }

            @keyframes fadeInDown {
                from { opacity: 0; transform: translate3d(0, -20px, 0); }
                to { opacity: 1; transform: translate3d(0, 0, 0); }
            }
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.05); }
                100% { transform: scale(1); }
            }
            @media (max-width: 768px) {
                .header h1 { font-size: 1.8rem; }
                .btn { padding: 15px 10px; font-size: 1rem; }
                .buttons-container { grid-template-columns: 1fr; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>به سایت رسمی دبیرستان پسرانه جوادالائمه خوش آمدید</h1>
            </div>
            <div class="buttons-container">
                <button class="btn btn-admin" onclick="window.location.href='/admin-login'">ورود مدیران<br><small>این بخش فقط برای مدیران است</small></button>
                <button class="btn btn-teacher" onclick="window.location.href='/teacher-login'">ورود معلمان<br><small>این بخش فقط برای معلمان است</small></button>
                <button class="btn btn-parent">ورود والدین<br><small>این بخش فقط برای والدین است</small></button>
                <button class="btn btn-student">ورود دانش‌آموزان<br><small>این بخش فقط برای دانش آموزان است</small></button>
            </div>
            <div class="creator-info">
                سازنده: محمدرضا محمدی - دانش آموز دبیرستان جوادالائمه (رشته ریاضی)
            </div>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    """ورود مدیران."""
    if request.method == "POST":
        name = request.form.get("name")
        lastname = request.form.get("lastname")
        role = request.form.get("role")
        password = request.form.get("password")

        if not name or not lastname or not role or not password:
            error = "لطفاً همه فیلدها را پر کنید."
            return render_template_string(login_html, error=error, is_admin=True)

        if password != "dabirestan012345":
            error = "رمز عبور اشتباه است."
            return render_template_string(login_html, error=error, is_admin=True)

        data = load_data()
        admin_id = hashlib.md5((name + lastname + role).encode()).hexdigest()
        data["admin"] = {
            "id": admin_id,
            "name": name,
            "lastname": lastname,
            "role": role
        }
        save_data(data)
        session["admin_id"] = admin_id
        return redirect(url_for("admin_dashboard"))

    return render_template_string(login_html, is_admin=True)

@app.route("/teacher-login", methods=["GET", "POST"])
def teacher_login():
    """ورود معلمان."""
    if request.method == "POST":
        name = request.form.get("name")
        lastname = request.form.get("lastname")
        grade = request.form.get("grade")
        field = request.form.get("field")
        subject = request.form.get("subject")
        password = request.form.get("password")

        if not name or not lastname or not grade or not field or not subject or not password:
            error = "لطفاً همه فیلدها را پر کنید."
            return render_template_string(login_html, error=error, is_admin=False)

        if password != "dabirestan012345":
            error = "رمز عبور اشتباه است."
            return render_template_string(login_html, error=error, is_admin=False)

        data = load_data()
        teacher_id = hashlib.md5((name + lastname + subject).encode()).hexdigest()
        teacher_data = {
            "id": teacher_id,
            "name": name,
            "lastname": lastname,
            "grade": grade,
            "field": field,
            "subject": subject
        }
        if teacher_data not in data.get("teachers", []):
            data.setdefault("teachers", []).append(teacher_data)
        save_data(data)
        session["teacher_id"] = teacher_id
        return redirect(url_for("teacher_dashboard"))

    return render_template_string(login_html, is_admin=False)

login_html = '''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% if is_admin %}ورود مدیر{% else %}ورود معلم{% endif %}</title>
    <link href="https://v1.fontapi.ir/css/Vazirmatn" rel="stylesheet">
    <style>
        @import url('https://v1.fontapi.ir/css/Vazirmatn');
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Vazirmatn', sans-serif;
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
            padding: 30px;
            border-radius: 20px;
            width: 100%;
            max-width: 500px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            animation: bounceIn 0.6s ease-out;
            margin-top: 60px; /* فاصله از دکمه بازگشت */
        }
        .back-btn {
            position: absolute;
            top: 20px;
            left: 20px;
            padding: 10px 15px;
            border-radius: 10px;
            border: none;
            background: linear-gradient(45deg, #666666, #999999);
            color: white;
            cursor: pointer;
            transition: all 0.3s;
        }
        .back-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 4px 15px rgba(255, 255, 255, 0.2);
        }
        h2 {
            text-align: center;
            margin-bottom: 20px;
            background: linear-gradient(to right, #00eeff, #0066ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            color: #ccc;
        }
        .form-group input, .form-group select {
            width: 100%;
            padding: 15px;
            border-radius: 10px;
            border: 2px solid rgba(255, 255, 255, 0.2);
            background: rgba(0, 0, 0, 0.2);
            color: white;
            font-size: 1rem;
            transition: all 0.3s;
        }
        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: #00eeff;
            box-shadow: 0 0 10px rgba(0, 238, 255, 0.5);
            transform: scale(1.02);
        }
        .submit-btn {
            width: 100%;
            padding: 15px;
            border-radius: 10px;
            border: none;
            background: linear-gradient(45deg, #00eeff, #0066ff);
            color: white;
            font-size: 1.1rem;
            cursor: pointer;
            transition: all 0.3s;
        }
        .submit-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(0, 238, 255, 0.4);
        }
        .error {
            color: #ff4444;
            text-align: center;
            margin-top: 10px;
            background: rgba(255, 0, 0, 0.2);
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #ff4444;
        }
        @keyframes bounceIn {
            from, 20%, 40%, 60%, 80%, to {
                animation-timing-function: cubic-bezier(0.215, 0.61, 0.355, 1);
            }
            0% {
                opacity: 0;
                transform: scale3d(0.3, 0.3, 0.3);
            }
            20% {
                transform: scale3d(1.1, 1.1, 1.1);
            }
            40% {
                transform: scale3d(0.9, 0.9, 0.9);
            }
            60% {
                opacity: 1;
                transform: scale3d(1.03, 1.03, 1.03);
            }
            80% {
                transform: scale3d(0.97, 0.97, 0.97);
            }
            to {
                opacity: 1;
                transform: scale3d(1, 1, 1);
            }
        }
        @media (max-width: 768px) {
            .form-container {
                padding: 20px;
                margin-top: 40px;
            }
            .back-btn {
                top: 10px;
                left: 10px;
            }
        }
    </style>
</head>
<body>
    <button class="back-btn" onclick="window.location.href='/'">بازگشت</button>
    <div class="form-container">
        <h2>{% if is_admin %}ورود مدیر{% else %}ورود معلم{% endif %}</h2>
        <form method="POST">
            <div class="form-group">
                <label>نام</label>
                <input type="text" name="name" required>
            </div>
            <div class="form-group">
                <label>نام خانوادگی</label>
                <input type="text" name="lastname" required>
            </div>
            {% if is_admin %}
            <div class="form-group">
                <label>انتخاب مرتبه</label>
                <select name="role" required>
                    <option value="">انتخاب کنید</option>
                    <option value="مدیر">مدیر</option>
                    <option value="ناظم">ناظم</option>
                    <option value="معاون">معاون</option>
                    <option value="مشاور">مشاور</option>
                </select>
            </div>
            {% else %}
            <div class="form-group">
                <label>پایه تدریس</label>
                <select name="grade" required>
                    <option value="">انتخاب کنید</option>
                    <option value="دهم">دهم</option>
                    <option value="یازدهم">یازدهم</option>
                    <option value="دوازدهم">دوازدهم</option>
                </select>
            </div>
            <div class="form-group">
                <label>رشته تدریس</label>
                <select name="field" required>
                    <option value="">انتخاب کنید</option>
                    <option value="ریاضی">ریاضی</option>
                    <option value="تجربی">تجربی</option>
                    <option value="انسانی">انسانی</option>
                </select>
            </div>
            <div class="form-group">
                <label>نام درس</label>
                <input type="text" name="subject" required>
            </div>
            {% endif %}
            <div class="form-group">
                <label>رمز عبور</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit" class="submit-btn">ورود</button>
        </form>
        {% if error %}
            <div class="error">{{ error }}</div>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route("/admin-dashboard")
def admin_dashboard():
    """درگاه مدیران."""
    user, role = get_current_user()
    if not user or role != "admin":
        return redirect(url_for("index"))

    html = '''
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>درگاه مدیران</title>
        <link href="https://v1.fontapi.ir/css/Vazirmatn" rel="stylesheet">
        <style>
            @import url('https://v1.fontapi.ir/css/Vazirmatn');
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: 'Vazirmatn', sans-serif;
                background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
                color: white;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                padding-bottom: 60px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                flex: 1;
                overflow-y: auto;
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
                animation: fadeInDown 1s ease-out;
            }
            .header h1 {
                font-size: 2.5rem;
                background: linear-gradient(to right, #ff00cc, #00eeff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-shadow: 0 0 10px rgba(255, 0, 204, 0.5), 0 0 20px rgba(0, 238, 255, 0.5);
            }
            .grid-buttons {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }
            .btn {
                padding: 20px 15px;
                border-radius: 15px;
                border: none;
                color: white;
                font-size: 1.2rem;
                cursor: pointer;
                transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
                position: relative;
                overflow: hidden;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                text-align: center;
            }
            .btn::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(45deg, #32cd32, #228b22);
                z-index: -1;
                opacity: 0.7;
                transition: opacity 0.4s;
            }
            .btn:hover::before {
                opacity: 1;
            }
            .btn:hover {
                transform: translateY(-8px) scale(1.02);
                box-shadow: 0 8px 30px rgba(255, 255, 255, 0.2);
            }
            .btn:active {
                transform: scale(0.98);
            }
            .btn-students::before { background: linear-gradient(45deg, #32cd32, #228b22); }
            .btn-teachers::before { background: linear-gradient(45deg, #00eeff, #0066ff); }
            .btn-reports-parents::before { background: linear-gradient(45deg, #ffcc00, #ff6600); }
            .btn-reports-teachers::before { background: linear-gradient(45deg, #00bfff, #1e90ff); }
            .btn-reports-students::before { background: linear-gradient(45deg, #ff6b6b, #ff8e53); }
            .btn-labs::before { background: linear-gradient(45deg, #9932cc, #4b0082); }
            .btn-announcements::before { background: linear-gradient(45deg, #00bfff, #1e90ff); }

            .creator-info {
                text-align: center;
                margin-top: 30px;
                padding: 10px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                animation: pulse 2s infinite;
            }

            .toolbar {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background: rgba(0, 0, 0, 0.9);
                backdrop-filter: blur(10px);
                border-top: 2px solid rgba(255, 255, 255, 0.1);
                display: flex;
                justify-content: space-around;
                padding: 15px 0;
                z-index: 1000;
            }
            .toolbar-item {
                display: flex;
                flex-direction: column;
                align-items: center;
                text-decoration: none;
                color: white;
                transition: all 0.3s;
                padding: 5px 10px;
                border-radius: 10px;
            }
            .toolbar-item:hover {
                transform: translateY(-8px);
                background: rgba(0, 238, 255, 0.2);
                box-shadow: 0 0 15px rgba(0, 238, 255, 0.5);
            }
            .toolbar-icon {
                font-size: 1.5rem;
                margin-bottom: 3px;
            }
            .active {
                background: rgba(0, 238, 255, 0.2);
                box-shadow: 0 0 15px rgba(0, 238, 255, 0.5);
            }

            @keyframes fadeInDown {
                from { opacity: 0; transform: translate3d(0, -20px, 0); }
                to { opacity: 1; transform: translate3d(0, 0, 0); }
            }
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.05); }
                100% { transform: scale(1); }
            }
            @media (max-width: 768px) {
                .header h1 { font-size: 1.8rem; }
                .btn { padding: 15px 10px; font-size: 1rem; }
                .grid-buttons { grid-template-columns: 1fr; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>درگاه مدیران</h1>
            </div>
            <div class="grid-buttons">
                <button class="btn btn-students" onclick="window.location.href='/manage-students'">مدیریت دانش‌آموزان</button>
                <button class="btn btn-teachers">مدیریت معلمان</button>
                <button class="btn btn-reports-parents">مدیریت گزارشات والدین</button>
                <button class="btn btn-reports-teachers">مدیریت گزارشات معلمان</button>
                <button class="btn btn-reports-students">مدیریت گزارشات دانش آموزان</button>
                <button class="btn btn-labs">مدیریت بخش آزمایشگاه</button>
                <button class="btn btn-announcements" onclick="window.location.href='/announcements'">اعلانات</button>
            </div>
            <div class="creator-info">
                سازنده: محمدرضا محمدی - دانش آموز دبیرستان جوادالائمه (رشته ریاضی)
            </div>
        </div>

        <div class="toolbar">
            <a href="/admin-dashboard" class="toolbar-item active">
                <span class="toolbar-icon">🏠</span>
                <span>صفحه اصلی</span>
            </a>
            <a href="/announcements" class="toolbar-item">
                <span class="toolbar-icon">📢</span>
                <span>اعلانات</span>
            </a>
            <a href="/profile" class="toolbar-item">
                <span class="toolbar-icon">👤</span>
                <span>پروفایل</span>
            </a>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route("/announcements")
def announcements():
    """صفحه اعلانات."""
    user, role = get_current_user()
    if not user:
        return redirect(url_for("index"))

    html = '''
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>اعلانات</title>
        <link href="https://v1.fontapi.ir/css/Vazirmatn" rel="stylesheet">
        <style>
            @import url('https://v1.fontapi.ir/css/Vazirmatn');
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: 'Vazirmatn', sans-serif;
                background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
                color: white;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                padding-bottom: 60px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                flex: 1;
                overflow-y: auto;
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
            }
            .header h1 {
                font-size: 2.5rem;
                background: linear-gradient(to right, #00bfff, #1e90ff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-shadow: 0 0 10px rgba(0, 191, 255, 0.5), 0 0 20px rgba(30, 144, 255, 0.5);
            }
            .announcements-list {
                display: flex;
                flex-direction: column;
                gap: 15px;
            }
            .announcement-card {
                background: rgba(255, 255, 255, 0.1);
                padding: 15px;
                border-radius: 12px;
                display: flex;
                flex-direction: column;
                backdrop-filter: blur(10px);
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.2);
                transition: all 0.3s;
            }
            .announcement-card:hover {
                transform: translateY(-3px) scale(1.02);
                box-shadow: 0 6px 20px rgba(255, 255, 255, 0.2);
            }
            .announcement-title {
                font-weight: bold;
                font-size: 1.2rem;
            }
            .announcement-content {
                margin-top: 5px;
                color: #ccc;
            }
            .back-btn {
                display: block;
                width: 200px;
                margin: 20px auto;
                padding: 10px 15px;
                border-radius: 10px;
                border: none;
                background: linear-gradient(45deg, #666666, #999999);
                color: white;
                cursor: pointer;
                transition: all 0.3s;
            }
            .back-btn:hover {
                transform: translateY(-3px);
                box-shadow: 0 4px 15px rgba(255, 255, 255, 0.2);
            }
            .creator-info {
                text-align: center;
                margin-top: 30px;
                padding: 10px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                animation: pulse 2s infinite;
            }

            .toolbar {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background: rgba(0, 0, 0, 0.9);
                backdrop-filter: blur(10px);
                border-top: 2px solid rgba(255, 255, 255, 0.1);
                display: flex;
                justify-content: space-around;
                padding: 15px 0;
                z-index: 1000;
            }
            .toolbar-item {
                display: flex;
                flex-direction: column;
                align-items: center;
                text-decoration: none;
                color: white;
                transition: all 0.3s;
                padding: 5px 10px;
                border-radius: 10px;
            }
            .toolbar-item:hover {
                transform: translateY(-8px);
                background: rgba(0, 238, 255, 0.2);
                box-shadow: 0 0 15px rgba(0, 238, 255, 0.5);
            }
            .toolbar-icon {
                font-size: 1.5rem;
                margin-bottom: 3px;
            }
            .active {
                background: rgba(0, 238, 255, 0.2);
                box-shadow: 0 0 15px rgba(0, 238, 255, 0.5);
            }

            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.05); }
                100% { transform: scale(1); }
            }
            @media (max-width: 768px) {
                .header h1 { font-size: 1.8rem; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>اعلانات</h1>
            </div>
            <div class="announcements-list">
                <div class="announcement-card">
                    <div class="announcement-title">اعلان تستی 1</div>
                    <div class="announcement-content">متن اعلان تستی برای پایه دهم رشته ریاضی.</div>
                </div>
                <div class="announcement-card">
                    <div class="announcement-title">اعلان تستی 2</div>
                    <div class="announcement-content">متن اعلان تستی دیگر.</div>
                </div>
            </div>
            <button class="back-btn" onclick="window.location.href='/admin-dashboard'">بازگشت</button>
            <div class="creator-info">
                سازنده: محمدرضا محمدی - دانش آموز دبیرستان جوادالائمه (رشته ریاضی)
            </div>
        </div>

        <div class="toolbar">
            <a href="/admin-dashboard" class="toolbar-item">
                <span class="toolbar-icon">🏠</span>
                <span>صفحه اصلی</span>
            </a>
            <a href="/announcements" class="toolbar-item active">
                <span class="toolbar-icon">📢</span>
                <span>اعلانات</span>
            </a>
            <a href="/profile" class="toolbar-item">
                <span class="toolbar-icon">👤</span>
                <span>پروفایل</span>
            </a>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route("/profile")
def profile():
    """صفحه پروفایل کاربر."""
    user, role = get_current_user()
    if not user:
        return redirect(url_for("index"))

    html = f'''
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>پروفایل</title>
        <link href="https://v1.fontapi.ir/css/Vazirmatn" rel="stylesheet">
        <style>
            @import url('https://v1.fontapi.ir/css/Vazirmatn');
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: 'Vazirmatn', sans-serif;
                background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
                color: white;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                padding-bottom: 60px;
                overflow-y: auto; /* اجازه اسکرول کامل */
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                flex: 1;
                overflow-y: auto;
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .header h1 {{
                font-size: 2.5rem;
                background: linear-gradient(to right, #00eeff, #0066ff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-shadow: 0 0 10px rgba(0, 238, 255, 0.5), 0 0 20px rgba(0, 102, 255, 0.5);
            }}
            .profile-container {{
                background: rgba(255, 255, 255, 0.1);
                padding: 30px;
                border-radius: 20px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                animation: zoomIn 0.5s ease-out;
            }}
            .profile-item {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 15px 10px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                transition: all 0.3s;
            }}
            .profile-item:hover {{
                background: rgba(255, 255, 255, 0.05);
                transform: translateX(5px);
            }}
            .profile-label {{
                font-weight: bold;
                color: #ccc;
            }}
            .profile-value {{
                flex-grow: 1;
                padding: 0 20px;
            }}
            .edit-btn {{
                background: rgba(255, 204, 0, 0.2);
                border: 1px solid #ffcc00;
                color: white;
                border-radius: 50%;
                width: 30px;
                height: 30px;
                cursor: pointer;
                transition: all 0.3s;
            }}
            .edit-btn:hover {{
                background: rgba(255, 204, 0, 0.4);
            }}
            .edit-field {{
                display: none;
                width: 100%;
                padding: 10px;
                border-radius: 10px;
                border: 1px solid #00eeff;
                background: rgba(0, 0, 0, 0.2);
                color: white;
                margin-top: 5px;
            }}
            .controls {{
                display: none;
                margin-top: 10px;
            }}
            .controls button {{
                padding: 8px 15px;
                margin: 0 5px;
                border-radius: 10px;
                border: none;
                cursor: pointer;
            }}
            .btn-confirm {{
                background: linear-gradient(45deg, #00ff99, #00cc66);
                color: white;
            }}
            .btn-cancel {{
                background: linear-gradient(45deg, #ff0066, #ff00cc);
                color: white;
            }}
            .logout-btn {{
                display: block;
                width: 100%;
                margin-top: 30px;
                padding: 15px;
                border-radius: 10px;
                border: none;
                background: linear-gradient(45deg, #ff0066, #ff00cc);
                color: white;
                font-size: 1.1rem;
                cursor: pointer;
                transition: all 0.3s;
            }}
            .logout-btn:hover {{
                transform: translateY(-3px);
                box-shadow: 0 6px 20px rgba(255, 0, 102, 0.4);
            }}
            .creator-info {{
                text-align: center;
                margin-top: 30px;
                padding: 10px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                animation: pulse 2s infinite;
            }}
            .toolbar {{
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background: rgba(0, 0, 0, 0.9);
                backdrop-filter: blur(10px);
                border-top: 2px solid rgba(255, 255, 255, 0.1);
                display: flex;
                justify-content: space-around;
                padding: 15px 0;
                z-index: 1000;
            }}
            .toolbar-item {{
                display: flex;
                flex-direction: column;
                align-items: center;
                text-decoration: none;
                color: white;
                transition: all 0.3s;
                padding: 5px 10px;
                border-radius: 10px;
            }}
            .toolbar-item:hover {{
                transform: translateY(-8px);
                background: rgba(0, 238, 255, 0.2);
                box-shadow: 0 0 15px rgba(0, 238, 255, 0.5);
            }}
            .toolbar-icon {{
                font-size: 1.5rem;
                margin-bottom: 3px;
            }}
            .active {{
                background: rgba(0, 238, 255, 0.2);
                box-shadow: 0 0 15px rgba(0, 238, 255, 0.5);
            }}
            @keyframes zoomIn {{
                from {{ opacity: 0; transform: scale3d(0.3, 0.3, 0.3); }}
                50% {{ opacity: 1; }}
            }}
            @keyframes pulse {{
                0% {{ transform: scale(1); }}
                50% {{ transform: scale(1.05); }}
                100% {{ transform: scale(1); }}
            }}
            @media (max-width: 768px) {{
                .header h1 {{ font-size: 1.8rem; }}
                .profile-item {{ flex-direction: column; align-items: flex-start; }}
                .profile-value, .edit-field {{ width: 100%; }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>پروفایل</h1>
            </div>
            <div class="profile-container">
                <div class="profile-item">
                    <span class="profile-label">نام:</span>
                    <span class="profile-value" id="name-view">{user['name']}</span>
                    <input type="text" class="edit-field" id="name-edit" value="{user['name']}">
                    <button class="edit-btn" onclick="toggleEdit('name')">✎</button>
                    <div class="controls" id="name-controls">
                        <button class="btn-confirm" onclick="saveEdit('name')">تأیید</button>
                        <button class="btn-cancel" onclick="cancelEdit('name')">انصراف</button>
                    </div>
                </div>
                <div class="profile-item">
                    <span class="profile-label">نام خانوادگی:</span>
                    <span class="profile-value" id="family-view">{user['lastname']}</span>
                    <input type="text" class="edit-field" id="family-edit" value="{user['lastname']}">
                    <button class="edit-btn" onclick="toggleEdit('family')">✎</button>
                    <div class="controls" id="family-controls">
                        <button class="btn-confirm" onclick="saveEdit('family')">تأیید</button>
                        <button class="btn-cancel" onclick="cancelEdit('family')">انصراف</button>
                    </div>
                </div>
                <div class="profile-item">
                    <span class="profile-label">مرتبه:</span>
                    <span class="profile-value" id="role-view">{user['role']}</span>
                    <select class="edit-field" id="role-edit">
                        <option value="مدیر" {"selected" if user['role'] == "مدیر" else ""}>مدیر</option>
                        <option value="ناظم" {"selected" if user['role'] == "ناظم" else ""}>ناظم</option>
                        <option value="معاون" {"selected" if user['role'] == "معاون" else ""}>معاون</option>
                        <option value="مشاور" {"selected" if user['role'] == "مشاور" else ""}>مشاور</option>
                    </select>
                    <button class="edit-btn" onclick="toggleEdit('role')">✎</button>
                    <div class="controls" id="role-controls">
                        <button class="btn-confirm" onclick="saveEdit('role')">تأیید</button>
                        <button class="btn-cancel" onclick="cancelEdit('role')">انصراف</button>
                    </div>
                </div>
                <div class="profile-item">
                    <span class="profile-label">رمز عبور:</span>
                    <span class="profile-value">********</span>
                </div>
                <button class="logout-btn" onclick="logout()">خروج از حساب</button>
            </div>
            <div class="creator-info">
                سازنده: محمدرضا محمدی - دانش آموز دبیرستان جوادالائمه (رشته ریاضی)
            </div>
        </div>

        <div class="toolbar">
            <a href="/admin-dashboard" class="toolbar-item">
                <span class="toolbar-icon">🏠</span>
                <span>صفحه اصلی</span>
            </a>
            <a href="/announcements" class="toolbar-item">
                <span class="toolbar-icon">📢</span>
                <span>اعلانات</span>
            </a>
            <a href="/profile" class="toolbar-item active">
                <span class="toolbar-icon">👤</span>
                <span>پروفایل</span>
            </a>
        </div>

        <script>
            function toggleEdit(field) {{
                const view = document.getElementById(field + "-view");
                const edit = document.getElementById(field + "-edit");
                const controls = document.getElementById(field + "-controls");

                if (edit.style.display === "none") {{
                    edit.style.display = "inline-block";
                    view.style.display = "none";
                    controls.style.display = "block";
                }} else {{
                    edit.style.display = "none";
                    view.style.display = "inline";
                    controls.style.display = "none";
                }}
            }}
            function saveEdit(field) {{
                let newValue;
                if (field === 'role') {{
                    newValue = document.getElementById(field + "-edit").value;
                }} else {{
                    newValue = document.getElementById(field + "-edit").value;
                }}
                document.getElementById(field + "-view").textContent = newValue;
                // Update session data
                fetch('/update-profile', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ [field]: newValue }})
                }});
                toggleEdit(field);
            }}
            function cancelEdit(field) {{
                if (field === 'role') {{
                    document.getElementById(field + "-edit").value = document.getElementById(field + "-view").textContent;
                }} else {{
                    document.getElementById(field + "-edit").value = document.getElementById(field + "-view").textContent;
                }}
                toggleEdit(field);
            }}
            function logout() {{
                if (confirm("آیا مطمئن هستید می‌خواهید از حساب خارج شوید؟")) {{
                    fetch('/logout', {{ method: 'POST' }})
                        .then(() => window.location.href = '/');
                }}
            }}
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route("/update-profile", methods=["POST"])
def update_profile():
    """به‌روزرسانی پروفایل کاربر."""
    user, role = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    field = list(data.keys())[0]
    new_value = data[field]

    if field in ["name", "lastname", "role"]:
        user[field] = new_value
        data_db = load_data()
        if role == "admin":
            data_db["admin"] = user
        elif role == "teacher":
            for i, t in enumerate(data_db.get("teachers", [])):
                if t.get("id") == user["id"]:
                    data_db["teachers"][i][field] = new_value
                    break
        save_data(data_db)
        session[f"{role}_id"] = user["id"]
        return jsonify({"success": True})
    return jsonify({"error": "Invalid field"}), 400

@app.route("/logout", methods=["POST"])
def logout():
    """خروج از حساب کاربری."""
    session.pop("admin_id", None)
    session.pop("teacher_id", None)
    return jsonify({"success": True})

@app.route("/manage-students")
def manage_students():
    """مدیریت دانش‌آموزان - انتخاب پایه."""
    user, role = get_current_user()
    if not user or role != "admin":
        return redirect(url_for("index"))

    html = '''
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>مدیریت دانش‌آموزان</title>
        <link href="https://v1.fontapi.ir/css/Vazirmatn" rel="stylesheet">
        <style>
            @import url('https://v1.fontapi.ir/css/Vazirmatn');
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: 'Vazirmatn', sans-serif;
                background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
                color: white;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                padding-bottom: 60px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                flex: 1;
                overflow-y: auto;
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
            }
            .header h1 {
                font-size: 2.5rem;
                background: linear-gradient(to right, #00ff99, #00cc66);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-shadow: 0 0 10px rgba(0, 255, 153, 0.5), 0 0 20px rgba(0, 204, 102, 0.5);
            }
            .grid-buttons {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }
            .btn {
                padding: 20px 15px;
                border-radius: 15px;
                border: none;
                color: white;
                font-size: 1.2rem;
                cursor: pointer;
                transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
                position: relative;
                overflow: hidden;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                text-align: center;
            }
            .btn::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(45deg, #9932cc, #4b0082);
                z-index: -1;
                opacity: 0.7;
                transition: opacity 0.4s;
            }
            .btn:hover::before {
                opacity: 1;
            }
            .btn:hover {
                transform: translateY(-8px) scale(1.02);
                box-shadow: 0 8px 30px rgba(255, 255, 255, 0.2);
            }
            .btn:active {
                transform: scale(0.98);
            }

            .creator-info {
                text-align: center;
                margin-top: 30px;
                padding: 10px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                animation: pulse 2s infinite;
            }

            .toolbar {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background: rgba(0, 0, 0, 0.9);
                backdrop-filter: blur(10px);
                border-top: 2px solid rgba(255, 255, 255, 0.1);
                display: flex;
                justify-content: space-around;
                padding: 15px 0;
                z-index: 1000;
            }
            .toolbar-item {
                display: flex;
                flex-direction: column;
                align-items: center;
                text-decoration: none;
                color: white;
                transition: all 0.3s;
                padding: 5px 10px;
                border-radius: 10px;
            }
            .toolbar-item:hover {
                transform: translateY(-8px);
                background: rgba(0, 238, 255, 0.2);
                box-shadow: 0 0 15px rgba(0, 238, 255, 0.5);
            }
            .toolbar-icon {
                font-size: 1.5rem;
                margin-bottom: 3px;
            }
            .active {
                background: rgba(0, 238, 255, 0.2);
                box-shadow: 0 0 15px rgba(0, 238, 255, 0.5);
            }

            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.05); }
                100% { transform: scale(1); }
            }
            @media (max-width: 768px) {
                .header h1 { font-size: 1.8rem; }
                .btn { padding: 15px 10px; font-size: 1rem; }
                .grid-buttons { grid-template-columns: 1fr; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>مدیریت دانش‌آموزان</h1>
            </div>
            <div class="grid-buttons">
                <button class="btn" onclick="window.location.href='/grade/10'">پایه دهم</button>
                <button class="btn" onclick="window.location.href='/grade/11'">پایه یازدهم</button>
                <button class="btn" onclick="window.location.href='/grade/12'">پایه دوازدهم</button>
            </div>
            <div class="creator-info">
                سازنده: محمدرضا محمدی - دانش آموز دبیرستان جوادالائمه (رشته ریاضی)
            </div>
        </div>

        <div class="toolbar">
            <a href="/admin-dashboard" class="toolbar-item">
                <span class="toolbar-icon">🏠</span>
                <span>صفحه اصلی</span>
            </a>
            <a href="/announcements" class="toolbar-item">
                <span class="toolbar-icon">📢</span>
                <span>اعلانات</span>
            </a>
            <a href="/profile" class="toolbar-item">
                <span class="toolbar-icon">👤</span>
                <span>پروفایل</span>
            </a>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route("/grade/<int:grade>")
def grade_page(grade):
    """صفحه انتخاب رشته برای یک پایه خاص."""
    user, role = get_current_user()
    if not user or role != "admin":
        return redirect(url_for("index"))

    html = f'''
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>پایه {grade}</title>
        <link href="https://v1.fontapi.ir/css/Vazirmatn" rel="stylesheet">
        <style>
            @import url('https://v1.fontapi.ir/css/Vazirmatn');
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: 'Vazirmatn', sans-serif;
                background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
                color: white;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                padding-bottom: 60px;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                flex: 1;
                overflow-y: auto;
            }}
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 30px;
            }}
            .header h1 {{
                font-size: 2.5rem;
                background: linear-gradient(to right, #ff4500, #ff8c00);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-shadow: 0 0 10px rgba(255, 69, 0, 0.5), 0 0 20px rgba(255, 140, 0, 0.5);
            }}
            .grid-buttons {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }}
            .btn {{
                padding: 20px 15px;
                border-radius: 15px;
                border: none;
                color: white;
                font-size: 1.2rem;
                cursor: pointer;
                transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
                position: relative;
                overflow: hidden;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                text-align: center;
            }}
            .btn::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(45deg, #ff4500, #ff8c00);
                z-index: -1;
                opacity: 0.7;
                transition: opacity 0.4s;
            }}
            .btn:hover::before {{
                opacity: 1;
            }}
            .btn:hover {{
                transform: translateY(-8px) scale(1.02);
                box-shadow: 0 8px 30px rgba(255, 255, 255, 0.2);
            }}
            .btn:active {{
                transform: scale(0.98);
            }}

            .creator-info {{
                text-align: center;
                margin-top: 30px;
                padding: 10px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                animation: pulse 2s infinite;
            }}

            .toolbar {{
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background: rgba(0, 0, 0, 0.9);
                backdrop-filter: blur(10px);
                border-top: 2px solid rgba(255, 255, 255, 0.1);
                display: flex;
                justify-content: space-around;
                padding: 15px 0;
                z-index: 1000;
            }}
            .toolbar-item {{
                display: flex;
                flex-direction: column;
                align-items: center;
                text-decoration: none;
                color: white;
                transition: all 0.3s;
                padding: 5px 10px;
                border-radius: 10px;
            }}
            .toolbar-item:hover {{
                transform: translateY(-8px);
                background: rgba(0, 238, 255, 0.2);
                box-shadow: 0 0 15px rgba(0, 238, 255, 0.5);
            }}
            .toolbar-icon {{
                font-size: 1.5rem;
                margin-bottom: 3px;
            }}
            .active {{
                background: rgba(0, 238, 255, 0.2);
                box-shadow: 0 0 15px rgba(0, 238, 255, 0.5);
            }}

            @keyframes pulse {{
                0% {{ transform: scale(1); }}
                50% {{ transform: scale(1.05); }}
                100% {{ transform: scale(1); }}
            }}
            @media (max-width: 768px) {{
                .header h1 {{ font-size: 1.8rem; }}
                .btn {{ padding: 15px 10px; font-size: 1rem; }}
                .grid-buttons {{ grid-template-columns: 1fr; }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>پایه {grade}</h1>
            </div>
            <div class="grid-buttons">
                <button class="btn" onclick="window.location.href='/grade/{grade}/math'">رشته ریاضی</button>
                <button class="btn" onclick="window.location.href='/grade/{grade}/science'">رشته تجربی</button>
                <button class="btn" onclick="window.location.href='/grade/{grade}/humanities'">رشته انسانی</button>
            </div>
            <div class="creator-info">
                سازنده: محمدرضا محمدی - دانش آموز دبیرستان جوادالائمه (رشته ریاضی)
            </div>
        </div>

        <div class="toolbar">
            <a href="/admin-dashboard" class="toolbar-item">
                <span class="toolbar-icon">🏠</span>
                <span>صفحه اصلی</span>
            </a>
            <a href="/announcements" class="toolbar-item">
                <span class="toolbar-icon">📢</span>
                <span>اعلانات</span>
            </a>
            <a href="/profile" class="toolbar-item">
                <span class="toolbar-icon">👤</span>
                <span>پروفایل</span>
            </a>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route("/grade/<int:grade>/<string:field>")
def field_page(grade, field):
    """صفحه لیست دانش‌آموزان یک رشته خاص."""
    user, role = get_current_user()
    if not user or role != "admin":
        return redirect(url_for("index"))

    data = load_data()
    students = data.get("students", {}).get(str(grade), {}).get(field, [])
    field_name = {"math": "ریاضی", "science": "تجربی", "humanities": "انسانی"}.get(field, "ناشناخته")

    html = f'''
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{field_name} پایه {grade}</title>
        <link href="https://v1.fontapi.ir/css/Vazirmatn" rel="stylesheet">
        <style>
            @import url('https://v1.fontapi.ir/css/Vazirmatn');
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: 'Vazirmatn', sans-serif;
                background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
                color: white;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                padding-bottom: 120px; /* فضای بیشتر برای دکمه + */
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                flex: 1;
                overflow-y: auto;
            }}
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 30px;
            }}
            .header h1 {{
                font-size: 2.5rem;
                background: linear-gradient(to right, #ff00cc, #00eeff, #ff00cc);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-shadow: 0 0 20px #00eeff;
                animation: fadeInDown 1s ease-out;
            }}
            .counter {{
                display: flex;
                align-items: center;
                padding: 10px 15px;
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 15px;
                font-size: 1.2rem;
            }}
            .counter i {{
                margin-right: 10px;
                font-size: 1.5rem;
            }}
            .students-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
                gap: 25px;
                margin: 20px 0;
            }}
            .student-card {{
                background: rgba(255, 255, 255, 0.1);
                padding: 20px;
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                min-height: 180px;
                display: flex;
                flex-direction: column;
                transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                animation: fadeIn 0.5s ease-out;
                cursor: pointer;
            }}
            .student-card:hover {{
                transform: translateY(-5px) scale(1.02);
                background: rgba(255, 255, 255, 0.15);
                box-shadow: 0 10px 25px rgba(0,0,0,0.3);
            }}
            .student-card-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }}
            .student-name {{
                font-size: 1.3rem;
                font-weight: bold;
                color: white;
            }}
            .student-card-actions {{
                display: flex;
                gap: 10px;
            }}
            .edit-card-btn, .delete-card-btn {{
                width: 40px;
                height: 40px;
                border-radius: 50%;
                border: none;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                transition: all 0.3s;
            }}
            .edit-card-btn {{
                background: linear-gradient(45deg, #ffcc00, #ff6600);
                color: white;
            }}
            .delete-card-btn {{
                background: linear-gradient(45deg, #ff0066, #ff00cc);
                color: white;
            }}
            .edit-card-btn:hover, .delete-card-btn:hover {{
                transform: scale(1.1);
            }}
            .student-info {{
                display: flex;
                flex-direction: column;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                padding-bottom: 10px;
                line-height: 1.8;
            }}
            .student-national-id {{
                color: #00eeff;
                font-size: 1rem;
            }}
            .add-student-btn {{
                position: fixed;
                bottom: 80px; /* بالاتر از تولبار */
                right: 30px;
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: linear-gradient(45deg, #00eeff, #0066ff);
                color: white;
                border: none;
                font-size: 2rem;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
                z-index: 100;
                transition: all 0.3s;
            }}
            .add-student-btn:hover {{
                transform: translateY(-5px) scale(1.1);
                box-shadow: 0 15px 35px rgba(0, 238, 255, 0.6);
            }}
            .add-student-btn:active {{
                transform: translateY(2px) scale(0.95);
            }}
            .creator-info {{
                text-align: center;
                margin-top: 30px;
                padding: 10px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                animation: pulse 2s infinite;
            }}

            .toolbar {{
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background: rgba(0, 0, 0, 0.9);
                backdrop-filter: blur(10px);
                border-top: 2px solid rgba(255, 255, 255, 0.1);
                display: flex;
                justify-content: space-around;
                padding: 15px 0;
                z-index: 1000;
            }}
            .toolbar-item {{
                display: flex;
                flex-direction: column;
                align-items: center;
                text-decoration: none;
                color: white;
                transition: all 0.3s;
                padding: 5px 10px;
                border-radius: 10px;
            }}
            .toolbar-item:hover {{
                transform: translateY(-8px);
                background: rgba(0, 238, 255, 0.2);
                box-shadow: 0 0 15px rgba(0, 238, 255, 0.5);
            }}
            .toolbar-icon {{
                font-size: 1.5rem;
                margin-bottom: 3px;
            }}
            .active {{
                background: rgba(0, 238, 255, 0.2);
                box-shadow: 0 0 15px rgba(0, 238, 255, 0.5);
            }}

            @keyframes fadeInDown {{
                from {{ opacity: 0; transform: translate3d(0, -20px, 0); }}
                to {{ opacity: 1; transform: translate3d(0, 0, 0); }}
            }}
            @keyframes fadeIn {{
                from {{ opacity: 0; }}
                to {{ opacity: 1; }}
            }}
            @keyframes pulse {{
                0% {{ transform: scale(1); }}
                50% {{ transform: scale(1.05); }}
                100% {{ transform: scale(1); }}
            }}
            @media (max-width: 768px) {{
                .header h1 {{ font-size: 1.8rem; }}
                .student-card {{
                    padding: 15px;
                }}
                .student-name {{
                    font-size: 1.1rem;
                }}
                .edit-card-btn, .delete-card-btn {{
                    width: 35px;
                    height: 35px;
                    font-size: 1rem;
                }}
                .add-student-btn {{
                    width: 50px;
                    height: 50px;
                    font-size: 1.5rem;
                    bottom: 100px;
                    right: 20px;
                }}
                .students-grid {{ grid-template-columns: 1fr; }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{field_name} پایه {grade}</h1>
                <div class="counter">
                    <i>👤</i>
                    <span id="studentCount">{len(students)}</span>
                </div>
            </div>
            <div class="students-grid" id="students-list">
                {''.join([
                    f'''
                    <div class="student-card" onclick="viewStudent({s['id']})">
                        <div class="student-card-header">
                            <div class="student-name">{s['name']} {s['family']}</div>
                            <div class="student-card-actions">
                                <button class="edit-card-btn" onclick="editStudent(event, {s['id']});">✎</button>
                                <button class="delete-card-btn" onclick="deleteStudent(event, {s['id']});">🗑️</button>
                            </div>
                        </div>
                        <div class="student-info">
                            <div class="student-national-id">{s['national_id']}</div>
                        </div>
                    </div>
                    '''
                    for s in students
                ])}
            </div>
            <div class="creator-info">
                سازنده: محمدرضا محمدی - دانش آموز دبیرستان جوادالائمه (رشته ریاضی)
            </div>
        </div>
        <button class="add-student-btn" onclick="openAddForm()">+</button>

        <div class="toolbar">
            <a href="/admin-dashboard" class="toolbar-item">
                <span class="toolbar-icon">🏠</span>
                <span>صفحه اصلی</span>
            </a>
            <a href="/announcements" class="toolbar-item">
                <span class="toolbar-icon">📢</span>
                <span>اعلانات</span>
            </a>
            <a href="/profile" class="toolbar-item">
                <span class="toolbar-icon">👤</span>
                <span>پروفایل</span>
            </a>
        </div>

        <div id="form-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.7); justify-content:center; align-items:center; z-index:2000;">
            <div style="background:rgba(0,0,0,0.9); padding:20px; border-radius:10px; width:90%; max-width:500px;">
                <h3 id="form-title">ثبت دانش‌آموز</h3>
                <input type="hidden" id="student-id">
                <div class="form-group">
                    <label>نام دانش آموز (اجباری)</label>
                    <input type="text" id="name" required>
                </div>
                <div class="form-group">
                    <label>نام خانوادگی دانش آموز (اجباری)</label>
                    <input type="text" id="family" required>
                </div>
                <div class="form-group">
                    <label>کد ملی دانش آموز (اجباری)</label>
                    <input type="text" id="national_id" required>
                </div>
                <div class="form-group">
                    <label>شماره دانش آموز (اختیاری)</label>
                    <input type="text" id="student_number">
                </div>
                <div class="form-group">
                    <label>شماره پدر (اختیاری)</label>
                    <input type="text" id="father_phone">
                </div>
                <div class="form-group">
                    <label>شماره مادر (اختیاری)</label>
                    <input type="text" id="mother_phone">
                </div>
                <div id="error-message" style="color: #ff4444; margin: 10px 0; display:none;"></div>
                <button onclick="submitStudent()">تایید</button>
                <button onclick="closeForm()">انصراف</button>
            </div>
        </div>

        <div id="deleteStudentModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); justify-content:center; align-items:center; z-index:2001;">
            <div style="background:linear-gradient(135deg, #1a1a2e, #16213e); padding:30px; border-radius:20px; width:90%; max-width:400px; box-shadow: 0 20px 50px rgba(0,0,0,0.5);">
                <h3>حذف دانش آموز</h3>
                <p>آیا مطمئن هستید می‌خواهید اطلاعات دانش آموز را پاک کنید؟</p>
                <div class="modal-buttons">
                    <button class="modal-btn-yes" onclick="confirmDelete()">بله</button>
                    <button class="modal-btn-no" onclick="closeDeleteModal()">خیر</button>
                </div>
            </div>
        </div>

        <script>
            let students = {json.dumps(students)};
            let currentGrade = {grade};
            let currentField = '{field}';
            let studentToDelete = null;

            function openAddForm() {{
                document.getElementById('form-title').textContent = 'ثبت دانش‌آموز';
                document.getElementById('student-id').value = '';
                document.getElementById('name').value = '';
                document.getElementById('family').value = '';
                document.getElementById('national_id').value = '';
                document.getElementById('student_number').value = '';
                document.getElementById('father_phone').value = '';
                document.getElementById('mother_phone').value = '';
                document.getElementById('error-message').style.display = 'none';
                document.getElementById('form-modal').style.display = 'flex';
            }}

            function editStudent(event, id) {{
                event.stopPropagation();
                const student = students.find(s => s.id === id);
                if (student) {{
                    document.getElementById('form-title').textContent = 'ویرایش دانش‌آموز';
                    document.getElementById('student-id').value = student.id;
                    document.getElementById('name').value = student.name;
                    document.getElementById('family').value = student.family;
                    document.getElementById('national_id').value = student.national_id;
                    document.getElementById('student_number').value = student.student_number || '';
                    document.getElementById('father_phone').value = student.father_phone || '';
                    document.getElementById('mother_phone').value = student.mother_phone || '';
                    document.getElementById('error-message').style.display = 'none';
                    document.getElementById('form-modal').style.display = 'flex';
                }}
            }}

            function closeForm() {{
                document.getElementById('form-modal').style.display = 'none';
            }}

            function submitStudent() {{
                const id = document.getElementById('student-id').value;
                const name = document.getElementById('name').value;
                const family = document.getElementById('family').value;
                const national_id = document.getElementById('national_id').value;
                const student_number = document.getElementById('student_number').value;
                const father_phone = document.getElementById('father_phone').value;
                const mother_phone = document.getElementById('mother_phone').value;

                if (!name || !family || !national_id) {{
                    document.getElementById('error-message').textContent = 'لطفاً فیلدهای اجباری را پر کنید.';
                    document.getElementById('error-message').style.display = 'block';
                    return;
                }}

                const payload = {{ id, name, family, national_id, student_number, father_phone, mother_phone, grade: currentGrade, field: currentField }};
                const method = id ? 'PUT' : 'POST';
                const url = id ? '/api/student/' + id : '/api/student';

                fetch(url, {{
                    method: method,
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(payload)
                }})
                .then(response => response.json())
                .then(data => {{
                    if (data.error) {{
                        document.getElementById('error-message').textContent = data.error;
                        document.getElementById('error-message').style.display = 'block';
                    }} else {{
                        location.reload();
                    }}
                }});
            }}

            function deleteStudent(event, id) {{
                event.stopPropagation();
                if (confirm('آیا مطمئن هستید می‌خواهید اطلاعات دانش آموز را پاک کنید؟')) {{
                    fetch('/api/student/' + id, {{ method: 'DELETE' }})
                        .then(() => location.reload());
                }}
            }}

            function viewStudent(id) {{
                window.location.href = '/student/' + id;
            }}
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route("/student/<int:student_id>")
def view_student(student_id):
    """صفحه جزئیات یک دانش‌آموز."""
    user, role = get_current_user()
    if not user or role != "admin":
        return redirect(url_for("index"))

    data = load_data()
    student = None
    for grade_data in data.get("students", {}).values():
        for field_data in grade_
            for s in field_data:
                if s.get("id") == student_id:
                    student = s
                    break
            if student:
                break
        if student:
            break

    if not student:
        return "دانش آموز یافت نشد", 404

    html = f'''
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>جزئیات دانش آموز</title>
        <link href="https://v1.fontapi.ir/css/Vazirmatn" rel="stylesheet">
        <style>
            @import url('https://v1.fontapi.ir/css/Vazirmatn');
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: 'Vazirmatn', sans-serif;
                background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
                color: white;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                padding-bottom: 60px;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                flex: 1;
                overflow-y: auto;
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .header h1 {{
                font-size: 2.5rem;
                background: linear-gradient(to right, #00ff99, #00cc66);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-shadow: 0 0 10px rgba(0, 255, 153, 0.5), 0 0 20px rgba(0, 204, 102, 0.5);
            }}
            .student-details {{
                background: rgba(255, 255, 255, 0.1);
                padding: 30px;
                border-radius: 20px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                animation: zoomIn 0.5s ease-out;
            }}
            .detail-item {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 15px 10px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }}
            .detail-label {{
                font-weight: bold;
                color: #ccc;
                width: 150px;
            }}
            .detail-value {{
                flex-grow: 1;
                padding: 0 20px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                padding: 5px 10px;
                border-radius: 5px;
            }}
            .back-btn {{
                display: block;
                width: 200px;
                margin: 20px auto;
                padding: 10px 15px;
                border-radius: 10px;
                border: none;
                background: linear-gradient(45deg, #666666, #999999);
                color: white;
                cursor: pointer;
                transition: all 0.3s;
            }}
            .back-btn:hover {{
                transform: translateY(-3px);
                box-shadow: 0 4px 15px rgba(255, 255, 255, 0.2);
            }}
            .creator-info {{
                text-align: center;
                margin-top: 30px;
                padding: 10px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                animation: pulse 2s infinite;
            }}

            .toolbar {{
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background: rgba(0, 0, 0, 0.9);
                backdrop-filter: blur(10px);
                border-top: 2px solid rgba(255, 255, 255, 0.1);
                display: flex;
                justify-content: space-around;
                padding: 15px 0;
                z-index: 1000;
            }}
            .toolbar-item {{
                display: flex;
                flex-direction: column;
                align-items: center;
                text-decoration: none;
                color: white;
                transition: all 0.3s;
                padding: 5px 10px;
                border-radius: 10px;
            }}
            .toolbar-item:hover {{
                transform: translateY(-8px);
                background: rgba(0, 238, 255, 0.2);
                box-shadow: 0 0 15px rgba(0, 238, 255, 0.5);
            }}
            .toolbar-icon {{
                font-size: 1.5rem;
                margin-bottom: 3px;
            }}
            .active {{
                background: rgba(0, 238, 255, 0.2);
                box-shadow: 0 0 15px rgba(0, 238, 255, 0.5);
            }}

            @keyframes zoomIn {{
                from {{ opacity: 0; transform: scale3d(0.3, 0.3, 0.3); }}
                50% {{ opacity: 1; }}
            }}
            @keyframes pulse {{
                0% {{ transform: scale(1); }}
                50% {{ transform: scale(1.05); }}
                100% {{ transform: scale(1); }}
            }}
            @media (max-width: 768px) {{
                .header h1 {{ font-size: 1.8rem; }}
                .detail-item {{ flex-direction: column; align-items: flex-start; }}
                .detail-value, .detail-label {{ width: 100%; }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>جزئیات دانش آموز</h1>
            </div>
            <div class="student-details">
                <div class="detail-item">
                    <span class="detail-label">نام دانش آموز:</span>
                    <span class="detail-value">{student['name']}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">نام خانوادگی دانش آموز:</span>
                    <span class="detail-value">{student['family']}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">کد ملی دانش آموز:</span>
                    <span class="detail-value">{student['national_id']}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">شماره دانش آموز:</span>
                    <span class="detail-value">{student.get('student_number', 'ثبت نشده')}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">شماره پدر:</span>
                    <span class="detail-value">{student.get('father_phone', 'ثبت نشده')}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">شماره مادر:</span>
                    <span class="detail-value">{student.get('mother_phone', 'ثبت نشده')}</span>
                </div>
            </div>
            <button class="back-btn" onclick="window.location.href='/grade/{student['grade']}/{student['field']}'">بازگشت</button>
            <div class="creator-info">
                سازنده: محمدرضا محمدی - دانش آموز دبیرستان جوادالائمه (رشته ریاضی)
            </div>
        </div>

        <div class="toolbar">
            <a href="/admin-dashboard" class="toolbar-item">
                <span class="toolbar-icon">🏠</span>
                <span>صفحه اصلی</span>
            </a>
            <a href="/announcements" class="toolbar-item">
                <span class="toolbar-icon">📢</span>
                <span>اعلانات</span>
            </a>
            <a href="/profile" class="toolbar-item">
                <span class="toolbar-icon">👤</span>
                <span>پروفایل</span>
            </a>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route("/teacher-dashboard")
def teacher_dashboard():
    """درگاه معلمان."""
    user, role = get_current_user()
    if not user or role != "teacher":
        return redirect(url_for("index"))

    html = '''
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>درگاه معلمان</title>
        <link href="https://v1.fontapi.ir/css/Vazirmatn" rel="stylesheet">
        <style>
            @import url('https://v1.fontapi.ir/css/Vazirmatn');
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: 'Vazirmatn', sans-serif;
                background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
                color: white;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                padding-bottom: 60px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                flex: 1;
                overflow-y: auto;
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
                animation: fadeInDown 1s ease-out;
            }
            .header h1 {
                font-size: 2.5rem;
                background: linear-gradient(to right, #00eeff, #0066ff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-shadow: 0 0 10px rgba(0, 238, 255, 0.5), 0 0 20px rgba(0, 102, 255, 0.5);
            }
            .grid-buttons {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }
            .btn {
                padding: 20px 15px;
                border-radius: 15px;
                border: none;
                color: white;
                font-size: 1.2rem;
                cursor: pointer;
                transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
                position: relative;
                overflow: hidden;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                text-align: center;
            }
            .btn::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(45deg, #32cd32, #228b22);
                z-index: -1;
                opacity: 0.7;
                transition: opacity 0.4s;
            }
            .btn:hover::before {
                opacity: 1;
            }
            .btn:hover {
                transform: translateY(-8px) scale(1.02);
                box-shadow: 0 8px 30px rgba(255, 255, 255, 0.2);
            }
            .btn:active {
                transform: scale(0.98);
            }
            .btn-announcements::before { background: linear-gradient(45deg, #00bfff, #1e90ff); }
            .btn-attendance::before { background: linear-gradient(45deg, #ff6b6b, #ff8e53); }

            .creator-info {
                text-align: center;
                margin-top: 30px;
                padding: 10px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                animation: pulse 2s infinite;
            }

            .toolbar {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background: rgba(0, 0, 0, 0.9);
                backdrop-filter: blur(10px);
                border-top: 2px solid rgba(255, 255, 255, 0.1);
                display: flex;
                justify-content: space-around;
                padding: 15px 0;
                z-index: 1000;
            }
            .toolbar-item {
                display: flex;
                flex-direction: column;
                align-items: center;
                text-decoration: none;
                color: white;
                transition: all 0.3s;
                padding: 5px 10px;
                border-radius: 10px;
            }
            .toolbar-item:hover {
                transform: translateY(-8px);
                background: rgba(0, 238, 255, 0.2);
                box-shadow: 0 0 15px rgba(0, 238, 255, 0.5);
            }
            .toolbar-icon {
                font-size: 1.5rem;
                margin-bottom: 3px;
            }
            .active {
                background: rgba(0, 238, 255, 0.2);
                box-shadow: 0 0 15px rgba(0, 238, 255, 0.5);
            }

            @keyframes fadeInDown {
                from { opacity: 0; transform: translate3d(0, -20px, 0); }
                to { opacity: 1; transform: translate3d(0, 0, 0); }
            }
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.05); }
                100% { transform: scale(1); }
            }
            @media (max-width: 768px) {
                .header h1 { font-size: 1.8rem; }
                .btn { padding: 15px 10px; font-size: 1rem; }
                .grid-buttons { grid-template-columns: 1fr; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>درگاه معلمان</h1>
            </div>
            <div class="grid-buttons">
                <button class="btn btn-announcements" onclick="window.location.href='/announcements'">اعلانات</button>
                <button class="btn btn-attendance">ثبت حضور و غیاب</button>
            </div>
            <div class="creator-info">
                سازنده: محمدرضا محمدی - دانش آموز دبیرستان جوادالائمه (رشته ریاضی)
            </div>
        </div>

        <div class="toolbar">
            <a href="/teacher-dashboard" class="toolbar-item active">
                <span class="toolbar-icon">🏠</span>
                <span>صفحه اصلی</span>
            </a>
            <a href="/announcements" class="toolbar-item">
                <span class="toolbar-icon">📢</span>
                <span>اعلانات</span>
            </a>
            <a href="/profile" class="toolbar-item">
                <span class="toolbar-icon">👤</span>
                <span>پروفایل</span>
            </a>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route("/api/student", methods=["POST"])
def api_add_student():
    """API برای افزودن دانش‌آموز جدید."""
    data = load_data()
    new_student = request.json
    grade = new_student["grade"]
    field = new_student["field"]
    national_id = new_student["national_id"]

    students_list = data.get("students", {}).get(str(grade), {}).get(field, [])
    for s in students_list:
        if s["national_id"] == national_id:
            return jsonify({"error": "این دانش آموز با این کد ملی وجود دارد"}), 400

    new_id = max([s.get("id", 0) for g in data.get("students", {}).values() for f in g.values() for s in f], default=0) + 1
    new_student["id"] = new_id
    data.setdefault("students", {}).setdefault(str(grade), {}).setdefault(field, []).append(new_student)
    save_data(data)
    return jsonify({"success": True})

@app.route("/api/student/<int:student_id>", methods=["PUT", "DELETE"])
def api_edit_delete_student(student_id):
    """API برای ویرایش یا حذف دانش‌آموز."""
    data = load_data()
    student = None
    target_list = None
    for grade_data in data.get("students", {}).values():
        for field_data in grade_data.values():
            for i, s in enumerate(field_data):
                if s.get("id") == student_id:
                    student = s
                    target_list = field_data
                    target_index = i
                    break
            if student:
                break
        if student:
            break

    if not student:
        return "دانش آموز یافت نشد", 404

    if request.method == "PUT":
        updated_data = request.json
        if updated_data["national_id"] != student["national_id"]:
            # Check for duplicate national_id in same grade/field
            for s in target_list:
                if s["id"] != student_id and s["national_id"] == updated_data["national_id"]:
                    return jsonify({"error": "کد ملی وارد شده قبلاً ثبت شده است."}), 400
        target_list[target_index].update(updated_data)
        save_data(data)
        return jsonify({"success": True})

    elif request.method == "DELETE":
        target_list.pop(target_index)
        save_data(data)
        return jsonify({"success": True})

# --- RUN APP ---
if __name__ == "__main__":
    # خواندن پورت از متغیر محیطی PORT
    port = int(os.environ.get("PORT", 10000))  # اگر PORT وجود نداشت، از 10000 استفاده کن
    # اجرای سرور Flask با گوش دادن به 0.0.0.0
    app.run(host="0.0.0.0", port=port, debug=False)