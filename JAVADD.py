from flask import Flask, render_template_string, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = 'dabirestan_secret_key'

# حالت اولیه پروفایل مدیر
DEFAULT_PROFILE = {
    'name': 'نام',
    'family': 'نام خانوادگی',
    'rank': 'انتخاب کنید',
    'password': 'dabirestan012345'
}

@app.route('/')
def home():
    return render_template_string(HOME_HTML)

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        name = request.form['name']
        family = request.form['family']
        rank = request.form['rank']
        password = request.form['password']

        if not name or not family or rank == 'انتخاب کنید' or password != 'dabirestan012345':
            error = 'اطلاعات وارد شده نادرست است. لطفاً دوباره تلاش کنید.'
        else:
            session['logged_in'] = True
            session['profile'] = {
                'name': name,
                'family': family,
                'rank': rank,
                'password': password
            }
            return redirect(url_for('admin_portal'))

    return render_template_string(LOGIN_HTML, error=error)

@app.route('/admin_portal')
def admin_portal():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    profile = session.get('profile', DEFAULT_PROFILE)
    return render_template_string(PORTAL_HTML, profile=profile)

@app.route('/update_profile', methods=['POST'])
def update_profile():
    field = request.form.get('field')
    value = request.form.get('value')
    profile = session.get('profile', DEFAULT_PROFILE)
    if field != 'password':
        profile[field] = value
        session['profile'] = profile
    return '', 204

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('admin_login'))

CSS = """
@font-face {
    font-family: 'Vazir';
    src: url('https://cdn.jsdelivr.net/gh/rastikerdar/vazir-font@v30.1.0/dist/Vazir.woff2') format('woff2');
}
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Vazir', sans-serif;
    direction: rtl;
}
body {
    background: linear-gradient(135deg, #0f172a, #2e026d, #00fff7);
    color: white;
    min-height: 100vh;
    padding: 20px;
    overflow-x: hidden;
}
.title {
    text-align: center;
    font-size: 2rem;
    margin: 30px 0;
    color: #ffffff;
    text-shadow: 0 0 10px #ff007f;
}
.buttons-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 25px;
    max-width: 1000px;
    margin: 0 auto;
}
.btn {
    padding: 30px 20px;
    border-radius: 15px;
    font-size: 1.4rem;
    color: white;
    text-align: center;
    cursor: pointer;
    border: none;
    transition: transform 0.3s, box-shadow 0.3s;
    box-shadow: 0 0 15px rgba(0, 0, 0, 0.5);
}
.btn:hover {
    transform: scale(1.05);
    box-shadow: 0 0 25px currentColor;
}
.btn1 { background: linear-gradient(45deg, #00fff7, #007bff); }
.btn2 { background: linear-gradient(45deg, #39ff14, #007bff); }
.btn3 { background: linear-gradient(45deg, #ff007f, #00fff7); }
.btn4 { background: linear-gradient(45deg, #007bff, #39ff14); }

/* Login Form */
.login-form {
    max-width: 500px;
    margin: 50px auto;
    padding: 30px;
    background: rgba(0,0,0,0.4);
    border-radius: 10px;
    box-shadow: 0 0 20px #00fff7;
}
.login-form input, .login-form select {
    width: 100%;
    padding: 12px;
    margin: 10px 0;
    border-radius: 8px;
    border: none;
    background: rgba(255,255,255,0.1);
    color: white;
}
.login-form button {
    width: 100%;
    padding: 12px;
    background: #00fff7;
    border: none;
    border-radius: 8px;
    color: black;
    font-weight: bold;
    cursor: pointer;
}
.login-form .error {
    color: #ff007f;
    text-align: center;
    margin: 10px 0;
}

/* Portal */
.portal-container {
    max-width: 1000px;
    margin: 0 auto;
    padding: 20px;
}
.portal-btns {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}
.portal-btn {
    padding: 20px;
    background: linear-gradient(45deg, #00fff7, #007bff);
    color: black;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    transition: transform 0.2s;
}
.portal-btn:hover {
    transform: scale(1.03);
}
.menu-toggle {
    position: fixed;
    top: 20px;
    right: 20px;
    cursor: pointer;
    z-index: 1000;
    font-size: 2rem;
    color: white;
}
.sidebar {
    position: fixed;
    top: 0;
    right: 0;
    width: 300px;
    height: 100vh;
    background: rgba(15, 23, 42, 0.95);
    padding: 20px;
    box-shadow: -5px 0 15px rgba(0,0,0,0.5);
    transform: translateX(100%);
    transition: transform 0.3s ease;
    z-index: 999;
}
.sidebar.active {
    transform: translateX(0);
}
.sidebar ul {
    list-style: none;
    margin-top: 40px;
}
.sidebar ul li {
    padding: 15px;
    border-bottom: 1px solid #444;
    cursor: pointer;
    transition: background 0.2s;
}
.sidebar ul li:hover {
    background: rgba(0,255,247,0.1);
}
.profile-section {
    padding: 20px;
    background: rgba(0,0,0,0.3);
    border-radius: 10px;
    margin-top: 20px;
}
.editable-field {
    margin: 10px 0;
    padding: 10px;
    background: rgba(255,255,255,0.1);
    border-radius: 5px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.editable-field input, .editable-field select {
    background: transparent;
    border: none;
    color: white;
    width: 70%;
    padding: 5px;
}
.edit-btn {
    background: #00fff7;
    color: black;
    border: none;
    border-radius: 4px;
    padding: 5px 10px;
    cursor: pointer;
}
.edit-actions {
    display: flex;
    gap: 10px;
    margin-top: 5px;
}
.edit-actions button {
    padding: 5px 10px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}
.confirm-btn { background: #00ff7f; }
.cancel-btn { background: #ff007f; }

.modal {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.7);
    justify-content: center;
    align-items: center;
    z-index: 2000;
}
.modal-content {
    background: rgba(15,23,42,0.95);
    padding: 20px;
    border-radius: 10px;
    text-align: center;
    width: 300px;
}
.modal button {
    margin: 10px;
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}
.confirm-logout { background: #00ff7f; }
.cancel-logout { background: #ff007f; }

.footer-typed {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    color: white;
    font-size: 1rem;
    white-space: nowrap;
    overflow: hidden;
    border-right: 2px solid white;
    padding-right: 2px;
}
"""

HOME_HTML = f'''
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>دبیرستان جوادالائمه</title>
    <style>{CSS}</style>
</head>
<body>
    <h1 class="title">به سایت رسمی دبیرستان پسرانه جوادالائمه خوش آمدید</h1>

    <div class="buttons-container">
        <div class="btn btn1" onclick="window.location.href='/admin_login'">ورود مدیران<br><small>این بخش فقط برای مدیران است</small></div>
        <div class="btn btn2">ورود معلمان<br><small>این بخش فقط برای معلمان است</small></div>
        <div class="btn btn3">ورود والدین<br><small>این بخش فقط برای والدین است</small></div>
        <div class="btn btn4">ورود دانش‌آموزان<br><small>این بخش فقط برای دانش‌آموزان است</small></div>
    </div>

    <div class="footer-typed" id="footer-typed"></div>

    <script>
        const text = "سازنده : محمدرضا محمدی - دانش آموز دبیرستان جوادالائمه - رشته ریاضی";
        const element = document.getElementById("footer-typed");
        let i = 0;
        function typeWriter() {{
            if (i < text.length) {{
                element.innerHTML += text.charAt(i);
                i++;
                setTimeout(typeWriter, 100);
            }}
        }}
        window.onload = typeWriter;
    </script>
</body>
</html>
'''

LOGIN_HTML = '''
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ورود مدیران</title>
    <style>{CSS}</style>
</head>
<body>
    <div class="login-form">
        <h2>ورود مدیران</h2>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        <form method="POST">
            <input type="text" name="name" placeholder="نام" required>
            <input type="text" name="family" placeholder="نام خانوادگی" required>
            <select name="rank" required>
                <option value="انتخاب کنید" disabled selected>مرتبه</option>
                <option value="مدیر">مدیر</option>
                <option value="ناظم">ناظم</option>
                <option value="معاون">معاون</option>
                <option value="مشاور">مشاور</option>
            </select>
            <input type="password" name="password" placeholder="رمز" required>
            <button type="submit">ورود</button>
        </form>
    </div>
</body>
</html>
'''

PORTAL_HTML = '''
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>درگاه مدیران</title>
    <style>{CSS}</style>
</head>
<body>
    <div class="menu-toggle" onclick="toggleSidebar()">☰</div>

    <div class="sidebar" id="sidebar">
        <ul>
            <li onclick="showProfile()">پروفایل</li>
            <li onclick="showNotifications()">اعلانات</li>
            <li onclick="logout()">خروج</li>
        </ul>
    </div>

    <div class="portal-container">
        <h1>درگاه مدیران</h1>
        <div class="portal-btns">
            <button class="portal-btn">مدیریت دانش آموزان</button>
            <button class="portal-btn">مدیریت معلمان</button>
            <button class="portal-btn">مدیریت گزارشات والدین</button>
            <button class="portal-btn">مدیریت گزارشات معلمان</button>
            <button class="portal-btn">مدیریت گزارشات دانش آموزان</button>
            <button class="portal-btn">مدیریت بخش آزمایشگاه</button>
            <button class="portal-btn">مدیریت نمرات</button>
            <button class="portal-btn">مدیریت کارنامه</button>
        </div>
    </div>

    <div class="modal" id="modal">
        <div class="modal-content">
            <p>آیا مطمئن هستید می‌خواهید از حساب خارج شوید؟</p>
            <button class="confirm-logout" onclick="confirmLogout()">بله</button>
            <button class="cancel-logout" onclick="closeModal()">خیر</button>
        </div>
    </div>

    <div class="modal" id="profile-modal">
        <div class="modal-content">
            <div class="profile-section">
                <div class="editable-field">
                    <span>نام:</span>
                    <div id="name-display">{{ profile.name }}</div>
                    <button class="edit-btn" onclick="startEdit('name', 'name-display')">✏️</button>
                </div>
                <div class="editable-field">
                    <span>نام خانوادگی:</span>
                    <div id="family-display">{{ profile.family }}</div>
                    <button class="edit-btn" onclick="startEdit('family', 'family-display')">✏️</button>
                </div>
                <div class="editable-field">
                    <span>مرتبه:</span>
                    <div id="rank-display">{{ profile.rank }}</div>
                    <button class="edit-btn" onclick="startEdit('rank', 'rank-display')">✏️</button>
                </div>
                <div class="editable-field">
                    <span>رمز:</span>
                    <div id="password-display">••••••••</div>
                    <button class="edit-btn" disabled>✏️</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        let editingField = null;

        function toggleSidebar() {{
            document.getElementById('sidebar').classList.toggle('active');
        }}

        function showProfile() {{
            document.getElementById('profile-modal').style.display = 'flex';
        }}

        function showNotifications() {{
            alert('بخش اعلانات');
        }}

        function logout() {{
            document.getElementById('modal').style.display = 'flex';
        }}

        function confirmLogout() {{
            window.location.href = '/logout';
        }}

        function closeModal() {{
            document.getElementById('modal').style.display = 'none';
        }}

        function startEdit(field, displayId) {{
            const display = document.getElementById(displayId);
            const current = display.textContent;
            editingField = field;

            if (field === 'rank') {{
                display.innerHTML = `
                    <select id="edit-input">
                        <option value="مدیر" {{'selected' if profile.rank == 'مدیر' else ''}}>مدیر</option>
                        <option value="ناظم" {{'selected' if profile.rank == 'ناظم' else ''}}>ناظم</option>
                        <option value="معاون" {{'selected' if profile.rank == 'معاون' else ''}}>معاون</option>
                        <option value="مشاور" {{'selected' if profile.rank == 'مشاور' else ''}}>مشاور</option>
                    </select>
                `;
            }} else {{
                display.innerHTML = `<input type="text" id="edit-input" value="${current}">`;
            }}

            display.innerHTML += `
                <div class="edit-actions">
                    <button class="confirm-btn" onclick="saveEdit('${field}', '${displayId}')">✓ تأیید</button>
                    <button class="cancel-btn" onclick="cancelEdit('${displayId}', '${current}')">✗ انصراف</button>
                </div>
            `;
        }}

        function saveEdit(field, displayId) {{
            const input = document.getElementById('edit-input');
            const value = input.value || input.options[input.selectedIndex].value;

            fetch('/update_profile', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/x-www-form-urlencoded' }},
                body: `field=${field}&value=${encodeURIComponent(value)}`
            }}).then(() => {{
                document.getElementById(displayId).innerHTML = value;
                document.getElementById(displayId).innerHTML += `<button class="edit-btn" onclick="startEdit('${field}', '${displayId}')">✏️</button>`;
            }});
        }}

        function cancelEdit(displayId, original) {{
            document.getElementById(displayId).innerHTML = original;
            document.getElementById(displayId).innerHTML += '<button class="edit-btn" onclick="startEdit()">✏️</button>';
        }}
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    import os
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
