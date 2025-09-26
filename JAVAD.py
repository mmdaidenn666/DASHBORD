from flask import Flask, render_template_string, request, session, redirect, url_for, jsonify
import os

app = Flask(__name__)
app.secret_key = 'neon_dabirestan_secret_2025'

ADMIN_PASSWORD = "dabirestan012345"

# صفحه اصلی
@app.route('/')
def home():
    return render_template_string('''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
            padding: 30px;
            min-height: 100vh;
        }
        .welcome {
            text-align: center;
            font-size: 28px;
            margin-bottom: 40px;
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
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 24px;
            max-width: 1000px;
            margin: 0 auto;
        }
        .btn-card {
            display: block;
            padding: 28px;
            border-radius: 16px;
            text-decoration: none;
            text-align: center;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            border: 2px solid transparent;
        }
        .btn-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: linear-gradient(45deg, #00C6FF, #FF3CAC, #00FF9C, #9D4EDD);
            z-index: -1;
            opacity: 0;
            transition: opacity 0.3s;
        }
        .btn-card:hover::before {
            opacity: 1;
        }
        .btn-card h3 {
            font-size: 20px;
            margin-bottom: 10px;
            color: white;
        }
        .btn-card p {
            font-size: 14px;
            opacity: 0.9;
        }
        .footer {
            text-align: center;
            margin-top: 50px;
            color: #6B7280;
            font-size: 14px;
            animation: typing 4s steps(40) 1s forwards;
            white-space: nowrap;
            overflow: hidden;
            width: 0;
        }
        @keyframes typing {
            to { width: 100%; }
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
    <div class="footer">سازنده: محمدرضا محمدی دانش آموز دبیرستان جوادالائمه (رشته ریاضی)</div>
</body>
</html>
    ''')

# ورود مدیران
@app.route('/login/admin', methods=['GET', 'POST'])
def admin_login():
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
    <title>ورود مدیران</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazir:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        body {
            background: #0D0D0D;
            color: white;
            font-family: 'Vazir', sans-serif;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .form-container {
            background: #1A1A1A;
            padding: 30px;
            border-radius: 20px;
            width: 90%;
            max-width: 500px;
            box-shadow: 0 0 20px rgba(0, 200, 255, 0.3);
            border: 1px solid #333;
        }
        h2 {
            text-align: center;
            margin-bottom: 24px;
            color: #00C6FF;
            text-shadow: 0 0 10px #00C6FF;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #00FF9C;
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
            color: white;
            border: none;
            border-radius: 14px;
            font-weight: bold;
            font-size: 16px;
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
        }
        .back-link {
            display: block;
            text-align: center;
            margin-top: 20px;
            color: #00C6FF;
            text-decoration: none;
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
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    return render_template_string('''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
        }
        .toolbar {
            display: flex;
            justify-content: space-between;
            padding: 12px 20px;
            background: #151515;
            border-bottom: 1px solid #333;
        }
        .toolbar-btn {
            background: #222;
            color: #00C6FF;
            border: 1px solid #00C6FF;
            border-radius: 12px;
            padding: 8px 16px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 0 8px rgba(0, 198, 255, 0.4);
        }
        .toolbar-btn:hover {
            background: #00C6FF;
            color: #0D0D0D;
            box-shadow: 0 0 12px #00C6FF, 0 0 20px #00FF9C;
        }
        .menu-toggle {
            background: #222;
            color: #FF3CAC;
            border: 1px solid #FF3CAC;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 0 8px rgba(255, 60, 172, 0.4);
        }
        .menu-toggle:hover {
            background: #FF3CAC;
            color: #0D0D0D;
            box-shadow: 0 0 12px #FF3CAC, 0 0 20px #FF9E00;
        }
        .sidebar {
            position: fixed;
            top: 0;
            right: 0;
            height: 100%;
            width: 280px;
            background: #1A1A1A;
            border-left: 1px solid #333;
            transform: translateX(100%);
            transition: transform 0.4s cubic-bezier(0.68, -0.55, 0.27, 1.55);
            z-index: 1000;
            padding-top: 60px;
        }
        .sidebar.active {
            transform: translateX(0);
        }
        .sidebar .close-btn {
            position: absolute;
            top: 15px;
            left: 15px;
            background: #EF4444;
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-weight: bold;
        }
        .sidebar .sidebar-btn {
            display: block;
            width: calc(100% - 30px);
            margin: 15px 15px;
            padding: 14px;
            text-align: center;
            background: #222;
            color: #00FF9C;
            border: 1px solid #00FF9C;
            border-radius: 12px;
            text-decoration: none;
            transition: all 0.3s;
            box-shadow: 0 0 8px rgba(0, 255, 156, 0.4);
        }
        .sidebar .sidebar-btn:hover {
            background: #00FF9C;
            color: #0D0D0D;
            box-shadow: 0 0 12px #00FF9C, 0 0 20px #00C6FF;
        }
        .dashboard {
            padding: 30px;
        }
        .dashboard h2 {
            color: #00FF9C;
            margin-bottom: 24px;
            text-shadow: 0 0 10px #00FF9C;
        }
        .cards-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 20px;
        }
        .card {
            background: #1A1A1A;
            padding: 24px;
            border-radius: 16px;
            text-align: center;
            color: #00C6FF;
            border: 1px solid #333;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 0 8px rgba(0, 198, 255, 0.2);
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
        <div></div> <!-- فضای خالی سمت چپ -->
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

# صفحه پروفایل (صفحه جداگانه)
@app.route('/admin/profile', methods=['GET', 'POST'])
def admin_profile():
    if 'admin' not in session:
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
    <title>پروفایل</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazir:wght@400;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body {
            background: #0D0D0D;
            color: white;
            font-family: 'Vazir', sans-serif;
            padding: 20px;
        }
        .toolbar {
            display: flex;
            justify-content: space-between;
            padding: 12px 20px;
            background: #151515;
            border-bottom: 1px solid #333;
        }
        .menu-toggle {
            background: #222;
            color: #FF3CAC;
            border: 1px solid #FF3CAC;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 0 8px rgba(255, 60, 172, 0.4);
        }
        .container {
            max-width: 600px;
            margin: 30px auto;
            background: #1A1A1A;
            padding: 30px;
            border-radius: 20px;
            border: 1px solid #333;
            box-shadow: 0 0 20px rgba(0, 255, 156, 0.2);
        }
        h2 {
            text-align: center;
            margin-bottom: 30px;
            color: #00FF9C;
            text-shadow: 0 0 10px #00FF9C;
        }
        .profile-field {
            display: flex;
            align-items: center;
            margin: 20px 0;
            gap: 15px;
        }
        .field-label {
            min-width: 120px;
            color: #00C6FF;
        }
        .field-value {
            flex: 1;
            padding: 10px;
            background: #222;
            border-radius: 10px;
            direction: rtl;
        }
        .edit-btn {
            background: #222;
            color: #FF3CAC;
            border: 1px solid #FF3CAC;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 0 8px rgba(255, 60, 172, 0.4);
        }
        .edit-btn:hover {
            background: #FF3CAC;
            color: #0D0D0D;
        }
        .edit-controls {
            display: flex;
            gap: 10px;
            margin-top: 8px;
        }
        .btn-ghost {
            padding: 8px 16px;
            background: transparent;
            border: 1px solid #00C6FF;
            color: #00C6FF;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .btn-ghost:hover {
            background: rgba(0, 198, 255, 0.1);
        }
        .btn-primary {
            padding: 8px 16px;
            background: linear-gradient(90deg, #00C6FF, #00FF9C);
            color: #0D0D0D;
            border: none;
            border-radius: 10px;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 0 10px #00C6FF, 0 0 20px #00FF9C;
        }
        .btn-logout {
            width: 100%;
            padding: 14px;
            background: linear-gradient(90deg, #EF4444, #FF3CAC);
            color: white;
            border: none;
            border-radius: 14px;
            font-size: 16px;
            margin-top: 30px;
            cursor: pointer;
            box-shadow: 0 0 12px #EF4444, 0 0 24px #FF3CAC;
        }
        .modal {
            display: none;
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: rgba(0,0,0,0.7);
            justify-content: center;
            align-items: center;
            z-index: 2000;
        }
        .modal-content {
            background: #1A1A1A;
            padding: 24px;
            border-radius: 16px;
            width: 90%;
            max-width: 400px;
            text-align: center;
            border: 1px solid #FF3CAC;
            box-shadow: 0 0 20px #FF3CAC;
        }
        .modal-buttons {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <header class="toolbar">
        <div></div>
        <button class="menu-toggle" onclick="window.history.back()">
            <i class="fas fa-arrow-right"></i>
        </button>
    </header>

    <div class="container">
        <h2>پروفایل کاربری</h2>
        
        <div class="profile-field">
            <div class="field-label">نام:</div>
            <div class="field-value" id="nameValue">{{ user.name }}</div>
            <button class="edit-btn" onclick="editField('name')"><i class="fas fa-pencil-alt"></i></button>
        </div>
        
        <div class="profile-field">
            <div class="field-label">نام خانوادگی:</div>
            <div class="field-value" id="familyValue">{{ user.family }}</div>
            <button class="edit-btn" onclick="editField('family')"><i class="fas fa-pencil-alt"></i></button>
        </div>
        
        <div class="profile-field">
            <div class="field-label">مرتبه:</div>
            <div class="field-value" id="roleValue">{{ user.role }}</div>
            <button class="edit-btn" onclick="editField('role')"><i class="fas fa-pencil-alt"></i></button>
        </div>
        
        <div class="profile-field">
            <div class="field-label">رمز عبور:</div>
            <div class="field-value">********</div>
            <span style="color:#6B7280; font-size:12px;">(غیرقابل تغییر)</span>
        </div>
        
        <button class="btn-logout" onclick="showLogoutModal()">خروج از حساب</button>
    </div>

    <!-- مدال تأیید خروج -->
    <div class="modal" id="logoutModal">
        <div class="modal-content">
            <p>آیا مطمئن هستید می‌خواهید از حساب خارج شوید؟</p>
            <div class="modal-buttons">
                <button class="btn-ghost" onclick="closeLogout()">خیر</button>
                <button class="btn-primary" onclick="logout()">بله</button>
            </div>
        </div>
    </div>

    <script>
        function editField(field) {
            const valueEl = document.getElementById(field + 'Value');
            const currentValue = valueEl.innerText;

            // حذف محتوای فعلی
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
                select.style.padding = '8px';
                select.style.background = '#222';
                select.style.color = 'white';
                select.style.borderRadius = '8px';
                select.style.border = '1px solid #444';
                valueEl.appendChild(select);
            } else {
                const input = document.createElement('input');
                input.type = 'text';
                input.value = currentValue;
                input.style.width = '100%';
                input.style.padding = '8px';
                input.style.background = '#222';
                input.style.color = 'white';
                input.style.borderRadius = '8px';
                input.style.border = '1px solid #444';
                input.style.direction = 'rtl';
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
    if 'admin' not in session:
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
    <div style="background:#0D0D0D; color:white; font-family:Vazir,sans-serif; padding:50px; text-align:center; direction:rtl;">
        <h2 style="color:#FF3CAC; text-shadow:0 0 10px #FF3CAC;">ورود {roles.get(role, 'کاربر')}</h2>
        <p>این بخش در حال توسعه است.</p>
        <a href="/" style="color:#00C6FF; text-decoration:underline; display:inline-block; margin-top:20px;">بازگشت به صفحه اصلی</a>
    </div>
    '''

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))