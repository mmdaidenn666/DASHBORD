from flask import Flask, render_template_string, request, redirect, url_for, session, flash
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Data Storage
users = {
    'admin': {'password': 'dabirestan012345', 'name': 'مدیر', 'surname': 'دبیرستان', 'rank': 'مدیر'},
    'teacher': {'password': 'dabirjavadol', 'name': 'معلم', 'surname': 'نمونه', 'rank': 'معلم', 'grades': ['دهم'], 'fields': ['ریاضی'], 'subjects': ['ریاضی']},
    'parent': {'name': 'والد', 'surname': 'نمونه', 'grade': 'دهم', 'field': 'ریاضی', 'child1': 'علی احمدی', 'child2': None},
    'student': {'name': 'دانش آموز', 'surname': 'نمونه', 'grade': 'دهم', 'field': 'ریاضی', 'national_id': '1234567890', 'password': '123456'}
}

students = {
    'ریاضی': {'دهم': [{'id': 1, 'name': 'علی', 'surname': 'احمدی', 'national_id': '1234567890'}], 'یازدهم': [], 'دوازدهم': []},
    'تجربی': {'دهم': [], 'یازدهم': [], 'دوازدهم': []},
    'انسانی': {'دهم': [], 'یازدهم': [], 'دوازدهم': []},
}

announcements = []
attendance_records = []
grades = {}
reports = []
notes = []
assignments = []
admin_list = [{'name': 'محمد', 'surname': 'حسینی', 'rank': 'مدیر'}]
teacher_list = [{'name': 'علی', 'surname': 'محمدی', 'grades': ['دهم'], 'fields': ['ریاضی'], 'subjects': ['ریاضی']}]
lab_experiments = [{'images': ['img1.jpg'], 'desc': 'توضیحات آزمایش'}]

CSS = """
<style>
body {
    font-family: 'Vazirmatn', sans-serif;
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    color: white;
    margin: 0;
    padding: 0;
    min-height: 100vh;
    overflow-x: hidden;
}
.container {
    max-width: 1200px;
    margin: auto;
    padding: 20px;
}
.header {
    text-align: center;
    font-size: 2rem;
    margin: 20px 0;
    animation: fadeInDown 1s;
    background: linear-gradient(90deg, #ff00cc, #00eeff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 0 10px rgba(255, 0, 204, 0.7);
}
.buttons-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin-top: 40px;
}
.btn {
    background: rgba(255,255,255,0.1);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    padding: 20px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    border: 1px solid rgba(255,255,255,0.2);
    position: relative;
    overflow: hidden;
    color: white;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}
.btn::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    transition: 0.5s;
}
.btn:hover::before {
    left: 100%;
}
.btn:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 10px 25px rgba(0,0,0,0.3);
}
.btn-admin { background: linear-gradient(135deg, #ff00cc, #ff0066); }
.btn-teacher { background: linear-gradient(135deg, #00eeff, #0066ff); }
.btn-parent { background: linear-gradient(135deg, #ffcc00, #ff6600); }
.btn-student { background: linear-gradient(135deg, #00ff99, #00cc66); }
.form-container {
    background: rgba(255,255,255,0.1);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    padding: 30px;
    max-width: 500px;
    margin: 50px auto;
    box-shadow: 0 10px 20px rgba(0,0,0,0.3);
    border: 1px solid rgba(255,255,255,0.2);
}
.form-group {
    margin-bottom: 15px;
    text-align: right;
}
.form-group label {
    display: block;
    margin-bottom: 5px;
}
.form-group input, .form-group select, .form-group textarea {
    width: 100%;
    padding: 10px;
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,0.2);
    background: rgba(0,0,0,0.2);
    color: white;
    transition: all 0.3s;
}
.form-group input:focus, .form-group select:focus, .form-group textarea:focus {
    outline: none;
    border-color: #00eeff;
    box-shadow: 0 0 10px rgba(0,238,255,0.5);
    transform: scale(1.02);
}
.btn-submit {
    background: linear-gradient(135deg, #00eeff, #0066ff);
    color: white;
    border: none;
    padding: 12px;
    border-radius: 10px;
    cursor: pointer;
    width: 100%;
    font-size: 1rem;
}
.btn-submit:hover {
    transform: scale(1.02);
}
.error {
    color: #ff4444;
    background: rgba(255,0,0,0.2);
    padding: 10px;
    border-radius: 10px;
    margin-top: 10px;
}
.dashboard-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-top: 30px;
}
.student-card {
    background: rgba(255,255,255,0.1);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    padding: 15px;
    margin: 10px 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border: 1px solid rgba(255,255,255,0.2);
}
.student-card:hover {
    background: rgba(255,255,255,0.2);
}
.notification-dot {
    width: 10px;
    height: 10px;
    background-color: #ff4444;
    border-radius: 50%;
    display: inline-block;
    margin-right: 10px;
}
.sidebar {
    position: fixed;
    top: 0;
    right: 0;
    width: 300px;
    height: 100%;
    background: rgba(0,0,0,0.8);
    backdrop-filter: blur(10px);
    z-index: 1000;
    transform: translateX(100%);
    transition: transform 0.3s ease;
    padding: 20px;
    color: white;
}
.sidebar.active {
    transform: translateX(0);
}
.menu-toggle {
    position: fixed;
    top: 20px;
    right: 20px;
    width: 30px;
    height: 30px;
    display: flex;
    flex-direction: column;
    justify-content: space-around;
    cursor: pointer;
    z-index: 1001;
}
.menu-toggle span {
    height: 3px;
    background: white;
    width: 100%;
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.05); } 100% { transform: scale(1); } }
@keyframes bounceIn { from { transform: scale(0.1); opacity: 0; } to { transform: scale(1); opacity: 1; } }
@keyframes zoomIn { from { transform: scale(0.8); opacity: 0; } to { transform: scale(1); opacity: 1; } }
@keyframes fadeInDown { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: translateY(0); } }
</style>
"""

@app.route('/')
def index():
    html = f"""
    {CSS}
    <div class="container">
        <h1 class="header">به سایت رسمی دبیرستان پسرانه جوادالائمه خوش آمدید</h1>
        <div class="buttons-container">
            <div class="btn btn-admin" onclick="location.href='/login/admin'">ورود مدیران<br><small>این بخش فقط برای مدیران است</small></div>
            <div class="btn btn-teacher" onclick="location.href='/login/teacher'">ورود معلمان<br><small>این بخش فقط برای معلمان است</small></div>
            <div class="btn btn-parent" onclick="location.href='/login/parent'">ورود والدین<br><small>این بخش فقط برای والدین است</small></div>
            <div class="btn btn-student" onclick="location.href='/login/student'">ورود دانش آموزان<br><small>این بخش فقط برای دانش آموزان است</small></div>
        </div>
    </div>
    """
    return render_template_string(html)

@app.route('/login/admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        name = request.form.get('name')
        surname = request.form.get('surname')
        rank = request.form.get('rank')
        password = request.form.get('password')

        if not name or not surname or not rank or not password or password != 'dabirestan012345':
            flash('اطلاعات نامعتبر است.')
            return redirect(url_for('login_admin'))

        session['user'] = {'name': name, 'surname': surname, 'rank': rank, 'type': 'admin'}
        return redirect(url_for('admin_dashboard'))

    html = f"""
    {CSS}
    <div class="container">
        <div class="form-container">
            <h2>ورود مدیران</h2>
            <form method="post">
                <div class="form-group">
                    <label>نام</label>
                    <input type="text" name="name" required />
                </div>
                <div class="form-group">
                    <label>نام خانوادگی</label>
                    <input type="text" name="surname" required />
                </div>
                <div class="form-group">
                    <label>مرتبه</label>
                    <select name="rank" required>
                        <option value="مدیر">مدیر</option>
                        <option value="ناظم">ناظم</option>
                        <option value="معاون">معاون</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>رمز عبور</label>
                    <input type="password" name="password" value="dabirestan012345" readonly />
                </div>
                <button type="submit" class="btn-submit">ورود</button>
                <a href="/">← بازگشت</a>
            </form>
        </div>
    </div>
    """
    return render_template_string(html)

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user' not in session or session['user']['type'] != 'admin':
        return redirect(url_for('index'))

    # Check for new notifications
    new_reports = len(reports)
    new_notifications = 0
    if new_reports > 0:
        new_notifications += 1

    html = f"""
    {CSS}
    <div class="menu-toggle" onclick="toggleSidebar()">
        <span></span>
        <span></span>
        <span></span>
    </div>
    <div class="container">
        <h1 class="header">درگاه مدیران</h1>
        <div class="dashboard-container">
            <div class="btn btn-admin" onclick="markAsRead('/manage/students'); location.href='/manage/students'">مدیریت دانش آموزان</div>
            <div class="btn btn-admin" onclick="markAsRead('/manage/teachers'); location.href='/manage/teachers'">مدیریت معلمان</div>
            <div class="btn btn-admin" onclick="markAsRead('/manage/reports/parents'); location.href='/manage/reports/parents'">مدیریت گزارشات والدین</div>
            <div class="btn btn-admin" onclick="markAsRead('/manage/reports/teachers'); location.href='/manage/reports/teachers'">مدیریت گزارشات معلمان</div>
            <div class="btn btn-admin" onclick="markAsRead('/manage/reports/students'); location.href='/manage/reports/students'">مدیریت گزارشات دانش آموزان</div>
            <div class="btn btn-admin" onclick="markAsRead('/manage/labs'); location.href='/manage/labs'">مدیریت آزمایشگاه</div>
            <div class="btn btn-admin" onclick="markAsRead('/manage/grades'); location.href='/manage/grades'">مدیریت نمرات</div>
            <div class="btn btn-admin" onclick="markAsRead('/manage/reportcards'); location.href='/manage/reportcards'">مدیریت کارنامه</div>
        </div>
    </div>
    <div class="sidebar" id="sidebar">
        <a href="/admin/dashboard" class="toolbar-btn">🏠 صفحه اصلی</a>
        <a href="/admin/profile" class="toolbar-btn">👤 پروفایل</a>
        <a href="/admin/announcements" class="toolbar-btn">🔔 اعلانات</a>
    </div>
    <script>
        function toggleSidebar() {{
            document.getElementById('sidebar').classList.toggle('active');
        }}
        function markAsRead(url) {{
            // Remove notification dot
            let btn = document.querySelector(`[onclick*="${{url}}"]`);
            if (btn) {{
                let dot = btn.querySelector('.notification-dot');
                if (dot) dot.remove();
            }}
        }}
    </script>
    """
    return render_template_string(html)

@app.route('/admin/profile')
def admin_profile():
    if 'user' not in session:
        return redirect(url_for('index'))

    user = session['user']
    html = f"""
    {CSS}
    <div class="container">
        <h1 class="header">پروفایل</h1>
        <div class="form-container">
            <p><b>نام:</b> {user['name']}</p>
            <p><b>نام خانوادگی:</b> {user['surname']}</p>
            <p><b>مرتبه:</b> {user['rank']}</p>
            <p><b>رمز:</b> dabirestan012345</p>
            <button onclick="location.href='/admin/logout'" class="btn-submit">خروج از حساب</button>
        </div>
    </div>
    """
    return render_template_string(html)

@app.route('/admin/logout')
def admin_logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/admin/announcements')
def admin_announcements():
    html = f"""
    {CSS}
    <div class="container">
        <h1 class="header">اعلانات</h1>
        <div class="form-container">
            <p>هیچ اعلانی وجود ندارد.</p>
        </div>
    </div>
    """
    return render_template_string(html)

@app.route('/manage/students', defaults={'grade': None, 'field': None})
@app.route('/manage/students/<grade>', defaults={'field': None})
@app.route('/manage/students/<grade>/<field>')
def manage_students(grade, field):
    if 'user' not in session or session['user']['type'] != 'admin':
        return redirect(url_for('index'))

    if not grade:
        html = f"""
        {CSS}
        <div class="container">
            <h1 class="header">مدیریت دانش آموزان</h1>
            <div class="dashboard-container">
                <div class="btn btn-student" onclick="location.href='/manage/students/دهم'">پایه دهم</div>
                <div class="btn btn-student" onclick="location.href='/manage/students/یازدهم'">پایه یازدهم</div>
                <div class="btn btn-student" onclick="location.href='/manage/students/دوازدهم'">پایه دوازدهم</div>
            </div>
        </div>
        """
    elif not field:
        html = f"""
        {CSS}
        <div class="container">
            <h1 class="header">رشته دانش آموزان {grade}</h1>
            <div class="dashboard-container">
                <div class="btn btn-student" onclick="location.href='/manage/students/{grade}/ریاضی'">ریاضی</div>
                <div class="btn btn-student" onclick="location.href='/manage/students/{grade}/تجربی'">تجربی</div>
                <div class="btn btn-student" onclick="location.href='/manage/students/{grade}/انسانی'">انسانی</div>
            </div>
        </div>
        """
    else:
        student_list = students[field][grade]
        count = len(student_list)
        html = f"""
        {CSS}
        <div class="container">
            <h1 class="header">دانش آموزان {grade} - {field}</h1>
            <div style="display:flex; align-items:center; margin-bottom:20px;">
                <span>تعداد: {count}</span>
            </div>
            <div id="students-list">
                {''.join([f'<div class="student-card"><div><b>{s["name"]} {s["surname"]}</b><br>{s["national_id"]}</div><div class="edit-del"><button class="edit">✏️</button><button class="delete">🗑️</button></div></div>' for s in student_list])}
            </div>
        </div>
        """
    return render_template_string(html)

@app.route('/manage/teachers')
def manage_teachers():
    if 'user' not in session or session['user']['type'] != 'admin':
        return redirect(url_for('index'))

    html = f"""
    {CSS}
    <div class="container">
        <h1 class="header">مدیریت معلمان</h1>
        <div class="form-container">
            <p>هیچ معلمی وجود ندارد.</p>
        </div>
    </div>
    """
    return render_template_string(html)

@app.route('/manage/reports/<rtype>')
def manage_reports(rtype):
    if 'user' not in session or session['user']['type'] != 'admin':
        return redirect(url_for('index'))

    report_type_map = {'parents': 'گزارشات والدین', 'teachers': 'گزارشات معلمان', 'students': 'گزارشات دانش آموزان'}
    html = f"""
    {CSS}
    <div class="container">
        <h1 class="header">{report_type_map.get(rtype, 'گزارشات')}</h1>
        <div class="form-container">
            <p>هیچ گزارشی وجود ندارد.</p>
        </div>
    </div>
    """
    return render_template_string(html)

@app.route('/manage/labs')
def manage_labs():
    if 'user' not in session or session['user']['type'] != 'admin':
        return redirect(url_for('index'))

    html = f"""
    {CSS}
    <div class="container">
        <h1 class="header">مدیریت آزمایشگاه</h1>
        <div class="form-container">
            <p>هیچ محتوایی وجود ندارد.</p>
        </div>
    </div>
    """
    return render_template_string(html)

@app.route('/manage/grades')
def manage_grades():
    if 'user' not in session or session['user']['type'] != 'admin':
        return redirect(url_for('index'))

    html = f"""
    {CSS}
    <div class="container">
        <h1 class="header">مدیریت نمرات</h1>
        <div class="form-container">
            <p>هیچ نمره‌ای وجود ندارد.</p>
        </div>
    </div>
    """
    return render_template_string(html)

@app.route('/manage/reportcards')
def manage_reportcards():
    if 'user' not in session or session['user']['type'] != 'admin':
        return redirect(url_for('index'))

    html = f"""
    {CSS}
    <div class="container">
        <h1 class="header">مدیریت کارنامه</h1>
        <div class="form-container">
            <p>هیچ کارنامه‌ای وجود ندارد.</p>
        </div>
    </div>
    """
    return render_template_string(html)

@app.route('/login/teacher', methods=['GET', 'POST'])
def login_teacher():
    if request.method == 'POST':
        name = request.form.get('name')
        surname = request.form.get('surname')
        grade_count = request.form.get('grade_count')
        grade1 = request.form.get('grade1') if grade_count and int(grade_count) >= 1 else None
        grade2 = request.form.get('grade2') if grade_count and int(grade_count) >= 2 else None
        grade3 = request.form.get('grade3') if grade_count and int(grade_count) == 3 else None
        field_count = request.form.get('field_count')
        field1 = request.form.get('field1') if field_count and int(field_count) >= 1 else None
        field2 = request.form.get('field2') if field_count and int(field_count) >= 2 else None
        field3 = request.form.get('field3') if field_count and int(field_count) == 3 else None
        subject_count = request.form.get('subject_count')
        subject1 = request.form.get('subject1') if subject_count and int(subject_count) >= 1 else None
        subject2 = request.form.get('subject2') if subject_count and int(subject_count) >= 2 else None
        subject3 = request.form.get('subject3') if subject_count and int(subject_count) >= 3 else None
        subject4 = request.form.get('subject4') if subject_count and int(subject_count) == 4 else None
        password = request.form.get('password')

        if not name or not surname or not password or password != 'dabirjavadol':
            flash('اطلاعات نامعتبر است.')
            return redirect(url_for('login_teacher'))

        grades = [g for g in [grade1, grade2, grade3] if g]
        fields = [f for f in [field1, field2, field3] if f]
        subjects = [s for s in [subject1, subject2, subject3, subject4] if s]

        session['user'] = {
            'name': name,
            'surname': surname,
            'rank': 'معلم',
            'grades': grades,
            'fields': fields,
            'subjects': subjects
        }
        return redirect(url_for('teacher_dashboard'))

    html = f"""
    {CSS}
    <div class="container">
        <div class="form-container">
            <h2>ورود معلمان</h2>
            <form method="post">
                <div class="form-group">
                    <label>نام</label>
                    <input type="text" name="name" required />
                </div>
                <div class="form-group">
                    <label>نام خانوادگی</label>
                    <input type="text" name="surname" required />
                </div>
                <div class="form-group">
                    <label>تعداد پایه‌ها</label>
                    <select name="grade_count" onchange="toggleFields('grade', this.value)">
                        <option value="">انتخاب کنید</option>
                        <option value="1">1</option>
                        <option value="2">2</option>
                        <option value="3">3</option>
                    </select>
                </div>
                <div class="form-group" id="grade1" style="display:none;">
                    <label>پایه 1</label>
                    <select name="grade1">
                        <option value="دهم">دهم</option>
                        <option value="یازدهم">یازدهم</option>
                        <option value="دوازدهم">دوازدهم</option>
                    </select>
                </div>
                <div class="form-group" id="grade2" style="display:none;">
                    <label>پایه 2</label>
                    <select name="grade2">
                        <option value="دهم">دهم</option>
                        <option value="یازدهم">یازدهم</option>
                        <option value="دوازدهم">دوازدهم</option>
                    </select>
                </div>
                <div class="form-group" id="grade3" style="display:none;">
                    <label>پایه 3</label>
                    <select name="grade3">
                        <option value="دهم">دهم</option>
                        <option value="یازدهم">یازدهم</option>
                        <option value="دوازدهم">دوازدهم</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>تعداد رشته‌ها</label>
                    <select name="field_count" onchange="toggleFields('field', this.value)">
                        <option value="">انتخاب کنید</option>
                        <option value="1">1</option>
                        <option value="2">2</option>
                        <option value="3">3</option>
                    </select>
                </div>
                <div class="form-group" id="field1" style="display:none;">
                    <label>رشته 1</label>
                    <select name="field1">
                        <option value="ریاضی">ریاضی</option>
                        <option value="تجربی">تجربی</option>
                        <option value="انسانی">انسانی</option>
                    </select>
                </div>
                <div class="form-group" id="field2" style="display:none;">
                    <label>رشته 2</label>
                    <select name="field2">
                        <option value="ریاضی">ریاضی</option>
                        <option value="تجربی">تجربی</option>
                        <option value="انسانی">انسانی</option>
                    </select>
                </div>
                <div class="form-group" id="field3" style="display:none;">
                    <label>رشته 3</label>
                    <select name="field3">
                        <option value="ریاضی">ریاضی</option>
                        <option value="تجربی">تجربی</option>
                        <option value="انسانی">انسانی</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>تعداد دروس</label>
                    <select name="subject_count" onchange="toggleFields('subject', this.value)">
                        <option value="">انتخاب کنید</option>
                        <option value="1">1</option>
                        <option value="2">2</option>
                        <option value="3">3</option>
                        <option value="4">4</option>
                    </select>
                </div>
                <div class="form-group" id="subject1" style="display:none;">
                    <label>درس 1</label>
                    <input type="text" name="subject1" />
                </div>
                <div class="form-group" id="subject2" style="display:none;">
                    <label>درس 2</label>
                    <input type="text" name="subject2" />
                </div>
                <div class="form-group" id="subject3" style="display:none;">
                    <label>درس 3</label>
                    <input type="text" name="subject3" />
                </div>
                <div class="form-group" id="subject4" style="display:none;">
                    <label>درس 4</label>
                    <input type="text" name="subject4" />
                </div>
                <div class="form-group">
                    <label>رمز عبور</label>
                    <input type="text" name="password" value="dabirjavadol" readonly />
                </div>
                <button type="submit" class="btn-submit">ورود</button>
                <a href="/">← بازگشت</a>
            </form>
        </div>
    </div>
    <script>
        function toggleFields(prefix, count) {{
            for (let i = 1; i <= 4; i++) {{
                let el = document.getElementById(prefix + i);
                if (el) {{
                    if (i <= count) el.style.display = 'block';
                    else el.style.display = 'none';
                }}
            }}
        }}
    </script>
    """
    return render_template_string(html)

@app.route('/teacher/dashboard')
def teacher_dashboard():
    if 'user' not in session or session['user']['rank'] != 'معلم':
        return redirect(url_for('index'))

    # Check for new notifications
    new_reports = len(reports)
    new_notifications = 0
    if new_reports > 0:
        new_notifications += 1

    html = f"""
    {CSS}
    <div class="menu-toggle" onclick="toggleSidebar()">
        <span></span>
        <span></span>
        <span></span>
    </div>
    <div class="container">
        <h1 class="header">درگاه معلمان</h1>
        <div class="dashboard-container">
            <div class="btn btn-teacher" onclick="markAsRead('/attendance'); location.href='/attendance'">حضور و غیاب</div>
            <div class="btn btn-teacher" onclick="markAsRead('/grades'); location.href='/grades'">نمرات</div>
            <div class="btn btn-teacher" onclick="markAsRead('/report'); location.href='/report'">گزارش</div>
            <div class="btn btn-teacher" onclick="markAsRead('/notes'); location.href='/notes'">جزوه ها</div>
            <div class="btn btn-teacher" onclick="markAsRead('/assignments'); location.href='/assignments'">تکالیف و امتحانات</div>
        </div>
    </div>
    <div class="sidebar" id="sidebar">
        <a href="/teacher/dashboard" class="toolbar-btn">🏠 صفحه اصلی</a>
        <a href="/teacher/profile" class="toolbar-btn">👤 پروفایل</a>
        <a href="/teacher/announcements" class="toolbar-btn">🔔 اعلانات</a>
    </div>
    <script>
        function toggleSidebar() {{
            document.getElementById('sidebar').classList.toggle('active');
        }}
        function markAsRead(url) {{
            // Remove notification dot
            let btn = document.querySelector(`[onclick*="${{url}}"]`);
            if (btn) {{
                let dot = btn.querySelector('.notification-dot');
                if (dot) dot.remove();
            }}
        }}
    </script>
    """
    return render_template_string(html)

@app.route('/teacher/profile')
def teacher_profile():
    if 'user' not in session:
        return redirect(url_for('index'))

    user = session['user']
    html = f"""
    {CSS}
    <div class="container">
        <h1 class="header">پروفایل</h1>
        <div class="form-container">
            <p><b>نام:</b> {user['name']}</p>
            <p><b>نام خانوادگی:</b> {user['surname']}</p>
            <p><b>مرتبه:</b> {user['rank']}</p>
            <p><b>پایه‌های انتخاب شده:</b> {', '.join(user['grades'])}</p>
            <p><b>رشته‌های انتخاب شده:</b> {', '.join(user['fields'])}</p>
            <p><b>درس‌های انتخاب شده:</b> {', '.join(user['subjects'])}</p>
            <p><b>رمز:</b> dabirjavadol</p>
            <button onclick="location.href='/teacher/logout'" class="btn-submit">خروج از حساب</button>
        </div>
    </div>
    """
    return render_template_string(html)

@app.route('/teacher/logout')
def teacher_logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/attendance', defaults={'grade': None, 'field': None})
@app.route('/attendance/<grade>', defaults={'field': None})
@app.route('/attendance/<grade>/<field>')
def attendance(grade, field):
    if 'user' not in session:
        return redirect(url_for('index'))

    if not grade:
        html = f"""
        {CSS}
        <div class="container">
            <h1 class="header">حضور و غیاب</h1>
            <div class="dashboard-container">
                {''.join([f'<div class="btn btn-student" onclick="location.href=\'/attendance/{g}\'">{g}</div>' for g in session['user']['grades']])}
            </div>
        </div>
        """
    elif not field:
        html = f"""
        {CSS}
        <div class="container">
            <h1 class="header">رشته {grade}</h1>
            <div class="dashboard-container">
                {''.join([f'<div class="btn btn-student" onclick="location.href=\'/attendance/{grade}/{f}\'">{f}</div>' for f in session['user']['fields']])}
            </div>
        </div>
        """
    else:
        student_list = students[field][grade]
        count = len(student_list)
        html = f"""
        {CSS}
        <div class="container">
            <h1 class="header">دانش آموزان {grade} - {field}</h1>
            <div style="display:flex; justify-content:space-between; margin-bottom:20px;">
                <span>تعداد: {count}</span>
                <div style="display:flex; align-items:center;">
                    <span style="color:#ff4444;">غائب: 0</span>
                    <span style="color:#00ff99; margin-right:20px;">حاضر: 0</span>
                </div>
            </div>
            <div id="students-list">
                {''.join([f'<div class="student-card"><div><b>{s["name"]} {s["surname"]}</b><br>{s["national_id"]}</div><div style="display:flex; gap:5px;"><button class="attendance-btn" onclick="toggleAttendance(this, \'absent\')"></button><button class="attendance-btn" onclick="toggleAttendance(this, \'present\')"></button></div></div>' for s in student_list])}
            </div>
            <div style="margin-top:30px; display:flex; gap:10px;">
                <button class="btn-submit" onclick="sendAttendance()">ارسال فرم حضور و غیاب</button>
                <button class="btn-submit" style="background:gray;" onclick="resetAttendance()">پاک کردن انتخاب شدگان</button>
            </div>
        </div>
        <script>
            function toggleAttendance(btn, type) {{
                if (type === 'absent') {{
                    btn.classList.toggle('absent');
                    if (btn.classList.contains('absent')) {{
                        document.querySelectorAll('.attendance-btn').forEach(b => {{
                            if (b !== btn && b.classList.contains('present')) b.classList.remove('present');
                        }});
                    }}
                }} else if (type === 'present') {{
                    btn.classList.toggle('present');
                    if (btn.classList.contains('present')) {{
                        document.querySelectorAll('.attendance-btn').forEach(b => {{
                            if (b !== btn && b.classList.contains('absent')) b.classList.remove('absent');
                        }});
                    }}
                }}
            }}
            function sendAttendance() {{
                alert('تاریخ را وارد کنید');
                // بعداً فرم تاریخ اضافه می‌شود
            }}
            function resetAttendance() {{
                if (confirm('آیا مطمئن هستید؟')) {{
                    document.querySelectorAll('.attendance-btn').forEach(b => b.classList.remove('absent', 'present'));
                }}
            }}
        </script>
        """
    return render_template_string(html)

@app.route('/grades', defaults={'grade': None, 'field': None})
@app.route('/grades/<grade>', defaults={'field': None})
@app.route('/grades/<grade>/<field>')
def grades_page(grade, field):
    if 'user' not in session:
        return redirect(url_for('index'))

    if not grade:
        html = f"""
        {CSS}
        <div class="container">
            <h1 class="header">نمرات</h1>
            <div class="dashboard-container">
                {''.join([f'<div class="btn btn-student" onclick="location.href=\'/grades/{g}\'">{g}</div>' for g in session['user']['grades']])}
            </div>
        </div>
        """
    elif not field:
        html = f"""
        {CSS}
        <div class="container">
            <h1 class="header">رشته {grade}</h1>
            <div class="dashboard-container">
                {''.join([f'<div class="btn btn-student" onclick="location.href=\'/grades/{grade}/{f}\'">{f}</div>' for f in session['user']['fields']])}
            </div>
        </div>
        """
    else:
        student_list = students[field][grade]
        html = f"""
        {CSS}
        <div class="container">
            <h1 class="header">نمرات دانش آموزان {grade} - {field}</h1>
            <div id="students-list">
                {''.join([f'''
                <div class="student-card">
                    <div><b>{s["name"]} {s["surname"]}</b></div>
                    <div style="display:flex; gap:5px;">
                        <input type="number" placeholder="میان ترم اول" min="0" max="20" style="width:60px;" />
                        <input type="number" placeholder="نوبت اول" min="0" max="20" style="width:60px;" disabled />
                        <input type="number" placeholder="میان ترم دوم" min="0" max="20" style="width:60px;" disabled />
                        <input type="number" placeholder="نوبت دوم" min="0" max="20" style="width:60px;" disabled />
                    </div>
                </div>
                ''' for s in student_list])}
            </div>
        </div>
        """
    return render_template_string(html)

@app.route('/report', methods=['GET', 'POST'])
def teacher_report():
    if request.method == 'POST':
        text = request.form.get('report_text')
        if not text:
            flash('متن گزارش نمی‌تواند خالی باشد.')
            return redirect(url_for('teacher_report'))

        user = session['user']
        report_entry = {
            'name': user['name'],
            'surname': user['surname'],
            'grades': ', '.join(user['grades']),
            'fields': ', '.join(user['fields']),
            'subjects': ', '.join(user['subjects']),
            'text': text
        }
        reports.append(report_entry)
        return redirect(url_for('teacher_dashboard'))

    html = f"""
    {CSS}
    <div class="container">
        <h1 class="header">ارسال گزارش</h1>
        <div class="form-container">
            <p>چه گزارشی برای مدیر می‌خواهید ارسال کنید؟</p>
            <form method="post">
                <div class="form-group">
                    <textarea name="report_text" style="width:100%; height:150px; border-radius:10px; padding:10px; background:rgba(0,0,0,0.2); color:white; border:1px solid rgba(255,255,255,0.2);"></textarea>
                </div>
                <button type="submit" class="btn-submit">ارسال</button>
                <a href="/teacher/dashboard">← بازگشت</a>
            </form>
        </div>
    </div>
    """
    return render_template_string(html)

@app.route('/notes', methods=['GET', 'POST'])
def notes_page():
    if request.method == 'POST':
        file = request.files.get('note_file')
        desc = request.form.get('desc')
        if file:
            # ذخیره فایل یا ارسال به درگاه دانش آموزان
            pass
        return redirect(url_for('teacher_dashboard'))

    html = f"""
    {CSS}
    <div class="container">
        <h1 class="header">ارسال جزوه</h1>
        <div class="form-container">
            <p>فایل مورد نظر خود را انتخاب کنید:</p>
            <form method="post" enctype="multipart/form-data">
                <div class="form-group">
                    <input type="file" name="note_file" accept=".pdf,.doc,.docx,.zip,.rar" />
                </div>
                <div class="form-group">
                    <textarea name="desc" placeholder="توضیحات (اختیاری)" style="width:100%; height:100px; border-radius:10px; padding:10px; background:rgba(0,0,0,0.2); color:white; border:1px solid rgba(255,255,255,0.2);"></textarea>
                </div>
                <button type="submit" class="btn-submit">ارسال</button>
                <a href="/teacher/dashboard">← بازگشت</a>
            </form>
        </div>
    </div>
    """
    return render_template_string(html)

@app.route('/assignments', methods=['GET', 'POST'])
def assignments_page():
    if request.method == 'POST':
        text = request.form.get('assignment_text')
        if not text:
            flash('متن تکلیف نمی‌تواند خالی باشد.')
            return redirect(url_for('assignments_page'))

        user = session['user']
        assignment_entry = {
            'name': user['name'],
            'surname': user['surname'],
            'grades': ', '.join(user['grades']),
            'fields': ', '.join(user['fields']),
            'subjects': ', '.join(user['subjects']),
            'text': text
        }
        assignments.append(assignment_entry)
        return redirect(url_for('teacher_dashboard'))

    html = f"""
    {CSS}
    <div class="container">
        <h1 class="header">ارسال تکالیف و امتحانات</h1>
        <div class="form-container">
            <p>تکالیف و امتحان مورد نظر خود را بنویسید:</p>
            <form method="post">
                <div class="form-group">
                    <textarea name="assignment_text" style="width:100%; height:150px; border-radius:10px; padding:10px; background:rgba(0,0,0,0.2); color:white; border:1px solid rgba(255,255,255,0.2);"></textarea>
                </div>
                <button type="submit" class="btn-submit">ارسال</button>
                <a href="/teacher/dashboard">← بازگشت</a>
            </form>
        </div>
    </div>
    """
    return render_template_string(html)

@app.route('/teacher/announcements')
def teacher_announcements():
    html = f"""
    {CSS}
    <div class="container">
        <h1 class="header">اعلانات</h1>
        <div class="form-container">
            <p>هیچ اعلانی وجود ندارد.</p>
        </div>
    </div>
    """
    return render_template_string(html)

@app.route('/login/parent', methods=['GET', 'POST'])
def login_parent():
    if request.method == 'POST':
        name = request.form.get('name')
        surname = request.form.get('surname')
        grade = request.form.get('grade')
        field = request.form.get('field')
        child1 = request.form.get('child1')
        child2 = request.form.get('child2')

        if not name or not surname or not grade or not field or not child1:
            flash('اطلاعات نامعتبر است.')
            return redirect(url_for('login_parent'))

        session['user'] = {
            'name': name,
            'surname': surname,
            'rank': 'والدین',
            'grade': grade,
            'field': field,
            'child1': child1,
            'child2': child2
        }
        return redirect(url_for('parent_dashboard'))

    html = f"""
    {CSS}
    <div class="container">
        <div class="form-container">
            <h2>ورود والدین</h2>
            <form method="post">
                <div class="form-group">
                    <label>نام</label>
                    <input type="text" name="name" required />
                </div>
                <div class="form-group">
                    <label>نام خانوادگی</label>
                    <input type="text" name="surname" required />
                </div>
                <div class="form-group">
                    <label>انتخاب پایه فرزند</label>
                    <select name="grade" onchange="toggleFields('field', this.value)" required>
                        <option value="">انتخاب کنید</option>
                        <option value="دهم">دهم</option>
                        <option value="یازدهم">یازدهم</option>
                        <option value="دوازدهم">دوازدهم</option>
                    </select>
                </div>
                <div class="form-group" id="field-section" style="display:none;">
                    <label>انتخاب رشته فرزند</label>
                    <select name="field" onchange="toggleFields('child1', this.value)" required>
                        <option value="">انتخاب کنید</option>
                        <option value="ریاضی">ریاضی</option>
                        <option value="تجربی">تجربی</option>
                        <option value="انسانی">انسانی</option>
                    </select>
                </div>
                <div class="form-group" id="child1-section" style="display:none;">
                    <label>فرزند خود را انتخاب کنید</label>
                    <select name="child1" required>
                        <option value="">انتخاب کنید</option>
                        {''.join([f'<option value="{s["name"]} {s["surname"]}">{s["name"]} {s["surname"]} - {s["national_id"][-4:]}</option>' for s in students[request.form.get("field", "")][request.form.get("grade", "")]])}
                    </select>
                </div>
                <div class="form-group" id="child2-section" style="display:none;">
                    <label>فرزند دوم خود را انتخاب کنید (اختیاری)</label>
                    <select name="child2">
                        <option value="">انتخاب کنید</option>
                        {''.join([f'<option value="{s["name"]} {s["surname"]}">{s["name"]} {s["surname"]} - {s["national_id"][-4:]}</option>' for s in students[request.form.get("field", "")][request.form.get("grade", "")]])}
                    </select>
                </div>
                <button type="submit" class="btn-submit">ورود</button>
                <a href="/">← بازگشت</a>
            </form>
        </div>
    </div>
    <script>
        function toggleFields(prefix, value) {{
            if (prefix === 'field') {{
                document.getElementById('field-section').style.display = value ? 'block' : 'none';
            }} else if (prefix === 'child1') {{
                document.getElementById('child1-section').style.display = value ? 'block' : 'none';
                document.getElementById('child2-section').style.display = value ? 'block' : 'none';
            }}
        }}
    </script>
    """
    return render_template_string(html)

@app.route('/parent/dashboard')
def parent_dashboard():
    if 'user' not in session or session['user']['rank'] != 'والدین':
        return redirect(url_for('index'))

    # Check for new notifications
    new_reports = len(reports)
    new_notifications = 0
    if new_reports > 0:
        new_notifications += 1

    html = f"""
    {CSS}
    <div class="menu-toggle" onclick="toggleSidebar()">
        <span></span>
        <span></span>
        <span></span>
    </div>
    <div class="container">
        <h1 class="header">درگاه والدین</h1>
        <div class="dashboard-container">
            <div class="btn btn-parent" onclick="markAsRead('/attendance'); location.href='/attendance'">حضور فرزندم در دبیرستان</div>
            <div class="btn btn-parent" onclick="markAsRead('/grades'); location.href='/grades'">نمرات فرزندم</div>
            <div class="btn btn-parent" onclick="markAsRead('/assignments'); location.href='/assignments'">تکالیف و امتحان فرزندم</div>
            <div class="btn btn-parent" onclick="markAsRead('/reportcard'); location.href='/reportcard'">کارنامه فرزندم</div>
            <div class="btn btn-parent" onclick="markAsRead('/report'); location.href='/report'">گزارش</div>
            <div class="btn btn-parent" onclick="markAsRead('/admins'); location.href='/admins'">لیست مدیران</div>
            <div class="btn btn-parent" onclick="markAsRead('/teachers'); location.href='/teachers'">لیست معلمان</div>
            <div class="btn btn-parent" onclick="markAsRead('/lab'); location.href='/lab'">آزمایشگاه علوم</div>
        </div>
    </div>
    <div class="sidebar" id="sidebar">
        <a href="/parent/dashboard" class="toolbar-btn">🏠 صفحه اصلی</a>
        <a href="/parent/profile" class="toolbar-btn">👤 پروفایل</a>
        <a href="/parent/announcements" class="toolbar-btn">🔔 اعلانات</a>
    </div>
    <script>
        function toggleSidebar() {{
            document.getElementById('sidebar').classList.toggle('active');
        }}
        function markAsRead(url) {{
            // Remove notification dot
            let btn = document.querySelector(`[onclick*="${{url}}"]`);
            if (btn) {{
                let dot = btn.querySelector('.notification-dot');
                if (dot) dot.remove();
            }}
        }}
    </script>
    """
    return render_template_string(html)

@app.route('/parent/profile')
def parent_profile():
    if 'user' not in session:
        return redirect(url_for('index'))

    user = session['user']
    html = f"""
    {CSS}
    <div class="container">
        <h1 class="header">پروفایل</h1>
        <div class="form-container">
            <p><b>نام:</b> {user['name']}</p>
            <p><b>نام خانوادگی:</b> {user['surname']}</p>
            <p><b>مرتبه:</b> {user['rank']}</p>
            <p><b>پایه فرزند:</b> {user['grade']}</p>
            <p><b>رشته فرزند:</b> {user['field']}</p>
            <p><b>فرزند اول:</b> {user['child1']}</p>
            <p><b>فرزند دوم:</b> {user['child2'] or 'ندارد'}</p>
            <button onclick="location.href='/parent/logout'" class="btn-submit">خروج از حساب</button>
        </div>
    </div>
    """
    return render_template_string(html)

@app.route('/parent/logout')
def parent_logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/report', methods=['GET', 'POST'])
def parent_report():
    if request.method == 'POST':
        text = request.form.get('report_text')
        if not text:
            flash('متن گزارش نمی‌تواند خالی باشد.')
            return redirect(url_for('parent_report'))

        user = session['user']
        report_entry = {
            'name': user['name'],
            'surname': user['surname'],
            'grade': user['grade'],
            'field': user['field'],
            'child1': user['child1'],
            'text': text
        }
        reports.append(report_entry)
        return redirect(url_for('parent_dashboard'))

    html = f"""
    {CSS}
    <div class="container">
        <h1 class="header">ارسال گزارش</h1>
        <div class="form-container">
            <p>چه گزارشی برای مدیر می‌خواهید ارسال کنید؟</p>
            <form method="post">
                <div class="form-group">
                    <textarea name="report_text" style="width:100%; height:150px; border-radius:10px; padding:10px; background:rgba(0,0,0,0.2); color:white; border:1px solid rgba(255,255,255,0.2);"></textarea>
                </div>
                <button type="submit" class="btn-submit">ارسال</button>
                <a href="/parent/dashboard">← بازگشت</a>
            </form>
        </div>
    </div>
    """
    return render_template_string(html)

@app.route('/admins')
def admins_list():
    html = f"""
    {CSS}
    <div class="container">
        <h1 class="header">لیست مدیران</h1>
        <div id="admins-list">
            {''.join([f'<div class="student-card"><b>{a["name"]} {a["surname"]}</b> - {a["rank"]}</div>' for a in admin_list])}
        </div>
    </div>
    """
    return render_template_string(html)

@app.route('/teachers')
def teachers_list():
    html = f"""
    {CSS}
    <div class="container">
        <h1 class="header">لیست معلمان</h1>
        <div id="teachers-list">
            {''.join([f'<div class="student-card"><b>{t["name"]} {t["surname"]}</b> - {", ".join(t["grades"])} - {", ".join(t["fields"])} - {", ".join(t["subjects"])}</div>' for t in teacher_list])}
        </div>
    </div>
    """
    return render_template_string(html)

@app.route('/lab')
def lab_experiments_page():
    html = f"""
    {CSS}
    <div class="container">
        <h1 class="header">آزمایشگاه علوم</h1>
        <div id="lab-list">
            {''.join([f'<div class="student-card"><img src="{img}" style="width:100px; height:100px; object-fit:cover; border-radius:10px;" /> - {exp["desc"]}</div>' for exp in lab_experiments for img in exp["images"]])}
        </div>
    </div>
    """
    return render_template_string(html)

@app.route('/parent/announcements')
def parent_announcements():
    html = f"""
    {CSS}
    <div class="container">
        <h1 class="header">اعلانات</h1>
        <div class="form-container">
            <p>هیچ اعلانی وجود ندارد.</p>
        </div>
    </div>
    """
    return render_template_string(html)

@app.route('/login/student', methods=['GET', 'POST'])
def login_student():
    if request.method == 'POST':
        grade = request.form.get('grade')
        field = request.form.get('field')
        student_name = request.form.get('student_name')
        national_id = request.form.get('national_id')
        password = request.form.get('password')

        if not grade or not field or not student_name or not national_id or not password:
            flash('اطلاعات نامعتبر است.')
            return redirect(url_for('login_student'))

        if len(national_id) != 10 or not national_id.isdigit():
            flash('کد ملی باید 10 رقم باشد.')
            return redirect(url_for('login_student'))

        session['user'] = {
            'name': student_name.split()[0],
            'surname': ' '.join(student_name.split()[1:]),
            'rank': 'دانش آموز',
            'grade': grade,
            'field': field,
            'national_id': national_id,
            'password': password
        }
        return redirect(url_for('student_dashboard'))

    html = f"""
    {CSS}
    <div class="container">
        <div class="form-container">
            <h2>ورود دانش آموزان</h2>
            <form method="post">
                <div class="form-group">
                    <label>پایه</label>
                    <select name="grade" onchange="toggleFields('field', this.value)" required>
                        <option value="">انتخاب کنید</option>
                        <option value="دهم">دهم</option>
                        <option value="یازدهم">یازدهم</option>
                        <option value="دوازدهم">دوازدهم</option>
                    </select>
                </div>
                <div class="form-group" id="field-section" style="display:none;">
                    <label>رشته</label>
                    <select name="field" onchange="toggleFields('student_name', this.value)" required>
                        <option value="">انتخاب کنید</option>
                        <option value="ریاضی">ریاضی</option>
                        <option value="تجربی">تجربی</option>
                        <option value="انسانی">انسانی</option>
                    </select>
                </div>
                <div class="form-group" id="student-name-section" style="display:none;">
                    <label>نام و نام خانوادگی</label>
                    <select name="student_name" required>
                        <option value="">انتخاب کنید</option>
                        {''.join([f'<option value="{s["name"]} {s["surname"]}">{s["name"]} {s["surname"]} - {s["national_id"][-4:]}</option>' for s in students[request.form.get("field", "")][request.form.get("grade", "")]])}
                    </select>
                </div>
                <div class="form-group" id="national-id-section" style="display:none;">
                    <label>کد ملی</label>
                    <input type="text" name="national_id" placeholder="10 رقم" />
                </div>
                <div class="form-group" id="password-section" style="display:none;">
                    <label>رمز عبور</label>
                    <input type="text" name="password" placeholder="حداقل 6 کاراکتر" />
                </div>
                <button type="submit" class="btn-submit">ورود</button>
                <a href="/">← بازگشت</a>
            </form>
        </div>
    </div>
    <script>
        function toggleFields(prefix, value) {{
            if (prefix === 'field') {{
                document.getElementById('field-section').style.display = value ? 'block' : 'none';
            }} else if (prefix === 'student_name') {{
                document.getElementById('student-name-section').style.display = value ? 'block' : 'none';
                document.getElementById('national-id-section').style.display = value ? 'block' : 'none';
                document.getElementById('password-section').style.display = value ? 'block' : 'none';
            }}
        }}
    </script>
    """
    return render_template_string(html)

@app.route('/student/dashboard')
def student_dashboard():
    if 'user' not in session or session['user']['rank'] != 'دانش آموز':
        return redirect(url_for('index'))

    # Check for new notifications
    new_reports = len(reports)
    new_notifications = 0
    if new_reports > 0:
        new_notifications += 1

    html = f"""
    {CSS}
    <div class="menu-toggle" onclick="toggleSidebar()">
        <span></span>
        <span></span>
        <span></span>
    </div>
    <div class="container">
        <h1 class="header">درگاه دانش آموزان</h1>
        <div class="dashboard-container">
            <div class="btn btn-student" onclick="markAsRead('/attendance'); location.href='/attendance'">حضورم در دبیرستان</div>
            <div class="btn btn-student" onclick="markAsRead('/grades'); location.href='/grades'">نمرات درسم</div>
            <div class="btn btn-student" onclick="markAsRead('/assignments'); location.href='/assignments'">تکالیف و امتحانات روزم</div>
            <div class="btn btn-student" onclick="markAsRead('/reportcard'); location.href='/reportcard'">کارنامه من</div>
            <div class="btn btn-student" onclick="markAsRead('/report'); location.href='/report'">گزارش</div>
        </div>
    </div>
    <div class="sidebar" id="sidebar">
        <a href="/student/dashboard" class="toolbar-btn">🏠 صفحه اصلی</a>
        <a href="/student/profile" class="toolbar-btn">👤 پروفایل</a>
        <a href="/student/announcements" class="toolbar-btn">🔔 اعلانات</a>
    </div>
    <script>
        function toggleSidebar() {{
            document.getElementById('sidebar').classList.toggle('active');
        }}
        function markAsRead(url) {{
            // Remove notification dot
            let btn = document.querySelector(`[onclick*="${{url}}"]`);
            if (btn) {{
                let dot = btn.querySelector('.notification-dot');
                if (dot) dot.remove();
            }}
        }}
    </script>
    """
    return render_template_string(html)

@app.route('/student/profile')
def student_profile():
    if 'user' not in session:
        return redirect(url_for('index'))

    user = session['user']
    html = f"""
    {CSS}
    <div class="container">
        <h1 class="header">پروفایل</h1>
        <div class="form-container">
            <p><b>نام:</b> {user['name']}</p>
            <p><b>نام خانوادگی:</b> {user['surname']}</p>
            <p><b>مرتبه:</b> {user['rank']}</p>
            <p><b>پایه:</b> {user['grade']}</p>
            <p><b>رشته:</b> {user['field']}</p>
            <p><b>کد ملی:</b> {user['national_id']}</p>
            <p><b>رمز:</b> {user['password']}</p>
            <button onclick="location.href='/student/logout'" class="btn-submit">خروج از حساب</button>
        </div>
    </div>
    """
    return render_template_string(html)

@app.route('/student/logout')
def student_logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/student/announcements')
def student_announcements():
    html = f"""
    {CSS}
    <div class="container">
        <h1 class="header">اعلانات</h1>
        <div class="form-container">
            <p>هیچ اعلانی وجود ندارد.</p>
        </div>
    </div>
    """
    return render_template_string(html)

if __name__ == '__main__':
    app.run(debug=True)