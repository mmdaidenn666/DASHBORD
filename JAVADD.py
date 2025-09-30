from flask import Flask, render_template_string
import os

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>سایت رسمی دبیرستان جوادالائمه</title>
    <style>
        @font-face {
            font-family: 'Vazir';
            src: url('https://cdn.jsdelivr.net/gh/rastikerdar/vazir-font@v30.1.0/dist/Vazir.woff2') format('woff2');
        }

        body {
            margin: 0;
            padding: 0;
            font-family: 'Vazir', Tahoma, sans-serif;
            background-color: white;
            overflow: hidden;
            direction: rtl;
        }

        .border-light {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 10;
            box-shadow: inset 0 0 20px rgba(128, 0, 128, 0.6), inset 0 0 40px rgba(0, 100, 255, 0.5);
            animation: colorShift 3s infinite alternate;
        }

        @keyframes colorShift {
            0% { box-shadow: inset 0 0 20px rgba(128, 0, 128, 0.6), inset 0 0 40px rgba(0, 100, 255, 0.5); }
            100% { box-shadow: inset 0 0 20px rgba(0, 100, 255, 0.6), inset 0 0 40px rgba(128, 0, 128, 0.5); }
        }

        .logo {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 250px;
            height: auto;
            opacity: 0;
            z-index: 20;
            transition: opacity 1s ease, transform 1.5s ease;
        }

        .logo.fade-in {
            animation: fadeInScale 2s forwards;
        }

        @keyframes fadeInScale {
            from { opacity: 0; transform: translate(-50%, -50%) scale(0.1); }
            to { opacity: 1; transform: translate(-50%, -50%) scale(1); }
        }

        .welcome-text {
            position: absolute;
            top: 60%;
            left: 50%;
            transform: translateX(-50%);
            color: #2e026d;
            font-size: 1.5em;
            font-weight: bold;
            opacity: 0;
            z-index: 20;
            white-space: nowrap;
            text-align: center;
        }

        .typing {
            opacity: 1;
            overflow: hidden;
            border-right: 3px solid #2e026d;
            letter-spacing: 0.1em;
            animation: typing 3s steps(40, end), blink 0.75s infinite;
        }

        @keyframes typing {
            from { width: 0 }
            to { width: 100% }
        }

        @keyframes blink {
            from, to { border-color: transparent }
            50% { border-color: #2e026d; }
        }

        .spinner {
            position: absolute;
            top: 70%;
            left: 50%;
            transform: translateX(-50%);
            width: 50px;
            height: 50px;
            border: 5px solid rgba(46, 2, 109, 0.2);
            border-top: 5px solid #2e026d;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            opacity: 0;
            z-index: 20;
        }

        @keyframes spin {
            0% { transform: translateX(-50%) rotate(0deg); }
            100% { transform: translateX(-50%) rotate(360deg); }
        }

        .main-content {
            display: none;
            padding: 20px;
            margin-top: 20px;
        }

        .header {
            font-size: 1.5em;
            color: #2e026d;
            margin-bottom: 30px;
            text-shadow: 0 0 10px rgba(0, 255, 247, 0.7);
        }

        .buttons-container {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
        }

        @media (max-width: 768px) {
            .buttons-container {
                grid-template-columns: 1fr;
                width: 95%;
            }
            .btn {
                width: 100%;
            }
            .header {
                font-size: 1.2em;
            }
            .welcome-text {
                font-size: 1.2em;
            }
        }

        .btn {
            width: 200px;
            height: 200px;
            border-radius: 20px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            cursor: pointer;
            box-shadow: 0 0 20px rgba(0, 255, 247, 0.5);
            transition: all 0.3s ease;
            font-size: 1.2em;
            font-weight: bold;
            color: white;
            text-decoration: none;
            padding: 20px;
            text-align: center;
        }

        .btn:hover {
            transform: scale(1.1);
            box-shadow: 0 0 30px rgba(255, 0, 127, 0.8);
        }

        .btn1 { background: linear-gradient(45deg, #00fff7, #39ff14); }
        .btn2 { background: linear-gradient(45deg, #ff007f, #007bff); }
        .btn3 { background: linear-gradient(45deg, #007bff, #0f172a); }
        .btn4 { background: linear-gradient(45deg, #39ff14, #00fff7); }

        .subtitle {
            font-size: 0.9em;
            margin-top: 10px;
            font-weight: normal;
        }

        .top-logo {
            position: fixed;
            top: 15px;
            right: 15px;
            width: 50px;
            height: auto;
            z-index: 100;
            opacity: 0;
            transition: opacity 1s ease, transform 1.5s ease;
        }

        .top-logo.visible {
            opacity: 1;
            transform: scale(1);
        }
    </style>
</head>
<body>

    <div class="border-light"></div>

    <!-- لوگو از گیت‌هاب -->
    <img id="logo" class="logo" src="https://raw.githubusercontent.com/mmdaidenn666/DASHBORD/main/logo.jpg" alt="لوگوی مدرسه">
    <div id="welcome" class="welcome-text"></div>
    <div id="spinner" class="spinner"></div>

    <img id="topLogo" class="top-logo" src="https://raw.githubusercontent.com/mmdaidenn666/DASHBORD/main/logo.jpg" alt="لوگو بالای صفحه">

    <div id="mainContent" class="main-content">
        <div class="header">
            به سایت رسمی دبیرستان پسرانه جوادالائمه خوش آمدید
        </div>
        <div class="buttons-container">
            <a href="#" class="btn btn1">
                ورود مدیران
                <div class="subtitle">این بخش فقط برای مدیران است</div>
            </a>
            <a href="#" class="btn btn2">
                ورود معلمان
                <div class="subtitle">این بخش فقط برای معلمان است</div>
            </a>
            <a href="#" class="btn btn3">
                ورود والدین
                <div class="subtitle">این بخش فقط برای والدین است</div>
            </a>
            <a href="#" class="btn btn4">
                ورود دانش آموزان
                <div class="subtitle">این بخش فقط برای دانش آموزان است</div>
            </a>
        </div>
    </div>

    <script>
        document.addEventListener("DOMContentLoaded", function () {
            const logo = document.getElementById('logo');
            const welcome = document.getElementById('welcome');
            const spinner = document.getElementById('spinner');
            const mainContent = document.getElementById('mainContent');
            const topLogo = document.getElementById('topLogo');

            // نمایش لوگو
            setTimeout(() => {
                logo.classList.add('fade-in');
            }, 500);

            // نمایش متن تایپینگ
            setTimeout(() => {
                welcome.style.opacity = 1;
                welcome.classList.add('typing');
                welcome.innerHTML = 'به سایت رسمی دبیرستان پسرانه<br>جوادالائمه خوش آمدید';
            }, 2500);

            // نمایش دایره لودینگ
            setTimeout(() => {
                spinner.style.opacity = 1;
            }, 3000);

            // پس از 5 ثانیه
            setTimeout(() => {
                // محو کردن اجزای موقت
                document.querySelector('.border-light').style.opacity = 0;
                logo.style.transition = 'opacity 1s ease, transform 2s ease';
                logo.style.transform = 'translateY(-45vh) translateX(-50%) scale(0.3)';
                
                welcome.style.opacity = 0;
                spinner.style.opacity = 0;

                // نمایش لوگو بالای صفحه
                setTimeout(() => {
                    topLogo.classList.add('visible');
                    mainContent.style.display = 'block';
                }, 1000);
            }, 5000);
        });
    </script>

</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)