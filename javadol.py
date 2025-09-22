from flask import Flask, render_template_string, request, session, redirect, url_for, flash
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# داده‌های کاربران (در عمل باید در دیتابیس ذخیره شود)
users = {
    'admin': {
        'name': 'مدیر',
        'lastname': 'سیستم',
        'role': 'مدیر',
        'password': 'dabirstan012345'
    }
}

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>سایت رسمی دبیرستان پسرانه جوادالائمه</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;700&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Vazirmatn', sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            color: white;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            flex: 1;
        }
        
        .header {
            text-align: center;
            padding: 30px 0;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 15px;
            text-shadow: 0 0 20px #00eeff;
            background: linear-gradient(45deg, #ff00cc, #00eeff, #ff00cc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .welcome-text {
            font-size: 1.2rem;
            margin-bottom: 30px;
            color: #e0e0ff;
            line-height: 1.6;
        }
        
        .buttons-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 25px;
            margin: 40px 0;
        }
        
        .btn {
            padding: 20px;
            border: none;
            border-radius: 15px;
            font-size: 1.1rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
            position: relative;
            overflow: hidden;
            color: white;
            text-align: center;
        }
        
        .btn:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0,0,0,0.4);
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
        
        .btn-admin { background: linear-gradient(45deg, #ff00cc, #ff0066); }
        .btn-teacher { background: linear-gradient(45deg, #00eeff, #0066ff); }
        .btn-parent { background: linear-gradient(45deg, #ffcc00, #ff6600); }
        .btn-student { background: linear-gradient(45deg, #00ff99, #00cc66); }
        
        .form-container {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin: 20px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
        }
        
        input, select {
            width: 100%;
            padding: 15px;
            border: 2px solid rgba(255,255,255,0.2);
            border-radius: 10px;
            background: rgba(0,0,0,0.3);
            color: white;
            font-size: 1rem;
            transition: border-color 0.3s;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: #00eeff;
            box-shadow: 0 0 15px rgba(0, 238, 255, 0.5);
        }
        
        .submit-btn {
            background: linear-gradient(45deg, #00eeff, #0066ff);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 1.1rem;
            cursor: pointer;
            width: 100%;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .submit-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(0, 238, 255, 0.4);
        }
        
        .error {
            background: rgba(255, 0, 0, 0.2);
            border: 1px solid #ff4444;
            padding: 15px;
            border-radius: 10px;
            margin: 15px 0;
            text-align: center;
        }
        
        .success {
            background: rgba(0, 255, 0, 0.2);
            border: 1px solid #00ff00;
            padding: 15px;
            border-radius: 10px;
            margin: 15px 0;
            text-align: center;
        }
        
        .profile-container {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin: 20px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        
        .profile-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            margin: 10px 0;
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        .edit-btn {
            background: linear-gradient(45deg, #ffcc00, #ff6600);
            border: none;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            cursor: pointer;
            color: white;
            font-weight: bold;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
        }
        
        .edit-btn:hover {
            transform: scale(1.1);
        }
        
        .logout-btn {
            background: linear-gradient(45deg, #ff0066, #ff00cc);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 1.1rem;
            cursor: pointer;
            width: 100%;
            font-weight: 500;
            margin-top: 20px;
            transition: all 0.3s ease;
        }
        
        .logout-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(255, 0, 102, 0.4);
        }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }
        
        .modal-content {
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            padding: 30px;
            border-radius: 20px;
            text-align: center;
            max-width: 400px;
            width: 90%;
            box-shadow: 0 20px 50px rgba(0,0,0,0.5);
        }
        
        .modal-buttons {
            display: flex;
            gap: 15px;
            margin-top: 20px;
            justify-content: center;
        }
        
        .modal-btn {
            padding: 12px 25px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .modal-btn-yes {
            background: linear-gradient(45deg, #00ff99, #00cc66);
            color: white;
        }
        
        .modal-btn-no {
            background: linear-gradient(45deg, #ff0066, #ff00cc);
            color: white;
        }
        
        .modal-btn:hover {
            transform: translateY(-2px);
        }
        
        .toolbar {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(0,0,0,0.8);
            backdrop-filter: blur(10px);
            display: flex;
            justify-content: space-around;
            padding: 15px;
            border-top: 2px solid rgba(255,255,255,0.1);
        }
        
        .toolbar-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            text-decoration: none;
            color: #ccc;
            transition: all 0.3s ease;
            padding: 10px 20px;
            border-radius: 15px;
        }
        
        .toolbar-item.active {
            background: rgba(0, 238, 255, 0.2);
            color: #00eeff;
            box-shadow: 0 0 20px rgba(0, 238, 255, 0.3);
        }
        
        .toolbar-item:hover {
            color: white;
            transform: translateY(-3px);
        }
        
        .toolbar-icon {
            font-size: 1.5rem;
            margin-bottom: 5px;
        }
        
        .back-btn {
            background: linear-gradient(45deg, #666666, #999999);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 10px;
            cursor: pointer;
            margin-bottom: 20px;
            transition: all 0.3s ease;
        }
        
        .back-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 102, 102, 0.4);
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 1.8rem;
            }
            
            .buttons-container {
                grid-template-columns: 1fr;
            }
            
            .btn {
                padding: 15px;
                font-size: 1rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        {% if not session.get('logged_in') %}
            {% if request.endpoint == 'login_admin' %}
                <button class="back-btn" onclick="window.location.href='/'">← بازگشت</button>
                <div class="header">
                    <h1>ورود مدیران</h1>
                </div>
                <div class="form-container">
                    <form method="POST">
                        <div class="form-group">
                            <label for="name">نام:</label>
                            <input type="text" id="name" name="name" value="{{ request.form.name or '' }}" required>
                        </div>
                        <div class="form-group">
                            <label for="lastname">نام خانوادگی:</label>
                            <input type="text" id="lastname" name="lastname" value="{{ request.form.lastname or '' }}" required>
                        </div>
                        <div class="form-group">
                            <label for="role">مرتبه:</label>
                            <select id="role" name="role" required>
                                <option value="">انتخاب کنید</option>
                                <option value="مدیر" {{ 'selected' if request.form.role == 'مدیر' }}>مدیر</option>
                                <option value="ناظم" {{ 'selected' if request.form.role == 'ناظم' }}>ناظم</option>
                                <option value="معاون" {{ 'selected' if request.form.role == 'معاون' }}>معاون</option>
                                <option value="سرپرست" {{ 'selected' if request.form.role == 'سرپرست' }}>سرپرست</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="password">رمز ورود:</label>
                            <input type="password" id="password" name="password" required>
                        </div>
                        {% if error %}
                            <div class="error">{{ error }}</div>
                        {% endif %}
                        <button type="submit" class="submit-btn">ورود</button>
                    </form>
                </div>
            {% else %}
                <div class="header">
                    <h1>سایت رسمی دبیرستان پسرانه جوادالائمه</h1>
                </div>
                <div class="welcome-text">
                    <p>به سایت رسمی دبیرستان جوادالائمه خوش آمدید</p>
                    <p>لطفاً برای ورود، با توجه به وضعیت خود، یکی از دکمه‌های زیر را انتخاب کنید:</p>
                </div>
                <div class="buttons-container">
                    <button class="btn btn-admin" onclick="window.location.href='/login/admin'">ورود مدیران</button>
                    <button class="btn btn-teacher" onclick="alert('این بخش در حال توسعه است')">ورود معلمان</button>
                    <button class="btn btn-parent" onclick="alert('این بخش در حال توسعه است')">ورود والدین</button>
                    <button class="btn btn-student" onclick="alert('این بخش در حال توسعه است')">ورود دانش‌آموزان</button>
                </div>
            {% endif %}
        {% else %}
            {% if page == 'profile' %}
                <button class="back-btn" onclick="window.location.href='/admin'">← بازگشت</button>
                <div class="header">
                    <h1>پروفایل کاربری</h1>
                </div>
                <div class="profile-container">
                    <div class="profile-item">
                        <span><strong>نام:</strong> {{ session.name }}</span>
                        <button class="edit-btn" onclick="editField('name', '{{ session.name }}')">✎</button>
                    </div>
                    <div class="profile-item">
                        <span><strong>نام خانوادگی:</strong> {{ session.lastname }}</span>
                        <button class="edit-btn" onclick="editField('lastname', '{{ session.lastname }}')">✎</button>
                    </div>
                    <div class="profile-item">
                        <span><strong>مرتبه:</strong> {{ session.role }}</span>
                        <button class="edit-btn" onclick="editField('role', '{{ session.role }}')">✎</button>
                    </div>
                    <div class="profile-item">
                        <span><strong>رمز ورود:</strong> ••••••••••</span>
                        <button class="edit-btn" disabled style="opacity: 0.5;">✎</button>
                    </div>
                    <button class="logout-btn" onclick="showLogoutModal()">خروج از حساب</button>
                </div>
            {% else %}
                <div class="header">
                    <h1>پنل مدیریت</h1>
                    <p>به پنل مدیریت خوش آمدید</p>
                </div>
                <div class="welcome-text">
                    <p>شما با موفقیت وارد شده‌اید. از منوی پایین می‌توانید بین صفحات جابجا شوید.</p>
                </div>
            {% endif %}
        {% endif %}
    </div>
    
    {% if session.get('logged_in') %}
        <div class="toolbar">
            <a href="/admin" class="toolbar-item {{ 'active' if page != 'profile' }}">
                <div class="toolbar-icon">🏠</div>
                <span>صفحه اصلی</span>
            </a>
            <a href="/admin/profile" class="toolbar-item {{ 'active' if page == 'profile' }}">
                <div class="toolbar-icon">👤</div>
                <span>پروفایل</span>
            </a>
        </div>
    {% endif %}
    
    <div id="logoutModal" class="modal">
        <div class="modal-content">
            <h3>آیا مطمئن هستید می‌خواهید از حساب خارج شوید؟</h3>
            <div class="modal-buttons">
                <button class="modal-btn modal-btn-yes" onclick="logout()">بله</button>
                <button class="modal-btn modal-btn-no" onclick="closeModal()">خیر</button>
            </div>
        </div>
    </div>
    
    <script>
        function showLogoutModal() {
            document.getElementById('logoutModal').style.display = 'flex';
        }
        
        function closeModal() {
            document.getElementById('logoutModal').style.display = 'none';
        }
        
        function logout() {
            window.location.href = '/logout';
        }
        
        function editField(field, currentValue) {
            const newValue = prompt('مقدار جدید را وارد کنید:', currentValue);
            if (newValue !== null && newValue !== '') {
                // ارسال درخواست برای ویرایش
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = '/edit_profile';
                
                const fieldInput = document.createElement('input');
                fieldInput.type = 'hidden';
                fieldInput.name = 'field';
                fieldInput.value = field;
                
                const valueInput = document.createElement('input');
                valueInput.type = 'hidden';
                valueInput.name = 'value';
                valueInput.value = newValue;
                
                form.appendChild(fieldInput);
                form.appendChild(valueInput);
                document.body.appendChild(form);
                form.submit();
            }
        }
        
        // بستن مودال با کلیک خارج از آن
        window.onclick = function(event) {
            const modal = document.getElementById('logoutModal');
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/login/admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        name = request.form['name']
        lastname = request.form['lastname']
        role = request.form['role']
        password = request.form['password']
        
        # بررسی رمز عبور
        if password == 'dabirstan012345':
            # ذخیره اطلاعات در session
            session['logged_in'] = True
            session['name'] = name
            session['lastname'] = lastname
            session['role'] = role
            return redirect('/admin')
        else:
            return render_template_string(HTML_TEMPLATE, error='رمز ورود اشتباه است', page='login')
    
    return render_template_string(HTML_TEMPLATE, page='login')

@app.route('/admin')
def admin_panel():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template_string(HTML_TEMPLATE, page='admin')

@app.route('/admin/profile')
def admin_profile():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template_string(HTML_TEMPLATE, page='profile')

@app.route('/edit_profile', methods=['POST'])
def edit_profile():
    if not session.get('logged_in'):
        return redirect('/')
    
    field = request.form['field']
    value = request.form['value']
    
    # به‌روزرسانی اطلاعات session
    if field in ['name', 'lastname', 'role']:
        session[field] = value
    
    return redirect('/admin/profile')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)