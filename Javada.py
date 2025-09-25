from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    grades = db.Column(db.Text)  # JSON string
    fields = db.Column(db.Text)  # JSON string
    subjects = db.Column(db.Text)  # JSON string
    password = db.Column(db.String(100), nullable=False)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    national_code = db.Column(db.String(20), unique=True, nullable=False)
    student_number = db.Column(db.String(20))
    father_phone = db.Column(db.String(20))
    mother_phone = db.Column(db.String(20))
    grade = db.Column(db.String(10), nullable=False)
    field = db.Column(db.String(20), nullable=False)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(10), nullable=False)  # 'present' or 'absent'

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    midterm1 = db.Column(db.Float)
    exam1 = db.Column(db.Float)
    midterm2 = db.Column(db.Float)
    exam2 = db.Column(db.Float)

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_type = db.Column(db.String(20), nullable=False)  # 'teacher', 'parent', 'student'
    sender_name = db.Column(db.String(200), nullable=False)
    grade = db.Column(db.String(10))
    field = db.Column(db.String(20))
    subject = db.Column(db.String(50))
    content = db.Column(db.Text, nullable=False)

# Initialize DB
def create_tables():
    with app.app_context():
        db.create_all()
        # Add default admin if not exists
        if not Admin.query.first():
            admin = Admin(
                first_name='مدیر',
                last_name='اصلی',
                role='مدیر',
                password='dabirestan012345'
            )
            db.session.add(admin)
            db.session.commit()

# Ensure tables are created before first request
@app.before_request
def ensure_tables():
    create_tables()

# Routes
@app.route('/')
def index():
    return render_template_string(index_html)

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        role = request.form['role']
        password = request.form['password']
        
        if password != 'dabirestan012345':
            return render_template_string(admin_login_html, error='رمز عبور اشتباه است')
        
        admin = Admin(first_name=first_name, last_name=last_name, role=role, password=password)
        db.session.add(admin)
        db.session.commit()
        session['admin_id'] = admin.id
        session['admin_name'] = f"{first_name} {last_name}"
        session['admin_role'] = role
        return redirect(url_for('admin_dashboard'))
    
    return render_template_string(admin_login_html)

@app.route('/teacher-login', methods=['GET', 'POST'])
def teacher_login():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        grades = [request.form[f'grade{i}'] for i in range(1, int(request.form['grade_count'])+1) if request.form[f'grade{i}']]
        fields = [request.form[f'field{i}'] for i in range(1, int(request.form['field_count'])+1) if request.form[f'field{i}']]
        subjects = [request.form[f'subject{i}'] for i in range(1, int(request.form['subject_count'])+1) if request.form[f'subject{i}']]
        password = request.form['password']
        
        if password != 'dabirjavadol':
            return render_template_string(teacher_login_html, error='رمز عبور اشتباه است')
        
        teacher = Teacher(
            first_name=first_name,
            last_name=last_name,
            grades=str(grades),
            fields=str(fields),
            subjects=str(subjects),
            password=password
        )
        db.session.add(teacher)
        db.session.commit()
        session['teacher_id'] = teacher.id
        session['teacher_name'] = f"{first_name} {last_name}"
        return redirect(url_for('teacher_dashboard'))
    
    return render_template_string(teacher_login_html)

@app.route('/admin-dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    return render_template_string(admin_dashboard_html, admin_name=session['admin_name'], admin_role=session['admin_role'])

@app.route('/teacher-dashboard')
def teacher_dashboard():
    if 'teacher_id' not in session:
        return redirect(url_for('teacher_login'))
    return render_template_string(teacher_dashboard_html, teacher_name=session['teacher_name'])

@app.route('/profile')
def profile():
    if 'admin_id' in session:
        admin = Admin.query.get(session['admin_id'])
        return render_template_string(profile_html, user=admin, user_type='admin')
    elif 'teacher_id' in session:
        teacher = Teacher.query.get(session['teacher_id'])
        return render_template_string(profile_html, user=teacher, user_type='teacher')
    else:
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/manage-students')
def manage_students():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    return render_template_string(manage_students_html)

@app.route('/students/<grade>/<field>')
def students_list(grade, field):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    students = Student.query.filter_by(grade=grade, field=field).all()
    return render_template_string(students_list_html, students=students, grade=grade, field=field)

@app.route('/add-student/<grade>/<field>', methods=['POST'])
def add_student(grade, field):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    national_code = request.form['national_code']
    student_number = request.form.get('student_number', '')
    father_phone = request.form.get('father_phone', '')
    mother_phone = request.form.get('mother_phone', '')
    
    if Student.query.filter_by(national_code=national_code).first():
        return jsonify(success=False, message='دانش‌آموز با این کد ملی وجود دارد')
    
    student = Student(
        first_name=first_name,
        last_name=last_name,
        national_code=national_code,
        student_number=student_number,
        father_phone=father_phone,
        mother_phone=mother_phone,
        grade=grade,
        field=field
    )
    db.session.add(student)
    db.session.commit()
    return jsonify(success=True)

@app.route('/delete-student/<int:student_id>')
def delete_student(student_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    return jsonify(success=True)

@app.route('/view-student/<int:student_id>')
def view_student(student_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    student = Student.query.get_or_404(student_id)
    return f'''
    <div style="background:linear-gradient(135deg, #0f0c29, #302b63, #24243e); color:white; min-height:100vh; padding:20px;">
        <h1 style="text-align:center; background:linear-gradient(45deg, #ff00cc, #00eeff); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">اطلاعات دانش آموز</h1>
        <div style="max-width:600px; margin:0 auto; background:rgba(255,255,255,0.1); padding:20px; border-radius:10px;">
            <p><strong>نام دانش آموز:</strong> {student.first_name}</p>
            <p><strong>نام خانوادگی دانش آموز:</strong> {student.last_name}</p>
            <p><strong>کد ملی دانش آموز:</strong> {student.national_code}</p>
            <p><strong>شماره دانش آموز:</strong> {student.student_number or 'ثبت نشده'}</p>
            <p><strong>شماره پدر:</strong> {student.father_phone or 'ثبت نشده'}</p>
            <p><strong>شماره مادر:</strong> {student.mother_phone or 'ثبت نشده'}</p>
            <button onclick="history.back()" style="padding:10px 20px; background:#00eeff; color:black; border:none; border-radius:5px; cursor:pointer;">بازگشت</button>
        </div>
    </div>
    '''

@app.route('/attendance')
def attendance():
    if 'teacher_id' not in session:
        return redirect(url_for('teacher_login'))
    # اینجا لیست دانش‌آموزان مربوط به معلم باید گرفته شود
    # برای مثال فرض کنیم که معلم فقط دانش‌آموزان یک پایه و رشته را می‌بیند
    students = Student.query.filter_by(grade='دهم', field='ریاضی').all()
    return render_template_string(attendance_html, students=students)

@app.route('/grades')
def grades():
    if 'teacher_id' not in session:
        return redirect(url_for('teacher_login'))
    students = Student.query.filter_by(grade='دهم', field='ریاضی').all()
    return render_template_string(grades_html, students=students)

@app.route('/reports')
def reports():
    if 'teacher_id' not in session:
        return redirect(url_for('teacher_login'))
    return render_template_string(reports_html)

@app.route('/notes')
def notes():
    if 'teacher_id' not in session:
        return redirect(url_for('teacher_login'))
    return render_template_string(notes_html)

@app.route('/exams')
def exams():
    if 'teacher_id' not in session:
        return redirect(url_for('teacher_login'))
    return render_template_string(exams_html)

# HTML Templates
index_html = '''
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>دبیرستان پسرانه جوادالائمه</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: Tahoma, sans-serif; 
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: white;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .header { 
            text-align: center; 
            margin-bottom: 40px; 
            animation: fadeInDown 1s ease;
        }
        .header h1 { 
            font-size: 2.5rem; 
            background: linear-gradient(45deg, #ff00cc, #00eeff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 10px rgba(255, 0, 204, 0.5);
            margin-bottom: 10px;
        }
        .buttons-container { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 25px;
            width: 100%;
            max-width: 800px;
        }
        .btn {
            padding: 20px;
            border-radius: 15px;
            border: none;
            cursor: pointer;
            font-size: 1.2rem;
            font-weight: bold;
            text-align: center;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
        }
        .btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(45deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
            z-index: 1;
        }
        .btn span { position: relative; z-index: 2; }
        .btn:hover { transform: translateY(-8px) scale(1.02); box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4); }
        .btn:active { transform: scale(0.98); }
        .admin-btn { background: linear-gradient(45deg, #ff00cc, #ff0066); }
        .teacher-btn { background: linear-gradient(45deg, #00eeff, #0066ff); }
        .parent-btn { background: linear-gradient(45deg, #ffcc00, #ff6600); }
        .student-btn { background: linear-gradient(45deg, #00ff99, #00cc66); }
        .footer { margin-top: 40px; text-align: center; color: rgba(255,255,255,0.6); }
        @keyframes fadeInDown {
            from { opacity: 0; transform: translateY(-30px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>به سایت رسمی دبیرستان پسرانه جوادالائمه خوش آمدید</h1>
    </div>
    <div class="buttons-container">
        <button class="btn admin-btn" onclick="location.href='/admin-login'"><span>ورود مدیران<br>این بخش فقط برای مدیران است</span></button>
        <button class="btn teacher-btn" onclick="location.href='/teacher-login'"><span>ورود معلمان<br>این بخش فقط برای معلمان است</span></button>
        <button class="btn parent-btn" onclick="location.href='#'"><span>ورود والدین<br>این بخش فقط برای والدین است</span></button>
        <button class="btn student-btn" onclick="location.href='#'"><span>ورود دانش آموزان<br>این بخش فقط برای دانش آموزان است</span></button>
    </div>
    <div class="footer">
        <p>سازنده : محمدرضا محمدی دانش آموز دبیرستان جوادالائمه (رشته ریاضی)</p>
    </div>
</body>
</html>
'''

teacher_login_html = '''
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ورود معلمان</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: Tahoma, sans-serif; 
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: white;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .form-container {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            width: 100%;
            max-width: 500px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            animation: bounceIn 0.6s ease;
        }
        .form-container h2 {
            text-align: center;
            margin-bottom: 25px;
            background: linear-gradient(45deg, #ff00cc, #00eeff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
        }
        input, select {
            width: 100%;
            padding: 12px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            background: rgba(0, 0, 0, 0.2);
            color: white;
            font-size: 1rem;
            transition: all 0.3s;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #00eeff;
            box-shadow: 0 0 10px rgba(0, 238, 255, 0.5);
            transform: scale(1.02);
        }
        .btn {
            width: 100%;
            padding: 14px;
            border-radius: 10px;
            border: none;
            background: linear-gradient(45deg, #00eeff, #0066ff);
            color: black;
            font-size: 1.1rem;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn:hover { transform: translateY(-3px); box-shadow: 0 5px 15px rgba(0, 238, 255, 0.4); }
        .error {
            color: #ff4444;
            background: rgba(255, 0, 0, 0.2);
            padding: 10px;
            border-radius: 8px;
            margin-top: 10px;
            text-align: center;
        }
        .back-btn {
            position: absolute;
            top: 20px;
            left: 20px;
            background: rgba(255, 255, 255, 0.1);
            border: none;
            color: white;
            padding: 10px 15px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 1.2rem;
        }
        @keyframes bounceIn {
            from { opacity: 0; transform: scale(0.8); }
            to { opacity: 1; transform: scale(1); }
        }
    </style>
</head>
<body>
    <button class="back-btn" onclick="location.href='/'">←</button>
    <div class="form-container">
        <h2>ورود معلمان</h2>
        <form method="POST">
            <div class="form-group">
                <label>نام</label>
                <input type="text" name="first_name" required>
            </div>
            <div class="form-group">
                <label>نام خانوادگی</label>
                <input type="text" name="last_name" required>
            </div>
            
            <div class="form-group">
                <label>تعداد پایه ها</label>
                <select name="grade_count" id="grade_count" required>
                    <option value="">انتخاب کنید</option>
                    <option value="1">1</option>
                    <option value="2">2</option>
                    <option value="3">3</option>
                </select>
            </div>
            <div id="grade_fields" style="display:none;">
                <div class="form-group">
                    <label>پایه اول</label>
                    <select name="grade1" disabled>
                        <option value="">انتخاب کنید</option>
                        <option value="دهم">دهم</option>
                        <option value="یازدهم">یازدهم</option>
                        <option value="دوازدهم">دوازدهم</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>پایه دوم</label>
                    <select name="grade2" disabled>
                        <option value="">انتخاب کنید</option>
                        <option value="دهم">دهم</option>
                        <option value="یازدهم">یازدهم</option>
                        <option value="دوازدهم">دوازدهم</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>پایه سوم</label>
                    <select name="grade3" disabled>
                        <option value="">انتخاب کنید</option>
                        <option value="دهم">دهم</option>
                        <option value="یازدهم">یازدهم</option>
                        <option value="دوازدهم">دوازدهم</option>
                    </select>
                </div>
            </div>
            
            <div class="form-group">
                <label>تعداد رشته ها</label>
                <select name="field_count" id="field_count" required>
                    <option value="">انتخاب کنید</option>
                    <option value="1">1</option>
                    <option value="2">2</option>
                    <option value="3">3</option>
                </select>
            </div>
            <div id="field_fields" style="display:none;">
                <div class="form-group">
                    <label>رشته اول</label>
                    <select name="field1" disabled>
                        <option value="">انتخاب کنید</option>
                        <option value="ریاضی">ریاضی</option>
                        <option value="تجربی">تجربی</option>
                        <option value="انسانی">انسانی</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>رشته دوم</label>
                    <select name="field2" disabled>
                        <option value="">انتخاب کنید</option>
                        <option value="ریاضی">ریاضی</option>
                        <option value="تجربی">تجربی</option>
                        <option value="انسانی">انسانی</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>رشته سوم</label>
                    <select name="field3" disabled>
                        <option value="">انتخاب کنید</option>
                        <option value="ریاضی">ریاضی</option>
                        <option value="تجربی">تجربی</option>
                        <option value="انسانی">انسانی</option>
                    </select>
                </div>
            </div>
            
            <div class="form-group">
                <label>تعداد دروس</label>
                <select name="subject_count" id="subject_count" required>
                    <option value="">انتخاب کنید</option>
                    <option value="1">1</option>
                    <option value="2">2</option>
                    <option value="3">3</option>
                    <option value="4">4</option>
                </select>
            </div>
            <div id="subject_fields" style="display:none;">
                <div class="form-group">
                    <label>درس اول</label>
                    <input type="text" name="subject1" disabled>
                </div>
                <div class="form-group">
                    <label>درس دوم</label>
                    <input type="text" name="subject2" disabled>
                </div>
                <div class="form-group">
                    <label>درس سوم</label>
                    <input type="text" name="subject3" disabled>
                </div>
                <div class="form-group">
                    <label>درس چهارم</label>
                    <input type="text" name="subject4" disabled>
                </div>
            </div>
            
            <div class="form-group">
                <label>رمز</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit" class="btn">ورود</button>
            {% if error %}
                <div class="error">{{ error }}</div>
            {% endif %}
        </form>
    </div>
    
    <script>
        document.getElementById('grade_count').addEventListener('change', function() {
            const count = parseInt(this.value);
            const fields = document.getElementById('grade_fields');
            fields.style.display = count ? 'block' : 'none';
            for(let i = 1; i <= 3; i++) {
                const field = document.querySelector(`[name="grade${i}"]`);
                field.disabled = i > count;
                if(i <= count) field.required = true;
                else field.required = false;
            }
        });
        
        document.getElementById('field_count').addEventListener('change', function() {
            const count = parseInt(this.value);
            const fields = document.getElementById('field_fields');
            fields.style.display = count ? 'block' : 'none';
            for(let i = 1; i <= 3; i++) {
                const field = document.querySelector(`[name="field${i}"]`);
                field.disabled = i > count;
                if(i <= count) field.required = true;
                else field.required = false;
            }
        });
        
        document.getElementById('subject_count').addEventListener('change', function() {
            const count = parseInt(this.value);
            const fields = document.getElementById('subject_fields');
            fields.style.display = count ? 'block' : 'none';
            for(let i = 1; i <= 4; i++) {
                const field = document.querySelector(`[name="subject${i}"]`);
                field.disabled = i > count;
                if(i <= count) field.required = true;
                else field.required = false;
            }
        });
    </script>
</body>
</html>
'''

admin_login_html = '''
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ورود مدیران</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: Tahoma, sans-serif; 
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: white;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .form-container {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            width: 100%;
            max-width: 400px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            animation: bounceIn 0.6s ease;
        }
        .form-container h2 {
            text-align: center;
            margin-bottom: 25px;
            background: linear-gradient(45deg, #ff00cc, #00eeff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
        }
        input, select {
            width: 100%;
            padding: 12px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            background: rgba(0, 0, 0, 0.2);
            color: white;
            font-size: 1rem;
            transition: all 0.3s;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #00eeff;
            box-shadow: 0 0 10px rgba(0, 238, 255, 0.5);
            transform: scale(1.02);
        }
        .btn {
            width: 100%;
            padding: 14px;
            border-radius: 10px;
            border: none;
            background: linear-gradient(45deg, #ff00cc, #ff0066);
            color: white;
            font-size: 1.1rem;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn:hover { transform: translateY(-3px); box-shadow: 0 5px 15px rgba(255, 0, 102, 0.4); }
        .error {
            color: #ff4444;
            background: rgba(255, 0, 0, 0.2);
            padding: 10px;
            border-radius: 8px;
            margin-top: 10px;
            text-align: center;
        }
        .back-btn {
            position: absolute;
            top: 20px;
            left: 20px;
            background: rgba(255, 255, 255, 0.1);
            border: none;
            color: white;
            padding: 10px 15px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 1.2rem;
        }
        @keyframes bounceIn {
            from { opacity: 0; transform: scale(0.8); }
            to { opacity: 1; transform: scale(1); }
        }
    </style>
</head>
<body>
    <button class="back-btn" onclick="location.href='/'">←</button>
    <div class="form-container">
        <h2>ورود مدیران</h2>
        <form method="POST">
            <div class="form-group">
                <label>نام</label>
                <input type="text" name="first_name" required>
            </div>
            <div class="form-group">
                <label>نام خانوادگی</label>
                <input type="text" name="last_name" required>
            </div>
            <div class="form-group">
                <label>مرتبه</label>
                <select name="role" required>
                    <option value="مدیر">مدیر</option>
                    <option value="ناظم">ناظم</option>
                    <option value="معاون">معاون</option>
                    <option value="مشاور">مشاور</option>
                </select>
            </div>
            <div class="form-group">
                <label>رمز</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit" class="btn">ورود</button>
            {% if error %}
                <div class="error">{{ error }}</div>
            {% endif %}
        </form>
    </div>
</body>
</html>
'''

admin_dashboard_html = '''
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>درگاه مدیران</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: Tahoma, sans-serif; 
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: white;
            min-height: 100vh;
            padding-top: 70px;
            padding-bottom: 60px;
        }
        .header {
            position: fixed;
            top: 0;
            width: 100%;
            background: rgba(0, 0, 0, 0.3);
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 100;
        }
        .menu-btn {
            background: none;
            border: none;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
        }
        .menu-container {
            position: fixed;
            top: 0;
            right: 0;
            width: 300px;
            height: 100%;
            background: rgba(30, 30, 60, 0.95);
            backdrop-filter: blur(10px);
            transform: translateX(100%);
            transition: transform 0.3s ease;
            z-index: 200;
            padding: 60px 20px 20px;
        }
        .menu-container.active {
            transform: translateX(0);
        }
        .menu-item {
            display: block;
            padding: 15px;
            margin: 10px 0;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            color: white;
            text-decoration: none;
            text-align: center;
            font-weight: bold;
            transition: all 0.3s;
        }
        .menu-item:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        .overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 150;
            display: none;
        }
        .overlay.active {
            display: block;
        }
        .dashboard-title {
            text-align: center;
            margin: 20px 0;
            background: linear-gradient(45deg, #ff00cc, #00eeff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 1.8rem;
        }
        .buttons-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }
        .btn {
            padding: 25px 15px;
            border-radius: 15px;
            border: none;
            cursor: pointer;
            font-size: 1.1rem;
            font-weight: bold;
            text-align: center;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
            color: white;
        }
        .btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(45deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
            z-index: 1;
        }
        .btn span { position: relative; z-index: 2; }
        .btn:hover { transform: translateY(-8px) scale(1.02); box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4); }
        .btn:active { transform: scale(0.98); }
        .students-btn { background: linear-gradient(45deg, #ff00cc, #ff0066); }
        .teachers-btn { background: linear-gradient(45deg, #00eeff, #0066ff); }
        .reports-parent-btn { background: linear-gradient(45deg, #ffcc00, #ff6600); }
        .reports-teacher-btn { background: linear-gradient(45deg, #00ff99, #00cc66); }
        .reports-student-btn { background: linear-gradient(45deg, #ff9900, #cc6600); }
        .lab-btn { background: linear-gradient(45deg, #9966ff, #6600cc); }
        .grades-btn { background: linear-gradient(45deg, #ff66cc, #cc0099); }
        .cards-btn { background: linear-gradient(45deg, #66ffcc, #00cc99); }
    </style>
</head>
<body>
    <div class="header">
        <button class="menu-btn" id="menuBtn">☰</button>
        <h2>درگاه مدیران</h2>
    </div>
    
    <div class="menu-container" id="menuContainer">
        <a href="/admin-dashboard" class="menu-item">صفحه اصلی</a>
        <a href="/profile" class="menu-item">پروفایل</a>
        <a href="#" class="menu-item">اعلانات</a>
    </div>
    
    <div class="overlay" id="overlay"></div>
    
    <h1 class="dashboard-title">خوش آمدید، {{ admin_name }} ({{ admin_role }})</h1>
    
    <div class="buttons-container">
        <button class="btn students-btn" onclick="location.href='/manage-students'"><span>مدیریت دانش آموزان</span></button>
        <button class="btn teachers-btn" onclick="location.href='/manage-teachers'"><span>مدیریت معلمان</span></button>
        <button class="btn reports-parent-btn" onclick="location.href='/manage-reports/parent'"><span>گزارشات والدین</span></button>
        <button class="btn reports-teacher-btn" onclick="location.href='/manage-reports/teacher'"><span>گزارشات معلمان</span></button>
        <button class="btn reports-student-btn" onclick="location.href='/manage-reports/student'"><span>گزارشات دانش آموزان</span></button>
        <button class="btn lab-btn" onclick="location.href='/manage-lab'"><span>مدیریت آزمایشگاه</span></button>
        <button class="btn grades-btn" onclick="location.href='/manage-grades'"><span>مدیریت نمرات</span></button>
        <button class="btn cards-btn" onclick="location.href='/manage-report-cards'"><span>مدیریت کارنامه</span></button>
    </div>
    
    <script>
        document.getElementById('menuBtn').addEventListener('click', function() {
            const menu = document.getElementById('menuContainer');
            const overlay = document.getElementById('overlay');
            menu.classList.toggle('active');
            overlay.classList.toggle('active');
        });
        
        document.getElementById('overlay').addEventListener('click', function() {
            document.getElementById('menuContainer').classList.remove('active');
            this.classList.remove('active');
        });
    </script>
</body>
</html>
'''

teacher_dashboard_html = '''
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>درگاه معلمان</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: Tahoma, sans-serif; 
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: white;
            min-height: 100vh;
            padding-top: 70px;
            padding-bottom: 60px;
        }
        .header {
            position: fixed;
            top: 0;
            width: 100%;
            background: rgba(0, 0, 0, 0.3);
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 100;
        }
        .menu-btn {
            background: none;
            border: none;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
        }
        .menu-container {
            position: fixed;
            top: 0;
            right: 0;
            width: 300px;
            height: 100%;
            background: rgba(30, 30, 60, 0.95);
            backdrop-filter: blur(10px);
            transform: translateX(100%);
            transition: transform 0.3s ease;
            z-index: 200;
            padding: 60px 20px 20px;
        }
        .menu-container.active {
            transform: translateX(0);
        }
        .menu-item {
            display: block;
            padding: 15px;
            margin: 10px 0;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            color: white;
            text-decoration: none;
            text-align: center;
            font-weight: bold;
            transition: all 0.3s;
        }
        .menu-item:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        .overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 150;
            display: none;
        }
        .overlay.active {
            display: block;
        }
        .dashboard-title {
            text-align: center;
            margin: 20px 0;
            background: linear-gradient(45deg, #00eeff, #0066ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 1.8rem;
        }
        .buttons-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }
        .btn {
            padding: 25px 15px;
            border-radius: 15px;
            border: none;
            cursor: pointer;
            font-size: 1.1rem;
            font-weight: bold;
            text-align: center;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
            color: white;
        }
        .btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(45deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
            z-index: 1;
        }
        .btn span { position: relative; z-index: 2; }
        .btn:hover { transform: translateY(-8px) scale(1.02); box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4); }
        .btn:active { transform: scale(0.98); }
        .attendance-btn { background: linear-gradient(45deg, #ff00cc, #ff0066); }
        .grades-btn { background: linear-gradient(45deg, #00eeff, #0066ff); }
        .reports-btn { background: linear-gradient(45deg, #ffcc00, #ff6600); }
        .notes-btn { background: linear-gradient(45deg, #00ff99, #00cc66); }
        .exams-btn { background: linear-gradient(45deg, #9966ff, #6600cc); }
    </style>
</head>
<body>
    <div class="header">
        <button class="menu-btn" id="menuBtn">☰</button>
        <h2>درگاه معلمان</h2>
    </div>
    
    <div class="menu-container" id="menuContainer">
        <a href="/teacher-dashboard" class="menu-item">صفحه اصلی</a>
        <a href="/profile" class="menu-item">پروفایل</a>
        <a href="#" class="menu-item">اعلانات</a>
    </div>
    
    <div class="overlay" id="overlay"></div>
    
    <h1 class="dashboard-title">خوش آمدید، {{ teacher_name }}</h1>
    
    <div class="buttons-container">
        <button class="btn attendance-btn" onclick="location.href='/attendance'"><span>حضور و غیاب</span></button>
        <button class="btn grades-btn" onclick="location.href='/grades'"><span>نمرات</span></button>
        <button class="btn reports-btn" onclick="location.href='/reports'"><span>گزارش</span></button>
        <button class="btn notes-btn" onclick="location.href='/notes'"><span>جزوه ها</span></button>
        <button class="btn exams-btn" onclick="location.href='/exams'"><span>تکالیف و امتحانات</span></button>
    </div>
    
    <script>
        document.getElementById('menuBtn').addEventListener('click', function() {
            const menu = document.getElementById('menuContainer');
            const overlay = document.getElementById('overlay');
            menu.classList.toggle('active');
            overlay.classList.toggle('active');
        });
        
        document.getElementById('overlay').addEventListener('click', function() {
            document.getElementById('menuContainer').classList.remove('active');
            this.classList.remove('active');
        });
    </script>
</body>
</html>
'''

profile_html = '''
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>پروفایل</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: Tahoma, sans-serif; 
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: white;
            min-height: 100vh;
            padding-top: 70px;
            padding-bottom: 60px;
        }
        .header {
            position: fixed;
            top: 0;
            width: 100%;
            background: rgba(0, 0, 0, 0.3);
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 100;
        }
        .menu-btn {
            background: none;
            border: none;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
        }
        .menu-container {
            position: fixed;
            top: 0;
            right: 0;
            width: 300px;
            height: 100%;
            background: rgba(30, 30, 60, 0.95);
            backdrop-filter: blur(10px);
            transform: translateX(100%);
            transition: transform 0.3s ease;
            z-index: 200;
            padding: 60px 20px 20px;
        }
        .menu-container.active {
            transform: translateX(0);
        }
        .menu-item {
            display: block;
            padding: 15px;
            margin: 10px 0;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            color: white;
            text-decoration: none;
            text-align: center;
            font-weight: bold;
            transition: all 0.3s;
        }
        .menu-item:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        .overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 150;
            display: none;
        }
        .overlay.active {
            display: block;
        }
        .profile-title {
            text-align: center;
            margin: 20px 0;
            background: linear-gradient(45deg, #ff00cc, #00eeff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 1.8rem;
        }
        .profile-container {
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        .profile-field {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            margin: 10px 0;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
        }
        .field-label {
            font-weight: bold;
        }
        .field-value {
            flex: 1;
            padding: 0 10px;
        }
        .edit-btn {
            background: #ffcc00;
            border: none;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            cursor: pointer;
            font-weight: bold;
        }
        .edit-input {
            width: 100%;
            padding: 8px;
            border-radius: 5px;
            border: 1px solid #555;
            background: rgba(0, 0, 0, 0.3);
            color: white;
        }
        .action-buttons {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-top: 20px;
        }
        .action-btn {
            padding: 10px 20px;
            border-radius: 5px;
            border: none;
            cursor: pointer;
            font-weight: bold;
        }
        .confirm-btn { background: #00ff99; color: black; }
        .cancel-btn { background: #ff4444; color: white; }
        .logout-btn {
            display: block;
            width: 200px;
            margin: 30px auto;
            padding: 15px;
            background: #ff0066;
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1.1rem;
            font-weight: bold;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="header">
        <button class="menu-btn" id="menuBtn">☰</button>
        <h2>پروفایل</h2>
    </div>
    
    <div class="menu-container" id="menuContainer">
        <a href="/teacher-dashboard" class="menu-item">صفحه اصلی</a>
        <a href="/profile" class="menu-item">پروفایل</a>
        <a href="#" class="menu-item">اعلانات</a>
    </div>
    
    <div class="overlay" id="overlay"></div>
    
    <h1 class="profile-title">اطلاعات شخصی</h1>
    
    <div class="profile-container">
        <div class="profile-field">
            <span class="field-label">نام:</span>
            <span class="field-value" id="first_name">{{ user.first_name }}</span>
            <button class="edit-btn" onclick="editField('first_name')">✎</button>
        </div>
        <div class="profile-field">
            <span class="field-label">نام خانوادگی:</span>
            <span class="field-value" id="last_name">{{ user.last_name }}</span>
            <button class="edit-btn" onclick="editField('last_name')">✎</button>
        </div>
        <div class="profile-field">
            <span class="field-label">مرتبه:</span>
            <span class="field-value">معلم</span>
        </div>
        <div class="profile-field">
            <span class="field-label">پایه ها:</span>
            <span class="field-value" id="grades">{{ user.grades }}</span>
            <button class="edit-btn" onclick="editField('grades')">✎</button>
        </div>
        <div class="profile-field">
            <span class="field-label">رشته ها:</span>
            <span class="field-value" id="fields">{{ user.fields }}</span>
            <button class="edit-btn" onclick="editField('fields')">✎</button>
        </div>
        <div class="profile-field">
            <span class="field-label">درس ها:</span>
            <span class="field-value" id="subjects">{{ user.subjects }}</span>
            <button class="edit-btn" onclick="editField('subjects')">✎</button>
        </div>
        <div class="profile-field">
            <span class="field-label">رمز:</span>
            <span class="field-value">••••••••</span>
        </div>
    </div>
    
    <button class="logout-btn" onclick="logout()">خروج از حساب</button>
    
    <script>
        function editField(field) {
            const span = document.getElementById(field);
            const currentValue = span.textContent;
            span.innerHTML = `<input type="text" class="edit-input" id="input_${field}" value="${currentValue}">`;
            
            const input = document.getElementById(`input_${field}`);
            input.focus();
            
            const editBtn = span.nextElementSibling;
            editBtn.innerHTML = '✓';
            editBtn.onclick = function() { confirmEdit(field); };
        }
        
        function confirmEdit(field) {
            const input = document.getElementById(`input_${field}`);
            const newValue = input.value;
            
            // In a real app, you would send this to the server
            const span = document.getElementById(field);
            span.textContent = newValue;
            
            const editBtn = span.nextElementSibling;
            editBtn.innerHTML = '✎';
            editBtn.onclick = function() { editField(field); };
        }
        
        function logout() {
            if(confirm('آیا مطمئن هستید می‌خواهید از حساب خارج شوید؟')) {
                location.href = '/logout';
            }
        }
        
        document.getElementById('menuBtn').addEventListener('click', function() {
            const menu = document.getElementById('menuContainer');
            const overlay = document.getElementById('overlay');
            menu.classList.toggle('active');
            overlay.classList.toggle('active');
        });
        
        document.getElementById('overlay').addEventListener('click', function() {
            document.getElementById('menuContainer').classList.remove('active');
            this.classList.remove('active');
        });
    </script>
</body>
</html>
'''

manage_students_html = '''
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مدیریت دانش آموزان</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: Tahoma, sans-serif; 
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: white;
            min-height: 100vh;
            padding-top: 70px;
            padding-bottom: 60px;
        }
        .header {
            position: fixed;
            top: 0;
            width: 100%;
            background: rgba(0, 0, 0, 0.3);
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 100;
        }
        .menu-btn {
            background: none;
            border: none;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
        }
        .menu-container {
            position: fixed;
            top: 0;
            right: 0;
            width: 300px;
            height: 100%;
            background: rgba(30, 30, 60, 0.95);
            backdrop-filter: blur(10px);
            transform: translateX(100%);
            transition: transform 0.3s ease;
            z-index: 200;
            padding: 60px 20px 20px;
        }
        .menu-container.active {
            transform: translateX(0);
        }
        .menu-item {
            display: block;
            padding: 15px;
            margin: 10px 0;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            color: white;
            text-decoration: none;
            text-align: center;
            font-weight: bold;
            transition: all 0.3s;
        }
        .menu-item:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        .overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 150;
            display: none;
        }
        .overlay.active {
            display: block;
        }
        .section-title {
            text-align: center;
            margin: 20px 0;
            background: linear-gradient(45deg, #ff00cc, #00eeff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 1.8rem;
        }
        .grade-buttons {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin: 20px 0;
            flex-wrap: wrap;
        }
        .btn {
            padding: 15px 25px;
            border-radius: 10px;
            border: none;
            cursor: pointer;
            font-size: 1rem;
            font-weight: bold;
            text-align: center;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
            color: white;
        }
        .btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(45deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
            z-index: 1;
        }
        .btn span { position: relative; z-index: 2; }
        .btn:hover { transform: translateY(-5px) scale(1.05); box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4); }
        .btn:active { transform: scale(0.98); }
        .grade-btn { background: linear-gradient(45deg, #ff00cc, #ff0066); }
        .field-btn { background: linear-gradient(45deg, #00eeff, #0066ff); }
        .students-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .student-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 15px;
            margin: 15px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s;
            cursor: pointer;
        }
        .student-card:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-3px);
        }
        .student-info {
            flex: 1;
        }
        .student-name {
            font-weight: bold;
            font-size: 1.1rem;
        }
        .student-national {
            color: #aaa;
            font-size: 0.9rem;
        }
        .student-actions {
            display: flex;
            gap: 10px;
        }
        .action-btn {
            width: 35px;
            height: 35px;
            border-radius: 50%;
            border: none;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s;
        }
        .edit-btn { background: #ffcc00; color: black; }
        .delete-btn { background: #ff4444; color: white; }
        .add-btn {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            border: none;
            background: #00eeff;
            color: black;
            font-size: 2rem;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
            transition: all 0.3s;
        }
        .add-btn:hover {
            transform: scale(1.1);
            box-shadow: 0 8px 20px rgba(0, 238, 255, 0.5);
        }
        .search-container {
            display: flex;
            justify-content: center;
            margin: 20px 0;
            padding: 0 20px;
        }
        .search-box {
            width: 100%;
            max-width: 500px;
            padding: 12px 15px;
            border-radius: 30px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            background: rgba(0, 0, 0, 0.2);
            color: white;
            font-size: 1rem;
        }
        .search-btn {
            margin-right: 10px;
            padding: 12px 20px;
            border-radius: 30px;
            border: none;
            background: #00eeff;
            color: black;
            font-weight: bold;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="header">
        <button class="menu-btn" id="menuBtn">☰</button>
        <h2>مدیریت دانش آموزان</h2>
    </div>
    
    <div class="menu-container" id="menuContainer">
        <a href="/admin-dashboard" class="menu-item">صفحه اصلی</a>
        <a href="/profile" class="menu-item">پروفایل</a>
        <a href="#" class="menu-item">اعلانات</a>
    </div>
    
    <div class="overlay" id="overlay"></div>
    
    <h1 class="section-title">پایه‌ها</h1>
    <div class="grade-buttons">
        <button class="btn grade-btn" onclick="location.href='/students/دهم/ریاضی'"><span>پایه دهم</span></button>
        <button class="btn grade-btn" onclick="location.href='/students/یازدهم/ریاضی'"><span>پایه یازدهم</span></button>
        <button class="btn grade-btn" onclick="location.href='/students/دوازدهم/ریاضی'"><span>پایه دوازدهم</span></button>
    </div>
    
    <script>
        document.getElementById('menuBtn').addEventListener('click', function() {
            const menu = document.getElementById('menuContainer');
            const overlay = document.getElementById('overlay');
            menu.classList.toggle('active');
            overlay.classList.toggle('active');
        });
        
        document.getElementById('overlay').addEventListener('click', function() {
            document.getElementById('menuContainer').classList.remove('active');
            this.classList.remove('active');
        });
    </script>
</body>
</html>
'''

students_list_html = '''
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>دانش آموزان {{ grade }} {{ field }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: Tahoma, sans-serif; 
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: white;
            min-height: 100vh;
            padding-top: 70px;
            padding-bottom: 60px;
        }
        .header {
            position: fixed;
            top: 0;
            width: 100%;
            background: rgba(0, 0, 0, 0.3);
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 100;
        }
        .menu-btn {
            background: none;
            border: none;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
        }
        .menu-container {
            position: fixed;
            top: 0;
            right: 0;
            width: 300px;
            height: 100%;
            background: rgba(30, 30, 60, 0.95);
            backdrop-filter: blur(10px);
            transform: translateX(100%);
            transition: transform 0.3s ease;
            z-index: 200;
            padding: 60px 20px 20px;
        }
        .menu-container.active {
            transform: translateX(0);
        }
        .menu-item {
            display: block;
            padding: 15px;
            margin: 10px 0;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            color: white;
            text-decoration: none;
            text-align: center;
            font-weight: bold;
            transition: all 0.3s;
        }
        .menu-item:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        .overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 150;
            display: none;
        }
        .overlay.active {
            display: block;
        }
        .section-title {
            text-align: center;
            margin: 20px 0;
            background: linear-gradient(45deg, #ff00cc, #00eeff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 1.8rem;
        }
        .field-buttons {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin: 20px 0;
            flex-wrap: wrap;
        }
        .btn {
            padding: 15px 25px;
            border-radius: 10px;
            border: none;
            cursor: pointer;
            font-size: 1rem;
            font-weight: bold;
            text-align: center;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
            color: white;
        }
        .btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(45deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
            z-index: 1;
        }
        .btn span { position: relative; z-index: 2; }
        .btn:hover { transform: translateY(-5px) scale(1.05); box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4); }
        .btn:active { transform: scale(0.98); }
        .field-btn { background: linear-gradient(45deg, #ff00cc, #ff0066); }
        .students-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .student-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 15px;
            margin: 15px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s;
            cursor: pointer;
        }
        .student-card:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-3px);
        }
        .student-info {
            flex: 1;
        }
        .student-name {
            font-weight: bold;
            font-size: 1.1rem;
        }
        .student-national {
            color: #aaa;
            font-size: 0.9rem;
        }
        .student-actions {
            display: flex;
            gap: 10px;
        }
        .action-btn {
            width: 35px;
            height: 35px;
            border-radius: 50%;
            border: none;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s;
        }
        .edit-btn { background: #ffcc00; color: black; }
        .delete-btn { background: #ff4444; color: white; }
        .add-btn {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            border: none;
            background: #00eeff;
            color: black;
            font-size: 2rem;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
            transition: all 0.3s;
        }
        .add-btn:hover {
            transform: scale(1.1);
            box-shadow: 0 8px 20px rgba(0, 238, 255, 0.5);
        }
        .search-container {
            display: flex;
            justify-content: center;
            margin: 20px 0;
            padding: 0 20px;
        }
        .search-box {
            width: 100%;
            max-width: 500px;
            padding: 12px 15px;
            border-radius: 30px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            background: rgba(0, 0, 0, 0.2);
            color: white;
            font-size: 1rem;
        }
        .search-btn {
            margin-right: 10px;
            padding: 12px 20px;
            border-radius: 30px;
            border: none;
            background: #00eeff;
            color: black;
            font-weight: bold;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="header">
        <button class="menu-btn" id="menuBtn">☰</button>
        <h2>دانش آموزان {{ grade }} {{ field }}</h2>
    </div>
    
    <div class="menu-container" id="menuContainer">
        <a href="/admin-dashboard" class="menu-item">صفحه اصلی</a>
        <a href="/profile" class="menu-item">پروفایل</a>
        <a href="#" class="menu-item">اعلانات</a>
    </div>
    
    <div class="overlay" id="overlay"></div>
    
    <h1 class="section-title">رشته‌ها</h1>
    <div class="field-buttons">
        <button class="btn field-btn" onclick="location.href='/students/{{ grade }}/ریاضی'"><span>ریاضی</span></button>
        <button class="btn field-btn" onclick="location.href='/students/{{ grade }}/تجربی'"><span>تجربی</span></button>
        <button class="btn field-btn" onclick="location.href='/students/{{ grade }}/انسانی'"><span>انسانی</span></button>
    </div>
    
    <div class="search-container">
        <input type="text" class="search-box" placeholder="جستجوی نام، نام خانوادگی یا کد ملی...">
        <button class="search-btn">جستجو</button>
    </div>
    
    <div class="students-container">
        {% for student in students %}
        <div class="student-card" onclick="location.href='/view-student/{{ student.id }}'">
            <div class="student-info">
                <div class="student-name">{{ student.first_name }} {{ student.last_name }}</div>
                <div class="student-national">{{ student.national_code }}</div>
            </div>
            <div class="student-actions">
                <button class="action-btn edit-btn" onclick="event.stopPropagation(); editStudent({{ student.id }})">✎</button>
                <button class="action-btn delete-btn" onclick="event.stopPropagation(); deleteStudent({{ student.id }})">🗑</button>
            </div>
        </div>
        {% endfor %}
    </div>
    
    <button class="add-btn" onclick="showAddForm()">+</button>
    
    <div id="addForm" style="display:none; position:fixed; top:50%; left:50%; transform:translate(-50%,-50%); background:rgba(0,0,0,0.8); padding:20px; border-radius:10px; z-index:300; width:90%; max-width:500px;">
        <h3>افزودن دانش آموز</h3>
        <form id="studentForm">
            <div style="margin-bottom:15px;">
                <label>نام دانش آموز (اجباری)</label>
                <input type="text" name="first_name" required style="width:100%; padding:10px; border-radius:5px; border:1px solid #555; background:rgba(0,0,0,0.5); color:white;">
            </div>
            <div style="margin-bottom:15px;">
                <label>نام خانوادگی دانش آموز (اجباری)</label>
                <input type="text" name="last_name" required style="width:100%; padding:10px; border-radius:5px; border:1px solid #555; background:rgba(0,0,0,0.5); color:white;">
            </div>
            <div style="margin-bottom:15px;">
                <label>کد ملی دانش آموز (اجباری)</label>
                <input type="text" name="national_code" required style="width:100%; padding:10px; border-radius:5px; border:1px solid #555; background:rgba(0,0,0,0.5); color:white;">
            </div>
            <div style="margin-bottom:15px;">
                <label>شماره دانش آموز (اختیاری)</label>
                <input type="text" name="student_number" style="width:100%; padding:10px; border-radius:5px; border:1px solid #555; background:rgba(0,0,0,0.5); color:white;">
            </div>
            <div style="margin-bottom:15px;">
                <label>شماره پدر (اختیاری)</label>
                <input type="text" name="father_phone" style="width:100%; padding:10px; border-radius:5px; border:1px solid #555; background:rgba(0,0,0,0.5); color:white;">
            </div>
            <div style="margin-bottom:15px;">
                <label>شماره مادر (اختیاری)</label>
                <input type="text" name="mother_phone" style="width:100%; padding:10px; border-radius:5px; border:1px solid #555; background:rgba(0,0,0,0.5); color:white;">
            </div>
            <div style="display:flex; justify-content:space-between;">
                <button type="button" onclick="hideAddForm()">انصراف</button>
                <button type="submit">تایید</button>
            </div>
        </form>
    </div>
    
    <script>
        document.getElementById('menuBtn').addEventListener('click', function() {
            const menu = document.getElementById('menuContainer');
            const overlay = document.getElementById('overlay');
            menu.classList.toggle('active');
            overlay.classList.toggle('active');
        });
        
        document.getElementById('overlay').addEventListener('click', function() {
            document.getElementById('menuContainer').classList.remove('active');
            this.classList.remove('active');
        });
        
        function showAddForm() {
            document.getElementById('addForm').style.display = 'block';
            document.getElementById('studentForm').onsubmit = function(e) {
                e.preventDefault();
                const formData = new FormData(this);
                fetch('/add-student/{{ grade }}/{{ field }}', {
                    method: 'POST',
                    body: new URLSearchParams(new FormData(this))
                })
                .then(response => response.json())
                .then(data => {
                    if(data.success) {
                        alert('دانش آموز با موفقیت اضافه شد');
                        location.reload();
                    } else {
                        alert(data.message);
                    }
                });
            };
        }
        
        function hideAddForm() {
            document.getElementById('addForm').style.display = 'none';
        }
        
        function deleteStudent(id) {
            if(confirm('آیا مطمئن هستید می‌خواهید اطلاعات دانش آموز را پاک کنید؟')) {
                fetch('/delete-student/' + id)
                .then(response => response.json())
                .then(data => {
                    if(data.success) location.reload();
                });
            }
        }
        
        function editStudent(id) {
            alert('ویرایش دانش آموز ' + id);
            // در نسخه کامل این قسمت اجرا می‌شود
        }
    </script>
</body>
</html>
'''

attendance_html = '''
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>حضور و غیاب</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: Tahoma, sans-serif; 
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: white;
            min-height: 100vh;
            padding-top: 70px;
            padding-bottom: 60px;
        }
        .header {
            position: fixed;
            top: 0;
            width: 100%;
            background: rgba(0, 0, 0, 0.3);
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 100;
        }
        .menu-btn {
            background: none;
            border: none;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
        }
        .menu-container {
            position: fixed;
            top: 0;
            right: 0;
            width: 300px;
            height: 100%;
            background: rgba(30, 30, 60, 0.95);
            backdrop-filter: blur(10px);
            transform: translateX(100%);
            transition: transform 0.3s ease;
            z-index: 200;
            padding: 60px 20px 20px;
        }
        .menu-container.active {
            transform: translateX(0);
        }
        .menu-item {
            display: block;
            padding: 15px;
            margin: 10px 0;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            color: white;
            text-decoration: none;
            text-align: center;
            font-weight: bold;
            transition: all 0.3s;
        }
        .menu-item:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        .overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 150;
            display: none;
        }
        .overlay.active {
            display: block;
        }
        .section-title {
            text-align: center;
            margin: 20px 0;
            background: linear-gradient(45deg, #ff00cc, #00eeff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 1.8rem;
        }
        .attendance-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .student-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 15px;
            margin: 15px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s;
        }
        .student-info {
            flex: 1;
        }
        .student-name {
            font-weight: bold;
            font-size: 1.1rem;
        }
        .student-national {
            color: #aaa;
            font-size: 0.9rem;
        }
        .attendance-actions {
            display: flex;
            gap: 10px;
        }
        .absent-btn, .present-btn {
            width: 35px;
            height: 35px;
            border-radius: 50%;
            border: none;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s;
        }
        .absent-btn { background: #ff4444; color: white; }
        .absent-btn.active { background: #ff0000; }
        .present-btn { background: #00ff99; color: black; }
        .present-btn.active { background: #00cc77; }
        .summary {
            display: flex;
            justify-content: space-between;
            margin: 20px 0;
            padding: 10px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
        }
        .absent-count { color: #ff4444; font-weight: bold; }
        .present-count { color: #00ff99; font-weight: bold; }
        .actions {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 30px;
        }
        .action-btn {
            padding: 12px 30px;
            border-radius: 10px;
            border: none;
            font-size: 1.1rem;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }
        .submit-btn { background: linear-gradient(45deg, #00eeff, #0066ff); color: black; }
        .clear-btn { background: linear-gradient(45deg, #ffcc00, #ff6600); color: black; }
    </style>
</head>
<body>
    <div class="header">
        <button class="menu-btn" id="menuBtn">☰</button>
        <h2>حضور و غیاب</h2>
    </div>
    
    <div class="menu-container" id="menuContainer">
        <a href="/teacher-dashboard" class="menu-item">صفحه اصلی</a>
        <a href="/profile" class="menu-item">پروفایل</a>
        <a href="#" class="menu-item">اعلانات</a>
    </div>
    
    <div class="overlay" id="overlay"></div>
    
    <h1 class="section-title">دانش آموزان</h1>
    
    <div class="summary">
        <div class="absent-count">غائب: <span id="absent-count">0</span></div>
        <div class="present-count">حاضر: <span id="present-count">0</span></div>
    </div>
    
    <div class="attendance-container">
        {% for student in students %}
        <div class="student-card">
            <div class="student-info">
                <div class="student-name">{{ student.first_name }} {{ student.last_name }}</div>
                <div class="student-national">{{ student.national_code }}</div>
            </div>
            <div class="attendance-actions">
                <button class="absent-btn" onclick="toggleStatus(this, 'absent')">X</button>
                <button class="present-btn" onclick="toggleStatus(this, 'present')">O</button>
            </div>
        </div>
        {% endfor %}
    </div>
    
    <div class="actions">
        <button class="action-btn submit-btn" onclick="submitAttendance()">ارسال فرم حضور و غیاب</button>
        <button class="action-btn clear-btn" onclick="clearSelections()">پاک کردن انتخاب شدگان</button>
    </div>
    
    <script>
        document.getElementById('menuBtn').addEventListener('click', function() {
            const menu = document.getElementById('menuContainer');
            const overlay = document.getElementById('overlay');
            menu.classList.toggle('active');
            overlay.classList.toggle('active');
        });
        
        document.getElementById('overlay').addEventListener('click', function() {
            document.getElementById('menuContainer').classList.remove('active');
            this.classList.remove('active');
        });
        
        function toggleStatus(btn, status) {
            const parent = btn.parentElement;
            const absentBtn = parent.querySelector('.absent-btn');
            const presentBtn = parent.querySelector('.present-btn');
            
            if (status === 'absent') {
                absentBtn.classList.toggle('active');
                if (absentBtn.classList.contains('active')) {
                    presentBtn.classList.remove('active');
                }
            } else {
                presentBtn.classList.toggle('active');
                if (presentBtn.classList.contains('active')) {
                    absentBtn.classList.remove('active');
                }
            }
            
            updateCount();
        }
        
        function updateCount() {
            const absentCount = document.querySelectorAll('.absent-btn.active').length;
            const presentCount = document.querySelectorAll('.present-btn.active').length;
            document.getElementById('absent-count').textContent = absentCount;
            document.getElementById('present-count').textContent = presentCount;
        }
        
        function clearSelections() {
            if(confirm('آیا مطمئن هستید می‌خواهید انتخاب شدگان را پاک کنید؟')) {
                document.querySelectorAll('.absent-btn').forEach(btn => btn.classList.remove('active'));
                document.querySelectorAll('.present-btn').forEach(btn => btn.classList.remove('active'));
                updateCount();
            }
        }
        
        function submitAttendance() {
            alert('فرم حضور و غیاب ارسال شد');
            // در نسخه کامل، این اطلاعات به سرور ارسال می‌شوند
        }
    </script>
</body>
</html>
'''

grades_html = '''
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ثبت نمرات</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: Tahoma, sans-serif; 
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: white;
            min-height: 100vh;
            padding-top: 70px;
            padding-bottom: 60px;
        }
        .header {
            position: fixed;
            top: 0;
            width: 100%;
            background: rgba(0, 0, 0, 0.3);
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 100;
        }
        .menu-btn {
            background: none;
            border: none;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
        }
        .menu-container {
            position: fixed;
            top: 0;
            right: 0;
            width: 300px;
            height: 100%;
            background: rgba(30, 30, 60, 0.95);
            backdrop-filter: blur(10px);
            transform: translateX(100%);
            transition: transform 0.3s ease;
            z-index: 200;
            padding: 60px 20px 20px;
        }
        .menu-container.active {
            transform: translateX(0);
        }
        .menu-item {
            display: block;
            padding: 15px;
            margin: 10px 0;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            color: white;
            text-decoration: none;
            text-align: center;
            font-weight: bold;
            transition: all 0.3s;
        }
        .menu-item:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        .overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 150;
            display: none;
        }
        .overlay.active {
            display: block;
        }
        .section-title {
            text-align: center;
            margin: 20px 0;
            background: linear-gradient(45deg, #ff00cc, #00eeff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 1.8rem;
        }
        .grades-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .student-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 15px;
            margin: 15px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s;
        }
        .student-info {
            flex: 1;
        }
        .student-name {
            font-weight: bold;
            font-size: 1.1rem;
        }
        .grades-inputs {
            display: flex;
            gap: 10px;
        }
        .grade-input {
            width: 60px;
            padding: 8px;
            border-radius: 5px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            background: rgba(0, 0, 0, 0.2);
            color: white;
            text-align: center;
        }
        .action-btn {
            padding: 10px 20px;
            border-radius: 5px;
            border: none;
            font-weight: bold;
            cursor: pointer;
            margin-top: 10px;
        }
        .submit-btn { background: #00eeff; color: black; }
    </style>
</head>
<body>
    <div class="header">
        <button class="menu-btn" id="menuBtn">☰</button>
        <h2>ثبت نمرات</h2>
    </div>
    
    <div class="menu-container" id="menuContainer">
        <a href="/teacher-dashboard" class="menu-item">صفحه اصلی</a>
        <a href="/profile" class="menu-item">پروفایل</a>
        <a href="#" class="menu-item">اعلانات</a>
    </div>
    
    <div class="overlay" id="overlay"></div>
    
    <h1 class="section-title">دانش آموزان</h1>
    
    <div class="grades-container">
        {% for student in students %}
        <div class="student-card">
            <div class="student-info">
                <div class="student-name">{{ student.first_name }} {{ student.last_name }}</div>
            </div>
            <div class="grades-inputs">
                <input type="number" class="grade-input" placeholder="میان ترم اول" min="0" max="20" step="0.01">
                <input type="number" class="grade-input" placeholder="نوبت اول" min="0" max="20" step="0.01">
                <input type="number" class="grade-input" placeholder="میان ترم دوم" min="0" max="20" step="0.01">
                <input type="number" class="grade-input" placeholder="نوبت دوم" min="0" max="20" step="0.01">
            </div>
        </div>
        {% endfor %}
        <button class="action-btn submit-btn" onclick="submitGrades()">ثبت نمرات</button>
    </div>
    
    <script>
        document.getElementById('menuBtn').addEventListener('click', function() {
            const menu = document.getElementById('menuContainer');
            const overlay = document.getElementById('overlay');
            menu.classList.toggle('active');
            overlay.classList.toggle('active');
        });
        
        document.getElementById('overlay').addEventListener('click', function() {
            document.getElementById('menuContainer').classList.remove('active');
            this.classList.remove('active');
        });
        
        function submitGrades() {
            alert('نمرات با موفقیت ثبت شدند');
            // در نسخه کامل، این اطلاعات به سرور ارسال می‌شوند
        }
    </script>
</body>
</html>
'''

reports_html = '''
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>گزارش</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: Tahoma, sans-serif; 
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: white;
            min-height: 100vh;
            padding-top: 70px;
            padding-bottom: 60px;
        }
        .header {
            position: fixed;
            top: 0;
            width: 100%;
            background: rgba(0, 0, 0, 0.3);
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 100;
        }
        .menu-btn {
            background: none;
            border: none;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
        }
        .menu-container {
            position: fixed;
            top: 0;
            right: 0;
            width: 300px;
            height: 100%;
            background: rgba(30, 30, 60, 0.95);
            backdrop-filter: blur(10px);
            transform: translateX(100%);
            transition: transform 0.3s ease;
            z-index: 200;
            padding: 60px 20px 20px;
        }
        .menu-container.active {
            transform: translateX(0);
        }
        .menu-item {
            display: block;
            padding: 15px;
            margin: 10px 0;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            color: white;
            text-decoration: none;
            text-align: center;
            font-weight: bold;
            transition: all 0.3s;
        }
        .menu-item:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        .overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 150;
            display: none;
        }
        .overlay.active {
            display: block;
        }
        .section-title {
            text-align: center;
            margin: 20px 0;
            background: linear-gradient(45deg, #ff00cc, #00eeff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 1.8rem;
        }
        .report-container {
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        .report-text {
            width: 100%;
            height: 150px;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            background: rgba(0, 0, 0, 0.2);
            color: white;
            font-size: 1rem;
            margin-bottom: 20px;
        }
        .submit-btn {
            padding: 12px 30px;
            border-radius: 10px;
            border: none;
            font-size: 1.1rem;
            font-weight: bold;
            background: linear-gradient(45deg, #00eeff, #0066ff);
            color: black;
            cursor: pointer;
            display: block;
            margin: 0 auto;
        }
    </style>
</head>
<body>
    <div class="header">
        <button class="menu-btn" id="menuBtn">☰</button>
        <h2>گزارش</h2>
    </div>
    
    <div class="menu-container" id="menuContainer">
        <a href="/teacher-dashboard" class="menu-item">صفحه اصلی</a>
        <a href="/profile" class="menu-item">پروفایل</a>
        <a href="#" class="menu-item">اعلانات</a>
    </div>
    
    <div class="overlay" id="overlay"></div>
    
    <h1 class="section-title">گزارش</h1>
    
    <div class="report-container">
        <p>چه گزارشی برای مدیر می‌خواهید ارسال کنید؟</p>
        <textarea class="report-text" placeholder="متن گزارش را وارد کنید..."></textarea>
        <button class="submit-btn" onclick="submitReport()">تایید</button>
    </div>
    
    <script>
        document.getElementById('menuBtn').addEventListener('click', function() {
            const menu = document.getElementById('menuContainer');
            const overlay = document.getElementById('overlay');
            menu.classList.toggle('active');
            overlay.classList.toggle('active');
        });
        
        document.getElementById('overlay').addEventListener('click', function() {
            document.getElementById('menuContainer').classList.remove('active');
            this.classList.remove('active');
        });
        
        function submitReport() {
            const text = document.querySelector('.report-text').value;
            if(text.trim() === '') {
                alert('لطفاً متن گزارش را وارد کنید');
                return;
            }
            alert('گزارش با موفقیت ارسال شد');
            // در نسخه کامل، این اطلاعات به سرور ارسال می‌شوند
        }
    </script>
</body>
</html>
'''

notes_html = '''
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>جزوه ها</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: Tahoma, sans-serif; 
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: white;
            min-height: 100vh;
            padding-top: 70px;
            padding-bottom: 60px;
        }
        .header {
            position: fixed;
            top: 0;
            width: 100%;
            background: rgba(0, 0, 0, 0.3);
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 100;
        }
        .menu-btn {
            background: none;
            border: none;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
        }
        .menu-container {
            position: fixed;
            top: 0;
            right: 0;
            width: 300px;
            height: 100%;
            background: rgba(30, 30, 60, 0.95);
            backdrop-filter: blur(10px);
            transform: translateX(100%);
            transition: transform 0.3s ease;
            z-index: 200;
            padding: 60px 20px 20px;
        }
        .menu-container.active {
            transform: translateX(0);
        }
        .menu-item {
            display: block;
            padding: 15px;
            margin: 10px 0;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            color: white;
            text-decoration: none;
            text-align: center;
            font-weight: bold;
            transition: all 0.3s;
        }
        .menu-item:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        .overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 150;
            display: none;
        }
        .overlay.active {
            display: block;
        }
        .section-title {
            text-align: center;
            margin: 20px 0;
            background: linear-gradient(45deg, #ff00cc, #00eeff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 1.8rem;
        }
        .notes-container {
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        .upload-area {
            border: 2px dashed rgba(255, 255, 255, 0.3);
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            margin-bottom: 20px;
            cursor: pointer;
        }
        .upload-area:hover {
            border-color: #00eeff;
        }
        .upload-icon {
            font-size: 3rem;
            margin-bottom: 10px;
        }
        .notes-text {
            width: 100%;
            height: 100px;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            background: rgba(0, 0, 0, 0.2);
            color: white;
            font-size: 1rem;
            margin-bottom: 20px;
        }
        .submit-btn {
            padding: 12px 30px;
            border-radius: 10px;
            border: none;
            font-size: 1.1rem;
            font-weight: bold;
            background: linear-gradient(45deg, #00eeff, #0066ff);
            color: black;
            cursor: pointer;
            display: block;
            margin: 0 auto;
        }
    </style>
</head>
<body>
    <div class="header">
        <button class="menu-btn" id="menuBtn">☰</button>
        <h2>جزوه ها</h2>
    </div>
    
    <div class="menu-container" id="menuContainer">
        <a href="/teacher-dashboard" class="menu-item">صفحه اصلی</a>
        <a href="/profile" class="menu-item">پروفایل</a>
        <a href="#" class="menu-item">اعلانات</a>
    </div>
    
    <div class="overlay" id="overlay"></div>
    
    <h1 class="section-title">جزوه</h1>
    
    <div class="notes-container">
        <div class="upload-area" onclick="document.getElementById('fileInput').click()">
            <div class="upload-icon">+</div>
            <p>فایل جزوه را انتخاب کنید (Word, PDF, ZIP, RAR)</p>
            <input type="file" id="fileInput" style="display:none;" multiple>
        </div>
        <textarea class="notes-text" placeholder="توضیحات (اختیاری)"></textarea>
        <button class="submit-btn" onclick="submitNotes()">تایید</button>
    </div>
    
    <script>
        document.getElementById('menuBtn').addEventListener('click', function() {
            const menu = document.getElementById('menuContainer');
            const overlay = document.getElementById('overlay');
            menu.classList.toggle('active');
            overlay.classList.toggle('active');
        });
        
        document.getElementById('overlay').addEventListener('click', function() {
            document.getElementById('menuContainer').classList.remove('active');
            this.classList.remove('active');
        });
        
        function submitNotes() {
            alert('جزوه با موفقیت ارسال شد');
            // در نسخه کامل، این اطلاعات به سرور ارسال می‌شوند
        }
    </script>
</body>
</html>
'''

exams_html = '''
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تکالیف و امتحانات</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: Tahoma, sans-serif; 
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: white;
            min-height: 100vh;
            padding-top: 70px;
            padding-bottom: 60px;
        }
        .header {
            position: fixed;
            top: 0;
            width: 100%;
            background: rgba(0, 0, 0, 0.3);
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 100;
        }
        .menu-btn {
            background: none;
            border: none;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
        }
        .menu-container {
            position: fixed;
            top: 0;
            right: 0;
            width: 300px;
            height: 100%;
            background: rgba(30, 30, 60, 0.95);
            backdrop-filter: blur(10px);
            transform: translateX(100%);
            transition: transform 0.3s ease;
            z-index: 200;
            padding: 60px 20px 20px;
        }
        .menu-container.active {
            transform: translateX(0);
        }
        .menu-item {
            display: block;
            padding: 15px;
            margin: 10px 0;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            color: white;
            text-decoration: none;
            text-align: center;
            font-weight: bold;
            transition: all 0.3s;
        }
        .menu-item:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        .overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 150;
            display: none;
        }
        .overlay.active {
            display: block;
        }
        .section-title {
            text-align: center;
            margin: 20px 0;
            background: linear-gradient(45deg, #ff00cc, #00eeff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 1.8rem;
        }
        .exams-container {
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        .exams-text {
            width: 100%;
            height: 150px;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            background: rgba(0, 0, 0, 0.2);
            color: white;
            font-size: 1rem;
            margin-bottom: 20px;
        }
        .submit-btn {
            padding: 12px 30px;
            border-radius: 10px;
            border: none;
            font-size: 1.1rem;
            font-weight: bold;
            background: linear-gradient(45deg, #00eeff, #0066ff);
            color: black;
            cursor: pointer;
            display: block;
            margin: 0 auto;
        }
    </style>
</head>
<body>
    <div class="header">
        <button class="menu-btn" id="menuBtn">☰</button>
        <h2>تکالیف و امتحانات</h2>
    </div>
    
    <div class="menu-container" id="menuContainer">
        <a href="/teacher-dashboard" class="menu-item">صفحه اصلی</a>
        <a href="/profile" class="menu-item">پروفایل</a>
        <a href="#" class="menu-item">اعلانات</a>
    </div>
    
    <div class="overlay" id="overlay"></div>
    
    <h1 class="section-title">تکالیف و امتحانات</h1>
    
    <div class="exams-container">
        <p>تکالیف و امتحان مورد نظر خود را بنویسید:</p>
        <textarea class="exams-text" placeholder="متن تکالیف و امتحانات را وارد کنید..."></textarea>
        <button class="submit-btn" onclick="submitExams()">تایید</button>
    </div>
    
    <script>
        document.getElementById('menuBtn').addEventListener('click', function() {
            const menu = document.getElementById('menuContainer');
            const overlay = document.getElementById('overlay');
            menu.classList.toggle('active');
            overlay.classList.toggle('active');
        });
        
        document.getElementById('overlay').addEventListener('click', function() {
            document.getElementById('menuContainer').classList.remove('active');
            this.classList.remove('active');
        });
        
        function submitExams() {
            const text = document.querySelector('.exams-text').value;
            if(text.trim() === '') {
                alert('لطفاً متن تکالیف و امتحانات را وارد کنید');
                return;
            }
            alert('تکالیف و امتحانات با موفقیت ارسال شد');
            // در نسخه کامل، این اطلاعات به سرور ارسال می‌شوند
        }
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)