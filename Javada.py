from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify
import json
import os
import hashlib

# کلید امنیتی
SECRET_KEY = "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2"

app = Flask(__name__)
app.secret_key = SECRET_KEY

DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"students": {}, "admin": None}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@app.route("/")
def index():
    html = '''
    <!DOCTYPE html>
    <html lang="fa">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>دبیرستان جوادالائمه</title>
        <style>
            @import url('https://v1.fontapi.ir/css/Shabnam');
            body {
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
                color: white;
                font-family: 'Shabnam', sans-serif;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                overflow-x: hidden;
            }
            .hero {
                text-align: center;
                margin-bottom: 50px;
            }
            h1 {
                font-size: 2.5rem;
                text-shadow: 0 0 10px #00f7ff, 0 0 20px #00f7ff;
                animation: neon 1.5s infinite alternate;
            }
            .buttons-container {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 20px;
                width: 80%;
                max-width: 600px;
            }
            .btn {
                padding: 20px;
                border-radius: 15px;
                border: none;
                color: white;
                font-size: 1.2rem;
                cursor: pointer;
                transition: all 0.3s ease;
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
                position: relative;
                overflow: hidden;
            }
            .btn:hover {
                transform: translateY(-5px);
                box-shadow: 0 6px 25px rgba(255, 255, 255, 0.2);
            }
            .btn::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(45deg, #ff00cc, #333399, #00f7ff);
                z-index: -1;
                opacity: 0.7;
                transition: opacity 0.3s;
            }
            .btn:hover::before {
                opacity: 1;
            }
            @keyframes neon {
                from { text-shadow: 0 0 5px #00f7ff; }
                to { text-shadow: 0 0 20px #00f7ff, 0 0 30px #00f7ff; }
            }
        </style>
    </head>
    <body>
        <div class="hero">
            <h1>به سایت رسمی دبیرستان پسرانه جوادالائمه خوش آمدید</h1>
        </div>
        <div class="buttons-container">
            <button class="btn" onclick="window.location.href='/admin-login'">ورود مدیران</button>
            <button class="btn">ورود معلمان</button>
            <button class="btn">ورود والدین</button>
            <button class="btn">ورود دانش‌آموزان</button>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        name = request.form.get("name")
        family = request.form.get("family")
        rank = request.form.get("rank")
        password = request.form.get("password")

        if not name or not family or not rank or not password:
            error = "لطفاً همه فیلدها را پر کنید."
            return render_template_string(login_html, error=error)

        if password != "dabirestan012345":
            error = "رمز عبور اشتباه است."
            return render_template_string(login_html, error=error)

        session["admin"] = {"name": name, "family": family, "rank": rank}
        return redirect(url_for("admin_dashboard"))

    return render_template_string(login_html)

login_html = '''
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ورود مدیر</title>
    <style>
        @import url('https://v1.fontapi.ir/css/Shabnam');
        body {
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: white;
            font-family: 'Shabnam', sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .form-container {
            background: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 15px;
            width: 90%;
            max-width: 400px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(10px);
        }
        input, select {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border-radius: 10px;
            border: none;
            background: rgba(255, 255, 255, 0.1);
            color: white;
        }
        button {
            width: 100%;
            padding: 12px;
            margin-top: 15px;
            border-radius: 10px;
            border: none;
            background: linear-gradient(45deg, #ff00cc, #00f7ff);
            color: white;
            font-size: 1.1rem;
            cursor: pointer;
        }
        .error {
            color: #ff5252;
            text-align: center;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="form-container">
        <h2>ورود مدیران</h2>
        <form method="POST">
            <input type="text" name="name" placeholder="نام" required>
            <input type="text" name="family" placeholder="نام خانوادگی" required>
            <select name="rank" required>
                <option value="">انتخاب مرتبه</option>
                <option value="مدیر">مدیر</option>
                <option value="ناظم">ناظم</option>
                <option value="معاون">معاون</option>
                <option value="مشاور">مشاور</option>
            </select>
            <input type="password" name="password" placeholder="رمز عبور" required>
            <button type="submit">ورود</button>
        </form>
        {% if error %}
            <div class="error">{{ error }}</div>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route("/admin-dashboard")
def admin_dashboard():
    if not session.get("admin"):
        return redirect(url_for("index"))

    html = '''
    <!DOCTYPE html>
    <html lang="fa">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>درگاه مدیران</title>
        <style>
            @import url('https://v1.fontapi.ir/css/Shabnam');
            body {
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
                color: white;
                font-family: 'Shabnam', sans-serif;
                min-height: 100vh;
            }
            .toolbar {
                display: flex;
                justify-content: space-between;
                padding: 15px 30px;
                background: rgba(0, 0, 0, 0.2);
                backdrop-filter: blur(10px);
            }
            .btn {
                padding: 15px 25px;
                border-radius: 12px;
                border: none;
                color: white;
                font-size: 1.1rem;
                cursor: pointer;
                transition: all 0.3s ease;
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            }
            .btn:hover {
                transform: translateY(-3px);
                box-shadow: 0 6px 20px rgba(255, 255, 255, 0.2);
            }
            .btn::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(45deg, #ff00cc, #00f7ff);
                z-index: -1;
                opacity: 0.7;
                transition: opacity 0.3s;
                border-radius: 12px;
            }
            .btn:hover::before {
                opacity: 1;
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 20px;
                padding: 30px;
            }
        </style>
    </head>
    <body>
        <div class="toolbar">
            <a href="/profile" class="btn">پروفایل</a>
            <div>اعلانات</div>
            <a href="/" class="btn">صفحه اصلی</a>
        </div>
        <div class="grid">
            <button class="btn" onclick="window.location.href='/manage-students'">مدیریت دانش‌آموزان</button>
            <button class="btn">مدیریت معلمان</button>
            <button class="btn">مدیریت گزارشات والدین</button>
            <button class="btn">مدیریت گزارشات معلمان</button>
            <button class="btn">مدیریت گزارشات دانش‌آموزان</button>
            <button class="btn">مدیریت بخش آزمایشگاه</button>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route("/profile")
def profile():
    admin = session.get("admin")
    if not admin:
        return redirect(url_for("index"))

    html = f'''
    <!DOCTYPE html>
    <html lang="fa">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>پروفایل</title>
        <style>
            @import url('https://v1.fontapi.ir/css/Shabnam');
            body {{
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
                color: white;
                font-family: 'Shabnam', sans-serif;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                align-items: center;
            }}
            .profile-card {{
                background: rgba(255, 255, 255, 0.1);
                padding: 30px;
                border-radius: 15px;
                width: 90%;
                max-width: 500px;
                margin-top: 30px;
                backdrop-filter: blur(10px);
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            }}
            .field {{
                margin: 15px 0;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .edit-btn {{
                background: rgba(0, 247, 255, 0.2);
                border: 1px solid #00f7ff;
                color: white;
                border-radius: 50%;
                width: 30px;
                height: 30px;
                cursor: pointer;
            }}
            .edit-field {{
                display: none;
            }}
            .controls {{
                display: none;
                margin-top: 10px;
            }}
            .logout-btn {{
                margin-top: 30px;
                padding: 12px 30px;
                border: none;
                border-radius: 10px;
                background: linear-gradient(45deg, #ff00cc, #00f7ff);
                color: white;
                font-size: 1.1rem;
                cursor: pointer;
            }}
        </style>
    </head>
    <body>
        <div class="profile-card">
            <h2>پروفایل مدیر</h2>
            <div class="field">
                <span>نام:</span>
                <div>
                    <span id="name-view">{admin["name"]}</span>
                    <input type="text" id="name-edit" class="edit-field" value="{admin["name"]}">
                    <button class="edit-btn" onclick="toggleEdit('name')">✎</button>
                </div>
            </div>
            <div class="field">
                <span>نام خانوادگی:</span>
                <div>
                    <span id="family-view">{admin["family"]}</span>
                    <input type="text" id="family-edit" class="edit-field" value="{admin["family"]}">
                    <button class="edit-btn" onclick="toggleEdit('family')">✎</button>
                </div>
            </div>
            <div class="field">
                <span>مرتبه:</span>
                <span>{admin["rank"]}</span>
            </div>
            <div class="field">
                <span>رمز عبور:</span>
                <span>********</span>
            </div>
            <div id="name-controls" class="controls">
                <button onclick="saveEdit('name')">تأیید</button>
                <button onclick="cancelEdit('name')">انصراف</button>
            </div>
            <div id="family-controls" class="controls">
                <button onclick="saveEdit('family')">تأیید</button>
                <button onclick="cancelEdit('family')">انصراف</button>
            </div>
            <button class="logout-btn" onclick="logout()">خروج از حساب</button>
        </div>

        <script>
            function toggleEdit(field) {{
                const view = document.getElementById(field + "-view");
                const edit = document.getElementById(field + "-edit");
                const controls = document.getElementById(field + "-controls");

                if (edit.style.display === "none") {{
                    edit.style.display = "inline";
                    view.style.display = "none";
                    controls.style.display = "block";
                }} else {{
                    edit.style.display = "none";
                    view.style.display = "inline";
                    controls.style.display = "none";
                }}
            }}
            function saveEdit(field) {{
                const newValue = document.getElementById(field + "-edit").value;
                document.getElementById(field + "-view").textContent = newValue;
                session["admin"][field] = newValue;
                toggleEdit(field);
            }}
            function cancelEdit(field) {{
                document.getElementById(field + "-edit").value = document.getElementById(field + "-view").textContent;
                toggleEdit(field);
            }}
            function logout() {{
                if (confirm("آیا مطمئن هستید؟")) {{
                    window.location.href = "/";
                }}
            }}
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route("/manage-students")
def manage_students():
    html = '''
    <!DOCTYPE html>
    <html lang="fa">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>مدیریت دانش‌آموزان</title>
        <style>
            @import url('https://v1.fontapi.ir/css/Shabnam');
            body {
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
                color: white;
                font-family: 'Shabnam', sans-serif;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            .btn {
                padding: 15px 25px;
                margin: 10px;
                border-radius: 12px;
                border: none;
                color: white;
                font-size: 1.1rem;
                cursor: pointer;
                transition: all 0.3s ease;
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            }
            .btn:hover {
                transform: translateY(-3px);
                box-shadow: 0 6px 20px rgba(255, 255, 255, 0.2);
            }
            .btn::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(45deg, #ff00cc, #00f7ff);
                z-index: -1;
                opacity: 0.7;
                transition: opacity 0.3s;
                border-radius: 12px;
            }
            .btn:hover::before {
                opacity: 1;
            }
        </style>
    </head>
    <body>
        <h2>انتخاب پایه</h2>
        <button class="btn" onclick="window.location.href='/grade/10'">پایه دهم</button>
        <button class="btn" onclick="window.location.href='/grade/11'">پایه یازدهم</button>
        <button class="btn" onclick="window.location.href='/grade/12'">پایه دوازدهم</button>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route("/grade/<int:grade>")
def grade_page(grade):
    html = f'''
    <!DOCTYPE html>
    <html lang="fa">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>پایه {grade}</title>
        <style>
            @import url('https://v1.fontapi.ir/css/Shabnam');
            body {{
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
                color: white;
                font-family: 'Shabnam', sans-serif;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                align-items: center;
            }}
            .btn {{
                padding: 15px 25px;
                margin: 10px;
                border-radius: 12px;
                border: none;
                color: white;
                font-size: 1.1rem;
                cursor: pointer;
                transition: all 0.3s ease;
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            }}
            .btn:hover {{
                transform: translateY(-3px);
                box-shadow: 0 6px 20px rgba(255, 255, 255, 0.2);
            }}
            .btn::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(45deg, #ff00cc, #00f7ff);
                z-index: -1;
                opacity: 0.7;
                transition: opacity 0.3s;
                border-radius: 12px;
            }}
            .btn:hover::before {{
                opacity: 1;
            }}
        </style>
    </head>
    <body>
        <h2>پایه {grade}</h2>
        <button class="btn" onclick="window.location.href='/grade/{grade}/math'">رشته ریاضی</button>
        <button class="btn" onclick="window.location.href='/grade/{grade}/science'">رشته تجربی</button>
        <button class="btn" onclick="window.location.href='/grade/{grade}/humanities'">رشته انسانی</button>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route("/grade/<int:grade>/<string:field>")
def field_page(grade, field):
    data = load_data()
    students = data.get("students", {}).get(str(grade), {}).get(field, [])
    field_name = {"math": "ریاضی", "science": "تجربی", "humanities": "انسانی"}[field]
    count = len(students)

    html = f'''
    <!DOCTYPE html>
    <html lang="fa">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{field_name}</title>
        <style>
            @import url('https://v1.fontapi.ir/css/Shabnam');
            body {{
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
                color: white;
                font-family: 'Shabnam', sans-serif;
                min-height: 100vh;
            }}
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 10px;
                margin-bottom: 20px;
            }}
            .counter {{
                display: flex;
                align-items: center;
                font-size: 1.2rem;
            }}
            .counter i {{
                margin-right: 10px;
                font-size: 1.5rem;
            }}
            .fab {{
                position: fixed;
                bottom: 30px;
                right: 30px;
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: linear-gradient(45deg, #ff00cc, #00f7ff);
                color: white;
                border: none;
                font-size: 2rem;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            }}
            .card {{
                background: rgba(255, 255, 255, 0.1);
                padding: 15px;
                border-radius: 12px;
                margin: 10px 0;
                display: flex;
                justify-content: space-between;
                align-items: center;
                backdrop-filter: blur(10px);
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            }}
            .actions {{
                display: flex;
                gap: 10px;
            }}
            .action-btn {{
                width: 30px;
                height: 30px;
                border-radius: 50%;
                border: none;
                background: rgba(255, 255, 255, 0.2);
                color: white;
                cursor: pointer;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>{field_name}</h2>
            <div class="counter">
                <i>👤</i>
                <span>{count}</span>
            </div>
        </div>

        <div id="students-list">
            {''.join([
                f'<div class="card"><div><div>{s["name"]} {s["family"]}</div><div>{s["national_id"]}</div></div><div class="actions"><button class="action-btn">✎</button><button class="action-btn">🗑️</button></div></div>'
                for s in students
            ])}
        </div>

        <button class="fab" onclick="openForm()">+</button>

        <div id="form-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.7); justify-content:center; align-items:center;">
            <div style="background:rgba(0,0,0,0.9); padding:20px; border-radius:10px; width:90%; max-width:500px;">
                <h3>ثبت دانش‌آموز</h3>
                <input type="text" id="name" placeholder="نام" required><br>
                <input type="text" id="family" placeholder="نام خانوادگی" required><br>
                <input type="text" id="national_id" placeholder="کد ملی" required><br>
                <input type="text" id="student_number" placeholder="شماره دانش‌آموز"><br>
                <input type="text" id="father_phone" placeholder="شماره پدر"><br>
                <input type="text" id="mother_phone" placeholder="شماره مادر"><br>
                <button onclick="submitStudent()">ثبت</button>
                <button onclick="closeForm()">انصراف</button>
            </div>
        </div>

        <script>
            function openForm() {{
                document.getElementById("form-modal").style.display = "flex";
            }}
            function closeForm() {{
                document.getElementById("form-modal").style.display = "none";
            }}
            function submitStudent() {{
                const data = {{
                    name: document.getElementById("name").value,
                    family: document.getElementById("family").value,
                    national_id: document.getElementById("national_id").value,
                    student_number: document.getElementById("student_number").value,
                    father_phone: document.getElementById("father_phone").value,
                    mother_phone: document.getElementById("mother_phone").value
                }};
                fetch("/add-student/{grade}/{field}", {{
                    method: "POST",
                    headers: {{"Content-Type": "application/json"}},
                    body: JSON.stringify(data)
                }}).then(() => location.reload());
            }}
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route("/add-student/<int:grade>/<string:field>", methods=["POST"])
def add_student(grade, field):
    data = load_data()
    new_student = request.json
    students = data.get("students", {}).get(str(grade), {}).get(field, [])
    for s in students:
        if s["national_id"] == new_student["national_id"]:
            return jsonify({"error": "این دانش آموز با این کد ملی وجود دارد"}), 400
    students.append(new_student)
    data["students"].setdefault(str(grade), {})[field] = students
    save_data(data)
    return jsonify({"success": True})

if __name__ == "__main__":
    # خواندن پورت از متغیر محیطی PORT
    port = int(os.environ.get("PORT", 10000))  # اگر PORT وجود نداشت، از 10000 استفاده کن
    # اجرای سرور Flask با گوش دادن به 0.0.0.0
    app.run(host="0.0.0.0", port=port, debug=False)