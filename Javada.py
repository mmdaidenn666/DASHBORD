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
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"students": {}, "announcements": [], "admin": None, "teachers": []}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# تابع برای گرفتن اطلاعات کاربر فعلی (admin یا teacher)
def get_current_user():
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
            .welcome-text {
                text-align: center;
                color: #e0e0ff;
                margin-bottom: 20px;
                animation: fadeInUp 1s ease-out;
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

            /* انیمیشن‌ها */
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            @keyframes fadeInDown {
                from {
                    opacity: 0;
                    transform: translate3d(0, -20px, 0);
                }
                to {
                    opacity: 1;
                    transform: translate3d(0, 0, 0);
                }
            }
            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translate3d(0, 20px, 0);
                }
                to {
                    opacity: 1;
                    transform: translate3d(0, 0, 0);
                }
            }
            @keyframes slideInUp {
                from {
                    transform: translate3d(0, 100%, 0);
                    visibility: visible;
                }
                to {
                    transform: translate3d(0, 0, 0);
                }
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
            @keyframes shake {
                from, to {
                    transform: translate3d(0, 0, 0);
                }
                10%, 30%, 50%, 70%, 90% {
                    transform: translate3d(-10px, 0, 0);
                }
                20%, 40%, 60%, 80% {
                    transform: translate3d(10px, 0, 0);
                }
            }
            @keyframes pulse {
                0% {
                    transform: scale(1);
                }
                50% {
                    transform: scale(1.05);
                }
                100% {
                    transform: scale(1);
                }
            }
            @keyframes zoomIn {
                from {
                    opacity: 0;
                    transform: scale3d(0.3, 0.3, 0.3);
                }
                50% {
                    opacity: 1;
                }
            }

            /* ریسپانسیو */
            @media (max-width: 768px) {
                .header h1 {
                    font-size: 1.8rem;
                }
                .btn {
                    padding: 15px 10px;
                    font-size: 1rem;
                }
                .buttons-container {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>به سایت رسمی دبیرستان پسرانه جوادالائمه خوش آمدید</h1>
            </div>
            <p class="welcome-text">سیستم مدیریت یکپارچه دانش‌آموزان، اساتید و گزارشات</p>
            <div class="buttons-container">
                <button class="btn btn-admin" onclick="window.location.href='/admin-login'">ورود مدیران</button>
                <button class="btn btn-teacher" onclick="window.location.href='/teacher-login'">ورود معلمان</button>
                <button class="btn btn-parent">ورود والدین</button>
                <button class="btn btn-student">ورود دانش‌آموزان</button>
            </div>
            <div class="creator-info">
                طراحی و توسعه توسط یک دانش‌آموز
            </div>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
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

        # ذخیره اطلاعات در دیتابیس
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

        # ذخیره اطلاعات در دیتابیس
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
        # بررسی تکراری نبودن
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
        @media (max-width: 768px) {
            .form-container {
                padding: 20px;
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
                padding-bottom: 60px; /* فضایی برای تولبار */
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
            .btn-announcements::before { background: linear-gradient(45deg, #00bfff, #1e90ff); }
            .btn-students::before { background: linear-gradient(45deg, #32cd32, #228b22); }
            .btn-reports::before { background: linear-gradient(45deg, #ff6b6b, #ff8e53); }

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
            .badge {
                background: #ff0000;
                color: white;
                border-radius: 50%;
                padding: 2px 6px;
                font-size: 0.7rem;
                position: absolute;
                top: -5px;
                right: -5px;
            }

            /* انیمیشن‌ها و ریسپانسیو از قبل */
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
                <button class="btn btn-announcements" onclick="window.location.href='/announcements'">اعلانات</button>
                <button class="btn btn-students" onclick="window.location.href='/manage-students'">مدیریت دانش‌آموزان</button>
                <button class="btn btn-reports" onclick="window.location.href='/reports'">گزارشات</button>
            </div>
            <div class="creator-info">
                خوش آمدید، {{ user.name }} {{ user.lastname }} ({{ user.role }})
            </div>
        </div>

        <div class="toolbar">
            <a href="/admin-dashboard" class="toolbar-item active">
                <span class="toolbar-icon">🏠</span>
                <span>خانه</span>
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

        <script>
            // مخفی کردن تولبار در برخی صفحات (این جا فقط نمایش می‌دهیم که چگونه کار می‌کند)
            // در صفحات دیگر مانند /add-student باید با جاوا اسکریپت یا تغییر قالب انجام شود
        </script>
    </body>
    </html>
    '''
    return render_template_string(html, user=user)

@app.route("/teacher-dashboard")
def teacher_dashboard():
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
                <button class="btn btn-attendance" onclick="window.location.href='/attendance'">ثبت حضور و غیاب</button>
            </div>
            <div class="creator-info">
                خوش آمدید، {{ user.name }} {{ user.lastname }} ({{ user.subject }})
            </div>
        </div>

        <div class="toolbar">
            <a href="/teacher-dashboard" class="toolbar-item active">
                <span class="toolbar-icon">🏠</span>
                <span>خانه</span>
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
    return render_template_string(html, user=user)

# سایر route ها (profile, announcements, manage-students, attendance, reports) باید به همین شکل گرافیکی و با ویژگی‌های تحلیل شده پیاده شوند.
# برای کوتاهی، اینجا فقط نمونه‌های اصلی را نشان دادم.

# --- RUN APP ---
if __name__ == "__main__":
    # خواندن پورت از متغیر محیطی PORT
    port = int(os.environ.get("PORT", 10000))  # اگر PORT وجود نداشت، از 10000 استفاده کن
    # اجرای سرور Flask با گوش دادن به 0.0.0.0
    app.run(host="0.0.0.0", port=port, debug=False)