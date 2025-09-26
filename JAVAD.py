from flask import Flask, render_template_string, request, session, redirect, url_for, jsonify
import os

app = Flask(__name__)
app.secret_key = 'very_secret_key_for_dabirestan_javade_aeme'

# رمز عبور ثابت مدیران
ADMIN_PASSWORD = "dabirestan012345"

# صفحه اصلی: چهار دکمه ورود
@app.route('/')
def home():
    return render_template_string('''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>دبیرستان پسرانه جوادالائمه</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazir:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        {{ style }}
    </style>
</head>
<body>
    <div class="container">
        <h1 class="welcome">به سایت رسمی دبیرستان پسرانه جوادالائمه خوش آمدید</h1>
        <div class="button-grid">
            <a href="/login/admin" class="btn-card primary">
                <h3>ورود مدیران</h3>
                <p>این بخش فقط برای مدیران است</p>
            </a>
            <a href="/login/teacher" class="btn-card accent">
                <h3>ورود معلمان</h3>
                <p>این بخش فقط برای معلمان است</p>
            </a>
            <a href="/login/parent" class="btn-card success">
                <h3>ورود والدین</h3>
                <p>این بخش فقط برای والدین است</p>
            </a>
            <a href="/login/student" class="btn-card info">
                <h3>ورود دانش آموزان</h3>
                <p>این بخش فقط برای دانش آموزان است</p>
            </a>
        </div>
        <footer class="footer">سازنده: محمدرضا محمدی دانش آموز دبیرستان جوادالائمه (رشته ریاضی)</footer>
    </div>

    <script>
        // Hover animation for cards
        document.querySelectorAll('.btn-card').forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-4px)';
                card.style.boxShadow = '0 6px 12px rgba(0,0,0,0.15)';
            });
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0)';
                card.style.boxShadow = '0 2px 6px rgba(0,0,0,0.1)';
            });
        });
    </script>
</body>
</html>

<style>
    :root {
        --primary: #2B7AFC;
        --accent: #FFB84D;
        --dark-text: #0F172A;
        --bg-light: #F7FAFF;
        --success: #34D399;
        --error: #EF4444;
    }

    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    body {
        font-family: 'Vazir', sans-serif;
        background: var(--bg-light);
        color: var(--dark-text);
        line-height: 1.5;
        padding: 20px;
    }

    .container {
        max-width: 1000px;
        margin: 0 auto;
        text-align: center;
    }

    .welcome {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 40px;
        color: var(--primary);
    }

    .button-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 24px;
        margin-bottom: 40px;
    }

    .btn-card {
        display: block;
        padding: 24px;
        border-radius: 16px;
        background: white;
        text-decoration: none;
        color: var(--dark-text);
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        text-align: center;
    }

    .btn-card.primary { background: linear-gradient(135deg, var(--primary), #1a6be0); color: white; }
    .btn-card.accent { background: linear-gradient(135deg, var(--accent), #e6a03d); color: white; }
    .btn-card.success { background: linear-gradient(135deg, var(--success), #2bb88a); color: white; }
    .btn-card.info { background: linear-gradient(135deg, #6366f1, #4f46e5); color: white; }

    .btn-card h3 {
        font-size: 18px;
        margin-bottom: 8px;
    }

    .btn-card p {
        font-size: 14px;
        opacity: 0.9;
    }

    .footer {
        margin-top: 40px;
        font-size: 14px;
        color: #64748b;
    }
</style>
    ''')

# صفحه ورود مدیران
@app.route('/login/admin', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        family = request.form.get('family', '').strip()
        role = request.form.get('role', '')
        password = request.form.get('password', '')

        if not name or not family or not role or not password:
            error = "لطفاً تمامی فیلدها را پر کنید."
        elif password != ADMIN_PASSWORD:
            error = "رمز عبور اشتباه است."
        else:
            session['admin'] = {
                'name': name,
                'family': family,
                'role': role
            }
            return redirect(url_for('admin_dashboard'))

    return render_template_string('''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>ورود مدیران</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazir:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        {{ style }}
    </style>
</head>
<body>
    <div class="container">
        <h2>ورود مدیران</h2>
        <form method="POST" class="login-form">
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
            {% if error %}
            <div class="alert error">{{ error }}</div>
            {% endif %}
            <button type="submit" class="btn-primary">ورود</button>
        </form>
        <a href="/" class="back-link">بازگشت به صفحه اصلی</a>
    </div>

    <style>
        :root {
            --primary: #2B7AFC;
            --error: #EF4444;
            --bg-light: #F7FAFF;
            --dark-text: #0F172A;
        }
        body {
            font-family: 'Vazir', sans-serif;
            background: var(--bg-light);
            color: var(--dark-text);
            padding: 40px 20px;
        }
        .container {
            max-width: 500px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
        h2 {
            text-align: center;
            margin-bottom: 24px;
            color: var(--primary);
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 6px;
            font-weight: 500;
        }
        input, select {
            width: 100%;
            padding: 12px;
            border: 1px solid #cbd5e1;
            border-radius: 12px;
            font-size: 16px;
            direction: rtl;
        }
        .btn-primary {
            background: var(--primary);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 12px;
            width: 100%;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .btn-primary:hover {
            background: #1f63d6;
            transform: translateY(-2px);
        }
        .alert {
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 16px;
            text-align: center;
        }
        .error {
            background: #fee2e2;
            color: var(--error);
            border: 1px solid var(--error);
        }
        .back-link {
            display: block;
            text-align: center;
            margin-top: 20px;
            color: var(--primary);
            text-decoration: none;
        }
    </style>
</body>
</html>
    ''', error=error)

# درگاه مدیران
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    user = session['admin']
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
        {{ style }}
    </style>
</head>
<body>
    <!-- تولبار -->
    <header class="toolbar">
        <div class="toolbar-left">
            <button class="menu-toggle" id="menuToggle">
                <i class="fas fa-bars"></i>
            </button>
            <span>صفحه اصلی</span>
        </div>
        <div class="toolbar-center">اعلانات</div>
        <div class="toolbar-right">
            <button class="profile-btn" id="profileBtn">پروفایل</button>
        </div>
    </header>

    <!-- منوی کشویی -->
    <div class="sidebar" id="sidebar">
        <div class="sidebar-content">
            <button class="close-btn" id="closeSidebar">&times;</button>
            <a href="#" class="sidebar-item">صفحه اصلی</a>
            <a href="#" class="sidebar-item" id="sidebarProfile">پروفایل</a>
            <a href="#" class="sidebar-item">اعلانات</a>
        </div>
    </div>

    <!-- صفحه اصلی درگاه -->
    <div class="dashboard">
        <h2>درگاه مدیران</h2>
        <div class="cards-grid">
            {% for item in items %}
            <div class="card">{{ item }}</div>
            {% endfor %}
        </div>
    </div>

    <!-- مدال پروفایل -->
    <div class="modal" id="profileModal" style="display:none;">
        <div class="modal-content">
            <span class="close" id="closeProfile">&times;</span>
            <h3>پروفایل کاربری</h3>
            <div class="profile-field">
                <span>نام:</span>
                <span id="nameText">{{ user.name }}</span>
                <button class="edit-btn" onclick="editField('name')"><i class="fas fa-pencil-alt"></i></button>
            </div>
            <div class="profile-field">
                <span>نام خانوادگی:</span>
                <span id="familyText">{{ user.family }}</span>
                <button class="edit-btn" onclick="editField('family')"><i class="fas fa-pencil-alt"></i></button>
            </div>
            <div class="profile-field">
                <span>مرتبه:</span>
                <span id="roleText">{{ user.role }}</span>
                <button class="edit-btn" onclick="editField('role')"><i class="fas fa-pencil-alt"></i></button>
            </div>
            <div class="profile-field">
                <span>رمز عبور:</span>
                <span>********</span>
                <span style="color:#94a3b8; font-size:12px;">(غیرقابل تغییر)</span>
            </div>
            <button class="btn-logout" onclick="confirmLogout()">خروج از حساب</button>
        </div>
    </div>

    <!-- مدال تأیید خروج -->
    <div class="modal" id="logoutModal" style="display:none;">
        <div class="modal-content">
            <p>آیا مطمئن هستید می‌خواهید از حساب خارج شوید؟</p>
            <div class="modal-buttons">
                <button class="btn-ghost" onclick="closeLogout()">خیر</button>
                <button class="btn-primary" onclick="logout()">بله</button>
            </div>
        </div>
    </div>

    <script>
        // مدیریت منوی کشویی
        document.getElementById('menuToggle').addEventListener('click', () => {
            document.getElementById('sidebar').style.transform = 'translateX(0)';
        });
        document.getElementById('closeSidebar').addEventListener('click', () => {
            document.getElementById('sidebar').style.transform = 'translateX(100%)';
        });

        // باز کردن پروفایل از تولبار و منو
        const openProfile = () => {
            document.getElementById('profileModal').style.display = 'block';
        };
        document.getElementById('profileBtn').addEventListener('click', openProfile);
        document.getElementById('sidebarProfile').addEventListener('click', openProfile);

        // بستن مدال پروفایل
        document.getElementById('closeProfile').addEventListener('click', () => {
            document.getElementById('profileModal').style.display = 'none';
        });

        // ویرایش فیلدها
        function editField(field) {
            const textEl = document.getElementById(field + 'Text');
            const currentValue = textEl.innerText;
            const isRole = field === 'role';

            // حذف متن و اضافه کردن فیلد ورودی
            textEl.innerHTML = '';
            const input = document.createElement('input');
            input.type = 'text';
            input.value = currentValue;
            input.className = 'edit-input';
            if (isRole) {
                input.type = 'select';
                const select = document.createElement('select');
                ['مدیر', 'ناظم', 'معاون', 'مشاور'].forEach(r => {
                    const opt = document.createElement('option');
                    opt.value = r;
                    opt.innerText = r;
                    if (r === currentValue) opt.selected = true;
                    select.appendChild(opt);
                });
                textEl.appendChild(select);
            } else {
                textEl.appendChild(input);
            }

            // دکمه‌های تأیید و انصراف
            const btns = document.createElement('div');
            btns.className = 'edit-buttons';
            btns.innerHTML = `
                <button class="btn-ghost" onclick="cancelEdit('${field}')">انصراف</button>
                <button class="btn-primary" onclick="saveEdit('${field}', ${isRole})">تایید</button>
            `;
            textEl.parentNode.appendChild(btns);
        }

        function cancelEdit(field) {
            location.reload(); // ساده‌ترین راه برای بازگشت به حالت اولیه
        }

        function saveEdit(field, isRole) {
            let newValue;
            if (isRole) {
                newValue = document.querySelector('#' + field + 'Text select').value;
            } else {
                newValue = document.querySelector('#' + field + 'Text input').value;
            }
            if (!newValue.trim()) return alert('مقدار نمی‌تواند خالی باشد.');

            // به‌روزرسانی session از طریق POST (در اینجا برای سادگی با reload)
            fetch('/admin/update_profile', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({field: field, value: newValue})
            }).then(() => {
                document.getElementById(field + 'Text').innerText = newValue;
                document.querySelector('.edit-buttons').remove();
            });
        }

        // خروج
        function confirmLogout() {
            document.getElementById('profileModal').style.display = 'none';
            document.getElementById('logoutModal').style.display = 'block';
        }
        function closeLogout() {
            document.getElementById('logoutModal').style.display = 'none';
        }
        function logout() {
            window.location.href = '/admin/logout';
        }
    </script>

    <style>
        :root {
            --primary: #2B7AFC;
            --accent: #FFB84D;
            --dark-text: #0F172A;
            --bg-light: #F7FAFF;
            --success: #34D399;
            --error: #EF4444;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Vazir', sans-serif;
            background: var(--bg-light);
            color: var(--dark-text);
        }

        .toolbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 20px;
            background: white;
            box-shadow: 0 2px 6px rgba(0,0,0,0.08);
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .toolbar-left {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .menu-toggle {
            background: none;
            border: none;
            font-size: 20px;
            cursor: pointer;
            color: var(--primary);
        }

        .toolbar-center {
            font-weight: bold;
            font-size: 16px;
        }

        .toolbar-right .profile-btn {
            background: var(--primary);
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 8px;
            cursor: pointer;
        }

        .sidebar {
            position: fixed;
            top: 0;
            right: 0;
            height: 100%;
            width: 300px;
            background: white;
            box-shadow: -4px 0 12px rgba(0,0,0,0.1);
            transform: translateX(100%);
            transition: transform 0.3s ease;
            z-index: 200;
        }

        .sidebar-content {
            padding: 20px;
        }

        .close-btn {
            float: left;
            font-size: 28px;
            background: none;
            border: none;
            cursor: pointer;
            color: #94a3b8;
        }

        .sidebar-item {
            display: block;
            padding: 12px 0;
            text-decoration: none;
            color: var(--dark-text);
            font-size: 16px;
        }

        .dashboard {
            padding: 20px;
        }

        .dashboard h2 {
            margin-bottom: 24px;
            color: var(--primary);
        }

        .cards-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 20px;
        }

        .card {
            background: white;
            padding: 20px;
            border-radius: 16px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            text-align: center;
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .card:hover {
            transform: translateY(-4px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }

        .modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 300;
        }

        .modal-content {
            background: white;
            padding: 24px;
            border-radius: 16px;
            width: 90%;
            max-width: 500px;
            position: relative;
        }

        .close {
            position: absolute;
            top: 10px;
            left: 15px;
            font-size: 28px;
            cursor: pointer;
            color: #94a3b8;
        }

        .profile-field {
            display: flex;
            align-items: center;
            margin: 16px 0;
            gap: 10px;
        }

        .profile-field span:first-child {
            min-width: 100px;
            font-weight: 500;
        }

        .edit-btn {
            background: none;
            border: none;
            color: var(--primary);
            cursor: pointer;
            font-size: 14px;
        }

        .edit-input {
            padding: 6px 10px;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            direction: rtl;
        }

        .edit-buttons {
            display: flex;
            gap: 10px;
            margin-top: 8px;
        }

        .btn-logout {
            background: var(--error);
            color: white;
            border: none;
            padding: 10px;
            border-radius: 8px;
            width: 100%;
            margin-top: 20px;
            cursor: pointer;
        }

        .modal-buttons {
            display: flex;
            gap: 10px;
            margin-top: 20px;
            justify-content: flex-end;
        }

        /* دکمه‌های عمومی */
        .btn-primary {
            background: var(--primary);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .btn-ghost {
            background: transparent;
            border: 1px solid #cbd5e1;
            padding: 10px 20px;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .btn-ghost:hover {
            background: rgba(43,122,252,0.08);
        }
    </style>
</body>
</html>
    ''', user=user, items=[
        "مدیریت دانش آموزان",
        "مدیریت معلمان",
        "مدیریت گزارشات والدین",
        "مدیریت گزارشات معلمان",
        "مدیریت گزارشات دانش آموزان",
        "مدیریت بخش آزمایشگاه",
        "مدیریت نمرات",
        "مدیریت کارنامه"
    ])

# به‌روزرسانی پروفایل (AJAX)
@app.route('/admin/update_profile', methods=['POST'])
def update_profile():
    if 'admin' not in session:
        return jsonify(success=False), 403
    data = request.get_json()
    field = data.get('field')
    value = data.get('value')
    if field in ['name', 'family', 'role'] and value:
        session['admin'][field] = value
        return jsonify(success=True)
    return jsonify(success=False), 400

# خروج از حساب
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('home'))

# سایر ورودها (معلمان، والدین، دانش‌آموزان) — فقط صفحه placeholder
@app.route('/login/<role>')
def other_login(role):
    roles = {
        'teacher': 'معلمان',
        'parent': 'والدین',
        'student': 'دانش آموزان'
    }
    return f'''
    <div style="text-align:center; padding:50px; font-family:Vazir, sans-serif; direction:rtl;">
        <h2>ورود {roles.get(role, 'کاربر')}</h2>
        <p>این بخش در حال توسعه است.</p>
        <a href="/" style="color:#2B7AFC; text-decoration:underline;">بازگشت به صفحه اصلی</a>
    </div>
    '''

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))