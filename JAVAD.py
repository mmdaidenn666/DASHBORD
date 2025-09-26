from flask import Flask, render_template_string, request, session, redirect, url_for, jsonify
import os

app = Flask(__name__)
app.secret_key = 'neon_dabirestan_2025_secure_key'

ADMIN_PASSWORD = "dabirestan012345"
TEACHER_PASSWORD = "dabirjavadol"

# ========== صفحه اصلی ==========
@app.route('/')
def home():
    if session.get('admin'):
        return redirect(url_for('admin_dashboard'))
    if session.get('teacher'):
        return redirect(url_for('teacher_dashboard'))
    return render_template_string('''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>دبیرستان جوادالائمه</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazir:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body {
            background: #0D0D0D;
            color: white;
            font-family: 'Vazir', sans-serif;
            padding: 20px;
            min-height: 100vh;
        }
        .welcome {
            text-align: center;
            font-size: clamp(20px, 6vw, 28px);
            margin: 20px 0 30px;
            color: #00FF9C;
            text-shadow: 0 0 8px #00FF9C, 0 0 16px #00C6FF;
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
            font-size: clamp(16px, 4vw, 18px);
        }
        .btn-admin::before { background: linear-gradient(45deg, #00C6FF, #00FF9C); }
        .btn-teacher::before { background: linear-gradient(45deg, #FF3CAC, #FF9E00); }
        .btn-parent::before { background: linear-gradient(45deg, #9D4EDD, #00C6FF); }
        .btn-student::before { background: linear-gradient(45deg, #00FF9C, #FF3CAC); }
        .btn-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0;
            width: 100%; height: 100%;
            z-index: -1;
            border-radius: 18px;
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
            margin-top: 40px;
            color: #6B7280;
            font-size: 14px;
            white-space: pre-line;
            text-align: center;
            line-height: 1.6;
            max-width: 600px;
            margin: 40px auto 0;
            padding: 15px;
            background: rgba(0,0,0,0.2);
            border-radius: 10px;
        }
    </style>
</head>
<body>
    <h1 class="welcome">به سایت رسمی دبیرستان پسرانه جوادالائمه خوش آمدید</h1>
    <div class="button-grid">
        <a href="/login/admin" class="btn-card btn-admin"><h3>ورود مدیران</h3><p>این بخش فقط برای مدیران است</p></a>
        <a href="/login/teacher" class="btn-card btn-teacher"><h3>ورود معلمان</h3><p>این بخش فقط برای معلمان است</p></a>
        <a href="/login/parent" class="btn-card btn-parent"><h3>ورود والدین</h3><p>این بخش فقط برای والدین است</p></a>
        <a href="/login/student" class="btn-card btn-student"><h3>ورود دانش آموزان</h3><p>این بخش فقط برای دانش آموزان است</p></a>
    </div>
    <div class="footer">سازنده: محمدرضا محمدی
دانش آموز دبیرستان جوادالائمه
(رشته ریاضی)</div>
</body>
</html>
    ''')

# ========== ورود مدیران ==========
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
            # مقداردهی اولیه دانش‌آموزان
            if 'students' not in session:
                session['students'] = {
                    'دهم': {'ریاضی': [], 'تجربی': [], 'انسانی': []},
                    'یازدهم': {'ریاضی': [], 'تجربی': [], 'انسانی': []},
                    'دوازدهم': {'ریاضی': [], 'تجربی': [], 'انسانی': []}
                }
            return redirect(url_for('admin_dashboard'))
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ورود مدیران</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazir:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        body { background: #0D0D0D; color: white; font-family: 'Vazir', sans-serif; padding: 15px; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .form-container { background: #1A1A1A; padding: 25px; border-radius: 20px; width: 100%; max-width: 500px; box-shadow: 0 0 20px rgba(0, 200, 255, 0.3); border: 1px solid #333; }
        h2 { text-align: center; margin-bottom: 24px; color: #00C6FF; text-shadow: 0 0 10px #00C6FF; font-size: 24px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; color: #00FF9C; font-size: 16px; }
        input, select { width: 100%; padding: 14px; background: #222; border: 1px solid #444; border-radius: 12px; color: white; font-size: 16px; direction: rtl; }
        .btn-primary { width: 100%; padding: 14px; background: linear-gradient(90deg, #00C6FF, #00FF9C); color: #0D0D0D; border: none; border-radius: 14px; font-weight: bold; font-size: 18px; cursor: pointer; box-shadow: 0 0 12px #00C6FF, 0 0 24px #00FF9C; }
        .alert { padding: 12px; background: #331111; border: 1px solid #EF4444; border-radius: 8px; color: #FF6B6B; text-align: center; margin-bottom: 20px; font-size: 16px; }
        .back-link { display: block; text-align: center; margin-top: 20px; color: #00C6FF; text-decoration: none; font-size: 16px; }
    </style>
</head>
<body>
    <div class="form-container">
        <h2>ورود مدیران</h2>
        <form method="POST">
            {% if error %}<div class="alert">{{ error }}</div>{% endif %}
            <div class="form-group"><label>نام</label><input type="text" name="name" value="{{ request.form.name or '' }}" required></div>
            <div class="form-group"><label>نام خانوادگی</label><input type="text" name="family" value="{{ request.form.family or '' }}" required></div>
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
            <div class="form-group"><label>رمز عبور</label><input type="password" name="password" required></div>
            <button type="submit" class="btn-primary">ورود</button>
        </form>
        <a href="/" class="back-link">بازگشت به صفحه اصلی</a>
    </div>
</body>
</html>
    ''', error=error)

# ========== درگاه مدیران ==========
@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
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
        * { margin:0; padding:0; box-sizing:border-box; }
        body { background: #0D0D0D; color: white; font-family: 'Vazir', sans-serif; }
        .toolbar { display: flex; justify-content: flex-end; padding: 12px 20px; background: #151515; border-bottom: 1px solid #333; }
        .menu-toggle { background: #222; color: #FF3CAC; border: 1px solid #FF3CAC; border-radius: 50%; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 0 8px rgba(255, 60, 172, 0.5); font-size: 20px; }
        .sidebar { position: fixed; top: 0; right: 0; height: 100%; width: clamp(240px, 80vw, 300px); background: #1A1A1A; border-left: 1px solid #444; transform: translateX(100%); transition: transform 0.4s cubic-bezier(0.68, -0.55, 0.27, 1.55); z-index: 1000; padding-top: 70px; }
        .sidebar.active { transform: translateX(0); }
        .close-btn { position: absolute; top: 20px; left: 20px; background: #EF4444; color: white; width: 34px; height: 34px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; font-weight: bold; font-size: 20px; box-shadow: 0 0 10px #EF4444; }
        .sidebar-btn { display: block; width: calc(100% - 40px); margin: 18px 20px; padding: 16px; text-align: center; background: linear-gradient(90deg, #00C6FF, #00FF9C); color: #0D0D0D; border: none; border-radius: 14px; text-decoration: none; font-weight: bold; font-size: 18px; box-shadow: 0 0 10px #00C6FF, 0 0 20px #00FF9C; }
        .dashboard { padding: 20px; }
        .dashboard h2 { color: #00FF9C; margin: 20px 0 25px; text-shadow: 0 0 10px #00FF9C; font-size: 26px; text-align: center; }
        .cards-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(clamp(150px, 45vw, 220px), 1fr)); gap: 20px; padding: 0 10px; }
        .card { background: #1A1A1A; padding: 22px 16px; border-radius: 18px; text-align: center; color: #00C6FF; border: 1px solid #333; cursor: pointer; transition: all 0.3s; font-size: 18px; box-shadow: 0 0 8px rgba(0, 198, 255, 0.3); }
        .card:hover { transform: translateY(-6px); box-shadow: 0 0 16px #00C6FF, 0 0 24px #00FF9C; background: #222; }
    </style>
</head>
<body>
    <header class="toolbar">
        <button class="menu-toggle" id="menuToggle"><i class="fas fa-bars"></i></button>
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
            <a href="/admin/students" class="card">مدیریت دانش آموزان</a>
            <div class="card">مدیریت معلمان</div>
            <div class="card">مدیریت گزارشات والدین</div>
            <div class="card">مدیریت گزارشات معلمان</div>
            <div class="card">مدیریت گزارشات دانش آموزان</div>
            <div class="card">مدیریت بخش آزمایشگاه</div>
            <div class="card">مدیریت نمرات</div>
            <div class="card">مدیریت کارنامه</div>
        </div>
    </div>
    <script>
        history.pushState(null, null, location.href);
        window.addEventListener('popstate', () => history.pushState(null, null, location.href));
        document.getElementById('menuToggle').addEventListener('click', () => document.getElementById('sidebar').classList.add('active'));
        document.getElementById('closeSidebar').addEventListener('click', () => document.getElementById('sidebar').classList.remove('active'));
    </script>
</body>
</html>
    ''')

# ========== پروفایل مدیران ==========
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
    
    user = session['admin']  # اینجا user تعریف می‌شود
    return render_template_string('''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>پروفایل مدیر</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazir:wght@400;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background: #0D0D0D; color: white; font-family: 'Vazir', sans-serif; padding: 15px; }
        .toolbar { display: flex; justify-content: flex-end; padding: 12px 20px; background: #151515; border-bottom: 1px solid #333; }
        .back-btn { background: #222; color: #00FF9C; border: 1px solid #00FF9C; border-radius: 50%; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 0 8px rgba(0, 255, 156, 0.5); font-size: 20px; }
        .container { max-width: 600px; margin: 25px auto; background: #1A1A1A; padding: 25px; border-radius: 20px; border: 1px solid #333; box-shadow: 0 0 20px rgba(0, 255, 156, 0.2); }
        h2 { text-align: center; margin-bottom: 25px; color: #00FF9C; text-shadow: 0 0 10px #00FF9C; font-size: 24px; }
        .profile-field { display: flex; align-items: center; margin: 22px 0; gap: 15px; flex-wrap: wrap; }
        .field-label { min-width: 130px; color: #00C6FF; font-size: 18px; }
        .field-value { flex: 1; padding: 12px; background: #222; border-radius: 12px; direction: rtl; font-size: 18px; min-width: 150px; }
        .edit-btn { background: #222; color: #FF3CAC; border: 1px solid #FF3CAC; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 0 8px rgba(255, 60, 172, 0.5); font-size: 16px; }
        .edit-controls { display: flex; gap: 12px; margin-top: 12px; width: 100%; }
        .btn-ghost { flex: 1; padding: 10px; background: transparent; border: 1px solid #00C6FF; color: #00C6FF; border-radius: 12px; cursor: pointer; font-size: 16px; }
        .btn-primary { flex: 1; padding: 10px; background: linear-gradient(90deg, #00C6FF, #00FF9C); color: #0D0D0D; border: none; border-radius: 12px; font-weight: bold; font-size: 16px; cursor: pointer; box-shadow: 0 0 10px #00C6FF, 0 0 20px #00FF9C; }
        .btn-logout { width: 100%; padding: 16px; background: linear-gradient(90deg, #EF4444, #FF3CAC); color: white; border: none; border-radius: 16px; font-size: 18px; margin-top: 30px; cursor: pointer; box-shadow: 0 0 12px #EF4444, 0 0 24px #FF3CAC; }
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); justify-content: center; align-items: center; z-index: 2000; }
        .modal-content { background: #1A1A1A; padding: 25px; border-radius: 18px; width: 90%; max-width: 420px; text-align: center; border: 1px solid #FF3CAC; box-shadow: 0 0 25px #FF3CAC; }
        .modal-buttons { display: flex; gap: 15px; justify-content: center; margin-top: 25px; }
    </style>
</head>
<body>
    <header class="toolbar">
        <button class="back-btn" onclick="window.history.back()"><i class="fas fa-arrow-right"></i></button>
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
        function editField(field, btn) {
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
                select.style.width = '100%'; select.style.padding = '10px'; select.style.background = '#222'; select.style.color = 'white'; select.style.borderRadius = '10px'; select.style.border = '1px solid #444'; select.style.fontSize = '18px';
                valueEl.appendChild(select);
            } else {
                const input = document.createElement('input');
                input.type = 'text';
                input.value = currentValue;
                input.style.width = '100%'; input.style.padding = '10px'; input.style.background = '#222'; input.style.color = 'white'; input.style.borderRadius = '10px'; input.style.border = '1px solid #444'; input.style.direction = 'rtl'; input.style.fontSize = '18px';
                valueEl.appendChild(input);
            }

            const controls = document.createElement('div');
            controls.className = 'edit-controls';
            controls.innerHTML = `<button class="btn-ghost" onclick="cancelEdit('${field}')">انصراف</button><button class="btn-primary" onclick="saveEdit('${field}')">تایید</button>`;
            valueEl.parentNode.appendChild(controls);
        }

        function cancelEdit(field) { location.reload(); }

        function saveEdit(field) {
            let newValue;
            if (field === 'role') {
                newValue = document.querySelector('#roleValue select').value;
            } else {
                newValue = document.querySelector('#' + field + 'Value input').value;
            }
            if (!newValue.trim()) { alert('مقدار نمی‌تواند خالی باشد.'); return; }

            fetch('/admin/profile', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({field: field, value: newValue})
            }).then(res => res.json()).then(data => {
                if (data.success) {
                    document.getElementById(field + 'Value').innerText = newValue;
                } else {
                    alert('خطا در ذخیره‌سازی.');
                }
            });
        }

        function showLogoutModal() { document.getElementById('logoutModal').style.display = 'flex'; }
        function closeLogout() { document.getElementById('logoutModal').style.display = 'none'; }
        function logout() { window.location.href = '/admin/logout'; }
    </script>
</body>
</html>
    ''', user=user)  # ارسال user به تمپلیت

# ========== مدیریت دانش‌آموزان ==========
@app.route('/admin/students')
def students_overview():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    return render_template_string('''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مدیریت دانش آموزان</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazir:wght@400;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { background: #0D0D0D; color: white; font-family: 'Vazir', sans-serif; }
        .toolbar { display: flex; justify-content: flex-end; padding: 12px 20px; background: #151515; border-bottom: 1px solid #333; }
        .menu-toggle { background: #222; color: #FF3CAC; border: 1px solid #FF3CAC; border-radius: 50%; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 0 8px rgba(255, 60, 172, 0.5); font-size: 20px; }
        .sidebar { position: fixed; top: 0; right: 0; height: 100%; width: clamp(240px, 80vw, 300px); background: #1A1A1A; border-left: 1px solid #444; transform: translateX(100%); transition: transform 0.4s cubic-bezier(0.68, -0.55, 0.27, 1.55); z-index: 1000; padding-top: 70px; }
        .sidebar.active { transform: translateX(0); }
        .close-btn { position: absolute; top: 20px; left: 20px; background: #EF4444; color: white; width: 34px; height: 34px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; font-weight: bold; font-size: 20px; box-shadow: 0 0 10px #EF4444; }
        .sidebar-btn { display: block; width: calc(100% - 40px); margin: 18px 20px; padding: 16px; text-align: center; background: linear-gradient(90deg, #00C6FF, #00FF9C); color: #0D0D0D; border: none; border-radius: 14px; text-decoration: none; font-weight: bold; font-size: 18px; box-shadow: 0 0 10px #00C6FF, 0 0 20px #00FF9C; }
        .dashboard { padding: 20px; }
        .dashboard h2 { color: #00FF9C; margin: 20px 0 25px; text-shadow: 0 0 10px #00FF9C; font-size: 26px; text-align: center; }
        .cards-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(clamp(150px, 45vw, 220px), 1fr)); gap: 20px; padding: 0 10px; }
        .card { background: #1A1A1A; padding: 22px 16px; border-radius: 18px; text-align: center; color: #00C6FF; border: 1px solid #333; cursor: pointer; transition: all 0.3s; font-size: 18px; box-shadow: 0 0 8px rgba(0, 198, 255, 0.3); }
        .card:hover { transform: translateY(-6px); box-shadow: 0 0 16px #00C6FF, 0 0 24px #00FF9C; background: #222; }
    </style>
</head>
<body>
    <header class="toolbar">
        <button class="menu-toggle" id="menuToggle"><i class="fas fa-bars"></i></button>
    </header>
    <div class="sidebar" id="sidebar">
        <div class="close-btn" id="closeSidebar">&times;</div>
        <a href="/admin/dashboard" class="sidebar-btn">صفحه اصلی</a>
        <a href="/admin/profile" class="sidebar-btn">پروفایل</a>
        <a href="#" class="sidebar-btn">اعلانات</a>
    </div>
    <div class="dashboard">
        <h2>مدیریت دانش آموزان</h2>
        <div class="cards-grid">
            <a href="/admin/students/grade/دهم" class="card">پایه دهم</a>
            <a href="/admin/students/grade/یازدهم" class="card">پایه یازدهم</a>
            <a href="/admin/students/grade/دوازدهم" class="card">پایه دوازدهم</a>
        </div>
    </div>
    <script>
        history.pushState(null, null, location.href);
        window.addEventListener('popstate', () => history.pushState(null, null, location.href));
        document.getElementById('menuToggle').addEventListener('click', () => document.getElementById('sidebar').classList.add('active'));
        document.getElementById('closeSidebar').addEventListener('click', () => document.getElementById('sidebar').classList.remove('active'));
    </script>
</body>
</html>
    ''')

# ========== انتخاب پایه ==========
@app.route('/admin/students/grade/<grade>')
def select_field(grade):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    if grade not in ['دهم', 'یازدهم', 'دوازدهم']:
        return "پایه نامعتبر", 400
    return render_template_string('''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ grade }} - مدیریت دانش آموزان</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazir:wght@400;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { background: #0D0D0D; color: white; font-family: 'Vazir', sans-serif; }
        .toolbar { display: flex; justify-content: space-between; align-items: center; padding: 12px 20px; background: #151515; border-bottom: 1px solid #333; }
        .menu-toggle { background: #222; color: #FF3CAC; border: 1px solid #FF3CAC; border-radius: 50%; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 0 8px rgba(255, 60, 172, 0.5); font-size: 20px; }
        .search-btn { background: #222; color: #00FF9C; border: 1px solid #00FF9C; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 0 8px rgba(0, 255, 156, 0.5); font-size: 18px; }
        .student-count { display: flex; align-items: center; gap: 8px; color: #00FF9C; font-weight: bold; }
        .dashboard { padding: 20px; }
        .dashboard h2 { color: #00FF9C; margin: 20px 0 25px; text-shadow: 0 0 10px #00FF9C; font-size: 26px; text-align: center; }
        .cards-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(clamp(150px, 45vw, 220px), 1fr)); gap: 20px; padding: 0 10px; }
        .card { background: #1A1A1A; padding: 22px 16px; border-radius: 18px; text-align: center; color: #FF3CAC; border: 1px solid #333; cursor: pointer; transition: all 0.3s; font-size: 18px; box-shadow: 0 0 8px rgba(255, 60, 172, 0.3); }
        .card:hover { transform: translateY(-6px); box-shadow: 0 0 16px #FF3CAC, 0 0 24px #FF9E00; background: #222; }
        .fab { position: fixed; bottom: 20px; right: 20px; width: 60px; height: 60px; border-radius: 50%; background: linear-gradient(135deg, #00C6FF, #00FF9C); display: flex; align-items: center; justify-content: center; color: white; font-size: 24px; box-shadow: 0 4px 12px rgba(0,198,255,0.4); cursor: pointer; }
    </style>
</head>
<body>
    <header class="toolbar">
        <div class="student-count">
            <i class="fas fa-user-graduate"></i>
            <span id="count">{{ count }}</span>
        </div>
        <div>{{ grade }}</div>
        <div style="display:flex; gap:10px;">
            <button class="search-btn" onclick="searchStudents('{{ grade }}')"><i class="fas fa-search"></i></button>
            <button class="menu-toggle" id="menuToggle"><i class="fas fa-bars"></i></button>
        </div>
    </header>
    <div class="sidebar" id="sidebar">
        <div class="close-btn" id="closeSidebar">&times;</div>
        <a href="/admin/dashboard" class="sidebar-btn">صفحه اصلی</a>
        <a href="/admin/profile" class="sidebar-btn">پروفایل</a>
        <a href="#" class="sidebar-btn">اعلانات</a>
    </div>
    <div class="dashboard">
        <h2>رشته‌ها</h2>
        <div class="cards-grid">
            <a href="/admin/students/grade/{{ grade }}/field/ریاضی" class="card">ریاضی</a>
            <a href="/admin/students/grade/{{ grade }}/field/تجربی" class="card">تجربی</a>
            <a href="/admin/students/grade/{{ grade }}/field/انسانی" class="card">انسانی</a>
        </div>
    </div>
    <div class="fab" onclick="addStudent('{{ grade }}')"><i class="fas fa-plus"></i></div>
    <script>
        const count = {{ count }};
        history.pushState(null, null, location.href);
        window.addEventListener('popstate', () => history.pushState(null, null, location.href));
        document.getElementById('menuToggle').addEventListener('click', () => document.getElementById('sidebar').classList.add('active'));
        document.getElementById('closeSidebar').addEventListener('click', () => document.getElementById('sidebar').classList.remove('active'));

        function addStudent(grade) {
            alert('برای اضافه کردن دانش‌آموز، ابتدا یک رشته را انتخاب کنید.');
        }

        function searchStudents(grade) {
            window.location.href = `/admin/students/search?grade=${grade}`;
        }
    </script>
</body>
</html>
    ''', grade=grade, count=len(session['students'][grade]['ریاضی']) + len(session['students'][grade]['تجربی']) + len(session['students'][grade]['انسانی']))

# ========== انتخاب رشته ==========
@app.route('/admin/students/grade/<grade>/field/<field>')
def list_students(grade, field):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    if grade not in ['دهم', 'یازدهم', 'دوازدهم'] or field not in ['ریاضی', 'تجربی', 'انسانی']:
        return "داده نامعتبر", 400
    students = session['students'][grade][field]
    return render_template_string('''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ grade }} - {{ field }} - مدیریت دانش آموزان</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazir:wght@400;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { background: #0D0D0D; color: white; font-family: 'Vazir', sans-serif; }
        .toolbar { display: flex; justify-content: space-between; align-items: center; padding: 12px 20px; background: #151515; border-bottom: 1px solid #333; }
        .menu-toggle { background: #222; color: #FF3CAC; border: 1px solid #FF3CAC; border-radius: 50%; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 0 8px rgba(255, 60, 172, 0.5); font-size: 20px; }
        .search-btn { background: #222; color: #00FF9C; border: 1px solid #00FF9C; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 0 8px rgba(0, 255, 156, 0.5); font-size: 18px; }
        .student-count { display: flex; align-items: center; gap: 8px; color: #00FF9C; font-weight: bold; }
        .dashboard { padding: 20px; }
        .dashboard h2 { color: #00FF9C; margin: 20px 0 25px; text-shadow: 0 0 10px #00FF9C; font-size: 26px; text-align: center; }
        .student-list { display: flex; flex-direction: column; gap: 15px; }
        .student-card { background: #1A1A1A; padding: 16px; border-radius: 16px; display: flex; justify-content: space-between; align-items: center; border: 1px solid #333; cursor: pointer; transition: all 0.2s; }
        .student-card:hover { background: #222; transform: translateY(-2px); }
        .student-info { text-align: right; }
        .student-name { font-weight: bold; font-size: 18px; color: #00C6FF; }
        .student-id { font-size: 14px; color: #6B7280; margin-top: 4px; }
        .student-actions { display: flex; gap: 10px; }
        .action-btn { width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; }
        .edit-btn { background: #222; color: #00FF9C; border: 1px solid #00FF9C; }
        .delete-btn { background: #222; color: #EF4444; border: 1px solid #EF4444; }
        .fab { position: fixed; bottom: 20px; right: 20px; width: 60px; height: 60px; border-radius: 50%; background: linear-gradient(135deg, #00C6FF, #00FF9C); display: flex; align-items: center; justify-content: center; color: white; font-size: 24px; box-shadow: 0 4px 12px rgba(0,198,255,0.4); cursor: pointer; }
    </style>
</head>
<body>
    <header class="toolbar">
        <div class="student-count">
            <i class="fas fa-user-graduate"></i>
            <span id="count">{{ count }}</span>
        </div>
        <div>{{ grade }} - {{ field }}</div>
        <div style="display:flex; gap:10px;">
            <button class="search-btn" onclick="searchStudents('{{ grade }}')"><i class="fas fa-search"></i></button>
            <button class="menu-toggle" id="menuToggle"><i class="fas fa-bars"></i></button>
        </div>
    </header>
    <div class="sidebar" id="sidebar">
        <div class="close-btn" id="closeSidebar">&times;</div>
        <a href="/admin/dashboard" class="sidebar-btn">صفحه اصلی</a>
        <a href="/admin/profile" class="sidebar-btn">پروفایل</a>
        <a href="#" class="sidebar-btn">اعلانات</a>
    </div>
    <div class="dashboard">
        <h2>دانش‌آموزان</h2>
        <div class="student-list" id="studentList">
            {% for student in students %}
            <div class="student-card" onclick="viewStudent({{ loop.index0 }})">
                <div class="student-info">
                    <div class="student-name">{{ student.name }} {{ student.family }}</div>
                    <div class="student-id">کد ملی: {{ student.national_id }}</div>
                </div>
                <div class="student-actions">
                    <div class="action-btn edit-btn" onclick="editStudent(event, {{ loop.index0 }})"><i class="fas fa-pencil-alt"></i></div>
                    <div class="action-btn delete-btn" onclick="deleteStudent(event, {{ loop.index0 }})"><i class="fas fa-trash"></i></div>
                </div>
            </div>
            {% endfor %}
            {% if not students %}
            <div style="text-align:center; padding:30px; color:#6B7280;">دانش‌آموزی وجود ندارد.</div>
            {% endif %}
        </div>
    </div>
    <div class="fab" onclick="addStudentForm('{{ grade }}', '{{ field }}')"><i class="fas fa-plus"></i></div>

    <!-- فرم اضافه کردن دانش‌آموز -->
    <div id="addStudentModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); z-index:2000; justify-content:center; align-items:center;">
        <div style="background:#1A1A1A; padding:25px; border-radius:20px; width:90%; max-width:500px; border:1px solid #333;">
            <h3 style="text-align:center; margin-bottom:20px; color:#00FF9C;">اضافه کردن دانش‌آموز</h3>
            <div id="formAlert" style="display:none; padding:10px; background:#331111; border:1px solid #EF4444; border-radius:8px; color:#FF6B6B; margin-bottom:15px; text-align:center;"></div>
            <div style="display:flex; flex-direction:column; gap:15px;">
                <input type="text" id="studentName" placeholder="نام دانش‌آموز (اجباری)" style="padding:12px; background:#222; border:1px solid #444; border-radius:10px; color:white; direction:rtl;">
                <input type="text" id="studentFamily" placeholder="نام خانوادگی دانش‌آموز (اجباری)" style="padding:12px; background:#222; border:1px solid #444; border-radius:10px; color:white; direction:rtl;">
                <input type="text" id="studentNationalId" placeholder="کد ملی دانش‌آموز (اجباری)" style="padding:12px; background:#222; border:1px solid #444; border-radius:10px; color:white; direction:rtl;">
                <input type="text" id="studentNumber" placeholder="شماره دانش‌آموز (اختیاری)" style="padding:12px; background:#222; border:1px solid #444; border-radius:10px; color:white; direction:rtl;">
                <input type="text" id="fatherNumber" placeholder="شماره پدر (اختیاری)" style="padding:12px; background:#222; border:1px solid #444; border-radius:10px; color:white; direction:rtl;">
                <input type="text" id="motherNumber" placeholder="شماره مادر (اختیاری)" style="padding:12px; background:#222; border:1px solid #444; border-radius:10px; color:white; direction:rtl;">
            </div>
            <div style="display:flex; gap:10px; margin-top:20px;">
                <button style="flex:1; padding:12px; background:#333; border:1px solid #444; border-radius:10px; color:white;" onclick="closeAddForm()">انصراف</button>
                <button style="flex:1; padding:12px; background:linear-gradient(90deg, #00C6FF, #00FF9C); border:none; border-radius:10px; color:#0D0D0D; font-weight:bold;" onclick="submitAddStudent('{{ grade }}', '{{ field }}')">تایید</button>
            </div>
        </div>
    </div>

    <!-- مدال تأیید حذف -->
    <div id="deleteModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); z-index:2000; justify-content:center; align-items:center;">
        <div style="background:#1A1A1A; padding:25px; border-radius:20px; width:90%; max-width:400px; border:1px solid #EF4444; text-align:center;">
            <p style="font-size:18px; margin-bottom:20px;">آیا مطمئن هستید می‌خواهید اطلاعات دانش‌آموز را پاک کنید؟</p>
            <div style="display:flex; gap:10px; justify-content:center;">
                <button style="flex:1; padding:12px; background:#333; border:1px solid #444; border-radius:10px; color:white;" onclick="closeDeleteModal()">خیر</button>
                <button style="flex:1; padding:12px; background:linear-gradient(90deg, #EF4444, #FF3CAC); border:none; border-radius:10px; color:white; font-weight:bold;" onclick="confirmDelete()">بله</button>
            </div>
        </div>
    </div>

    <!-- مدال مشاهده جزئیات -->
    <div id="viewModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); z-index:2000; justify-content:center; align-items:center; overflow:auto;">
        <div style="background:#1A1A1A; padding:25px; border-radius:20px; width:90%; max-width:500px; border:1px solid #333; margin:20px auto;">
            <h3 style="text-align:center; margin-bottom:20px; color:#00FF9C;">جزئیات دانش‌آموز</h3>
            <div id="viewContent" style="display:flex; flex-direction:column; gap:15px;"></div>
            <button style="width:100%; padding:12px; background:#333; border:1px solid #444; border-radius:10px; color:white; margin-top:20px;" onclick="closeViewModal()">بستن</button>
        </div>
    </div>

    <script>
        const students = {{ students|tojson }};
        let deleteIndex = -1;
        let viewIndex = -1;

        history.pushState(null, null, location.href);
        window.addEventListener('popstate', () => history.pushState(null, null, location.href));
        document.getElementById('menuToggle').addEventListener('click', () => document.getElementById('sidebar').classList.add('active'));
        document.getElementById('closeSidebar').addEventListener('click', () => document.getElementById('sidebar').classList.remove('active'));

        function searchStudents(grade) {
            window.location.href = `/admin/students/search?grade=${grade}`;
        }

        function addStudentForm(grade, field) {
            document.getElementById('addStudentModal').style.display = 'flex';
            // پاک کردن فیلدها
            document.getElementById('studentName').value = '';
            document.getElementById('studentFamily').value = '';
            document.getElementById('studentNationalId').value = '';
            document.getElementById('studentNumber').value = '';
            document.getElementById('fatherNumber').value = '';
            document.getElementById('motherNumber').value = '';
            document.getElementById('formAlert').style.display = 'none';
        }

        function closeAddForm() {
            document.getElementById('addStudentModal').style.display = 'none';
        }

        function submitAddStudent(grade, field) {
            const name = document.getElementById('studentName').value.trim();
            const family = document.getElementById('studentFamily').value.trim();
            const nationalId = document.getElementById('studentNationalId').value.trim();
            const studentNumber = document.getElementById('studentNumber').value.trim();
            const fatherNumber = document.getElementById('fatherNumber').value.trim();
            const motherNumber = document.getElementById('motherNumber').value.trim();

            if (!name || !family || !nationalId) {
                showAlert('لطفاً فیلدهای اجباری را پر کنید.');
                return;
            }

            // بررسی تکرار کد ملی
            const allStudents = {{ session['students']|tojson }};
            for (const g in allStudents) {
                for (const f in allStudents[g]) {
                    if (allStudents[g][f].some(s => s.national_id === nationalId)) {
                        showAlert('این دانش‌آموز با این کد ملی وجود دارد.');
                        return;
                    }
                }
            }

            fetch('/admin/students/add', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    grade: grade,
                    field: field,
                    student: {
                        name: name,
                        family: family,
                        national_id: nationalId,
                        student_number: studentNumber,
                        father_number: fatherNumber,
                        mother_number: motherNumber
                    }
                })
            }).then(res => res.json()).then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    showAlert('خطا در اضافه کردن دانش‌آموز.');
                }
            });
        }

        function showAlert(message) {
            const alertEl = document.getElementById('formAlert');
            alertEl.innerText = message;
            alertEl.style.display = 'block';
        }

        function editStudent(e, index) {
            e.stopPropagation();
            const student = students[index];
            document.getElementById('addStudentModal').style.display = 'flex';
            document.getElementById('studentName').value = student.name;
            document.getElementById('studentFamily').value = student.family;
            document.getElementById('studentNationalId').value = student.national_id;
            document.getElementById('studentNumber').value = student.student_number || '';
            document.getElementById('fatherNumber').value = student.father_number || '';
            document.getElementById('motherNumber').value = student.mother_number || '';
            document.getElementById('formAlert').style.display = 'none';

            // ذخیره ایندکس برای ویرایش
            document.getElementById('addStudentModal').dataset.editIndex = index;
            document.getElementById('addStudentModal').dataset.editGrade = students[index].grade;
            document.getElementById('addStudentModal').dataset.editField = students[index].field;
        }

        function deleteStudent(e, index) {
            e.stopPropagation();
            deleteIndex = index;
            document.getElementById('deleteModal').style.display = 'flex';
        }

        function closeDeleteModal() {
            document.getElementById('deleteModal').style.display = 'none';
            deleteIndex = -1;
        }

        function confirmDelete() {
            if (deleteIndex === -1) return;
            const student = students[deleteIndex];
            fetch('/admin/students/delete', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    grade: student.grade,
                    field: student.field,
                    index: deleteIndex
                })
            }).then(res => res.json()).then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert('خطا در حذف دانش‌آموز.');
                }
            });
        }

        function viewStudent(index) {
            viewIndex = index;
            const student = students[index];
            const content = `
                <div style="border:1px solid #444; padding:12px; border-radius:10px;">
                    <div><strong>نام دانش‌آموز:</strong> ${student.name}</div>
                    <div><strong>نام خانوادگی دانش‌آموز:</strong> ${student.family}</div>
                    <div><strong>کد ملی دانش‌آموز:</strong> ${student.national_id}</div>
                    <div><strong>شماره دانش‌آموز:</strong> ${student.student_number || 'ندارد'}</div>
                    <div><strong>شماره پدر:</strong> ${student.father_number || 'ندارد'}</div>
                    <div><strong>شماره مادر:</strong> ${student.mother_number || 'ندارد'}</div>
                </div>
            `;
            document.getElementById('viewContent').innerHTML = content;
            document.getElementById('viewModal').style.display = 'block';
        }

        function closeViewModal() {
            document.getElementById('viewModal').style.display = 'none';
            viewIndex = -1;
        }
    </script>
</body>
</html>
    ''', grade=grade, field=field, students=students, count=len(students))

# ========== API اضافه کردن دانش‌آموز ==========
@app.route('/admin/students/add', methods=['POST'])
def add_student():
    if not session.get('admin'):
        return jsonify(success=False), 403
    data = request.get_json()
    grade = data['grade']
    field = data['field']
    student = data['student']
    
    # بررسی تکرار کد ملی
    for g in session['students']:
        for f in session['students'][g]:
            if any(s['national_id'] == student['national_id'] for s in session['students'][g][f]):
                return jsonify(success=False, error="کد ملی تکراری است.")
    
    # اضافه کردن پایه و رشته به داده‌ها
    student['grade'] = grade
    student['field'] = field
    session['students'][grade][field].append(student)
    return jsonify(success=True)

# ========== API حذف دانش‌آموز ==========
@app.route('/admin/students/delete', methods=['POST'])
def delete_student():
    if not session.get('admin'):
        return jsonify(success=False), 403
    data = request.get_json()
    grade = data['grade']
    field = data['field']
    index = data['index']
    try:
        session['students'][grade][field].pop(index)
        return jsonify(success=True)
    except (IndexError, KeyError):
        return jsonify(success=False)

# ========== جستجوی دانش‌آموزان ==========
@app.route('/admin/students/search')
def search_students():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    grade = request.args.get('grade', '')
    query = request.args.get('q', '').strip().lower()
    
    results = []
    grades_to_search = [grade] if grade in ['دهم', 'یازدهم', 'دوازدهم'] else ['دهم', 'یازدهم', 'دوازدهم']
    
    for g in grades_to_search:
        for f in ['ریاضی', 'تجربی', 'انسانی']:
            for student in session['students'][g][f]:
                name = (student['name'] + ' ' + student['family']).lower()
                if query in name or query in student['national_id'].lower():
                    results.append({
                        'name': student['name'],
                        'family': student['family'],
                        'national_id': student['national_id'],
                        'grade': g,
                        'field': f
                    })
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>جستجوی دانش‌آموزان</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazir:wght@400;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { background: #0D0D0D; color: white; font-family: 'Vazir', sans-serif; }
        .toolbar { display: flex; justify-content: space-between; align-items: center; padding: 12px 20px; background: #151515; border-bottom: 1px solid #333; }
        .menu-toggle { background: #222; color: #FF3CAC; border: 1px solid #FF3CAC; border-radius: 50%; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 0 8px rgba(255, 60, 172, 0.5); font-size: 20px; }
        .search-container { display: flex; gap: 10px; flex: 1; margin: 0 10px; }
        .search-input { flex: 1; padding: 10px 15px; background: #222; border: 1px solid #444; border-radius: 10px; color: white; direction: rtl; }
        .search-btn { padding: 10px 20px; background: linear-gradient(90deg, #00C6FF, #00FF9C); border: none; border-radius: 10px; color: #0D0D0D; font-weight: bold; cursor: pointer; }
        .dashboard { padding: 20px; }
        .dashboard h2 { color: #00FF9C; margin: 20px 0 25px; text-shadow: 0 0 10px #00FF9C; font-size: 26px; text-align: center; }
        .student-list { display: flex; flex-direction: column; gap: 15px; }
        .student-card { background: #1A1A1A; padding: 16px; border-radius: 16px; display: flex; justify-content: space-between; align-items: center; border: 1px solid #333; cursor: pointer; transition: all 0.2s; }
        .student-card:hover { background: #222; transform: translateY(-2px); }
        .student-info { text-align: right; }
        .student-name { font-weight: bold; font-size: 18px; color: #00C6FF; }
        .student-id { font-size: 14px; color: #6B7280; margin-top: 4px; }
        .student-grade-field { font-size: 12px; color: #00FF9C; }
    </style>
</head>
<body>
    <header class="toolbar">
        <button class="menu-toggle" id="menuToggle"><i class="fas fa-bars"></i></button>
        <div>جستجوی دانش‌آموزان</div>
        <div></div>
    </header>
    <div class="sidebar" id="sidebar">
        <div class="close-btn" id="closeSidebar">&times;</div>
        <a href="/admin/dashboard" class="sidebar-btn">صفحه اصلی</a>
        <a href="/admin/profile" class="sidebar-btn">پروفایل</a>
        <a href="#" class="sidebar-btn">اعلانات</a>
    </div>
    <div class="dashboard">
        <div class="search-container">
            <input type="text" id="searchInput" class="search-input" placeholder="جستجو بر اساس نام، نام خانوادگی یا کد ملی..." value="{{ query }}">
            <button class="search-btn" onclick="performSearch()"><i class="fas fa-search"></i> جستجو</button>
        </div>
        <h2>نتایج جستجو</h2>
        <div class="student-list">
            {% for student in results %}
            <div class="student-card" onclick="viewStudentDetails('{{ student.name }}', '{{ student.family }}', '{{ student.national_id }}', '{{ student.grade }}', '{{ student.field }}')">
                <div class="student-info">
                    <div class="student-name">{{ student.name }} {{ student.family }}</div>
                    <div class="student-id">کد ملی: {{ student.national_id }}</div>
                    <div class="student-grade-field">{{ student.grade }} - {{ student.field }}</div>
                </div>
            </div>
            {% endfor %}
            {% if not results %}
            <div style="text-align:center; padding:30px; color:#6B7280;">نتیجه‌ای یافت نشد.</div>
            {% endif %}
        </div>
    </div>
    <script>
        history.pushState(null, null, location.href);
        window.addEventListener('popstate', () => history.pushState(null, null, location.href));
        document.getElementById('menuToggle').addEventListener('click', () => document.getElementById('sidebar').classList.add('active'));
        document.getElementById('closeSidebar').addEventListener('click', () => document.getElementById('sidebar').classList.remove('active'));

        function performSearch() {
            const q = document.getElementById('searchInput').value.trim();
            const grade = "{{ grade }}";
            let url = '/admin/students/search?q=' + encodeURIComponent(q);
            if (grade) url += '&grade=' + encodeURIComponent(grade);
            window.location.href = url;
        }

        function viewStudentDetails(name, family, nationalId, grade, field) {
            // در اینجا می‌توانید به صفحه جزئیات هدایت کنید
            alert(`نام: ${name} ${family}\nکد ملی: ${nationalId}\nپایه: ${grade}\nرشته: ${field}`);
        }
    </script>
</body>
</html>
    ''', query=query, results=results, grade=grade)

# ========== خروج ==========
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    session.pop('students', None)  # اختیاری: اگر می‌خواهید داده‌ها پاک شوند
    return redirect(url_for('home'))

# ========== صفحات placeholder ==========
@app.route('/login/<role>')
def other_login(role):
    roles = {'parent': 'والدین', 'student': 'دانش آموزان', 'teacher': 'معلمان'}
    title = roles.get(role, 'کاربر')
    return f'''
    <div style="background:#0D0D0D; color:white; font-family:Vazir,sans-serif; padding:30px 20px; text-align:center; direction:rtl; min-height:100vh;">
        <h2 style="color:#9D4EDD; text-shadow:0 0 10px #9D4EDD; font-size:24px;">ورود {title}</h2>
        <p style="margin:20px 0; font-size:18px;">این بخش در حال توسعه است.</p>
        <a href="/" style="color:#9D4EDD; text-decoration:underline; display:inline-block; margin-top:20px; font-size:18px;">بازگشت به صفحه اصلی</a>
    </div>
    '''

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))