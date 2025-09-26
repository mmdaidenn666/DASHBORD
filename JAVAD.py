from flask import Flask, render_template_string, request, session, redirect, url_for, jsonify
import os

app = Flask(__name__)
app.secret_key = 'neon_dabirestan_2025_secure_key'

ADMIN_PASSWORD = "dabirestan012345"

# صفحه اصلی
@app.route('/')
def home():
    # اگر کاربر لاگین کرده، مستقیماً به درگاه هدایت شود
    if session.get('admin'):
        return redirect(url_for('admin_dashboard'))
    return render_template_string('''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>دبیرستان جوادالائمه</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazir:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            background: #0D0D0D;
            color: white;
            font-family: 'Vazir', sans-serif;
            padding: 20px;
            min-height: 100vh;
            overflow-x: hidden;
        }
        .welcome {
            text-align: center;
            font-size: clamp(20px, 6vw, 28px);
            margin: 20px 0 30px;
            color: #00FF9C;
            text-shadow: 0 0 8px #00FF9C, 0 0 16px #00C6FF;
            animation: glow 2s infinite alternate;
        }
        @keyframes glow {
            from { text-shadow: 0 0 8px #00FF9C, 0 0 16px #00C6FF; }
            to { text-shadow: 0 0 12px #00FF9C, 0 0 24px #00C6FF, 0 0 32px #FF3CAC; }
        }
        .button-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(clamp(160px, 80vw, 240px), 1fr));
            gap: 20px;
            max-width: 1000px;
            margin: 0 auto;
        }
        .btn-card {
            display: block;
            padding: 24px 16px;
            border-radius: 18px;
            text-decoration: none;
            text-align: center;
            position: relative;
            overflow: hidden;
            border: 2px solid transparent;
            font-size: clamp(16px, 4vw, 18px);
        }
        .btn-card::before {
            content: '';
            position: absolute;
            top: -2px; left: -2px;
            right: -2px; bottom: -2px;
            background: linear-gradient(45deg, #00C6FF, #FF3CAC, #00FF9C, #9D4EDD, #FF9E00);
            z-index: -1;
            border-radius: 20px;
            opacity: 0;
            transition: opacity 0.4s ease;
        }
        .btn-card:hover::before, .btn-card:focus::before {
            opacity: 1;
        }
        .btn-card h3 {
            font-size: clamp(18px, 5vw, 22px);
            margin-bottom: 8px;
            color: white;
        }
        .btn-card p {
            font-size: clamp(13px, 3.5vw, 15px);
            opacity: 0.9;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            color: #6B7280;
            font-size: clamp(12px, 3.2vw, 14px);
            white-space: nowrap;
            overflow: hidden;
            width: 100%;
            padding: 0 10px;
            box-sizing: border-box;
        }
        @keyframes typing {
            from { width: 0; }
            to { width: 100%; }
        }
        .typing-text {
            display: inline-block;
            overflow: hidden;
            white-space: nowrap;
            border-right: 2px solid #00FF9C;
            animation: typing 4s steps(50) 1s forwards, blink 0.7s step-end infinite;
        }
        @keyframes blink {
            50% { border-color: transparent; }
        }
    </style>
</head>
<body>
    <h1 class="welcome">به سایت رسمی دبیرستان پسرانه جوادالائمه خوش آمدید</h1>
    <div class="button-grid">
        <a href="/login/admin" class="btn-card"><h3>ورود مدیران</h3><p>این بخش فقط برای مدیران است</p></a>
        <a href="/login/teacher" class="btn-card"><h3>ورود معلمان</h3><p>این بخش فقط برای معلمان است</p></a>
        <a href="/login/parent" class="btn-card"><h3>ورود والدین</h3><p>این بخش فقط برای والدین است</p></a>
        <a href="/login/student" class="btn-card"><h3>ورود دانش آموزان</h3><p>این بخش فقط برای دانش آموزان است</p></a>
    </div>
    <div class="footer">
        <span class="typing-text">سازنده: محمدرضا محمدی دانش آموز دبیرستان جوادالائمه (رشته ریاضی)</span>
    </div>
</body>
</html>
    ''')

# ورود مدیران
@app.route('/login/admin', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin'):
        return redirect(url_for('admin_dashboard'))
    error = None
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        family = request.form.get('family', '').strip()
        role = request.form.get('role', '')
        password = request.form.get('password', '')
        if not all([name, family, role, password]):
            error = "لطفاً تمامی فیلدها را پر کنید."
        elif password != ADMIN_PASSWORD:
            error = "رمز عبور اشتباه است."
        else:
            session['admin'] = {'name': name, 'family': family, 'role': role}
            return redirect(url_for('admin_dashboard'))
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>ورود مدیران</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazir:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        body {
            background: #0D0D0D;
            color: white;
            font-family: 'Vazir', sans-serif;
            padding: 15px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            overflow: hidden;
        }
        .form-container {
            background: #1A1A1A;
            padding: 25px;
            border-radius: 20px;
            width: 100%;
            max-width: 500px;
            box-shadow: 0 0 20px rgba(0, 200, 255, 0.3);
            border: 1px solid #333;
        }
        h2 {
            text-align: center;
            margin-bottom: 24px;
            color: #00C6FF;
            text-shadow: 0 0 10px #00C6FF;
            font-size: 24px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #00FF9C;
            font-size: 16px;
        }
        input, select {
            width: 100%;
            padding: 14px;
            background: #222;
            border: 1px solid #444;
            border-radius: 12px;
            color: white;
            font-size: 16px;
            direction: rtl;
        }
        .btn-primary {
            width: 100%;
            padding: 14px;
            background: linear-gradient(90deg, #00C6FF, #00FF9C);
            color: #0D0D0D;
            border: none;
            border-radius: 14px;
            font-weight: bold;
            font-size: 18px;
            cursor: pointer;
            box-shadow: 0 0 12px #00C6FF, 0 0 24px #00FF9C;
            transition: all 0.3s ease;
        }
        .btn-primary:hover {
            background: linear-gradient(90deg, #FF3CAC, #00FF9C);
            box-shadow: 0 0 20px #FF3CAC, 0 0 40px #00FF9C;
            transform: translateY(-3px);
        }
        @keyframes click-bounce {
            0% { transform: scale(1); }
            50% { transform: scale(0.95); }
            100% { transform: scale(1); }
        }
        .btn-primary:active {
            animation: click-bounce 0.2s ease;
        }
        .alert {
            padding: 12px;
            background: #331111;
            border: 1px solid #EF4444;
            border-radius: 8px;
            color: #FF6B6B;
            text-align: center;
            margin-bottom: 20px;
            font-size: 16px;
        }
        .back-link {
            display: block;
            text-align: center;
            margin-top: 20px;
            color: #00C6FF;
            text-decoration: none;
            font-size: 16px;
        }
    </style>
</head>
<body>
    <div class="form-container">
        <h2>ورود مدیران</h2>
        <form method="POST">
            {% if error %}
            <div class="alert">{{ error }}</div>
            {% endif %}
            <div class="form-group">
                <label>نام</label>
                <input type="text" name="name" value="{{ request.form.name or '' }}" required>
            </div>
            <div class="form-group">
                <label>نام خانوادگی</label>
                <input type="text" name="family" value="{{ request.form.family or '' }}" required>
            </div>
            <div class="form-group">
                <label>مرتبه</label>
                <select name="role" required>
                    <option value="">انتخاب کنید...</option>
                    <option value="مدیر" {{ 'selected' if request.form.role == 'مدیر' }}>مدیر</option>
                    <option value="ناظم" {{ 'selected' if request.form.role == 'ناظم'}}>ناظم</option>
                    <option value="معاون" {{ 'selected' if request.form.role == 'معاون'}}>معاون</option>
                    <option value="مشاور" {{ 'selected' if request.form.role == 'مشاور'}}>مشاور</option>
                </select>
            </div>
            <div class="form-group">
                <label>رمز عبور</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit" class="btn-primary">ورود</button>
        </form>
        <a href="/" class="back-link">بازگشت به صفحه اصلی</a>
    </div>
</body>
</html>
    ''', error=error)

# درگاه مدیران
@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    return render_template_string('''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>درگاه مدیران</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazir:wght@400;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            background: #0D0D0D;
            color: white;
            font-family: 'Vazir', sans-serif;
            overflow-x: hidden;
        }
        .toolbar {
            display: flex;
            justify-content: flex-end;
            padding: 12px 20px;
            background: #151515;
            border-bottom: 1px solid #333;
        }
        .menu-toggle {
            background: #222;
            color: #FF3CAC;
            border: 1px solid #FF3CAC;
            border-radius: 50%;
            width: 44px;
            height: 44px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 0 8px rgba(255, 60, 172, 0.5);
            font-size: 20px;
        }
        .menu-toggle:hover {
            background: #FF3CAC;
            color: #0D0D0D;
            box-shadow: 0 0 15px #FF3CAC, 0 0 25px #FF9E00;
        }
        .sidebar {
            position: fixed;
            top: 0;
            right: 0;
            height: 100%;
            width: clamp(240px, 80vw, 300px);
            background: #1A1A1A;
            border-left: 1px solid #444;
            transform: translateX(100%);
            transition: transform 0.4s cubic-bezier(0.68, -0.55, 0.27, 1.55);
            z-index: 1000;
            padding-top: 70px;
        }
        .sidebar.active {
            transform: translateX(0);
        }
        .close-btn {
            position: absolute;
            top: 20px;
            left: 20px;
            background: #EF4444;
            color: white;
            width: 34px;
            height: 34px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-weight: bold;
            font-size: 20px;
            box-shadow: 0 0 10px #EF4444;
        }
        .sidebar-btn {
            display: block;
            width: calc(100% - 40px);
            margin: 18px 20px;
            padding: 16px;
            text-align: center;
            background: linear-gradient(90deg, #00C6FF, #00FF9C);
            color: #0D0D0D;
            border: none;
            border-radius: 14px;
            text-decoration: none;
            font-weight: bold;
            font-size: 18px;
            box-shadow: 0 0 10px #00C6FF, 0 0 20px #00FF9C;
            transition: all 0.3s;
        }
        .sidebar-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 0 15px #FF3CAC, 0 0 30px #00FF9C;
        }
        .dashboard {
            padding: 20px;
        }
        .dashboard h2 {
            color: #00FF9C;
            margin: 20px 0 25px;
            text-shadow: 0 0 10px #00FF9C;
            font-size: 26px;
            text-align: center;
        }
        .cards-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(clamp(150px, 45vw, 220px), 1fr));
            gap: 20px;
            padding: 0 10px;
        }
        .card {
            background: #1A1A1A;
            padding: 22px 16px;
            border-radius: 18px;
            text-align: center;
            color: #00C6FF;
            border: 1px solid #333;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 18px;
            box-shadow: 0 0 8px rgba(0, 198, 255, 0.3);
        }
        .card:hover {
            transform: translateY(-6px);
            box-shadow: 0 0 16px #00C6FF, 0 0 24px #00FF9C;
            background: #222;
        }
    </style>
</head>
<body>
    <header class="toolbar">
        <button class="menu-toggle" id="menuToggle">
            <i class="fas fa-bars"></i>
        </button>
    </header>

    <div class="sidebar" id="sidebar">
        <div class="close-btn" id="closeSidebar">&times;</div>
        <a href="/admin/dashboard" class="sidebar-btn">صفحه اصلی</a>
        <a href="/admin/profile" class="sidebar-btn">پروفایل</a>
        <a href="#" class="sidebar-btn">اعلانات</a>
    </div>

    <div class="dashboard">
        <h2>درگاه مدیران</h2>
        <div class="cards-grid">
            {% for item in items %}
            <div class="card">{{ item }}</div>
            {% endfor %}
        </div>
    </div>

    <script>
        // جلوگیری از بازگشت با دکمه مرورگر
        history.pushState(null, null, location.href);
        window.addEventListener('popstate', function () {
            history.pushState(null, null, location.href);
        });

        document.getElementById('menuToggle').addEventListener('click', () => {
            document.getElementById('sidebar').classList.add('active');
        });
        document.getElementById('closeSidebar').addEventListener('click', () => {
            document.getElementById('sidebar').classList.remove('active');
        });
    </script>
</body>
</html>
    ''', items=[
        "مدیریت دانش آموزان",
        "مدیریت معلمان",
        "مدیریت گزارشات والدین",
        "مدیریت گزارشات معلمان",
        "مدیریت گزارشات دانش آموزان",
        "مدیریت بخش آزمایشگاه",
        "مدیریت نمرات",
        "مدیریت کارنامه"
    ])

# صفحه پروفایل
@app.route('/admin/profile', methods=['GET', 'POST'])
def admin_profile():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        data = request.get_json()
        field = data.get('field')
        value = data.get('value')
        if field in ['name', 'family', 'role'] and value.strip():
            session['admin'][field] = value.strip()
            return jsonify(success=True)
        return jsonify(success=False), 400

    user = session['admin']
    return render_template_string('''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>پروفایل</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazir:wght@400;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body {
            background: #0D0D0D;
            color: white;
            font-family: 'Vazir', sans-serif;
            padding: 15px;
            overflow-x: hidden;
        }
        .toolbar {
            display: flex;
            justify-content: flex-end;
            padding: 12px 20px;
            background: #151515;
            border-bottom: 1px solid #333;
        }
        .back-btn {
            background: #222;
            color: #00FF9C;
            border: 1px solid #00FF9C;
            border-radius: 50%;
            width: 44px;
            height: 44px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 0 8px rgba(0, 255, 156, 0.5);
            font-size: 20px;
        }
        .container {
            max-width: 600px;
            margin: 25px auto;
            background: #1A1A1A;
            padding: 25px;
            border-radius: 20px;
            border: 1px solid #333;
            box-shadow: 0 0 20px rgba(0, 255, 156, 0.2);
        }
        h2 {
            text-align: center;
            margin-bottom: 25px;
            color: #00FF9C;
            text-shadow: 0 0 10px #00FF9C;
            font-size: 24px;
        }
        .profile-field {
            display: flex;
            align-items: center;
            margin: 22px 0;
            gap: 15px;
            flex-wrap: wrap;
        }
        .field-label {
            min-width: 130px;
            color: #00C6FF;
            font-size: 18px;
        }
        .field-value {
            flex: 1;
            padding: 12px;
            background: #222;
            border-radius: 12px;
            direction: rtl;
            font-size: 18px;
            min-width: 150px;
        }
        .edit-btn {
            background: #222;
            color: #FF3CAC;
            border: 1px solid #FF3CAC;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 0 8px rgba(255, 60, 172, 0.5);
            font-size: 16px;
        }
        .edit-btn:hover {
            background: #FF3CAC;
            color: #0D0D0D;
        }
        .edit-controls {
            display: flex;
            gap: 12px;
            margin-top: 12px;
            width: 100%;
        }
        .btn-ghost {
            flex: 1;
            padding: 10px;
            background: transparent;
            border: 1px solid #00C6FF;
            color: #00C6FF;
            border-radius: 12px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.2s;
        }
        .btn-ghost:hover {
            background: rgba(0, 198, 255, 0.15);
        }
        .btn-primary {
            flex: 1;
            padding: 10px;
            background: linear-gradient(90deg, #00C6FF, #00FF9C);
            color: #0D0D0D;
            border: none;
            border-radius: 12px;
            font-weight: bold;
            font-size: 16px;
            cursor: pointer;
            box-shadow: 0 0 10px #00C6FF, 0 0 20px #00FF9C;
        }
        .btn-logout {
            width: 100%;
            padding: 16px;
            background: linear-gradient(90deg, #EF4444, #FF3CAC);
            color: white;
            border: none;
            border-radius: 16px;
            font-size: 18px;
            margin-top: 30px;
            cursor: pointer;
            box-shadow: 0 0 12px #EF4444, 0 0 24px #FF3CAC;
        }
        .modal {
            display: none;
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: rgba(0,0,0,0.8);
            justify-content: center;
            align-items: center;
            z-index: 2000;
        }
        .modal-content {
            background: #1A1A1A;
            padding: 25px;
            border-radius: 18px;
            width: 90%;
            max-width: 420px;
            text-align: center;
            border: 1px solid #FF3CAC;
            box-shadow: 0 0 25px #FF3CAC;
        }
        .modal-buttons {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-top: 25px;
        }
    </style>
</head>
<body>
    <header class="toolbar">
        <button class="back-btn" onclick="window.history.back()">
            <i class="fas fa-arrow-right"></i>
        </button>
    </header>

    <div class="container">
        <h2>پروفایل کاربری</h2>
        
        <div class="profile-field">
            <div class="field-label">نام:</div>
            <div class="field-value" id="nameValue">{{ user.name }}</div>
            <button class="edit-btn" onclick="editField('name', this)"><i class="fas fa-pencil-alt"></i></button>
        </div>
        
        <div class="profile-field">
            <div class="field-label">نام خانوادگی:</div>
            <div class="field-value" id="familyValue">{{ user.family }}</div>
            <button class="edit-btn" onclick="editField('family', this)"><i class="fas fa-pencil-alt"></i></button>
        </div>
        
        <div class="profile-field">
            <div class="field-label">مرتبه:</div>
            <div class="field-value" id="roleValue">{{ user.role }}</div>
            <button class="edit-btn" onclick="editField('role', this)"><i class="fas fa-pencil-alt"></i></button>
        </div>
        
        <div class="profile-field">
            <div class="field-label">رمز عبور:</div>
            <div class="field-value">********</div>
            <span style="color:#6B7280; font-size:14px;">(غیرقابل تغییر)</span>
        </div>
        
        <button class="btn-logout" onclick="showLogoutModal()">خروج از حساب</button>
    </div>

    <div class="modal" id="logoutModal">
        <div class="modal-content">
            <p style="font-size:18px;">آیا مطمئن هستید می‌خواهید از حساب خارج شوید؟</p>
            <div class="modal-buttons">
                <button class="btn-ghost" onclick="closeLogout()">خیر</button>
                <button class="btn-primary" onclick="logout()">بله</button>
            </div>
        </div>
    </div>

    <script>
        // جلوگیری از بازگشت با دکمه مرورگر
        history.pushState(null, null, location.href);
        window.addEventListener('popstate', function () {
            history.pushState(null, null, location.href);
        });

        function editField(field, btn) {
            // حذف دکمه مداد
            btn.remove();
            
            const valueEl = document.getElementById(field + 'Value');
            const currentValue = valueEl.innerText;

            valueEl.innerHTML = '';

            if (field === 'role') {
                const select = document.createElement('select');
                ['مدیر', 'ناظم', 'معاون', 'مشاور'].forEach(r => {
                    const opt = document.createElement('option');
                    opt.value = r;
                    opt.innerText = r;
                    if (r === currentValue) opt.selected = true;
                    select.appendChild(opt);
                });
                select.style.width = '100%';
                select.style.padding = '10px';
                select.style.background = '#222';
                select.style.color = 'white';
                select.style.borderRadius = '10px';
                select.style.border = '1px solid #444';
                select.style.fontSize = '18px';
                valueEl.appendChild(select);
            } else {
                const input = document.createElement('input');
                input.type = 'text';
                input.value = currentValue;
                input.style.width = '100%';
                input.style.padding = '10px';
                input.style.background = '#222';
                input.style.color = 'white';
                input.style.borderRadius = '10px';
                input.style.border = '1px solid #444';
                input.style.direction = 'rtl';
                input.style.fontSize = '18px';
                valueEl.appendChild(input);
            }

            const controls = document.createElement('div');
            controls.className = 'edit-controls';
            controls.innerHTML = `
                <button class="btn-ghost" onclick="cancelEdit('${field}')">انصراف</button>
                <button class="btn-primary" onclick="saveEdit('${field}')">تایید</button>
            `;
            valueEl.parentNode.appendChild(controls);
        }

        function cancelEdit(field) {
            location.reload();
        }

        function saveEdit(field) {
            let newValue;
            if (field === 'role') {
                newValue = document.querySelector('#roleValue select').value;
            } else {
                newValue = document.querySelector('#' + field + 'Value input').value;
            }
            if (!newValue.trim()) {
                alert('مقدار نمی‌تواند خالی باشد.');
                return;
            }

            fetch('/admin/profile', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({field: field, value: newValue})
            }).then(res => res.json()).then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert('خطا در ذخیره‌سازی.');
                }
            });
        }

        function showLogoutModal() {
            document.getElementById('logoutModal').style.display = 'flex';
        }
        function closeLogout() {
            document.getElementById('logoutModal').style.display = 'none';
        }
        function logout() {
            window.location.href = '/admin/logout';
        }
    </script>
</body>
</html>
    ''', user=session['admin'])

# به‌روزرسانی پروفایل
@app.route('/admin/profile', methods=['POST'])
def update_profile():
    if not session.get('admin'):
        return jsonify(success=False), 403
    data = request.get_json()
    field = data.get('field')
    value = data.get('value')
    if field in ['name', 'family', 'role'] and value.strip():
        session['admin'][field] = value.strip()
        return jsonify(success=True)
    return jsonify(success=False), 400

# خروج
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('home'))

# صفحات placeholder
@app.route('/login/<role>')
def other_login(role):
    roles = {'teacher': 'معلمان', 'parent': 'والدین', 'student': 'دانش آموزان'}
    return f'''
    <div style="background:#0D0D0D; color:white; font-family:Vazir,sans-serif; padding:30px 20px; text-align:center; direction:rtl; min-height:100vh;">
        <h2 style="color:#FF3CAC; text-shadow:0 0 10px #FF3CAC; font-size:24px;">ورود {roles.get(role, 'کاربر')}</h2>
        <p style="margin:20px 0; font-size:18px;">این بخش در حال توسعه است.</p>
        <a href="/" style="color:#00C6FF; text-decoration:underline; display:inline-block; margin-top:20px; font-size:18px;">بازگشت به صفحه اصلی</a>
    </div>
    '''

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))