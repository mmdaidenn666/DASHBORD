from flask import Flask, render_template_string, request, jsonify
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# ذخیره داده‌ها در حافظه
students = {
    'dahom': {'riazi': [], 'tajrobi': [], 'ensani': []},
    'yazdahom': {'riazi': [], 'tajrobi': [], 'ensani': []},
    'davazdahom': {'riazi': [], 'tajrobi': [], 'ensani': []}
}

current_user = None

# --- HTML Template با طراحی کاملاً جدید و انیمیشن و رنگ‌های نئونی ---
main_template = '''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>سایت مدیریت دبیرستان جوادالائمه</title>
    <link href="https://cdn.jsdelivr.net/npm/remixicon@2.5.0/fonts/remixicon.css" rel="stylesheet">
    <style>
        :root {
            --primary: #00c853;
            --secondary: #ff4081;
            --accent: #2979ff;
            --dark: #121212;
            --light: #f5f5f5;
            --neon: #00e5ff;
        }
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: "Vazir", Tahoma, sans-serif;
        }
        body {
            background: linear-gradient(135deg, var(--dark), #1a237e);
            color: white;
            min-height: 100vh;
            overflow-x: hidden;
        }
        .container {
            max-width: 100%;
            padding: 15px;
        }
        .header {
            text-align: center;
            padding: 20px;
            background: rgba(0, 0, 0, 0.5);
            border-radius: 10px;
            margin-bottom: 20px;
            animation: fadeIn 1s ease;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .form-box {
            background: rgba(255, 255, 255, 0.1);
            padding: 25px;
            border-radius: 15px;
            max-width: 500px;
            margin: 0 auto;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .form-group {
            margin-bottom: 15px;
        }
        input, select {
            width: 100%;
            padding: 12px;
            border-radius: 10px;
            border: 1px solid var(--neon);
            background: rgba(0, 0, 0, 0.3);
            color: white;
            font-size: 16px;
        }
        button {
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 10px;
            background: var(--primary);
            color: white;
            cursor: pointer;
            font-size: 16px;
            margin-top: 10px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0, 200, 83, 0.4);
        }
        button:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(0, 200, 83, 0.6);
            background: #009624;
        }
        .alert {
            color: #ff5252;
            text-align: center;
            margin-top: 10px;
            font-weight: bold;
        }
        .hidden {
            display: none !important;
        }
        .dashboard {
            padding: 20px;
        }
        .menu-btn {
            position: fixed;
            top: 20px;
            right: 20px;
            font-size: 24px;
            cursor: pointer;
            z-index: 1000;
            color: var(--neon);
            background: rgba(0,0,0,0.5);
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
        }
        .sidebar {
            position: fixed;
            top: 0;
            right: -300px;
            width: 300px;
            height: 100%;
            background: rgba(0,0,0,0.9);
            z-index: 999;
            transition: right 0.4s ease;
            padding: 60px 20px 20px;
            overflow-y: auto;
        }
        .sidebar.active {
            right: 0;
        }
        .sidebar-btn {
            display: block;
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            background: var(--accent);
            color: white;
            text-align: center;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .sidebar-btn:hover {
            background: #004ba0;
        }
        .btn-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .btn-grid button {
            background: var(--secondary);
            box-shadow: 0 4px 15px rgba(255, 64, 129, 0.4);
        }
        .btn-grid button:hover {
            background: #d81b60;
            transform: scale(1.05);
        }
        .student-card {
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            animation: slideIn 0.4s ease;
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(30px); }
            to { opacity: 1; transform: translateX(0); }
        }
        .edit-del {
            display: flex;
            gap: 8px;
        }
        .edit-del button {
            width: auto;
            padding: 6px 12px;
            font-size: 14px;
        }
        .profile-section {
            text-align: center;
            padding: 20px;
        }
        .profile-field {
            margin: 15px 0;
            padding: 10px;
            border: 1px solid var(--neon);
            border-radius: 8px;
            background: rgba(0,0,0,0.2);
        }
        .modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.7);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 2000;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease;
        }
        .modal.active {
            opacity: 1;
            pointer-events: all;
        }
        .modal-content {
            background: #222;
            padding: 25px;
            border-radius: 15px;
            width: 90%;
            max-width: 400px;
            text-align: center;
            box-shadow: 0 0 30px var(--neon);
            animation: popIn 0.4s ease;
        }
        @keyframes popIn {
            from { transform: scale(0.8); opacity: 0; }
            to { transform: scale(1); opacity: 1; }
        }
        .modal-btns {
            margin-top: 15px;
        }
        .modal-btns button {
            width: auto;
            margin: 0 5px;
            padding: 8px 20px;
        }
        .student-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 20px;
        }
        .search-box {
            width: 100%;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid var(--neon);
            background: rgba(0,0,0,0.3);
            color: white;
        }
        .plus-btn {
            position: fixed;
            bottom: 30px;
            left: 30px;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: var(--primary);
            color: white;
            border: none;
            font-size: 24px;
            cursor: pointer;
            box-shadow: 0 4px 20px rgba(0,200,83,0.6);
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .view-student-field {
            margin: 10px 0;
            padding: 10px;
            border: 1px solid #555;
            border-radius: 8px;
            background: rgba(0,0,0,0.2);
        }
        .view-student-field label {
            display: block;
            margin-bottom: 5px;
            color: var(--neon);
        }
        .view-student-field input {
            width: 100%;
            padding: 8px;
            background: rgba(0,0,0,0.3);
            border: 1px solid #555;
            color: white;
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

        <div id="dashboard" class="dashboard hidden">
            <div class="menu-btn" onclick="toggleSidebar()">☰</div>
            <div class="sidebar" id="sidebar">
                <div class="sidebar-btn" onclick="showSection('dashboard')">صفحه اصلی</div>
                <div class="sidebar-btn" onclick="showProfile()">پروفایل</div>
                <div class="sidebar-btn" onclick="showNotifications()">اعلان</div>
            </div>

            <h2>درگاه مدیران</h2>
            <div class="btn-grid">
                <button onclick="showSection('students')">مدیریت دانش آموزان</button>
                <button onclick="showSection('teachers')">مدیریت معلمان</button>
                <button onclick="showSection('reports-parents')">گزارشات والدین</button>
                <button onclick="showSection('reports-teachers')">گزارشات معلمان</button>
                <button onclick="showSection('reports-students')">گزارشات دانش آموزان</button>
                <button onclick="showSection('lab')">بخش آزمایشگاه</button>
                <button onclick="showSection('grades')">مدیریت نمرات</button>
                <button onclick="showSection('reportcard')">مدیریت کارنامه</button>
            </div>
        </div>

        <div id="students-section" class="dashboard hidden">
            <h2>مدیریت دانش آموزان</h2>
            <button onclick="goToGrade('dahom')">پایه دهم</button>
            <button onclick="goToGrade('yazdahom')">پایه یازدهم</button>
            <button onclick="goToGrade('davazdahom')">پایه دوازدهم</button>
            <br><br>
            <button onclick="showSection('dashboard')">بازگشت</button>
        </div>

        <div id="grade-section" class="dashboard hidden">
            <h2 id="grade-title">پایه دهم</h2>
            <button onclick="goToStream('riazi')">ریاضی</button>
            <button onclick="goToStream('tajrobi')">تجربی</button>
            <button onclick="goToStream('ensani')">انسانی</button>
            <br><br>
            <button onclick="showSection('students')">بازگشت</button>
        </div>

        <div id="stream-section" class="dashboard hidden">
            <h2 id="stream-title">ریاضی</h2>
            <div class="student-header">
                <i class="ri-user-3-line"></i>
                <span id="count">تعداد: 0</span>
            </div>
            <input type="text" class="search-box" placeholder="جستجو (نام، نام خانوادگی، کد ملی)" id="search-input" oninput="searchStudents()">
            <div id="student-list"></div>
            <button class="plus-btn" onclick="openAddForm()">+</button>
        </div>

        <div id="add-student-form" class="dashboard hidden">
            <h2>افزودن دانش آموز</h2>
            <div class="form-group">
                <input type="text" id="s-fname" placeholder="نام دانش آموز (اجباری)">
            </div>
            <div class="form-group">
                <input type="text" id="s-lname" placeholder="نام خانوادگی (اجباری)">
            </div>
            <div class="form-group">
                <input type="text" id="s-national-id" placeholder="کد ملی (اجباری)">
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
            <button onclick="showSection('stream')">بازگشت</button>
        </div>

        <div id="view-student" class="dashboard hidden">
            <h2 id="view-title">اطلاعات دانش آموز</h2>
            <div class="view-student-field">
                <label>نام:</label>
                <input type="text" id="v-fname" readonly>
            </div>
            <div class="view-student-field">
                <label>نام خانوادگی:</label>
                <input type="text" id="v-lname" readonly>
            </div>
            <div class="view-student-field">
                <label>کد ملی:</label>
                <input type="text" id="v-national-id" readonly>
            </div>
            <div class="view-student-field">
                <label>شماره دانش آموز:</label>
                <input type="text" id="v-student-id" readonly>
            </div>
            <div class="view-student-field">
                <label>شماره پدر:</label>
                <input type="text" id="v-father-phone" readonly>
            </div>
            <div class="view-student-field">
                <label>شماره مادر:</label>
                <input type="text" id="v-mother-phone" readonly>
            </div>
            <button onclick="showSection('stream')">بازگشت</button>
        </div>

        <div id="profile-section" class="profile-section hidden">
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
        let editingIndex = null;
        let currentStudents = [];

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

            current_user = { fname, lname, rank, password };
            document.getElementById("login-form").classList.add("hidden");
            document.getElementById("dashboard").classList.remove("hidden");
            document.getElementById("p-fname").textContent = fname;
            document.getElementById("p-lname").textContent = lname;
            document.getElementById("p-rank").textContent = rank;
        }

        function toggleSidebar() {
            document.getElementById("sidebar").classList.toggle("active");
        }

        function showSection(name) {
            document.querySelectorAll(".dashboard").forEach(el => el.classList.add("hidden"));
            document.getElementById(`${name}-section`).classList.remove("hidden");
            document.getElementById("sidebar").classList.remove("active");
        }

        function showProfile() {
            document.querySelectorAll(".dashboard").forEach(el => el.classList.add("hidden"));
            document.getElementById("profile-section").classList.remove("hidden");
            document.getElementById("sidebar").classList.remove("active");
        }

        function showNotifications() {
            alert("بخش اعلان در دسترس نیست.");
        }

        function goToGrade(grade) {
            currentGrade = grade;
            document.getElementById("grade-title").textContent = grade === 'dahom' ? 'پایه دهم' : grade === 'yazdahom' ? 'پایه یازدهم' : 'پایه دوازدهم';
            showSection("grade");
        }

        function goToStream(stream) {
            currentStream = stream;
            document.getElementById("stream-title").textContent = stream === 'riazi' ? 'ریاضی' : stream === 'tajrobi' ? 'تجربی' : 'انسانی';
            currentStudents = students[currentGrade][currentStream];
            showSection("stream");
            renderStudents();
        }

        function renderStudents() {
            const list = document.getElementById("student-list");
            list.innerHTML = "";

            currentStudents.forEach((s, i) => {
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

            document.getElementById("count").textContent = `تعداد: ${currentStudents.length}`;
        }

        function searchStudents() {
            const query = document.getElementById("search-input").value.toLowerCase();
            const filtered = currentStudents.filter(s =>
                s.fname.toLowerCase().includes(query) ||
                s.lname.toLowerCase().includes(query) ||
                s.national_id.includes(query)
            );
            const list = document.getElementById("student-list");
            list.innerHTML = "";

            filtered.forEach(s => {
                const card = document.createElement("div");
                card.className = "student-card";
                card.innerHTML = `
                    <div>
                        <strong>${s.fname} ${s.lname}</strong><br>
                        کد ملی: ${s.national_id}
                    </div>
                `;
                card.onclick = () => viewStudent(s);
                list.appendChild(card);
            });
        }

        function openAddForm() {
            editingIndex = null;
            document.querySelectorAll(".dashboard").forEach(el => el.classList.add("hidden"));
            document.getElementById("add-student-form").classList.remove("hidden");
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

            const exists = currentStudents.some(s => s.national_id === national_id);
            if (exists) {
                alert("دانش آموزی با این کد ملی قبلاً ثبت شده است.");
                return;
            }

            const newStudent = { fname, lname, national_id, student_id, father_phone, mother_phone };

            if (editingIndex !== null) {
                currentStudents[editingIndex] = newStudent;
            } else {
                currentStudents.push(newStudent);
            }

            showSection("stream");
        }

        function editStudent(index) {
            editingIndex = index;
            const s = currentStudents[index];
            document.getElementById("s-fname").value = s.fname;
            document.getElementById("s-lname").value = s.lname;
            document.getElementById("s-national-id").value = s.national_id;
            document.getElementById("s-student-id").value = s.student_id || '';
            document.getElementById("s-father-phone").value = s.father_phone || '';
            document.getElementById("s-mother-phone").value = s.mother_phone || '';
            document.querySelectorAll(".dashboard").forEach(el => el.classList.add("hidden"));
            document.getElementById("add-student-form").classList.remove("hidden");
        }

        function deleteStudent(index) {
            confirmAction(() => {
                currentStudents.splice(index, 1);
                renderStudents();
            }, "آیا مطمئن هستید می‌خواهید اطلاعات دانش آموز را پاک کنید؟");
        }

        function viewStudent(s) {
            document.querySelectorAll(".dashboard").forEach(el => el.classList.add("hidden"));
            document.getElementById("view-student").classList.remove("hidden");
            document.getElementById("view-title").textContent = s.fname + " " + s.lname;
            document.getElementById("v-fname").value = s.fname;
            document.getElementById("v-lname").value = s.lname;
            document.getElementById("v-national-id").value = s.national_id;
            document.getElementById("v-student-id").value = s.student_id || '';
            document.getElementById("v-father-phone").value = s.father_phone || '';
            document.getElementById("v-mother-phone").value = s.mother_phone || '';
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
            current_user[field] = value;
        }

        function logout() {
            confirmAction(() => {
                current_user = null;
                document.querySelectorAll(".dashboard").forEach(el => el.classList.add("hidden"));
                document.getElementById("login-form").classList.remove("hidden");
            }, "آیا مطمئن هستید می‌خواهید از حساب خارج شوید؟");
        }

        let confirmCallback = null;

        function confirmAction(callback, text) {
            confirmCallback = callback;
            document.getElementById("modal-text").textContent = text;
            document.getElementById("confirm-modal").classList.add("active");
        }

        function confirmYes() {
            if (confirmCallback) confirmCallback();
            document.getElementById("confirm-modal").classList.remove("active");
        }

        function confirmNo() {
            document.getElementById("confirm-modal").classList.remove("active");
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(main_template)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
