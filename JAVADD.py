from flask import Flask, render_template_string

app = Flask(__name__)

# CSS داخلی
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
.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 20px;
    background: rgba(0,0,0,0.4);
    border-radius: 10px;
    margin-bottom: 30px;
    box-shadow: 0 0 15px #00fff7;
}
.logo {
    font-size: 1.8rem;
    font-weight: bold;
    color: #00fff7;
    text-shadow: 0 0 10px #00fff7;
}
.nav ul {
    display: flex;
    list-style: none;
    gap: 20px;
}
.nav a {
    color: #cbd5e1;
    text-decoration: none;
    font-size: 1.1rem;
    transition: color 0.3s;
}
.nav a:hover {
    color: #00fff7;
    text-shadow: 0 0 5px #00fff7;
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

footer {
    margin-top: 50px;
    text-align: center;
    padding: 20px;
    color: #cbd5e1;
    font-size: 1rem;
}
.social-icons a {
    color: #ffffff;
    font-size: 1.5rem;
    margin: 0 10px;
    text-shadow: 0 0 8px #ff007f;
}
@media (max-width: 768px) {
    .header {
        flex-direction: column;
        gap: 15px;
    }
    .nav ul {
        flex-wrap: wrap;
        justify-content: center;
    }
    .title {
        font-size: 1.6rem;
    }
    .btn {
        padding: 20px 10px;
        font-size: 1.2rem;
    }
}
"""

# HTML داخلی
HTML = f"""
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>دبیرستان پسرانه جوادالائمه</title>
    <style>{CSS}</style>
</head>
<body>
    <div class="header">
        <div class="logo">دبیرستان جوادالائمه</div>
        <div class="nav">
            <ul>
                <li><a href="#">خانه</a></li>
                <li><a href="#">درباره ما</a></li>
                <li><a href="#">دانش‌آموزان</a></li>
                <li><a href="#">معلمان</a></li>
                <li><a href="#">اخبار</a></li>
                <li><a href="#">تماس</a></li>
            </ul>
        </div>
    </div>

    <h1 class="title">به سایت رسمی دبیرستان پسرانه جوادالائمه خوش آمدید</h1>

    <div class="buttons-container">
        <div class="btn btn1" onclick="alert('ورود مدیران')">ورود مدیران<br><small>این بخش فقط برای مدیران است</small></div>
        <div class="btn btn2" onclick="alert('ورود معلمان')">ورود معلمان<br><small>این بخش فقط برای معلمان است</small></div>
        <div class="btn btn3" onclick="alert('ورود والدین')">ورود والدین<br><small>این بخش فقط برای والدین است</small></div>
        <div class="btn btn4" onclick="alert('ورود دانش‌آموزان')">ورود دانش‌آموزان<br><small>این بخش فقط برای دانش‌آموزان است</small></div>
    </div>

    <footer>
        <p>تمامی حقوق محفوظ است &copy; ۱۴۰۳</p>
        <div class="social-icons">
            <a href="#">📱</a>
            <a href="#">📸</a>
            <a href="#">🐦</a>
        </div>
    </footer>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

if __name__ == '__main__':
    app.run(debug=True)