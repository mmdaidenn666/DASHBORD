from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'dabirestan012345_secret_key'

# داده‌های ذخیره‌سازی
DATA_FILE = 'school_data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'users': {},
        'students': {
            'tenth': {'math': [], 'experimental': [], 'humanities': []},
            'eleventh': {'math': [], 'experimental': [], 'humanities': []},
            'twelfth': {'math': [], 'experimental': [], 'humanities': []}
        },
        'teachers': [],
        'reports': []
    }

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# صفحه اصلی - لاگین
@app.route('/')
def login_page():
    return '''
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ورود - سایت رسمی مدیر</title>
        <style>
            :root {
                --primary-dark: #1a365d;
                --primary-blue: #2d3748;
                --gray-light: #f7fafc;
                --gray-medium: #e2e8f0;
                --silver: #cbd5e0;
                --white: #ffffff;
                --accent-green: #2d5a27;
                --accent-gold: #b7791f;
                --shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                --transition: all 0.3s ease;
            }

            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Vazir', 'Iran Sans', Tahoma, sans-serif;
            }

            body {
                background: linear-gradient(135deg, var(--primary-dark), var(--primary-blue));
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 1rem;
            }

            .login-container {
                background-color: var(--white);
                border-radius: 15px;
                padding: 2.5rem;
                box-shadow: var(--shadow);
                width: 100%;
                max-width: 450px;
                animation: fadeIn 0.8s ease;
            }

            .welcome-text {
                text-align: center;
                color: var(--primary-dark);
                font-size: 1.8rem;
                margin-bottom: 2rem;
                font-weight: bold;
            }

            .school-name {
                color: var(--accent-green);
                display: block;
                font-size: 1.4rem;
                margin-top: 0.5rem;
            }

            .form-group {
                margin-bottom: 1.5rem;
            }

            label {
                display: block;
                margin-bottom: 0.5rem;
                font-weight: bold;
                color: var(--primary-blue);
            }

            input, select {
                width: 100%;
                padding: 0.75rem;
                border: 2px solid var(--silver);
                border-radius: 8px;
                font-size: 1rem;
                transition: var(--transition);
            }

            input:focus, select:focus {
                outline: none;
                border-color: var(--accent-green);
                box-shadow: 0 0 0 3px rgba(45, 90, 39, 0.2);
            }

            .btn {
                width: 100%;
                padding: 0.75rem;
                background-color: var(--accent-green);
                color: var(--white);
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 1.1rem;
                transition: var(--transition);
                margin-top: 1rem;
            }

            .btn:hover {
                background-color: #23421f;
                transform: translateY(-2px);
                box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
            }

            .error-message {
                color: #e53e3e;
                text-align: center;
                margin-top: 1rem;
                display: none;
            }

            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }

            @media (max-width: 480px) {
                .login-container {
                    padding: 1.5rem;
                }
                
                .welcome-text {
                    font-size: 1.5rem;
                }
            }
        </style>
    </head>
    <body>
        <div class="login-container">
            <h1 class="welcome-text">
                به سایت رسمی مدیر
                <span class="school-name">دبیرستان جوادالائمه</span>
                خوش آمدید
            </h1>
            
            <form id="loginForm">
                <div class="form-group">
                    <label for="firstName">نام</label>
                    <input type="text" id="firstName" name="firstName" required>
                </div>
                
                <div class="form-group">
                    <label for="lastName">نام خانوادگی</label>
                    <input type="text" id="lastName" name="lastName" required>
                </div>
                
                <div class="form-group">
                    <label for="role">مرتبه</label>
                    <select id="role" name="role" required>
                        <option value="">انتخاب کنید</option>
                        <option value="manager">مدیر</option>
                        <option value="supervisor">ناظم</option>
                        <option value="assistant">معاون</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="password">رمز</label>
                    <input type="password" id="password" name="password" required>
                </div>
                
                <button type="submit" class="btn">ورود به سیستم</button>
                
                <div class="error-message" id="errorMessage"></div>
            </form>
        </div>

        <script>
            document.getElementById('loginForm').addEventListener('submit', function(e) {
                e.preventDefault();
                
                const firstName = document.getElementById('firstName').value;
                const lastName = document.getElementById('lastName').value;
                const role = document.getElementById('role').value;
                const password = document.getElementById('password').value;
                const errorMessage = document.getElementById('errorMessage');
                
                // اعتبارسنجی
                if (!firstName || !lastName || !role || !password) {
                    errorMessage.textContent = 'لطفا تمام فیلدها را پر کنید';
                    errorMessage.style.display = 'block';
                    return;
                }
                
                if (password !== 'dabirestan012345') {
                    errorMessage.textContent = 'رمز وارد شده صحیح نیست';
                    errorMessage.style.display = 'block';
                    return;
                }
                
                // ذخیره اطلاعات کاربر
                const userData = {
                    firstName: firstName,
                    lastName: lastName,
                    role: role
                };
                localStorage.setItem('currentUser', JSON.stringify(userData));
                
                // انتقال به صفحه اصلی
                window.location.href = '/main';
            });
        </script>
    </body>
    </html>
    '''

# صفحه اصلی
@app.route('/main')
def main_page():
    return '''
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>درگاه مدیران - دبیرستان جوادالائمه</title>
        <style>
            :root {
                --primary-dark: #1a365d;
                --primary-blue: #2d3748;
                --gray-light: #f7fafc;
                --gray-medium: #e2e8f0;
                --silver: #cbd5e0;
                --white: #ffffff;
                --accent-green: #2d5a27;
                --accent-gold: #b7791f;
                --shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                --transition: all 0.3s ease;
            }

            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Vazir', 'Iran Sans', Tahoma, sans-serif;
            }

            body {
                background-color: var(--gray-light);
                color: var(--primary-blue);
                min-height: 100vh;
            }

            header {
                background-color: var(--primary-dark);
                color: var(--white);
                padding: 1rem 0;
                box-shadow: var(--shadow);
                position: sticky;
                top: 0;
                z-index: 1000;
            }

            .container {
                width: 100%;
                max-width: 1200px;
                margin: 0 auto;
                padding: 0 15px;
            }

            .header-content {
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .logo {
                font-size: 1.5rem;
                font-weight: bold;
            }

            .user-info {
                display: flex;
                align-items: center;
                gap: 1rem;
            }

            .hamburger-menu {
                display: none;
                flex-direction: column;
                cursor: pointer;
                width: 30px;
                height: 25px;
                justify-content: space-between;
            }

            .hamburger-line {
                height: 3px;
                width: 100%;
                background-color: var(--white);
                border-radius: 2px;
                transition: var(--transition);
            }

            .welcome-text {
                text-align: center;
                margin: 2rem 0;
                font-size: 2rem;
                color: var(--primary-dark);
                animation: fadeIn 1s ease;
            }

            .card-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 2rem;
                padding: 2rem 0;
            }

            .card {
                background-color: var(--white);
                border-radius: 15px;
                padding: 2rem;
                box-shadow: var(--shadow);
                transition: var(--transition);
                cursor: pointer;
                border: 1px solid var(--gray-medium);
                text-align: center;
                animation: slideUp 0.6s ease;
            }

            .card:hover {
                transform: translateY(-10px);
                box-shadow: 0 15px 30px rgba(0, 0, 0, 0.15);
            }

            .card h3 {
                margin-bottom: 1rem;
                color: var(--primary-dark);
                font-size: 1.3rem;
            }

            .card-icon {
                font-size: 3rem;
                margin-bottom: 1rem;
            }

            .mobile-sidebar {
                position: fixed;
                top: 0;
                right: -100%;
                width: 80%;
                max-width: 300px;
                height: 100vh;
                background-color: var(--primary-dark);
                z-index: 2000;
                transition: var(--transition);
                padding: 2rem 1rem;
                overflow-y: auto;
            }

            .mobile-sidebar.active {
                right: 0;
            }

            .close-sidebar {
                position: absolute;
                top: 1rem;
                left: 1rem;
                color: var(--white);
                font-size: 1.5rem;
                cursor: pointer;
            }

            .sidebar-menu {
                list-style: none;
                margin-top: 2rem;
            }

            .sidebar-menu li {
                margin-bottom: 1rem;
            }

            .sidebar-menu a {
                color: var(--white);
                text-decoration: none;
                display: block;
                padding: 0.75rem;
                border-radius: 8px;
                transition: var(--transition);
            }

            .sidebar-menu a:hover {
                background-color: rgba(255, 255, 255, 0.1);
                transform: translateX(-5px);
            }

            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }

            @keyframes slideUp {
                from { 
                    opacity: 0;
                    transform: translateY(30px);
                }
                to { 
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            @media (max-width: 768px) {
                .hamburger-menu {
                    display: flex;
                }
                
                .welcome-text {
                    font-size: 1.5rem;
                }
                
                .card-grid {
                    grid-template-columns: 1fr;
                    gap: 1.5rem;
                }
            }
        </style>
    </head>
    <body>
        <header>
            <div class="container">
                <div class="header-content">
                    <div class="logo">دبیرستان جوادالائمه</div>
                    <div class="user-info">
                        <span id="userWelcome">خوش آمدید</span>
                        <div class="hamburger-menu" id="hamburgerMenu">
                            <div class="hamburger-line"></div>
                            <div class="hamburger-line"></div>
                            <div class="hamburger-line"></div>
                        </div>
                    </div>
                </div>
            </div>
        </header>

        <div class="mobile-sidebar" id="mobileSidebar">
            <div class="close-sidebar" id="closeSidebar">×</div>
            <ul class="sidebar-menu">
                <li><a href="/main">صفحه اصلی</a></li>
                <li><a href="/students">مدیریت دانش آموزان</a></li>
                <li><a href="/teachers">مدیریت معلمان</a></li>
                <li><a href="/parent-reports">مدیریت گزارشات والدین</a></li>
                <li><a href="/teacher-reports">مدیریت گزارشات معلمان</a></li>
                <li><a href="/student-reports">مدیریت گزارشات دانش آموزان</a></li>
                <li><a href="/lab">مدیریت بخش آزمایشگاه</a></li>
                <li><a href="/grades">مدیریت نمرات</a></li>
                <li><a href="/report-cards">مدیریت کارنامه</a></li>
                <li><a href="/profile">پروفایل</a></li>
                <li><a href="#" id="sidebarLogout">خروج</a></li>
            </ul>
        </div>

        <div class="container">
            <h1 class="welcome-text">درگاه مدیران</h1>
            
            <div class="card-grid">
                <div class="card" onclick="window.location.href='/students'">
                    <div class="card-icon">👨‍🎓</div>
                    <h3>مدیریت دانش آموزان</h3>
                </div>
                
                <div class="card" onclick="window.location.href='/teachers'">
                    <div class="card-icon">👨‍🏫</div>
                    <h3>مدیریت معلمان</h3>
                </div>
                
                <div class="card" onclick="window.location.href='/parent-reports'">
                    <div class="card-icon">👨‍👩‍👧‍👦</div>
                    <h3>مدیریت گزارشات والدین</h3>
                </div>
                
                <div class="card" onclick="window.location.href='/teacher-reports'">
                    <div class="card-icon">📊</div>
                    <h3>مدیریت گزارشات معلمان</h3>
                </div>
                
                <div class="card" onclick="window.location.href='/student-reports'">
                    <div class="card-icon">📝</div>
                    <h3>مدیریت گزارشات دانش آموزان</h3>
                </div>
                
                <div class="card" onclick="window.location.href='/lab'">
                    <div class="card-icon">🔬</div>
                    <h3>مدیریت بخش آزمایشگاه</h3>
                </div>
                
                <div class="card" onclick="window.location.href='/grades'">
                    <div class="card-icon">📚</div>
                    <h3>مدیریت نمرات</h3>
                </div>
                
                <div class="card" onclick="window.location.href='/report-cards'">
                    <div class="card-icon">🏆</div>
                    <h3>مدیریت کارنامه</h3>
                </div>
            </div>
        </div>

        <script>
            // بارگذاری اطلاعات کاربر
            const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
            if (!currentUser.firstName) {
                window.location.href = '/';
            }
            
            document.getElementById('userWelcome').textContent = `خوش آمدید ${currentUser.firstName} ${currentUser.lastName}`;
            
            // مدیریت منوی موبایل
            document.getElementById('hamburgerMenu').addEventListener('click', () => {
                document.getElementById('mobileSidebar').classList.add('active');
            });
            
            document.getElementById('closeSidebar').addEventListener('click', () => {
                document.getElementById('mobileSidebar').classList.remove('active');
            });
            
            // خروج از سیستم
            document.getElementById('sidebarLogout').addEventListener('click', (e) => {
                e.preventDefault();
                if (confirm('آیا مطمئن هستید می‌خواهید از حساب خارج شوید؟')) {
                    localStorage.removeItem('currentUser');
                    window.location.href = '/';
                }
            });
        </script>
    </body>
    </html>
    '''

# صفحه مدیریت دانش آموزان
@app.route('/students')
def students_page():
    return '''
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>مدیریت دانش آموزان - دبیرستان جوادالائمه</title>
        <style>
            :root {
                --primary-dark: #1a365d;
                --primary-blue: #2d3748;
                --gray-light: #f7fafc;
                --gray-medium: #e2e8f0;
                --silver: #cbd5e0;
                --white: #ffffff;
                --accent-green: #2d5a27;
                --accent-gold: #b7791f;
                --shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                --transition: all 0.3s ease;
            }

            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Vazir', 'Iran Sans', Tahoma, sans-serif;
            }

            body {
                background-color: var(--gray-light);
                color: var(--primary-blue);
                min-height: 100vh;
            }

            header {
                background-color: var(--primary-dark);
                color: var(--white);
                padding: 1rem 0;
                box-shadow: var(--shadow);
                position: sticky;
                top: 0;
                z-index: 1000;
            }

            .container {
                width: 100%;
                max-width: 1200px;
                margin: 0 auto;
                padding: 0 15px;
            }

            .header-content {
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .logo {
                font-size: 1.5rem;
                font-weight: bold;
            }

            .nav-buttons {
                display: flex;
                gap: 1rem;
            }

            .btn {
                padding: 0.5rem 1rem;
                background-color: var(--accent-green);
                color: var(--white);
                border: none;
                border-radius: 5px;
                cursor: pointer;
                text-decoration: none;
                transition: var(--transition);
            }

            .btn:hover {
                background-color: #23421f;
            }

            .btn-secondary {
                background-color: var(--silver);
                color: var(--primary-blue);
            }

            .welcome-text {
                text-align: center;
                margin: 2rem 0;
                font-size: 2rem;
                color: var(--primary-dark);
            }

            .grades-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 2rem;
                padding: 2rem 0;
            }

            .grade-card {
                background-color: var(--white);
                border-radius: 15px;
                padding: 2rem;
                box-shadow: var(--shadow);
                transition: var(--transition);
                cursor: pointer;
                border: 2px solid transparent;
                text-align: center;
            }

            .grade-card:hover {
                transform: translateY(-5px);
                border-color: var(--accent-green);
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
            }

            .grade-icon {
                font-size: 4rem;
                margin-bottom: 1rem;
            }

            .grade-title {
                font-size: 1.5rem;
                color: var(--primary-dark);
                margin-bottom: 1rem;
            }

            .grade-description {
                color: var(--primary-blue);
                line-height: 1.6;
            }

            .back-btn {
                margin-bottom: 2rem;
            }

            @media (max-width: 768px) {
                .grades-grid {
                    grid-template-columns: 1fr;
                }
                
                .nav-buttons {
                    flex-direction: column;
                    gap: 0.5rem;
                }
            }
        </style>
    </head>
    <body>
        <header>
            <div class="container">
                <div class="header-content">
                    <div class="logo">مدیریت دانش آموزان</div>
                    <div class="nav-buttons">
                        <a href="/main" class="btn btn-secondary">بازگشت به صفحه اصلی</a>
                    </div>
                </div>
            </div>
        </header>

        <div class="container">
            <h1 class="welcome-text">مدیریت دانش آموزان</h1>
            
            <div class="grades-grid">
                <div class="grade-card" onclick="window.location.href='/students/tenth'">
                    <div class="grade-icon">🔟</div>
                    <h2 class="grade-title">پایه دهم</h2>
                    <p class="grade-description">مدیریت دانش آموزان پایه دهم در تمامی رشته‌ها</p>
                </div>
                
                <div class="grade-card" onclick="window.location.href='/students/eleventh'">
                    <div class="grade-icon">1️⃣1️⃣</div>
                    <h2 class="grade-title">پایه یازدهم</h2>
                    <p class="grade-description">مدیریت دانش آموزان پایه یازدهم در تمامی رشته‌ها</p>
                </div>
                
                <div class="grade-card" onclick="window.location.href='/students/twelfth'">
                    <div class="grade-icon">1️⃣2️⃣</div>
                    <h2 class="grade-title">پایه دوازدهم</h2>
                    <p class="grade-description">مدیریت دانش آموزان پایه دوازدهم در تمامی رشته‌ها</p>
                </div>
            </div>
        </div>

        <script>
            // بررسی لاگین
            const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
            if (!currentUser.firstName) {
                window.location.href = '/';
            }
        </script>
    </body>
    </html>
    '''

# صفحه پایه دهم
@app.route('/students/tenth')
def tenth_grade_page():
    return '''
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>پایه دهم - دبیرستان جوادالائمه</title>
        <style>
            :root {
                --primary-dark: #1a365d;
                --primary-blue: #2d3748;
                --gray-light: #f7fafc;
                --gray-medium: #e2e8f0;
                --silver: #cbd5e0;
                --white: #ffffff;
                --accent-green: #2d5a27;
                --accent-gold: #b7791f;
                --shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                --transition: all 0.3s ease;
            }

            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Vazir', 'Iran Sans', Tahoma, sans-serif;
            }

            body {
                background-color: var(--gray-light);
                color: var(--primary-blue);
                min-height: 100vh;
            }

            header {
                background-color: var(--primary-dark);
                color: var(--white);
                padding: 1rem 0;
                box-shadow: var(--shadow);
                position: sticky;
                top: 0;
                z-index: 1000;
            }

            .container {
                width: 100%;
                max-width: 1200px;
                margin: 0 auto;
                padding: 0 15px;
            }

            .header-content {
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .logo {
                font-size: 1.5rem;
                font-weight: bold;
            }

            .nav-buttons {
                display: flex;
                gap: 1rem;
            }

            .btn {
                padding: 0.5rem 1rem;
                background-color: var(--accent-green);
                color: var(--white);
                border: none;
                border-radius: 5px;
                cursor: pointer;
                text-decoration: none;
                transition: var(--transition);
            }

            .btn:hover {
                background-color: #23421f;
            }

            .btn-secondary {
                background-color: var(--silver);
                color: var(--primary-blue);
            }

            .welcome-text {
                text-align: center;
                margin: 2rem 0;
                font-size: 2rem;
                color: var(--primary-dark);
            }

            .fields-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 2rem;
                padding: 2rem 0;
            }

            .field-card {
                background-color: var(--white);
                border-radius: 15px;
                padding: 2rem;
                box-shadow: var(--shadow);
                transition: var(--transition);
                cursor: pointer;
                border: 2px solid transparent;
                text-align: center;
            }

            .field-card:hover {
                transform: translateY(-5px);
                border-color: var(--accent-gold);
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
            }

            .field-icon {
                font-size: 3rem;
                margin-bottom: 1rem;
            }

            .field-title {
                font-size: 1.5rem;
                color: var(--primary-dark);
                margin-bottom: 1rem;
            }

            .field-description {
                color: var(--primary-blue);
                line-height: 1.6;
            }

            @media (max-width: 768px) {
                .fields-grid {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <header>
            <div class="container">
                <div class="header-content">
                    <div class="logo">پایه دهم</div>
                    <div class="nav-buttons">
                        <a href="/students" class="btn btn-secondary">بازگشت</a>
                        <a href="/main" class="btn btn-secondary">صفحه اصلی</a>
                    </div>
                </div>
            </div>
        </header>

        <div class="container">
            <h1 class="welcome-text">پایه دهم - انتخاب رشته</h1>
            
            <div class="fields-grid">
                <div class="field-card" onclick="window.location.href='/students/tenth/math'">
                    <div class="field-icon">∫</div>
                    <h2 class="field-title">رشته ریاضی</h2>
                    <p class="field-description">مدیریت دانش آموزان رشته ریاضی فیزیک</p>
                </div>
                
                <div class="field-card" onclick="window.location.href='/students/tenth/experimental'">
                    <div class="field-icon">🧪</div>
                    <h2 class="field-title">رشته تجربی</h2>
                    <p class="field-description">مدیریت دانش آموزان رشته علوم تجربی</p>
                </div>
                
                <div class="field-card" onclick="window.location.href='/students/tenth/humanities'">
                    <div class="field-icon">📚</div>
                    <h2 class="field-title">رشته انسانی</h2>
                    <p class="field-description">مدیریت دانش آموزان رشته علوم انسانی</p>
                </div>
            </div>
        </div>

        <script>
            // بررسی لاگین
            const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
            if (!currentUser.firstName) {
                window.location.href = '/';
            }
        </script>
    </body>
    </html>
    '''

# صفحه رشته ریاضی پایه دهم
@app.route('/students/tenth/math')
def tenth_math_page():
    return render_student_management_page('دهم', 'ریاضی')

# تابع برای تولید صفحه مدیریت دانش آموزان
def render_student_management_page(grade, field):
    return f'''
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>پایه {grade} - رشته {field}</title>
        <style>
            :root {{
                --primary-dark: #1a365d;
                --primary-blue: #2d3748;
                --gray-light: #f7fafc;
                --gray-medium: #e2e8f0;
                --silver: #cbd5e0;
                --white: #ffffff;
                --accent-green: #2d5a27;
                --accent-gold: #b7791f;
                --shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                --transition: all 0.3s ease;
            }}

            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Vazir', 'Iran Sans', Tahoma, sans-serif;
            }}

            body {{
                background-color: var(--gray-light);
                color: var(--primary-blue);
                min-height: 100vh;
            }}

            header {{
                background-color: var(--primary-dark);
                color: var(--white);
                padding: 1rem 0;
                box-shadow: var(--shadow);
                position: sticky;
                top: 0;
                z-index: 1000;
            }}

            .container {{
                width: 100%;
                max-width: 1200px;
                margin: 0 auto;
                padding: 0 15px;
            }}

            .header-content {{
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}

            .logo {{
                font-size: 1.5rem;
                font-weight: bold;
            }}

            .nav-buttons {{
                display: flex;
                gap: 1rem;
            }}

            .btn {{
                padding: 0.5rem 1rem;
                background-color: var(--accent-green);
                color: var(--white);
                border: none;
                border-radius: 5px;
                cursor: pointer;
                text-decoration: none;
                transition: var(--transition);
            }}

            .btn:hover {{
                background-color: #23421f;
            }}

            .btn-secondary {{
                background-color: var(--silver);
                color: var(--primary-blue);
            }}

            .student-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin: 2rem 0;
                padding: 1.5rem;
                background-color: var(--white);
                border-radius: 10px;
                box-shadow: var(--shadow);
            }}

            .student-count {{
                display: flex;
                align-items: center;
                font-size: 1.2rem;
                gap: 0.5rem;
            }}

            .search-container {{
                display: flex;
                gap: 0.5rem;
            }}

            .search-input {{
                padding: 0.5rem;
                border: 1px solid var(--silver);
                border-radius: 5px;
                width: 250px;
            }}

            .student-list {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 1.5rem;
                margin-bottom: 4rem;
            }}

            .student-card {{
                background-color: var(--white);
                border-radius: 10px;
                padding: 1.5rem;
                box-shadow: var(--shadow);
                transition: var(--transition);
                border: 1px solid var(--gray-medium);
                position: relative;
            }}

            .student-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
            }}

            .student-name {{
                font-size: 1.2rem;
                font-weight: bold;
                margin-bottom: 0.5rem;
                color: var(--primary-dark);
            }}

            .student-national-code {{
                color: var(--primary-blue);
                margin-bottom: 1rem;
            }}

            .student-actions {{
                display: flex;
                justify-content: flex-end;
                gap: 0.5rem;
                margin-top: 1rem;
            }}

            .action-btn {{
                width: 35px;
                height: 35px;
                border-radius: 50%;
                display: flex;
                justify-content: center;
                align-items: center;
                cursor: pointer;
                transition: var(--transition);
            }}

            .edit-btn {{
                background-color: var(--accent-gold);
                color: var(--white);
            }}

            .delete-btn {{
                background-color: #c53030;
                color: var(--white);
            }}

            .add-student-btn {{
                position: fixed;
                bottom: 2rem;
                left: 2rem;
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background-color: var(--accent-green);
                color: var(--white);
                display: flex;
                justify-content: center;
                align-items: center;
                font-size: 1.5rem;
                box-shadow: var(--shadow);
                cursor: pointer;
                z-index: 100;
                transition: var(--transition);
            }}

            .add-student-btn:hover {{
                transform: scale(1.1);
            }}

            /* مودال */
            .modal-overlay {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.5);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 3000;
                opacity: 0;
                visibility: hidden;
                transition: var(--transition);
            }}

            .modal-overlay.active {{
                opacity: 1;
                visibility: visible;
            }}

            .modal {{
                background-color: var(--white);
                border-radius: 10px;
                padding: 2rem;
                width: 90%;
                max-width: 500px;
                max-height: 90vh;
                overflow-y: auto;
                transform: translateY(20px);
                transition: var(--transition);
            }}

            .modal-overlay.active .modal {{
                transform: translateY(0);
            }}

            .modal-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1.5rem;
            }}

            .modal-title {{
                font-size: 1.5rem;
                color: var(--primary-dark);
            }}

            .close-modal {{
                background: none;
                border: none;
                font-size: 1.5rem;
                cursor: pointer;
                color: var(--primary-blue);
            }}

            .form-group {{
                margin-bottom: 1.5rem;
            }}

            label {{
                display: block;
                margin-bottom: 0.5rem;
                font-weight: bold;
            }}

            input {{
                width: 100%;
                padding: 0.75rem;
                border: 1px solid var(--silver);
                border-radius: 5px;
                font-size: 1rem;
            }}

            .form-actions {{
                display: flex;
                gap: 1rem;
                margin-top: 1rem;
            }}

            @media (max-width: 768px) {{
                .student-header {{
                    flex-direction: column;
                    gap: 1rem;
                    align-items: flex-start;
                }}

                .search-container {{
                    width: 100%;
                }}

                .search-input {{
                    width: 100%;
                }}

                .student-list {{
                    grid-template-columns: 1fr;
                }}
            }}
        </style>
    </head>
    <body>
        <header>
            <div class="container">
                <div class="header-content">
                    <div class="logo">پایه {grade} - رشته {field}</div>
                    <div class="nav-buttons">
                        <a href="/students/tenth" class="btn btn-secondary">بازگشت</a>
                        <a href="/main" class="btn btn-secondary">صفحه اصلی</a>
                    </div>
                </div>
            </div>
        </header>

        <div class="container">
            <div class="student-header">
                <div class="student-count">
                    <span>👤</span>
                    <span id="studentCount">0</span> دانش آموز
                </div>
                <div class="search-container">
                    <input type="text" id="searchInput" placeholder="جستجو..." class="search-input">
                    <button class="btn" id="searchBtn">جستجو</button>
                </div>
            </div>
            
            <div class="student-list" id="studentList">
                <!-- دانش آموزان اینجا نمایش داده می‌شوند -->
            </div>
            
            <div class="add-student-btn" id="addStudentBtn">+</div>
        </div>

        <!-- مودال اضافه کردن دانش آموز -->
        <div class="modal-overlay" id="studentModal">
            <div class="modal">
                <div class="modal-header">
                    <h2 class="modal-title" id="modalTitle">اضافه کردن دانش آموز</h2>
                    <button class="close-modal" id="closeModal">×</button>
                </div>
                <form id="studentForm">
                    <div class="form-group">
                        <label for="firstName">نام دانش آموز *</label>
                        <input type="text" id="firstName" required>
                    </div>
                    <div class="form-group">
                        <label for="lastName">نام خانوادگی دانش آموز *</label>
                        <input type="text" id="lastName" required>
                    </div>
                    <div class="form-group">
                        <label for="nationalCode">کد ملی دانش آموز *</label>
                        <input type="text" id="nationalCode" required>
                    </div>
                    <div class="form-group">
                        <label for="studentNumber">شماره دانش آموز</label>
                        <input type="text" id="studentNumber">
                    </div>
                    <div class="form-group">
                        <label for="fatherPhone">شماره پدر</label>
                        <input type="text" id="fatherPhone">
                    </div>
                    <div class="form-group">
                        <label for="motherPhone">شماره مادر</label>
                        <input type="text" id="motherPhone">
                    </div>
                    <div class="form-actions">
                        <button type="submit" class="btn">تایید</button>
                        <button type="button" class="btn btn-secondary" id="cancelBtn">انصراف</button>
                    </div>
                </form>
            </div>
        </div>

        <script>
            let students = [];
            let editingIndex = -1;

            // بارگذاری دانش آموزان
            function loadStudents() {{
                // در حالت واقعی از API استفاده می‌شود
                studentList.innerHTML = '';
                studentCount.textContent = students.length;
                
                students.forEach((student, index) => {{
                    const card = document.createElement('div');
                    card.className = 'student-card';
                    card.innerHTML = `
                        <div class="student-name">${{student.firstName}} ${{student.lastName}}</div>
                        <div class="student-national-code">کد ملی: ${{student.nationalCode}}</div>
                        <div class="student-actions">
                            <div class="action-btn edit-btn" onclick="editStudent(${{index}})">✏️</div>
                            <div class="action-btn delete-btn" onclick="deleteStudent(${{index}})">🗑️</div>
                        </div>
                    `;
                    studentList.appendChild(card);
                }});
            }}

            function showModal() {{
                document.getElementById('studentModal').classList.add('active');
            }}

            function hideModal() {{
                document.getElementById('studentModal').classList.remove('active');
                document.getElementById('studentForm').reset();
                editingIndex = -1;
                document.getElementById('modalTitle').textContent = 'اضافه کردن دانش آموز';
            }}

            function addStudent() {{
                const firstName = document.getElementById('firstName').value;
                const lastName = document.getElementById('lastName').value;
                const nationalCode = document.getElementById('nationalCode').value;
                const studentNumber = document.getElementById('studentNumber').value;
                const fatherPhone = document.getElementById('fatherPhone').value;
                const motherPhone = document.getElementById('motherPhone').value;

                if (!firstName || !lastName || !nationalCode) {{
                    alert('لطفا فیلدهای اجباری را پر کنید');
                    return;
                }}

                const studentData = {{
                    firstName,
                    lastName,
                    nationalCode,
                    studentNumber,
                    fatherPhone,
                    motherPhone
                }};

                if (editingIndex === -1) {{
                    students.push(studentData);
                }} else {{
                    students[editingIndex] = studentData;
                }}

                loadStudents();
                hideModal();
            }}

            function editStudent(index) {{
                const student = students[index];
                editingIndex = index;
                
                document.getElementById('firstName').value = student.firstName;
                document.getElementById('lastName').value = student.lastName;
                document.getElementById('nationalCode').value = student.nationalCode;
                document.getElementById('studentNumber').value = student.studentNumber || '';
                document.getElementById('fatherPhone').value = student.fatherPhone || '';
                document.getElementById('motherPhone').value = student.motherPhone || '';
                
                document.getElementById('modalTitle').textContent = 'ویرایش دانش آموز';
                showModal();
            }}

            function deleteStudent(index) {{
                if (confirm('آیا مطمئن هستید می‌خواهید این دانش آموز را حذف کنید؟')) {{
                    students.splice(index, 1);
                    loadStudents();
                }}
            }}

            // Event Listeners
            document.getElementById('addStudentBtn').addEventListener('click', showModal);
            document.getElementById('closeModal').addEventListener('click', hideModal);
            document.getElementById('cancelBtn').addEventListener('click', hideModal);
            document.getElementById('studentForm').addEventListener('submit', function(e) {{
                e.preventDefault();
                addStudent();
            }});

            // بارگذاری اولیه
            loadStudents();

            // بررسی لاگین
            const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{{}}');
            if (!currentUser.firstName) {{
                window.location.href = '/';
            }}
        </script>
    </body>
    </html>
    '''

# صفحات دیگر...
@app.route('/students/tenth/experimental')
def tenth_experimental_page():
    return render_student_management_page('دهم', 'تجربی')

@app.route('/students/tenth/humanities')
def tenth_humanities_page():
    return render_student_management_page('دهم', 'انسانی')

# صفحه پروفایل
@app.route('/profile')
def profile_page():
    return '''
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>پروفایل - دبیرستان جوادالائمه</title>
        <style>
            :root {
                --primary-dark: #1a365d;
                --primary-blue: #2d3748;
                --gray-light: #f7fafc;
                --gray-medium: #e2e8f0;
                --silver: #cbd5e0;
                --white: #ffffff;
                --accent-green: #2d5a27;
                --accent-gold: #b7791f;
                --shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                --transition: all 0.3s ease;
            }

            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Vazir', 'Iran Sans', Tahoma, sans-serif;
            }

            body {
                background-color: var(--gray-light);
                color: var(--primary-blue);
                min-height: 100vh;
            }

            header {
                background-color: var(--primary-dark);
                color: var(--white);
                padding: 1rem 0;
                box-shadow: var(--shadow);
            }

            .container {
                width: 100%;
                max-width: 1200px;
                margin: 0 auto;
                padding: 0 15px;
            }

            .header-content {
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .logo {
                font-size: 1.5rem;
                font-weight: bold;
            }

            .nav-buttons {
                display: flex;
                gap: 1rem;
            }

            .btn {
                padding: 0.5rem 1rem;
                background-color: var(--accent-green);
                color: var(--white);
                border: none;
                border-radius: 5px;
                cursor: pointer;
                text-decoration: none;
                transition: var(--transition);
            }

            .btn:hover {
                background-color: #23421f;
            }

            .btn-secondary {
                background-color: var(--silver);
                color: var(--primary-blue);
            }

            .btn-danger {
                background-color: #c53030;
            }

            .btn-danger:hover {
                background-color: #9b2c2c;
            }

            .profile-container {
                max-width: 600px;
                margin: 2rem auto;
                background-color: var(--white);
                border-radius: 15px;
                padding: 2rem;
                box-shadow: var(--shadow);
            }

            .profile-header {
                text-align: center;
                margin-bottom: 2rem;
            }

            .profile-avatar {
                width: 100px;
                height: 100px;
                border-radius: 50%;
                background-color: var(--accent-gold);
                display: flex;
                justify-content: center;
                align-items: center;
                font-size: 2.5rem;
                color: var(--white);
                margin: 0 auto 1rem;
            }

            .profile-info {
                margin-bottom: 2rem;
            }

            .info-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 1rem 0;
                border-bottom: 1px solid var(--gray-medium);
            }

            .info-item:last-child {
                border-bottom: none;
            }

            .info-label {
                font-weight: bold;
            }

            .info-value {
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }

            .edit-icon {
                cursor: pointer;
                color: var(--accent-gold);
                transition: var(--transition);
            }

            .edit-icon:hover {
                transform: scale(1.2);
            }

            .edit-form {
                display: none;
                margin-top: 1rem;
            }

            .edit-form.active {
                display: block;
            }

            .form-actions {
                display: flex;
                gap: 1rem;
                margin-top: 1rem;
            }

            .logout-section {
                text-align: center;
                margin-top: 2rem;
                padding-top: 2rem;
                border-top: 1px solid var(--gray-medium);
            }

            @media (max-width: 768px) {
                .profile-container {
                    margin: 1rem;
                    padding: 1.5rem;
                }
            }
        </style>
    </head>
    <body>
        <header>
            <div class="container">
                <div class="header-content">
                    <div class="logo">پروفایل کاربر</div>
                    <div class="nav-buttons">
                        <a href="/main" class="btn btn-secondary">بازگشت به صفحه اصلی</a>
                    </div>
                </div>
            </div>
        </header>

        <div class="container">
            <div class="profile-container">
                <div class="profile-header">
                    <div class="profile-avatar">👤</div>
                    <h1>پروفایل کاربری</h1>
                </div>

                <div class="profile-info">
                    <div class="info-item">
                        <span class="info-label">نام:</span>
                        <div class="info-value">
                            <span class="edit-icon" onclick="editField('firstName')">✏️</span>
                            <span id="firstNameValue">نام کاربر</span>
                        </div>
                    </div>

                    <div class="info-item">
                        <span class="info-label">نام خانوادگی:</span>
                        <div class="info-value">
                            <span class="edit-icon" onclick="editField('lastName')">✏️</span>
                            <span id="lastNameValue">نام خانوادگی کاربر</span>
                        </div>
                    </div>

                    <div class="info-item">
                        <span class="info-label">مرتبه:</span>
                        <div class="info-value">
                            <span class="edit-icon" onclick="editField('role')">✏️</span>
                            <span id="roleValue">مرتبه کاربر</span>
                        </div>
                    </div>

                    <div class="info-item">
                        <span class="info-label">رمز:</span>
                        <div class="info-value">
                            <span>••••••••</span>
                        </div>
                    </div>
                </div>

                <div class="logout-section">
                    <button class="btn btn-danger" onclick="showLogoutConfirm()">خروج از حساب</button>
                </div>
            </div>
        </div>

        <!-- مودال تایید خروج -->
        <div class="modal-overlay" id="logoutModal">
            <div class="modal">
                <div class="modal-header">
                    <h2 class="modal-title">خروج از حساب</h2>
                    <button class="close-modal" onclick="hideLogoutConfirm()">×</button>
                </div>
                <p>آیا مطمئن هستید می‌خواهید از حساب خارج شوید؟</p>
                <div class="form-actions">
                    <button class="btn btn-danger" onclick="logout()">بله</button>
                    <button class="btn btn-secondary" onclick="hideLogoutConfirm()">خیر</button>
                </div>
            </div>
        </div>

        <script>
            // بارگذاری اطلاعات کاربر
            const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
            
            if (!currentUser.firstName) {
                window.location.href = '/';
            }

            // نمایش اطلاعات کاربر
            document.getElementById('firstNameValue').textContent = currentUser.firstName;
            document.getElementById('lastNameValue').textContent = currentUser.lastName;
            
            let roleText = '';
            if (currentUser.role === 'manager') roleText = 'مدیر';
            else if (currentUser.role === 'supervisor') roleText = 'ناظم';
            else if (currentUser.role === 'assistant') roleText = 'معاون';
            
            document.getElementById('roleValue').textContent = roleText;

            function editField(field) {
                const currentValue = document.getElementById(field + 'Value').textContent;
                const newValue = prompt(`لطفا ${field === 'firstName' ? 'نام' : field === 'lastName' ? 'نام خانوادگی' : 'مرتبه'} جدید را وارد کنید:`, currentValue);
                
                if (newValue && newValue.trim() !== '') {
                    currentUser[field] = newValue.trim();
                    localStorage.setItem('currentUser', JSON.stringify(currentUser));
                    
                    if (field === 'role') {
                        let roleText = '';
                        if (newValue === 'manager') roleText = 'مدیر';
                        else if (newValue === 'supervisor') roleText = 'ناظم';
                        else if (newValue === 'assistant') roleText = 'معاون';
                        else roleText = newValue;
                        
                        document.getElementById('roleValue').textContent = roleText;
                    } else {
                        document.getElementById(field + 'Value').textContent = newValue;
                    }
                }
            }

            function showLogoutConfirm() {
                document.getElementById('logoutModal').style.display = 'flex';
            }

            function hideLogoutConfirm() {
                document.getElementById('logoutModal').style.display = 'none';
            }

            function logout() {
                localStorage.removeItem('currentUser');
                window.location.href = '/';
            }

            // استایل مودال
            const style = document.createElement('style');
            style.textContent = `
                .modal-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background-color: rgba(0, 0, 0, 0.5);
                    display: none;
                    justify-content: center;
                    align-items: center;
                    z-index: 3000;
                }
                .modal {
                    background-color: var(--white);
                    border-radius: 10px;
                    padding: 2rem;
                    width: 90%;
                    max-width: 400px;
                }
                .modal-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 1rem;
                }
                .modal-title {
                    font-size: 1.5rem;
                    color: var(--primary-dark);
                }
                .close-modal {
                    background: none;
                    border: none;
                    font-size: 1.5rem;
                    cursor: pointer;
                }
            `;
            document.head.appendChild(style);
        </script>
    </body>
    </html>
    '''

# صفحات دیگر مدیریت (نمونه)
@app.route('/teachers')
def teachers_page():
    return '<h1>مدیریت معلمان - به زودی...</h1><a href="/main">بازگشت</a>'

@app.route('/parent-reports')
def parent_reports_page():
    return '<h1>مدیریت گزارشات والدین - به زودی...</h1><a href="/main">بازگشت</a>'

@app.route('/teacher-reports')
def teacher_reports_page():
    return '<h1>مدیریت گزارشات معلمان - به زودی...</h1><a href="/main">بازگشت</a>'

@app.route('/student-reports')
def student_reports_page():
    return '<h1>مدیریت گزارشات دانش آموزان - به زودی...</h1><a href="/main">بازگشت</a>'

@app.route('/lab')
def lab_page():
    return '<h1>مدیریت بخش آزمایشگاه - به زودی...</h1><a href="/main">بازگشت</a>'

@app.route('/grades')
def grades_page():
    return '<h1>مدیریت نمرات - به زودی...</h1><a href="/main">بازگشت</a>'

@app.route('/report-cards')
def report_cards_page():
    return '<h1>مدیریت کارنامه - به زودی...</h1><a href="/main">بازگشت</a>'


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
