from flask import Flask, request, render_template_string, redirect, url_for, session, jsonify
import re
import os

app = Flask(__name__)
app.secret_key = "supersecretkey1234"

# رمز ثابت
PASSWORD = "dabirestan012345"

# داده‌ها در حافظه برای نمونه (در عمل به دیتابیس وصل شود)
students_data = {
    # پایه -> رشته -> لیست دانش آموز (هر دانش آموز dict)
    "10": {
        "ریاضی": []
    }
}

# تابع تشخیص موبایل ساده (User-Agent)
def is_mobile():
    ua = request.headers.get("User-Agent", "").lower()
    mobile_keys = ['iphone', 'android', 'blackberry', 'mobile']
    return any(k in ua for k in mobile_keys)

# قالب کلی CSS و JS داخل فایل Python (فقط نمونه)
base_css = """
<style>
    @import url('https://cdn.jsdelivr.net/gh/rastikerdar/vazir-font@v30.1.0/dist/font-face.css');
    body {
        font-family: 'Vazir', sans-serif;
        margin:0; padding:0; background:#0a1f44; color:#fff;
    }
    header {
        background:#022c3a; 
        padding: 10px 15px; 
        font-size: 24px;
        font-weight: bold;
        color: #d4af37;
        text-align:center;
        position: relative;
    }
    .container {
        max-width: 960px;
        margin: 10px auto;
        background: #152f57;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 0 10px #074d07;
    }
    label {display:block; margin-top:12px;}
    input, select {
        width: 100%;
        padding: 7px;
        border-radius: 6px;
        border: none;
        font-size: 16px;
    }
    input[type=button], button {
        border:none;
        padding: 12px;
        background: #4caf50;
        color: white;
        margin-top: 15px;
        border-radius: 12px;
        cursor: pointer;
        font-weight: bold;
        transition: .3s ease;
    }
    input[type=button]:hover, button:hover {
        background: #357a38;
        transform: scale(1.05);
    }
    .error {
        color:#ff5f5f; margin-top: 10px;
    }
    .menu-button {
        margin: 10px 5px 10px 0;
    }
    .student-card {
        background: #0f2d4f;
        padding: 14px 16px;
        margin: 10px 0;
        border-radius: 14px;
        position: relative;
        box-shadow: 0 0 10px #b4af37;
        cursor: pointer;
        display:flex;
        justify-content: space-between;
        align-items: center;
    }
    .student-info {
        flex-grow: 1;
    }
    .icon-btn {
        margin: 0 6px;
        background: #367636;
        border-radius: 50%;
        padding: 6px;
        cursor: pointer;
        transition: .3s ease;
    }
    .icon-btn:hover {
        background: #8cbf45;
        transform: scale(1.2);
    }
    .profile-section {
        background: #112f4c;
        padding: 15px;
        border-radius: 12px;
        max-width: 400px;
        margin: 20px auto;
    }
    .edit-field {
        display:flex;
        align-items:center;
        gap: 5px;
        margin: 10px 0;
    }
    .edit-field input[readonly] {
        background: #224776;
        border:none;
        color: #eee;
        border-radius: 6px;
        padding: 8px;
        flex-grow: 1;
    }
    .edit-field input.editable {
        background: #12355b;
    }
    .toolbar {
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: #224d44;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        color: #d4af37;
        font-size: 36px;
        line-height: 60px;
        text-align: center;
        cursor: pointer;
        box-shadow: 0 0 10px #d4af37;
        transition: background .3s ease;
    }
    .toolbar:hover {
        background: #176216;
    }
    /* توکار پاپ‌آپ */
    .popup-backdrop {
        position: fixed;
        top:0; left:0; right:0; bottom:0;
        background: rgba(0,0,0,0.7);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 99;
    }
    .popup {
        background: #0f2d4f;
        border-radius: 14px;
        padding: 20px;
        max-width: 320px;
        width: 90%;
        box-shadow: 0 0 20px #8cf17b;
    }
    .popup button {
        width: 45%;
        margin: 10px 2%;
        background: #587433;
    }
    /* انیمشن‌های اسلاید منو */
    .sidebar {
        position: fixed;
        top:0; right: -300px;
        width: 300px;
        height: 100%;
        background: #011627;
        box-shadow: -3px 0 10px rgba(0,0,0,.7);
        transition: right .4s cubic-bezier(0.25, 0.8, 0.25, 1);
        z-index: 100;
        display: flex;
        flex-direction: column;
        padding: 15px;
        color: #9a9a9a;
    }
    .sidebar.open {
        right: 0;
    }
    .sidebar .close-btn {
        align-self: flex-end;
        font-size: 28px;
        padding: 5px 10px;
        cursor: pointer;
        color: #d4af37;
    }
    .sidebar nav button {
        margin: 10px 0;
        background: #246524;
        border-radius: 12px;
        font-weight: bold;
    }
</style>
"""

base_js = """
<script>
    // باز و بسته کردن سایدبار
    function toggleSidebar() {
        const side = document.getElementById('sidebar');
        side.classList.toggle('open');
    }
    // تایید/انصراف ویرایش پروفایل
    function enableEdit(field) {
        const input = document.getElementById(field);
        if(!input.readOnly){
            return;
        }
        input.readOnly = false;
        input.classList.add('editable');
        const container = input.parentElement;
        // دکمه‌ها رو اضافه کن زیرش
        if(!container.querySelector('.edit-btns')) {
            let div = document.createElement('div');
            div.className = 'edit-btns';
            div.innerHTML = `
                <button onclick="saveEdit('${field}')">تایید</button>
                <button onclick="cancelEdit('${field}')">انصراف</button>`;
            container.appendChild(div);
            // مداد رو مخفی کن
            container.querySelector('.edit-btn').style.display = 'none';
        }
    }
    function saveEdit(field) {
        const input = document.getElementById(field);
        input.readOnly = true;
        input.classList.remove('editable');
        // حذف دکمه‌ها و مداد رو نمایش بده
        const container = input.parentElement;
        let btns = container.querySelector('.edit-btns');
        if (btns) btns.remove();
        container.querySelector('.edit-btn').style.display = 'inline-block';
        // ارسال تغییرات به سرور با Ajax
        fetch('/profile/edit', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({field: field, value: input.value})
        }).then(r => r.json()).then(data => {
            if(!data.success){
                alert('خطا در ثبت تغییرات');
            }
        });
    }
    function cancelEdit(field) {
        const input = document.getElementById(field);
        input.readOnly = true;
        input.classList.remove('editable');
        // حذف دکمه‌ها و مداد رو نمایش بده
        const container = input.parentElement;
        let btns = container.querySelector('.edit-btns');
        if (btns) btns.remove();
        container.querySelector('.edit-btn').style.display = 'inline-block';
        // بازگردانی مقدار اولیه (از سرور یا session)
        fetch('/profile/data').then(r => r.json()).then(data => {
            if(data[field]) {
                input.value = data[field];
            }
        });
    }
    // تایید خروج
    function confirmLogout() {
        if(confirm('آیا مطمئن هستید می‌خواهید از حساب خارج شوید؟')){
            window.location.href = '/logout';
        }
    }
    // نمایش پیام هشدار زیر فرم
    function showError(msg) {
        let errDiv = document.getElementById('error-msg');
        if(errDiv) {
            errDiv.innerText = msg;
            errDiv.style.display = 'block';
        }
    }
</script>
"""

# صفحه ورود
login_html = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head><meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1">
<title>ورود مدیر</title>
""" + base_css + """
</head>
<body>
<header>به سایت رسمی مدیر دبیرستان جوادالائمه خوش آمدید</header>
<div class="container">
    <form method="post" action="/">
        <label>نام:</label>
        <input type="text" name="name" value="{{ request.form.name or '' }}">
        <label>نام خانوادگی:</label>
        <input type="text" name="family" value="{{ request.form.family or '' }}">
        <label>مشخص کردن مرتبه:</label>
        <select name="role">
            <option value="">انتخاب کنید</option>
            <option value="مدیر" {% if request.form.role == 'مدیر' %}selected{% endif %}>مدیر</option>
            <option value="ناظم" {% if request.form.role == 'ناظم' %}selected{% endif %}>ناظم</option>
            <option value="معاون" {% if request.form.role == 'معاون' %}selected{% endif %}>معاون</option>
        </select>
        <label>رمز:</label>
        <input type="password" name="password" value="">
        {% if error %}
            <div class="error" id="error-msg">{{ error }}</div>
        {% else %}
            <div class="error" style="display:none;" id="error-msg"></div>
        {% endif %}
        <button type="submit">ورود</button>
    </form>
</div>
""" + base_js + """
</body>
</html>
"""

# منوی اصلی مدیران
dashboard_html = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head><meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1">
<title>داشبورد مدیر</title>
""" + base_css + """
</head>
<body>
<header>
  دبیرستان جوادالائمه
  <!-- دکمه سه خط بالا سمت راست -->
  <div style="position:absolute; top:10px; right:10px; cursor:pointer; font-size:24px; user-select:none;" onclick="toggleSidebar()">
    <div style="border-top:3px solid #d4af37; margin:4px 0;"></div>
    <div style="border-top:3px solid #d4af37; margin:4px 0;"></div>
    <div style="border-top:3px solid #d4af37; margin:4px 0;"></div>
  </div>
</header>

<div class="container">
    <h2>درگاه مدیران</h2>
    <button class="menu-button" onclick="location.href='/students'">مدیریت دانش آموزان</button>
    <button class="menu-button" disabled>مدیریت معلمان</button>
    <button class="menu-button" disabled>مدیریت گزارشات والدین</button>
    <button class="menu-button" disabled>مدیریت گزارشات معلمان</button>
    <button class="menu-button" disabled>مدیریت گزارشات دانش آموزان</button>
    <button class="menu-button" disabled>مدیریت بخش آزمایشگاه</button>
    <button class="menu-button" disabled>مدیریت نمرات</button>
    <button class="menu-button" disabled>مدیریت کارنامه</button>
</div>

<!-- سایدبار -->
<div id="sidebar" class="sidebar">
    <div class="close-btn" onclick="toggleSidebar()">&times;</div>
    <nav>
        <button onclick="location.href='/'">صفحه اصلی</button>
        <button onclick="location.href='/profile'">پروفایل</button>
        <button onclick="alert('نمایش اعلان‌ها - زیرساخت ندارد')">اعلان‌ها</button>
    </nav>
</div>

""" + base_js + """
</body>
</html>
"""

# قالب مدیریت دانش‌آموزان پایه دهم و ریاضی
students_html = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head><meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1">
<title>مدیریت دانش آموزان</title>
""" + base_css + """
</head>
<body>
<header>
  مدیریت دانش آموزان - پایه دهم - رشته ریاضی
  <div style="position:absolute; top:10px; right:10px; cursor:pointer; font-size:24px; user-select:none;" onclick="location.href='/dashboard'">
    ← بازگشت
  </div>
</header>
<div class="container">
    <div style="font-size: 20px; font-weight: bold; margin-bottom: 10px;">
        تعداد دانش‌آموز: <span id="student-count">{{ students|length }}</span> <span>👤</span>
    </div>

    <div id="students-list">
        {% for s in students %}
        <div class="student-card" data-id="{{ loop.index0 }}">
            <div class="student-info">
                <div><b>{{ s['name'] }} {{ s['family'] }}</b></div>
                <div>کد ملی: {{ s['national_id'] }}</div>
            </div>
            <div>
                <span class="icon-btn" onclick="editStudent({{ loop.index0 }}, event)" title="ویرایش">✏️</span>
                <span class="icon-btn" onclick="deleteStudent({{ loop.index0 }}, event)" title="حذف">🗑️</span>
            </div>
        </div>
        {% endfor %}
    </div>

    <div class="toolbar" title="افزودن دانش آموز +" onclick="showAddForm()">+</div>

    <div id="form-popup" class="popup-backdrop" style="display:none;">
        <div class="popup">
            <h3 id="form-title">افزودن دانش‌آموز جدید</h3>
            <form id="student-form">
                <label>نام دانش آموز (اجباری):</label>
                <input type="text" id="stu-name" name="name" required>
                <label>نام خانوادگی دانش آموز (اجباری):</label>
                <input type="text" id="stu-family" name="family" required>
                <label>کد ملی دانش آموز (اجباری):</label>
                <input type="text" id="stu-nid" name="national_id" required pattern="\\d{10,10}">
                <label>شماره دانش آموز (اختیاری):</label>
                <input type="text" id="stu-student-num" name="student_number">
                <label>شماره پدر (اختیاری):</label>
                <input type="text" id="stu-father-num" name="father_phone">
                <label>شماره مادر (اختیاری):</label>
                <input type="text" id="stu-mother-num" name="mother_phone">
                <div id="form-error" style="color:#ff5f5f; margin-top:10px; display:none;"></div>
                <button type="button" onclick="submitStudentForm()">تایید</button>
                <button type="button" onclick="hideAddForm()">انصراف</button>
            </form>
        </div>
    </div>
</div>

<script>
    var students = {{ students|tojson }};
    var editingIndex = -1;

    function showAddForm() {
        editingIndex = -1;
        document.getElementById('form-title').innerText = 'افزودن دانش‌آموز جدید';
        document.getElementById('student-form').reset();
        document.getElementById('form-error').style.display = 'none';
        document.getElementById('form-popup').style.display = 'flex';
    }
    function hideAddForm() {
        document.getElementById('form-popup').style.display = 'none';
    }
    function submitStudentForm() {
        var name = document.getElementById('stu-name').value.trim();
        var family = document.getElementById('stu-family').value.trim();
        var nid = document.getElementById('stu-nid').value.trim();
        // اعتبارسنجی اجباری
        if(!name || !family || !nid) {
            showError('لطفاً همه فیلدهای اجباری را پر کنید.');
            return;
        }
        // بررسی کد ملی تکراری
        for(let i=0; i<students.length; i++) {
            if(i !== editingIndex && students[i].national_id === nid) {
                showError('این دانش‌آموز با این کد ملی وجود دارد.');
                return;
            }
        }
        let studentNum = document.getElementById('stu-student-num').value.trim();
        let fatherNum = document.getElementById('stu-father-num').value.trim();
        let motherNum = document.getElementById('stu-mother-num').value.trim();
        let studentData = {
            name: name,
            family: family,
            national_id: nid,
            student_number: studentNum,
            father_phone: fatherNum,
            mother_phone: motherNum
        };
        if(editingIndex === -1) {
            students.push(studentData);
        } else {
            students[editingIndex] = studentData;
        }
        updateStudentsList();
        hideAddForm();
    }
    function showError(msg) {
        let err = document.getElementById('form-error');
        err.style.display = 'block';
        err.innerText = msg;
    }
    function updateStudentsList() {
        let container = document.getElementById('students-list');
        container.innerHTML = '';
        for(let i=0; i<students.length; i++) {
            let s = students[i];
            let div = document.createElement('div');
            div.className = 'student-card';
            div.setAttribute("data-id", i);
            div.innerHTML = `
                <div class="student-info">
                    <div><b>${s.name} ${s.family}</b></div>
                    <div>کد ملی: ${s.national_id}</div>
                </div>
                <div>
                    <span class="icon-btn" title="ویرایش" onclick="editStudent(${i}, event)">✏️</span>
                    <span class="icon-btn" title="حذف" onclick="deleteStudent(${i}, event)">🗑️</span>
                </div>`;
            container.appendChild(div);
        }
        document.getElementById('student-count').innerText = students.length;
    }
    function editStudent(idx, event) {
        event.stopPropagation();
        editingIndex = idx;
        let s = students[idx];
        document.getElementById('form-title').innerText = 'ویرایش دانش‌آموز';
        document.getElementById('stu-name').value = s.name;
        document.getElementById('stu-family').value = s.family;
        document.getElementById('stu-nid').value = s.national_id;
        document.getElementById('stu-student-num').value = s.student_number || '';
        document.getElementById('stu-father-num').value = s.father_phone || '';
        document.getElementById('stu-mother-num').value = s.mother_phone || '';
        document.getElementById('form-error').style.display = 'none';
        document.getElementById('form-popup').style.display = 'flex';
    }
    function deleteStudent(idx, event) {
        event.stopPropagation();
        if(confirm('آیا مطمئن هستید می‌خواهید اطلاعات دانش آموز را پاک کنید؟')) {
            students.splice(idx, 1);
            updateStudentsList();
        }
    }
</script>
</body>
</html>
"""

# صفحه پروفایل مدیر
profile_html = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head><meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1">
<title>پروفایل مدیر</title>
""" + base_css + """
</head>
<body>
<header>
  پروفایل
  <div style="position:absolute; top:10px; right:10px; cursor:pointer; font-size:24px; user-select:none;"
       onclick="location.href='/dashboard'">← بازگشت</div>
</header>
<div class="container profile-section">
    <div class="edit-field">
        <label for="name" style="flex-grow: 1;">نام:</label>
        <input id="name" type="text" value="{{ user.name }}" readonly>
        <span class="edit-btn" style="cursor:pointer; color:#d4af37;" onclick="enableEdit('name')">✏️</span>
    </div>
    <div class="edit-field">
        <label for="family" style="flex-grow: 1;">نام خانوادگی:</label>
        <input id="family" type="text" value="{{ user.family }}" readonly>
        <span class="edit-btn" style="cursor:pointer; color:#d4af37;" onclick="enableEdit('family')">✏️</span>
    </div>
    <div class="edit-field">
        <label for="role" style="flex-grow: 1;">مرتبه:</label>
        <input id="role" type="text" value="{{ user.role }}" readonly>
        <span class="edit-btn" style="cursor:pointer; color:#999;" title="قابل تغییر نمیباشد">🔒</span>
    </div>
    <div class="edit-field">
        <label for="password" style="flex-grow: 1;">رمز:</label>
        <input id="password" type="password" value="**********" readonly>
        <span class="edit-btn" style="cursor:pointer; color:#999;" title="قابل تغییر نمیباشد">🔒</span>
    </div>
    <button onclick="confirmLogout()">خروج از حساب</button>
</div>
""" + base_js + """
</body>
</html>
"""

# صفحه موبایل (نمونه ساده تفاوت)
mobile_html = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head><meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1">
<title>وب سایت مخصوص گوشی</title>
""" + base_css + """
<style>
.container {font-size: 18px;}
</style>
</head>
<body>
<header>به سایت رسمی مدیر دبیرستان جوادالائمه خوش آمدید (نسخه موبایل)</header>
<div class="container">
    <p>نسخه موبایل در حال توسعه است.</p>
    <button onclick="location.href='/dashboard'">ورود به داشبورد</button>
</div>
""" + base_js + """
</body>
</html>
"""

# صفحه دسکتاپ (صفحه ورود اصلی)
desktop_html = login_html

# مسیرها:

@app.route("/", methods=["GET", "POST"])
def login():
    if 'user' in session:
        return redirect("/dashboard")
    error = None
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        family = request.form.get("family", "").strip()
        role = request.form.get("role", "")
        password = request.form.get("password", "")
        if not name or not family or not role or not password:
            error = "لطفاً همه فیلدها را پر کنید."
        elif password != PASSWORD:
            error = "رمز وارد شده اشتباه است."
        else:
            # ذخیره کاربر در سشن
            session['user'] = {"name": name, "family": family, "role": role}
            return redirect("/dashboard")
    # تشخیص موبایل یا دسکتاپ
    if is_mobile():
        return render_template_string(mobile_html, error=error, request=request)
    else:
        return render_template_string(desktop_html, error=error, request=request)

@app.route("/dashboard")
def dashboard():
    if 'user' not in session:
        return redirect("/")
    # صفحه منوی اصلی
    return render_template_string(dashboard_html)

@app.route("/profile")
def profile():
    if 'user' not in session:
        return redirect("/")
    return render_template_string(profile_html, user=session['user'])

@app.route("/profile/edit", methods=['POST'])
def profile_edit():
    if 'user' not in session:
        return jsonify({"success": False})
    data = request.json
    field = data.get("field")
    value = data.get("value")
    if field in ["name", "family"]:
        user = session['user']
        user[field] = value
        session['user'] = user
        return jsonify({"success": True})
    return jsonify({"success": False})

@app.route("/profile/data")
def profile_data():
    if 'user' not in session:
        return jsonify({})
    return jsonify(session['user'])

# مدیریت دانش‌آموزان پایه دهم رشته ریاضی (نمونه)

@app.route("/students")
def students():
    if 'user' not in session:
        return redirect("/")
    # فقط پایه دهم و ریاضی برای نمونه
    students = students_data.get("10", {}).get("ریاضی", [])
    return render_template_string(students_html, students=students)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
