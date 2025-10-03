from flask import Flask, render_template_string, request, jsonify, session
import os  # اضافه شد
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# متغیرهای ذخیره‌سازی
users = {}
students = {
    'dahom': {
        'riazi': [],
        'tajrobi': [],
        'ensani': []
    },
    'yazdahom': {
        'riazi': [],
        'tajrobi': [],
        'ensani': []
    },
    'davazdahom': {
        'riazi': [],
        'tajrobi': [],
        'ensani': []
    }
}

# --- HTML Templates ---
main_template = '''
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مدیریت دبیرستان جوادالائمه</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: Tahoma, sans-serif;
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            color: white;
            direction: rtl;
        }
        .container {
            max-width: 100%;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            padding: 20px;
            background: rgba(0,0,0,0.3);
        }
        .form-box {
            width: 90%;
            max-width: 500px;
            margin: 50px auto;
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        }
        .form-group {
            margin-bottom: 15px;
        }
        input, select {
            width: 100%;
            padding: 12px;
            border-radius: 8px;
            border: 1px solid #ccc;
            background: rgba(255,255,255,0.9);
        }
        button {
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 8px;
            background: #00c853;
            color: white;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s;
        }
        button:hover {
            background: #009624;
            transform: scale(1.02);
        }
        .alert {
            color: red;
            text-align: center;
            margin-top: 10px;
        }
        .dashboard {
            display: none;
        }
        .menu-btn {
            position: absolute;
            top: 20px;
            right: 20px;
            font-size: 24px;
            cursor: pointer;
        }
        .sidebar {
            position: fixed;
            top: 0;
            right: -300px;
            width: 300px;
            height: 100%;
            background: rgba(0,0,0,0.8);
            transition: all 0.4s ease;
            z-index: 1000;
            padding: 20px;
        }
        .sidebar.active {
            right: 0;
        }
        .sidebar-btn {
            display: block;
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            background: #00c853;
            color: white;
            text-align: center;
            border-radius: 8px;
            cursor: pointer;
        }
        .btn-row {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
            margin: 20px 0;
        }
        .btn-row button {
            flex: 1;
            min-width: 120px;
            background: #00c853;
        }
        .btn-row button:hover {
            background: #009624;
        }
        .student-card {
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 10px;
            margin: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .edit-del {
            display: flex;
            gap: 10px;
        }
        .edit-del button {
            width: auto;
            padding: 5px 10px;
            font-size: 12px;
        }
        .profile-section {
            text-align: center;
            padding: 20px;
        }
        .profile-field {
            margin: 10px 0;
        }
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.7);
            z-index: 2000;
        }
        .modal-content {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            color: black;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .modal-btns {
            margin-top: 15px;
        }
        .modal-btns button {
            width: auto;
            margin: 0 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>به سایت رسمی مدیر دبیرستان جوادالائمه خوش آمدید</h1>
        </div>

        <div id="login-form">
            <div class="form-box">
                <div class="form-group">
                    <input type="text" id="fname" placeholder="نام">
                </div>
                <div class="form-group">
                    <input type="text" id="lname" placeholder="نام خانوادگی">
                </div>
                <div class="form-group">
                    <select id="rank">
                        <option value="">مرتبه خود را انتخاب کنید</option>
                        <option value="مدیر">مدیر</option>
                        <option value="ناظم">ناظم</option>
                        <option value="معاون">معاون</option>
                    </select>
                </div>
                <div class="form-group">
                    <input type="password" id="password" placeholder="رمز">
                </div>
                <button onclick="login()">ورود</button>
                <div id="alert" class="alert"></div>
            </div>
        </div>

        <div id="dashboard" class="dashboard">
            <div class="menu-btn" onclick="toggleSidebar()">☰</div>
            <div class="sidebar" id="sidebar">
                <div class="sidebar-btn" onclick="showDashboard()">صفحه اصلی</div>
                <div class="sidebar-btn" onclick="showProfile()">پروفایل</div>
                <div class="sidebar-btn" onclick="showNotifications()">اعلان</div>
            </div>

            <div style="padding: 20px;">
                <h2>درگاه مدیران</h2>
                <div class="btn-row">
                    <button onclick="goToStudents()">مدیریت دانش آموزان</button>
                    <button onclick="goToTeachers()">مدیریت معلمان</button>
                    <button onclick="goToReports()">گزارشات والدین</button>
                    <button onclick="goToTeacherReports()">گزارشات معلمان</button>
                    <button onclick="goToStudentReports()">گزارشات دانش آموزان</button>
                    <button onclick="goToLab()">بخش آزمایشگاه</button>
                    <button onclick="goToGrades()">مدیریت نمرات</button>
                    <button onclick="goToReportCard()">مدیریت کارنامه</button>
                </div>
            </div>
        </div>

        <div id="profile-section" class="profile-section dashboard">
            <h2>پروفایل</h2>
            <div class="profile-field">
                <label>نام:</label>
                <span id="p-fname" contenteditable="true" onblur="saveProfile('fname', this.textContent)"></span>
            </div>
            <div class="profile-field">
                <label>نام خانوادگی:</label>
                <span id="p-lname" contenteditable="true" onblur="saveProfile('lname', this.textContent)"></span>
            </div>
            <div class="profile-field">
                <label>مرتبه:</label>
                <span id="p-rank"></span>
            </div>
            <div class="profile-field">
                <label>رمز:</label>
                <span id="p-password">غیرقابل تغییر</span>
            </div>
            <button onclick="logout()">خروج از حساب</button>
        </div>

        <div id="students-section" class="dashboard">
            <h2>مدیریت دانش آموزان</h2>
            <button onclick="goToGrade('dahom')">پایه دهم</button>
            <button onclick="goToGrade('yazdahom')">پایه یازدهم</button>
            <button onclick="goToGrade('davazdahom')">پایه دوازدهم</button>
        </div>

        <div id="grade-section" class="dashboard">
            <h2 id="grade-title">پایه دهم</h2>
            <button onclick="goToStream('riazi')">ریاضی</button>
            <button onclick="goToStream('tajrobi')">تجربی</button>
            <button onclick="goToStream('ensani')">انسانی</button>
        </div>

        <div id="stream-section" class="dashboard">
            <h2 id="stream-title">ریاضی</h2>
            <div class="student-header">
                <span id="count">تعداد: 0</span>
            </div>
            <div id="student-list"></div>
            <button onclick="openAddForm()" style="position: fixed; bottom: 30px; left: 30px; width: 60px; height: 60px; border-radius: 50%; padding: 0;">+</button>
        </div>

        <div id="add-student-form" class="dashboard">
            <h2>افزودن دانش آموز</h2>
            <div class="form-group">
                <input type="text" id="s-fname" placeholder="نام دانش آموز">
            </div>
            <div class="form-group">
                <input type="text" id="s-lname" placeholder="نام خانوادگی">
            </div>
            <div class="form-group">
                <input type="text" id="s-national-id" placeholder="کد ملی">
            </div>
            <div class="form-group">
                <input type="text" id="s-student-id" placeholder="شماره دانش آموز (اختیاری)">
            </div>
            <div class="form-group">
                <input type="text" id="s-father-phone" placeholder="شماره پدر (اختیاری)">
            </div>
            <div class="form-group">
                <input type="text" id="s-mother-phone" placeholder="شماره مادر (اختیاری)">
            </div>
            <button onclick="submitStudent()">تایید</button>
            <button onclick="backToStream()">بازگشت</button>
        </div>

        <div id="view-student" class="dashboard">
            <h2 id="view-title">اطلاعات دانش آموز</h2>
            <div class="form-group">
                <label>نام:</label>
                <input type="text" id="v-fname" readonly>
            </div>
            <div class="form-group">
                <label>نام خانوادگی:</label>
                <input type="text" id="v-lname" readonly>
            </div>
            <div class="form-group">
                <label>کد ملی:</label>
                <input type="text" id="v-national-id" readonly>
            </div>
            <div class="form-group">
                <label>شماره دانش آموز:</label>
                <input type="text" id="v-student-id" readonly>
            </div>
            <div class="form-group">
                <label>شماره پدر:</label>
                <input type="text" id="v-father-phone" readonly>
            </div>
            <div class="form-group">
                <label>شماره مادر:</label>
                <input type="text" id="v-mother-phone" readonly>
            </div>
            <button onclick="backToStream()">بازگشت</button>
        </div>
    </div>

    <div id="confirm-modal" class="modal">
        <div class="modal-content">
            <p id="modal-text">آیا مطمئن هستید؟</p>
            <div class="modal-btns">
                <button onclick="confirmYes()">بله</button>
                <button onclick="confirmNo()">خیر</button>
            </div>
        </div>
    </div>

    <script>
        let currentGrade = '';
        let currentStream = '';
        let editingStudent = null;

        function login() {
            const fname = document.getElementById("fname").value;
            const lname = document.getElementById("lname").value;
            const rank = document.getElementById("rank").value;
            const password = document.getElementById("password").value;

            if (!fname || !lname || !rank || !password) {
                document.getElementById("alert").textContent = "لطفاً تمام فیلدها را پر کنید.";
                return;
            }

            if (password !== "dabirestan012345") {
                document.getElementById("alert").textContent = "رمز اشتباه است.";
                return;
            }

            users = { fname, lname, rank, password };
            document.getElementById("login-form").style.display = "none";
            document.getElementById("dashboard").style.display = "block";

            document.getElementById("p-fname").textContent = fname;
            document.getElementById("p-lname").textContent = lname;
            document.getElementById("p-rank").textContent = rank;
        }

        function toggleSidebar() {
            const sidebar = document.getElementById("sidebar");
            sidebar.classList.toggle("active");
        }

        function showDashboard() {
            document.querySelectorAll(".dashboard").forEach(el => el.style.display = "none");
            document.getElementById("dashboard").style.display = "block";
            document.getElementById("sidebar").classList.remove("active");
        }

        function showProfile() {
            document.querySelectorAll(".dashboard").forEach(el => el.style.display = "none");
            document.getElementById("profile-section").style.display = "block";
            document.getElementById("sidebar").classList.remove("active");
        }

        function showNotifications() {
            alert("بخش اعلان در دسترس نیست.");
        }

        function goToStudents() {
            document.querySelectorAll(".dashboard").forEach(el => el.style.display = "none");
            document.getElementById("students-section").style.display = "block";
        }

        function goToGrade(grade) {
            currentGrade = grade;
            document.querySelectorAll(".dashboard").forEach(el => el.style.display = "none");
            document.getElementById("grade-section").style.display = "block";
        }

        function goToStream(stream) {
            currentStream = stream;
            document.querySelectorAll(".dashboard").forEach(el => el.style.display = "none");
            document.getElementById("stream-section").style.display = "block";
            document.getElementById("stream-title").textContent = stream === 'riazi' ? 'ریاضی' : stream === 'tajrobi' ? 'تجربی' : 'انسانی';
            renderStudents();
        }

        function renderStudents() {
            const list = document.getElementById("student-list");
            list.innerHTML = "";
            const data = students[currentGrade][currentStream];
            document.getElementById("count").textContent = "تعداد: " + data.length;

            data.forEach((s, i) => {
                const card = document.createElement("div");
                card.className = "student-card";
                card.innerHTML = `
                    <div>
                        <strong>${s.fname} ${s.lname}</strong><br>
                        کد ملی: ${s.national_id}
                    </div>
                    <div class="edit-del">
                        <button onclick="editStudent(${i})">✏️</button>
                        <button onclick="deleteStudent(${i})">🗑️</button>
                    </div>
                `;
                card.onclick = () => viewStudent(s);
                list.appendChild(card);
            });
        }

        function openAddForm() {
            editingStudent = null;
            document.querySelectorAll(".dashboard").forEach(el => el.style.display = "none");
            document.getElementById("add-student-form").style.display = "block";
            clearForm();
        }

        function submitStudent() {
            const fname = document.getElementById("s-fname").value;
            const lname = document.getElementById("s-lname").value;
            const national_id = document.getElementById("s-national-id").value;
            const student_id = document.getElementById("s-student-id").value;
            const father_phone = document.getElementById("s-father-phone").value;
            const mother_phone = document.getElementById("s-mother-phone").value;

            if (!fname || !lname || !national_id) {
                alert("نام، نام خانوادگی و کد ملی الزامی است.");
                return;
            }

            const exists = students[currentGrade][currentStream].some(s => s.national_id === national_id);
            if (exists) {
                alert("دانش آموزی با این کد ملی قبلاً ثبت شده است.");
                return;
            }

            const newStudent = { fname, lname, national_id, student_id, father_phone, mother_phone };

            if (editingStudent !== null) {
                students[currentGrade][currentStream][editingStudent] = newStudent;
            } else {
                students[currentGrade][currentStream].push(newStudent);
            }

            backToStream();
        }

        function editStudent(index) {
            editingStudent = index;
            const s = students[currentGrade][currentStream][index];
            document.getElementById("s-fname").value = s.fname;
            document.getElementById("s-lname").value = s.lname;
            document.getElementById("s-national-id").value = s.national_id;
            document.getElementById("s-student-id").value = s.student_id || '';
            document.getElementById("s-father-phone").value = s.father_phone || '';
            document.getElementById("s-mother-phone").value = s.mother_phone || '';
            document.querySelectorAll(".dashboard").forEach(el => el.style.display = "none");
            document.getElementById("add-student-form").style.display = "block";
        }

        function deleteStudent(index) {
            confirmAction(() => {
                students[currentGrade][currentStream].splice(index, 1);
                renderStudents();
            }, "آیا مطمئن هستید می‌خواهید اطلاعات دانش آموز را پاک کنید؟");
        }

        function viewStudent(s) {
            document.querySelectorAll(".dashboard").forEach(el => el.style.display = "none");
            document.getElementById("view-student").style.display = "block";
            document.getElementById("view-title").textContent = s.fname + " " + s.lname;
            document.getElementById("v-fname").value = s.fname;
            document.getElementById("v-lname").value = s.lname;
            document.getElementById("v-national-id").value = s.national_id;
            document.getElementById("v-student-id").value = s.student_id || '';
            document.getElementById("v-father-phone").value = s.father_phone || '';
            document.getElementById("v-mother-phone").value = s.mother_phone || '';
        }

        function backToStream() {
            document.querySelectorAll(".dashboard").forEach(el => el.style.display = "none");
            document.getElementById("stream-section").style.display = "block";
            renderStudents();
        }

        function clearForm() {
            document.getElementById("s-fname").value = '';
            document.getElementById("s-lname").value = '';
            document.getElementById("s-national-id").value = '';
            document.getElementById("s-student-id").value = '';
            document.getElementById("s-father-phone").value = '';
            document.getElementById("s-mother-phone").value = '';
        }

        function saveProfile(field, value) {
            users[field] = value;
        }

        function logout() {
            confirmAction(() => {
                document.getElementById("login-form").style.display = "block";
                document.getElementById("dashboard").style.display = "none";
                document.getElementById("profile-section").style.display = "none";
            }, "آیا مطمئن هستید می‌خواهید از حساب خارج شوید؟");
        }

        let confirmCallback = null;

        function confirmAction(callback, text) {
            confirmCallback = callback;
            document.getElementById("modal-text").textContent = text;
            document.getElementById("confirm-modal").style.display = "block";
        }

        function confirmYes() {
            if (confirmCallback) confirmCallback();
            document.getElementById("confirm-modal").style.display = "none";
        }

        function confirmNo() {
            document.getElementById("confirm-modal").style.display = "none";
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(main_template)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # پورت از متغیرهای محیطی
    app.run(host='0.0.0.0', port=port, debug=False)  # debug=False برای محیط تولید