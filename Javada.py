from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# داده‌های موقت برای ذخیره اطلاعات
admins = []
teachers = []
parents = []
students = []
reports = {
    'admin': [],
    'teacher': [],
    'student': []
}
grades = {
    '10': {'math': [], 'science': [], 'humanities': []},
    '11': {'math': [], 'science': [], 'humanities': []},
    '12': {'math': [], 'science': [], 'humanities': []}
}
laboratory = []
attendance_records = []
announcements = []
exams = []
homeworks = []

# صفحه اصلی
@app.route('/')
def index():
    return render_template('index.html')

# ورود مدیران
@app.route('/login_admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        name = request.form['name']
        lastname = request.form['lastname']
        position = request.form['position']
        password = request.form['password']
        
        if password == 'dabirestan012345':
            admin_data = {
                'name': name,
                'lastname': lastname,
                'position': position,
                'password': password
            }
            admins.append(admin_data)
            session['admin'] = admin_data
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('login_admin.html', error='رمز اشتباه است')
    
    return render_template('login_admin.html')

# صفحه داشبورد مدیران
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('login_admin'))
    return render_template('admin_dashboard.html', admin=session['admin'])

# مدیریت دانش‌آموزان
@app.route('/manage_students')
def manage_students():
    if 'admin' not in session:
        return redirect(url_for('login_admin'))
    return render_template('manage_students.html', grades=grades)

# مشاهده دانش‌آموزان یک رشته
@app.route('/view_students/<grade>/<field>')
def view_students(grade, field):
    if 'admin' not in session:
        return redirect(url_for('login_admin'))
    students_list = grades[grade][field]
    return render_template('view_students.html', students=students_list, grade=grade, field=field)

# افزودن دانش‌آموز
@app.route('/add_student/<grade>/<field>', methods=['GET', 'POST'])
def add_student(grade, field):
    if 'admin' not in session:
        return redirect(url_for('login_admin'))
    
    if request.method == 'POST':
        name = request.form['name']
        lastname = request.form['lastname']
        national_id = request.form['national_id']
        student_number = request.form.get('student_number', '')
        father_number = request.form.get('father_number', '')
        mother_number = request.form.get('mother_number', '')
        
        # بررسی تکراری نبودن کد ملی
        for student_list in grades.values():
            for field_list in student_list.values():
                for student in field_list:
                    if student['national_id'] == national_id:
                        return render_template('add_student.html', grade=grade, field=field, 
                                               error='این دانش‌آموز با این کد ملی وجود دارد')
        
        student_data = {
            'name': name,
            'lastname': lastname,
            'national_id': national_id,
            'student_number': student_number,
            'father_number': father_number,
            'mother_number': mother_number
        }
        grades[grade][field].append(student_data)
        return redirect(url_for('view_students', grade=grade, field=field))
    
    return render_template('add_student.html', grade=grade, field=field)

# ویرایش دانش‌آموز
@app.route('/edit_student/<grade>/<field>/<int:index>', methods=['GET', 'POST'])
def edit_student(grade, field, index):
    if 'admin' not in session:
        return redirect(url_for('login_admin'))
    
    student = grades[grade][field][index]
    
    if request.method == 'POST':
        student['name'] = request.form['name']
        student['lastname'] = request.form['lastname']
        student['national_id'] = request.form['national_id']
        student['student_number'] = request.form.get('student_number', '')
        student['father_number'] = request.form.get('father_number', '')
        student['mother_number'] = request.form.get('mother_number', '')
        return redirect(url_for('view_students', grade=grade, field=field))
    
    return render_template('edit_student.html', student=student, grade=grade, field=field)

# حذف دانش‌آموز
@app.route('/delete_student/<grade>/<field>/<int:index>')
def delete_student(grade, field, index):
    if 'admin' not in session:
        return redirect(url_for('login_admin'))
    
    del grades[grade][field][index]
    return redirect(url_for('view_students', grade=grade, field=field))

# جستجوی دانش‌آموزان
@app.route('/search_students/<grade>/<field>', methods=['GET', 'POST'])
def search_students(grade, field):
    if 'admin' not in session:
        return redirect(url_for('login_admin'))
    
    results = []
    if request.method == 'POST':
        query = request.form['query']
        for student in grades[grade][field]:
            if (query.lower() in student['name'].lower() or 
                query.lower() in student['lastname'].lower() or 
                query in student['national_id']):
                results.append(student)
    
    return render_template('search_results.html', results=results, grade=grade, field=field)

# مشاهده جزئیات دانش‌آموز
@app.route('/view_student_details/<grade>/<field>/<int:index>')
def view_student_details(grade, field, index):
    if 'admin' not in session:
        return redirect(url_for('login_admin'))
    
    student = grades[grade][field][index]
    return render_template('student_details.html', student=student, grade=grade, field=field)

# مدیریت گزارشات
@app.route('/manage_reports/<report_type>')
def manage_reports(report_type):
    if 'admin' not in session:
        return redirect(url_for('login_admin'))
    return render_template('manage_reports.html', reports=reports[report_type], report_type=report_type)

# مدیریت آزمایشگاه
@app.route('/manage_lab', methods=['GET', 'POST'])
def manage_lab():
    if 'admin' not in session:
        return redirect(url_for('login_admin'))
    
    if request.method == 'POST':
        # افزودن یا ویرایش آزمایشگاه
        images = request.form.getlist('images[]')
        description = request.form.get('description', '')
        laboratory.append({'images': images, 'description': description})
        return redirect(url_for('manage_lab'))
    
    return render_template('manage_lab.html', laboratory=laboratory)

# مدیریت نمرات
@app.route('/manage_grades')
def manage_grades():
    if 'admin' not in session:
        return redirect(url_for('login_admin'))
    return render_template('manage_grades.html', grades=grades)

# مدیریت کارنامه
@app.route('/manage_report_card', methods=['GET', 'POST'])
def manage_report_card():
    if 'admin' not in session:
        return redirect(url_for('login_admin'))
    
    if request.method == 'POST':
        # انتخاب کارنامه و دانش‌آموز
        grade = request.form['grade']
        field = request.form['field']
        student_name = request.form['student']
        # در اینجا کارنامه را به دانش‌آموز و والد ارسال می‌کنیم
        # عملیات ارسال کارنامه
        return redirect(url_for('manage_report_card'))
    
    return render_template('manage_report_card.html', grades=grades)

# پروفایل مدیر
@app.route('/admin_profile', methods=['GET', 'POST'])
def admin_profile():
    if 'admin' not in session:
        return redirect(url_for('login_admin'))
    
    admin = session['admin']
    
    if request.method == 'POST':
        admin['name'] = request.form['name']
        admin['lastname'] = request.form['lastname']
        admin['position'] = request.form['position']
        return redirect(url_for('admin_profile'))
    
    return render_template('admin_profile.html', admin=admin)

# خروج از حساب مدیر
@app.route('/admin_logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

# ورود معلمان
@app.route('/login_teacher', methods=['GET', 'POST'])
def login_teacher():
    if request.method == 'POST':
        name = request.form['name']
        lastname = request.form['lastname']
        grade_count = int(request.form['grade_count'])
        subject_count = int(request.form['subject_count'])
        password = request.form['password']
        
        if password == 'dabirjavadol':
            teacher_data = {
                'name': name,
                'lastname': lastname,
                'grade_count': grade_count,
                'subject_count': subject_count,
                'password': password
            }
            teachers.append(teacher_data)
            session['teacher'] = teacher_data
            return redirect(url_for('teacher_dashboard'))
        else:
            return render_template('login_teacher.html', error='رمز اشتباه است')
    
    return render_template('login_teacher.html')

# صفحه داشبورد معلمان
@app.route('/teacher_dashboard')
def teacher_dashboard():
    if 'teacher' not in session:
        return redirect(url_for('login_teacher'))
    return render_template('teacher_dashboard.html', teacher=session['teacher'])

# حضور و غیاب
@app.route('/attendance/<grade>/<field>')
def attendance(grade, field):
    if 'teacher' not in session:
        return redirect(url_for('login_teacher'))
    
    students_list = grades[grade][field]
    attendance_status = {}
    for i, student in enumerate(students_list):
        attendance_status[i] = {'present': False, 'absent': False}
    
    return render_template('attendance.html', 
                           students=students_list, 
                           grade=grade, 
                           field=field, 
                           attendance_status=attendance_status)

# ثبت حضور و غیاب
@app.route('/submit_attendance/<grade>/<field>', methods=['POST'])
def submit_attendance(grade, field):
    if 'teacher' not in session:
        return redirect(url_for('login_teacher'))
    
    attendance_data = {}
    for key, value in request.form.items():
        if key.startswith('student_'):
            index = int(key.split('_')[1])
            attendance_data[index] = value
    
    # ذخیره اطلاعات حضور و غیاب
    attendance_record = {
        'grade': grade,
        'field': field,
        'teacher': session['teacher'],
        'attendance': attendance_data
    }
    attendance_records.append(attendance_record)
    
    # ارسال اعلان به مدیر
    announcement = f"معلم: {session['teacher']['name']} {session['teacher']['lastname']}, "
    announcement += f"پایه: {grade}, رشته: {field}, "
    announcement += "ثبت حضور و غیاب انجام شد"
    announcements.append(announcement)
    
    return redirect(url_for('teacher_dashboard'))

# نمرات
@app.route('/grades/<grade>/<field>')
def teacher_grades(grade, field):
    if 'teacher' not in session:
        return redirect(url_for('login_teacher'))
    
    students_list = grades[grade][field]
    return render_template('teacher_grades.html', 
                           students=students_list, 
                           grade=grade, 
                           field=field)

# ثبت نمره
@app.route('/submit_grade/<grade>/<field>/<int:student_index>', methods=['POST'])
def submit_grade(grade, field, student_index):
    if 'teacher' not in session:
        return redirect(url_for('login_teacher'))
    
    student = grades[grade][field][student_index]
    
    # دریافت نمرات
    midterm1 = request.form.get('midterm1', '')
    exam1 = request.form.get('exam1', '')
    midterm2 = request.form.get('midterm2', '')
    exam2 = request.form.get('exam2', '')
    
    # ذخیره نمرات در داده‌های دانش‌آموز
    if 'grades' not in student:
        student['grades'] = {}
    
    student['grades'] = {
        'midterm1': midterm1,
        'exam1': exam1,
        'midterm2': midterm2,
        'exam2': exam2
    }
    
    # ارسال اعلان به دانش‌آموز و والدین
    announcement = f"نمره توسط معلم {session['teacher']['name']} {session['teacher']['lastname']} ثبت شد"
    announcements.append(announcement)
    
    return redirect(url_for('teacher_grades', grade=grade, field=field))

# گزارش
@app.route('/teacher_report', methods=['GET', 'POST'])
def teacher_report():
    if 'teacher' not in session:
        return redirect(url_for('login_teacher'))
    
    if request.method == 'POST':
        report_text = request.form['report']
        report_data = {
            'teacher': session['teacher'],
            'report': report_text
        }
        reports['teacher'].append(report_data)
        return redirect(url_for('teacher_dashboard'))
    
    return render_template('teacher_report.html')

# جزوه‌ها
@app.route('/notes', methods=['GET', 'POST'])
def notes():
    if 'teacher' not in session:
        return redirect(url_for('login_teacher'))
    
    if request.method == 'POST':
        # دریافت فایل‌ها و توضیحات
        files = request.files.getlist('files')
        description = request.form.get('description', '')
        
        # ذخیره فایل‌ها و توضیحات
        # عملیات ذخیره فایل‌ها
        
        return redirect(url_for('teacher_dashboard'))
    
    return render_template('notes.html')

# تکالیف و امتحانات
@app.route('/exams', methods=['GET', 'POST'])
def exams():
    if 'teacher' not in session:
        return redirect(url_for('login_teacher'))
    
    if request.method == 'POST':
        exam_text = request.form['exam']
        exam_data = {
            'teacher': session['teacher'],
            'exam': exam_text
        }
        exams.append(exam_data)
        return redirect(url_for('teacher_dashboard'))
    
    return render_template('exams.html')

# پروفایل معلم
@app.route('/teacher_profile', methods=['GET', 'POST'])
def teacher_profile():
    if 'teacher' not in session:
        return redirect(url_for('login_teacher'))
    
    teacher = session['teacher']
    
    if request.method == 'POST':
        teacher['name'] = request.form['name']
        teacher['lastname'] = request.form['lastname']
        return redirect(url_for('teacher_profile'))
    
    return render_template('teacher_profile.html', teacher=teacher)

# خروج از حساب معلم
@app.route('/teacher_logout')
def teacher_logout():
    session.pop('teacher', None)
    return redirect(url_for('index'))

# ورود والدین
@app.route('/login_parent', methods=['GET', 'POST'])
def login_parent():
    if request.method == 'POST':
        name = request.form['name']
        lastname = request.form['lastname']
        child_grade = request.form['child_grade']
        child_field = request.form['child_field']
        child_name = request.form['child_name']
        child2_name = request.form.get('child2_name', '')
        
        parent_data = {
            'name': name,
            'lastname': lastname,
            'child_grade': child_grade,
            'child_field': child_field,
            'child_name': child_name,
            'child2_name': child2_name
        }
        parents.append(parent_data)
        session['parent'] = parent_data
        return redirect(url_for('parent_dashboard'))
    
    return render_template('login_parent.html', grades=grades)

# صفحه داشبورد والدین
@app.route('/parent_dashboard')
def parent_dashboard():
    if 'parent' not in session:
        return redirect(url_for('login_parent'))
    return render_template('parent_dashboard.html', parent=session['parent'])

# گزارش والدین
@app.route('/parent_report', methods=['GET', 'POST'])
def parent_report():
    if 'parent' not in session:
        return redirect(url_for('login_parent'))
    
    if request.method == 'POST':
        report_text = request.form['report']
        report_data = {
            'parent': session['parent'],
            'report': report_text
        }
        reports['admin'].append(report_data)
        return redirect(url_for('parent_dashboard'))
    
    return render_template('parent_report.html')

# لیست مدیران
@app.route('/admin_list')
def admin_list():
    if 'parent' not in session:
        return redirect(url_for('login_parent'))
    return render_template('admin_list.html', admins=admins)

# لیست معلمان
@app.route('/teacher_list')
def teacher_list():
    if 'parent' not in session:
        return redirect(url_for('login_parent'))
    return render_template('teacher_list.html', teachers=teachers)

# آزمایشگاه علوم
@app.route('/science_lab')
def science_lab():
    if 'parent' not in session:
        return redirect(url_for('login_parent'))
    return render_template('science_lab.html', laboratory=laboratory)

# پروفایل والدین
@app.route('/parent_profile', methods=['GET', 'POST'])
def parent_profile():
    if 'parent' not in session:
        return redirect(url_for('login_parent'))
    
    parent = session['parent']
    
    if request.method == 'POST':
        parent['name'] = request.form['name']
        parent['lastname'] = request.form['lastname']
        return redirect(url_for('parent_profile'))
    
    return render_template('parent_profile.html', parent=parent)

# خروج از حساب والدین
@app.route('/parent_logout')
def parent_logout():
    session.pop('parent', None)
    return redirect(url_for('index'))

# ورود دانش‌آموزان
@app.route('/login_student', methods=['GET', 'POST'])
def login_student():
    if request.method == 'POST':
        grade = request.form['grade']
        field = request.form['field']
        full_name = request.form['full_name']
        national_id = request.form['national_id']
        password = request.form['password']
        
        # بررسی وجود دانش‌آموز
        student_found = False
        for student in grades[grade][field]:
            if (student['name'] + ' ' + student['lastname'] == full_name and 
                student['national_id'] == national_id):
                student_found = True
                break
        
        if student_found:
            student_data = {
                'name': full_name.split()[0],
                'lastname': ' '.join(full_name.split()[1:]),
                'grade': grade,
                'field': field,
                'national_id': national_id,
                'password': password
            }
            students.append(student_data)
            session['student'] = student_data
            return redirect(url_for('student_dashboard'))
        else:
            return render_template('login_student.html', error='اطلاعات نادرست است')
    
    return render_template('login_student.html', grades=grades)

# صفحه داشبورد دانش‌آموزان
@app.route('/student_dashboard')
def student_dashboard():
    if 'student' not in session:
        return redirect(url_for('login_student'))
    return render_template('student_dashboard.html', student=session['student'])

# گزارش دانش‌آموزان
@app.route('/student_report', methods=['GET', 'POST'])
def student_report():
    if 'student' not in session:
        return redirect(url_for('login_student'))
    
    if request.method == 'POST':
        report_text = request.form['report']
        report_data = {
            'student': session['student'],
            'report': report_text
        }
        reports['student'].append(report_data)
        return redirect(url_for('student_dashboard'))
    
    return render_template('student_report.html')

# پروفایل دانش‌آموز
@app.route('/student_profile', methods=['GET', 'POST'])
def student_profile():
    if 'student' not in session:
        return redirect(url_for('login_student'))
    
    student = session['student']
    
    if request.method == 'POST':
        student['name'] = request.form['name']
        student['lastname'] = request.form['lastname']
        student['grade'] = request.form['grade']
        student['field'] = request.form['field']
        student['national_id'] = request.form['national_id']
        student['password'] = request.form['password']
        return redirect(url_for('student_profile'))
    
    return render_template('student_profile.html', student=student)

# خروج از حساب دانش‌آموز
@app.route('/student_logout')
def student_logout():
    session.pop('student', None)
    return redirect(url_for('index'))

# تمپلیت‌ها
templates = {
    'index.html': '''<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>دبیرستان پسرانه جوادالائمه</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            direction: rtl;
            font-family: 'Vazir', Tahoma, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            color: white;
        }
        
        .header {
            text-align: center;
            padding: 20px;
            background: rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(10px);
            border-radius: 0 0 20px 20px;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 1.8rem;
            background: linear-gradient(to right, #ff00cc, #00eeff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 10px rgba(255, 0, 204, 0.5);
        }
        
        .buttons-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 20px;
            flex: 1;
        }
        
        .btn {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.2);
            position: relative;
            overflow: hidden;
        }
        
        .btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(45deg, #ff00cc, #00eeff, #ffcc00, #00ff99);
            opacity: 0;
            transition: opacity 0.3s ease;
            z-index: 1;
        }
        
        .btn:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
            z-index: 2;
        }
        
        .btn:hover::before {
            opacity: 0.2;
        }
        
        .btn:active {
            transform: scale(0.98);
        }
        
        .btn h3 {
            margin-bottom: 10px;
            font-size: 1.3rem;
        }
        
        .btn p {
            font-size: 0.9rem;
            color: #ccc;
        }
        
        .admin-btn { background: linear-gradient(45deg, #ff00cc, #ff0066); }
        .teacher-btn { background: linear-gradient(45deg, #00eeff, #0066ff); }
        .parent-btn { background: linear-gradient(45deg, #ffcc00, #ff6600); }
        .student-btn { background: linear-gradient(45deg, #00ff99, #00cc66); }
        
        .footer {
            text-align: center;
            padding: 20px;
            background: rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(10px);
            border-radius: 20px 20px 0 0;
            margin-top: 30px;
        }
        
        .menu-toggle {
            position: fixed;
            top: 20px;
            right: 20px;
            width: 50px;
            height: 50px;
            display: flex;
            flex-direction: column;
            justify-content: space-around;
            z-index: 1000;
        }
        
        .menu-toggle span {
            width: 100%;
            height: 4px;
            background: white;
            border-radius: 2px;
            transition: all 0.3s ease;
        }
        
        .menu-sidebar {
            position: fixed;
            top: 0;
            right: 0;
            width: 300px;
            height: 100vh;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(10px);
            transform: translateX(100%);
            transition: transform 0.3s ease;
            z-index: 999;
            padding: 20px;
        }
        
        .menu-sidebar.active {
            transform: translateX(0);
        }
        
        .menu-sidebar ul {
            list-style: none;
            padding: 20px 0;
        }
        
        .menu-sidebar li {
            padding: 15px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .menu-sidebar a {
            color: white;
            text-decoration: none;
            display: block;
            padding: 10px;
            border-radius: 10px;
            transition: background 0.3s ease;
        }
        
        .menu-sidebar a:hover {
            background: rgba(255, 255, 255, 0.1);
        }
    </style>
</head>
<body>
    <div class="menu-toggle" id="menuToggle">
        <span></span>
        <span></span>
        <span></span>
    </div>
    
    <div class="menu-sidebar" id="menuSidebar">
        <ul>
            <li><a href="/">صفحه اصلی</a></li>
            <li><a href="/admin_dashboard">پروفایل</a></li>
            <li><a href="#">اعلانات</a></li>
        </ul>
    </div>

    <div class="header">
        <h1>به سایت رسمی دبیرستان پسرانه جوادالائمه خوش آمدید</h1>
    </div>
    
    <div class="buttons-container">
        <div class="btn admin-btn" onclick="location.href='/login_admin'">
            <h3>ورود مدیران</h3>
            <p>این بخش فقط برای مدیران است</p>
        </div>
        
        <div class="btn teacher-btn" onclick="location.href='/login_teacher'">
            <h3>ورود معلمان</h3>
            <p>این بخش فقط برای معلمان است</p>
        </div>
        
        <div class="btn parent-btn" onclick="location.href='/login_parent'">
            <h3>ورود والدین</h3>
            <p>این بخش فقط برای والدین است</p>
        </div>
        
        <div class="btn student-btn" onclick="location.href='/login_student'">
            <h3>ورود دانش آموزان</h3>
            <p>این بخش فقط برای دانش آموزان است</p>
        </div>
    </div>
    
    <div class="footer">
        <p>دبیرستان پسرانه جوادالائمه - سال تحصیلی 1403</p>
    </div>

    <script>
        const menuToggle = document.getElementById('menuToggle');
        const menuSidebar = document.getElementById('menuSidebar');
        
        menuToggle.addEventListener('click', function() {
            menuSidebar.classList.toggle('active');
        });
        
        // Close sidebar when clicking outside
        document.addEventListener('click', function(event) {
            if (!menuSidebar.contains(event.target) && !menuToggle.contains(event.target)) {
                menuSidebar.classList.remove('active');
            }
        });
    </script>
</body>
</html>''',
    'login_admin.html': '''<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ورود مدیران</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            direction: rtl;
            font-family: 'Vazir', Tahoma, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            color: white;
        }
        
        .container {
            max-width: 500px;
            margin: 40px auto;
            padding: 30px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
        }
        
        .form-control {
            width: 100%;
            padding: 12px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            background: rgba(0, 0, 0, 0.3);
            color: white;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        
        .form-control:focus {
            outline: none;
            border-color: #00eeff;
            box-shadow: 0 0 10px rgba(0, 238, 255, 0.5);
            transform: scale(1.02);
        }
        
        .btn {
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 10px;
            background: linear-gradient(45deg, #ff00cc, #ff0066);
            color: white;
            font-size: 1.1rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(255, 0, 204, 0.4);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .error {
            color: #ff4444;
            background: rgba(255, 0, 0, 0.2);
            padding: 10px;
            border-radius: 10px;
            margin-top: 10px;
        }
        
        .back-btn {
            position: fixed;
            top: 20px;
            left: 20px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            font-size: 1.5rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .back-btn:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: scale(1.1);
        }
        
        .menu-toggle {
            position: fixed;
            top: 20px;
            right: 20px;
            width: 50px;
            height: 50px;
            display: flex;
            flex-direction: column;
            justify-content: space-around;
            z-index: 1000;
        }
        
        .menu-toggle span {
            width: 100%;
            height: 4px;
            background: white;
            border-radius: 2px;
            transition: all 0.3s ease;
        }
        
        .menu-sidebar {
            position: fixed;
            top: 0;
            right: 0;
            width: 300px;
            height: 100vh;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(10px);
            transform: translateX(100%);
            transition: transform 0.3s ease;
            z-index: 999;
            padding: 20px;
        }
        
        .menu-sidebar.active {
            transform: translateX(0);
        }
        
        .menu-sidebar ul {
            list-style: none;
            padding: 20px 0;
        }
        
        .menu-sidebar li {
            padding: 15px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .menu-sidebar a {
            color: white;
            text-decoration: none;
            display: block;
            padding: 10px;
            border-radius: 10px;
            transition: background 0.3s ease;
        }
        
        .menu-sidebar a:hover {
            background: rgba(255, 255, 255, 0.1);
        }
    </style>
</head>
<body>
    <div class="menu-toggle" id="menuToggle">
        <span></span>
        <span></span>
        <span></span>
    </div>
    
    <div class="menu-sidebar" id="menuSidebar">
        <ul>
            <li><a href="/">صفحه اصلی</a></li>
            <li><a href="/admin_dashboard">پروفایل</a></li>
            <li><a href="#">اعلانات</a></li>
        </ul>
    </div>

    <button class="back-btn" onclick="location.href='/'">←</button>
    
    <div class="container">
        <h2 style="text-align: center; margin-bottom: 30px; color: #00eeff;">ورود مدیران</h2>
        
        <form method="POST">
            <div class="form-group">
                <label for="name">نام</label>
                <input type="text" id="name" name="name" class="form-control" required>
            </div>
            
            <div class="form-group">
                <label for="lastname">نام خانوادگی</label>
                <input type="text" id="lastname" name="lastname" class="form-control" required>
            </div>
            
            <div class="form-group">
                <label for="position">مرتبه</label>
                <select id="position" name="position" class="form-control" required>
                    <option value="">انتخاب کنید</option>
                    <option value="مدیر">مدیر</option>
                    <option value="ناظم">ناظم</option>
                    <option value="معاون">معاون</option>
                    <option value="مشاور">مشاور</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="password">رمز</label>
                <input type="password" id="password" name="password" class="form-control" required>
            </div>
            
            <button type="submit" class="btn">ورود</button>
        </form>
        
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
    </div>

    <script>
        const menuToggle = document.getElementById('menuToggle');
        const menuSidebar = document.getElementById('menuSidebar');
        
        menuToggle.addEventListener('click', function() {
            menuSidebar.classList.toggle('active');
        });
        
        // Close sidebar when clicking outside
        document.addEventListener('click', function(event) {
            if (!menuSidebar.contains(event.target) && !menuToggle.contains(event.target)) {
                menuSidebar.classList.remove('active');
            }
        });
    </script>
</body>
</html>''',
    'admin_dashboard.html': '''<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>درگاه مدیران</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            direction: rtl;
            font-family: 'Vazir', Tahoma, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            color: white;
        }
        
        .header {
            text-align: center;
            padding: 20px;
            background: rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(10px);
            border-radius: 0 0 20px 20px;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 1.8rem;
            background: linear-gradient(to right, #ff00cc, #00eeff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 10px rgba(255, 0, 204, 0.5);
        }
        
        .buttons-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 20px;
            flex: 1;
        }
        
        .btn {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.2);
            position: relative;
            overflow: hidden;
        }
        
        .btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(45deg, #ff00cc, #00eeff, #ffcc00, #00ff99);
            opacity: 0;
            transition: opacity 0.3s ease;
            z-index: 1;
        }
        
        .btn:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
            z-index: 2;
        }
        
        .btn:hover::before {
            opacity: 0.2;
        }
        
        .btn:active {
            transform: scale(0.98);
        }
        
        .btn h3 {
            margin-bottom: 10px;
            font-size: 1.3rem;
        }
        
        .btn p {
            font-size: 0.9rem;
            color: #ccc;
        }
        
        .manage-students { background: linear-gradient(45deg, #ff00cc, #ff0066); }
        .manage-teachers { background: linear-gradient(45deg, #00eeff, #0066ff); }
        .manage-parent-reports { background: linear-gradient(45deg, #ffcc00, #ff6600); }
        .manage-teacher-reports { background: linear-gradient(45deg, #00ff99, #00cc66); }
        .manage-student-reports { background: linear-gradient(45deg, #ff00cc, #00eeff); }
        .manage-lab { background: linear-gradient(45deg, #ff6600, #ffcc00); }
        .manage-grades { background: linear-gradient(45deg, #00cc66, #00ff99); }
        .manage-report-card { background: linear-gradient(45deg, #6600ff, #cc00ff); }
        
        .footer {
            text-align: center;
            padding: 20px;
            background: rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(10px);
            border-radius: 20px 20px 0 0;
            margin-top: 30px;
        }
        
        .menu-toggle {
            position: fixed;
            top: 20px;
            right: 20px;
            width: 50px;
            height: 50px;
            display: flex;
            flex-direction: column;
            justify-content: space-around;
            z-index: 1000;
        }
        
        .menu-toggle span {
            width: 100%;
            height: 4px;
            background: white;
            border-radius: 2px;
            transition: all 0.3s ease;
        }
        
        .menu-sidebar {
            position: fixed;
            top: 0;
            right: 0;
            width: 300px;
            height: 100vh;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(10px);
            transform: translateX(100%);
            transition: transform 0.3s ease;
            z-index: 999;
            padding: 20px;
        }
        
        .menu-sidebar.active {
            transform: translateX(0);
        }
        
        .menu-sidebar ul {
            list-style: none;
            padding: 20px 0;
        }
        
        .menu-sidebar li {
            padding: 15px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .menu-sidebar a {
            color: white;
            text-decoration: none;
            display: block;
            padding: 10px;
            border-radius: 10px;
            transition: background 0.3s ease;
        }
        
        .menu-sidebar a:hover {
            background: rgba(255, 255, 255, 0.1);
        }
    </style>
</head>
<body>
    <div class="menu-toggle" id="menuToggle">
        <span></span>
        <span></span>
        <span></span>
    </div>
    
    <div class="menu-sidebar" id="menuSidebar">
        <ul>
            <li><a href="/">صفحه اصلی</a></li>
            <li><a href="/admin_profile">پروفایل</a></li>
            <li><a href="#">اعلانات</a></li>
        </ul>
    </div>

    <div class="header">
        <h1>درگاه مدیران</h1>
    </div>
    
    <div class="buttons-container">
        <div class="btn manage-students" onclick="location.href='/manage_students'">
            <h3>مدیریت دانش آموزان</h3>
        </div>
        
        <div class="btn manage-teachers" onclick="location.href='/manage_teachers'">
            <h3>مدیریت معلمان</h3>
        </div>
        
        <div class="btn manage-parent-reports" onclick="location.href='/manage_reports/admin'">
            <h3>مدیریت گزارشات والدین</h3>
        </div>
        
        <div class="btn manage-teacher-reports" onclick="location.href='/manage_reports/teacher'">
            <h3>مدیریت گزارشات معلمان</h3>
        </div>
        
        <div class="btn manage-student-reports" onclick="location.href='/manage_reports/student'">
            <h3>مدیریت گزارشات دانش آموزان</h3>
        </div>
        
        <div class="btn manage-lab" onclick="location.href='/manage_lab'">
            <h3>مدیریت بخش آزمایشگاه</h3>
        </div>
        
        <div class="btn manage-grades" onclick="location.href='/manage_grades'">
            <h3>مدیریت نمرات</h3>
        </div>
        
        <div class="btn manage-report-card" onclick="location.href='/manage_report_card'">
            <h3>مدیریت کارنامه</h3>
        </div>
    </div>
    
    <div class="footer">
        <p>درگاه مدیران - دبیرستان جوادالائمه</p>
    </div>

    <script>
        const menuToggle = document.getElementById('menuToggle');
        const menuSidebar = document.getElementById('menuSidebar');
        
        menuToggle.addEventListener('click', function() {
            menuSidebar.classList.toggle('active');
        });
        
        // Close sidebar when clicking outside
        document.addEventListener('click', function(event) {
            if (!menuSidebar.contains(event.target) && !menuToggle.contains(event.target)) {
                menuSidebar.classList.remove('active');
            }
        });
    </script>
</body>
</html>''',
    'manage_students.html': '''<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مدیریت دانش آموزان</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            direction: rtl;
            font-family: 'Vazir', Tahoma, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            color: white;
        }
        
        .header {
            text-align: center;
            padding: 20px;
            background: rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(10px);
            border-radius: 0 0 20px 20px;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 1.8rem;
            background: linear-gradient(to right, #ff00cc, #00eeff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 10px rgba(255, 0, 204, 0.5);
        }
        
        .buttons-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 20px;
            flex: 1;
        }
        
        .btn {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.2);
            position: relative;
            overflow: hidden;
        }
        
        .btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(45deg, #ff00cc, #00eeff, #ffcc00, #00ff99);
            opacity: 0;
            transition: opacity 0.3s ease;
            z-index: 1;
        }
        
        .btn:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
            z-index: 2;
        }
        
        .btn:hover::before {
            opacity: 0.2;
        }
        
        .btn:active {
            transform: scale(0.98);
        }
        
        .btn h3 {
            margin-bottom: 10px;
            font-size: 1.3rem;
        }
        
        .btn p {
            font-size: 0.9rem;
            color: #ccc;
        }
        
        .grade-btn { background: linear-gradient(45deg, #ff00cc, #ff0066); }
        .field-btn { background: linear-gradient(45deg, #00eeff, #0066ff); }
        
        .footer {
            text-align: center;
            padding: 20px;
            background: rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(10px);
            border-radius: 20px 20px 0 0;
            margin-top: 30px;
        }
        
        .menu-toggle {
            position: fixed;
            top: 20px;
            right: 20px;
            width: 50px;
            height: 50px;
            display: flex;
            flex-direction: column;
            justify-content: space-around;
            z-index: 1000;
        }
        
        .menu-toggle span {
            width: 100%;
            height: 4px;
            background: white;
            border-radius: 2px;
            transition: all 0.3s ease;
        }
        
        .menu-sidebar {
            position: fixed;
            top: 0;
            right: 0;
            width: 300px;
            height: 100vh;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(10px);
            transform: translateX(100%);
            transition: transform 0.3s ease;
            z-index: 999;
            padding: 20px;
        }
        
        .menu-sidebar.active {
            transform: translateX(0);
        }
        
        .menu-sidebar ul {
            list-style: none;
            padding: 20px 0;
        }
        
        .menu-sidebar li {
            padding: 15px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .menu-sidebar a {
            color: white;
            text-decoration: none;
            display: block;
            padding: 10px;
            border-radius: 10px;
            transition: background 0.3s ease;
        }
        
        .menu-sidebar a:hover {
            background: rgba(255, 255, 255, 0.1);
        }
    </style>
</head>
<body>
    <div class="menu-toggle" id="menuToggle">
        <span></span>
        <span></span>
        <span></span>
    </div>
    
    <div class="menu-sidebar" id="menuSidebar">
        <ul>
            <li><a href="/">صفحه اصلی</a></li>
            <li><a href="/admin_profile">پروفایل</a></li>
            <li><a href="#">اعلانات</a></li>
        </ul>
    </div>

    <div class="header">
        <h1>مدیریت دانش آموزان</h1>
    </div>
    
    <div class="buttons-container">
        <div class="btn grade-btn" onclick="location.href='/view_students/10/math'">
            <h3>پایه دهم</h3>
        </div>
        
        <div class="btn grade-btn" onclick="location.href='/view_students/11/math'">
            <h3>پایه یازدهم</h3>
        </div>
        
        <div class="btn grade-btn" onclick="location.href='/view_students/12/math'">
            <h3>پایه دوازدهم</h3>
        </div>
    </div>
    
    <div class="footer">
        <p>مدیریت دانش آموزان - دبیرستان جوادالائمه</p>
    </div>

    <script>
        const menuToggle = document.getElementById('menuToggle');
        const menuSidebar = document.getElementById('menuSidebar');
        
        menuToggle.addEventListener('click', function() {
            menuSidebar.classList.toggle('active');
        });
        
        // Close sidebar when clicking outside
        document.addEventListener('click', function(event) {
            if (!menuSidebar.contains(event.target) && !menuToggle.contains(event.target)) {
                menuSidebar.classList.remove('active');
            }
        });
    </script>
</body>
</html>''',
    'view_students.html': '''<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ grade }} - {{ field }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            direction: rtl;
            font-family: 'Vazir', Tahoma, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            color: white;
        }
        
        .header {
            text-align: center;
            padding: 20px;
            background: rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(10px);
            border-radius: 0 0 20px 20px;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 1.8rem;
            background: linear-gradient(to right, #ff00cc, #00eeff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 10px rgba(255, 0, 204, 0.5);
        }
        
        .students-container {
            padding: 20px;
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .student-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: all 0.3s ease;
        }
        
        .student-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        }
        
        .student-info {
            flex: 1;
        }
        
        .student-name {
            font-size: 1.2rem;
            margin-bottom: 5px;
        }
        
        .student-national-id {
            color: #ccc;
            font-size: 0.9rem;
        }
        
        .student-actions {
            display: flex;
            gap: 10px;
        }
        
        .action-btn {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            border: none;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .edit-btn {
            background: linear-gradient(45deg, #00eeff, #0066ff);
        }
        
        .delete-btn {
            background: linear-gradient(45deg, #ff4444, #cc0000);
        }
        
        .add-btn {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(45deg, #00ff99, #00cc66);
            border: none;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            cursor: pointer;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
        }
        
        .add-btn:hover {
            transform: scale(1.1);
        }
        
        .student-count {
            position: fixed;
            top: 20px;
            left: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 10px;
            padding: 10px 15px;
        }
        
        .search-btn {
            position: fixed;
            top: 80px;
            left: 20px;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: linear-gradient(45deg, #ffcc00, #ff6600);
            border: none;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .search-btn:hover {
            transform: scale(1.1);
        }
        
        .footer {
            text-align: center;
            padding: 20px;
            background: rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(10px);
            border-radius: 20px 20px 0 0;
            margin-top: 30px;
        }
        
        .menu-toggle {
            position: fixed;
            top: 20px;
            right: 20px;
            width: 50px;
            height: 50px;
            display: flex;
            flex-direction: column;
            justify-content: space-around;
            z-index: 1000;
        }
        
        .menu-toggle span {
            width: 100%;
            height: 4px;
            background: white;
            border-radius: 2px;
            transition: all 0.3s ease;
        }
        
        .menu-sidebar {
            position: fixed;
            top: 0;
            right: 0;
            width: 300px;
            height: 100vh;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(10px);
            transform: translateX(100%);
            transition: transform 0.3s ease;
            z-index: 999;
            padding: 20px;
        }
        
        .menu-sidebar.active {
            transform: translateX(0);
        }
        
        .menu-sidebar ul {
            list-style: none;
            padding: 20px 0;
        }
        
        .menu-sidebar li {
            padding: 15px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .menu-sidebar a {
            color: white;
            text-decoration: none;
            display: block;
            padding: 10px;
            border-radius: 10px;
            transition: background 0.3s ease;
        }
        
        .menu-sidebar a:hover {
            background: rgba(255, 255, 255, 0.1);
        }
    </style>
</head>
<body>
    <div class="menu-toggle" id="menuToggle">
        <span></span>
        <span></span>
        <span></span>
    </div>
    
    <div class="menu-sidebar" id="menuSidebar">
        <ul>
            <li><a href="/">صفحه اصلی</a></li>
            <li><a href="/admin_profile">پروفایل</a></li>
            <li><a href="#">اعلانات</a></li>
        </ul>
    </div>

    <div class="header">
        <h1>{{ grade }} - {{ field }}</h1>
    </div>
    
    <div class="student-count">
        <span>تعداد دانش آموزان:</span>
        <span>{{ students|length }}</span>
    </div>
    
    <button class="search-btn" onclick="location.href='/search_students/{{ grade }}/{{ field }}'">🔍</button>
    
    <div class="students-container">
        {% for student in students %}
        <div class="student-card" onclick="location.href='/view_student_details/{{ grade }}/{{ field }}/{{ loop.index0 }}'">
            <div class="student-info">
                <div class="student-name">{{ student.name }} {{ student.lastname }}</div>
                <div class="student-national-id">{{ student.national_id }}</div>
            </div>
            <div class="student-actions">
                <button class="action-btn edit-btn" onclick="event.stopPropagation(); location.href='/edit_student/{{ grade }}/{{ field }}/{{ loop.index0 }}'">✏️</button>
                <button class="action-btn delete-btn" onclick="event.stopPropagation(); if(confirm('آیا مطمئن هستید می‌خواهید اطلاعات دانش آموز را پاک کنید؟')) location.href='/delete_student/{{ grade }}/{{ field }}/{{ loop.index0 }}'">🗑️</button>
            </div>
        </div>
        {% endfor %}
    </div>
    
    <button class="add-btn" onclick="location.href='/add_student/{{ grade }}/{{ field }}'">+</button>
    
    <div class="footer">
        <p>مدیریت دانش آموزان - {{ grade }} {{ field }}</p>
    </div>

    <script>
        const menuToggle = document.getElementById('menuToggle');
        const menuSidebar = document.getElementById('menuSidebar');
        
        menuToggle.addEventListener('click', function() {
            menuSidebar.classList.toggle('active');
        });
        
        // Close sidebar when clicking outside
        document.addEventListener('click', function(event) {
            if (!menuSidebar.contains(event.target) && !menuToggle.contains(event.target)) {
                menuSidebar.classList.remove('active');
            }
        });
    </script>
</body>
</html>''',
    'add_student.html': '''<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>افزودن دانش آموز</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            direction: rtl;
            font-family: 'Vazir', Tahoma, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            color: white;
        }
        
        .container {
            max-width: 500px;
            margin: 40px auto;
            padding: 30px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
        }
        
        .form-control {
            width: 100%;
            padding: 12px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            background: rgba(0, 0, 0, 0.3);
            color: white;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        
        .form-control:focus {
            outline: none;
            border-color: #00eeff;
            box-shadow: 0 0 10px rgba(0, 238, 255, 0.5);
            transform: scale(1.02);
        }
        
        .btn {
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 10px;
            background: linear-gradient(45deg, #00ff99, #00cc66);
            color: white;
            font-size: 1.1rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(0, 255, 153, 0.4);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .error {
            color: #ff4444;
            background: rgba(255, 0, 0, 0.2);
            padding: 10px;
            border-radius: 10px;
            margin-top: 10px;
        }
        
        .back-btn {
            position: fixed;
            top: 20px;
            left: 20px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            font-size: 1.5rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .back-btn:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: scale(1.1);
        }
        
        .menu-toggle {
            position: fixed;
            top: 20px;
            right: 20px;
            width: 50px;
            height: 50px;
            display: flex;
            flex-direction: column;
            justify-content: space-around;
            z-index: 1000;
        }
        
        .menu-toggle span {
            width: 100%;
            height: 4px;
            background: white;
            border-radius: 2px;
            transition: all 0.3s ease;
        }
        
        .menu-sidebar {
            position: fixed;
            top: 0;
            right: 0;
            width: 300px;
            height: 100vh;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(10px);
            transform: translateX(100%);
            transition: transform 0.3s ease;
            z-index: 999;
            padding: 20px;
        }
        
        .menu-sidebar.active {
            transform: translateX(0);
        }
        
        .menu-sidebar ul {
            list-style: none;
            padding: 20px 0;
        }
        
        .menu-sidebar li {
            padding: 15px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .menu-sidebar a {
            color: white;
            text-decoration: none;
            display: block;
            padding: 10px;
            border-radius: 10px;
            transition: background 0.3s ease;
        }
        
        .menu-sidebar a:hover {
            background: rgba(255, 255, 255, 0.1);
        }
    </style>
</head>
<body>
    <div class="menu-toggle" id="menuToggle">
        <span></span>
        <span></span>
        <span></span>
    </div>
    
    <div class="menu-sidebar" id="menuSidebar">
        <ul>
            <li><a href="/">صفحه اصلی</a></li>
            <li><a href="/admin_profile">پروفایل</a></li>
            <li><a href="#">اعلانات</a></li>
        </ul>
    </div>

    <button class="back-btn" onclick="location.href='/view_students/{{ grade }}/{{ field }}'">←</button>
    
    <div class="container">
        <h2 style="text-align: center; margin-bottom: 30px; color: #00eeff;">افزودن دانش آموز</h2>
        
        <form method="POST">
            <div class="form-group">
                <label for="name">نام دانش آموز (اجباری)</label>
                <input type="text" id="name" name="name" class="form-control" required>
            </div>
            
            <div class="form-group">
                <label for="lastname">نام خانوادگی دانش آموز (اجباری)</label>
                <input type="text" id="lastname" name="lastname" class="form-control" required>
            </div>
            
            <div class="form-group">
                <label for="national_id">کد ملی دانش آموز (اجباری)</label>
                <input type="text" id="national_id" name="national_id" class="form-control" required>
            </div>
            
            <div class="form-group">
                <label for="student_number">شماره دانش آموز (اختیاری)</label>
                <input type="text" id="student_number" name="student_number" class="form-control">
            </div>
            
            <div class="form-group">
                <label for="father_number">شماره پدر (اختیاری)</label>
                <input type="text" id="father_number" name="father_number" class="form-control">
            </div>
            
            <div class="form-group">
                <label for="mother_number">شماره مادر (اختیاری)</label>
                <input type="text" id="mother_number" name="mother_number" class="form-control">
            </div>
            
            <button type="submit" class="btn">تایید</button>
        </form>
        
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
    </div>

    <script>
        const menuToggle = document.getElementById('menuToggle');
        const menuSidebar = document.getElementById('menuSidebar');
        
        menuToggle.addEventListener('click', function() {
            menuSidebar.classList.toggle('active');
        });
        
        // Close sidebar when clicking outside
        document.addEventListener('click', function(event) {
            if (!menuSidebar.contains(event.target) && !menuToggle.contains(event.target)) {
                menuSidebar.classList.remove('active');
            }
        });
    </script>
</body>
</html>''',
    'edit_student.html': '''<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ویرایش دانش آموز</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            direction: rtl;
            font-family: 'Vazir', Tahoma, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            color: white;
        }
        
        .container {
            max-width: 500px;
            margin: 40px auto;
            padding: 30px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
        }
        
        .form-control {
            width: 100%;
            padding: 12px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            background: rgba(0, 0, 0, 0.3);
            color: white;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        
        .form-control:focus {
            outline: none;
            border-color: #00eeff;
            box-shadow: 0 0 10px rgba(0, 238, 255, 0.5);
            transform: scale(1.02);
        }
        
        .btn {
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 10px;
            background: linear-gradient(45deg, #00ff99, #00cc66);
            color: white;
            font-size: 1.1rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(0, 255, 153, 0.4);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .back-btn {
            position: fixed;
            top: 20px;
            left: 20px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            font-size: 1.5rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .back-btn:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: scale(1.1);
        }
        
        .menu-toggle {
            position: fixed;
            top: 20px;
            right: 20px;
            width: 50px;
            height: 50px;
            display: flex;
            flex-direction: column;
            justify-content: space-around;
            z-index: 1000;
        }
        
        .menu-toggle span {
            width: 100%;
            height: 4px;
            background: white;
            border-radius: 2px;
            transition: all 0.3s ease;
        }
        
        .menu-sidebar {
            position: fixed;
            top: 0;
            right: 0;
            width: 300px;
            height: 100vh;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(10px);
            transform: translateX(100%);
            transition: transform 0.3s ease;
            z-index: 999;
            padding: 20px;
        }
        
        .menu-sidebar.active {
            transform: translateX(0);
        }
        
        .menu-sidebar ul {
            list-style: none;
            padding: 20px 0;
        }
        
        .menu-sidebar li {
            padding: 15px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .menu-sidebar a {
            color: white;
            text-decoration: none;
            display: block;
            padding: 10px;
            border-radius: 10px;
            transition: background 0.3s ease;
        }
        
        .menu-sidebar a:hover {
            background: rgba(255, 255, 255, 0.1);
        }
    </style>
</head>
<body>
    <div class="menu-toggle" id="menuToggle">
        <span></span>
        <span></span>
        <span></span>
    </div>
    
    <div class="menu-sidebar" id="menuSidebar">
        <ul>
            <li><a href="/">صفحه اصلی</a></li>
            <li><a href="/admin_profile">پروفایل</a></li>
            <li><a href="#">اعلانات</a></li>
        </ul>
    </div>

    <button class="back-btn" onclick="location.href='/view_students/{{ grade }}/{{ field }}'">←</button>
    
    <div class="container">
        <h2 style="text-align: center; margin-bottom: 30px; color: #00eeff;">ویرایش دانش آموز</h2>
        
        <form method="POST">
            <div class="form-group">
                <label for="name">نام دانش آموز</label>
                <input type="text" id="name" name="name" class="form-control" value="{{ student.name }}" required>
            </div>
            
            <div class="form-group">
                <label for="lastname">نام خانوادگی دانش آموز</label>
                <input type="text" id="lastname" name="lastname" class="form-control" value="{{ student.lastname }}" required>
            </div>
            
            <div class="form-group">
                <label for="national_id">کد ملی دانش آموز</label>
                <input type="text" id="national_id" name="national_id" class="form-control" value="{{ student.national_id }}" required>
            </div>
            
            <div class="form-group">
                <label for="student_number">شماره دانش آموز</label>
                <input type="text" id="student_number" name="student_number" class="form-control" value="{{ student.student_number }}">
            </div>
            
            <div class="form-group">
                <label for="father_number">شماره پدر</label>
                <input type="text" id="father_number" name="father_number" class="form-control" value="{{ student.father_number }}">
            </div>
            
            <div class="form-group">
                <label for="mother_number">شماره مادر</label>
                <input type="text" id="mother_number" name="mother_number" class="form-control" value="{{ student.mother_number }}">
            </div>
            
            <button type="submit" class="btn">تایید</button>
        </form>
    </div>

    <script>
        const menuToggle = document.getElementById('menuToggle');
        const menuSidebar = document.getElementById('menuSidebar');
        
        menuToggle.addEventListener('click', function() {
            menuSidebar.classList.toggle('active');
        });
        
        // Close sidebar when clicking outside
        document.addEventListener('click', function(event) {
            if (!menuSidebar.contains(event.target) && !menuToggle.contains(event.target)) {
                menuSidebar.classList.remove('active');
            }
        });
    </script>
</body>
</html>''',
    'student_details.html': '''<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>جزئیات دانش آموز</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            direction: rtl;
            font-family: 'Vazir', Tahoma, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            color: white;
        }
        
        .container {
            max-width: 500px;
            margin: 40px auto;
            padding: 30px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .info-group {
            margin-bottom: 20px;
            padding: 15px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 10px;
        }
        
        .info-label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #00eeff;
        }
        
        .info-value {
            display: block;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .back-btn {
            position: fixed;
            top: 20px;
            left: 20px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            font-size: 1.5rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .back-btn:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: scale(1.1);
        }
        
        .menu-toggle {
            position: fixed;
            top: 20px;
            right: 20px;
            width: 50px;
            height: 50px;
            display: flex;
            flex-direction: column;
            justify-content: space-around;
            z-index: 1000;
        }
        
        .menu-toggle span {
            width: 100%;
            height: 4px;
            background: white;
            border-radius: 2px;
            transition: all 0.3s ease;
        }
        
        .menu-sidebar {
            position: fixed;
            top: 0;
            right: 0;
            width: 300px;
            height: 100vh;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(10px);
            transform: translateX(100%);
            transition: transform 0.3s ease;
            z-index: 999;
            padding: 20px;
        }
        
        .menu-sidebar.active {
            transform: translateX(0);
        }
        
        .menu-sidebar ul {
            list-style: none;
            padding: 20px 0;
        }
        
        .menu-sidebar li {
            padding: 15px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .menu-sidebar a {
            color: white;
            text-decoration: none;
            display: block;
            padding: 10px;
            border-radius: 10px;
            transition: background 0.3s ease;
        }
        
        .menu-sidebar a:hover {
            background: rgba(255, 255, 255, 0.1);
        }
    </style>
</head>
<body>
    <div class="menu-toggle" id="menuToggle">
        <span></span>
        <span></span>
        <span></span>
    </div>
    
    <div class="menu-sidebar" id="menuSidebar">
        <ul>
            <li><a href="/">صفحه اصلی</a></li>
            <li><a href="/admin_profile">پروفایل</a></li>
            <li><a href="#">اعلانات</a></li>
        </ul>
    </div>

    <button class="back-btn" onclick="location.href='/view_students/{{ grade }}/{{ field }}'">←</button>
    
    <div class="container">
        <h2 style="text-align: center; margin-bottom: 30px; color: #00eeff;">جزئیات دانش آموز</h2>
        
        <div class="info-group">
            <span class="info-label">نام دانش آموز</span>
            <span class="info-value">{{ student.name }}</span>
        </div>
        
        <div class="info-group">
            <span class="info-label">نام خانوادگی دانش آموز</span>
            <span class="info-value">{{ student.lastname }}</span>
        </div>
        
        <div class="info-group">
            <span class="info-label">کد ملی دانش آموز</span>
            <span class="info-value">{{ student.national_id }}</span>
        </div>
        
        <div class="info-group">
            <span class="info-label">شماره دانش آموز</span>
            <span class="info-value">{{ student.student_number if student.student_number else "ثبت نشده" }}</span>
        </div>
        
        <div class="info-group">
            <span class="info-label">شماره پدر</span>
            <span class="info-value">{{ student.father_number if student.father_number else "ثبت نشده" }}</span>
        </div>
        
        <div class="info-group">
            <span class="info-label">شماره مادر</span>
            <span class="info-value">{{ student.mother_number if student.mother_number else "ثبت نشده" }}</span>
        </div>
    </div>

    <script>
        const menuToggle = document.getElementById('menuToggle');
        const menuSidebar = document.getElementById('menuSidebar');
        
        menuToggle.addEventListener('click', function() {
            menuSidebar.classList.toggle('active');
        });
        
        // Close sidebar when clicking outside
        document.addEventListener('click', function(event) {
            if (!menuSidebar.contains(event.target) && !menuToggle.contains(event.target)) {
                menuSidebar.classList.remove('active');
            }
        });
    </script>
</body>
</html>''',
    'search_results.html': '''<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>نتایج جستجو</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            direction: rtl;
            font-family: 'Vazir', Tahoma, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            color: white;
        }
        
        .container {
            max-width: 500px;
            margin: 40px auto;
            padding: 30px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .search-form {
            margin-bottom: 30px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
        }
        
        .form-control {
            width: 100%;
            padding: 12px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            background: rgba(0, 0, 0, 0.3);
            color: white;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        
        .form-control:focus {
            outline: none;
            border-color: #00eeff;
            box-shadow: 0 0 10px rgba(0, 238, 255, 0.5);
            transform: scale(1.02);
        }
        
        .btn {
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 10px;
            background: linear-gradient(45deg, #00eeff, #0066ff);
            color: white;
            font-size: 1.1rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(0, 238, 255, 0.4);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .results-container {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .result-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 15px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: all 0.3s ease;
        }
        
        .result-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        }
        
        .result-name {
            font-size: 1.2rem;
            margin-bottom: 5px;
        }
        
        .result-national-id {
            color: #ccc;
            font-size: 0.9rem;
            margin-bottom: 5px;
        }
        
        .result-grade-field {
            color: #aaa;
            font-size: 0.9rem;
        }
        
        .back-btn {
            position: fixed;
            top: 20px;
            left: 20px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            font-size: 1.5rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .back-btn:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: scale(1.1);
        }
        
        .menu-toggle {
            position: fixed;
            top: 20px;
            right: 20px;
            width: 50px;
            height: 50px;
            display: flex;
            flex-direction: column;
            justify-content: space-around;
            z-index: 1000;
        }
        
        .menu-toggle span {
            width: 100%;
            height: 4px;
            background: white;
            border-radius: 2px;
            transition: all 0.3s ease;
        }
        
        .menu-sidebar {
            position: fixed;
            top: 0;
            right: 0;
            width: 300px;
            height: 100vh;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(10px);
            transform: translateX(100%);
            transition: transform 0.3s ease;
            z-index: 999;
            padding: 20px;
        }
        
        .menu-sidebar.active {
            transform: translateX(0);
        }
        
        .menu-sidebar ul {
            list-style: none;
            padding: 20px 0;
        }
        
        .menu-sidebar li {
            padding: 15px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .menu-sidebar a {
            color: white;
            text-decoration: none;
            display: block;
            padding: 10px;
            border-radius: 10px;
            transition: background 0.3s ease;
        }
        
        .menu-sidebar a:hover {
            background: rgba(255, 255, 255, 0.1);
        }
    </style>
</head>
<body>
    <div class="menu-toggle" id="menuToggle">
        <span></span>
        <span></span>
        <span></span>
    </div>
    
    <div class="menu-sidebar" id="menuSidebar">
        <ul>
            <li><a href="/">صفحه اصلی</a></li>
            <li><a href="/admin_profile">پروفایل</a></li>
            <li><a href="#">اعلانات</a></li>
        </ul>
    </div>

    <button class="back-btn" onclick="location.href='/view_students/{{ grade }}/{{ field }}'">←</button>
    
    <div class="container">
        <h2 style="text-align: center; margin-bottom: 30px; color: #00eeff;">جستجوی دانش آموزان</h2>
        
        <form method="POST" class="search-form">
            <div class="form-group">
                <label for="query">جستجو بر اساس نام، نام خانوادگی یا کد ملی</label>
                <input type="text" id="query" name="query" class="form-control" required>
            </div>
            <button type="submit" class="btn">جستجو</button>
        </form>
        
        <div class="results-container">
            {% for result in results %}
            <div class="result-card" onclick="location.href='/view_student_details/{{ grade }}/{{ field }}/{{ results.index(result) }}'">
                <div class="result-name">{{ result.name }} {{ result.lastname }}</div>
                <div class="result-national-id">{{ result.national_id }}</div>
                <div class="result-grade-field">{{ grade }} - {{ field }}</div>
            </div>
            {% endfor %}
        </div>
    </div>

    <script>
        const menuToggle = document.getElementById('menuToggle');
        const menuSidebar = document.getElementById('menuSidebar');
        
        menuToggle.addEventListener('click', function() {
            menuSidebar.classList.toggle('active');
        });
        
        // Close sidebar when clicking outside
        document.addEventListener('click', function(event) {
            if (!menuSidebar.contains(event.target) && !menuToggle.contains(event.target)) {
                menuSidebar.classList.remove('active');
            }
        });
    </script>
</body>
</html>''',
    'manage_reports.html': '''<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مدیریت گزارشات</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            direction: rtl;
            font-family: 'Vazir', Tahoma, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            color: white;
        }
        
        .header {
            text-align: center;
            padding: 20px;
            background: rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(10px);
            border-radius: 0 0 20px 20px;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 1.8rem;
            background: linear-gradient(to right, #ff00cc, #00eeff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 10px rgba(255, 0, 204, 0.5);
        }
        
        .reports-container {
            padding: 20px;
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .report-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 15px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: all 0.3s ease;
        }
        
        .report-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        }
        
        .report-header {
            font-size: 1.1rem;
            margin-bottom: 10px;
            color: #00eeff;
        }
        
        .report-content {
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .back-btn {
            position: fixed;
            top: 20px;
            left: 20px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            font-size: 1.5rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .back-btn:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: scale(1.1);
        }
        
        .menu-toggle {
            position: fixed;
            top: 20px;
            right: 20px;
            width: 50px;
            height: 50px;
            display: flex;
            flex-direction: column;
            justify-content: space-around;
            z-index: 1000;
        }
        
        .menu-toggle span {
            width: 100%;
            height: 4px;
            background: white;
            border-radius: 2px;
            transition: all 0.3s ease;
        }
        
        .menu-sidebar {
            position: fixed;
            top: 0;
            right: 0;
            width: 300px;
            height: 100vh;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(10px);
            transform: translateX(100%);
            transition: transform 0.3s ease;
            z-index: 999;
            padding: 20px;
        }
        
        .menu-sidebar.active {
            transform: translateX(0);
        }
        
        .menu-sidebar ul {
            list-style: none;
            padding: 20px 0;
        }
        
        .menu-sidebar li {
            padding: 15px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .menu-sidebar a {
            color: white;
            text-decoration: none;
            display: block;
            padding: 10px;
            border-radius: 10px;
            transition: background 0.3s ease;
        }
        
        .menu-sidebar a:hover {
            background: rgba(255, 255, 255, 0.1);
        }
    </style>
</head>
<body>
    <div class="menu-toggle" id="menuToggle">
        <span></span>
        <span></span>
        <span></span>
    </div>
    
    <div class="menu-sidebar" id="menuSidebar">
        <ul>
            <li><a href="/">صفحه اصلی</a></li>
            <li><a href="/admin_profile">پروفایل</a></li>
            <li><a href="#">اعلانات</a></li>
        </ul>
    </div>

    <button class="back-btn" onclick="location.href='/admin_dashboard'">←</button>
    
    <div class="header">
        <h1>مدیریت گزارشات {{ report_type }}</h1>
    </div>
    
    <div class="reports-container">
        {% for report in reports %}
        <div class="report-card">
            <div class="report-header">
                {% if report_type == 'admin' %}
                نام والد: {{ report.parent.name }} {{ report.parent.lastname }}<br>
                نام فرزند: {{ report.parent.child_name }}<br>
                {% elif report_type == 'teacher' %}
                نام معلم: {{ report.teacher.name }} {{ report.teacher.lastname }}<br>
                {% else %}
                نام دانش آموز: {{ report.student.name }} {{ report.student.lastname }}<br>
                {% endif %}
            </div>
            <div class="report-content">
                {{ report.report }}
            </div>
        </div>
        {% endfor %}
    </div>
    
    <div class="footer">
        <p>مدیریت گزارشات - {{ report_type }}</p>
    </div>

    <script>
        const menuToggle = document.getElementById('menuToggle');
        const menuSidebar = document.getElementById('menuSidebar');
        
        menuToggle.addEventListener('click', function() {
            menuSidebar.classList.toggle('active');
        });
        
        // Close sidebar when clicking outside
        document.addEventListener('click', function(event) {
            if (!menuSidebar.contains(event.target) && !menuToggle.contains(event.target)) {
                menuSidebar.classList.remove('active');
            }
        });
    </script>
</body>
</html>''',
    'manage_lab.html': '''<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مدیریت آزمایشگاه</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            direction: rtl;
            font-family: 'Vazir', Tahoma, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            color: white;
        }
        
        .header {
            text-align: center;
            padding: 20px;
            background: rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(10px);
            border-radius: 0 0 20px 20px;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 1.8rem;
            background: linear-gradient(to right, #ff00cc, #00eeff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 10px rgba(255, 0, 204, 0.5);
        }
        
        .lab-container {
            padding: 20px;
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .lab-item {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 15px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .image-container {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
            margin-bottom: 15px;
        }
        
        .image-item {
            aspect-ratio: 1/1;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            overflow: hidden;
        }
        
        .image-item img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        .description {
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .action-buttons {
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }
        
        .action-btn {
            flex: 1;
            padding: 10px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .edit-btn {
            background: linear-gradient(45deg, #00eeff, #0066ff);
        }
        
        .delete-btn {
            background: linear-gradient(45deg, #ff4444, #cc0000);
        }
        
        .add-btn {
            position: fixed;
            top: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(45deg, #00ff99, #00cc66);
            border: none;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            cursor: pointer;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
        }
        
        .add-btn:hover {
            transform: scale(1.1);
        }
        
        .back-btn {
            position: fixed;
            top: 20px;
            left: 20px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            font-size: 1.5rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .back-btn:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: scale(1.1);
        }
        
        .menu-toggle {
            position: fixed;
            top: 20px;
            right: 20px;
            width: 50px;
            height: 50px;
            display: flex;
            flex-direction: column;
            justify-content: space-around;
            z-index: 1000;
        }
        
        .menu-toggle span {
            width: 100%;
            height: 4px;
            background: white;
            border-radius: 2px;
            transition: all 0.3s ease;
        }
        
        .menu-sidebar {
            position: fixed;
            top: 0;
            right: 0;
            width: 300px;
            height: 100vh;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(10px);
            transform: translateX(100%);
            transition: transform 0.3s ease;
            z-index: 999;
            padding: 20px;
        }
        
        .menu-sidebar.active {
            transform: translateX(0);
        }
        
        .menu-sidebar ul {
            list-style: none;
            padding: 20px 0;
        }
        
        .menu-sidebar li {
            padding: 15px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .menu-sidebar a {
            color: white;
            text-decoration: none;
            display: block;
            padding: 10px;
            border-radius: 10px;
            transition: background 0.3s ease;
        }
        
        .menu-sidebar a:hover {
            background: rgba(255, 255, 255, 0.1);
        }
    </style>
</head>
<body>
    <div class="menu-toggle" id="menuToggle">
        <span></span>
        <span></span>
        <span></span>
    </div>
    
    <div class="menu-sidebar" id="menuSidebar">
        <ul>
            <li><a href="/">صفحه اصلی</a></li>
            <li><a href="/admin_profile">پروفایل</a></li>
            <li><a href="#">اعلانات</a></li>
        </ul>
    </div>

    <button class="back-btn" onclick="location.href='/admin_dashboard'">←</button>
    
    <div class="header">
        <h1>مدیریت بخش آزمایشگاه</h1>
    </div>
    
    <div class="lab-container">
        {% for item in laboratory %}
        <div class="lab-item">
            <div class="image-container">
                {% for image in item.images %}
                <div class="image-item">
                    <img src="{{ image }}" alt="عکس آزمایش">
                </div>
                {% endfor %}
            </div>
            <div class="description">{{ item.description }}</div>
            <div class="action-buttons">
                <button class="action-btn edit-btn">✏️ ویرایش</button>
                <button class="action-btn delete-btn" onclick="if(confirm('آیا مطمئن هستید می‌خواهید این مورد را پاک کنید؟')) location.href='#'">🗑️ حذف</button>
            </div>
        </div>
        {% endfor %}
    </div>
    
    <button class="add-btn" onclick="location.href='#'">+</button>
    
    <div class="footer">
        <p>مدیریت آزمایشگاه - دبیرستان جوادالائمه</p>
    </div>

    <script>
        const menuToggle = document.getElementById('menuToggle');
        const menuSidebar = document.getElementById('menuSidebar');
        
        menuToggle.addEventListener('click', function() {
            menuSidebar.classList.toggle('active');
        });
        
        // Close sidebar when clicking outside
        document.addEventListener('click', function(event) {
            if (!menuSidebar.contains(event.target) && !menuToggle.contains(event.target)) {
                menuSidebar.classList.remove('active');
            }
        });
    </script>
</body>
</html>''',
    'manage_grades.html': '''<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مدیریت نمرات</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            direction: rtl;
            font-family: 'Vazir', Tahoma, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            color: white;
        }
        
        .header {
            text-align: center;
            padding: 20px;
            background: rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(10px);
            border-radius: 0 0 20px 20px;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 1.8rem;
            background: linear-gradient(to right, #ff00cc, #00eeff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 10px rgba(255, 0, 204, 0.5);
        }
        
        .grades-container {
            padding: 20px;
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .grade-item {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 15px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: all 0.3s ease;
        }
        
        .grade-item:hover {
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        }
        
        .grade-header {
            font-size: 1.2rem;
            margin-bottom: 10px;
            color: #00eeff;
        }
        
        .student-list {
            margin-top: 15px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        .student-item {
            padding: 10px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .grades-inputs {
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }
        
        .grade-input {
            flex: 1;
            padding: 8px;
            border-radius: 5px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            background: rgba(0, 0, 0, 0.3);
            color: white;
            text-align: center;
        }
        
        .back-btn {
            position: fixed;
            top: 20px;
            left: 20px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            font-size: 1.5rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .back-btn:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: scale(1.1);
        }
        
        .menu-toggle {
            position: fixed;
            top: 20px;
            right: 20px;
            width: 50px;
            height: 50px;
            display: flex;
            flex-direction: column;
            justify-content: space-around;
            z-index: 1000;
        }
        
        .menu-toggle span {
            width: 100%;
            height: 4px;
            background: white;
            border-radius: 2px;
            transition: all 0.3s ease;
        }
        
        .menu-sidebar {
            position: fixed;
            top: 0;
            right: 0;
            width: 300px;
            height: 100vh;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(10px);
            transform: translateX(100%);
            transition: transform 0.3s ease;
            z-index: 999;
            padding: 20px;
        }
        
        .menu-sidebar.active {
            transform: translateX(0);
        }
        
        .menu-sidebar ul {
            list-style: none;
            padding: 20px 0;
        }
        
        .menu-sidebar li {
            padding: 15px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .menu-sidebar a {
            color: white;
            text-decoration: none;
            display: block;
            padding: 10px;
            border-radius: 10px;
            transition: background 0.3s ease;
        }
        
        .menu-sidebar a:hover {
            background: rgba(255, 255, 255, 0.1);
        }
    </style>
</head>
<body>
    <div class="menu-toggle" id="menuToggle">
        <span></span>
        <span></span>
        <span></span>
    </div>
    
    <div class="menu-sidebar" id="menuSidebar">
        <ul>
            <li><a href="/">صفحه اصلی</a></li>
            <li><a href="/admin_profile">پروفایل</a></li>
            <li><a href="#">اعلانات</a></li>
        </ul>
    </div>

    <button class="back-btn" onclick="location.href='/admin_dashboard'">←</button>
    
    <div class="header">
        <h1>مدیریت نمرات</h1>
    </div>
    
    <div class="grades-container">
        {% for grade, subjects in grades.items() %}
        <div class="grade-item">
            <div class="grade-header">پایه {{ grade }}</div>
            {% for subject, students in subjects.items() %}
            <div class="subject-header">رشته {{ subject }}</div>
            <div class="student-list">
                {% for student in students %}
                <div class="student-item">
                    <div>{{ student.name }} {{ student.lastname }}</div>
                    <div class="grades-inputs">
                        <input type="number" class="grade-input" min="0" max="20" placeholder="میان ترم ۱" value="{{ student.grades.get('midterm1', '') if student.get('grades') else '' }}">
                        <input type="number" class="grade-input" min="0" max="20" placeholder="نوبت ۱" value="{{ student.grades.get('exam1', '') if student.get('grades') else '' }}">
                        <input type="number" class="grade-input" min="0" max="20" placeholder="میان ترم ۲" value="{{ student.grades.get('midterm2', '') if student.get('grades') else '' }}">
                        <input type="number" class="grade-input" min="0" max="20" placeholder="نوبت ۲" value="{{ student.grades.get('exam2', '') if student.get('grades') else '' }}">
                    </div>
                </div>
                {% endfor %}
            </div>
            {% endfor %}
        </div>
        {% endfor %}
    </div>
    
    <div class="footer">
        <p>مدیریت نمرات - دبیرستان جوادالائمه</p>
    </div>

    <script>
        const menuToggle = document.getElementById('menuToggle');
        const menuSidebar = document.getElementById('menuSidebar');
        
        menuToggle.addEventListener('click', function() {
            menuSidebar.classList.toggle('active');
        });
        
        // Close sidebar when clicking outside
        document.addEventListener('click', function(event) {
            if (!menuSidebar.contains(event.target) && !menuToggle.contains(event.target)) {
                menuSidebar.classList.remove('active');
            }
        });
    </script>
</body>
</html>''',
    'manage_report_card.html': '''<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مدیریت کارنامه</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            direction: rtl;
            font-family: 'Vazir', Tahoma, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            color: white;
        }
        
        .container {
            max-width: 500px;
            margin: 40px auto;
            padding: 30px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
        }
        
        .form-control {
            width: 100%;
            padding: 12px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            background: rgba(0, 0, 0, 0.3);
            color: white;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        
        .form-control:focus {
            outline: none;
            border-color: #00eeff;
            box-shadow: 0 0 10px rgba(0, 238, 255, 0.5);
            transform: scale(1.02);
        }
        
        .btn {
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 10px;
            background: linear-gradient(45deg, #00ff99, #00cc66);
            color: white;
            font-size: 1.1rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(0, 255, 153, 0.4);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .back-btn {
            position: fixed;
            top: 20px;
            left: 20px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            font-size: 1.5rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .back-btn:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: scale(1.1);
        }
        
        .menu-toggle {
            position: fixed;
            top: 20px;
            right: 20px;
            width: 50px;
            height: 50px;
            display: flex;
            flex-direction: column;
            justify-content: space-around;
            z-index: 1000;
        }
        
        .menu-toggle span {
            width: 100%;
            height: 4px;
            background: white;
            border-radius: 2px;
            transition: all 0.3s ease;
        }
        
        .menu-sidebar {
            position: fixed;
            top: 0;
            right: 0;
            width: 300px;
            height: 100vh;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(10px);
            transform: translateX(100%);
            transition: transform 0.3s ease;
            z-index: 999;
            padding: 20px;
        }
        
        .menu-sidebar.active {
            transform: translateX(0);
        }
        
        .menu-sidebar ul {
            list-style: none;
            padding: 20px 0;
        }
        
        .menu-sidebar li {
            padding: 15px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .menu-sidebar a {
            color: white;
            text-decoration: none;
            display: block;
            padding: 10px;
            border-radius: 10px;
            transition: background 0.3s ease;
        }
        
        .menu-sidebar a:hover {
            background: rgba(255, 255, 255, 0.1);
        }
    </style>
</head>
<body>
    <div class="menu-toggle" id="menuToggle">
        <span></span>
        <span></span>
        <span></span>
    </div>
    
    <div class="menu-sidebar" id="menuSidebar">
        <ul>
            <li><a href="/">صفحه اصلی</a></li>
            <li><a href="/admin_profile">پروفایل</a></li>
            <li><a href="#">اعلانات</a></li>
        </ul>
    </div>

    <button class="back-btn" onclick="location.href='/admin_dashboard'">←</button>
    
    <div class="container">
        <h2 style="text-align: center; margin-bottom: 30px; color: #00eeff;">مدیریت کارنامه</h2>
        
        <form method="POST">
            <div class="form-group">
                <label for="grade">پایه</label>
                <select id="grade" name="grade" class="form-control" required>
                    <option value="">انتخاب کنید</option>
                    <option value="10">دهم</option>
                    <option value="11">یازدهم</option>
                    <option value="12">دوازدهم</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="field">رشته</label>
                <select id="field" name="field" class="form-control" required>
                    <option value="">انتخاب کنید</option>
                    <option value="math">ریاضی</option>
                    <option value="science">تجربی</option>
                    <option value="humanities">انسانی</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="student">دانش آموز</label>
                <select id="student" name="student" class="form-control" required>
                    <option value="">انتخاب کنید</option>
                    <!-- دانش آموزان به صورت پویا اضافه خواهند شد -->
                </select>
            </div>
            
            <button type="submit" class="btn">تایید</button>
        </form>
    </div>

    <script>
        const menuToggle = document.getElementById('menuToggle');
        const menuSidebar = document.getElementById('menuSidebar');
        
        menuToggle.addEventListener('click', function() {
            menuSidebar.classList.toggle('active');
        });
        
        // Close sidebar when clicking outside
        document.addEventListener('click', function(event) {
            if (!menuSidebar.contains(event.target) && !menuToggle.contains(event.target)) {
                menuSidebar.classList.remove('active');
            }
        });
    </script>
</body>
</html>''',
    'admin_profile.html': '''<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>پروفایل مدیر</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            direction: rtl;
            font-family: 'Vazir', Tahoma, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            color: white;
        }
        
        .container {
            max-width: 500px;
            margin: 40px auto;
            padding: 30px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .info-group {
            margin-bottom: 20px;
            padding: 15px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .info-label {
            font-weight: bold;
            color: #00eeff;
        }
        
        .info-value {
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .edit-btn {
            background: linear-gradient(45deg, #00eeff, #0066ff);
            color: white;
            border: none;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .edit-btn:hover {
            transform: scale(1.1);
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
        }
        
        .form-control {
            width: 100%;
            padding: 12px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            background: rgba(0, 0, 0, 0.3);
            color: white;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        
        .form-control:focus {
            outline: none;
            border-color: #00eeff;
            box-shadow: 0 0 10px rgba(0, 238, 255, 0.5);
            transform: scale(1.02);
        }
        
        .btn {
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 10px;
            background: linear-gradient(45deg, #00ff99, #00cc66);
            color: white;
            font-size: 1.1rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(0, 255, 153, 0.4);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .logout-btn {
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 10px;
            background: linear-gradient(45deg, #ff4444, #cc0000);
            color: white;
            font-size: 1.1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 20px;
        }
        
        .logout-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(255, 68, 68, 0.4);
        }
        
        .logout-btn:active {
            transform: translateY(0);
        }
        
        .back-btn {
            position: fixed;
            top: 20px;
            left: 20px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            font-size: 1.5rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .back-btn:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: scale(1.1);
        }
        
        .menu-toggle {
            position: fixed;
            top: 20px;
            right: 20px;
            width: 50px;
            height: 50px;
            display: flex;
            flex-direction: column;
            justify-content: space-around;
            z-index: 1000;
        }
        
        .menu-toggle span {
            width: 100%;
            height: 4px;
            background: white;
            border-radius: 2px;
            transition: all 0.3s ease;
        }
        
        .menu-sidebar {
            position: fixed;
            top: 0;
            right: 0;
            width: 300px;
            height: 100vh;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(10px);
            transform: translateX(100%);
            transition: transform 0.3s ease;
            z-index: 999;
            padding: 20px;
        }
        
        .menu-sidebar.active {
            transform: translateX(0);
        }
        
        .menu-sidebar ul {
            list-style: none;
            padding: 20px 0;
        }
        
        .menu-sidebar li {
            padding: 15px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .menu-sidebar a {
            color: white;
            text-decoration: none;
            display: block;
            padding: 10px;
            border-radius: 10px;
            transition: background 0.3s ease;
        }
        
        .menu-sidebar a:hover {
            background: rgba(255, 255, 255, 0.1);
        }
    </style>
</head>
<body>
    <div class="menu-toggle" id="menuToggle">
        <span></span>
        <span></span>
        <span></span>
    </div>
    
    <div class="menu-sidebar" id="menuSidebar">
        <ul>
            <li><a href="/">صفحه اصلی</a></li>
            <li><a href="/admin_profile">پروفایل</a></li>
            <li><a href="#">اعلانات</a></li>
        </ul>
    </div>

    <button class="back-btn" onclick="location.href='/admin_dashboard'">←</button>
    
    <div class="container">
        <h2 style="text-align: center; margin-bottom: 30px; color: #00eeff;">پروفایل مدیر</h2>
        
        <div class="info-group">
            <span class="info-label">نام:</span>
            <div class="info-value">{{ admin.name }}</div>
            <button class="edit-btn" onclick="editField('name')">✏️</button>
        </div>
        
        <div class="info-group">
            <span class="info-label">نام خانوادگی:</span>
            <div class="info-value">{{ admin.lastname }}</div>
            <button class="edit-btn" onclick="editField('lastname')">✏️</button>
        </div>
        
        <div class="info-group">
            <span class="info-label">مرتبه:</span>
            <div class="info-value">{{ admin.position }}</div>
            <button class="edit-btn" disabled>✏️</button>
        </div>
        
        <div class="info-group">
            <span class="info-label">رمز:</span>
            <div class="info-value">••••••••</div>
            <button class="edit-btn" disabled>✏️</button>
        </div>
        
        <form id="editForm" method="POST" style="display: none;">
            <div class="form-group">
                <label for="name">نام</label>
                <input type="text" id="name" name="name" class="form-control" value="{{ admin.name }}">
            </div>
            
            <div class="form-group">
                <label for="lastname">نام خانوادگی</label>
                <input type="text" id="lastname" name="lastname" class="form-control" value="{{ admin.lastname }}">
            </div>
            
            <div class="form-group">
                <label for="position">مرتبه</label>
                <select id="position" name="position" class="form-control">
                    <option value="مدیر" {% if admin.position == 'مدیر' %}selected{% endif %}>مدیر</option>
                    <option value="ناظم" {% if admin.position == 'ناظم' %}selected{% endif %}>ناظم</option>
                    <option value="معاون" {% if admin.position == 'معاون' %}selected{% endif %}>معاون</option>
                    <option value="مشاور" {% if admin.position == 'مشاور' %}selected{% endif %}>مشاور</option>
                </select>
            </div>
            
            <button type="submit" class="btn">تایید</button>
            <button type="button" class="btn" onclick="cancelEdit()" style="background: linear-gradient(45deg, #ffcc00, #ff6600); margin-top: 10px;">انصراف</button>
        </form>
        
        <button class="logout-btn" onclick="if(confirm('آیا مطمئن هستید می‌خواهید از حساب خارج شوید؟')) location.href='/admin_logout'">خروج از حساب</button>
    </div>

    <script>
        const menuToggle = document.getElementById('menuToggle');
        const menuSidebar = document.getElementById('menuSidebar');
        
        menuToggle.addEventListener('click', function() {
            menuSidebar.classList.toggle('active');
        });
        
        // Close sidebar when clicking outside
        document.addEventListener('click', function(event) {
            if (!menuSidebar.contains(event.target) && !menuToggle.contains(event.target)) {
                menuSidebar.classList.remove('active');
            }
        });
        
        function editField(field) {
            document.getElementById('editForm').style.display = 'block';
        }
        
        function cancelEdit() {
            document.getElementById('editForm').style.display = 'none';
        }
    </script>
</body>
</html>'''
}

# ایجاد فایل‌های HTML در پوشه templates
import os
if not os.path.exists('templates'):
    os.makedirs('templates')

for filename, content in templates.items():
    with open(f'templates/{filename}', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))  # استفاده از پورت 10000 در صورت عدم وجود متغیر PORT
    app.run(host='0.0.0.0', port=port, debug=True)