import os
import io
import base64
import json
import sqlite3

from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
import qrcode
import uvicorn

# FastAPI App
app = FastAPI()

# SQLite Setup
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            name TEXT,
            title TEXT,
            bio TEXT,
            phone TEXT,
            email TEXT,
            social TEXT,
            profile_img TEXT,
            logo_img TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Utility to generate QR Code
def generate_qr(url):
    qr = qrcode.make(url)
    buf = io.BytesIO()
    qr.save(buf, format="PNG")
    img_str = base64.b64encode(buf.getvalue()).decode()
    return img_str

# HTML Templates as strings
INDEX_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Live Business Card</title>
    <style>
        body { 
            background: #111; 
            color: white; 
            text-align: center; 
            padding: 50px;
            font-family: Arial, sans-serif;
        }
        a {
            color: cyan;
            font-size: 20px;
            text-decoration: none;
        }
        a:hover {
            text-shadow: 0 0 10px cyan;
        }
    </style>
</head>
<body>
    <h1>Live Business Card</h1>
    <p>Create your own neon-themed business card at:</p>
    <a href="/create">Create Card</a>
</body>
</html>
"""

CREATE_FORM_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Create Card</title>
    <style>
        body { 
            background: #111; 
            color: white; 
            padding: 20px;
            font-family: Arial, sans-serif;
        }
        input, textarea {
            width: 100%;
            padding: 10px;
            margin: 5px 0;
            background: #222;
            border: 1px solid #444;
            color: white;
            border-radius: 5px;
        }
        button {
            background: #0ff;
            padding: 12px 20px;
            border: none;
            color: black;
            font-weight: bold;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover {
            box-shadow: 0 0 15px #0ff;
        }
        label {
            display: block;
            margin-top: 15px;
            color: #0ff;
        }
    </style>
</head>
<body>
    <h2>Create Your Neon Card</h2>
    <form action="/submit" method="post" enctype="multipart/form-data">
        <input type="text" name="username" placeholder="Username" required><br>
        <input type="text" name="name" placeholder="Full Name" required><br>
        <input type="text" name="title" placeholder="Job Title" required><br>
        <textarea name="bio" placeholder="Bio" required></textarea><br>
        <input type="text" name="phone" placeholder="Phone"><br>
        <input type="email" name="email" placeholder="Email"><br>
        <input type="text" name="social" placeholder='{"linkedin":"url","instagram":"url"}'><br>

        <label>Profile Image:</label>
        <input type="file" name="profile_img"><br>

        <label>Logo:</label>
        <input type="file" name="logo_img"><br>

        <button type="submit">Create Card</button>
    </form>
</body>
</html>
"""

PROFILE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{{username}}'s Card</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Poppins:wght@400;600&display=swap');
    
    body {
      background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
      font-family: 'Poppins', sans-serif;
      color: white;
      margin: 0;
      padding: 20px;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    
    .card {
      background: rgba(255, 255, 255, 0.05);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 20px;
      padding: 30px;
      max-width: 400px;
      width: 100%;
      text-align: center;
      box-shadow: 0 0 30px rgba(0, 255, 255, 0.3);
      position: relative;
      overflow: hidden;
    }
    
    .card::before {
      content: '';
      position: absolute;
      top: -2px;
      left: -2px;
      right: -2px;
      bottom: -2px;
      background: linear-gradient(45deg, #00ffff, #ff00ff, #00ffff);
      z-index: -1;
      border-radius: 22px;
      animation: glow 3s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
      0% { filter: blur(5px); }
      100% { filter: blur(10px); }
    }
    
    .profile-img {
      width: 120px;
      height: 120px;
      border-radius: 50%;
      border: 3px solid #0ff;
      box-shadow: 0 0 20px #0ff, inset 0 0 10px rgba(0, 255, 255, 0.5);
      margin: 0 auto 20px;
      object-fit: cover;
    }
    
    .name {
      font-family: 'Orbitron', sans-serif;
      font-size: 28px;
      font-weight: 700;
      margin: 0;
      background: linear-gradient(45deg, #00ffff, #ff00ff);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      text-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
    }
    
    .title {
      color: #00ffff;
      font-size: 18px;
      margin: 5px 0 15px;
      font-weight: 600;
    }
    
    .bio {
      color: #ccc;
      font-size: 14px;
      line-height: 1.5;
      margin: 20px 0;
    }
    
    .contact-info {
      text-align: left;
      margin: 20px 0;
    }
    
    .contact-item {
      display: flex;
      align-items: center;
      margin: 10px 0;
      color: #aaa;
    }
    
    .contact-icon {
      margin-right: 10px;
      color: #00ffff;
      font-size: 18px;
    }
    
    .social-icons {
      display: flex;
      justify-content: center;
      gap: 20px;
      margin: 25px 0;
    }
    
    .social-icon {
      width: 50px;
      height: 50px;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.1);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
      color: #00ffff;
      text-decoration: none;
      transition: all 0.3s ease;
      border: 1px solid rgba(0, 255, 255, 0.3);
    }
    
    .social-icon:hover {
      transform: translateY(-5px);
      box-shadow: 0 0 20px #00ffff;
      background: rgba(0, 255, 255, 0.1);
    }
    
    .qr-section {
      margin-top: 25px;
      padding-top: 20px;
      border-top: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .qr-label {
      font-size: 12px;
      color: #888;
      margin-bottom: 10px;
    }
    
    .qr-code {
      width: 120px;
      height: 120px;
      margin: 0 auto;
      border: 2px solid #0ff;
      border-radius: 10px;
      box-shadow: 0 0 15px rgba(0, 255, 255, 0.3);
    }
    
    @media (max-width: 480px) {
      .card {
        padding: 20px;
        margin: 10px;
      }
      
      .name {
        font-size: 24px;
      }
      
      .social-icon {
        width: 40px;
        height: 40px;
        font-size: 16px;
      }
    }
  </style>
</head>
<body>
  <div class="card">
    {% if profile_img %}
      <img src="/{{ profile_img }}" alt="Profile" class="profile-img">
    {% endif %}

    <h1 class="name">{{ name }}</h1>
    <p class="title">{{ title }}</p>
    <p class="bio">{{ bio }}</p>

    <div class="contact-info">
      {% if phone %}
        <div class="contact-item">
          <span class="contact-icon">📞</span>
          <span>{{ phone }}</span>
        </div>
      {% endif %}
      {% if email %}
        <div class="contact-item">
          <span class="contact-icon">✉️</span>
          <span>{{ email }}</span>
        </div>
      {% endif %}
    </div>

    <div class="social-icons">
      {% for name, url in social.items() %}
        <a href="{{ url }}" class="social-icon" target="_blank">🔗</a>
      {% endfor %}
    </div>

    <div class="qr-section">
      <p class="qr-label">Scan to share this card:</p>
      <img src="image/png;base64,{{ qr_code }}" class="qr-code" />
    </div>
  </div>
</body>
</html>
"""

# Routes
@app.get("/", response_class=HTMLResponse)
async def index():
    return INDEX_TEMPLATE

@app.get("/create", response_class=HTMLResponse)
async def create_form():
    return CREATE_FORM_TEMPLATE

@app.post("/submit")
async def submit_profile(
    username: str,
    name: str,
    title: str,
    bio: str,
    phone: str = "",
    email: str = "",
    social: str = "{}",
    profile_img: UploadFile = File(None),
    logo_img: UploadFile = File(None)
):
    profile_path = logo_path = None

    if profile_img:
        profile_path = f"static/{username}_profile.png"
        os.makedirs("static", exist_ok=True)
        with open(profile_path, "wb") as f:
            f.write(await profile_img.read())

    if logo_img:
        logo_path = f"static/{username}_logo.png"
        os.makedirs("static", exist_ok=True)
        with open(logo_path, "wb") as f:
            f.write(await logo_img.read())

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO profiles
        (username, name, title, bio, phone, email, social, profile_img, logo_img)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (username, name, title, bio, phone, email, social, profile_path, logo_path))
    conn.commit()
    conn.close()

    return RedirectResponse(url=f"/u/{username}", status_code=303)

@app.get("/u/{username}", response_class=HTMLResponse)
async def show_card(request: Request, username: str):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM profiles WHERE username=?", (username,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return "<h2 style='color:white;background:#111;padding:20px;'>User not found</h2>"

    _, username, name, title, bio, phone, email, social, profile_img, logo_img = row

    qr_code = generate_qr(str(request.url))

    # Replace template variables
    template = PROFILE_TEMPLATE
    template = template.replace("{{username}}", username)
    template = template.replace("{{name}}", name)
    template = template.replace("{{title}}", title)
    template = template.replace("{{bio}}", bio)
    template = template.replace("{{phone}}", phone)
    template = template.replace("{{email}}", email)
    template = template.replace("{{profile_img}}", profile_img or "")
    template = template.replace("{{qr_code}}", qr_code)
    
    # Handle social links
    try:
        social_dict = json.loads(social) if social else {}
    except:
        social_dict = {}
    
    social_html = ""
    for name, url in social_dict.items():
        social_html += f'<a href="{url}" class="social-icon" target="_blank">🔗</a>'
    
    template = template.replace(
        '{% for name, url in social.items() %}\n        <a href="{{ url }}" class="social-icon" target="_blank">🔗</a>\n      {% endfor %}',
        social_html
    )

    return template

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)