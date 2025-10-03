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
        }
    }

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# HTML template as string
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>سایت رسمی مدیر - دبیرستان جوادالائمه</title>
    <style>
        /* متغیرهای رنگ */
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

        /* استایل‌های پایه */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Vazir', 'Iran Sans', Tahoma, sans-serif;
        }

        body {
            background-color: var(--gray-light);
            color: var(--primary-blue);
            line-height: 1.6;
            overflow-x: hidden;
        }

        .container {
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 15px;
        }

        /* هدر */
        header {
            background-color: var(--primary-dark);
            color: var(--white);
            padding: 1rem 0;
            box-shadow: var(--shadow);
            position: sticky;
            top: 0;
            z-index: 1000;
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

        .welcome-text {
            text-align: center;
            margin: 2rem 0;
            font-size: 1.8rem;
            color: var(--primary-dark);
        }

        /* منوی همبرگری */
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

        /* سایدبار موبایل */
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
            padding: 0.5rem;
            border-radius: 5px;
            transition: var(--transition);
        }

        .sidebar-menu a:hover {
            background-color: rgba(255, 255, 255, 0.1);
        }

        /* فرم‌ها */
        .form-container {
            background-color: var(--white);
            border-radius: 10px;
            padding: 2rem;
            box-shadow: var(--shadow);
            max-width: 500px;
            margin: 0 auto;
        }

        .form-group {
            margin-bottom: 1.5rem;
        }

        label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: bold;
        }

        input, select {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid var(--silver);
            border-radius: 5px;
            font-size: 1rem;
            transition: var(--transition);
        }

        input:focus, select:focus {
            outline: none;
            border-color: var(--accent-green);
            box-shadow: 0 0 0 2px rgba(45, 90, 39, 0.2);
        }

        /* دکمه‌ها */
        .btn {
            display: inline-block;
            padding: 0.75rem 1.5rem;
            background-color: var(--accent-green);
            color: var(--white);
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1rem;
            text-align: center;
            text-decoration: none;
            transition: var(--transition);
            transform: translateY(0);
        }

        .btn:hover {
            background-color: #23421f;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }

        .btn-gold {
            background-color: var(--accent-gold);
        }

        .btn-gold:hover {
            background-color: #9e691a;
        }

        .btn-danger {
            background-color: #c53030;
        }

        .btn-danger:hover {
            background-color: #9b2c2c;
        }

        .btn-secondary {
            background-color: var(--silver);
            color: var(--primary-blue);
        }

        .btn-secondary:hover {
            background-color: #a0aec0;
        }

        /* کارت‌ها */
        .card-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-top: 2rem;
        }

        .card {
            background-color: var(--white);
            border-radius: 10px;
            padding: 1.5rem;
            box-shadow: var(--shadow);
            transition: var(--transition);
            cursor: pointer;
            border: 1px solid var(--gray-medium);
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
        }

        .card h3 {
            margin-bottom: 1rem;
            color: var(--primary-dark);
        }

        /* مدیریت دانش‌آموزان */
        .student-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
        }

        .student-count {
            display: flex;
            align-items: center;
            font-size: 1.2rem;
        }

        .student-count i {
            margin-left: 0.5rem;
            font-size: 1.5rem;
        }

        .add-student-btn {
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
        }

        .add-student-btn:hover {
            transform: scale(1.1);
        }

        .student-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 1.5rem;
            margin-top: 2rem;
        }

        .student-card {
            background-color: var(--white);
            border-radius: 10px;
            padding: 1.5rem;
            box-shadow: var(--shadow);
            position: relative;
            border: 1px solid var(--gray-medium);
        }

        .student-name {
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }

        .student-national-code {
            color: var(--primary-blue);
            margin-bottom: 1rem;
        }

        .student-actions {
            display: flex;
            justify-content: flex-end;
            gap: 0.5rem;
            margin-top: 1rem;
        }

        .action-btn {
            width: 35px;
            height: 35px;
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            cursor: pointer;
            transition: var(--transition);
        }

        .edit-btn {
            background-color: var(--accent-gold);
            color: var(--white);
        }

        .delete-btn {
            background-color: #c53030;
            color: var(--white);
        }

        /* مودال */
        .modal-overlay {
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
        }

        .modal-overlay.active {
            opacity: 1;
            visibility: visible;
        }

        .modal {
            background-color: var(--white);
            border-radius: 10px;
            padding: 2rem;
            width: 90%;
            max-width: 500px;
            max-height: 90vh;
            overflow-y: auto;
            transform: translateY(20px);
            transition: var(--transition);
        }

        .modal-overlay.active .modal {
            transform: translateY(0);
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
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
            color: var(--primary-blue);
        }

        /* پروفایل */
        .profile-info {
            background-color: var(--white);
            border-radius: 10px;
            padding: 2rem;
            box-shadow: var(--shadow);
            max-width: 500px;
            margin: 0 auto;
        }

        .profile-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 0;
            border-bottom: 1px solid var(--gray-medium);
        }

        .profile-item:last-child {
            border-bottom: none;
        }

        .profile-label {
            font-weight: bold;
        }

        .profile-value {
            display: flex;
            align-items: center;
        }

        .edit-icon {
            margin-right: 0.5rem;
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

        /* جستجو */
        .search-container {
            display: flex;
            margin-bottom: 2rem;
        }

        .search-input {
            flex: 1;
            border-top-right-radius: 0;
            border-bottom-right-radius: 0;
        }

        .search-btn {
            border-top-left-radius: 0;
            border-bottom-left-radius: 0;
        }

        /* انیمیشن‌ها */
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        @keyframes slideInRight {
            from { transform: translateX(100%); }
            to { transform: translateX(0); }
        }

        @keyframes slideOutRight {
            from { transform: translateX(0); }
            to { transform: translateX(100%); }
        }

        .fade-in {
            animation: fadeIn 0.5s ease;
        }

        .slide-in-right {
            animation: slideInRight 0.3s ease;
        }

        .slide-out-right {
            animation: slideOutRight 0.3s ease;
        }

        /* رسپانسیو */
        @media (max-width: 768px) {
            .hamburger-menu {
                display: flex;
            }
            
            .card-grid {
                grid-template-columns: 1fr;
            }
            
            .student-list {
                grid-template-columns: 1fr;
            }
            
            .welcome-text {
                font-size: 1.5rem;
            }
            
            .student-header {
                flex-direction: column;
                align-items: flex-start;
                gap: 1rem;
            }
        }

        /* استایل‌های خاص برای موبایل */
        @media (max-width: 480px) {
            .form-container, .profile-info {
                padding: 1rem;
            }
            
            .modal {
                padding: 1rem;
            }
            
            .btn {
                padding: 0.6rem 1.2rem;
            }
        }
    </style>
</head>
<body>
    <!-- هدر -->
    <header>
        <div class="container">
            <div class="header-content">
                <div class="logo">دبیرستان جوادالائمه</div>
                <div class="hamburger-menu" id="hamburgerMenu">
                    <div class="hamburger-line"></div>
                    <div class="hamburger-line"></div>
                    <div class="hamburger-line"></div>
                </div>
            </div>
        </div>
    </header>

    <!-- سایدبار موبایل -->
    <div class="mobile-sidebar" id="mobileSidebar">
        <div class="close-sidebar" id="closeSidebar">×</div>
        <ul class="sidebar-menu">
            <li><a href="#" class="menu-item" data-page="main">صفحه اصلی</a></li>
            <li><a href="#" class="menu-item" data-page="students">مدیریت دانش آموزان</a></li>
            <li><a href="#" class="menu-item" data-page="teachers">مدیریت معلمان</a></li>
            <li><a href="#" class="menu-item" data-page="parent-reports">مدیریت گزارشات والدین</a></li>
            <li><a href="#" class="menu-item" data-page="teacher-reports">مدیریت گزارشات معلمان</a></li>
            <li><a href="#" class="menu-item" data-page="student-reports">مدیریت گزارشات دانش آموزان</a></li>
            <li><a href="#" class="menu-item" data-page="lab">مدیریت بخش آزمایشگاه</a></li>
            <li><a href="#" class="menu-item" data-page="grades">مدیریت نمرات</a></li>
            <li><a href="#" class="menu-item" data-page="report-cards">مدیریت کارنامه</a></li>
            <li><a href="#" class="menu-item" data-page="profile">پروفایل</a></li>
        </ul>
    </div>

    <!-- محتوای اصلی -->
    <main class="container">
        <!-- صفحه ورود -->
        <div id="loginPage" class="page active">
            <h1 class="welcome-text">به سایت رسمی مدیر دبیرستان جوادالائمه خوش آمدید</h1>
            <div class="form-container">
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
                    <button type="submit" class="btn">ورود</button>
                </form>
            </div>
        </div>

        <!-- صفحه اصلی -->
        <div id="mainPage" class="page">
            <h1 class="welcome-text">درگاه مدیران</h1>
            <div class="card-grid">
                <div class="card" data-page="students">
                    <h3>مدیریت دانش آموزان</h3>
                </div>
                <div class="card" data-page="teachers">
                    <h3>مدیریت معلمان</h3>
                </div>
                <div class="card" data-page="parent-reports">
                    <h3>مدیریت گزارشات والدین</h3>
                </div>
                <div class="card" data-page="teacher-reports">
                    <h3>مدیریت گزارشات معلمان</h3>
                </div>
                <div class="card" data-page="student-reports">
                    <h3>مدیریت گزارشات دانش آموزان</h3>
                </div>
                <div class="card" data-page="lab">
                    <h3>مدیریت بخش آزمایشگاه</h3>
                </div>
                <div class="card" data-page="grades">
                    <h3>مدیریت نمرات</h3>
                </div>
                <div class="card" data-page="report-cards">
                    <h3>مدیریت کارنامه</h3>
                </div>
            </div>
        </div>

        <!-- صفحه مدیریت دانش آموزان -->
        <div id="studentsPage" class="page">
            <h1 class="welcome-text">مدیریت دانش آموزان</h1>
            <div class="card-grid">
                <div class="card" data-grade="tenth">
                    <h3>پایه دهم</h3>
                </div>
                <div class="card" data-grade="eleventh">
                    <h3>پایه یازدهم</h3>
                </div>
                <div class="card" data-grade="twelfth">
                    <h3>پایه دوازدهم</h3>
                </div>
            </div>
        </div>

        <!-- صفحه پایه‌ها -->
        <div id="gradePage" class="page">
            <h1 class="welcome-text" id="gradeTitle">پایه دهم</h1>
            <div class="card-grid">
                <div class="card" data-field="math">
                    <h3>رشته ریاضی</h3>
                </div>
                <div class="card" data-field="experimental">
                    <h3>رشته تجربی</h3>
                </div>
                <div class="card" data-field="humanities">
                    <h3>رشته انسانی</h3>
                </div>
            </div>
        </div>

        <!-- صفحه رشته‌ها -->
        <div id="fieldPage" class="page">
            <div class="student-header">
                <div class="student-count">
                    <i>👤</i>
                    <span id="studentCount">0</span> دانش آموز
                </div>
                <div class="search-container">
                    <input type="text" id="searchInput" placeholder="جستجو بر اساس نام، نام خانوادگی یا کد ملی..." class="search-input">
                    <button class="btn search-btn" id="searchBtn">جستجو</button>
                </div>
            </div>
            
            <div class="student-list" id="studentList">
                <!-- لیست دانش آموزان اینجا نمایش داده می‌شود -->
            </div>
            
            <div class="add-student-btn" id="addStudentBtn">+</div>
        </div>

        <!-- صفحه پروفایل -->
        <div id="profilePage" class="page">
            <h1 class="welcome-text">پروفایل کاربر</h1>
            <div class="profile-info">
                <div class="profile-item">
                    <span class="profile-label">نام:</span>
                    <div class="profile-value">
                        <span class="edit-icon" data-field="firstName">✏️</span>
                        <span id="profileFirstName">نام کاربر</span>
                    </div>
                </div>
                <div class="profile-item">
                    <span class="profile-label">نام خانوادگی:</span>
                    <div class="profile-value">
                        <span class="edit-icon" data-field="lastName">✏️</span>
                        <span id="profileLastName">نام خانوادگی کاربر</span>
                    </div>
                </div>
                <div class="profile-item">
                    <span class="profile-label">مرتبه:</span>
                    <div class="profile-value">
                        <span class="edit-icon" data-field="role">✏️</span>
                        <span id="profileRole">مرتبه کاربر</span>
                    </div>
                </div>
                <div class="profile-item">
                    <span class="profile-label">رمز:</span>
                    <div class="profile-value">
                        <span>••••••••</span>
                    </div>
                </div>
                <div class="form-actions" style="margin-top: 2rem;">
                    <button class="btn btn-danger" id="logoutBtn">خروج از حساب</button>
                </div>
            </div>
        </div>

        <!-- مودال اضافه کردن/ویرایش دانش آموز -->
        <div class="modal-overlay" id="studentModal">
            <div class="modal">
                <div class="modal-header">
                    <h2 class="modal-title" id="studentModalTitle">اضافه کردن دانش آموز</h2>
                    <button class="close-modal" id="closeStudentModal">×</button>
                </div>
                <form id="studentForm">
                    <div class="form-group">
                        <label for="studentFirstName">نام دانش آموز *</label>
                        <input type="text" id="studentFirstName" name="firstName" required>
                    </div>
                    <div class="form-group">
                        <label for="studentLastName">نام خانوادگی دانش آموز *</label>
                        <input type="text" id="studentLastName" name="lastName" required>
                    </div>
                    <div class="form-group">
                        <label for="studentNationalCode">کد ملی دانش آموز *</label>
                        <input type="text" id="studentNationalCode" name="nationalCode" required>
                    </div>
                    <div class="form-group">
                        <label for="studentNumber">شماره دانش آموز</label>
                        <input type="text" id="studentNumber" name="studentNumber">
                    </div>
                    <div class="form-group">
                        <label for="fatherPhone">شماره پدر</label>
                        <input type="text" id="fatherPhone" name="fatherPhone">
                    </div>
                    <div class="form-group">
                        <label for="motherPhone">شماره مادر</label>
                        <input type="text" id="motherPhone" name="motherPhone">
                    </div>
                    <div class="form-actions">
                        <button type="submit" class="btn">تایید</button>
                        <button type="button" class="btn btn-secondary" id="cancelStudentForm">انصراف</button>
                    </div>
                </form>
            </div>
        </div>

        <!-- مودال نمایش اطلاعات دانش آموز -->
        <div class="modal-overlay" id="studentInfoModal">
            <div class="modal">
                <div class="modal-header">
                    <h2 class="modal-title">اطلاعات دانش آموز</h2>
                    <button class="close-modal" id="closeStudentInfoModal">×</button>
                </div>
                <div class="student-info">
                    <div class="form-group">
                        <label>نام دانش آموز:</label>
                        <div class="info-value" id="infoFirstName"></div>
                    </div>
                    <div class="form-group">
                        <label>نام خانوادگی دانش آموز:</label>
                        <div class="info-value" id="infoLastName"></div>
                    </div>
                    <div class="form-group">
                        <label>کد ملی دانش آموز:</label>
                        <div class="info-value" id="infoNationalCode"></div>
                    </div>
                    <div class="form-group">
                        <label>شماره دانش آموز:</label>
                        <div class="info-value" id="infoStudentNumber"></div>
                    </div>
                    <div class="form-group">
                        <label>شماره پدر:</label>
                        <div class="info-value" id="infoFatherPhone"></div>
                    </div>
                    <div class="form-group">
                        <label>شماره مادر:</label>
                        <div class="info-value" id="infoMotherPhone"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- مودال تایید حذف -->
        <div class="modal-overlay" id="confirmModal">
            <div class="modal">
                <div class="modal-header">
                    <h2 class="modal-title">تایید حذف</h2>
                    <button class="close-modal" id="closeConfirmModal">×</button>
                </div>
                <p id="confirmMessage">آیا مطمئن هستید می‌خواهید این دانش آموز را حذف کنید؟</p>
                <div class="form-actions">
                    <button class="btn btn-danger" id="confirmDelete">بله</button>
                    <button class="btn btn-secondary" id="cancelDelete">خیر</button>
                </div>
            </div>
        </div>

        <!-- مودال تایید خروج -->
        <div class="modal-overlay" id="logoutModal">
            <div class="modal">
                <div class="modal-header">
                    <h2 class="modal-title">خروج از حساب</h2>
                    <button class="close-modal" id="closeLogoutModal">×</button>
                </div>
                <p>آیا مطمئن هستید می‌خواهید از حساب خارج شوید؟</p>
                <div class="form-actions">
                    <button class="btn btn-danger" id="confirmLogout">بله</button>
                    <button class="btn btn-secondary" id="cancelLogout">خیر</button>
                </div>
            </div>
        </div>
    </main>

    <script>
        // داده‌های برنامه
        let currentUser = null;
        let currentGrade = null;
        let currentField = null;
        let students = [];
        let editingStudentId = null;

        // عناصر DOM
        const loginPage = document.getElementById('loginPage');
        const mainPage = document.getElementById('mainPage');
        const studentsPage = document.getElementById('studentsPage');
        const gradePage = document.getElementById('gradePage');
        const fieldPage = document.getElementById('fieldPage');
        const profilePage = document.getElementById('profilePage');
        
        const hamburgerMenu = document.getElementById('hamburgerMenu');
        const mobileSidebar = document.getElementById('mobileSidebar');
        const closeSidebar = document.getElementById('closeSidebar');
        
        const loginForm = document.getElementById('loginForm');
        const studentForm = document.getElementById('studentForm');
        
        const studentModal = document.getElementById('studentModal');
        const studentInfoModal = document.getElementById('studentInfoModal');
        const confirmModal = document.getElementById('confirmModal');
        const logoutModal = document.getElementById('logoutModal');
        
        const studentList = document.getElementById('studentList');
        const studentCount = document.getElementById('studentCount');
        const addStudentBtn = document.getElementById('addStudentBtn');
        const searchInput = document.getElementById('searchInput');
        const searchBtn = document.getElementById('searchBtn');
        
        const logoutBtn = document.getElementById('logoutBtn');

        // مدیریت وضعیت لاگین
        function checkLoginStatus() {
            const savedUser = localStorage.getItem('currentUser');
            if (savedUser) {
                currentUser = JSON.parse(savedUser);
                showPage('main');
            } else {
                showPage('login');
            }
        }

        // نمایش صفحات
        function showPage(pageName) {
            // مخفی کردن همه صفحات
            document.querySelectorAll('.page').forEach(page => {
                page.classList.remove('active');
            });
            
            // نمایش صفحه درخواستی
            if (pageName === 'login') {
                loginPage.classList.add('active');
            } else if (pageName === 'main') {
                mainPage.classList.add('active');
            } else if (pageName === 'students') {
                studentsPage.classList.add('active');
            } else if (pageName === 'grade') {
                gradePage.classList.add('active');
            } else if (pageName === 'field') {
                fieldPage.classList.add('active');
                loadStudents();
            } else if (pageName === 'profile') {
                profilePage.classList.add('active');
                updateProfileInfo();
            }
            
            // بستن سایدبار در موبایل
            mobileSidebar.classList.remove('active');
        }

        // به‌روزرسانی اطلاعات پروفایل
        function updateProfileInfo() {
            if (currentUser) {
                document.getElementById('profileFirstName').textContent = currentUser.firstName;
                document.getElementById('profileLastName').textContent = currentUser.lastName;
                
                let roleText = '';
                if (currentUser.role === 'manager') roleText = 'مدیر';
                else if (currentUser.role === 'supervisor') roleText = 'ناظم';
                else if (currentUser.role === 'assistant') roleText = 'معاون';
                
                document.getElementById('profileRole').textContent = roleText;
            }
        }

        // بارگذاری دانش‌آموزان
        function loadStudents() {
            // در حالت واقعی این اطلاعات از سرور دریافت می‌شود
            // اینجا فقط یک نمونه نمایش داده می‌شود
            studentList.innerHTML = '';
            studentCount.textContent = students.length;
            
            students.forEach((student, index) => {
                const studentCard = document.createElement('div');
                studentCard.className = 'student-card fade-in';
                studentCard.innerHTML = `
                    <div class="student-name">${student.firstName} ${student.lastName}</div>
                    <div class="student-national-code">کد ملی: ${student.nationalCode}</div>
                    <div class="student-actions">
                        <div class="action-btn edit-btn" data-index="${index}">✏️</div>
                        <div class="action-btn delete-btn" data-index="${index}">🗑️</div>
                    </div>
                `;
                
                studentCard.addEventListener('click', (e) => {
                    if (!e.target.classList.contains('action-btn')) {
                        showStudentInfo(index);
                    }
                });
                
                studentList.appendChild(studentCard);
            });
            
            // اضافه کردن event listener برای دکمه‌های ویرایش و حذف
            document.querySelectorAll('.edit-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    editStudent(parseInt(e.target.dataset.index));
                });
            });
            
            document.querySelectorAll('.delete-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    confirmDeleteStudent(parseInt(e.target.dataset.index));
                });
            });
        }

        // نمایش اطلاعات دانش‌آموز
        function showStudentInfo(index) {
            const student = students[index];
            document.getElementById('infoFirstName').textContent = student.firstName;
            document.getElementById('infoLastName').textContent = student.lastName;
            document.getElementById('infoNationalCode').textContent = student.nationalCode;
            document.getElementById('infoStudentNumber').textContent = student.studentNumber || '---';
            document.getElementById('infoFatherPhone').textContent = student.fatherPhone || '---';
            document.getElementById('infoMotherPhone').textContent = student.motherPhone || '---';
            
            studentInfoModal.classList.add('active');
        }

        // اضافه کردن دانش‌آموز جدید
        function addStudent() {
            editingStudentId = null;
            document.getElementById('studentModalTitle').textContent = 'اضافه کردن دانش آموز';
            document.getElementById('studentForm').reset();
            studentModal.classList.add('active');
        }

        // ویرایش دانش‌آموز
        function editStudent(index) {
            const student = students[index];
            editingStudentId = index;
            
            document.getElementById('studentModalTitle').textContent = 'ویرایش دانش آموز';
            document.getElementById('studentFirstName').value = student.firstName;
            document.getElementById('studentLastName').value = student.lastName;
            document.getElementById('studentNationalCode').value = student.nationalCode;
            document.getElementById('studentNumber').value = student.studentNumber || '';
            document.getElementById('fatherPhone').value = student.fatherPhone || '';
            document.getElementById('motherPhone').value = student.motherPhone || '';
            
            studentModal.classList.add('active');
        }

        // تایید حذف دانش‌آموز
        function confirmDeleteStudent(index) {
            document.getElementById('confirmMessage').textContent = 'آیا مطمئن هستید می‌خواهید اطلاعات دانش آموز را پاک کنید؟';
            
            document.getElementById('confirmDelete').onclick = () => {
                students.splice(index, 1);
                loadStudents();
                confirmModal.classList.remove('active');
            };
            
            confirmModal.classList.add('active');
        }

        // جستجوی دانش‌آموز
        function searchStudents() {
            const query = searchInput.value.toLowerCase().trim();
            
            if (query === '') {
                loadStudents();
                return;
            }
            
            const filteredStudents = students.filter(student => 
                student.firstName.toLowerCase().includes(query) ||
                student.lastName.toLowerCase().includes(query) ||
                student.nationalCode.includes(query)
            );
            
            studentList.innerHTML = '';
            studentCount.textContent = filteredStudents.length;
            
            filteredStudents.forEach((student, index) => {
                const studentCard = document.createElement('div');
                studentCard.className = 'student-card fade-in';
                studentCard.innerHTML = `
                    <div class="student-name">${student.firstName} ${student.lastName}</div>
                    <div class="student-national-code">کد ملی: ${student.nationalCode}</div>
                    <div class="student-grade-field">پایه ${currentGrade === 'tenth' ? 'دهم' : currentGrade === 'eleventh' ? 'یازدهم' : 'دوازدهم'} - رشته ${currentField === 'math' ? 'ریاضی' : currentField === 'experimental' ? 'تجربی' : 'انسانی'}</div>
                    <div class="student-actions">
                        <div class="action-btn edit-btn" data-index="${index}">✏️</div>
                        <div class="action-btn delete-btn" data-index="${index}">🗑️</div>
                    </div>
                `;
                
                studentCard.addEventListener('click', (e) => {
                    if (!e.target.classList.contains('action-btn')) {
                        showStudentInfo(index);
                    }
                });
                
                studentList.appendChild(studentCard);
            });
            
            // اضافه کردن event listener برای دکمه‌های ویرایش و حذف
            document.querySelectorAll('.edit-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    editStudent(parseInt(e.target.dataset.index));
                });
            });
            
            document.querySelectorAll('.delete-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    confirmDeleteStudent(parseInt(e.target.dataset.index));
                });
            });
        }

        // Event Listeners
        document.addEventListener('DOMContentLoaded', () => {
            checkLoginStatus();
            
            // منوی همبرگری
            hamburgerMenu.addEventListener('click', () => {
                mobileSidebar.classList.add('active');
            });
            
            closeSidebar.addEventListener('click', () => {
                mobileSidebar.classList.remove('active');
            });
            
            // آیتم‌های منو
            document.querySelectorAll('.menu-item').forEach(item => {
                item.addEventListener('click', (e) => {
                    e.preventDefault();
                    showPage(e.target.dataset.page);
                });
            });
            
            // فرم ورود
            loginForm.addEventListener('submit', (e) => {
                e.preventDefault();
                
                const firstName = document.getElementById('firstName').value;
                const lastName = document.getElementById('lastName').value;
                const role = document.getElementById('role').value;
                const password = document.getElementById('password').value;
                
                if (!firstName || !lastName || !role || !password) {
                    alert('لطفا تمام فیلدها را پر کنید');
                    return;
                }
                
                if (password !== 'dabirestan012345') {
                    alert('رمز وارد شده صحیح نیست');
                    return;
                }
                
                currentUser = {
                    firstName,
                    lastName,
                    role,
                    password
                };
                
                localStorage.setItem('currentUser', JSON.stringify(currentUser));
                showPage('main');
            });
            
            // کارت‌های صفحه اصلی
            document.querySelectorAll('#mainPage .card').forEach(card => {
                card.addEventListener('click', () => {
                    showPage(card.dataset.page);
                });
            });
            
            // کارت‌های پایه‌ها
            document.querySelectorAll('#studentsPage .card').forEach(card => {
                card.addEventListener('click', () => {
                    currentGrade = card.dataset.grade;
                    document.getElementById('gradeTitle').textContent = card.querySelector('h3').textContent;
                    showPage('grade');
                });
            });
            
            // کارت‌های رشته‌ها
            document.querySelectorAll('#gradePage .card').forEach(card => {
                card.addEventListener('click', () => {
                    currentField = card.dataset.field;
                    
                    // در حالت واقعی این اطلاعات از سرور دریافت می‌شود
                    // اینجا فقط یک نمونه نمایش داده می‌شود
                    students = [
                        {
                            firstName: 'علی',
                            lastName: 'محمدی',
                            nationalCode: '0012345678',
                            studentNumber: '1001',
                            fatherPhone: '09123456789',
                            motherPhone: '09129876543'
                        },
                        {
                            firstName: 'فاطمه',
                            lastName: 'احمدی',
                            nationalCode: '0023456789',
                            studentNumber: '1002',
                            fatherPhone: '09134567890',
                            motherPhone: '09138765432'
                        }
                    ];
                    
                    showPage('field');
                });
            });
            
            // دکمه اضافه کردن دانش‌آموز
            addStudentBtn.addEventListener('click', addStudent);
            
            // فرم دانش‌آموز
            studentForm.addEventListener('submit', (e) => {
                e.preventDefault();
                
                const firstName = document.getElementById('studentFirstName').value;
                const lastName = document.getElementById('studentLastName').value;
                const nationalCode = document.getElementById('studentNationalCode').value;
                const studentNumber = document.getElementById('studentNumber').value;
                const fatherPhone = document.getElementById('fatherPhone').value;
                const motherPhone = document.getElementById('motherPhone').value;
                
                if (!firstName || !lastName || !nationalCode) {
                    alert('لطفا فیلدهای اجباری را پر کنید');
                    return;
                }
                
                // بررسی تکراری نبودن کد ملی
                if (editingStudentId === null) {
                    const existingStudent = students.find(s => s.nationalCode === nationalCode);
                    if (existingStudent) {
                        alert('این دانش آموز با این کد ملی وجود دارد');
                        return;
                    }
                }
                
                const studentData = {
                    firstName,
                    lastName,
                    nationalCode,
                    studentNumber,
                    fatherPhone,
                    motherPhone
                };
                
                if (editingStudentId !== null) {
                    students[editingStudentId] = studentData;
                } else {
                    students.push(studentData);
                }
                
                loadStudents();
                studentModal.classList.remove('active');
            });
            
            // دکمه جستجو
            searchBtn.addEventListener('click', searchStudents);
            
            // جستجو با اینتر
            searchInput.addEventListener('keyup', (e) => {
                if (e.key === 'Enter') {
                    searchStudents();
                }
            });
            
            // دکمه خروج
            logoutBtn.addEventListener('click', () => {
                logoutModal.classList.add('active');
            });
            
            // بستن مودال‌ها
            document.getElementById('closeStudentModal').addEventListener('click', () => {
                studentModal.classList.remove('active');
            });
            
            document.getElementById('closeStudentInfoModal').addEventListener('click', () => {
                studentInfoModal.classList.remove('active');
            });
            
            document.getElementById('closeConfirmModal').addEventListener('click', () => {
                confirmModal.classList.remove('active');
            });
            
            document.getElementById('closeLogoutModal').addEventListener('click', () => {
                logoutModal.classList.remove('active');
            });
            
            document.getElementById('cancelStudentForm').addEventListener('click', () => {
                studentModal.classList.remove('active');
            });
            
            document.getElementById('cancelDelete').addEventListener('click', () => {
                confirmModal.classList.remove('active');
            });
            
            document.getElementById('cancelLogout').addEventListener('click', () => {
                logoutModal.classList.remove('active');
            });
            
            // تایید خروج
            document.getElementById('confirmLogout').addEventListener('click', () => {
                localStorage.removeItem('currentUser');
                currentUser = null;
                logoutModal.classList.remove('active');
                showPage('login');
            });
            
            // بستن مودال‌ها با کلیک خارج از آنها
            document.querySelectorAll('.modal-overlay').forEach(modal => {
                modal.addEventListener('click', (e) => {
                    if (e.target === modal) {
                        modal.classList.remove('active');
                    }
                });
            });
            
            // ویرایش اطلاعات پروفایل
            document.querySelectorAll('.edit-icon').forEach(icon => {
                icon.addEventListener('click', () => {
                    const field = icon.dataset.field;
                    const currentValue = document.getElementById(`profile${field.charAt(0).toUpperCase() + field.slice(1)}`).textContent;
                    
                    // ایجاد فیلد ویرایش
                    const input = document.createElement('input');
                    input.type = 'text';
                    input.value = currentValue;
                    input.className = 'edit-input';
                    
                    // ایجاد دکمه‌های تایید و انصراف
                    const confirmBtn = document.createElement('button');
                    confirmBtn.textContent = 'تایید';
                    confirmBtn.className = 'btn';
                    
                    const cancelBtn = document.createElement('button');
                    cancelBtn.textContent = 'انصراف';
                    cancelBtn.className = 'btn btn-secondary';
                    
                    const actionsDiv = document.createElement('div');
                    actionsDiv.className = 'form-actions';
                    actionsDiv.appendChild(confirmBtn);
                    actionsDiv.appendChild(cancelBtn);
                    
                    // جایگزینی محتوا
                    const parent = icon.parentElement;
                    parent.innerHTML = '';
                    parent.appendChild(input);
                    parent.appendChild(actionsDiv);
                    
                    // رویدادهای دکمه‌ها
                    confirmBtn.addEventListener('click', () => {
                        const newValue = input.value;
                        if (newValue.trim() !== '') {
                            // به‌روزرسانی اطلاعات کاربر
                            currentUser[field] = newValue;
                            localStorage.setItem('currentUser', JSON.stringify(currentUser));
                            updateProfileInfo();
                        }
                    });
                    
                    cancelBtn.addEventListener('click', () => {
                        updateProfileInfo();
                    });
                });
            });
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return HTML_TEMPLATE

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    role = data.get('role')
    password = data.get('password')
    
    # بررسی صحت رمز
    if password != 'dabirestan012345':
        return jsonify({'success': False, 'message': 'رمز وارد شده صحیح نیست'})
    
    # ذخیره اطلاعات کاربر
    user_data = {
        'firstName': first_name,
        'lastName': last_name,
        'role': role
    }
    
    # در اینجا می‌توانید اطلاعات کاربر را در session یا دیتابیس ذخیره کنید
    session['user'] = user_data
    
    return jsonify({'success': True})

@app.route('/students/<grade>/<field>', methods=['GET', 'POST'])
def manage_students(grade, field):
    data = load_data()
    
    if request.method == 'GET':
        students = data['students'].get(grade, {}).get(field, [])
        return jsonify({'students': students})
    
    elif request.method == 'POST':
        student_data = request.json
        
        # بررسی تکراری نبودن کد ملی
        existing_students = data['students'].get(grade, {}).get(field, [])
        for student in existing_students:
            if student['nationalCode'] == student_data['nationalCode']:
                return jsonify({'success': False, 'message': 'این دانش آموز با این کد ملی وجود دارد'})
        
        # اضافه کردن دانش آموز جدید
        if grade not in data['students']:
            data['students'][grade] = {}
        if field not in data['students'][grade]:
            data['students'][grade][field] = []
        
        data['students'][grade][field].append(student_data)
        save_data(data)
        
        return jsonify({'success': True})

@app.route('/students/<grade>/<field>/<int:student_id>', methods=['PUT', 'DELETE'])
def student_detail(grade, field, student_id):
    data = load_data()
    
    if request.method == 'PUT':
        # ویرایش دانش آموز
        student_data = request.json
        data['students'][grade][field][student_id] = student_data
        save_data(data)
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        # حذف دانش آموز
        del data['students'][grade][field][student_id]
        save_data(data)
        return jsonify({'success': True})

@app.route('/search', methods=['POST'])
def search_students():
    query = request.json.get('query', '')
    data = load_data()
    
    results = []
    for grade, fields in data['students'].items():
        for field, students in fields.items():
            for student in students:
                if (query in student['firstName'] or 
                    query in student['lastName'] or 
                    query in student['nationalCode']):
                    student_with_info = student.copy()
                    student_with_info['grade'] = grade
                    student_with_info['field'] = field
                    results.append(student_with_info)
    
    return jsonify({'results': results})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
