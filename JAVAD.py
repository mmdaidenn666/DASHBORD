from flask import Flask, render_template_string, request, session, redirect, url_for, jsonify
import os

app = Flask(__name__)
app.secret_key = 'neon_dabirestan_2025_secure_key'

ADMIN_PASSWORD = "dabirestan012345"
TEACHER_PASSWORD = "dabirjavadol"
PARENT_PASSWORD = "valedein"
STUDENT_PASSWORD = "daneshamozan"

# To enhance security, we'll use a set to track logged-in users by unique identifiers
logged_in_admins = set()
logged_in_teachers = set()
logged_in_parents = set()
logged_in_students = set()

def init_students():
    if 'students' not in session:
        session['students'] = {
            'دهم': {
                'ریاضی': [
                    {'name': 'علی', 'family': 'رضایی', 'national_id': '0012345678', 'student_number': '1001'},
                    {'name': 'محمد', 'family': 'محمدی', 'national_id': '0012345679', 'student_number': '1002'}
                ],
                'تجربی': [
                    {'name': 'حسین', 'family': 'کریمی', 'national_id': '0012345680', 'student_number': '1003'}
                ],
                'انسانی': [
                    {'name': 'رضا', 'family': 'جعفری', 'national_id': '0012345681', 'student_number': '1004'}
                ]
            },
            'یازدهم': {
                'ریاضی': [
                    {'name': 'امیر', 'family': 'احمدی', 'national_id': '0012345682', 'student_number': '1101'}
                ],
                'تجربی': [
                    {'name': 'سجاد', 'family': 'قاسمی', 'national_id': '0012345683', 'student_number': '1102'}
                ],
                'انسانی': []
            },
            'دوازدهم': {
                'ریاضی': [],
                'تجربی': [
                    {'name': 'مهدی', 'family': 'اکبری', 'national_id': '0012345684', 'student_number': '1201'}
                ],
                'انسانی': []
            }
        }
    session.modified = True

# ========== صفحه اصلی ==========
@app.route('/')
def home():
    if session.get('admin'):
        init_students()
        return redirect(url_for('admin_dashboard'))
    if session.get('teacher'):
        return redirect(url_for('teacher_dashboard'))
    if session.get('parent'):
        return redirect(url_for('parent_dashboard'))
    if session.get('student'):
        return redirect(url_for('student_dashboard'))
    return render_template_string('''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
        init_students()
        return redirect(url_for('admin_dashboard'))
    error = None
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        family = request.form.get('family', '').strip()
        role = request.form.get('role', '')
        password = request.form.get('password', '')
        unique_id = f"{name}_{family}_{role}"
        if not all([name, family, role, password]):
            error = "لطفاً تمامی فیلدها را پر کنید."
        elif password != ADMIN_PASSWORD:
            error = "رمز عبور اشتباه است."
        elif unique_id in logged_in_admins:
            error = "این حساب قبلاً وارد شده است."
        else:
            session['admin'] = {'name': name, 'family': family, 'role': role}
            logged_in_admins.add(unique_id)
            init_students()
            session.modified = True
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
    init_students()
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
        .card { background: #1A1A1A; padding: 22px 16px; border-radius: 18px; text-align: center; color: #00C6FF; border: 1px solid #333; cursor: pointer; transition: all 0.3s; font-size: 18px; box-shadow: 0 0 8px rgba(0, 198, 255, 0.3); text-decoration: none; display: block; }
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

# ========== مدیریت دانش‌آموزان - صفحه اصلی ==========
@app.route('/admin/students')
def students_overview():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    init_students()
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
        .card { background: #1A1A1A; padding: 22px 16px; border-radius: 18px; text-align: center; color: #00C6FF; border: 1px solid #333; cursor: pointer; transition: all 0.3s; font-size: 18px; box-shadow: 0 0 8px rgba(0, 198, 255, 0.3); text-decoration: none; display: block; }
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
    init_students()
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
        .back-btn { background: #222; color: #00FF9C; border: 1px solid #00FF9C; border-radius: 50%; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 0 8px rgba(0, 255, 156, 0.5); font-size: 20px; }
        .dashboard { padding: 20px; }
        .dashboard h2 { color: #00FF9C; margin: 20px 0 25px; text-shadow: 0 0 10px #00FF9C; font-size: 26px; text-align: center; }
        .cards-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(clamp(150px, 45vw, 220px), 1fr)); gap: 20px; padding: 0 10px; }
        .card { background: #1A1A1A; padding: 22px 16px; border-radius: 18px; text-align: center; color: #FF3CAC; border: 1px solid #333; cursor: pointer; transition: all 0.3s; font-size: 18px; box-shadow: 0 0 8px rgba(255, 60, 172, 0.3); text-decoration: none; display: block; }
        .card:hover { transform: translateY(-6px); box-shadow: 0 0 16px #FF3CAC, 0 0 24px #FF9E00; background: #222; }
    </style>
</head>
<body>
    <header class="toolbar">
        <button class="back-btn" onclick="window.location.href='/admin/students'"><i class="fas fa-arrow-right"></i></button>
        <div style="color: #00FF9C; font-weight: bold;">{{ grade }}</div>
        <div style="width: 44px;"></div>
    </header>
    <div class="dashboard">
        <h2>{{ grade }}</h2>
        <div class="cards-grid">
            <a href="/admin/students/grade/{{ grade }}/field/ریاضی" class="card">ریاضی</a>
            <a href="/admin/students/grade/{{ grade }}/field/تجربی" class="card">تجربی</a>
            <a href="/admin/students/grade/{{ grade }}/field/انسانی" class="card">انسانی</a>
        </div>
    </div>
</body>
</html>
    ''', grade=grade)

# ========== انتخاب رشته ==========
@app.route('/admin/students/grade/<grade>/field/<field>')
def list_students(grade, field):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    init_students()
    if grade not in ['دهم', 'یازدهم', 'دوازدهم'] or field not in ['ریاضی', 'تجربی', 'انسانی']:
        return "داده نامعتبر", 400
    
    students = session['students'][grade][field]
    count = len(students)
    
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
        .back-btn { background: #222; color: #00FF9C; border: 1px solid #00FF9C; border-radius: 50%; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 0 8px rgba(0, 255, 156, 0.5); font-size: 20px; }
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
        .action-btn { width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: transform 0.3s ease, box-shadow 0.3s ease; }
        .edit-btn { background: #222; color: #00FF9C; border: 1px solid #00FF9C; }
        .delete-btn { background: #222; color: #EF4444; border: 1px solid #EF4444; }
        .action-btn:hover { transform: scale(1.1); box-shadow: 0 0 10px rgba(0, 255, 156, 0.5); }
        .fab { position: fixed; bottom: 20px; right: 20px; width: 60px; height: 60px; border-radius: 50%; background: linear-gradient(135deg, #00C6FF, #00FF9C); display: flex; align-items: center; justify-content: center; color: white; font-size: 24px; box-shadow: 0 4px 12px rgba(0,198,255,0.4); cursor: pointer; z-index: 100; transition: transform 0.3s ease; }
        .fab:hover { transform: rotate(90deg); }
        
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 2000; justify-content: center; align-items: center; opacity: 0; transition: opacity 0.3s ease; }
        .modal.active { opacity: 1; }
        .modal-content { background: #1A1A1A; padding: 25px; border-radius: 20px; width: 90%; max-width: 500px; border: 1px solid #333; transform: scale(0.8); transition: transform 0.3s ease; box-shadow: 0 0 20px rgba(0, 198, 255, 0.5); }
        .modal.active .modal-content { transform: scale(1); }
        .modal-buttons { display: flex; gap: 10px; margin-top: 20px; }
        .modal-input { width: 100%; padding: 12px; background: #222; border: 1px solid #444; border-radius: 10px; color: white; direction: rtl; margin-bottom: 15px; }
    </style>
</head>
<body>
    <header class="toolbar">
        <button class="back-btn" onclick="window.location.href='/admin/students/grade/{{ grade }}'"><i class="fas fa-arrow-right"></i></button>
        <div class="student-count">
            <i class="fas fa-user-graduate"></i>
            <span id="count">{{ count }}</span>
        </div>
        <div style="display:flex; gap:10px;">
            <button class="search-btn" onclick="searchStudents('{{ grade }}')"><i class="fas fa-search"></i></button>
        </div>
    </header>

    <div class="dashboard">
        <h2>{{ grade }} - {{ field }}</h2>
        <div class="student-list" id="studentList">
            {% for student in students %}
            <div class="student-card" onclick="viewStudent({{ loop.index0 }})">
                <div class="student-info">
                    <div class="student-name">{{ student.name }} {{ student.family }}</div>
                    <div class="student-id">کد ملی: {{ student.national_id }}</div>
                </div>
                <div class="student-actions">
                    <div class="action-btn edit-btn" onclick="event.stopPropagation(); editStudent({{ loop.index0 }})"><i class="fas fa-pencil-alt"></i></div>
                    <div class="action-btn delete-btn" onclick="event.stopPropagation(); deleteStudent({{ loop.index0 }})"><i class="fas fa-trash"></i></div>
                </div>
            </div>
            {% endfor %}
            {% if not students %}
            <div style="text-align:center; padding:30px; color:#6B7280;">دانش‌آموزی وجود ندارد.</div>
            {% endif %}
        </div>
    </div>

    <div class="fab" onclick="showAddStudentModal()"><i class="fas fa-plus"></i></div>

    <div class="modal" id="addStudentModal">
        <div class="modal-content">
            <h3 style="text-align:center; margin-bottom:20px; color:#00FF9C;">اضافه کردن دانش‌آموز</h3>
            <div id="formAlert" style="display:none; padding:10px; background:#331111; border:1px solid #EF4444; border-radius:8px; color:#FF6B6B; margin-bottom:15px; text-align:center;"></div>
            
            <input type="text" id="studentName" class="modal-input" placeholder="نام دانش‌آموز (اجباری)">
            <input type="text" id="studentFamily" class="modal-input" placeholder="نام خانوادگی دانش‌آموز (اجباری)">
            <input type="text" id="studentNationalId" class="modal-input" placeholder="کد ملی دانش‌آموز (اجباری)">
            <input type="text" id="studentNumber" class="modal-input" placeholder="شماره دانش‌آموز (اختیاری)">
            <input type="text" id="fatherNumber" class="modal-input" placeholder="شماره پدر (اختیاری)">
            <input type="text" id="motherNumber" class="modal-input" placeholder="شماره مادر (اختیاری)">
            
            <div class="modal-buttons">
                <button style="flex:1; padding:12px; background:#333; border:1px solid #444; border-radius:10px; color:white;" onclick="closeAddStudentModal()">انصراف</button>
                <button style="flex:1; padding:12px; background:linear-gradient(90deg, #00C6FF, #00FF9C); border:none; border-radius:10px; color:#0D0D0D; font-weight:bold;" onclick="submitAddStudent()">تایید</button>
            </div>
        </div>
    </div>

    <div class="modal" id="deleteModal">
        <div class="modal-content">
            <p style="font-size:18px; margin-bottom:20px; text-align:center;">آیا مطمئن هستید می‌خواهید اطلاعات دانش‌آموز را پاک کنید؟</p>
            <div class="modal-buttons">
                <button style="flex:1; padding:12px; background:#333; border:1px solid #444; border-radius:10px; color:white;" onclick="closeDeleteModal()">خیر</button>
                <button style="flex:1; padding:12px; background:linear-gradient(90deg, #EF4444, #FF3CAC); border:none; border-radius:10px; color:white; font-weight:bold;" onclick="confirmDelete()">بله</button>
            </div>
        </div>
    </div>

    <div class="modal" id="viewModal">
        <div class="modal-content">
            <h3 style="text-align:center; margin-bottom:20px; color:#00FF9C;">جزئیات دانش‌آموز</h3>
            <div id="viewContent"></div>
            <button style="width:100%; padding:12px; background:#333; border:1px solid #444; border-radius:10px; color:white; margin-top:20px;" onclick="closeViewModal()">بستن</button>
        </div>
    </div>

    <script>
        const students = {{ students|tojson }};
        let currentDeleteIndex = -1;
        let currentEditIndex = -1;

        function showModal(modalId) {
            const modal = document.getElementById(modalId);
            modal.style.display = 'flex';
            setTimeout(() => modal.classList.add('active'), 10);
        }

        function closeModal(modalId) {
            const modal = document.getElementById(modalId);
            modal.classList.remove('active');
            setTimeout(() => modal.style.display = 'none', 300);
        }

        function showAddStudentModal() {
            document.getElementById('formAlert').style.display = 'none';
            ['studentName', 'studentFamily', 'studentNationalId', 'studentNumber', 'fatherNumber', 'motherNumber'].forEach(id => {
                document.getElementById(id).value = '';
            });
            currentEditIndex = -1;
            showModal('addStudentModal');
        }

        function closeAddStudentModal() {
            closeModal('addStudentModal');
        }

        function submitAddStudent() {
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

            const studentData = {
                name: name,
                family: family,
                national_id: nationalId,
                student_number: studentNumber,
                father_number: fatherNumber,
                mother_number: motherNumber
            };

            const url = '/admin/students/add';
            const data = {
                grade: "{{ grade }}",
                field: "{{ field }}",
                student: studentData
            };

            fetch(url, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            }).then(res => res.json()).then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    showAlert(data.error || 'خطا در عملیات');
                }
            }).catch(error => {
                showAlert('خطا در ارتباط با سرور');
            });
        }

        function editStudent(index) {
            const student = students[index];
            document.getElementById('studentName').value = student.name;
            document.getElementById('studentFamily').value = student.family;
            document.getElementById('studentNationalId').value = student.national_id;
            document.getElementById('studentNumber').value = student.student_number || '';
            document.getElementById('fatherNumber').value = student.father_number || '';
            document.getElementById('motherNumber').value = student.mother_number || '';
            document.getElementById('formAlert').style.display = 'none';
            currentEditIndex = index;
            showModal('addStudentModal');
        }

        function deleteStudent(index) {
            currentDeleteIndex = index;
            showModal('deleteModal');
        }

        function closeDeleteModal() {
            closeModal('deleteModal');
            currentDeleteIndex = -1;
        }

        function confirmDelete() {
            if (currentDeleteIndex === -1) return;
            
            fetch('/admin/students/delete', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    grade: "{{ grade }}",
                    field: "{{ field }}",
                    index: currentDeleteIndex
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
            const student = students[index];
            const content = `
                <div style="border:1px solid #444; padding:15px; border-radius:10px; background:#222;">
                    <div style="margin-bottom:10px;"><strong>نام:</strong> ${student.name}</div>
                    <div style="margin-bottom:10px;"><strong>نام خانوادگی:</strong> ${student.family}</div>
                    <div style="margin-bottom:10px;"><strong>کد ملی:</strong> ${student.national_id}</div>
                    <div style="margin-bottom:10px;"><strong>شماره دانش‌آموز:</strong> ${student.student_number || 'ندارد'}</div>
                    <div style="margin-bottom:10px;"><strong>شماره پدر:</strong> ${student.father_number || 'ندارد'}</div>
                    <div style="margin-bottom:10px;"><strong>شماره مادر:</strong> ${student.mother_number || 'ندارد'}</div>
                </div>
            `;
            document.getElementById('viewContent').innerHTML = content;
            showModal('viewModal');
        }

        function closeViewModal() {
            closeModal('viewModal');
        }

        function showAlert(message) {
            const alertEl = document.getElementById('formAlert');
            alertEl.innerText = message;
            alertEl.style.display = 'block';
        }

        function searchStudents(grade) {
            window.location.href = `/admin/students/search?grade=${grade}`;
        }
    </script>
</body>
</html>
    ''', grade=grade, field=field, students=students, count=count)

# ========== جستجو دانش‌آموزان ==========
@app.route('/admin/students/search', methods=['GET', 'POST'])
def search_students():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    init_students()
    query = request.form.get('query', '') if request.method == 'POST' else ''
    grade = request.args.get('grade', '')
    results = []
    if query:
        for g in session['students']:
            for f in session['students'][g]:
                for s in session['students'][g][f]:
                    if query in s['name'] or query in s['family'] or query in s['national_id']:
                        results.append({**s, 'grade': g, 'field': f})
    return render_template_string('''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>جستجو دانش آموزان</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazir:wght@400;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background: #0D0D0D; color: white; font-family: 'Vazir', sans-serif; padding: 20px; }
        h2 { color: #00FF9C; text-align: center; }
        form { max-width: 500px; margin: 0 auto; }
        input[type="text"] { width: 100%; padding: 10px; margin-bottom: 10px; }
        button { width: 100%; padding: 10px; background: #00C6FF; color: black; border: none; }
        .results { margin-top: 20px; }
        .student-card { background: #1A1A1A; padding: 10px; margin-bottom: 10px; border-radius: 10px; }
    </style>
</head>
<body>
    <h2>جستجو دانش آموزان</h2>
    <form method="POST">
        <input type="text" name="query" placeholder="نام، نام خانوادگی یا کد ملی" value="{{ query }}" required>
        <button type="submit">جستجو</button>
    </form>
    <div class="results">
        {% for result in results %}
        <div class="student-card">
            <p>نام: {{ result.name }} {{ result.family }}</p>
            <p>کد ملی: {{ result.national_id }}</p>
            <p>پایه: {{ result.grade }} - رشته: {{ result.field }}</p>
        </div>
        {% endfor %}
        {% if not results %}
        <p style="text-align:center;">نتیجه‌ای یافت نشد.</p>
        {% endif %}
    </div>
    <a href="/admin/students/grade/{{ grade }}" style="display:block; text-align:center; margin-top:20px;">بازگشت</a>
</body>
</html>
    ''', query=query, results=results, grade=grade)

# ========== API اضافه کردن دانش‌آموز ==========
@app.route('/admin/students/add', methods=['POST'])
def add_student():
    if not session.get('admin'):
        return jsonify(success=False), 403
    
    init_students()
    data = request.get_json()
    grade = data.get('grade')
    field = data.get('field')
    student = data.get('student')
    
    if not all([grade, field, student]):
        return jsonify(success=False, error="داده‌های ناقص")
    
    # بررسی تکرار کد ملی
    for g in session['students']:
        for f in session['students'][g]:
            if any(s['national_id'] == student['national_id'] for s in session['students'][g][f]):
                return jsonify(success=False, error="کد ملی تکراری است.")
    
    session['students'][grade][field].append(student)
    session.modified = True
    return jsonify(success=True)

# ========== API حذف دانش‌آموز ==========
@app.route('/admin/students/delete', methods=['POST'])
def delete_student():
    if not session.get('admin'):
        return jsonify(success=False), 403
    
    init_students()
    data = request.get_json()
    grade = data.get('grade')
    field = data.get('field')
    index = data.get('index')
    
    try:
        session['students'][grade][field].pop(index)
        session.modified = True
        return jsonify(success=True)
    except (IndexError, KeyError):
        return jsonify(success=False, error="دانش‌آموز یافت نشد")

# ========== پروفایل مدیران ==========
@app.route('/admin/profile', methods=['GET', 'POST'])
def admin_profile():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        data = request.get_json()
        field = data.get('field')
        value = data.get('value')
        if field in ['name', 'family', 'role'] and value and value.strip():
            session['admin'][field] = value.strip()
            session.modified = True
            return jsonify(success=True)
        return jsonify(success=False, error="مقدار نامعتبر"), 400
    
    user = session['admin']
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
        .profile-field { display: flex; align-items: center; margin: 22px 0; gap: 15px; flex-wrap: wrap; border-bottom: 1px solid #333; padding-bottom: 20px; }
        .field-label { min-width: 130px; color: #00C6FF; font-size: 18px; }
        .field-value { flex: 1; padding: 12px; background: #222; border-radius: 12px; direction: rtl; font-size: 18px; min-width: 150px; }
        .edit-btn { background: #222; color: #FF3CAC; border: 1px solid #FF3CAC; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 0 8px rgba(255, 60, 172, 0.5); font-size: 16px; transition: all 0.3s; }
        .edit-btn:hover { transform: scale(1.1); }
        .edit-controls { display: flex; gap: 12px; margin-top: 12px; width: 100%; animation: fadeIn 0.3s ease; }
        .btn-ghost { flex: 1; padding: 10px; background: transparent; border: 1px solid #00C6FF; color: #00C6FF; border-radius: 12px; cursor: pointer; font-size: 16px; transition: all 0.3s; }
        .btn-ghost:hover { background: rgba(0, 198, 255, 0.1); }
        .btn-primary { flex: 1; padding: 10px; background: linear-gradient(90deg, #00C6FF, #00FF9C); color: #0D0D0D; border: none; border-radius: 12px; font-weight: bold; font-size: 16px; cursor: pointer; box-shadow: 0 0 10px #00C6FF, 0 0 20px #00FF9C; transition: all 0.3s; }
        .btn-primary:hover { transform: translateY(-2px); }
        .btn-logout { width: 100%; padding: 16px; background: linear-gradient(90deg, #EF4444, #FF3CAC); color: white; border: none; border-radius: 16px; font-size: 18px; margin-top: 30px; cursor: pointer; box-shadow: 0 0 12px #EF4444, 0 0 24px #FF3CAC; transition: all 0.3s; }
        .btn-logout:hover { transform: translateY(-2px); }
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); justify-content: center; align-items: center; z-index: 2000; animation: fadeIn 0.3s ease; }
        .modal-content { background: #1A1A1A; padding: 25px; border-radius: 18px; width: 90%; max-width: 420px; text-align: center; border: 1px solid #FF3CAC; box-shadow: 0 0 25px #FF3CAC; animation: slideIn 0.3s ease; }
        .modal-buttons { display: flex; gap: 15px; justify-content: center; margin-top: 25px; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes slideIn { from { transform: translateY(-20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
    </style>
</head>
<body>
    <header class="toolbar">
        <button class="back-btn" onclick="window.location.href='/admin/dashboard'"><i class="fas fa-arrow-right"></i></button>
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
        let originalValues = {};

        function editField(field, btn) {
            const valueEl = document.getElementById(field + 'Value');
            const currentValue = valueEl.innerText;
            originalValues[field] = currentValue;
            
            btn.style.display = 'none';
            valueEl.innerHTML = '';

            if (field === 'role') {
                const select = document.createElement('select');
                select.style.cssText = 'width: 100%; padding: 10px; background: #222; color: white; border-radius: 10px; border: 1px solid #444; font-size: 18px;';
                
                const options = ['مدیر', 'ناظم', 'معاون'];
                options.forEach(role => {
                    const option = document.createElement('option');
                    option.value = role;
                    option.textContent = role;
                    if (role === currentValue) option.selected = true;
                    select.appendChild(option);
                });
                
                valueEl.appendChild(select);
            } else {
                const input = document.createElement('input');
                input.type = 'text';
                input.value = currentValue;
                input.style.cssText = 'width: 100%; padding: 10px; background: #222; color: white; border-radius: 10px; border: 1px solid #444; direction: rtl; font-size: 18px;';
                valueEl.appendChild(input);
            }

            const controls = document.createElement('div');
            controls.className = 'edit-controls';
            controls.innerHTML = `
                <button class="btn-ghost" onclick="cancelEdit('${field}', this)">انصراف</button>
                <button class="btn-primary" onclick="saveEdit('${field}', this)">تایید</button>
            `;
            
            valueEl.parentNode.appendChild(controls);
        }

        function cancelEdit(field, btn) {
            const controls = btn.parentNode;
            const valueEl = document.getElementById(field + 'Value');
            
            valueEl.innerHTML = originalValues[field];
            controls.remove();
            
            const editBtn = valueEl.nextElementSibling;
            editBtn.style.display = 'flex';
        }

        function saveEdit(field, btn) {
            const controls = btn.parentNode;
            const valueEl = document.getElementById(field + 'Value');
            let newValue;
            
            if (field === 'role') {
                const select = valueEl.querySelector('select');
                newValue = select ? select.value : '';
            } else {
                const input = valueEl.querySelector('input');
                newValue = input ? input.value.trim() : '';
            }

            if (!newValue) {
                alert('مقدار نمی‌تواند خالی باشد.');
                return;
            }

            fetch('/admin/profile', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({field: field, value: newValue})
            }).then(res => res.json()).then(data => {
                if (data.success) {
                    valueEl.innerHTML = newValue;
                    controls.remove();
                    const editBtn = valueEl.nextElementSibling;
                    editBtn.style.display = 'flex';
                } else {
                    alert('خطا در ذخیره‌سازی');
                }
            }).catch(error => {
                alert('خطا در ارتباط با سرور');
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
    ''', user=user)

# ========== ورود معلمان ==========
@app.route('/login/teacher', methods=['GET', 'POST'])
def teacher_login():
    if session.get('teacher'):
        return redirect(url_for('teacher_dashboard'))
    error = None
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        family = request.form.get('family', '').strip()
        num_grades = request.form.get('num_grades', '0')
        grades = [request.form.get(f'grade{i+1}', '') for i in range(int(num_grades))]
        num_fields = request.form.get('num_fields', '0')
        fields = [request.form.get(f'field{i+1}', '') for i in range(int(num_fields))]
        num_lessons = request.form.get('num_lessons', '0')
        lessons = [request.form.get(f'lesson{i+1}', '') for i in range(int(num_lessons))]
        password = request.form.get('password', '')
        unique_id = f"{name}_{family}"
        if not all([name, family, password]):
            error = "لطفاً تمامی فیلدها را پر کنید."
        elif password != TEACHER_PASSWORD:
            error = "رمز عبور اشتباه است."
        elif unique_id in logged_in_teachers:
            error = "این حساب قبلاً وارد شده است."
        else:
            session['teacher'] = {'name': name, 'family': family, 'num_grades': num_grades, 'grades': grades, 'num_fields': num_fields, 'fields': fields, 'num_lessons': num_lessons, 'lessons': lessons}
            logged_in_teachers.add(unique_id)
            session.modified = True
            return redirect(url_for('teacher_dashboard'))
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ورود معلمان</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazir:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        body { background: #0D0D0D; color: white; font-family: 'Vazir', sans-serif; padding: 15px; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .form-container { background: #1A1A1A; padding: 25px; border-radius: 20px; width: 100%; max-width: 500px; box-shadow: 0 0 20px rgba(255, 158, 0, 0.3); border: 1px solid #333; }
        h2 { text-align: center; margin-bottom: 24px; color: #FF3CAC; text-shadow: 0 0 10px #FF3CAC; font-size: 24px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; color: #FF9E00; font-size: 16px; }
        input, select { width: 100%; padding: 14px; background: #222; border: 1px solid #444; border-radius: 12px; color: white; font-size: 16px; direction: rtl; }
        .btn-primary { width: 100%; padding: 14px; background: linear-gradient(90deg, #FF3CAC, #FF9E00); color: #0D0D0D; border: none; border-radius: 14px; font-weight: bold; font-size: 18px; cursor: pointer; box-shadow: 0 0 12px #FF3CAC, 0 0 24px #FF9E00; }
        .alert { padding: 12px; background: #331111; border: 1px solid #EF4444; border-radius: 8px; color: #FF6B6B; text-align: center; margin-bottom: 20px; font-size: 16px; }
        .back-link { display: block; text-align: center; margin-top: 20px; color: #FF3CAC; text-decoration: none; font-size: 16px; }
    </style>
</head>
<body>
    <div class="form-container">
        <h2>ورود معلمان</h2>
        <form method="POST">
            {% if error %}<div class="alert">{{ error }}</div>{% endif %}
            <div class="form-group"><label>نام</label><input type="text" name="name" value="{{ request.form.name or '' }}" required></div>
            <div class="form-group"><label>نام خانوادگی</label><input type="text" name="family" value="{{ request.form.family or '' }}" required></div>
            <div class="form-group"><label>تعداد پایه‌هایی که تدریس می‌کنید</label><select name="num_grades" required onchange="updateFields('grade', this.value)"><option value="0">0</option><option value="1">1</option><option value="2">2</option><option value="3">3</option></select></div>
            <div id="grades"></div>
            <div class="form-group"><label>تعداد رشته‌هایی که تدریس می‌کنید</label><select name="num_fields" required onchange="updateFields('field', this.value)"><option value="0">0</option><option value="1">1</option><option value="2">2</option><option value="3">3</option></select></div>
            <div id="fields"></div>
            <div class="form-group"><label>تعداد درس‌هایی که تدریس می‌کنید</label><select name="num_lessons" required onchange="updateFields('lesson', this.value)"><option value="0">0</option><option value="1">1</option><option value="2">2</option><option value="3">3</option></select></div>
            <div id="lessons"></div>
            <div class="form-group"><label>رمز عبور</label><input type="password" name="password" required></div>
            <button type="submit" class="btn-primary">ورود</button>
        </form>
        <a href="/" class="back-link">بازگشت به صفحه اصلی</a>
    </div>
    <script>
        function updateFields(type, num) {
            const container = document.getElementById(type + 's');
            container.innerHTML = '';
            for (let i = 1; i <= num; i++) {
                const input = document.createElement('input');
                input.type = 'text';
                input.name = type + i;
                input.placeholder = (type === 'grade' ? 'پایه' : type === 'field' ? 'رشته' : 'درس') + ' ' + i;
                input.required = true;
                input.style.marginBottom = '10px';
                container.appendChild(input);
            }
        }
    </script>
</body>
</html>
    ''', error=error)

# ========== درگاه معلمان ==========
@app.route('/teacher/dashboard')
def teacher_dashboard():
    if not session.get('teacher'):
        return redirect(url_for('teacher_login'))
    return render_template_string('''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>درگاه معلمان</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazir:wght@400;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { background: #0D0D0D; color: white; font-family: 'Vazir', sans-serif; }
        .toolbar { display: flex; justify-content: flex-end; padding: 12px 20px; background: #151515; border-bottom: 1px solid #333; }
        .menu-toggle { background: #222; color: #FF9E00; border: 1px solid #FF9E00; border-radius: 50%; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 0 8px rgba(255, 158, 0, 0.5); font-size: 20px; }
        .sidebar { position: fixed; top: 0; right: 0; height: 100%; width: clamp(240px, 80vw, 300px); background: #1A1A1A; border-left: 1px solid #444; transform: translateX(100%); transition: transform 0.4s cubic-bezier(0.68, -0.55, 0.27, 1.55); z-index: 1000; padding-top: 70px; }
        .sidebar.active { transform: translateX(0); }
        .close-btn { position: absolute; top: 20px; left: 20px; background: #EF4444; color: white; width: 34px; height: 34px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; font-weight: bold; font-size: 20px; box-shadow: 0 0 10px #EF4444; }
        .sidebar-btn { display: block; width: calc(100% - 40px); margin: 18px 20px; padding: 16px; text-align: center; background: linear-gradient(90deg, #FF3CAC, #FF9E00); color: #0D0D0D; border: none; border-radius: 14px; text-decoration: none; font-weight: bold; font-size: 18px; box-shadow: 0 0 10px #FF3CAC, 0 0 20px #FF9E00; }
        .dashboard { padding: 20px; }
        .dashboard h2 { color: #FF9E00; margin: 20px 0 25px; text-shadow: 0 0 10px #FF9E00; font-size: 26px; text-align: center; }
        .cards-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(clamp(150px, 45vw, 220px), 1fr)); gap: 20px; padding: 0 10px; }
        .card { background: #1A1A1A; padding: 22px 16px; border-radius: 18px; text-align: center; color: #FF3CAC; border: 1px solid #333; cursor: pointer; transition: all 0.3s; font-size: 18px; box-shadow: 0 0 8px rgba(255, 60, 172, 0.3); text-decoration: none; display: block; }
        .card:hover { transform: translateY(-6px); box-shadow: 0 0 16px #FF3CAC, 0 0 24px #FF9E00; background: #222; }
    </style>
</head>
<body>
    <header class="toolbar">
        <button class="menu-toggle" id="menuToggle"><i class="fas fa-bars"></i></button>
    </header>
    <div class="sidebar" id="sidebar">
        <div class="close-btn" id="closeSidebar">&times;</div>
        <a href="/teacher/dashboard" class="sidebar-btn">صفحه اصلی</a>
        <a href="/teacher/profile" class="sidebar-btn">پروفایل</a>
        <a href="#" class="sidebar-btn">اعلانات</a>
    </div>
    <div class="dashboard">
        <h2>درگاه معلمان</h2>
        <div class="cards-grid">
            <a href="/teacher/attendance" class="card">حضور و غیاب</a>
            <div class="card">مدیریت نمرات</div>
            <div class="card">مدیریت تکالیف</div>
            <div class="card">گزارشات</div>
            <div class="card">لیست دانش آموزان</div>
            <div class="card">آزمایشگاه</div>
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

# ========== حضور و غیاب معلمان ==========
@app.route('/teacher/attendance/grade/<grade>/field/<field>', methods=['GET', 'POST'])
def teacher_attendance_list(grade, field):
    if not session.get('teacher'):
        return redirect(url_for('teacher_login'))
    init_students()
    if grade not in ['دهم', 'یازدهم', 'دوازدهم'] or field not in ['ریاضی', 'تجربی', 'انسانی']:
        return "داده نامعتبر", 400
    
    students = session['students'][grade][field]
    count = len(students)
    
    if request.method == 'POST':
        data = request.get_json()
        day = data.get('day')
        month = data.get('month')
        year = data.get('year')
        weekday = data.get('weekday')
        attendance = data.get('attendance')  # dict of student national_id: 'present' or 'absent'
        teacher = session['teacher']
        message = f"نام معلم: {teacher['name']} {teacher['family']}\nپایه: {grade}\nرشته: {field}\nدرس: {', '.join(teacher['lessons'])}\nتاریخ: {weekday} - {year}/{month}/{day}\n\nغائبین:\n"
        absent = [s for s in students if attendance.get(s['national_id'], '') == 'absent']
        present = [s for s in students if attendance.get(s['national_id'], '') == 'present']
        for s in absent:
            message += f"{s['name']} {s['family']}\n"
        message += "\nحاضرین:\n"
        for s in present:
            message += f"{s['name']} {s['family']}\n"
        # Simulate sending to notifications (for admin and teacher)
        print("Sent to admin and teacher notifications:", message)
        return jsonify(success=True)
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ grade }} - {{ field }} - حضور و غیاب</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazir:wght@400;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { background: #0D0D0D; color: white; font-family: 'Vazir', sans-serif; }
        .toolbar { display: flex; justify-content: space-between; align-items: center; padding: 12px 20px; background: #151515; border-bottom: 1px solid #333; }
        .back-btn { background: #222; color: #FF9E00; border: 1px solid #FF9E00; border-radius: 50%; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 0 8px rgba(255, 158, 0, 0.5); font-size: 20px; }
        .student-count { display: flex; align-items: center; gap: 8px; color: #FF9E00; font-weight: bold; }
        .dashboard { padding: 20px; }
        .dashboard h2 { color: #FF9E00; margin: 20px 0 25px; text-shadow: 0 0 10px #FF9E00; font-size: 26px; text-align: center; }
        .student-list { display: flex; flex-direction: column; gap: 15px; }
        .student-card { background: #1A1A1A; padding: 16px; border-radius: 16px; display: flex; justify-content: space-between; align-items: center; border: 1px solid #333; }
        .student-info { text-align: right; }
        .student-name { font-weight: bold; font-size: 18px; color: #FF3CAC; }
        .student-id { font-size: 14px; color: #6B7280; margin-top: 4px; }
        .student-actions { display: flex; gap: 10px; }
        .action-btn { padding: 8px 12px; border-radius: 8px; cursor: pointer; transition: all 0.2s; }
        .absent-btn { background: #222; color: #EF4444; border: 1px solid #EF4444; }
        .present-btn { background: #222; color: #00FF9C; border: 1px solid #00FF9C; }
        .active { background: linear-gradient(90deg, #EF4444, #FF3CAC); color: white; }
        .present.active { background: linear-gradient(90deg, #00FF9C, #00C6FF); }
        .attendance-summary { display: flex; justify-content: space-between; padding: 10px; background: #151515; margin-bottom: 20px; }
        .absent-count { color: #EF4444; }
        .present-count { color: #00FF9C; }
        .form-buttons { display: flex; flex-direction: column; gap: 10px; padding: 20px; }
        .btn { padding: 12px; border-radius: 10px; cursor: pointer; text-align: center; }
        .submit-btn { background: linear-gradient(90deg, #00C6FF, #00FF9C); color: #0D0D0D; }
        .reset-btn { background: linear-gradient(90deg, #EF4444, #FF3CAC); color: white; }
        
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 2000; justify-content: center; align-items: center; }
        .modal-content { background: #1A1A1A; padding: 25px; border-radius: 20px; width: 90%; max-width: 500px; border: 1px solid #333; }
        .modal-buttons { display: flex; gap: 10px; margin-top: 20px; }
        .modal-input { width: 100%; padding: 12px; background: #222; border: 1px solid #444; border-radius: 10px; color: white; direction: rtl; margin-bottom: 15px; }
    </style>
</head>
<body>
    <header class="toolbar">
        <button class="back-btn" onclick="window.location.href='/teacher/attendance/grade/{{ grade }}'"><i class="fas fa-arrow-right"></i></button>
        <div class="student-count">
            <i class="fas fa-user-graduate"></i>
            <span id="count">{{ count }}</span>
        </div>
        <div style="width: 44px;"></div>
    </header>

    <div class="dashboard">
        <h2>{{ grade }} - {{ field }}</h2>
        <div class="attendance-summary">
            <div class="absent-count">غائب: <span id="absentCount">0</span></div>
            <div class="present-count">حاضر: <span id="presentCount">0</span></div>
        </div>
        <div class="student-list" id="studentList">
            {% for student in students %}
            <div class="student-card" data-national-id="{{ student.national_id }}">
                <div class="student-info">
                    <div class="student-name">{{ student.name }} {{ student.family }}</div>
                    <div class="student-id">کد ملی: {{ student.national_id }}</div>
                </div>
                <div class="student-actions">
                    <div class="action-btn absent-btn" onclick="toggleAttendance(this, 'absent')">غائب</div>
                    <div class="action-btn present-btn" onclick="toggleAttendance(this, 'present')">حاضر</div>
                </div>
            </div>
            {% endfor %}
            {% if not students %}
            <div style="text-align:center; padding:30px; color:#6B7280;">دانش‌آموزی وجود ندارد.</div>
            {% endif %}
        </div>
        <div class="form-buttons">
            <div class="btn submit-btn" onclick="showDateModal()">ارسال فرم حضور و غیاب</div>
            <div class="btn reset-btn" onclick="showResetModal()">پاک کردن انتخاب شدگان</div>
        </div>
    </div>

    <div class="modal" id="dateModal">
        <div class="modal-content">
            <h3 style="text-align:center; margin-bottom:20px; color:#00FF9C;">انتخاب تاریخ</h3>
            <select id="day" class="modal-input" required><option value="">روز</option>{% for i in range(1,32) %}<option value="{{ i }}">{{ i }}</option>{% endfor %}</select>
            <select id="month" class="modal-input" required><option value="">ماه</option>{% for i in range(1,13) %}<option value="{{ i }}">{{ i }}</option>{% endfor %}</select>
            <select id="year" class="modal-input" required><option value="">سال</option>{% for i in range(1404,1451) %}<option value="{{ i }}">{{ i }}</option>{% endfor %}</select>
            <select id="weekday" class="modal-input"><option value="">روز هفته</option><option value="شنبه">شنبه</option><option value="یک‌شنبه">یک‌شنبه</option><option value="دوشنبه">دوشنبه</option><option value="سه‌شنبه">سه‌شنبه</option><option value="چهارشنبه">چهارشنبه</option><option value="پنجشنبه">پنجشنبه</option><option value="جمعه">جمعه</option></select>
            <div class="modal-buttons">
                <button style="flex:1; padding:12px; background:#333; border:1px solid #444; border-radius:10px; color:white;" onclick="closeDateModal()">انصراف</button>
                <button style="flex:1; padding:12px; background:linear-gradient(90deg, #00C6FF, #00FF9C); border:none; border-radius:10px; color:#0D0D0D; font-weight:bold;" onclick="submitAttendance()">تایید</button>
            </div>
        </div>
    </div>

    <div class="modal" id="resetModal">
        <div class="modal-content">
            <p style="font-size:18px; margin-bottom:20px; text-align:center;">آیا مطمئن هستید می‌خواهید انتخاب‌ها را پاک کنید؟</p>
            <div class="modal-buttons">
                <button style="flex:1; padding:12px; background:#333; border:1px solid #444; border-radius:10px; color:white;" onclick="closeResetModal()">خیر</button>
                <button style="flex:1; padding:12px; background:linear-gradient(90deg, #EF4444, #FF3CAC); border:none; border-radius:10px; color:white; font-weight:bold;" onclick="confirmReset()">بله</button>
            </div>
        </div>
    </div>

    <div class="modal" id="confirmSubmitModal">
        <div class="modal-content">
            <p style="font-size:18px; margin-bottom:20px; text-align:center;">آیا مطمئن هستید می‌خواهید فرم را ارسال کنید؟</p>
            <div class="modal-buttons">
                <button style="flex:1; padding:12px; background:#333; border:1px solid #444; border-radius:10px; color:white;" onclick="closeConfirmSubmitModal()">خیر</button>
                <button style="flex:1; padding:12px; background:linear-gradient(90deg, #00C6FF, #00FF9C); border:none; border-radius:10px; color:#0D0D0D; font-weight:bold;" onclick="confirmSubmit()">بله</button>
            </div>
        </div>
    </div>

    <script>
        let attendance = {};
        let absentCount = 0;
        let presentCount = 0;

        function toggleAttendance(btn, type) {
            const card = btn.parentNode.parentNode;
            const nationalId = card.dataset.nationalId;
            const otherBtn = btn.nextElementSibling || btn.previousElementSibling;
            const isActive = btn.classList.contains('active');
            
            if (isActive) {
                btn.classList.remove('active');
                delete attendance[nationalId];
                if (type === 'absent') absentCount--;
                else presentCount--;
            } else {
                if (otherBtn.classList.contains('active')) {
                    otherBtn.classList.remove('active');
                    if (type === 'absent') {
                        presentCount--;
                        absentCount++;
                    } else {
                        absentCount--;
                        presentCount++;
                    }
                } else {
                    if (type === 'absent') absentCount++;
                    else presentCount++;
                }
                btn.classList.add('active');
                attendance[nationalId] = type;
            }
            
            document.getElementById('absentCount').innerText = absentCount;
            document.getElementById('presentCount').innerText = presentCount;
        }

        function showDateModal() {
            if (absentCount + presentCount === 0) {
                alert('لطفاً حضور و غیاب را انجام دهید.');
                return;
            }
            document.getElementById('dateModal').style.display = 'flex';
        }

        function closeDateModal() {
            document.getElementById('dateModal').style.display = 'none';
        }

        function submitAttendance() {
            const day = document.getElementById('day').value;
            const month = document.getElementById('month').value;
            const year = document.getElementById('year').value;
            const weekday = document.getElementById('weekday').value;
            if (!day || !month || !year) {
                alert('لطفاً تمام فیلدهای اجباری را پر کنید.');
                return;
            }
            closeDateModal();
            document.getElementById('confirmSubmitModal').style.display = 'flex';
        }

        function closeConfirmSubmitModal() {
            document.getElementById('confirmSubmitModal').style.display = 'none';
        }

        function confirmSubmit() {
            const day = document.getElementById('day').value;
            const month = document.getElementById('month').value;
            const year = document.getElementById('year').value;
            const weekday = document.getElementById('weekday').value;
            fetch('/teacher/attendance/grade/{{ grade }}/field/{{ field }}', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({day, month, year, weekday, attendance})
            }).then(res => res.json()).then(data => {
                if (data.success) {
                    window.location.href = '/teacher/dashboard';
                } else {
                    alert('خطا در ارسال');
                }
            });
        }

        function showResetModal() {
            document.getElementById('resetModal').style.display = 'flex';
        }

        function closeResetModal() {
            document.getElementById('resetModal').style.display = 'none';
        }

        function confirmReset() {
            document.querySelectorAll('.action-btn.active').forEach(btn => btn.classList.remove('active'));
            attendance = {};
            absentCount = 0;
            presentCount = 0;
            document.getElementById('absentCount').innerText = 0;
            document.getElementById('presentCount').innerText = 0;
            closeResetModal();
        }
    </script>
</body>
</html>
    ''', grade=grade, field=field, students=students, count=count)

# ========== انتخاب پایه برای حضور غیاب ==========
@app.route('/teacher/attendance/grade/<grade>')
def teacher_attendance_select_field(grade):
    if not session.get('teacher'):
        return redirect(url_for('teacher_login'))
    if grade not in ['دهم', 'یازدهم', 'دوازدهم']:
        return "پایه نامعتبر", 400
    return render_template_string('''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ grade }} - حضور و غیاب</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazir:wght@400;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { background: #0D0D0D; color: white; font-family: 'Vazir', sans-serif; }
        .toolbar { display: flex; justify-content: space-between; align-items: center; padding: 12px 20px; background: #151515; border-bottom: 1px solid #333; }
        .back-btn { background: #222; color: #FF9E00; border: 1px solid #FF9E00; border-radius: 50%; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 0 8px rgba(255, 158, 0, 0.5); font-size: 20px; }
        .dashboard { padding: 20px; }
        .dashboard h2 { color: #FF9E00; margin: 20px 0 25px; text-shadow: 0 0 10px #FF9E00; font-size: 26px; text-align: center; }
        .cards-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(clamp(150px, 45vw, 220px), 1fr)); gap: 20px; padding: 0 10px; }
        .card { background: #1A1A1A; padding: 22px 16px; border-radius: 18px; text-align: center; color: #FF3CAC; border: 1px solid #333; cursor: pointer; transition: all 0.3s; font-size: 18px; box-shadow: 0 0 8px rgba(255, 60, 172, 0.3); text-decoration: none; display: block; }
        .card:hover { transform: translateY(-6px); box-shadow: 0 0 16px #FF3CAC, 0 0 24px #FF9E00; background: #222; }
    </style>
</head>
<body>
    <header class="toolbar">
        <button class="back-btn" onclick="window.location.href='/teacher/attendance'"><i class="fas fa-arrow-right"></i></button>
        <div style="color: #FF9E00; font-weight: bold;">{{ grade }}</div>
        <div style="width: 44px;"></div>
    </header>
    <div class="dashboard">
        <h2>{{ grade }}</h2>
        <div class="cards-grid">
            <a href="/teacher/attendance/grade/{{ grade }}/field/ریاضی" class="card">ریاضی</a>
            <a href="/teacher/attendance/grade/{{ grade }}/field/تجربی" class="card">تجربی</a>
            <a href="/teacher/attendance/grade/{{ grade }}/field/انسانی" class="card">انسانی</a>
        </div>
    </div>
</body>
</html>
    ''', grade=grade)

# ========== صفحه اصلی حضور غیاب ==========
@app.route('/teacher/attendance')
def teacher_attendance_overview():
    if not session.get('teacher'):
        return redirect(url_for('teacher_login'))
    return render_template_string('''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>حضور و غیاب</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazir:wght@400;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { background: #0D0D0D; color: white; font-family: 'Vazir', sans-serif; }
        .toolbar { display: flex; justify-content: space-between; align-items: center; padding: 12px 20px; background: #151515; border-bottom: 1px solid #333; }
        .back-btn { background: #222; color: #FF9E00; border: 1px solid #FF9E00; border-radius: 50%; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 0 8px rgba(255, 158, 0, 0.5); font-size: 20px; }
        .dashboard { padding: 20px; }
        .dashboard h2 { color: #FF9E00; margin: 20px 0 25px; text-shadow: 0 0 10px #FF9E00; font-size: 26px; text-align: center; }
        .cards-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(clamp(150px, 45vw, 220px), 1fr)); gap: 20px; padding: 0 10px; }
        .card { background: #1A1A1A; padding: 22px 16px; border-radius: 18px; text-align: center; color: #FF3CAC; border: 1px solid #333; cursor: pointer; transition: all 0.3s; font-size: 18px; box-shadow: 0 0 8px rgba(255, 60, 172, 0.3); text-decoration: none; display: block; }
        .card:hover { transform: translateY(-6px); box-shadow: 0 0 16px #FF3CAC, 0 0 24px #FF9E00; background: #222; }
    </style>
</head>
<body>
    <header class="toolbar">
        <button class="back-btn" onclick="window.location.href='/teacher/dashboard'"><i class="fas fa-arrow-right"></i></button>
        <div style="color: #FF9E00; font-weight: bold;">حضور و غیاب</div>
        <div style="width: 44px;"></div>
    </header>
    <div class="dashboard">
        <h2>حضور و غیاب</h2>
        <div class="cards-grid">
            <a href="/teacher/attendance/grade/دهم" class="card">پایه دهم</a>
            <a href="/teacher/attendance/grade/یازدهم" class="card">پایه یازدهم</a>
            <a href="/teacher/attendance/grade/دوازدهم" class="card">پایه دوازدهم</a>
        </div>
    </div>
</body>
</html>
    ''')

# ========== پروفایل معلمان ==========
@app.route('/teacher/profile', methods=['GET', 'POST'])
def teacher_profile():
    if not session.get('teacher'):
        return redirect(url_for('teacher_login'))
    
    if request.method == 'POST':
        data = request.get_json()
        field = data.get('field')
        value = data.get('value')
        if field in ['name', 'family', 'num_grades', 'num_fields', 'num_lessons']:
            session['teacher'][field] = value
            if field == 'num_grades':
                session['teacher']['grades'] = [''] * int(value)
            elif field == 'num_fields':
                session['teacher']['fields'] = [''] * int(value)
            elif field == 'num_lessons':
                session['teacher']['lessons'] = [''] * int(value)
        elif field.startswith('grade') or field.startswith('field') or field.startswith('lesson'):
            index = int(field[-1]) - 1
            key = field[:-1] + 's'
            session['teacher'][key][index] = value
        session.modified = True
        return jsonify(success=True)
    
    user = session['teacher']
    return render_template_string('''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>پروفایل معلم</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazir:wght@400;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background: #0D0D0D; color: white; font-family: 'Vazir', sans-serif; padding: 15px; }
        .toolbar { display: flex; justify-content: flex-end; padding: 12px 20px; background: #151515; border-bottom: 1px solid #333; }
        .back-btn { background: #222; color: #FF9E00; border: 1px solid #FF9E00; border-radius: 50%; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 0 8px rgba(255, 158, 0, 0.5); font-size: 20px; }
        .container { max-width: 600px; margin: 25px auto; background: #1A1A1A; padding: 25px; border-radius: 20px; border: 1px solid #333; box-shadow: 0 0 20px rgba(255, 158, 0, 0.2); }
        h2 { text-align: center; margin-bottom: 25px; color: #FF9E00; text-shadow: 0 0 10px #FF9E00; font-size: 24px; }
        .profile-field { display: flex; align-items: center; margin: 22px 0; gap: 15px; flex-wrap: wrap; border-bottom: 1px solid #333; padding-bottom: 20px; }
        .field-label { min-width: 130px; color: #FF3CAC; font-size: 18px; }
        .field-value { flex: 1; padding: 12px; background: #222; border-radius: 12px; direction: rtl; font-size: 18px; min-width: 150px; }
        .edit-btn { background: #222; color: #FF3CAC; border: 1px solid #FF3CAC; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 0 8px rgba(255, 60, 172, 0.5); font-size: 16px; transition: all 0.3s; }
        .edit-btn:hover { transform: scale(1.1); }
        .edit-controls { display: flex; gap: 12px; margin-top: 12px; width: 100%; animation: fadeIn 0.3s ease; }
        .btn-ghost { flex: 1; padding: 10px; background: transparent; border: 1px solid #FF3CAC; color: #FF3CAC; border-radius: 12px; cursor: pointer; font-size: 16px; transition: all 0.3s; }
        .btn-ghost:hover { background: rgba(255, 60, 172, 0.1); }
        .btn-primary { flex: 1; padding: 10px; background: linear-gradient(90deg, #FF3CAC, #FF9E00); color: #0D0D0D; border: none; border-radius: 12px; font-weight: bold; font-size: 16px; cursor: pointer; box-shadow: 0 0 10px #FF3CAC, 0 0 20px #FF9E00; transition: all 0.3s; }
        .btn-primary:hover { transform: translateY(-2px); }
        .btn-logout { width: 100%; padding: 16px; background: linear-gradient(90deg, #EF4444, #FF3CAC); color: white; border: none; border-radius: 16px; font-size: 18px; margin-top: 30px; cursor: pointer; box-shadow: 0 0 12px #EF4444, 0 0 24px #FF3CAC; transition: all 0.3s; }
        .btn-logout:hover { transform: translateY(-2px); }
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); justify-content: center; align-items: center; z-index: 2000; animation: fadeIn 0.3s ease; }
        .modal-content { background: #1A1A1A; padding: 25px; border-radius: 18px; width: 90%; max-width: 420px; text-align: center; border: 1px solid #FF3CAC; box-shadow: 0 0 25px #FF3CAC; animation: slideIn 0.3s ease; }
        .modal-buttons { display: flex; gap: 15px; justify-content: center; margin-top: 25px; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes slideIn { from { transform: translateY(-20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
    </style>
</head>
<body>
    <header class="toolbar">
        <button class="back-btn" onclick="window.location.href='/teacher/dashboard'"><i class="fas fa-arrow-right"></i></button>
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
            <div class="field-label">تعداد پایه‌ها:</div>
            <div class="field-value" id="numGradesValue">{{ user.num_grades }}</div>
            <button class="edit-btn" onclick="editField('num_grades', this)"><i class="fas fa-pencil-alt"></i></button>
        </div>
        
        {% for i in range(user.num_grades | int) %}
        <div class="profile-field">
            <div class="field-label">پایه {{ loop.index }}:</div>
            <div class="field-value" id="grade{{ loop.index }}Value">{{ user.grades[loop.index-1] }}</div>
            <button class="edit-btn" onclick="editField('grade{{ loop.index }}', this)"><i class="fas fa-pencil-alt"></i></button>
        </div>
        {% endfor %}
        
        <div class="profile-field">
            <div class="field-label">تعداد رشته‌ها:</div>
            <div class="field-value" id="numFieldsValue">{{ user.num_fields }}</div>
            <button class="edit-btn" onclick="editField('num_fields', this)"><i class="fas fa-pencil-alt"></i></button>
        </div>
        
        {% for i in range(user.num_fields | int) %}
        <div class="profile-field">
            <div class="field-label">رشته {{ loop.index }}:</div>
            <div class="field-value" id="field{{ loop.index }}Value">{{ user.fields[loop.index-1] }}</div>
            <button class="edit-btn" onclick="editField('field{{ loop.index }}', this)"><i class="fas fa-pencil-alt"></i></button>
        </div>
        {% endfor %}
        
        <div class="profile-field">
            <div class="field-label">تعداد درس‌ها:</div>
            <div class="field-value" id="numLessonsValue">{{ user.num_lessons }}</div>
            <button class="edit-btn" onclick="editField('num_lessons', this)"><i class="fas fa-pencil-alt"></i></button>
        </div>
        
        {% for i in range(user.num_lessons | int) %}
        <div class="profile-field">
            <div class="field-label">درس {{ loop.index }}:</div>
            <div class="field-value" id="lesson{{ loop.index }}Value">{{ user.lessons[loop.index-1] }}</div>
            <button class="edit-btn" onclick="editField('lesson{{ loop.index }}', this)"><i class="fas fa-pencil-alt"></i></button>
        </div>
        {% endfor %}
        
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
        let originalValues = {};

        function editField(field, btn) {
            const valueEl = document.getElementById(field + 'Value');
            const currentValue = valueEl.innerText;
            originalValues[field] = currentValue;
            
            btn.style.display = 'none';
            valueEl.innerHTML = '';

            const isNum = field.startsWith('num');
            if (isNum) {
                const select = document.createElement('select');
                select.style.cssText = 'width: 100%; padding: 10px; background: #222; color: white; border-radius: 10px; border: 1px solid #444; font-size: 18px;';
                for (let i = 0; i <= 3; i++) {
                    const option = document.createElement('option');
                    option.value = i;
                    option.textContent = i;
                    if (i == currentValue) option.selected = true;
                    select.appendChild(option);
                }
                valueEl.appendChild(select);
            } else {
                const input = document.createElement('input');
                input.type = 'text';
                input.value = currentValue;
                input.style.cssText = 'width: 100%; padding: 10px; background: #222; color: white; border-radius: 10px; border: 1px solid #444; direction: rtl; font-size: 18px;';
                valueEl.appendChild(input);
            }

            const controls = document.createElement('div');
            controls.className = 'edit-controls';
            controls.innerHTML = `
                <button class="btn-ghost" onclick="cancelEdit('${field}', this)">انصراف</button>
                <button class="btn-primary" onclick="saveEdit('${field}', this)">تایید</button>
            `;
            
            valueEl.parentNode.appendChild(controls);
        }

        function cancelEdit(field, btn) {
            const controls = btn.parentNode;
            const valueEl = document.getElementById(field + 'Value');
            
            valueEl.innerHTML = originalValues[field];
            controls.remove();
            
            const editBtn = valueEl.nextElementSibling;
            editBtn.style.display = 'flex';
        }

        function saveEdit(field, btn) {
            const controls = btn.parentNode;
            const valueEl = document.getElementById(field + 'Value');
            let newValue;
            
            const input = valueEl.querySelector('input') || valueEl.querySelector('select');
            newValue = input ? input.value.trim() : '';
            

            if (!newValue) {
                alert('مقدار نمی‌تواند خالی باشد.');
                return;
            }

            fetch('/teacher/profile', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({field: field, value: newValue})
            }).then(res => res.json()).then(data => {
                if (data.success) {
                    valueEl.innerHTML = newValue;
                    controls.remove();
                    const editBtn = valueEl.nextElementSibling;
                    editBtn.style.display = 'flex';
                    if (field.startsWith('num')) {
                        location.reload();  // Reload to update fields
                    }
                } else {
                    alert('خطا در ذخیره‌سازی');
                }
            }).catch(error => {
                alert('خطا در ارتباط با سرور');
            });
        }

        function showLogoutModal() { 
            document.getElementById('logoutModal').style.display = 'flex'; 
        }
        
        function closeLogout() { 
            document.getElementById('logoutModal').style.display = 'none'; 
        }
        
        function logout() { 
            window.location.href = '/teacher/logout'; 
        }
    </script>
</body>
</html>
    ''', user=user)

# ========== ورود والدین ==========
@app.route('/login/parent', methods=['GET', 'POST'])
def parent_login():
    if session.get('parent'):
        return redirect(url_for('parent_dashboard'))
    error = None
    init_students()
    students_data = []
    for grade in session['students']:
        for field in session['students'][grade]:
            for student in session['students'][grade][field]:
                students_data.append(student)
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        family = request.form.get('family', '').strip()
        grade = request.form.get('grade', '')
        field = request.form.get('field', '')
        child1 = request.form.get('child1', '')
        child2 = request.form.get('child2', '')
        password = request.form.get('password', '')
        unique_id = f"{name}_{family}_{child1}_{child2}"
        if not all([name, family, grade, field, password]):
            error = "لطفاً تمامی فیلدها را پر کنید."
        elif password != PARENT_PASSWORD:
            error = "رمز عبور اشتباه است."
        elif unique_id in logged_in_parents:
            error = "این حساب قبلاً وارد شده است."
        else:
            session['parent'] = {'name': name, 'family': family, 'grade': grade, 'field': field, 'child1': child1, 'child2': child2}
            logged_in_parents.add(unique_id)
            session.modified = True
            return redirect(url_for('parent_dashboard'))
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ورود والدین</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazir:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        body { background: #0D0D0D; color: white; font-family: 'Vazir', sans-serif; padding: 15px; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .form-container { background: #1A1A1A; padding: 25px; border-radius: 20px; width: 100%; max-width: 500px; box-shadow: 0 0 20px rgba(157, 78, 221, 0.3); border: 1px solid #333; }
        h2 { text-align: center; margin-bottom: 24px; color: #9D4EDD; text-shadow: 0 0 10px #9D4EDD; font-size: 24px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; color: #00C6FF; font-size: 16px; }
        input, select { width: 100%; padding: 14px; background: #222; border: 1px solid #444; border-radius: 12px; color: white; font-size: 16px; direction: rtl; }
        .btn-primary { width: 100%; padding: 14px; background: linear-gradient(90deg, #9D4EDD, #00C6FF); color: #0D0D0D; border: none; border-radius: 14px; font-weight: bold; font-size: 18px; cursor: pointer; box-shadow: 0 0 12px #9D4EDD, 0 0 24px #00C6FF; }
        .alert { padding: 12px; background: #331111; border: 1px solid #EF4444; border-radius: 8px; color: #FF6B6B; text-align: center; margin-bottom: 20px; font-size: 16px; }
        .back-link { display: block; text-align: center; margin-top: 20px; color: #9D4EDD; text-decoration: none; font-size: 16px; }
        select:disabled { background: #333; color: #666; }
    </style>
</head>
<body>
    <div class="form-container">
        <h2>ورود والدین</h2>
        <form method="POST" id="parentForm">
            {% if error %}<div class="alert">{{ error }}</div>{% endif %}
            <div class="form-group"><label>نام</label><input type="text" name="name" value="{{ request.form.name or '' }}" required></div>
            <div class="form-group"><label>نام خانوادگی</label><input type="text" name="family" value="{{ request.form.family or '' }}" required></div>
            <div class="form-group">
                <label>پایه فرزند</label>
                <select name="grade" id="gradeSelect" required onchange="updateFields()">
                    <option value="">انتخاب کنید...</option>
                    <option value="دهم" {{ 'selected' if request.form.grade == 'دهم' }}>دهم</option>
                    <option value="یازدهم" {{ 'selected' if request.form.grade == 'یازدهم' }}>یازدهم</option>
                    <option value="دوازدهم" {{ 'selected' if request.form.grade == 'دوازدهم' }}>دوازدهم</option>
                </select>
            </div>
            <div class="form-group">
                <label>رشته فرزند</label>
                <select name="field" id="fieldSelect" disabled required onchange="updateStudents()">
                    <option value="">انتخاب کنید...</option>
                    <option value="ریاضی" {{ 'selected' if request.form.field == 'ریاضی' }}>ریاضی</option>
                    <option value="تجربی" {{ 'selected' if request.form.field == 'تجربی' }}>تجربی</option>
                    <option value="انسانی" {{ 'selected' if request.form.field == 'انسانی' }}>انسانی</option>
                </select>
            </div>
            <div class="form-group">
                <label>فرزند اول</label>
                <select name="child1" id="child1Select" disabled>
                    <option value="">انتخاب کنید...</option>
                </select>
            </div>
            <div class="form-group">
                <label>فرزند دوم (اختیاری)</label>
                <select name="child2" id="child2Select" disabled>
                    <option value="">انتخاب کنید...</option>
                </select>
            </div>
            <div class="form-group"><label>رمز عبور</label><input type="password" name="password" required></div>
            <button type="submit" class="btn-primary">ورود</button>
        </form>
        <a href="/" class="back-link">بازگشت به صفحه اصلی</a>
    </div>
    <script>
        const students = {{ students_data|tojson }};
        
        function updateFields() {
            const gradeSelect = document.getElementById('gradeSelect');
            const fieldSelect = document.getElementById('fieldSelect');
            const child1Select = document.getElementById('child1Select');
            const child2Select = document.getElementById('child2Select');
            
            fieldSelect.disabled = !gradeSelect.value;
            child1Select.disabled = true;
            child2Select.disabled = true;
        }
        
        function updateStudents() {
            const grade = document.getElementById('gradeSelect').value;
            const field = document.getElementById('fieldSelect').value;
            const child1Select = document.getElementById('child1Select');
            const child2Select = document.getElementById('child2Select');
            
            child1Select.innerHTML = '<option value="">انتخاب کنید...</option>';
            child2Select.innerHTML = '<option value="">انتخاب کنید...</option>';
            
            if (grade && field) {
                const filteredStudents = students.filter(s => s.grade === grade && s.field === field);
                filteredStudents.forEach(student => {
                    const option1 = document.createElement('option');
                    option1.value = student.name + '|' + student.family + '|' + student.national_id;
                    option1.textContent = student.name + ' ' + student.family + ' (کد: ' + student.national_id + ')';
                    child1Select.appendChild(option1);
                    
                    const option2 = document.createElement('option');
                    option2.value = student.name + '|' + student.family + '|' + student.national_id;
                    option2.textContent = student.name + ' ' + student.family + ' (کد: ' + student.national_id + ')';
                    child2Select.appendChild(option2);
                });
                
                child1Select.disabled = false;
                child2Select.disabled = false;
            }
        }
        
        document.addEventListener('DOMContentLoaded', function() {
            updateFields();
            {% if request.form.grade %}
            updateStudents();
            {% endif %}
        });
    </script>
</body>
</html>
    ''', error=error, students_data=students_data)

# ========== درگاه والدین ==========
@app.route('/parent/dashboard')
def parent_dashboard():
    if not session.get('parent'):
        return redirect(url_for('parent_login'))
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>درگاه والدین</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazir:wght@400;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { background: #0D0D0D; color: white; font-family: 'Vazir', sans-serif; }
        .toolbar { display: flex; justify-content: flex-end; padding: 12px 20px; background: #151515; border-bottom: 1px solid #333; }
        .menu-toggle { 
            background: #222; 
            color: #9D4EDD; 
            border: 1px solid #9D4EDD; 
            border-radius: 4px; 
            width: 44px; 
            height: 44px; 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            justify-content: center; 
            cursor: pointer; 
            box-shadow: 0 0 8px rgba(157, 78, 221, 0.5); 
            gap: 3px;
            padding: 8px;
        }
        .menu-line {
            width: 20px;
            height: 2px;
            background: #9D4EDD;
            border-radius: 1px;
        }
        .sidebar { 
            position: fixed; 
            top: 0; 
            right: -100%; 
            height: 100%; 
            width: clamp(240px, 80vw, 300px); 
            background: #1A1A1A; 
            border-left: 1px solid #444; 
            transition: right 0.4s cubic-bezier(0.68, -0.55, 0.27, 1.55); 
            z-index: 1000; 
            padding-top: 70px; 
        }
        .sidebar.active { right: 0; }
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
            background: linear-gradient(90deg, #9D4EDD, #00C6FF); 
            color: #0D0D0D; 
            border: none; 
            border-radius: 14px; 
            text-decoration: none; 
            font-weight: bold; 
            font-size: 18px; 
            box-shadow: 0 0 10px #9D4EDD, 0 0 20px #00C6FF; 
            transition: all 0.3s;
        }
        .sidebar-btn:hover { transform: translateY(-2px); }
        .dashboard { padding: 20px; }
        .dashboard h2 { color: #9D4EDD; margin: 20px 0 25px; text-shadow: 0 0 10px #9D4EDD; font-size: 26px; text-align: center; }
        .cards-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(clamp(150px, 45vw, 220px), 1fr)); gap: 20px; padding: 0 10px; }
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
            animation: cardAppear 0.6s ease;
        }
        .card:hover { 
            transform: translateY(-6px) scale(1.05); 
            box-shadow: 0 0 20px #00C6FF, 0 0 30px #9D4EDD; 
            background: #222; 
        }
        @keyframes cardAppear {
            from { 
                opacity: 0; 
                transform: translateY(20px) scale(0.9); 
            }
            to { 
                opacity: 1; 
                transform: translateY(0) scale(1); 
            }
        }
    </style>
</head>
<body>
    <header class="toolbar">
        <button class="menu-toggle" id="menuToggle">
            <div class="menu-line"></div>
            <div class="menu-line"></div>
            <div class="menu-line"></div>
        </button>
    </header>
    
    <div class="sidebar" id="sidebar">
        <div class="close-btn" id="closeSidebar">&times;</div>
        <a href="/parent/dashboard" class="sidebar-btn">صفحه اصلی</a>
        <a href="/parent/profile" class="sidebar-btn">پروفایل</a>
        <a href="#" class="sidebar-btn">اعلانات</a>
    </div>
    
    <div class="dashboard">
        <h2>درگاه والدین</h2>
        <div class="cards-grid">
            <div class="card" style="animation-delay: 0.1s">حضور فرزندم در دبیرستان</div>
            <div class="card" style="animation-delay: 0.2s">نمرات فرزندم</div>
            <div class="card" style="animation-delay: 0.3s">تکالیف و امتحان فرزندم</div>
            <div class="card" style="animation-delay: 0.4s">کارنامه فرزندم</div>
            <div class="card" style="animation-delay: 0.5s">گزارش</div>
            <div class="card" style="animation-delay: 0.6s">لیست مدیران</div>
            <div class="card" style="animation-delay: 0.7s">لیست معلمان</div>
            <div class="card" style="animation-delay: 0.8s">آزمایشگاه علوم</div>
        </div>
    </div>

    <script>
        history.pushState(null, null, location.href);
        window.addEventListener('popstate', () => history.pushState(null, null, location.href));
        
        document.getElementById('menuToggle').addEventListener('click', function() {
            document.getElementById('sidebar').classList.add('active');
        });
        
        document.getElementById('closeSidebar').addEventListener('click', function() {
            document.getElementById('sidebar').classList.remove('active');
        });
        
        document.addEventListener('click', function(event) {
            const sidebar = document.getElementById('sidebar');
            const menuToggle = document.getElementById('menuToggle');
            if (sidebar.classList.contains('active') && 
                !sidebar.contains(event.target) && 
                !menuToggle.contains(event.target)) {
                sidebar.classList.remove('active');
            }
        });
    </script>
</body>
</html>
    ''')

# ========== پروفایل والدین ==========
@app.route('/parent/profile', methods=['GET', 'POST'])
def parent_profile():
    if not session.get('parent'):
        return redirect(url_for('parent_login'))
    
    if request.method == 'POST':
        data = request.get_json()
        field = data.get('field')
        value = data.get('value')
        if field in ['name', 'family', 'grade', 'field', 'child1', 'child2'] and value:
            session['parent'][field] = value
            session.modified = True
            return jsonify(success=True)
        return jsonify(success=False, error="مقدار نامعتبر"), 400
    
    user = session['parent']
    child1_display = user['child1'].split('|')[0] + ' ' + user['child1'].split('|')[1] if user['child1'] else 'ندارد'
    child2_display = user['child2'].split('|')[0] + ' ' + user['child2'].split('|')[1] if user['child2'] else 'ندارد'
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>پروفایل والدین</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazir:wght@400;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background: #0D0D0D; color: white; font-family: 'Vazir', sans-serif; padding: 15px; }
        .toolbar { display: flex; justify-content: flex-end; padding: 12px 20px; background: #151515; border-bottom: 1px solid #333; }
        .back-btn { background: #222; color: #9D4EDD; border: 1px solid #9D4EDD; border-radius: 50%; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 0 8px rgba(157, 78, 221, 0.5); font-size: 20px; }
        .container { max-width: 600px; margin: 25px auto; background: #1A1A1A; padding: 25px; border-radius: 20px; border: 1px solid #333; box-shadow: 0 0 20px rgba(157, 78, 221, 0.2); }
        h2 { text-align: center; margin-bottom: 25px; color: #9D4EDD; text-shadow: 0 0 10px #9D4EDD; font-size: 24px; }
        .profile-field { display: flex; align-items: center; margin: 22px 0; gap: 15px; flex-wrap: wrap; border-bottom: 1px solid #333; padding-bottom: 20px; }
        .field-label { min-width: 140px; color: #00C6FF; font-size: 18px; }
        .field-value { flex: 1; padding: 12px; background: #222; border-radius: 12px; direction: rtl; font-size: 18px; min-width: 150px; }
        .edit-btn { background: #222; color: #9D4EDD; border: 1px solid #9D4EDD; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 0 8px rgba(157, 78, 221, 0.5); font-size: 16px; transition: all 0.3s; }
        .edit-btn:hover { transform: scale(1.1); }
        .edit-controls { display: flex; gap: 12px; margin-top: 12px; width: 100%; animation: fadeIn 0.3s ease; }
        .btn-ghost { flex: 1; padding: 10px; background: transparent; border: 1px solid #9D4EDD; color: #9D4EDD; border-radius: 12px; cursor: pointer; font-size: 16px; transition: all 0.3s; }
        .btn-ghost:hover { background: rgba(157, 78, 221, 0.1); }
        .btn-primary { flex: 1; padding: 10px; background: linear-gradient(90deg, #9D4EDD, #00C6FF); color: #0D0D0D; border: none; border-radius: 12px; font-weight: bold; font-size: 16px; cursor: pointer; box-shadow: 0 0 10px #9D4EDD, 0 0 20px #00C6FF; transition: all 0.3s; }
        .btn-primary:hover { transform: translateY(-2px); }
        .btn-logout { width: 100%; padding: 16px; background: linear-gradient(90deg, #EF4444, #FF3CAC); color: white; border: none; border-radius: 16px; font-size: 18px; margin-top: 30px; cursor: pointer; box-shadow: 0 0 12px #EF4444, 0 0 24px #FF3CAC; transition: all 0.3s; }
        .btn-logout:hover { transform: translateY(-2px); }
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); justify-content: center; align-items: center; z-index: 2000; animation: fadeIn 0.3s ease; }
        .modal-content { background: #1A1A1A; padding: 25px; border-radius: 18px; width: 90%; max-width: 420px; text-align: center; border: 1px solid #FF3CAC; box-shadow: 0 0 25px #FF3CAC; animation: slideIn 0.3s ease; }
        .modal-buttons { display: flex; gap: 15px; justify-content: center; margin-top: 25px; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes slideIn { from { transform: translateY(-20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
    </style>
</head>
<body>
    <header class="toolbar">
        <button class="back-btn" onclick="window.location.href='/parent/dashboard'"><i class="fas fa-arrow-right"></i></button>
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
            <div class="field-value">والدین</div>
            <span style="color:#6B7280; font-size:14px;">(ثابت)</span>
        </div>
        
        <div class="profile-field">
            <div class="field-label">پایه انتخاب شده فرزند:</div>
            <div class="field-value" id="gradeValue">{{ user.grade }}</div>
            <button class="edit-btn" onclick="editField('grade', this)"><i class="fas fa-pencil-alt"></i></button>
        </div>
        
        <div class="profile-field">
            <div class="field-label">رشته انتخاب شده فرزند:</div>
            <div class="field-value" id="fieldValue">{{ user.field }}</div>
            <button class="edit-btn" onclick="editField('field', this)"><i class="fas fa-pencil-alt"></i></button>
        </div>
        
        <div class="profile-field">
            <div class="field-label">فرزند اول انتخاب شده:</div>
            <div class="field-value" id="child1Value">{{ child1_display }}</div>
            <button class="edit-btn" onclick="editField('child1', this)"><i class="fas fa-pencil-alt"></i></button>
        </div>
        
        <div class="profile-field">
            <div class="field-label">فرزند دوم انتخاب شده:</div>
            <div class="field-value" id="child2Value">{{ child2_display }}</div>
            <button class="edit-btn" onclick="editField('child2', this)"><i class="fas fa-pencil-alt"></i></button>
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
        let originalValues = {};

        function editField(field, btn) {
            const valueEl = document.getElementById(field + 'Value');
            const currentValue = valueEl.innerText;
            originalValues[field] = currentValue;
            
            btn.style.display = 'none';
            valueEl.innerHTML = '';

            if (field === 'grade') {
                const select = document.createElement('select');
                select.style.cssText = 'width: 100%; padding: 10px; background: #222; color: white; border-radius: 10px; border: 1px solid #444; font-size: 18px;';
                
                const options = ['دهم', 'یازدهم', 'دوازدهم'];
                options.forEach(opt => {
                    const option = document.createElement('option');
                    option.value = opt;
                    option.textContent = opt;
                    if (opt === currentValue) option.selected = true;
                    select.appendChild(option);
                });
                valueEl.appendChild(select);
                
            } else if (field === 'field') {
                const select = document.createElement('select');
                select.style.cssText = 'width: 100%; padding: 10px; background: #222; color: white; border-radius: 10px; border: 1px solid #444; font-size: 18px;';
                
                const options = ['ریاضی', 'تجربی', 'انسانی'];
                options.forEach(opt => {
                    const option = document.createElement('option');
                    option.value = opt;
                    option.textContent = opt;
                    if (opt === currentValue) option.selected = true;
                    select.appendChild(option);
                });
                valueEl.appendChild(select);
                
            } else {
                const input = document.createElement('input');
                input.type = 'text';
                input.value = currentValue;
                input.style.cssText = 'width: 100%; padding: 10px; background: #222; color: white; border-radius: 10px; border: 1px solid #444; direction: rtl; font-size: 18px;';
                valueEl.appendChild(input);
            }

            const controls = document.createElement('div');
            controls.className = 'edit-controls';
            controls.innerHTML = `
                <button class="btn-ghost" onclick="cancelEdit('${field}', this)">انصراف</button>
                <button class="btn-primary" onclick="saveEdit('${field}', this)">تایید</button>
            `;
            valueEl.parentNode.appendChild(controls);
        }

        function cancelEdit(field, btn) {
            const controls = btn.parentNode;
            const valueEl = document.getElementById(field + 'Value');
            
            valueEl.innerHTML = originalValues[field];
            controls.remove();
            const editBtn = valueEl.nextElementSibling;
            editBtn.style.display = 'flex';
        }

        function saveEdit(field, btn) {
            const controls = btn.parentNode;
            const valueEl = document.getElementById(field + 'Value');
            let newValue;

            if (field === 'grade' || field === 'field') {
                const select = valueEl.querySelector('select');
                newValue = select ? select.value : '';
            } else {
                const input = valueEl.querySelector('input');
                newValue = input ? input.value.trim() : '';
            }

            if (!newValue) {
                alert('مقدار نمی‌تواند خالی باشد.');
                return;
            }

            fetch('/parent/profile', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({field: field, value: newValue})
            }).then(res => res.json()).then(data => {
                if (data.success) {
                    valueEl.innerHTML = newValue;
                    controls.remove();
                    const editBtn = valueEl.nextElementSibling;
                    editBtn.style.display = 'flex';
                } else {
                    alert('خطا در ذخیره‌سازی');
                }
            }).catch(error => {
                alert('خطا در ارتباط با سرور');
            });
        }

        function showLogoutModal() { 
            document.getElementById('logoutModal').style.display = 'flex'; 
        }
        
        function closeLogout() { 
            document.getElementById('logoutModal').style.display = 'none'; 
        }
        
        function logout() { 
            window.location.href = '/parent/logout'; 
        }
    </script>
</body>
</html>
    ''', user=user, child1_display=child1_display, child2_display=child2_display)

# ========== ورود دانش‌آموزان ==========
@app.route('/login/student', methods=['GET', 'POST'])
def student_login():
    if session.get('student'):
        return redirect(url_for('student_dashboard'))
    
    error = None
    if request.method == 'POST':
        grade = request.form.get('grade', '')
        field = request.form.get('field', '')
        national_id = request.form.get('national_id', '')
        password = request.form.get('password', '')
        unique_id = national_id
        if not all([grade, field, national_id, password]):
            error = "لطفاً تمامی فیلدها را پر کنید."
        elif password != STUDENT_PASSWORD:
            error = "رمز عبور اشتباه است."
        elif unique_id in logged_in_students:
            error = "این حساب قبلاً وارد شده است."
        else:
            # پیدا کردن دانش‌آموز
            init_students()
            student_found = None
            for student in session['students'][grade][field]:
                if student['national_id'] == national_id:
                    student_found = student
                    break
            
            if not student_found:
                error = "دانش‌آموز با این کد ملی یافت نشد."
            else:
                session['student'] = {
                    'name': student_found['name'],
                    'family': student_found['family'],
                    'role': 'دانش‌آموز',
                    'grade': grade,
                    'field': field,
                    'national_id': national_id,
                    'student_number': student_found.get('student_number', ''),
                    'password': STUDENT_PASSWORD
                }
                logged_in_students.add(unique_id)
                session.modified = True
                return redirect(url_for('student_dashboard'))
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ورود دانش آموزان</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazir:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        body { background: #0D0D0D; color: white; font-family: 'Vazir', sans-serif; padding: 15px; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .form-container { background: #1A1A1A; padding: 25px; border-radius: 20px; width: 100%; max-width: 500px; box-shadow: 0 0 20px rgba(0, 255, 156, 0.3); border: 1px solid #333; }
        h2 { text-align: center; margin-bottom: 24px; color: #00FF9C; text-shadow: 0 0 10px #00FF9C; font-size: 24px; }
        .important-note { text-align: center; margin-bottom: 20px; color: #FF3CAC; font-size: 16px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; color: #FF3CAC; font-size: 16px; }
        input, select { width: 100%; padding: 12px; background: #222; border: 1px solid #444; border-radius: 10px; color: white; font-size: 16px; direction: rtl; }
        .btn-primary { width: 100%; padding: 14px; background: linear-gradient(90deg, #00FF9C, #FF3CAC); color: #0D0D0D; border: none; border-radius: 14px; font-weight: bold; font-size: 18px; cursor: pointer; box-shadow: 0 0 12px #00FF9C, 0 0 24px #FF3CAC; opacity: 0.5; cursor: not-allowed; }
        .btn-primary.active { opacity: 1; cursor: pointer; }
        .alert { padding: 12px; background: #331111; border: 1px solid #EF4444; border-radius: 8px; color: #FF6B6B; text-align: center; margin-bottom: 20px; font-size: 16px; }
        .back-link { display: block; text-align: center; margin-top: 20px; color: #00FF9C; text-decoration: none; font-size: 16px; }
        select:disabled { background: #333; color: #666; }
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 2000; justify-content: center; align-items: center; }
        .modal-content { background: #1A1A1A; padding: 25px; border-radius: 20px; width: 90%; max-width: 500px; border: 1px solid #333; text-align: center; }
        .checkbox { margin: 10px 0; }
        .modal-buttons { display: flex; gap: 10px; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="form-container">
        <h2>ورود دانش آموزان</h2>
        <p class="important-note">دانش آموز عزیز لطفاً کد ملی و پایه و رشته خود را به درستی وارد کرده تا با مشکل رو به رو نشوید</p>
        <form method="POST" id="studentForm" onsubmit="showConfirmModal(event)">
            {% if error %}<div class="alert">{{ error }}</div>{% endif %}
            
            <div class="form-group">
                <label>پایه</label>
                <select name="grade" id="gradeSelect" required onchange="updateField()">
                    <option value="">انتخاب کنید...</option>
                    <option value="دهم" {{ 'selected' if request.form.grade == 'دهم' }}>دهم</option>
                    <option value="یازدهم" {{ 'selected' if request.form.grade == 'یازدهم' }}>یازدهم</option>
                    <option value="دوازدهم" {{ 'selected' if request.form.grade == 'دوازدهم' }}>دوازدهم</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>رشته</label>
                <select name="field" id="fieldSelect" disabled required>
                    <option value="">انتخاب کنید...</option>
                    <option value="ریاضی" {{ 'selected' if request.form.field == 'ریاضی' }}>ریاضی</option>
                    <option value="تجربی" {{ 'selected' if request.form.field == 'تجربی' }}>تجربی</option>
                    <option value="انسانی" {{ 'selected' if request.form.field == 'انسانی' }}>انسانی</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>کد ملی (10 رقم انگلیسی)</label>
                <input type="text" name="national_id" id="nationalIdInput" value="{{ request.form.national_id or '' }}" required pattern="[0-9]{10}" title="لطفاً 10 رقم عددی وارد کنید">
            </div>
            
            <div class="form-group">
                <label>رمز عبور</label>
                <input type="password" name="password" required>
            </div>
            
            <button type="submit" class="btn-primary" id="submitBtn" disabled>ورود</button>
        </form>
        <a href="/" class="back-link">بازگشت به صفحه اصلی</a>
    </div>

    <div class="modal" id="confirmModal">
        <div class="modal-content">
            <p id="confirmText"></p>
            <div class="checkbox">
                <input type="checkbox" id="confirmCheck" onchange="toggleSubmit()">
                <label for="confirmCheck">تایید می‌کنم</label>
            </div>
            <div class="modal-buttons">
                <button style="flex:1; padding:12px; background:#333; border:1px solid #444; border-radius:10px; color:white;" onclick="closeConfirmModal()">انصراف</button>
                <button style="flex:1; padding:12px; background:linear-gradient(90deg, #00FF9C, #FF3CAC); border:none; border-radius:10px; color:#0D0D0D; font-weight:bold; opacity:0.5; cursor:not-allowed;" id="confirmSubmit" disabled>تایید</button>
            </div>
        </div>
    </div>

    <script>
        function updateField() {
            const gradeSelect = document.getElementById('gradeSelect');
            const fieldSelect = document.getElementById('fieldSelect');
            
            if (gradeSelect.value) {
                fieldSelect.disabled = false;
            } else {
                fieldSelect.disabled = true;
            }
            checkForm();
        }
        
        function checkForm() {
            const grade = document.getElementById('gradeSelect').value;
            const field = document.getElementById('fieldSelect').value;
            const nationalId = document.getElementById('nationalIdInput').value;
            const submitBtn = document.getElementById('submitBtn');
            submitBtn.disabled = !(grade && field && nationalId.length === 10);
            submitBtn.classList.toggle('active', !submitBtn.disabled);
        }
        
        function showConfirmModal(event) {
            event.preventDefault();
            const grade = document.getElementById('gradeSelect').value;
            const field = document.getElementById('fieldSelect').value;
            const nationalId = document.getElementById('nationalIdInput').value;
            document.getElementById('confirmText').innerText = `آیا کد ملی شما ${nationalId} و پایه ${grade} و رشته ${field} به درستی وارد شده؟`;
            document.getElementById('confirmModal').style.display = 'flex';
            document.getElementById('confirmCheck').checked = false;
            toggleSubmit();
        }

        function toggleSubmit() {
            const check = document.getElementById('confirmCheck').checked;
            const btn = document.getElementById('confirmSubmit');
            btn.disabled = !check;
            btn.style.opacity = check ? 1 : 0.5;
            btn.style.cursor = check ? 'pointer' : 'not-allowed';
        }

        function closeConfirmModal() {
            document.getElementById('confirmModal').style.display = 'none';
        }

        document.getElementById('confirmSubmit').addEventListener('click', () => {
            if (!document.getElementById('confirmSubmit').disabled) {
                document.getElementById('studentForm').submit();
            }
        });

        document.addEventListener('DOMContentLoaded', function() {
            updateField();
            document.getElementById('fieldSelect').addEventListener('change', checkForm);
            document.getElementById('nationalIdInput').addEventListener('input', checkForm);
        });
    </script>
</body>
</html>
    ''', error=error)

# ========== درگاه دانش‌آموزان ==========
@app.route('/student/dashboard')
def student_dashboard():
    if not session.get('student'):
        return redirect(url_for('student_login'))
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>درگاه دانش آموزان</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazir:wght@400;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { background: #0D0D0D; color: white; font-family: 'Vazir', sans-serif; }
        .toolbar { display: flex; justify-content: flex-end; padding: 12px 20px; background: #151515; border-bottom: 1px solid #333; }
        .menu-toggle { 
            background: #222; 
            color: #00FF9C; 
            border: 1px solid #00FF9C; 
            border-radius: 4px; 
            width: 44px; 
            height: 44px; 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            justify-content: center; 
            cursor: pointer; 
            box-shadow: 0 0 8px rgba(0, 255, 156, 0.5); 
            gap: 3px;
            padding: 8px;
        }
        .menu-line {
            width: 20px;
            height: 2px;
            background: #00FF9C;
            border-radius: 1px;
        }
        .sidebar { 
            position: fixed; 
            top: 0; 
            right: -100%; 
            height: 100%; 
            width: clamp(240px, 80vw, 300px); 
            background: #1A1A1A; 
            border-left: 1px solid #444; 
            transition: right 0.4s cubic-bezier(0.68, -0.55, 0.27, 1.55); 
            z-index: 1000; 
            padding-top: 70px; 
        }
        .sidebar.active { right: 0; }
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
            background: linear-gradient(90deg, #00FF9C, #FF3CAC); 
            color: #0D0D0D; 
            border: none; 
            border-radius: 14px; 
            text-decoration: none; 
            font-weight: bold; 
            font-size: 18px; 
            box-shadow: 0 0 10px #00FF9C, 0 0 20px #FF3CAC; 
            transition: all 0.3s;
        }
        .sidebar-btn:hover { transform: translateY(-2px); }
        .dashboard { padding: 20px; }
        .dashboard h2 { color: #00FF9C; margin: 20px 0 25px; text-shadow: 0 0 10px #00FF9C; font-size: 26px; text-align: center; }
        .cards-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(clamp(150px, 45vw, 220px), 1fr)); gap: 20px; padding: 0 10px; }
        .card { 
            background: #1A1A1A; 
            padding: 22px 16px; 
            border-radius: 18px; 
            text-align: center; 
            color: #FF3CAC; 
            border: 1px solid #333; 
            cursor: pointer; 
            transition: all 0.3s; 
            font-size: 18px; 
            box-shadow: 0 0 8px rgba(255, 60, 172, 0.3); 
            animation: cardAppear 0.6s ease;
        }
        .card:hover { 
            transform: translateY(-6px) scale(1.05); 
            box-shadow: 0 0 20px #FF3CAC, 0 0 30px #00FF9C; 
            background: #222; 
        }
        @keyframes cardAppear {
            from { 
                opacity: 0; 
                transform: translateY(20px) scale(0.9); 
            }
            to { 
                opacity: 1; 
                transform: translateY(0) scale(1); 
            }
        }
    </style>
</head>
<body>
    <header class="toolbar">
        <button class="menu-toggle" id="menuToggle">
            <div class="menu-line"></div>
            <div class="menu-line"></div>
            <div class="menu-line"></div>
        </button>
    </header>
    
    <div class="sidebar" id="sidebar">
        <div class="close-btn" id="closeSidebar">&times;</div>
        <a href="/student/dashboard" class="sidebar-btn">صفحه اصلی</a>
        <a href="/student/profile" class="sidebar-btn">پروفایل</a>
        <a href="#" class="sidebar-btn">اعلانات</a>
    </div>
    
    <div class="dashboard">
        <h2>درگاه دانش آموزان</h2>
        <div class="cards-grid">
            <div class="card" style="animation-delay: 0.1s">حضورم در دبیرستان</div>
            <div class="card" style="animation-delay: 0.2s">نمرات درسم</div>
            <div class="card" style="animation-delay: 0.3s">تکالیف و امتحانات روزم</div>
            <div class="card" style="animation-delay: 0.4s">کارنامه من</div>
            <div class="card" style="animation-delay: 0.5s">گزارش</div>
        </div>
    </div>

    <script>
        history.pushState(null, null, location.href);
        window.addEventListener('popstate', () => history.pushState(null, null, location.href));
        
        document.getElementById('menuToggle').addEventListener('click', function() {
            document.getElementById('sidebar').classList.add('active');
        });
        
        document.getElementById('closeSidebar').addEventListener('click', function() {
            document.getElementById('sidebar').classList.remove('active');
        });
        
        document.addEventListener('click', function(event) {
            const sidebar = document.getElementById('sidebar');
            const menuToggle = document.getElementById('menuToggle');
            if (sidebar.classList.contains('active') && 
                !sidebar.contains(event.target) && 
                !menuToggle.contains(event.target)) {
                sidebar.classList.remove('active');
            }
        });
    </script>
</body>
</html>
    ''')

# ========== پروفایل دانش‌آموزان ==========
@app.route('/student/profile', methods=['GET', 'POST'])
def student_profile():
    if not session.get('student'):
        return redirect(url_for('student_login'))
    
    user = session['student']
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>پروفایل دانش آموز</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazir:wght@400;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background: #0D0D0D; color: white; font-family: 'Vazir', sans-serif; padding: 15px; }
        .toolbar { display: flex; justify-content: flex-end; padding: 12px 20px; background: #151515; border-bottom: 1px solid #333; }
        .back-btn { background: #222; color: #00FF9C; border: 1px solid #00FF9C; border-radius: 50%; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 0 8px rgba(0, 255, 156, 0.5); font-size: 20px; }
        .container { max-width: 600px; margin: 25px auto; background: #1A1A1A; padding: 25px; border-radius: 20px; border: 1px solid #333; box-shadow: 0 0 20px rgba(0, 255, 156, 0.2); }
        h2 { text-align: center; margin-bottom: 25px; color: #00FF9C; text-shadow: 0 0 10px #00FF9C; font-size: 24px; }
        .profile-field { display: flex; align-items: center; margin: 22px 0; gap: 15px; flex-wrap: wrap; border-bottom: 1px solid #333; padding-bottom: 20px; }
        .field-label { min-width: 140px; color: #FF3CAC; font-size: 18px; }
        .field-value { flex: 1; padding: 12px; background: #222; border-radius: 12px; direction: rtl; font-size: 18px; min-width: 150px; }
        .edit-btn { background: #222; color: #6B7280; border: 1px solid #6B7280; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: not-allowed; font-size: 16px; opacity: 0.5; }
        .btn-logout { width: 100%; padding: 16px; background: linear-gradient(90deg, #EF4444, #FF3CAC); color: white; border: none; border-radius: 16px; font-size: 18px; margin-top: 30px; cursor: pointer; box-shadow: 0 0 12px #EF4444, 0 0 24px #FF3CAC; transition: all 0.3s; }
        .btn-logout:hover { transform: translateY(-2px); }
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); justify-content: center; align-items: center; z-index: 2000; animation: fadeIn 0.3s ease; }
        .modal-content { background: #1A1A1A; padding: 25px; border-radius: 18px; width: 90%; max-width: 420px; text-align: center; border: 1px solid #FF3CAC; box-shadow: 0 0 25px #FF3CAC; animation: slideIn 0.3s ease; }
        .modal-buttons { display: flex; gap: 15px; justify-content: center; margin-top: 25px; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes slideIn { from { transform: translateY(-20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
    </style>
</head>
<body>
    <header class="toolbar">
        <button class="back-btn" onclick="window.location.href='/student/dashboard'"><i class="fas fa-arrow-right"></i></button>
    </header>
    <div class="container">
        <h2>پروفایل کاربری</h2>
        
        <div class="profile-field">
            <div class="field-label">نام:</div>
            <div class="field-value" id="nameValue">{{ user.name }}</div>
            <div class="edit-btn"><i class="fas fa-pencil-alt"></i></div>
        </div>
        
        <div class="profile-field">
            <div class="field-label">نام خانوادگی:</div>
            <div class="field-value" id="familyValue">{{ user.family }}</div>
            <div class="edit-btn"><i class="fas fa-pencil-alt"></i></div>
        </div>
        
        <div class="profile-field">
            <div class="field-label">مرتبه:</div>
            <div class="field-value">دانش‌آموز</div>
            <span style="color:#6B7280; font-size:14px;">(ثابت)</span>
        </div>
        
        <div class="profile-field">
            <div class="field-label">پایه انتخاب شده:</div>
            <div class="field-value" id="gradeValue">{{ user.grade }}</div>
            <div class="edit-btn"><i class="fas fa-pencil-alt"></i></div>
        </div>
        
        <div class="profile-field">
            <div class="field-label">رشته انتخاب شده:</div>
            <div class="field-value" id="fieldValue">{{ user.field }}</div>
            <div class="edit-btn"><i class="fas fa-pencil-alt"></i></div>
        </div>
        
        <div class="profile-field">
            <div class="field-label">کد ملی:</div>
            <div class="field-value" id="nationalIdValue">{{ user.national_id }}</div>
            <div class="edit-btn"><i class="fas fa-pencil-alt"></i></div>
        </div>
        
        <div class="profile-field">
            <div class="field-label">رمز عبور:</div>
            <div class="field-value" id="passwordValue">{{ user.password }}</div>
            <div class="edit-btn"><i class="fas fa-pencil-alt"></i></div>
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
        function showLogoutModal() { 
            document.getElementById('logoutModal').style.display = 'flex'; 
        }
        
        function closeLogout() { 
            document.getElementById('logoutModal').style.display = 'none'; 
        }
        
        function logout() { 
            window.location.href = '/student/logout'; 
        }
    </script>
</body>
</html>
    ''', user=user)

# ========== خروج ==========
@app.route('/admin/logout')
def admin_logout():
    unique_id = f"{session['admin']['name']}_{session['admin']['family']}_{session['admin']['role']}"
    logged_in_admins.discard(unique_id)
    session.pop('admin', None)
    return redirect(url_for('home'))

@app.route('/teacher/logout')
def teacher_logout():
    unique_id = f"{session['teacher']['name']}_{session['teacher']['family']}"
    logged_in_teachers.discard(unique_id)
    session.pop('teacher', None)
    return redirect(url_for('home'))

@app.route('/parent/logout')
def parent_logout():
    unique_id = f"{session['parent']['name']}_{session['parent']['family']}_{session['parent']['child1']}_{session['parent']['child2']}"
    logged_in_parents.discard(unique_id)
    session.pop('parent', None)
    return redirect(url_for('home'))

@app.route('/student/logout')
def student_logout():
    unique_id = session['student']['national_id']
    logged_in_students.discard(unique_id)
    session.pop('student', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))