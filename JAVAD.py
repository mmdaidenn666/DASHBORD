from flask import Flask, render_template_string, request, session, redirect, url_for, jsonify
import os
import copy

app = Flask(__name__)
app.secret_key = 'neon_dabirestan_2025_secure_key'

ADMIN_PASSWORD = "dabirestan012345"
TEACHER_PASSWORD = "dabirjavadol"

def init_students():
    if 'students' not in session:
        session['students'] = {
            'دهم': {'ریاضی': [], 'تجربی': [], 'انسانی': []},
            'یازدهم': {'ریاضی': [], 'تجربی': [], 'انسانی': []},
            'دوازدهم': {'ریاضی': [], 'تجربی': [], 'انسانی': []}
        }
    # اطمینان از ذخیره‌سازی session
    session.modified = True

def save_students():
    """ذخیره‌سازی تغییرات در session"""
    session.modified = True

# ========== صفحه اصلی ==========
@app.route('/')
def home():
    if session.get('admin'):
        init_students()
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
        init_students()
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

# ========== ورود معلمان ==========
@app.route('/login/teacher', methods=['GET', 'POST'])
def teacher_login():
    if session.get('teacher'):
        return redirect(url_for('teacher_dashboard'))
    error = None
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        family = request.form.get('family', '').strip()
        grade_count = request.form.get('grade_count', '0')
        grades = [request.form.get(f'grade_{i}', '') for i in range(1, 4)]
        field_count = request.form.get('field_count', '0')
        fields = [request.form.get(f'field_{i}', '') for i in range(1, 4)]
        subject_count = request.form.get('subject_count', '0')
        subjects = [request.form.get(f'subject_{i}', '') for i in range(1, 5)]
        password = request.form.get('password', '')

        if not name or not family or not password:
            error = "نام، نام خانوادگی و رمز عبور الزامی است."
        elif password != TEACHER_PASSWORD:
            error = "رمز عبور اشتباه است."
        else:
            session['teacher'] = {
                'name': name,
                'family': family,
                'grade_count': grade_count,
                'grades': grades[:int(grade_count)] if grade_count != '0' else [],
                'field_count': field_count,
                'fields': fields[:int(field_count)] if field_count != '0' else [],
                'subject_count': subject_count,
                'subjects': subjects[:int(subject_count)] if subject_count != '0' else []
            }
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
        .form-container { background: #1A1A1A; padding: 25px; border-radius: 20px; width: 100%; max-width: 600px; box-shadow: 0 0 20px rgba(255, 60, 172, 0.3); border: 1px solid #333; }
        h2 { text-align: center; margin-bottom: 24px; color: #FF3CAC; text-shadow: 0 0 10px #FF3CAC; font-size: 24px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; color: #FF9E00; font-size: 16px; }
        input, select { width: 100%; padding: 12px; background: #222; border: 1px solid #444; border-radius: 10px; color: white; font-size: 16px; direction: rtl; }
        .btn-primary { width: 100%; padding: 14px; background: linear-gradient(90deg, #FF3CAC, #FF9E00); color: #0D0D0D; border: none; border-radius: 14px; font-weight: bold; font-size: 18px; cursor: pointer; box-shadow: 0 0 12px #FF3CAC, 0 0 24px #FF9E00; }
        .alert { padding: 12px; background: #331111; border: 1px solid #EF4444; border-radius: 8px; color: #FF6B6B; text-align: center; margin-bottom: 20px; font-size: 16px; }
        .back-link { display: block; text-align: center; margin-top: 20px; color: #FF3CAC; text-decoration: none; font-size: 16px; }
        .sub-group { margin-top: 15px; padding-top: 15px; border-top: 1px solid #333; }
        select:disabled, input:disabled { background: #333; color: #666; }
    </style>
</head>
<body>
    <div class="form-container">
        <h2>ورود معلمان</h2>
        <form method="POST" id="teacherForm">
            {% if error %}<div class="alert">{{ error }}</div>{% endif %}
            
            <div class="form-group">
                <label>نام</label>
                <input type="text" name="name" value="{{ request.form.name or '' }}" required>
            </div>
            <div class="form-group">
                <label>نام خانوادگی</label>
                <input type="text" name="family" value="{{ request.form.family or '' }}" required>
            </div>

            <!-- تعداد پایه‌ها -->
            <div class="form-group">
                <label>تعداد پایه‌ها</label>
                <select name="grade_count" id="gradeCount" required>
                    <option value="0">انتخاب کنید...</option>
                    <option value="1" {{ 'selected' if request.form.grade_count == '1' }}>1</option>
                    <option value="2" {{ 'selected' if request.form.grade_count == '2' }}>2</option>
                    <option value="3" {{ 'selected' if request.form.grade_count == '3' }}>3</option>
                </select>
            </div>
            <div class="sub-group">
                {% for i in range(1,4) %}
                <div class="form-group">
                    <label>پایه {{ i }}</label>
                    <select name="grade_{{ i }}" id="grade{{ i }}" disabled>
                        <option value="">انتخاب کنید...</option>
                        <option value="دهم" {{ 'selected' if request.form.get('grade_' + i|string) == 'دهم' }}>دهم</option>
                        <option value="یازدهم" {{ 'selected' if request.form.get('grade_' + i|string) == 'یازدهم' }}>یازدهم</option>
                        <option value="دوازدهم" {{ 'selected' if request.form.get('grade_' + i|string) == 'دوازدهم' }}>دوازدهم</option>
                    </select>
                </div>
                {% endfor %}
            </div>

            <!-- تعداد رشته‌ها -->
            <div class="form-group">
                <label>تعداد رشته‌ها</label>
                <select name="field_count" id="fieldCount" required>
                    <option value="0">انتخاب کنید...</option>
                    <option value="1" {{ 'selected' if request.form.field_count == '1' }}>1</option>
                    <option value="2" {{ 'selected' if request.form.field_count == '2' }}>2</option>
                    <option value="3" {{ 'selected' if request.form.field_count == '3' }}>3</option>
                </select>
            </div>
            <div class="sub-group">
                {% for i in range(1,4) %}
                <div class="form-group">
                    <label>رشته {{ i }}</label>
                    <select name="field_{{ i }}" id="field{{ i }}" disabled>
                        <option value="">انتخاب کنید...</option>
                        <option value="ریاضی" {{ 'selected' if request.form.get('field_' + i|string) == 'ریاضی' }}>ریاضی</option>
                        <option value="تجربی" {{ 'selected' if request.form.get('field_' + i|string) == 'تجربی' }}>تجربی</option>
                        <option value="انسانی" {{ 'selected' if request.form.get('field_' + i|string) == 'انسانی' }}>انسانی</option>
                    </select>
                </div>
                {% endfor %}
            </div>

            <!-- تعداد دروس -->
            <div class="form-group">
                <label>تعداد دروس</label>
                <select name="subject_count" id="subjectCount" required>
                    <option value="0">انتخاب کنید...</option>
                    <option value="1" {{ 'selected' if request.form.subject_count == '1' }}>1</option>
                    <option value="2" {{ 'selected' if request.form.subject_count == '2' }}>2</option>
                    <option value="3" {{ 'selected' if request.form.subject_count == '3' }}>3</option>
                    <option value="4" {{ 'selected' if request.form.subject_count == '4' }}>4</option>
                </select>
            </div>
            <div class="sub-group">
                {% for i in range(1,5) %}
                <div class="form-group">
                    <label>درس {{ i }}</label>
                    <input type="text" name="subject_{{ i }}" id="subject{{ i }}" value="{{ request.form.get('subject_' + i|string) or '' }}" disabled>
                </div>
                {% endfor %}
            </div>

            <div class="form-group">
                <label>رمز عبور</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit" class="btn-primary">ورود</button>
        </form>
        <a href="/" class="back-link">بازگشت به صفحه اصلی</a>
    </div>

    <script>
        function toggleFields(countId, prefix, max) {
            const count = document.getElementById(countId).value;
            for (let i = 1; i <= max; i++) {
                const el = document.getElementById(prefix + i);
                if (el) {
                    el.disabled = (i > count || count == "0");
                    if (el.disabled) {
                        el.value = "";
                    }
                }
            }
        }
        
        // فعال‌سازی اولیه
        document.addEventListener('DOMContentLoaded', function() {
            toggleFields('gradeCount', 'grade', 3);
            toggleFields('fieldCount', 'field', 3);
            toggleFields('subjectCount', 'subject', 4);
        });
        
        document.getElementById('gradeCount').addEventListener('change', () => toggleFields('gradeCount', 'grade', 3));
        document.getElementById('fieldCount').addEventListener('change', () => toggleFields('fieldCount', 'field', 3));
        document.getElementById('subjectCount').addEventListener('change', () => toggleFields('subjectCount', 'subject', 4));
    </script>
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
        function editField(field, btn) {
            const valueEl = document.getElementById(field + 'Value');
            const currentValue = valueEl.innerText;
            
            // ذخیره دکمه اصلی
            const originalBtn = btn.cloneNode(true);
            
            // مخفی کردن دکمه فعلی
            btn.style.display = 'none';
            
            // ایجاد فیلد ویرایش
            valueEl.innerHTML = '';

            if (field === 'role') {
                const select = document.createElement('select');
                select.style.width = '100%'; 
                select.style.padding = '10px'; 
                select.style.background = '#222'; 
                select.style.color = 'white'; 
                select.style.borderRadius = '10px'; 
                select.style.border = '1px solid #444'; 
                select.style.fontSize = '18px';
                
                const options = ['مدیر', 'ناظم', 'معاون', 'مشاور'];
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

            // ایجاد دکمه‌های کنترل
            const controls = document.createElement('div');
            controls.className = 'edit-controls';
            controls.innerHTML = `
                <button class="btn-ghost" onclick="cancelEdit('${field}', this)">انصراف</button>
                <button class="btn-primary" onclick="saveEdit('${field}', this, originalBtn)">تایید</button>
            `;
            
            // ذخیره reference به دکمه اصلی
            controls.originalBtn = originalBtn;
            valueEl.parentNode.appendChild(controls);
        }

        function cancelEdit(field, btn) {
            const controls = btn.parentNode;
            const valueEl = document.getElementById(field + 'Value');
            const originalValue = controls.previousElementSibling ? controls.previousElementSibling.innerText : '';
            
            // بازگردانی مقدار اصلی
            valueEl.innerHTML = originalValue;
            
            // حذف کنترل‌ها
            controls.remove();
            
            // نمایش مجدد دکمه ویرایش
            const editBtn = valueEl.nextElementSibling;
            editBtn.style.display = 'flex';
        }

        function saveEdit(field, btn, originalBtn) {
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
                    // به‌روزرسانی UI با مقدار جدید
                    valueEl.innerHTML = newValue;
                    
                    // حذف کنترل‌ها
                    controls.remove();
                    
                    // نمایش مجدد دکمه ویرایش
                    const editBtn = valueEl.nextElementSibling;
                    editBtn.style.display = 'flex';
                    
                } else {
                    alert('خطا در ذخیره‌سازی: ' + (data.error || ''));
                }
            }).catch(error => {
                alert('خطا در ارتباط با سرور');
                console.error('Error:', error);
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

# ========== مدیریت دانش‌آموزان ==========
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
        <div style="width: 44px;"></div> <!-- برای بالانس -->
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
        .action-btn { width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; }
        .edit-btn { background: #222; color: #00FF9C; border: 1px solid #00FF9C; }
        .delete-btn { background: #222; color: #EF4444; border: 1px solid #EF4444; }
        .fab { position: fixed; bottom: 20px; right: 20px; width: 60px; height: 60px; border-radius: 50%; background: linear-gradient(135deg, #00C6FF, #00FF9C); display: flex; align-items: center; justify-content: center; color: white; font-size: 24px; box-shadow: 0 4px 12px rgba(0,198,255,0.4); cursor: pointer; z-index: 100; }
        
        /* مدال‌ها */
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 2000; justify-content: center; align-items: center; }
        .modal-content { background: #1A1A1A; padding: 25px; border-radius: 20px; width: 90%; max-width: 500px; border: 1px solid #333; }
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

    <!-- مدال اضافه کردن دانش‌آموز -->
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

    <!-- مدال تأیید حذف -->
    <div class="modal" id="deleteModal">
        <div class="modal-content">
            <p style="font-size:18px; margin-bottom:20px; text-align:center;">آیا مطمئن هستید می‌خواهید اطلاعات دانش‌آموز را پاک کنید؟</p>
            <div class="modal-buttons">
                <button style="flex:1; padding:12px; background:#333; border:1px solid #444; border-radius:10px; color:white;" onclick="closeDeleteModal()">خیر</button>
                <button style="flex:1; padding:12px; background:linear-gradient(90deg, #EF4444, #FF3CAC); border:none; border-radius:10px; color:white; font-weight:bold;" onclick="confirmDelete()">بله</button>
            </div>
        </div>
    </div>

    <!-- مدال مشاهده جزئیات -->
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

        function showAddStudentModal() {
            document.getElementById('addStudentModal').style.display = 'flex';
            document.getElementById('formAlert').style.display = 'none';
            // پاک کردن فیلدها
            ['studentName', 'studentFamily', 'studentNationalId', 'studentNumber', 'fatherNumber', 'motherNumber'].forEach(id => {
                document.getElementById(id).value = '';
            });
            currentEditIndex = -1;
        }

        function closeAddStudentModal() {
            document.getElementById('addStudentModal').style.display = 'none';
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

            const url = currentEditIndex === -1 ? '/admin/students/add' : '/admin/students/update';
            const data = {
                grade: "{{ grade }}",
                field: "{{ field }}",
                student: studentData
            };

            if (currentEditIndex !== -1) {
                data.index = currentEditIndex;
            }

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
            document.getElementById('addStudentModal').style.display = 'flex';
            document.getElementById('studentName').value = student.name;
            document.getElementById('studentFamily').value = student.family;
            document.getElementById('studentNationalId').value = student.national_id;
            document.getElementById('studentNumber').value = student.student_number || '';
            document.getElementById('fatherNumber').value = student.father_number || '';
            document.getElementById('motherNumber').value = student.mother_number || '';
            document.getElementById('formAlert').style.display = 'none';
            currentEditIndex = index;
        }

        function deleteStudent(index) {
            currentDeleteIndex = index;
            document.getElementById('deleteModal').style.display = 'flex';
        }

        function closeDeleteModal() {
            document.getElementById('deleteModal').style.display = 'none';
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
            document.getElementById('viewModal').style.display = 'flex';
        }

        function closeViewModal() {
            document.getElementById('viewModal').style.display = 'none';
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

# ========== API به‌روزرسانی دانش‌آموز ==========
@app.route('/admin/students/update', methods=['POST'])
def update_student():
    if not session.get('admin'):
        return jsonify(success=False), 403
    
    init_students()
    data = request.get_json()
    grade = data.get('grade')
    field = data.get('field')
    index = data.get('index')
    student = data.get('student')
    
    try:
        # بررسی اینکه آیا کد ملی تغییر کرده و تکراری است
        current_student = session['students'][grade][field][index]
        if current_student['national_id'] != student['national_id']:
            for g in session['students']:
                for f in session['students'][g]:
                    if any(s['national_id'] == student['national_id'] for s in session['students'][g][f]):
                        return jsonify(success=False, error="کد ملی تکراری است.")
        
        session['students'][grade][field][index] = student
        session.modified = True
        return jsonify(success=True)
    except (IndexError, KeyError):
        return jsonify(success=False, error="دانش‌آموز یافت نشد")

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

# ========== جستجوی دانش‌آموزان ==========
@app.route('/admin/students/search')
def search_students():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    init_students()
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
        .back-btn { background: #222; color: #00FF9C; border: 1px solid #00FF9C; border-radius: 50%; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 0 8px rgba(0, 255, 156, 0.5); font-size: 20px; }
        .search-container { display: flex; gap: 10px; padding: 20px; }
        .search-input { flex: 1; padding: 12px 15px; background: #222; border: 1px solid #444; border-radius: 10px; color: white; direction: rtl; }
        .search-btn { padding: 12px 20px; background: linear-gradient(90deg, #00C6FF, #00FF9C); border: none; border-radius: 10px; color: #0D0D0D; font-weight: bold; cursor: pointer; }
        .dashboard { padding: 20px; }
        .dashboard h2 { color: #00FF9C; margin: 20px 0 25px; text-shadow: 0 0 10px #00FF9C; font-size: 26px; text-align: center; }
        .student-list { display: flex; flex-direction: column; gap: 15px; }
        .student-card { background: #1A1A1A; padding: 16px; border-radius: 16px; border: 1px solid #333; }
        .student-name { font-weight: bold; font-size: 18px; color: #00C6FF; }
        .student-id { font-size: 14px; color: #6B7280; margin-top: 4px; }
        .student-grade-field { font-size: 12px; color: #00FF9C; }
    </style>
</head>
<body>
    <header class="toolbar">
        <button class="back-btn" onclick="window.history.back()"><i class="fas fa-arrow-right"></i></button>
        <div>جستجوی دانش‌آموزان</div>
        <div style="width: 44px;"></div>
    </header>
    
    <div class="search-container">
        <input type="text" id="searchInput" class="search-input" placeholder="جستجو بر اساس نام، نام خانوادگی یا کد ملی..." value="{{ query }}">
        <button class="search-btn" onclick="performSearch()"><i class="fas fa-search"></i> جستجو</button>
    </div>
    
    <div class="dashboard">
        <h2>نتایج جستجو</h2>
        <div class="student-list">
            {% for student in results %}
            <div class="student-card">
                <div class="student-name">{{ student.name }} {{ student.family }}</div>
                <div class="student-id">کد ملی: {{ student.national_id }}</div>
                <div class="student-grade-field">{{ student.grade }} - {{ student.field }}</div>
            </div>
            {% endfor %}
            {% if not results and query %}
            <div style="text-align:center; padding:30px; color:#6B7280;">نتیجه‌ای یافت نشد.</div>
            {% endif %}
        </div>
    </div>
    
    <script>
        function performSearch() {
            const q = document.getElementById('searchInput').value.trim();
            const grade = "{{ grade }}";
            let url = '/admin/students/search?q=' + encodeURIComponent(q);
            if (grade) url += '&grade=' + encodeURIComponent(grade);
            window.location.href = url;
        }
        
        // فعال کردن جستجو با Enter
        document.getElementById('searchInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performSearch();
            }
        });
    </script>
</body>
</html>
    ''', query=query, results=results, grade=grade)

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
        .menu-toggle { background: #222; color: #00FF9C; border: 1px solid #00FF9C; border-radius: 50%; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 0 8px rgba(0, 255, 156, 0.5); font-size: 20px; }
        .sidebar { position: fixed; top: 0; right: 0; height: 100%; width: clamp(240px, 80vw, 300px); background: #1A1A1A; border-left: 1px solid #444; transform: translateX(100%); transition: transform 0.4s cubic-bezier(0.68, -0.55, 0.27, 1.55); z-index: 1000; padding-top: 70px; }
        .sidebar.active { transform: translateX(0); }
        .close-btn { position: absolute; top: 20px; left: 20px; background: #EF4444; color: white; width: 34px; height: 34px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; font-weight: bold; font-size: 20px; box-shadow: 0 0 10px #EF4444; }
        .sidebar-btn { display: block; width: calc(100% - 40px); margin: 18px 20px; padding: 16px; text-align: center; background: linear-gradient(90deg, #FF3CAC, #FF9E00); color: #0D0D0D; border: none; border-radius: 14px; text-decoration: none; font-weight: bold; font-size: 18px; box-shadow: 0 0 10px #FF3CAC, 0 0 20px #FF9E00; }
        .dashboard { padding: 20px; }
        .dashboard h2 { color: #FF9E00; margin: 20px 0 25px; text-shadow: 0 0 10px #FF9E00; font-size: 26px; text-align: center; }
        .cards-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(clamp(150px, 45vw, 220px), 1fr)); gap: 20px; padding: 0 10px; }
        .card { background: #1A1A1A; padding: 22px 16px; border-radius: 18px; text-align: center; color: #FF3CAC; border: 1px solid #333; cursor: pointer; transition: all 0.3s; font-size: 18px; box-shadow: 0 0 8px rgba(255, 60, 172, 0.3); }
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
            <div class="card">حضور و غیاب</div>
            <div class="card">نمرات</div>
            <div class="card">گزارش</div>
            <div class="card">جزوه ها</div>
            <div class="card">تکالیف و امتحانات</div>
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

# ========== پروفایل معلمان ==========
@app.route('/teacher/profile', methods=['GET', 'POST'])
def teacher_profile():
    if not session.get('teacher'):
        return redirect(url_for('teacher_login'))
    
    if request.method == 'POST':
        data = request.get_json()
        field = data.get('field')
        value = data.get('value')
        
        if field in ['name', 'family', 'grade_count', 'field_count', 'subject_count']:
            session['teacher'][field] = value
            # اگر تعداد تغییر کرد، آرایه‌ها را بر اساس تعداد جدید تنظیم کن
            if field == 'grade_count':
                session['teacher']['grades'] = session['teacher']['grades'][:int(value)] if int(value) > 0 else []
            elif field == 'field_count':
                session['teacher']['fields'] = session['teacher']['fields'][:int(value)] if int(value) > 0 else []
            elif field == 'subject_count':
                session['teacher']['subjects'] = session['teacher']['subjects'][:int(value)] if int(value) > 0 else []
        elif field in ['grades', 'fields', 'subjects']:
            session['teacher'][field] = value
        
        session.modified = True
        return jsonify(success=True)
    
    user = session['teacher']
    grades_str = ', '.join(user['grades']) if user['grades'] else 'ندارد'
    fields_str = ', '.join(user['fields']) if user['fields'] else 'ندارد'
    subjects_str = ', '.join(user['subjects']) if user['subjects'] else 'ندارد'
    
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
        .back-btn { background: #222; color: #FF3CAC; border: 1px solid #FF3CAC; border-radius: 50%; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 0 8px rgba(255, 60, 172, 0.5); font-size: 20px; }
        .container { max-width: 600px; margin: 25px auto; background: #1A1A1A; padding: 25px; border-radius: 20px; border: 1px solid #333; box-shadow: 0 0 20px rgba(255, 60, 172, 0.2); }
        h2 { text-align: center; margin-bottom: 25px; color: #FF3CAC; text-shadow: 0 0 10px #FF3CAC; font-size: 24px; }
        .profile-field { display: flex; align-items: center; margin: 22px 0; gap: 15px; flex-wrap: wrap; }
        .field-label { min-width: 140px; color: #FF9E00; font-size: 18px; }
        .field-value { flex: 1; padding: 12px; background: #222; border-radius: 12px; direction: rtl; font-size: 18px; min-width: 150px; }
        .edit-btn { background: #222; color: #00FF9C; border: 1px solid #00FF9C; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 0 8px rgba(0, 255, 156, 0.5); font-size: 16px; }
        .edit-controls { display: flex; gap: 12px; margin-top: 12px; width: 100%; }
        .btn-ghost { flex: 1; padding: 10px; background: transparent; border: 1px solid #FF3CAC; color: #FF3CAC; border-radius: 12px; cursor: pointer; font-size: 16px; }
        .btn-primary { flex: 1; padding: 10px; background: linear-gradient(90deg, #FF3CAC, #FF9E00); color: #0D0D0D; border: none; border-radius: 12px; font-weight: bold; font-size: 16px; cursor: pointer; box-shadow: 0 0 10px #FF3CAC, 0 0 20px #FF9E00; }
        .btn-logout { width: 100%; padding: 16px; background: linear-gradient(90deg, #EF4444, #FF3CAC); color: white; border: none; border-radius: 16px; font-size: 18px; margin-top: 30px; cursor: pointer; box-shadow: 0 0 12px #EF4444, 0 0 24px #FF3CAC; }
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); justify-content: center; align-items: center; z-index: 2000; }
        .modal-content { background: #1A1A1A; padding: 25px; border-radius: 18px; width: 90%; max-width: 420px; text-align: center; border: 1px solid #FF3CAC; box-shadow: 0 0 25px #FF3CAC; }
        .modal-buttons { display: flex; gap: 15px; justify-content: center; margin-top: 25px; }
        .multi-field { display: flex; flex-direction: column; gap: 8px; }
        .multi-field select, .multi-field input { width: 100%; padding: 8px; background: #222; border: 1px solid #444; border-radius: 8px; color: white; }
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
            <div class="field-value" id="gradeCountValue">{{ user.grade_count }}</div>
            <button class="edit-btn" onclick="editField('grade_count', this)"><i class="fas fa-pencil-alt"></i></button>
        </div>
        
        <div class="profile-field">
            <div class="field-label">پایه‌ها:</div>
            <div class="field-value" id="gradesValue">{{ grades_str }}</div>
            <button class="edit-btn" onclick="editField('grades', this)"><i class="fas fa-pencil-alt"></i></button>
        </div>
        
        <div class="profile-field">
            <div class="field-label">تعداد رشته‌ها:</div>
            <div class="field-value" id="fieldCountValue">{{ user.field_count }}</div>
            <button class="edit-btn" onclick="editField('field_count', this)"><i class="fas fa-pencil-alt"></i></button>
        </div>
        
        <div class="profile-field">
            <div class="field-label">رشته‌ها:</div>
            <div class="field-value" id="fieldsValue">{{ fields_str }}</div>
            <button class="edit-btn" onclick="editField('fields', this)"><i class="fas fa-pencil-alt"></i></button>
        </div>
        
        <div class="profile-field">
            <div class="field-label">تعداد دروس:</div>
            <div class="field-value" id="subjectCountValue">{{ user.subject_count }}</div>
            <button class="edit-btn" onclick="editField('subject_count', this)"><i class="fas fa-pencil-alt"></i></button>
        </div>
        
        <div class="profile-field">
            <div class="field-label">دروس:</div>
            <div class="field-value" id="subjectsValue">{{ subjects_str }}</div>
            <button class="edit-btn" onclick="editField('subjects', this)"><i class="fas fa-pencil-alt"></i></button>
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
            const valueEl = document.getElementById(field + 'Value');
            const currentValue = valueEl.innerText;
            
            // ذخیره دکمه اصلی
            const originalBtn = btn.cloneNode(true);
            btn.style.display = 'none';
            valueEl.innerHTML = '';

            if (field === 'grade_count' || field === 'field_count' || field === 'subject_count') {
                const select = document.createElement('select');
                select.style.cssText = 'width: 100%; padding: 10px; background: #222; color: white; border-radius: 10px; border: 1px solid #444; font-size: 18px;';
                
                const max = field === 'subject_count' ? 4 : 3;
                for (let i = 0; i <= max; i++) {
                    const option = document.createElement('option');
                    option.value = i;
                    option.textContent = i === 0 ? '0 (ندارد)' : i;
                    if (i == parseInt(currentValue) || (i === 0 && currentValue === '0')) {
                        option.selected = true;
                    }
                    select.appendChild(option);
                }
                valueEl.appendChild(select);
                
            } else if (field === 'grades' || field === 'fields') {
                const countField = field === 'grades' ? 'grade_count' : 'field_count';
                const count = parseInt(document.getElementById(countField + 'Value').innerText) || 0;
                const container = document.createElement('div');
                container.className = 'multi-field';
                
                const options = field === 'grades' ? ['دهم', 'یازدهم', 'دوازدهم'] : ['ریاضی', 'تجربی', 'انسانی'];
                const currentValues = currentValue === 'ندارد' ? [] : currentValue.split(', ').map(s => s.trim());
                
                for (let i = 0; i < count; i++) {
                    const select = document.createElement('select');
                    select.style.cssText = 'width: 100%; padding: 8px; background: #222; color: white; border-radius: 8px; border: 1px solid #444;';
                    
                    options.forEach(opt => {
                        const option = document.createElement('option');
                        option.value = opt;
                        option.textContent = opt;
                        if (i < currentValues.length && opt === currentValues[i]) {
                            option.selected = true;
                        }
                        select.appendChild(option);
                    });
                    container.appendChild(select);
                }
                valueEl.appendChild(container);
                
            } else if (field === 'subjects') {
                const count = parseInt(document.getElementById('subjectCountValue').innerText) || 0;
                const container = document.createElement('div');
                container.className = 'multi-field';
                const currentValues = currentValue === 'ندارد' ? [] : currentValue.split(', ').map(s => s.trim());
                
                for (let i = 0; i < count; i++) {
                    const input = document.createElement('input');
                    input.type = 'text';
                    input.value = i < currentValues.length ? currentValues[i] : '';
                    input.style.cssText = 'width: 100%; padding: 8px; background: #222; color: white; border-radius: 8px; border: 1px solid #444; direction: rtl;';
                    input.placeholder = `درس ${i + 1}`;
                    container.appendChild(input);
                }
                valueEl.appendChild(container);
                
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
            const originalValue = controls.previousElementSibling ? controls.previousElementSibling.innerText : '';
            
            valueEl.innerHTML = originalValue;
            controls.remove();
            
            const editBtn = valueEl.nextElementSibling;
            editBtn.style.display = 'flex';
        }

        function saveEdit(field, btn) {
            const controls = btn.parentNode;
            const valueEl = document.getElementById(field + 'Value');
            let newValue;

            if (field === 'grade_count' || field === 'field_count' || field === 'subject_count') {
                const select = valueEl.querySelector('select');
                newValue = select ? select.value : '0';
            } else if (field === 'grades' || field === 'fields') {
                const selects = valueEl.querySelectorAll('select');
                newValue = Array.from(selects).map(select => select.value).filter(val => val);
            } else if (field === 'subjects') {
                const inputs = valueEl.querySelectorAll('input');
                newValue = Array.from(inputs).map(input => input.value.trim()).filter(val => val);
            } else {
                const input = valueEl.querySelector('input');
                newValue = input ? input.value.trim() : '';
            }

            if ((field === 'name' || field === 'family') && !newValue) {
                alert('این فیلد نمی‌تواند خالی باشد.');
                return;
            }

            fetch('/teacher/profile', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({field: field, value: newValue})
            }).then(res => res.json()).then(data => {
                if (data.success) {
                    // نمایش مقدار جدید
                    if (Array.isArray(newValue)) {
                        valueEl.innerHTML = newValue.length ? newValue.join(', ') : 'ندارد';
                    } else {
                        valueEl.innerHTML = newValue === '0' ? '0 (ندارد)' : newValue;
                    }
                    
                    controls.remove();
                    const editBtn = valueEl.nextElementSibling;
                    editBtn.style.display = 'flex';
                    
                    // اگر تعداد تغییر کرد، صفحه را رفرش کن
                    if (field.includes('_count')) {
                        setTimeout(() => location.reload(), 500);
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
    ''', user=user, grades_str=grades_str, fields_str=fields_str, subjects_str=subjects_str)

# ========== خروج ==========
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('home'))

@app.route('/teacher/logout')
def teacher_logout():
    session.pop('teacher', None)
    return redirect(url_for('home'))

# ========== صفحات placeholder ==========
@app.route('/login/<role>')
def other_login(role):
    roles = {'parent': 'والدین', 'student': 'دانش آموزان'}
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