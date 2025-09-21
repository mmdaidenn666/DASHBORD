from flask import Flask, render_template_string, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2')

# ========== داده‌های موقت در حافظه ==========
users = {}  # {username: user_data}
notifications = {}  # {username: [notif1, notif2, ...]}
chats = {}  # {chat_id: {messages: [...], participants: [user1, user2]}}
user_chats = {}  # {username: [chat_id1, chat_id2, ...]}
likes = {}  # {(from_user, to_user): True}

CITIES = [
    "شهرک صدرا", "شهرک گلستان", "معالی آباد", "شهرک کشن", "شهرک مهدیه",
    "شهرک زینبیه", "شهرک بعثت", "شهرک والفجر", "شهرک صنعتی عفیف آباد",
    "کوی امام رضا", "شهرک گویم", "شهرک بزین", "شهرک رحمت آباد", "شهرک خورشید",
    "شهرک سلامت", "شهرک فرهنگیان", "کوی زاگرس", "کوی پاسداران", "شهرک عرفان",
    "شهرک هنرستان"
]

# ========== توابع کمکی ==========
def create_chat_id(user1, user2):
    return "-".join(sorted([user1, user2]))

def add_notification(target_user, msg, type="info", from_user=None, action_url=None):
    notif = {
        "id": str(uuid.uuid4()),
        "msg": msg,
        "type": type,
        "from_user": from_user,
        "action_url": action_url,
        "read": False
    }
    if target_user not in notifications:
        notifications[target_user] = []
    notifications[target_user].append(notif)

def get_unread_notifications_count(username):
    if username not in notifications:
        return 0
    return len([n for n in notifications[username] if not n['read']])


# ========== تابع ساخت صفحه پایه (بدون extends) ==========
def make_page(title, content, scripts=""):
    return f'''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | GOYIMIX</title>
    <style>
        :root {{
            --bg: #121212;
            --primary: #9B5DE5;
            --secondary: #00F5D4;
            --pink-neon: #F15BB5;
            --white: #FFFFFF;
            --light-gray: #E0E0E0;
            --glow: 0 0 10px var(--pink-neon), 0 0 20px rgba(241, 91, 181, 0.5);
        }}
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Vazirmatn', 'Segoe UI', Tahoma, sans-serif;
        }}
        body {{
            background-color: var(--bg);
            color: var(--white);
            min-height: 100vh;
            direction: rtl;
            padding-bottom: 70px;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}
        h1, h2, h3, h4, h5 {{
            font-weight: 800;
            letter-spacing: -0.5px;
        }}
        .btn, button {{
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            border: none;
            color: white;
            padding: 14px 28px;
            border-radius: 50px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 0 8px rgba(155, 93, 229, 0.4);
            text-align: center;
            display: inline-block;
            text-decoration: none;
        }}
        .btn:hover, button:hover {{
            transform: translateY(-3px);
            box-shadow: var(--glow);
        }}
        .btn-small {{
            padding: 8px 16px;
            font-size: 14px;
        }}
        input, select, textarea {{
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.2);
            color: var(--white);
            padding: 14px;
            border-radius: 16px;
            width: 100%;
            margin: 10px 0;
            font-size: 16px;
            transition: all 0.3s;
            backdrop-filter: blur(5px);
        }}
        input:focus, select:focus, textarea:focus {{
            outline: none;
            border-color: var(--pink-neon);
            box-shadow: 0 0 12px rgba(241, 91, 181, 0.4);
        }}
        .avatar-container {{
            width: 120px;
            height: 120px;
            margin: 20px auto;
            position: relative;
        }}
        .avatar {{
            width: 100%;
            height: 100%;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 42px;
            cursor: pointer;
            box-shadow: var(--glow);
            transition: all 0.3s ease;
        }}
        .avatar:hover {{
            transform: scale(1.05);
        }}
        .upload-btn {{
            position: absolute;
            bottom: -10px;
            right: -10px;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background: var(--pink-neon);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            box-shadow: 0 0 8px rgba(241, 91, 181, 0.6);
        }}
        .card {{
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 20px;
            margin: 16px 0;
            box-shadow: 0 4px 16px rgba(0,0,0,0.2);
            border: 1px solid rgba(255,255,255,0.1);
            transition: all 0.3s ease;
        }}
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        }}
        .filter-btn {{
            background: rgba(255,255,255,0.1);
            border: 2px solid var(--light-gray);
            color: var(--light-gray);
            padding: 10px 20px;
            border-radius: 50px;
            margin: 6px;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: 600;
            display: inline-block;
        }}
        .filter-btn.active {{
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            border-color: transparent;
            color: white;
            box-shadow: var(--glow);
        }}
        .bottom-nav {{
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            display: flex;
            justify-content: space-around;
            background: rgba(18,18,18,0.95);
            padding: 16px 0;
            backdrop-filter: blur(20px);
            z-index: 1000;
            border-top: 1px solid rgba(255,255,255,0.1);
        }}
        .nav-item {{
            display: flex;
            flex-direction: column;
            align-items: center;
            color: var(--light-gray);
            text-decoration: none;
            font-size: 11px;
            font-weight: 600;
            transition: all 0.3s;
            padding: 5px 0;
            border-radius: 12px;
        }}
        .nav-item.active {{
            color: var(--white);
            background: rgba(255,255,255,0.1);
        }}
        .nav-item i {{
            font-size: 26px;
            margin-bottom: 4px;
        }}
        .notification-dot {{
            position: absolute;
            top: -5px;
            right: -5px;
            width: 12px;
            height: 12px;
            background: #ff3b30;
            border-radius: 50%;
            animation: pulse 1.5s infinite;
        }}
        @keyframes pulse {{
            0% {{ transform: scale(1); opacity: 1; }}
            50% {{ transform: scale(1.2); opacity: 0.8; }}
            100% {{ transform: scale(1); opacity: 1; }}
        }}
        .message-container {{
            display: flex;
            flex-direction: column;
            margin: 12px 0;
            max-width: 75%;
        }}
        .message {{
            padding: 14px 18px;
            border-radius: 20px;
            font-size: 15px;
            line-height: 1.5;
            word-wrap: break-word;
            position: relative;
        }}
        .message.received {{
            background: rgba(255,255,255,0.08);
            align-self: flex-start;
            border-bottom-left-radius: 5px;
        }}
        .message.sent {{
            background: var(--pink-neon);
            color: white;
            align-self: flex-end;
            border-bottom-right-radius: 5px;
            margin-left: auto;
        }}
        .chat-header {{
            display: flex;
            align-items: center;
            padding: 16px;
            background: rgba(0,0,0,0.2);
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        .chat-header .avatar {{
            width: 50px;
            height: 50px;
            font-size: 24px;
            margin-right: 15px;
        }}
        .chat-header h3 {{
            flex: 1;
        }}
        .chat-header .back-btn {{
            color: white;
            font-size: 28px;
            text-decoration: none;
            margin-left: 15px;
        }}
        .chat-input {{
            position: fixed;
            bottom: 80px;
            left: 0;
            right: 0;
            padding: 16px;
            background: rgba(18,18,18,0.95);
            backdrop-filter: blur(20px);
            display: flex;
            gap: 10px;
            border-top: 1px solid rgba(255,255,255,0.1);
        }}
        .chat-input input {{
            flex: 1;
            padding: 14px 20px;
            border-radius: 50px;
            font-size: 16px;
        }}
        .chat-input button {{
            padding: 14px 24px;
            border-radius: 50px;
        }}
        .action-btns {{
            display: flex;
            gap: 8px;
            margin-top: 10px;
        }}
        .toggle-switch {{
            position: relative;
            display: inline-block;
            width: 60px;
            height: 30px;
            margin: 10px 0;
        }}
        .toggle-switch input {{
            opacity: 0;
            width: 0;
            height: 0;
        }}
        .slider {{
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #ccc;
            transition: .4s;
            border-radius: 34px;
        }}
        .slider:before {{
            position: absolute;
            content: "";
            height: 22px;
            width: 22px;
            left: 4px;
            bottom: 4px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }}
        input:checked + .slider {{
            background: linear-gradient(135deg, var(--primary), var(--secondary));
        }}
        input:checked + .slider:before {{
            transform: translateX(30px);
        }}
        .edit-icon {{
            position: absolute;
            left: 15px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--light-gray);
            font-size: 18px;
            cursor: pointer;
            opacity: 0.7;
            transition: opacity 0.3s;
        }}
        .edit-icon:hover {{
            opacity: 1;
        }}
        .password-container {{
            position: relative;
        }}
        .toggle-password {{
            position: absolute;
            left: 15px;
            top: 50%;
            transform: translateY(-50%);
            background: none;
            border: none;
            color: var(--light-gray);
            cursor: pointer;
            font-size: 18px;
        }}
        @media (max-width: 768px) {{
            .container {{ padding: 16px; }}
            .avatar {{ width: 100px; height: 100px; font-size: 36px; }}
            .btn {{ padding: 12px 24px; }}
        }}
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
</head>
<body>
    <!-- Flash Messages -->
    <div style="position: fixed; top: 20px; left: 50%; transform: translateX(-50%); z-index: 9999; width: 90%; max-width: 500px;">
        {{% with messages = get_flashed_messages(with_categories=true) %}}
            {{% if messages %}}
                {{% for category, message in messages %}}
                    <div style="background: {{ '{{' }} category == 'error' and '#ff3b30' or '#00F5D4' {{ '}}' }}; 
                               color: white; 
                               padding: 15px; 
                               text-align: center; 
                               margin: 10px 0; 
                               border-radius: 12px; 
                               font-weight: bold;
                               box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                               animation: slideIn 0.3s ease;">
                        {{ '{{' }} message {{ '}}' }}
                    </div>
                {{% endfor %}}
            {{% endif %}}
        {{% endwith %}}
    </div>

    <div class="container" style="padding: 20px;">
        {content}
    </div>

    {{% if 'username' in session %}}
    <div class="bottom-nav">
        <a href="{{ '{{' }} url_for('profile') {{ '}}' }}" class="nav-item {{ '{{' }} 'active' if request.endpoint == 'profile' else '' {{ '}}' }}">
            <i class="fas fa-user"></i>
            <span>پروفایل</span>
        </a>
        <a href="{{ '{{' }} url_for('home') {{ '}}' }}" class="nav-item {{ '{{' }} 'active' if request.endpoint == 'home' else '' {{ '}}' }}">
            <i class="fas fa-home"></i>
            <span>خانه</span>
        </a>
        <a href="{{ '{{' }} url_for('search') {{ '}}' }}" class="nav-item {{ '{{' }} 'active' if request.endpoint == 'search' else '' {{ '}}' }}">
            <i class="fas fa-search"></i>
            <span>جستجو</span>
        </a>
        <a href="{{ '{{' }} url_for('chat_list') {{ '}}' }}" class="nav-item {{ '{{' }} 'active' if request.endpoint in ['chat_list', 'chat_page'] else '' {{ '}}' }}">
            <i class="fas fa-comment"></i>
            <span>چت</span>
        </a>
        <a href="{{ '{{' }} url_for('view_notifications') {{ '}}' }}" class="nav-item {{ '{{' }} 'active' if request.endpoint == 'view_notifications' else '' {{ '}}' }}" style="position: relative;">
            <i class="fas fa-bell"></i>
            <span>اعلان‌ها</span>
            {{% if get_unread_notifications_count(session['username']) > 0 %}}
                <div class="notification-dot"></div>
            {{% endif %}}
        </a>
    </div>
    {{% endif %}}

    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            // درخواست مجوز نوتیفیکیشن
            if (Notification.permission !== "granted" && Notification.permission !== "denied") {{
                Notification.requestPermission();
            }}

            // تابع نمایش نوتیفیکیشن دسکتاپ
            function showDesktopNotification(title, message) {{
                if (Notification.permission === "granted") {{
                    new Notification(title, {{
                        body: message,
                        icon: "https://i.imgur.com/M0X0XeP.png"
                    }});
                }}
            }}

            // مانیتور کردن تغییرات نوتیفیکیشن
            const notificationBell = document.querySelector('.fa-bell');
            if (notificationBell) {{
                setInterval(() => {{
                    fetch('/api/notifications/unread')
                    .then(response => response.json())
                    .then(data => {{
                        const dot = document.querySelector('.notification-dot');
                        if (data.count > 0 && !dot) {{
                            const bellContainer = notificationBell.closest('.nav-item');
                            const newDot = document.createElement('div');
                            newDot.className = 'notification-dot';
                            bellContainer.appendChild(newDot);
                        }} else if (data.count === 0 && dot) {{
                            dot.remove();
                        }}
                    }})
                    .catch(err => console.log('Error checking notifications:', err));
                }}, 5000);
            }}

            // تابع تغییر عکس پروفایل
            const avatarContainers = document.querySelectorAll('.avatar-container');
            avatarContainers.forEach(container => {{
                const avatar = container.querySelector('.avatar');
                const uploadBtn = container.querySelector('.upload-btn');
                
                if (uploadBtn) {{
                    uploadBtn.addEventListener('click', function(e) {{
                        e.stopPropagation();
                        const input = document.createElement('input');
                        input.type = 'file';
                        input.accept = 'image/*';
                        input.onchange = function(e) {{
                            const file = e.target.files[0];
                            if (file) {{
                                const reader = new FileReader();
                                reader.onload = function(event) {{
                                    avatar.innerHTML = `<img src="${{event.target.result}}" style="width:100%;height:100%;border-radius:50%;object-fit:cover;">`;
                                }};
                                reader.readAsDataURL(file);
                            }}
                        }};
                        input.click();
                    }});
                }}
            }});

            // تابع نمایش/مخفی کردن رمز عبور
            const togglePasswordBtns = document.querySelectorAll('.toggle-password');
            togglePasswordBtns.forEach(btn => {{
                btn.addEventListener('click', function() {{
                    const input = this.nextElementSibling;
                    if (input.type === 'password') {{
                        input.type = 'text';
                        this.innerHTML = '<i class="fas fa-eye-slash"></i>';
                    }} else {{
                        input.type = 'password';
                        this.innerHTML = '<i class="fas fa-eye"></i>';
                    }}
                }});
            }});

            // تابع فعال/غیرفعال کردن فیلترها
            const filterBtns = document.querySelectorAll('.filter-btn');
            filterBtns.forEach(btn => {{
                btn.addEventListener('click', function() {{
                    this.classList.toggle('active');
                    applyFilters();
                }});
            }});

            function applyFilters() {{
                const activeFilters = [];
                document.querySelectorAll('.filter-btn.active').forEach(btn => {{
                    activeFilters.push(btn.dataset.filter);
                }});
                
                let url = '/home';
                if (activeFilters.length > 0) {{
                    url += '?' + activeFilters.map(f => f + '=1').join('&');
                }}
                window.location.href = url;
            }}
        }});
        {scripts}
    </script>
</body>
</html>
'''


# ========== صفحات ==========

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

# --- ورود ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form['identifier']
        password = request.form['password']
        for username, user in users.items():
            if (username == identifier or user.get('name') == identifier) and check_password_hash(user['password'], password):
                session['username'] = username
                flash('🎉 خوش آمدید! از دوباره دیدن شما خوشحالیم', 'success')
                return redirect(url_for('home'))
        flash('نام کاربری یا رمز عبور اشتباه است', 'error')

    content = '''
    <div style="text-align: center; padding: 40px 20px;">
        <h1 style="margin-bottom: 40px; font-size: 28px; background: linear-gradient(135deg, #9B5DE5, #00F5D4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900;">
            دوباره خوش آمدید ❤️
        </h1>
        
        <form method="POST" style="background: rgba(255,255,255,0.05); padding: 30px; border-radius: 24px; backdrop-filter: blur(10px); max-width: 400px; margin: 0 auto;">
            <input type="text" name="identifier" placeholder="نام کاربری یا نام" value="{{ request.form.identifier or '' }}" required>
            <input type="password" name="password" placeholder="رمز عبور" required>
            <button type="submit" class="btn" style="margin: 25px auto 20px; display: block; width: 100%;">
                ورود به گویمیکس
            </button>
        </form>
        
        <p style="margin-top: 25px; font-size: 16px;">
            حساب ندارید؟ <a href="{{ url_for('register') }}" style="color: var(--secondary); text-decoration: none; font-weight: bold;">ثبت‌نام کنید</a>
        </p>
    </div>
    '''

    return make_page("ورود", content)

# --- ثبت‌نام ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        if not username:
            flash('نام کاربری اجباری است', 'error')
            cities_options = "\n".join([f'<option value="{city}">{city}</option>' for city in CITIES])
            return make_page("ثبت‌نام", f'''
            <div style="text-align: center; padding: 30px 20px;">
                <h1 style="margin-bottom: 30px; font-size: 28px; background: linear-gradient(135deg, #9B5DE5, #00F5D4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900;">
                    خوش آمدید به گویمیکس | GOYIMIX
                </h1>
                
                <div class="avatar-container" style="margin: 30px auto;">
                    <div class="avatar" id="avatar-preview">
                        🧑‍💼
                    </div>
                    <div class="upload-btn" onclick="document.getElementById('avatar-input').click()">
                        ➕
                    </div>
                    <input type="file" id="avatar-input" accept="image/*" style="display:none" onchange="previewAvatar(event)">
                </div>

                <form method="POST" style="background: rgba(255,255,255,0.05); padding: 30px; border-radius: 24px; backdrop-filter: blur(10px);">
                    <input type="text" name="name" placeholder="نام (اختیاری)" value="{{ request.form.name or '' }}">
                    
                    <div style="position: relative;">
                        <input type="text" name="username" placeholder="@نام کاربری" value="{{ request.form.username or '' }}" required>
                        <span style="position: absolute; left: 15px; top: 50%; transform: translateY(-50%); color: var(--light-gray);">@</span>
                    </div>
                    
                    <select name="age" required style="text-align: center;">
                        <option value="" disabled selected>سن خود را انتخاب کنید</option>
                        {''.join(f'<option value="{i}">{i} سال</option>' for i in range(12, 81))}
                    </select>
                    
                    <select name="gender" required style="text-align: center;">
                        <option value="" disabled selected>جنسیت خود را انتخاب کنید</option>
                        <option value="پسر">پسر</option>
                        <option value="دختر">دختر</option>
                        <option value="دیگر">دیگر</option>
                    </select>
                    
                    <textarea name="bio" placeholder="بیوگرافی (اختیاری)" rows="3">{{ request.form.bio or '' }}</textarea>
                    
                    <input type="text" name="interests" placeholder="علاقه‌مندی‌ها (اختیاری)" value="{{ request.form.interests or '' }}">
                    
                    <select name="city" required style="text-align: center;">
                        <option value="" disabled selected>شهر خود را انتخاب کنید</option>
                        {cities_options}
                    </select>
                    
                    <input type="password" name="password" placeholder="رمز عبور" required>
                    <input type="password" name="confirm_password" placeholder="تکرار رمز عبور" required>
                    
                    <button type="submit" class="btn" style="margin: 25px auto 20px; display: block; width: 80%;">
                        🎉 ثبت‌نام در گویمیکس
                    </button>
                </form>
                
                <p style="margin-top: 20px; font-size: 16px;">
                    حساب دارید؟ <a href="{{ url_for('login') }}" style="color: var(--secondary); text-decoration: none; font-weight: bold;">وارد شوید</a>
                </p>
            </div>
            ''', '''
            function previewAvatar(event) {
                const file = event.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        document.getElementById('avatar-preview').innerHTML = `<img src="${e.target.result}" style="width:100%;height:100%;border-radius:50%;object-fit:cover;">`;
                    };
                    reader.readAsDataURL(file);
                }
            }
            ''')

        if username in users:
            flash('این نام کاربری قبلاً استفاده شده', 'error')
            cities_options = "\n".join([f'<option value="{city}">{city}</option>' for city in CITIES])
            return make_page("ثبت‌نام", f'''
            <div style="text-align: center; padding: 30px 20px;">
                <h1 style="margin-bottom: 30px; font-size: 28px; background: linear-gradient(135deg, #9B5DE5, #00F5D4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900;">
                    خوش آمدید به گویمیکس | GOYIMIX
                </h1>
                
                <div class="avatar-container" style="margin: 30px auto;">
                    <div class="avatar" id="avatar-preview">
                        🧑‍💼
                    </div>
                    <div class="upload-btn" onclick="document.getElementById('avatar-input').click()">
                        ➕
                    </div>
                    <input type="file" id="avatar-input" accept="image/*" style="display:none" onchange="previewAvatar(event)">
                </div>

                <form method="POST" style="background: rgba(255,255,255,0.05); padding: 30px; border-radius: 24px; backdrop-filter: blur(10px);">
                    <input type="text" name="name" placeholder="نام (اختیاری)" value="{{ request.form.name or '' }}">
                    
                    <div style="position: relative;">
                        <input type="text" name="username" placeholder="@نام کاربری" value="{{ request.form.username or '' }}" required>
                        <span style="position: absolute; left: 15px; top: 50%; transform: translateY(-50%); color: var(--light-gray);">@</span>
                    </div>
                    
                    <select name="age" required style="text-align: center;">
                        <option value="" disabled selected>سن خود را انتخاب کنید</option>
                        {''.join(f'<option value="{i}">{i} سال</option>' for i in range(12, 81))}
                    </select>
                    
                    <select name="gender" required style="text-align: center;">
                        <option value="" disabled selected>جنسیت خود را انتخاب کنید</option>
                        <option value="پسر">پسر</option>
                        <option value="دختر">دختر</option>
                        <option value="دیگر">دیگر</option>
                    </select>
                    
                    <textarea name="bio" placeholder="بیوگرافی (اختیاری)" rows="3">{{ request.form.bio or '' }}</textarea>
                    
                    <input type="text" name="interests" placeholder="علاقه‌مندی‌ها (اختیاری)" value="{{ request.form.interests or '' }}">
                    
                    <select name="city" required style="text-align: center;">
                        <option value="" disabled selected>شهر خود را انتخاب کنید</option>
                        {cities_options}
                    </select>
                    
                    <input type="password" name="password" placeholder="رمز عبور" required>
                    <input type="password" name="confirm_password" placeholder="تکرار رمز عبور" required>
                    
                    <button type="submit" class="btn" style="margin: 25px auto 20px; display: block; width: 80%;">
                        🎉 ثبت‌نام در گویمیکس
                    </button>
                </form>
                
                <p style="margin-top: 20px; font-size: 16px;">
                    حساب دارید؟ <a href="{{ url_for('login') }}" style="color: var(--secondary); text-decoration: none; font-weight: bold;">وارد شوید</a>
                </p>
            </div>
            ''', '''
            function previewAvatar(event) {
                const file = event.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        document.getElementById('avatar-preview').innerHTML = `<img src="${e.target.result}" style="width:100%;height:100%;border-radius:50%;object-fit:cover;">`;
                    };
                    reader.readAsDataURL(file);
                }
            }
            ''')

        if request.form['password'] != request.form['confirm_password']:
            flash('رمز عبور و تکرار آن مطابقت ندارند', 'error')
            cities_options = "\n".join([f'<option value="{city}">{city}</option>' for city in CITIES])
            return make_page("ثبت‌نام", f'''
            <div style="text-align: center; padding: 30px 20px;">
                <h1 style="margin-bottom: 30px; font-size: 28px; background: linear-gradient(135deg, #9B5DE5, #00F5D4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900;">
                    خوش آمدید به گویمیکس | GOYIMIX
                </h1>
                
                <div class="avatar-container" style="margin: 30px auto;">
                    <div class="avatar" id="avatar-preview">
                        🧑‍💼
                    </div>
                    <div class="upload-btn" onclick="document.getElementById('avatar-input').click()">
                        ➕
                    </div>
                    <input type="file" id="avatar-input" accept="image/*" style="display:none" onchange="previewAvatar(event)">
                </div>

                <form method="POST" style="background: rgba(255,255,255,0.05); padding: 30px; border-radius: 24px; backdrop-filter: blur(10px);">
                    <input type="text" name="name" placeholder="نام (اختیاری)" value="{{ request.form.name or '' }}">
                    
                    <div style="position: relative;">
                        <input type="text" name="username" placeholder="@نام کاربری" value="{{ request.form.username or '' }}" required>
                        <span style="position: absolute; left: 15px; top: 50%; transform: translateY(-50%); color: var(--light-gray);">@</span>
                    </div>
                    
                    <select name="age" required style="text-align: center;">
                        <option value="" disabled selected>سن خود را انتخاب کنید</option>
                        {''.join(f'<option value="{i}">{i} سال</option>' for i in range(12, 81))}
                    </select>
                    
                    <select name="gender" required style="text-align: center;">
                        <option value="" disabled selected>جنسیت خود را انتخاب کنید</option>
                        <option value="پسر">پسر</option>
                        <option value="دختر">دختر</option>
                        <option value="دیگر">دیگر</option>
                    </select>
                    
                    <textarea name="bio" placeholder="بیوگرافی (اختیاری)" rows="3">{{ request.form.bio or '' }}</textarea>
                    
                    <input type="text" name="interests" placeholder="علاقه‌مندی‌ها (اختیاری)" value="{{ request.form.interests or '' }}">
                    
                    <select name="city" required style="text-align: center;">
                        <option value="" disabled selected>شهر خود را انتخاب کنید</option>
                        {cities_options}
                    </select>
                    
                    <input type="password" name="password" placeholder="رمز عبور" required>
                    <input type="password" name="confirm_password" placeholder="تکرار رمز عبور" required>
                    
                    <button type="submit" class="btn" style="margin: 25px auto 20px; display: block; width: 80%;">
                        🎉 ثبت‌نام در گویمیکس
                    </button>
                </form>
                
                <p style="margin-top: 20px; font-size: 16px;">
                    حساب دارید؟ <a href="{{ url_for('login') }}" style="color: var(--secondary); text-decoration: none; font-weight: bold;">وارد شوید</a>
                </p>
            </div>
            ''', '''
            function previewAvatar(event) {
                const file = event.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        document.getElementById('avatar-preview').innerHTML = `<img src="${e.target.result}" style="width:100%;height:100%;border-radius:50%;object-fit:cover;">`;
                    };
                    reader.readAsDataURL(file);
                }
            }
            ''')

        gender = request.form['gender']
        default_avatar = "🧑‍💼" if gender == "پسر" else "🧕"
        
        user = {
            "name": request.form.get('name', '').strip(),
            "username": username,
            "age": int(request.form['age']),
            "gender": gender,
            "bio": request.form.get('bio', '').strip(),
            "interests": request.form.get('interests', '').strip(),
            "city": request.form['city'],
            "password": generate_password_hash(request.form['password']),
            "avatar": default_avatar,
            "show_in_home": True
        }
        
        users[username] = user
        session['username'] = username
        flash('🎉 خوش آمدید به گویمیکس! حساب شما با موفقیت ایجاد شد', 'success')
        return redirect(url_for('home'))

    cities_options = "\n".join([f'<option value="{city}">{city}</option>' for city in CITIES])
    content = f'''
    <div style="text-align: center; padding: 30px 20px;">
        <h1 style="margin-bottom: 30px; font-size: 28px; background: linear-gradient(135deg, #9B5DE5, #00F5D4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900;">
            خوش آمدید به گویمیکس | GOYIMIX
        </h1>
        
        <div class="avatar-container" style="margin: 30px auto;">
            <div class="avatar" id="avatar-preview">
                🧑‍💼
            </div>
            <div class="upload-btn" onclick="document.getElementById('avatar-input').click()">
                ➕
            </div>
            <input type="file" id="avatar-input" accept="image/*" style="display:none" onchange="previewAvatar(event)">
        </div>

        <form method="POST" style="background: rgba(255,255,255,0.05); padding: 30px; border-radius: 24px; backdrop-filter: blur(10px);">
            <input type="text" name="name" placeholder="نام (اختیاری)" value="{{ request.form.name or '' }}">
            
            <div style="position: relative;">
                <input type="text" name="username" placeholder="@نام کاربری" value="{{ request.form.username or '' }}" required>
                <span style="position: absolute; left: 15px; top: 50%; transform: translateY(-50%); color: var(--light-gray);">@</span>
            </div>
            
            <select name="age" required style="text-align: center;">
                <option value="" disabled selected>سن خود را انتخاب کنید</option>
                {''.join(f'<option value="{i}">{i} سال</option>' for i in range(12, 81))}
            </select>
            
            <select name="gender" required style="text-align: center;">
                <option value="" disabled selected>جنسیت خود را انتخاب کنید</option>
                <option value="پسر">پسر</option>
                <option value="دختر">دختر</option>
                <option value="دیگر">دیگر</option>
            </select>
            
            <textarea name="bio" placeholder="بیوگرافی (اختیاری)" rows="3">{{ request.form.bio or '' }}</textarea>
            
            <input type="text" name="interests" placeholder="علاقه‌مندی‌ها (اختیاری)" value="{{ request.form.interests or '' }}">
            
            <select name="city" required style="text-align: center;">
                <option value="" disabled selected>شهر خود را انتخاب کنید</option>
                {cities_options}
            </select>
            
            <input type="password" name="password" placeholder="رمز عبور" required>
            <input type="password" name="confirm_password" placeholder="تکرار رمز عبور" required>
            
            <button type="submit" class="btn" style="margin: 25px auto 20px; display: block; width: 80%;">
                🎉 ثبت‌نام در گویمیکس
            </button>
        </form>
        
        <p style="margin-top: 20px; font-size: 16px;">
            حساب دارید؟ <a href="{{ url_for('login') }}" style="color: var(--secondary); text-decoration: none; font-weight: bold;">وارد شوید</a>
        </p>
    </div>
    '''

    scripts = '''
    function previewAvatar(event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                document.getElementById('avatar-preview').innerHTML = `<img src="${e.target.result}" style="width:100%;height:100%;border-radius:50%;object-fit:cover;">`;
            };
            reader.readAsDataURL(file);
        }
    }
    '''

    return make_page("ثبت‌نام", content, scripts)

# --- خروج ---
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('با موفقیت از حساب خود خارج شدید', 'success')
    return redirect(url_for('login'))

# --- داشبورد ---
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    content = '''
    <div style="text-align: center; padding: 40px 20px;">
        <h1 style="font-size: 32px; margin-bottom: 20px; background: linear-gradient(135deg, #9B5DE5, #00F5D4); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            GOYIMIX | گویمیکس
        </h1>
        <p style="font-size: 18px; margin-bottom: 30px;">خوش آمدید {{ session.username }}! 🎉</p>
        <a href="{{ url_for('home') }}" class="btn" style="display: inline-block; margin: 20px;">
            <i class="fas fa-arrow-right"></i> رفتن به خانه
        </a>
        <a href="{{ url_for('chat_list') }}" class="btn" style="display: inline-block; margin: 20px; background: linear-gradient(135deg, #F15BB5, #00F5D4);">
            <i class="fas fa-comments"></i> چت‌های من
        </a>
    </div>
    '''
    return make_page("داشبورد", content)

# --- پروفایل ---
@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    user = users.get(session['username'])
    if not user:
        flash('حساب کاربری شما یافت نشد', 'error')
        return redirect(url_for('login'))
    
    content = f'''
    <div style="padding: 20px;">
        <h1 style="text-align: center; margin-bottom: 30px; font-size: 28px;">پروفایل من</h1>
        
        <div style="text-align: center; margin-bottom: 30px;">
            <div class="avatar-container" style="width: 150px; height: 150px; margin: 0 auto;">
                <div class="avatar" style="width: 100%; height: 100%; font-size: 48px;">
                    {user['avatar']}
                </div>
            </div>
        </div>
        
        <div class="card">
            <div style="position: relative; padding: 15px 15px 15px 45px; border-bottom: 1px solid rgba(255,255,255,0.1);">
                <strong>نام:</strong> {user.get('name', '—')}
                <a href="{{{{ url_for('edit_profile_field', field='name') }}}}" class="edit-icon">
                    <i class="fas fa-pencil"></i>
                </a>
            </div>
            <div style="position: relative; padding: 15px 15px 15px 45px; border-bottom: 1px solid rgba(255,255,255,0.1);">
                <strong>نام کاربری:</strong> @{user['username']}
                <a href="{{{{ url_for('edit_profile_field', field='username') }}}}" class="edit-icon">
                    <i class="fas fa-pencil"></i>
                </a>
            </div>
            <div style="position: relative; padding: 15px 15px 15px 45px; border-bottom: 1px solid rgba(255,255,255,0.1);">
                <strong>سن:</strong> {user['age']} سال
                <a href="{{{{ url_for('edit_profile_field', field='age') }}}}" class="edit-icon">
                    <i class="fas fa-pencil"></i>
                </a>
            </div>
            <div style="position: relative; padding: 15px 15px 15px 45px; border-bottom: 1px solid rgba(255,255,255,0.1);">
                <strong>جنسیت:</strong> {user['gender']}
                <a href="{{{{ url_for('edit_profile_field', field='gender') }}}}" class="edit-icon">
                    <i class="fas fa-pencil"></i>
                </a>
            </div>
            <div style="position: relative; padding: 15px 15px 15px 45px; border-bottom: 1px solid rgba(255,255,255,0.1);">
                <strong>بیو:</strong> {user.get('bio', '—')}
                <a href="{{{{ url_for('edit_profile_field', field='bio') }}}}" class="edit-icon">
                    <i class="fas fa-pencil"></i>
                </a>
            </div>
            <div style="position: relative; padding: 15px 15px 15px 45px; border-bottom: 1px solid rgba(255,255,255,0.1);">
                <strong>شهر:</strong> {user['city']}
                <a href="{{{{ url_for('edit_profile_field', field='city') }}}}" class="edit-icon">
                    <i class="fas fa-pencil"></i>
                </a>
            </div>
            <div style="position: relative; padding: 15px 15px 15px 45px;">
                <div class="password-container">
                    <strong>رمز عبور:</strong> ●●●●●●●●
                    <button type="button" class="toggle-password">
                        <i class="fas fa-eye"></i>
                    </button>
                    <input type="password" value="password123" style="opacity: 0; position: absolute; pointer-events: none;">
                    <a href="{{{{ url_for('edit_profile_field', field='password') }}}}" class="edit-icon">
                        <i class="fas fa-pencil"></i>
                    </a>
                </div>
            </div>
        </div>
        
        <div class="card" style="margin-top: 30px;">
            <h3 style="margin-bottom: 20px; text-align: center;">تنظیمات نمایش</h3>
            <div style="display: flex; align-items: center; justify-content: space-between; padding: 15px;">
                <span>نمایش پروفایل در خانه</span>
                <label class="toggle-switch">
                    <input type="checkbox" onchange="toggleShowInHome(this)" {'checked' if user.get('show_in_home', True) else ''}>
                    <span class="slider"></span>
                </label>
            </div>
        </div>
        
        <div style="text-align: center; margin: 40px 0;">
            <a href="{{{{ url_for('logout') }}}}" class="btn" style="margin: 10px; background: #666;">
                <i class="fas fa-sign-out-alt"></i> خروج از حساب
            </a>
            <button type="button" class="btn" style="margin: 10px; background: #ff3b30;" onclick="showDeleteAccountModal()">
                <i class="fas fa-trash"></i> حذف حساب
            </button>
        </div>
    </div>

    <div id="deleteAccountModal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 1000; justify-content: center; align-items: center;">
        <div class="card" style="max-width: 400px; margin: 0; animation: slideIn 0.3s ease;">
            <h3 style="text-align: center; margin-bottom: 20px;">⚠️ حذف حساب کاربری</h3>
            <p style="text-align: center; margin-bottom: 20px;">آیا مطمئنید می‌خواهید حساب خود را حذف کنید؟ این عمل غیرقابل بازگشت است!</p>
            <form method="POST" action="{{{{ url_for('delete_account') }}}}">
                <input type="password" name="password" placeholder="رمز عبور خود را وارد کنید" required style="margin-bottom: 15px;">
                <div style="display: flex; gap: 10px; justify-content: center;">
                    <button type="submit" class="btn" style="background: #ff3b30;">بله، حذف شود</button>
                    <button type="button" class="btn" style="background: #666;" onclick="hideDeleteAccountModal()">انصراف</button>
                </div>
            </form>
        </div>
    </div>
    '''

    scripts = '''
    function toggleShowInHome(checkbox) {
        fetch('{{ url_for("toggle_show_in_home") }}', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({show: checkbox.checked})
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('تنظیمات با موفقیت ذخیره شد!');
            } else {
                alert('خطا در ذخیره تنظیمات!');
                checkbox.checked = !checkbox.checked;
            }
        });
    }

    function showDeleteAccountModal() {
        document.getElementById('deleteAccountModal').style.display = 'flex';
    }

    function hideDeleteAccountModal() {
        document.getElementById('deleteAccountModal').style.display = 'none';
    }
    '''

    return make_page("پروفایل من", content, scripts)

# --- ویرایش فیلدهای پروفایل ---
@app.route('/edit-profile/<field>', methods=['GET', 'POST'])
def edit_profile_field(field):
    if 'username' not in session:
        return redirect(url_for('login'))
    user = users.get(session['username'])
    if not user:
        flash('حساب کاربری شما یافت نشد', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        if field == 'password':
            current_password = request.form['current_password']
            new_password = request.form['new_value']
            confirm_password = request.form['confirm_password']
            
            if not check_password_hash(user['password'], current_password):
                flash('رمز عبور فعلی اشتباه است', 'error')
            elif new_password != confirm_password:
                flash('رمز عبور جدید و تکرار آن مطابقت ندارند', 'error')
            else:
                user['password'] = generate_password_hash(new_password)
                flash('رمز عبور با موفقیت تغییر کرد', 'success')
                return redirect(url_for('profile'))
        elif field in ['age', 'gender', 'city', 'name', 'bio']:
            user[field] = request.form['new_value']
            flash(f'{field} با موفقیت به‌روز شد', 'success')
            return redirect(url_for('profile'))
        else:
            flash('فیلد نامعتبر', 'error')
    
    # ساخت select برای فیلدهای خاص
    field_input = ""
    if field == 'age':
        options = ''.join([f'<option value="{i}" {"selected" if i == user.get("age", 0) else ""}>{i} سال</option>' for i in range(12, 81)])
        field_input = f'<select name="new_value" required style="text-align: center;">{options}</select>'
    elif field == 'gender':
        options = ''.join([f'<option value="{g}" {"selected" if g == user.get("gender", "") else ""}>{g}</option>' for g in ["پسر", "دختر", "دیگر"]])
        field_input = f'<select name="new_value" required style="text-align: center;">{options}</select>'
    elif field == 'city':
        options = ''.join([f'<option value="{c}" {"selected" if c == user.get("city", "") else ""}>{c}</option>' for c in CITIES])
        field_input = f'<select name="new_value" required style="text-align: center;">{options}</select>'
    elif field == 'password':
        field_input = '''
        <input type="password" name="current_password" placeholder="رمز عبور فعلی" required>
        <input type="password" name="new_value" placeholder="رمز عبور جدید" required>
        <input type="password" name="confirm_password" placeholder="تکرار رمز عبور جدید" required>
        '''
    else:
        field_input = f'<input type="text" name="new_value" placeholder="{field} جدید" value="{user.get(field, "")}" required>'
    
    content = f'''
    <div style="padding: 20px; max-width: 500px; margin: 0 auto;">
        <h1 style="text-align: center; margin-bottom: 30px;">ویرایش {field}</h1>
        
        <div class="card">
            <form method="POST">
                {field_input}
                <div style="display: flex; gap: 10px; margin-top: 20px;">
                    <button type="submit" class="btn" style="flex: 1;">ذخیره تغییرات</button>
                    <a href="{{{{ url_for('profile') }}}}" class="btn" style="flex: 1; background: #666;">انصراف</a>
                </div>
            </form>
        </div>
    </div>
    '''
    
    return make_page(f"ویرایش {field}", content)

# --- تغییر وضعیت نمایش پروفایل در خانه ---
@app.route('/toggle-show-in-home', methods=['POST'])
def toggle_show_in_home():
    if 'username' not in session:
        return jsonify({"success": False, "error": "Unauthorized"})
    user = users.get(session['username'])
    if not user:
        return jsonify({"success": False, "error": "User not found"})
    
    data = request.get_json()
    user['show_in_home'] = data.get('show', True)
    return jsonify({"success": True})

# --- حذف حساب ---
@app.route('/delete_account', methods=['POST'])
def delete_account():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    password = request.form['password']
    
    if not check_password_hash(users[username]['password'], password):
        flash('رمز عبور اشتباه است', 'error')
        return redirect(url_for('profile'))
    
    # حذف کاربر و تمام داده‌های مرتبط
    del users[username]
    if username in notifications:
        del notifications[username]
    if username in user_chats:
        for chat_id in user_chats[username]:
            if chat_id in chats:
                del chats[chat_id]
        del user_chats[username]
    
    # حذف لایک‌های مرتبط
    keys_to_delete = [key for key in likes.keys() if key[0] == username or key[1] == username]
    for key in keys_to_delete:
        del likes[key]
    
    session.pop('username', None)
    flash('حساب شما با موفقیت حذف شد. 😔', 'success')
    return redirect(url_for('register'))

# --- خانه با فیلتر ---
@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    current_user = users[session['username']]
    
    # دریافت فیلترها
    same_age = request.args.get('same_age') == '1'
    same_gender = request.args.get('same_gender') == '1'
    opposite_gender = request.args.get('opposite_gender') == '1'
    same_city = request.args.get('same_city') == '1'
    
    filtered_users = []
    for username, user in users.items():
        if username == session['username']:
            continue
        if not user.get('show_in_home', True):
            continue
        if same_age and user['age'] != current_user['age']:
            continue
        if same_gender and user['gender'] != current_user['gender']:
            continue
        if opposite_gender and user['gender'] == current_user['gender']:
            continue
        if same_city and user['city'] != current_user['city']:
            continue
        filtered_users.append(user)
    
    # ساخت کارت‌های کاربران
    users_cards = ""
    for user in filtered_users:
        is_liked = (session['username'], user['username']) in likes
        heart_icon = "fas fa-heart" if is_liked else "far fa-heart"
        heart_bg = "#ff3b30" if is_liked else "linear-gradient(135deg, var(--primary), var(--secondary))"
        
        users_cards += f'''
        <div class="card" style="display: flex; align-items: center; gap: 20px; padding: 20px;">
            <div class="avatar" style="width: 80px; height: 80px; font-size: 32px;">
                {user['avatar']}
            </div>
            <div style="flex: 1;">
                <h3 style="margin-bottom: 5px;">{user.get('name', user['username'])}</h3>
                <p style="color: var(--light-gray); margin-bottom: 5px;">@{user['username']} • {user['age']} سال • {user['gender']}</p>
                {'<p style="margin-bottom: 5px;">'+user['bio']+'</p>' if user.get('bio') else ''}
                <p style="color: var(--secondary);">📍 {user['city']}</p>
            </div>
            <div style="display: flex; flex-direction: column; gap: 10px;">
                <form method="POST" action="{{{{ url_for('toggle_like', username="'''+user['username']+'''") }}}}" style="margin: 0;">
                    <button type="submit" class="btn btn-small" style="padding: 10px 15px; background: {heart_bg};">
                        <i class="{heart_icon}"></i>
                    </button>
                </form>
                <form method="POST" action="{{{{ url_for('request_chat', username="'''+user['username']+'''") }}}}" style="margin: 0;">
                    <button type="submit" class="btn btn-small" style="padding: 10px 15px;">
                        <i class="fas fa-comment"></i>
                    </button>
                </form>
            </div>
        </div>
        '''
    
    content = f'''
    <div style="padding: 20px;">
        <h1 style="text-align: center; margin-bottom: 30px; font-size: 28px;">کشف کاربران 🌟</h1>
        
        <div style="text-align: center; margin-bottom: 30px; display: flex; flex-wrap: wrap; justify-content: center; gap: 10px;">
            <button class="filter-btn {'active' if same_age else ''}" data-filter="same_age">هم‌سن</button>
            <button class="filter-btn {'active' if same_gender else ''}" data-filter="same_gender">هم‌جنسیت</button>
            <button class="filter-btn {'active' if opposite_gender else ''}" data-filter="opposite_gender">ناهم‌جنسیت</button>
            <button class="filter-btn {'active' if same_city else ''}" data-filter="same_city">هم‌شهر</button>
        </div>
        
        {users_cards if users_cards else '''
        <div class="card" style="text-align: center; padding: 40px;">
            <h3>کاربری یافت نشد 😔</h3>
            <p>فیلترها را تغییر دهید یا بعداً دوباره امتحان کنید.</p>
        </div>
        '''}
    </div>
    '''
    
    return make_page("خانه", content)

# --- تغییر وضعیت لایک ---
@app.route('/toggle-like/<username>', methods=['POST'])
def toggle_like(username):
    if 'username' not in session:
        return redirect(url_for('login'))
    if username not in users:
        flash('کاربر مورد نظر یافت نشد', 'error')
        return redirect(url_for('home'))
    
    from_user = session['username']
    key = (from_user, username)
    
    if key in likes:
        del likes[key]
        # حذف اعلان لایک
        if username in notifications:
            notifications[username] = [n for n in notifications[username] if not (n.get('from_user') == from_user and n['type'] == 'like')]
        flash('لایک با موفقیت حذف شد', 'success')
    else:
        likes[key] = True
        add_notification(username, f"کاربر @{from_user} شما را لایک کرد", "like", from_user)
        flash('کاربر با موفقیت لایک شد ❤️', 'success')
    
    # Redirect به همان صفحه‌ای که کاربر در آن بود
    referrer = request.headers.get("Referer")
    if referrer and 'search' in referrer:
        return redirect(url_for('search'))
    else:
        return redirect(url_for('home'))

# --- درخواست چت ---
@app.route('/request-chat/<username>', methods=['POST'])
def request_chat(username):
    if 'username' not in session:
        return redirect(url_for('login'))
    if username not in users:
        flash('کاربر مورد نظر یافت نشد', 'error')
        return redirect(url_for('home'))
    
    from_user = session['username']
    add_notification(username, f"کاربر @{from_user} درخواست چت داده", "chat_request", from_user)
    flash('درخواست چت با موفقیت ارسال شد ✅', 'success')
    
    referrer = request.headers.get("Referer")
    if referrer and 'search' in referrer:
        return redirect(url_for('search'))
    else:
        return redirect(url_for('home'))

# --- قبول درخواست چت ---
@app.route('/accept-chat/<from_user>', methods=['POST'])
def accept_chat(from_user):
    if 'username' not in session:
        return redirect(url_for('login'))
    if from_user not in users:
        flash('کاربر مورد نظر یافت نشد', 'error')
        return redirect(url_for('view_notifications'))
    
    current_user = session['username']
    chat_id = create_chat_id(current_user, from_user)
    
    if chat_id not in chats:
        chats[chat_id] = {
            "messages": [],
            "participants": [current_user, from_user]
        }
    
    # اضافه کردن چت به لیست چت‌های هر دو کاربر
    for user in [current_user, from_user]:
        if user not in user_chats:
            user_chats[user] = []
        if chat_id not in user_chats[user]:
            user_chats[user].append(chat_id)
    
    # حذف اعلان درخواست چت
    if current_user in notifications:
        notifications[current_user] = [n for n in notifications[current_user] if not (n.get('from_user') == from_user and n['type'] == 'chat_request')]
    
    flash('درخواست چت پذیرفته شد! می‌توانید شروع به چت کنید 💬', 'success')
    return redirect(url_for('chat_page', chat_id=chat_id))

# --- رد درخواست چت ---
@app.route('/reject-chat/<from_user>', methods=['POST'])
def reject_chat(from_user):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    current_user = session['username']
    if current_user in notifications:
        notifications[current_user] = [n for n in notifications[current_user] if not (n.get('from_user') == from_user and n['type'] == 'chat_request')]
    
    flash('درخواست چت رد شد', 'info')
    return redirect(url_for('view_notifications'))

# --- بلاک کردن کاربر ---
@app.route('/block-user/<username>', methods=['POST'])
def block_user(username):
    if 'username' not in session:
        return redirect(url_for('login'))
    # در این نسخه ساده، فقط اعلان را حذف می‌کنیم
    current_user = session['username']
    if current_user in notifications:
        notifications[current_user] = [n for n in notifications[current_user] if not (n.get('from_user') == username)]
    flash(f'کاربر @{username} بلاک شد', 'success')
    return redirect(url_for('view_notifications'))

# --- اعلان‌ها ---
@app.route('/notifications')
def view_notifications():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    user_notifications = notifications.get(username, [])
    # علامت زدن به عنوان خوانده
    for notif in user_notifications:
        notif['read'] = True
    
    notifications_html = ""
    for notif in user_notifications:
        from_avatar = "🔔"
        if notif.get('from_user') and notif['from_user'] in users:
            from_avatar = users[notif['from_user']]['avatar']
        
        action_buttons = ""
        if notif['type'] == 'chat_request':
            action_buttons = f'''
            <div class="action-btns">
                <form method="POST" action="{{{{ url_for('accept_chat', from_user="{notif['from_user']}") }}}}" style="display: inline;">
                    <button type="submit" class="btn btn-small" style="padding: 8px 16px; background: #00F5D4; color: black;">
                        <i class="fas fa-check"></i> قبول
                    </button>
                </form>
                <form method="POST" action="{{{{ url_for('reject_chat', from_user="{notif['from_user']}") }}}}" style="display: inline;">
                    <button type="submit" class="btn btn-small" style="padding: 8px 16px; background: #666;">
                        <i class="fas fa-times"></i> رد
                    </button>
                </form>
                <form method="POST" action="{{{{ url_for('block_user', username="{notif['from_user']}") }}}}" style="display: inline;">
                    <button type="submit" class="btn btn-small" style="padding: 8px 16px; background: #ff3b30;">
                        <i class="fas fa-ban"></i> بلاک
                    </button>
                </form>
            </div>
            '''
        
        notifications_html += f'''
        <div class="card" style="margin-bottom: 20px; padding: 20px; position: relative;">
            <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px;">
                <div class="avatar" style="width: 50px; height: 50px; font-size: 24px;">
                    {from_avatar}
                </div>
                <div>
                    <h3 style="margin-bottom: 5px;">{notif['msg']}</h3>
                    <p style="color: var(--light-gray); font-size: 14px;">{notif['type']}</p>
                </div>
            </div>
            {action_buttons}
        </div>
        '''
    
    content = f'''
    <div style="padding: 20px;">
        <h1 style="text-align: center; margin-bottom: 30px; font-size: 28px;">🔔 اعلان‌های من</h1>
        
        {notifications_html if notifications_html else '''
        <div class="card" style="text-align: center; padding: 40px;">
            <h3>اعلانی وجود ندارد 🌙</h3>
            <p>وقتی کسی شما را لایک کند یا درخواست چت بدهد، اینجا نمایش داده می‌شود.</p>
        </div>
        '''}
    </div>
    '''
    
    return make_page("اعلان‌ها", content)

# --- جستجو ---
@app.route('/search')
def search():
    if 'username' not in session:
        return redirect(url_for('login'))
    query = request.args.get('q', '').strip()
    results = []
    if query:
        if query.startswith('@'):
            username = query[1:]
            if username in users:
                results.append(users[username])
        else:
            for user in users.values():
                if query.lower() in (user.get('name', '').lower() or user['username'].lower()):
                    results.append(user)
    
    # ساخت کارت‌های نتایج
    results_cards = ""
    for user in results:
        is_liked = (session['username'], user['username']) in likes
        heart_icon = "fas fa-heart" if is_liked else "far fa-heart"
        heart_bg = "#ff3b30" if is_liked else "linear-gradient(135deg, var(--primary), var(--secondary))"
        
        results_cards += f'''
        <div class="card" style="display: flex; align-items: center; gap: 20px; padding: 20px;">
            <div class="avatar" style="width: 80px; height: 80px; font-size: 32px;">
                {user['avatar']}
            </div>
            <div style="flex: 1;">
                <h3 style="margin-bottom: 5px;">{user.get('name', user['username'])}</h3>
                <p style="color: var(--light-gray); margin-bottom: 5px;">@{user['username']} • {user['age']} سال • {user['gender']}</p>
                {'<p style="margin-bottom: 5px;">'+user['bio']+'</p>' if user.get('bio') else ''}
                <p style="color: var(--secondary);">📍 {user['city']}</p>
            </div>
            <div style="display: flex; flex-direction: column; gap: 10px;">
                <form method="POST" action="{{{{ url_for('toggle_like', username="'''+user['username']+'''") }}}}" style="margin: 0;">
                    <button type="submit" class="btn btn-small" style="padding: 10px 15px; background: {heart_bg};">
                        <i class="{heart_icon}"></i>
                    </button>
                </form>
                <a href="{{{{ url_for('chat_with_user', username="'''+user['username']+'''") }}}}" class="btn btn-small" style="padding: 10px 15px; text-align: center;">
                    <i class="fas fa-comment"></i>
                </a>
            </div>
        </div>
        '''
    
    content = f'''
    <div style="padding: 20px;">
        <h1 style="text-align: center; margin-bottom: 30px; font-size: 28px;">🔍 جستجوی کاربران</h1>
        
        <form method="GET" style="margin-bottom: 30px;">
            <div style="display: flex; gap: 10px;">
                <input type="text" name="q" placeholder="جستجو بر اساس نام یا @نام کاربری" value="{query}" style="flex: 1;">
                <button type="submit" class="btn" style="padding: 14px 24px; width: auto; white-space: nowrap;">
                    <i class="fas fa-search"></i> جستجو
                </button>
            </div>
        </form>
        
        {results_cards if results_cards else (f'''
        <div class="card" style="text-align: center; padding: 40px;">
            <h3>کاربری یافت نشد 😔</h3>
            <p>لطفاً نام یا نام کاربری را دقیق‌تر وارد کنید.</p>
        </div>
        ''' if query else '')}
    </div>
    '''
    
    return make_page("جستجو", content)

# --- چت با کاربر خاص ---
@app.route('/chat-with/<username>')
def chat_with_user(username):
    if 'username' not in session:
        return redirect(url_for('login'))
    if username not in users:
        flash('کاربر مورد نظر یافت نشد', 'error')
        return redirect(url_for('search'))
    
    current_user = session['username']
    chat_id = create_chat_id(current_user, username)
    
    if chat_id not in chats:
        chats[chat_id] = {
            "messages": [],
            "participants": [current_user, username]
        }
    
    if current_user not in user_chats:
        user_chats[current_user] = []
    if chat_id not in user_chats[current_user]:
        user_chats[current_user].append(chat_id)
    
    return redirect(url_for('chat_page', chat_id=chat_id))

# --- لیست چت‌ها ---
@app.route('/chat')
def chat_list():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    user_chat_list = []
    for chat_id in user_chats.get(username, []):
        if chat_id in chats:
            other_username = [u for u in chats[chat_id]['participants'] if u != username][0]
            last_msg = chats[chat_id]['messages'][-1] if chats[chat_id]['messages'] else None
            user_chat_list.append({
                "chat_id": chat_id,
                "other_user": users[other_username],
                "last_message": last_msg['text'] if last_msg else "هنوز پیامی وجود ندارد"
            })
    
    # ساخت کارت‌های چت
    chat_cards = ""
    for chat in user_chat_list:
        chat_cards += f'''
        <div class="card" style="display: flex; align-items: center; gap: 20px; padding: 20px; position: relative;">
            <div class="avatar" style="width: 60px; height: 60px; font-size: 28px;">
                {chat['other_user']['avatar']}
            </div>
            <div style="flex: 1;">
                <h3 style="margin-bottom: 5px;">{chat['other_user'].get('name', chat['other_user']['username'])}</h3>
                <p style="color: var(--light-gray);">@{chat['other_user']['username']}</p>
                <p style="margin-top: 10px;">{chat['last_message']}</p>
            </div>
            <div style="display: flex; flex-direction: column; gap: 10px;">
                <a href="{{{{ url_for('chat_page', chat_id="{chat['chat_id']}") }}}}" class="btn btn-small" style="padding: 8px 16px;">
                    <i class="fas fa-arrow-right"></i>
                </a>
                <form method="POST" action="{{{{ url_for('delete_chat', chat_id="{chat['chat_id']}") }}}}" style="margin: 0;">
                    <button type="submit" class="btn btn-small" style="padding: 8px 16px; background: #ff3b30;" onclick="return confirm('آیا مطمئنید می‌خواهید این چت را حذف کنید؟')">
                        <i class="fas fa-trash"></i>
                    </button>
                </form>
            </div>
        </div>
        '''
    
    content = f'''
    <div style="padding: 20px;">
        <h1 style="text-align: center; margin-bottom: 30px; font-size: 28px;">💬 چت‌های من</h1>
        
        {chat_cards if chat_cards else '''
        <div class="card" style="text-align: center; padding: 40px;">
            <h3>چتی وجود ندارد 🌙</h3>
            <p>وقتی کسی درخواست چت شما را بپذیرد، اینجا نمایش داده می‌شود.</p>
            <a href="{{ url_for('home') }}" class="btn" style="margin-top: 20px;">
                <i class="fas fa-users"></i> کشف کاربران
            </a>
        </div>
        '''}
    </div>
    '''
    
    return make_page("چت‌های من", content)

# --- صفحه چت ---
@app.route('/chat/<chat_id>', methods=['GET', 'POST'])
def chat_page(chat_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    if chat_id not in chats:
        flash('چت مورد نظر یافت نشد', 'error')
        return redirect(url_for('chat_list'))
    
    username = session['username']
    if username not in chats[chat_id]['participants']:
        flash('دسترسی غیرمجاز', 'error')
        return redirect(url_for('chat_list'))
    
    other_username = [u for u in chats[chat_id]['participants'] if u != username][0]
    target_user = users[other_username]
    
    if request.method == 'POST':
        message = request.form['message'].strip()
        if message:
            msg_data = {
                "id": str(uuid.uuid4()),
                "from": username,
                "text": message,
                "timestamp": "الان"
            }
            chats[chat_id]['messages'].append(msg_data)
            # اعلان به کاربر مقابل
            add_notification(other_username, f"پیام جدید از @{username}", "new_message", username)
            flash('پیام با موفقیت ارسال شد', 'success')
    
    # ساخت پیام‌ها
    messages_html = ""
    for msg in chats[chat_id]['messages']:
        msg_class = "sent" if msg['from'] == username else "received"
        messages_html += f'''
        <div style="display: flex; {'justify-content: flex-end;' if msg['from'] == username else ''}">
            <div class="message-container">
                <div class="message {msg_class}">
                    {msg['text']}
                    <div style="font-size: 12px; text-align: right; margin-top: 5px; opacity: 0.7;">
                        {msg['timestamp']}
                    </div>
                </div>
            </div>
        </div>
        '''
    
    if not messages_html:
        messages_html = '''
        <div style="text-align: center; color: var(--light-gray); padding: 40px;">
            هنوز پیامی وجود ندارد. اولین پیام را شما بفرستید! 🚀
        </div>
        '''
    
    content = f'''
    <div style="display: flex; flex-direction: column; min-height: 100vh;">
        <div class="chat-header">
            <a href="{{{{ url_for('chat_list') }}}}" class="back-btn">
                <i class="fas fa-arrow-right"></i>
            </a>
            <div class="avatar" style="width: 50px; height: 50px; font-size: 24px;">
                {target_user['avatar']}
            </div>
            <div>
                <h3>{target_user.get('name', target_user['username'])}</h3>
                <p style="color: var(--light-gray); font-size: 14px;">@{target_user['username']}</p>
            </div>
            <form method="POST" action="{{{{ url_for('delete_chat', chat_id="{chat_id}") }}}}" style="margin-left: 15px;">
                <button type="submit" class="btn btn-small" style="padding: 8px 12px; background: #ff3b30;" onclick="return confirm('آیا مطمئنید می‌خواهید این چت را حذف کنید؟')">
                    <i class="fas fa-trash"></i>
                </button>
            </form>
        </div>
        
        <div style="flex: 1; overflow-y: auto; padding: 20px;">
            {messages_html}
        </div>
        
        <div class="chat-input">
            <form method="POST" style="display: flex; gap: 10px; width: 100%;">
                <input type="text" name="message" placeholder="پیام خود را بنویسید..." required>
                <button type="submit" class="btn" style="padding: 14px 24px; white-space: nowrap;">
                    <i class="fas fa-paper-plane"></i> ارسال
                </button>
            </form>
        </div>
    </div>
    '''
    
    return make_page(f"چت با {target_user.get('name', target_user['username'])}", content)

# --- حذف چت ---
@app.route('/delete_chat/<chat_id>', methods=['POST'])
def delete_chat(chat_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    if chat_id in user_chats.get(username, []):
        user_chats[username].remove(chat_id)
        flash('چت با موفقیت حذف شد', 'success')
    else:
        flash('چت مورد نظر یافت نشد', 'error')
    return redirect(url_for('chat_list'))

# ========== API برای دریافت تعداد اعلان‌های خوانده نشده ==========
@app.route('/api/notifications/unread')
def api_unread_notifications():
    if 'username' not in session:
        return jsonify({"count": 0})
    count = get_unread_notifications_count(session['username'])
    return jsonify({"count": count})

# ========== اجرا ==========
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)