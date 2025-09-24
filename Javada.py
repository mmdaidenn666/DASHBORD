from flask import Flask, render_template_string, request, jsonify, redirect, url_for

app = Flask(__name__)

# --- متغیرهای جهانی ---
admins = []
students = []
admin_logged_in = False
current_admin = {}

# --- HTML/CSS/JS در یک استرینگ ---
html_template = '''
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <title>سایت دبیرستان جوادالائمه</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background: #0a0a0a;
            color: white;
            font-family: "Vazir", sans-serif;
            overflow-x: hidden;
        }

        .neon-btn {
            background: transparent;
            border: 2px solid;
            padding: 12px 24px;
            border-radius: 10px;
            cursor: pointer;
            color: #fff;
            outline: none;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            margin: 10px;
        }

        .neon-btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: inherit;
            filter: blur(20px);
            opacity: 0.7;
            z-index: -1;
        }

        .neon-btn:hover {
            transform: scale(1.05);
        }

        .btn-red { border-color: #ff0055; box-shadow: 0 0 10px #ff0055, 0 0 20px #ff0055; }
        .btn-green { border-color: #00ffaa; box-shadow: 0 0 10px #00ffaa, 0 0 20px #00ffaa; }
        .btn-blue { border-color: #00aaff; box-shadow: 0 0 10px #00aaff, 0 0 20px #00aaff; }
        .btn-purple { border-color: #cc00ff; box-shadow: 0 0 10px #cc00ff, 0 0 20px #cc00ff; }

        .container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 90vh;
        }

        .toolbar {
            display: flex;
            justify-content: space-between;
            padding: 15px;
            background: rgba(0,0,0,0.6);
            border-bottom: 1px solid #444;
        }

        .form-group {
            margin: 10px;
        }

        input, select {
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #444;
            background: rgba(0,0,0,0.5);
            color: white;
            width: 200px;
        }

        .alert {
            color: #ff0055;
            margin: 10px;
            animation: shake 0.5s;
        }

        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-5px); }
            75% { transform: translateX(5px); }
        }

        .student-card {
            background: rgba(0,0,0,0.6);
            border: 1px solid;
            border-radius: 10px;
            padding: 15px;
            margin: 10px;
            width: 200px;
            text-align: center;
            position: relative;
        }

        .card-actions {
            display: flex;
            justify-content: space-around;
            margin-top: 10px;
        }

        .edit-btn, .delete-btn {
            background: transparent;
            border: none;
            color: white;
            cursor: pointer;
        }

        .search-box {
            margin: 10px;
        }

        .hidden {
            display: none;
        }
    </style>
</head>
<body>
    <div id="home">
        <h1 style="text-align: center; margin-top: 50px; color: #00ffaa; text-shadow: 0 0 10px #00ffaa;">به سایت رسمی دبیرستان پسرانه جوادالائمه خوش آمدید</h1>
        <div class="container">
            <button class="neon-btn btn-red" onclick="showLogin('admin')">ورود مدیران</button>
            <button class="neon-btn btn-green" onclick="alert('این بخش فقط برای معلمان است')">ورود معلمان</button>
            <button class="neon-btn btn-blue" onclick="alert('این بخش فقط برای والدین است')">ورود والدین</button>
            <button class="neon-btn btn-purple" onclick="alert('این بخش فقط برای دانش آموزان است')">ورود دانش آموزان</button>
        </div>
    </div>

    <div id="loginAdmin" class="hidden">
        <h2>ورود مدیران</h2>
        <div class="form-group">
            <input type="text" id="adminName" placeholder="نام" />
        </div>
        <div class="form-group">
            <input type="text" id="adminFamily" placeholder="نام خانوادگی" />
        </div>
        <div class="form-group">
            <select id="adminRole">
                <option value="">انتخاب مرتبه</option>
                <option value="مدیر">مدیر</option>
                <option value="ناظم">ناظم</option>
                <option value="معاون">معاون</option>
                <option value="مشاور">مشاور</option>
            </select>
        </div>
        <div class="form-group">
            <input type="password" id="adminPass" placeholder="رمز" />
        </div>
        <button class="neon-btn btn-green" onclick="loginAdmin()">ورود</button>
        <div id="loginAlert" class="alert"></div>
    </div>

    <div id="adminPanel" class="hidden">
        <div class="toolbar">
            <button onclick="showSection('profile')">پروفایل</button>
            <button onclick="showSection('dashboard')">صفحه اصلی</button>
            <button onclick="showSection('notifications')">اعلانات</button>
        </div>

        <div id="profileSection" class="hidden">
            <h2>پروفایل</h2>
            <p>نام: <span id="profName">-</span> <button onclick="editField('name')">✏️</button></p>
            <p>نام خانوادگی: <span id="profFamily">-</span> <button onclick="editField('family')">✏️</button></p>
            <p>مرتبه: <span id="profRole">-</span> <button onclick="editField('role')">✏️</button></p>
            <p>رمز: <span id="profPass">******</span> (غیرقابل ویرایش)</p>
            <button class="neon-btn btn-red" onclick="confirmLogout()">خروج از حساب</button>
        </div>

        <div id="dashboardSection" class="hidden">
            <h2>درگاه مدیران</h2>
            <button class="neon-btn btn-purple" onclick="loadStudents()">مدیریت دانش آموزان</button>
            <button class="neon-btn btn-blue" onclick="alert('به زودی')">مدیریت معلمان</button>
            <button class="neon-btn btn-green" onclick="alert('به زودی')">مدیریت گزارشات والدین</button>
            <button class="neon-btn btn-red" onclick="alert('به زودی')">مدیریت گزارشات معلمان</button>
            <button class="neon-btn btn-blue" onclick="alert('به زودی')">مدیریت گزارشات دانش آموزان</button>
            <button class="neon-btn btn-purple" onclick="alert('به زودی')">مدیریت بخش آزمایشگاه</button>
        </div>

        <div id="studentsSection" class="hidden">
            <h2>مدیریت دانش آموزان</h2>
            <button class="neon-btn btn-green" onclick="loadGrade('10')">پایه دهم</button>
            <button class="neon-btn btn-blue" onclick="loadGrade('11')">پایه یازدهم</button>
            <button class="neon-btn btn-purple" onclick="loadGrade('12')">پایه دوازدهم</button>
        </div>

        <div id="gradeSection" class="hidden">
            <h2 id="gradeTitle"></h2>
            <button class="neon-btn btn-green" onclick="loadField('math')">ریاضی</button>
            <button class="neon-btn btn-blue" onclick="loadField('science')">تجربی</button>
            <button class="neon-btn btn-purple" onclick="loadField('human')">انسانی</button>
        </div>

        <div id="fieldSection" class="hidden">
            <h2 id="fieldTitle"></h2>
            <div style="display:flex; align-items:center;">
                <span>تعداد دانش‌آموزان:</span>
                <span id="studentCount">0</span>
                <span>👤</span>
            </div>
            <div id="studentList"></div>
            <div class="toolbar">
                <button onclick="showAddForm()" style="position:fixed; bottom:30px; right:30px; width:60px; height:60px; border-radius:50%; background:#00ffaa; color:white; border:none; font-size:24px;">+</button>
            </div>
        </div>

        <div id="addStudentForm" class="hidden">
            <h3>افزودن دانش‌آموز</h3>
            <div class="form-group">
                <input type="text" id="stdName" placeholder="نام دانش آموز" />
            </div>
            <div class="form-group">
                <input type="text" id="stdFamily" placeholder="نام خانوادگی دانش آموز" />
            </div>
            <div class="form-group">
                <input type="text" id="stdCode" placeholder="کد ملی دانش آموز" />
            </div>
            <div class="form-group">
                <input type="text" id="stdNumber" placeholder="شماره دانش آموز (اختیاری)" />
            </div>
            <div class="form-group">
                <input type="text" id="stdFather" placeholder="شماره پدر (اختیاری)" />
            </div>
            <div class="form-group">
                <input type="text" id="stdMother" placeholder="شماره مادر (اختیاری)" />
            </div>
            <button class="neon-btn btn-green" onclick="addStudent()">تایید</button>
            <button class="neon-btn btn-red" onclick="hideAddForm()">انصراف</button>
            <div id="addAlert" class="alert"></div>
        </div>

        <div id="searchSection" class="hidden">
            <h3>جستجوی دانش‌آموز</h3>
            <input type="text" id="searchInput" class="search-box" placeholder="نام، نام خانوادگی یا کد ملی" />
            <button class="neon-btn btn-green" onclick="performSearch()">جستجو</button>
            <div id="searchResults"></div>
        </div>
    </div>

    <script>
        let currentGrade = '';
        let currentField = '';
        let editingField = '';

        function showLogin(type) {
            document.getElementById('home').classList.add('hidden');
            document.getElementById('loginAdmin').classList.remove('hidden');
        }

        function loginAdmin() {
            const name = document.getElementById('adminName').value;
            const family = document.getElementById('adminFamily').value;
            const role = document.getElementById('adminRole').value;
            const password = document.getElementById('adminPass').value;

            if (!name || !family || !role || !password) {
                document.getElementById('loginAlert').innerText = 'لطفاً تمام فیلدها را پر کنید.';
                return;
            }

            if (password !== 'dabirestan012345') {
                document.getElementById('loginAlert').innerText = 'رمز اشتباه است.';
                return;
            }

            current_admin = { name, family, role, password };
            admins.push(current_admin);
            admin_logged_in = true;

            document.getElementById('loginAdmin').classList.add('hidden');
            document.getElementById('adminPanel').classList.remove('hidden');
            document.getElementById('profName').innerText = name;
            document.getElementById('profFamily').innerText = family;
            document.getElementById('profRole').innerText = role;
        }

        function showSection(sec) {
            document.getElementById('profileSection').classList.add('hidden');
            document.getElementById('dashboardSection').classList.add('hidden');
            document.getElementById('studentsSection').classList.add('hidden');
            document.getElementById('gradeSection').classList.add('hidden');
            document.getElementById('fieldSection').classList.add('hidden');
            document.getElementById('addStudentForm').classList.add('hidden');

            document.getElementById(`${sec}Section`).classList.remove('hidden');
        }

        function loadStudents() {
            showSection('students');
        }

        function loadGrade(grade) {
            currentGrade = grade;
            showSection('grade');
            document.getElementById('gradeTitle').innerText = `پایه ${grade}`;
        }

        function loadField(field) {
            currentField = field;
            showSection('field');
            document.getElementById('fieldTitle').innerText = getFieldName(field);
            updateStudentList();
        }

        function getFieldName(field) {
            if (field === 'math') return 'ریاضی';
            if (field === 'science') return 'تجربی';
            if (field === 'human') return 'انسانی';
            return field;
        }

        function updateStudentList() {
            const list = document.getElementById('studentList');
            list.innerHTML = '';
            const count = document.getElementById('studentCount');
            let total = 0;

            students.forEach((s, i) => {
                if (s.grade === currentGrade && s.field === currentField) {
                    total++;
                    const card = document.createElement('div');
                    card.className = 'student-card';
                    card.innerHTML = `
                        <p>${s.name} ${s.family}</p>
                        <p>${s.code}</p>
                        <div class="card-actions">
                            <button class="edit-btn" onclick="editStudent(${i})">✏️</button>
                            <button class="delete-btn" onclick="deleteStudent(${i})">🗑️</button>
                        </div>
                    `;
                    card.onclick = () => viewStudent(s);
                    list.appendChild(card);
                }
            });

            count.innerText = total;
        }

        function showAddForm() {
            document.getElementById('fieldSection').classList.add('hidden');
            document.getElementById('addStudentForm').classList.remove('hidden');
        }

        function hideAddForm() {
            document.getElementById('addStudentForm').classList.add('hidden');
            document.getElementById('fieldSection').classList.remove('hidden');
            clearForm();
        }

        function clearForm() {
            document.getElementById('stdName').value = '';
            document.getElementById('stdFamily').value = '';
            document.getElementById('stdCode').value = '';
            document.getElementById('stdNumber').value = '';
            document.getElementById('stdFather').value = '';
            document.getElementById('stdMother').value = '';
            document.getElementById('addAlert').innerText = '';
        }

        function addStudent() {
            const name = document.getElementById('stdName').value;
            const family = document.getElementById('stdFamily').value;
            const code = document.getElementById('stdCode').value;
            const number = document.getElementById('stdNumber').value;
            const father = document.getElementById('stdFather').value;
            const mother = document.getElementById('stdMother').value;

            if (!name || !family || !code) {
                document.getElementById('addAlert').innerText = 'نام، نام خانوادگی و کد ملی الزامی است.';
                return;
            }

            if (students.some(s => s.code === code)) {
                document.getElementById('addAlert').innerText = 'دانش‌آموزی با این کد ملی وجود دارد.';
                return;
            }

            const newStudent = { name, family, code, number, father, mother, grade: currentGrade, field: currentField };
            students.push(newStudent);
            hideAddForm();
            updateStudentList();
        }

        function editStudent(index) {
            alert('ویرایش دانش‌آموز در نسخه کامل پیاده‌سازی خواهد شد.');
        }

        function deleteStudent(index) {
            if (confirm('آیا مطمئن هستید می‌خواهید اطلاعات دانش آموز را پاک کنید؟')) {
                students.splice(index, 1);
                updateStudentList();
            }
        }

        function viewStudent(s) {
            alert(`نام: ${s.name}\\nنام خانوادگی: ${s.family}\\nکد ملی: ${s.code}\\nشماره دانش‌آموز: ${s.number || 'ثبت نشده'}\\nشماره پدر: ${s.father || 'ثبت نشده'}\\nشماره مادر: ${s.mother || 'ثبت نشده'}`);
        }

        function editField(field) {
            editingField = field;
            const span = document.getElementById('prof' + capitalize(field));
            span.innerHTML = `<input type="text" id="edit${capitalize(field)}" value="${current_admin[field]}"> <button onclick="saveEdit()">✓</button>`;
        }

        function capitalize(str) {
            return str.charAt(0).toUpperCase() + str.slice(1);
        }

        function saveEdit() {
            const input = document.getElementById('edit' + capitalize(editingField));
            const value = input.value;
            current_admin[editingField] = value;
            document.getElementById('prof' + capitalize(editingField)).innerText = value;
        }

        function confirmLogout() {
            if (confirm('آیا مطمئن هستید می‌خواهید از حساب خارج شوید؟')) {
                admin_logged_in = false;
                document.getElementById('adminPanel').classList.add('hidden');
                document.getElementById('home').classList.remove('hidden');
            }
        }

        function performSearch() {
            const query = document.getElementById('searchInput').value.toLowerCase();
            const results = document.getElementById('searchResults');
            results.innerHTML = '';

            students.forEach(s => {
                if (s.name.toLowerCase().includes(query) || s.family.toLowerCase().includes(query) || s.code.includes(query)) {
                    const card = document.createElement('div');
                    card.className = 'student-card';
                    card.innerHTML = `
                        <p>${s.name} ${s.family}</p>
                        <p>${s.code}</p>
                        <p>پایه ${s.grade} - ${getFieldName(s.field)}</p>
                    `;
                    card.onclick = () => viewStudent(s);
                    results.appendChild(card);
                }
            });
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(html_template)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)