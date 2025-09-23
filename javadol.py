from flask import Flask, render_template_string, request, session, redirect, url_for
import os
import jdatetime
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# داده‌های کاربران
users = {
    'admin': {
        'name': 'مدیر',
        'lastname': 'سیستم',
        'role': 'مدیر',
        'password': 'dabirstan012345'
    }
}

# داده‌های معلمان
teachers = []

# داده‌های اعلانات
announcements = []

# داده‌های دانش آموزان
students = {
    'math_10': [],
    'science_10': [],
    'humanities_10': [],
    'math_11': [],
    'science_11': [],
    'humanities_11': [],
    'math_12': [],
    'science_12': [],
    'humanities_12': []
}

# داده‌های حضور و غیاب
attendance_records = []

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
            overflow-x: hidden;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            flex: 1;
            overflow-y: auto;
            padding-bottom: 80px;
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
            animation: fadeInDown 0.8s ease-out;
        }
        
        .welcome-text {
            font-size: 1.2rem;
            margin-bottom: 30px;
            color: #e0e0ff;
            line-height: 1.6;
            animation: fadeInUp 1s ease-out;
        }
        
        .creator-info {
            text-align: center;
            margin: 20px 0;
            padding: 15px;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            border: 1px solid rgba(255,255,255,0.2);
            animation: pulse 2s infinite;
        }
        
        .buttons-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 25px;
            margin: 40px 0;
            animation: fadeIn 1s ease-out;
        }
        
        .grid-buttons {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin: 30px 0;
        }
        
        .btn {
            padding: 20px;
            border: none;
            border-radius: 15px;
            font-size: 1.1rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
            position: relative;
            overflow: hidden;
            color: white;
            text-align: center;
            transform: translateY(0);
        }
        
        .btn:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 15px 35px rgba(0,0,0,0.4);
        }
        
        .btn:active {
            transform: translateY(-2px) scale(0.98);
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
        .btn-grade { background: linear-gradient(45deg, #9932cc, #4b0082); }
        .btn-field { background: linear-gradient(45deg, #ff4500, #ff8c00); }
        .btn-announcement { background: linear-gradient(45deg, #00bfff, #1e90ff); }
        .btn-attendance { background: linear-gradient(45deg, #32cd32, #228b22); }
        .btn-search { background: linear-gradient(45deg, #ff1493, #ff69b4); }
        
        .form-container {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin: 20px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            animation: slideInUp 0.6s ease-out;
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
            transition: all 0.3s ease;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: #00eeff;
            box-shadow: 0 0 15px rgba(0, 238, 255, 0.5);
            transform: scale(1.02);
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
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        
        .submit-btn:hover {
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0 10px 25px rgba(0, 238, 255, 0.4);
        }
        
        .submit-btn:active {
            transform: translateY(1px) scale(0.98);
        }
        
        .error {
            background: rgba(255, 0, 0, 0.2);
            border: 1px solid #ff4444;
            padding: 15px;
            border-radius: 10px;
            margin: 15px 0;
            text-align: center;
            animation: shake 0.5s ease-in-out;
        }
        
        .success {
            background: rgba(0, 255, 0, 0.2);
            border: 1px solid #00ff00;
            padding: 15px;
            border-radius: 10px;
            margin: 15px 0;
            text-align: center;
            animation: bounceIn 0.6s ease-out;
        }
        
        .profile-container {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            margin: 20px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            animation: fadeIn 0.8s ease-out;
        }
        
        .profile-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 25px;
            margin: 20px 0;
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            border: 1px solid rgba(255,255,255,0.1);
            transition: all 0.3s ease;
            font-size: 1.2rem;
        }
        
        .profile-item:hover {
            background: rgba(255,255,255,0.1);
            transform: translateX(5px);
        }
        
        .profile-label {
            font-weight: 500;
            font-size: 1.3rem;
        }
        
        .profile-value {
            font-size: 1.2rem;
        }
        
        .edit-btn {
            background: linear-gradient(45deg, #ffcc00, #ff6600);
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            cursor: pointer;
            color: white;
            font-weight: bold;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            box-shadow: 0 3px 10px rgba(0,0,0,0.2);
            font-size: 1.5rem;
        }
        
        .edit-btn:hover {
            transform: scale(1.1) rotate(15deg);
            box-shadow: 0 5px 15px rgba(255, 102, 0, 0.4);
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
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        
        .logout-btn:hover {
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0 10px 25px rgba(255, 0, 102, 0.4);
        }
        
        .logout-btn:active {
            transform: translateY(1px) scale(0.98);
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
            animation: fadeIn 0.3s ease-out;
        }
        
        .modal-content {
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            padding: 30px;
            border-radius: 20px;
            text-align: center;
            max-width: 400px;
            width: 90%;
            box-shadow: 0 20px 50px rgba(0,0,0,0.5);
            animation: zoomIn 0.4s ease-out;
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
            transform: translateY(-2px) scale(1.05);
        }
        
        .toolbar {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(0,0,0,0.9);
            backdrop-filter: blur(10px);
            display: flex;
            justify-content: space-around;
            padding: 15px;
            border-top: 2px solid rgba(255,255,255,0.1);
            z-index: 999;
            transition: transform 0.5s ease-in-out;
        }
        
        .toolbar.hidden {
            transform: translateY(100%);
        }
        
        .toolbar-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            text-decoration: none;
            color: #ccc;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            padding: 10px 20px;
            border-radius: 15px;
            position: relative;
        }
        
        .toolbar-item.active {
            background: rgba(0, 238, 255, 0.2);
            color: #00eeff;
            box-shadow: 0 0 20px rgba(0, 238, 255, 0.3);
            transform: translateY(-5px);
        }
        
        .toolbar-item:hover {
            color: white;
            transform: translateY(-8px);
        }
        
        .toolbar-icon {
            font-size: 1.5rem;
            margin-bottom: 5px;
        }
        
        .notification-badge {
            position: absolute;
            top: -5px;
            right: -5px;
            background: red;
            color: white;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            font-size: 0.7rem;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .back-btn {
            background: linear-gradient(45deg, #666666, #999999);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 10px;
            cursor: pointer;
            margin-bottom: 20px;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        
        .back-btn:hover {
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0 5px 15px rgba(102, 102, 102, 0.4);
        }
        
        .back-btn:active {
            transform: translateY(1px) scale(0.98);
        }
        
        .student-count {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 1.2rem;
            margin-bottom: 20px;
            padding: 15px;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .student-count-icon {
            font-size: 1.5rem;
        }
        
        .attendance-stats {
            display: flex;
            justify-content: space-between;
            margin: 20px 0;
            padding: 15px;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .absent-count {
            color: #ff4444;
            font-weight: bold;
        }
        
        .present-count {
            color: #00ff00;
            font-weight: bold;
        }
        
        .students-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 25px;
            margin: 20px 0;
        }
        
        .student-card {
            background: rgba(255,255,255,0.1);
            border-radius: 20px;
            padding: 25px;
            border: 1px solid rgba(255,255,255,0.2);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            min-height: 180px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        
        .student-card:hover {
            transform: translateY(-5px) scale(1.02);
            box-shadow: 0 10px 25px rgba(0,0,0,0.3);
            background: rgba(255,255,255,0.15);
        }
        
        .student-card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .student-name {
            font-weight: bold;
            font-size: 1.3rem;
        }
        
        .student-card-actions {
            display: flex;
            gap: 12px;
        }
        
        .attendance-btn {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            border: 2px solid;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 1.2rem;
            font-weight: bold;
        }
        
        .absent-btn {
            border-color: #ff4444;
            color: #ff4444;
            background: rgba(255, 68, 68, 0.1);
        }
        
        .present-btn {
            border-color: #00ff00;
            color: #00ff00;
            background: rgba(0, 255, 0, 0.1);
        }
        
        .attendance-btn.active {
            transform: scale(1.2);
            box-shadow: 0 0 15px currentColor;
        }
        
        .attendance-btn:hover {
            transform: scale(1.1);
        }
        
        .student-info {
            font-size: 1rem;
            line-height: 1.8;
        }
        
        .student-info-item {
            margin: 8px 0;
            padding: 8px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        
        .student-national-id {
            font-weight: 500;
            color: #00eeff;
        }
        
        .announcements-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .announcement-card {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.2);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            position: relative;
        }
        
        .announcement-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        }
        
        .announcement-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .announcement-title {
            font-weight: bold;
            font-size: 1.1rem;
        }
        
        .delete-announcement-btn {
            background: linear-gradient(45deg, #ff0066, #ff00cc);
            color: white;
            border: none;
            border-radius: 50%;
            width: 35px;
            height: 35px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .delete-announcement-btn:hover {
            transform: scale(1.1);
        }
        
        .announcement-content {
            margin: 15px 0;
            line-height: 1.6;
        }
        
        .announcement-meta {
            font-size: 0.8rem;
            color: #ccc;
            text-align: left;
        }
        
        .absent-list {
            color: #ff4444;
            margin: 10px 0;
        }
        
        .present-list {
            color: #00ff00;
            margin: 10px 0;
        }
        
        .attendance-divider {
            height: 1px;
            background: rgba(255,255,255,0.2);
            margin: 20px 0;
        }
        
        .inline-edit-form {
            display: flex;
            flex-direction: column;
            gap: 15px;
            width: 100%;
        }
        
        .inline-edit-input {
            padding: 15px;
            border: 2px solid #00eeff;
            border-radius: 10px;
            background: rgba(0,0,0,0.5);
            color: white;
            font-size: 1.2rem;
            width: 100%;
        }
        
        .inline-edit-select {
            padding: 15px;
            border: 2px solid #00eeff;
            border-radius: 10px;
            background: rgba(0,0,0,0.5);
            color: white;
            font-size: 1.2rem;
            width: 100%;
        }
        
        .inline-edit-buttons {
            display: flex;
            gap: 10px;
            justify-content: flex-end;
            margin-top: 10px;
        }
        
        .inline-edit-btn {
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1.1rem;
            font-weight: 500;
        }
        
        .save-btn {
            background: linear-gradient(45deg, #00ff99, #00cc66);
            color: white;
        }
        
        .cancel-btn {
            background: linear-gradient(45deg, #ff0066, #ff00cc);
            color: white;
        }
        
        .student-details-container {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            margin: 20px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            animation: fadeIn 0.8s ease-out;
        }
        
        .student-detail-item {
            padding: 20px;
            margin: 15px 0;
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            border: 1px solid rgba(255,255,255,0.1);
            font-size: 1.2rem;
        }
        
        .student-detail-label {
            font-weight: 500;
            color: #00eeff;
            margin-bottom: 5px;
        }
        
        .student-detail-value {
            font-size: 1.1rem;
        }
        
        .attendance-form-buttons {
            display: flex;
            gap: 20px;
            margin: 30px 0;
            justify-content: center;
        }
        
        .attendance-submit-btn {
            background: linear-gradient(45deg, #00eeff, #0066ff);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 1.1rem;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        
        .attendance-clear-btn {
            background: linear-gradient(45deg, #ff0066, #ff00cc);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 1.1rem;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        
        .attendance-submit-btn:hover, .attendance-clear-btn:hover {
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0 10px 25px rgba(0, 238, 255, 0.4);
        }
        
        .search-form {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin: 20px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        
        .search-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        /* انیمیشن‌ها */
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes slideInUp {
            from {
                opacity: 0;
                transform: translateY(50px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes bounceIn {
            0% {
                opacity: 0;
                transform: scale(0.3);
            }
            50% {
                transform: scale(1.05);
            }
            70% {
                transform: scale(0.9);
            }
            100% {
                opacity: 1;
                transform: scale(1);
            }
        }
        
        @keyframes zoomIn {
            from {
                opacity: 0;
                transform: scale(0.5);
            }
            to {
                opacity: 1;
                transform: scale(1);
            }
        }
        
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-5px); }
            75% { transform: translateX(5px); }
        }
        
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(0, 238, 255, 0.4); }
            70% { box-shadow: 0 0 0 10px rgba(0, 238, 255, 0); }
            100% { box-shadow: 0 0 0 0 rgba(0, 238, 255, 0); }
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 1.8rem;
            }
            
            .buttons-container, .grid-buttons {
                grid-template-columns: 1fr;
            }
            
            .btn {
                padding: 15px;
                font-size: 1rem;
            }
            
            .profile-item {
                padding: 15px;
                font-size: 1rem;
            }
            
            .profile-label, .profile-value {
                font-size: 1.1rem;
            }
            
            .edit-btn {
                width: 40px;
                height: 40px;
                font-size: 1.2rem;
            }
            
            .students-grid {
                grid-template-columns: 1fr;
            }
            
            .student-card {
                padding: 20px;
            }
            
            .student-name {
                font-size: 1.1rem;
            }
            
            .attendance-btn {
                width: 35px;
                height: 35px;
                font-size: 1rem;
            }
            
            .search-grid {
                grid-template-columns: 1fr;
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
            {% elif request.endpoint == 'login_teacher' %}
                <button class="back-btn" onclick="window.location.href='/'">← بازگشت</button>
                <div class="header">
                    <h1>ورود معلمان</h1>
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
                            <label for="grade">پایه:</label>
                            <select id="grade" name="grade" required>
                                <option value="">انتخاب کنید</option>
                                <option value="10" {{ 'selected' if request.form.grade == '10' }}>دهم</option>
                                <option value="11" {{ 'selected' if request.form.grade == '11' }}>یازدهم</option>
                                <option value="12" {{ 'selected' if request.form.grade == '12' }}>دوازدهم</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="field">رشته:</label>
                            <select id="field" name="field" required>
                                <option value="">انتخاب کنید</option>
                                <option value="math" {{ 'selected' if request.form.field == 'math' }}>ریاضی</option>
                                <option value="science" {{ 'selected' if request.form.field == 'science' }}>تجربی</option>
                                <option value="humanities" {{ 'selected' if request.form.field == 'humanities' }}>انسانی</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="subject">درس:</label>
                            <input type="text" id="subject" name="subject" value="{{ request.form.subject or '' }}" required>
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
                    <button class="btn btn-teacher" onclick="window.location.href='/login/teacher'">ورود معلمان</button>
                    <button class="btn btn-parent" onclick="alert('این بخش در حال توسعه است')">ورود والدین</button>
                    <button class="btn btn-student" onclick="alert('این بخش در حال توسعه است')">ورود دانش‌آموزان</button>
                </div>
                <div class="creator-info">
                    <p><strong>سازنده:</strong> محمدرضا محمدی</p>
                    <p>دانش آموز دبیرستان جوادالائمه (رشته ریاضی)</p>
                </div>
            {% endif %}
        {% else %}
            {% if page == 'profile' %}
                <button class="back-btn" onclick="window.location.href='/{{ 'admin' if session.role == 'مدیر' else 'teacher' }}'">← بازگشت</button>
                <div class="header">
                    <h1>پروفایل کاربری</h1>
                </div>
                <div class="profile-container">
                    <div class="profile-item">
                        <div>
                            <div class="profile-label">نام:</div>
                            <div class="profile-value" id="name-value">{{ session.name }}</div>
                        </div>
                        <button class="edit-btn" onclick="editField('name', '{{ session.name }}')">✎</button>
                    </div>
                    <div class="profile-item">
                        <div>
                            <div class="profile-label">نام خانوادگی:</div>
                            <div class="profile-value" id="lastname-value">{{ session.lastname }}</div>
                        </div>
                        <button class="edit-btn" onclick="editField('lastname', '{{ session.lastname }}')">✎</button>
                    </div>
                    {% if session.role == 'مدیر' %}
                    <div class="profile-item">
                        <div>
                            <div class="profile-label">مرتبه:</div>
                            <div class="profile-value" id="role-value">{{ session.role }}</div>
                        </div>
                        <button class="edit-btn" onclick="editField('role', '{{ session.role }}')">✎</button>
                    </div>
                    {% else %}
                    <div class="profile-item">
                        <div>
                            <div class="profile-label">پایه:</div>
                            <div class="profile-value">{{ session.grade_name }}</div>
                        </div>
                    </div>
                    <div class="profile-item">
                        <div>
                            <div class="profile-label">رشته:</div>
                            <div class="profile-value">{{ session.field_name }}</div>
                        </div>
                    </div>
                    <div class="profile-item">
                        <div>
                            <div class="profile-label">درس:</div>
                            <div class="profile-value">{{ session.subject }}</div>
                        </div>
                    </div>
                    {% endif %}
                    <div class="profile-item">
                        <div>
                            <div class="profile-label">رمز ورود:</div>
                            <div class="profile-value">••••••••••</div>
                        </div>
                        <button class="edit-btn" disabled style="opacity: 0.5;">✎</button>
                    </div>
                    <button class="logout-btn" onclick="showLogoutModal()">خروج از حساب</button>
                </div>
            {% elif page == 'announcements' %}
                <button class="back-btn" onclick="window.location.href='/{{ 'admin' if session.role == 'مدیر' else 'teacher' }}'">← بازگشت</button>
                <div class="header">
                    <h1>اعلانات</h1>
                </div>
                {% if announcements %}
                    <div class="announcements-grid">
                        {% for announcement in announcements %}
                        <div class="announcement-card">
                            <div class="announcement-header">
                                <div class="announcement-title">{{ announcement.title }}</div>
                                {% if session.role == 'مدیر' %}
                                <button class="delete-announcement-btn" onclick="deleteAnnouncement({{ loop.index0 }})">🗑️</button>
                                {% endif %}
                            </div>
                            <div class="announcement-content">{{ announcement.content }}</div>
                            <div class="announcement-meta">
                                <div>تاریخ: {{ announcement.date }}</div>
                                <div>زمان: {{ announcement.time }}</div>
                                <div>بخش: {{ announcement.section }}</div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                {% else %}
                    <div class="welcome-text">
                        <p>هنوز هیچ اعلانی نیامده است</p>
                    </div>
                {% endif %}
            {% elif page == 'students' %}
                <button class="back-btn" onclick="window.location.href='/admin'">← بازگشت</button>
                <div class="header">
                    <h1>دانش آموزان</h1>
                </div>
                <div class="grid-buttons">
                    <button class="btn btn-grade" onclick="window.location.href='/admin/students/10'">پایه دهم</button>
                    <button class="btn btn-grade" onclick="window.location.href='/admin/students/11'">پایه یازدهم</button>
                    <button class="btn btn-grade" onclick="window.location.href='/admin/students/12'">پایه دوازدهم</button>
                </div>
            {% elif page == 'grade_students' %}
                <button class="back-btn" onclick="window.location.href='/admin/students'">← بازگشت</button>
                <div class="header">
                    <h1>پایه {{ grade }}</h1>
                </div>
                <div class="grid-buttons">
                    <button class="btn btn-field" onclick="window.location.href='/admin/students/{{ grade }}/math'">رشته ریاضی</button>
                    <button class="btn btn-field" onclick="window.location.href='/admin/students/{{ grade }}/science'">رشته تجربی</button>
                    <button class="btn btn-field" onclick="window.location.href='/admin/students/{{ grade }}/humanities'">رشته انسانی</button>
                </div>
            {% elif page == 'field_students' %}
                <button class="back-btn" onclick="window.location.href='/admin/students/{{ grade }}'">← بازگشت</button>
                <div class="header">
                    <h1>{{ field_name }} پایه {{ grade }}</h1>
                </div>
                <div class="student-count">
                    <span class="student-count-icon">👤</span>
                    <span>تعداد دانش آموزان: <span id="studentCount">{{ students[field_key]|length }}</span></span>
                </div>
                {% if students[field_key] %}
                    <div class="students-grid">
                        {% for student in students[field_key] %}
                        <div class="student-card">
                            <div class="student-card-header">
                                <div class="student-name">{{ student.name }} {{ student.lastname }}</div>
                            </div>
                            <div class="student-info">
                                <div class="student-info-item student-national-id">کد ملی: {{ student.national_id }}</div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                {% else %}
                    <div class="welcome-text">
                        <p>هنوز هیچ دانش آموزی ثبت نشده است</p>
                    </div>
                {% endif %}
            {% elif page == 'attendance' %}
                <button class="back-btn" onclick="window.location.href='/teacher'">← بازگشت</button>
                <div class="header">
                    <h1>حضور و غیاب - {{ session.grade_name }} {{ session.field_name }}</h1>
                </div>
                <div class="student-count">
                    <span class="student-count-icon">👤</span>
                    <span>تعداد دانش آموزان: <span id="studentCount">{{ students[session.field_key]|length }}</span></span>
                </div>
                <div class="attendance-stats">
                    <div class="absent-count">غائب: <span id="absentCount">0</span></div>
                    <div class="present-count">حاضر: <span id="presentCount">0</span></div>
                </div>
                {% if students[session.field_key] %}
                    <div class="students-grid">
                        {% for student in students[session.field_key] %}
                        <div class="student-card">
                            <div class="student-card-header">
                                <div class="student-name">{{ student.name }} {{ student.lastname }}</div>
                            </div>
                            <div class="student-card-actions">
                                <button class="attendance-btn absent-btn" onclick="toggleAttendance({{ loop.index0 }}, 'absent')">غ</button>
                                <button class="attendance-btn present-btn" onclick="toggleAttendance({{ loop.index0 }}, 'present')">ح</button>
                            </div>
                            <div class="student-info">
                                <div class="student-info-item student-national-id">کد ملی: {{ student.national_id }}</div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                    <div class="attendance-form-buttons">
                        <button class="attendance-submit-btn" onclick="showAttendanceDateModal()">ارسال فرم حضور و غیاب</button>
                        <button class="attendance-clear-btn" onclick="clearAttendance()">پاک کردن انتخاب شدگان</button>
                    </div>
                {% else %}
                    <div class="welcome-text">
                        <p>هنوز هیچ دانش آموزی ثبت نشده است</p>
                    </div>
                {% endif %}
            {% elif page == 'attendance_date' %}
                <button class="back-btn" onclick="window.location.href='/teacher/attendance'">← بازگشت</button>
                <div class="header">
                    <h1>انتخاب تاریخ حضور و غیاب</h1>
                </div>
                <div class="form-container">
                    <form method="POST" action="/teacher/attendance/submit">
                        <div class="form-group">
                            <label for="day">روز:</label>
                            <select id="day" name="day" required>
                                <option value="">انتخاب کنید</option>
                                {% for i in range(1, 32) %}
                                <option value="{{ i }}">{{ i }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="month">ماه:</label>
                            <select id="month" name="month" required>
                                <option value="">انتخاب کنید</option>
                                {% for i in range(1, 13) %}
                                <option value="{{ i }}">{{ i }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="year">سال:</label>
                            <select id="year" name="year" required>
                                <option value="">انتخاب کنید</option>
                                {% for i in range(1404, 1451) %}
                                <option value="{{ i }}">{{ i }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="weekday">روز هفته (اختیاری):</label>
                            <select id="weekday" name="weekday">
                                <option value="">انتخاب کنید</option>
                                <option value="شنبه">شنبه</option>
                                <option value="یک‌شنبه">یک‌شنبه</option>
                                <option value="دوشنبه">دوشنبه</option>
                                <option value="سه‌شنبه">سه‌شنبه</option>
                                <option value="چهارشنبه">چهارشنبه</option>
                                <option value="پنجشنبه">پنجشنبه</option>
                                <option value="جمعه">جمعه</option>
                            </select>
                        </div>
                        {% if error %}
                            <div class="error">{{ error }}</div>
                        {% endif %}
                        <button type="submit" class="submit-btn">تایید</button>
                    </form>
                </div>
            {% else %}
                <div class="header">
                    <h1>{% if session.role == 'مدیر' %}پنل مدیریت{% else %}پنل معلم{% endif %}</h1>
                    <p>به {% if session.role == 'مدیر' %}پنل مدیریت{% else %}پنل معلم{% endif %} خوش آمدید</p>
                </div>
                <div class="creator-info">
                    <p><strong>سازنده:</strong> محمدرضا محمدی</p>
                    <p>دانش آموز دبیرستان جوادالائمه (رشته ریاضی)</p>
                </div>
                <div class="grid-buttons">
                    {% if session.role == 'مدیر' %}
                    <button class="btn btn-announcement" onclick="window.location.href='/admin/announcements'">اعلانات</button>
                    <button class="btn btn-students" onclick="window.location.href='/admin/students'">دانش آموزان</button>
                    {% else %}
                    <button class="btn btn-attendance" onclick="window.location.href='/teacher/attendance'">حضور و غیاب</button>
                    <button class="btn btn-announcement" onclick="window.location.href='/teacher/announcements'">اعلانات</button>
                    {% endif %}
                </div>
            {% endif %}
        {% endif %}
    </div>
    
    {% if session.get('logged_in') and page not in ['add_student', 'edit_student', 'attendance_date'] %}
        <div class="toolbar" id="toolbar">
            <a href="/{{ 'admin' if session.role == 'مدیر' else 'teacher' }}" class="toolbar-item {{ 'active' if page not in ['profile', 'announcements', 'students', 'grade_students', 'field_students', 'student_details', 'add_student', 'edit_student', 'attendance', 'attendance_date'] }}">
                <div class="toolbar-icon">🏠</div>
                <span>صفحه اصلی</span>
            </a>
            <a href="/{{ 'admin' if session.role == 'مدیر' else 'teacher' }}/profile" class="toolbar-item {{ 'active' if page == 'profile' }}">
                <div class="toolbar-icon">👤</div>
                <span>پروفایل</span>
            </a>
        </div>
    {% endif %}
    
    <!-- مودال خروج -->
    <div id="logoutModal" class="modal">
        <div class="modal-content">
            <h3>آیا مطمئن هستید می‌خواهید از حساب خارج شوید؟</h3>
            <div class="modal-buttons">
                <button class="modal-btn modal-btn-yes" onclick="logout()">بله</button>
                <button class="modal-btn modal-btn-no" onclick="closeModal('logoutModal')">خیر</button>
            </div>
        </div>
    </div>
    
    <!-- مودال حذف اعلان -->
    <div id="deleteAnnouncementModal" class="modal">
        <div class="modal-content">
            <h3>آیا مطمئن هستید می‌خواهید این اعلان را پاک کنید؟</h3>
            <div class="modal-buttons">
                <button class="modal-btn modal-btn-yes" onclick="confirmDeleteAnnouncement()">بله</button>
                <button class="modal-btn modal-btn-no" onclick="closeModal('deleteAnnouncementModal')">خیر</button>
            </div>
        </div>
    </div>
    
    <!-- مودال پاک کردن انتخاب شدگان -->
    <div id="clearAttendanceModal" class="modal">
        <div class="modal-content">
            <h3>آیا مطمئن هستید می‌خواهید انتخاب شدگان را پاک کنید؟</h3>
            <div class="modal-buttons">
                <button class="modal-btn modal-btn-yes" onclick="confirmClearAttendance()">بله</button>
                <button class="modal-btn modal-btn-no" onclick="closeModal('clearAttendanceModal')">خیر</button>
            </div>
        </div>
    </div>
    
    <script>
        let pendingDeleteIndex = -1;
        let pendingDeleteField = '';
        let attendanceData = {};
        
        // مخفی کردن تولبار هنگام اسکرول
        window.addEventListener('scroll', function() {
            const toolbar = document.getElementById('toolbar');
            if (toolbar) {
                if (window.scrollY > 100) {
                    toolbar.classList.add('hidden');
                } else {
                    toolbar.classList.remove('hidden');
                }
            }
        });
        
        function showLogoutModal() {
            document.getElementById('logoutModal').style.display = 'flex';
        }
        
        function closeModal(modalId) {
            document.getElementById(modalId).style.display = 'none';
        }
        
        function logout() {
            window.location.href = '/logout';
        }
        
        function editField(field, currentValue) {
            // مخفی کردن دکمه مداد
            const editBtn = event.target;
            editBtn.style.display = 'none';
            
            const valueElement = document.getElementById(field + '-value');
            
            if (field === 'role') {
                valueElement.innerHTML = `
                    <form class="inline-edit-form" method="POST" action="/edit_profile">
                        <input type="hidden" name="field" value="${field}">
                        <select name="value" class="inline-edit-select">
                            <option value="مدیر" ${currentValue === 'مدیر' ? 'selected' : ''}>مدیر</option>
                            <option value="ناظم" ${currentValue === 'ناظم' ? 'selected' : ''}>ناظم</option>
                            <option value="معاون" ${currentValue === 'معاون' ? 'selected' : ''}>معاون</option>
                            <option value="سرپرست" ${currentValue === 'سرپرست' ? 'selected' : ''}>سرپرست</option>
                        </select>
                        <div class="inline-edit-buttons">
                            <button type="submit" class="inline-edit-btn save-btn">✓ تایید</button>
                            <button type="button" class="inline-edit-btn cancel-btn" onclick="cancelEdit('${field}', '${currentValue}', this)">✗ انصراف</button>
                        </div>
                    </form>
                `;
            } else {
                valueElement.innerHTML = `
                    <form class="inline-edit-form" method="POST" action="/edit_profile">
                        <input type="hidden" name="field" value="${field}">
                        <input type="text" name="value" value="${currentValue}" class="inline-edit-input" required>
                        <div class="inline-edit-buttons">
                            <button type="submit" class="inline-edit-btn save-btn">✓ تایید</button>
                            <button type="button" class="inline-edit-btn cancel-btn" onclick="cancelEdit('${field}', '${currentValue}', this)">✗ انصراف</button>
                        </div>
                    </form>
                `;
            }
        }
        
        function cancelEdit(field, originalValue, cancelButton) {
            const valueElement = document.getElementById(field + '-value');
            valueElement.textContent = originalValue;
            
            // نمایش دوباره دکمه مداد
            const profileItem = valueElement.closest('.profile-item');
            const editBtn = profileItem.querySelector('.edit-btn');
            editBtn.style.display = 'flex';
        }
        
        function deleteAnnouncement(index) {
            pendingDeleteIndex = index;
            document.getElementById('deleteAnnouncementModal').style.display = 'flex';
        }
        
        function confirmDeleteAnnouncement() {
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = '/admin/announcements/delete/' + pendingDeleteIndex;
            document.body.appendChild(form);
            form.submit();
        }
        
        function toggleAttendance(studentIndex, type) {
            const absentBtn = event.target.parentElement.querySelector('.absent-btn');
            const presentBtn = event.target.parentElement.querySelector('.present-btn');
            
            // اگر دکمه فعلی فعال بود، غیرفعال کن
            if (event.target.classList.contains('active')) {
                event.target.classList.remove('active');
                delete attendanceData[studentIndex];
            } else {
                // غیرفعال کردن دکمه مقابل
                if (type === 'absent') {
                    presentBtn.classList.remove('active');
                } else {
                    absentBtn.classList.remove('active');
                }
                
                // فعال کردن دکمه فعلی
                event.target.classList.add('active');
                attendanceData[studentIndex] = type;
            }
            
            // به‌روزرسانی شمارنده‌ها
            updateAttendanceCount();
        }
        
        function updateAttendanceCount() {
            let absentCount = 0;
            let presentCount = 0;
            
            for (let key in attendanceData) {
                if (attendanceData[key] === 'absent') {
                    absentCount++;
                } else if (attendanceData[key] === 'present') {
                    presentCount++;
                }
            }
            
            document.getElementById('absentCount').textContent = absentCount;
            document.getElementById('presentCount').textContent = presentCount;
        }
        
        function showAttendanceDateModal() {
            // بررسی اینکه حداقل یک دانش آموز انتخاب شده باشد
            if (Object.keys(attendanceData).length === 0) {
                alert('لطفاً حداقل یک دانش آموز را انتخاب کنید');
                return;
            }
            
            window.location.href = '/teacher/attendance/date';
        }
        
        function clearAttendance() {
            document.getElementById('clearAttendanceModal').style.display = 'flex';
        }
        
        function confirmClearAttendance() {
            // پاک کردن انتخاب‌ها
            attendanceData = {};
            
            // غیرفعال کردن تمام دکمه‌ها
            const attendanceBtns = document.querySelectorAll('.attendance-btn');
            attendanceBtns.forEach(btn => {
                btn.classList.remove('active');
            });
            
            // به‌روزرسانی شمارنده‌ها
            updateAttendanceCount();
            
            closeModal('clearAttendanceModal');
        }
        
        // بستن مودال‌ها با کلیک خارج از آن‌ها
        window.onclick = function(event) {
            const modals = ['logoutModal', 'deleteAnnouncementModal', 'clearAttendanceModal'];
            modals.forEach(modalId => {
                const modal = document.getElementById(modalId);
                if (event.target === modal) {
                    modal.style.display = 'none';
                }
            });
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
        
        if password == 'dabirstan012345':
            session['logged_in'] = True
            session['name'] = name
            session['lastname'] = lastname
            session['role'] = role
            return redirect('/admin')
        else:
            return render_template_string(HTML_TEMPLATE, error='رمز ورود اشتباه است', page='login_admin')
    
    return render_template_string(HTML_TEMPLATE, page='login_admin')

@app.route('/login/teacher', methods=['GET', 'POST'])
def login_teacher():
    if request.method == 'POST':
        name = request.form['name']
        lastname = request.form['lastname']
        grade = request.form['grade']
        field = request.form['field']
        subject = request.form['subject']
        password = request.form['password']
        
        # نگاشت پایه و رشته به نام‌های فارسی
        grade_names = {'10': 'دهم', '11': 'یازدهم', '12': 'دوازدهم'}
        field_names = {'math': 'ریاضی', 'science': 'تجربی', 'humanities': 'انسانی'}
        
        if password == 'Dabirjavad01':
            session['logged_in'] = True
            session['name'] = name
            session['lastname'] = lastname
            session['grade'] = grade
            session['field'] = field
            session['subject'] = subject
            session['grade_name'] = grade_names.get(grade, grade)
            session['field_name'] = field_names.get(field, field)
            session['field_key'] = f"{field}_{grade}"
            session['role'] = 'معلم'
            return redirect('/teacher')
        else:
            return render_template_string(HTML_TEMPLATE, error='رمز ورود اشتباه است', page='login_teacher')
    
    return render_template_string(HTML_TEMPLATE, page='login_teacher')

@app.route('/admin')
def admin_panel():
    if not session.get('logged_in') or session.get('role') != 'مدیر':
        return redirect('/')
    return render_template_string(HTML_TEMPLATE, page='admin')

@app.route('/teacher')
def teacher_panel():
    if not session.get('logged_in') or session.get('role') != 'معلم':
        return redirect('/')
    return render_template_string(HTML_TEMPLATE, page='teacher')

@app.route('/admin/profile')
def admin_profile():
    if not session.get('logged_in') or session.get('role') != 'مدیر':
        return redirect('/')
    return render_template_string(HTML_TEMPLATE, page='profile')

@app.route('/teacher/profile')
def teacher_profile():
    if not session.get('logged_in') or session.get('role') != 'معلم':
        return redirect('/')
    return render_template_string(HTML_TEMPLATE, page='profile')

@app.route('/admin/announcements')
def admin_announcements():
    if not session.get('logged_in') or session.get('role') != 'مدیر':
        return redirect('/')
    return render_template_string(HTML_TEMPLATE, page='announcements', announcements=announcements)

@app.route('/teacher/announcements')
def teacher_announcements():
    if not session.get('logged_in') or session.get('role') != 'معلم':
        return redirect('/')
    return render_template_string(HTML_TEMPLATE, page='announcements', announcements=announcements)

@app.route('/admin/students')
def admin_students():
    if not session.get('logged_in') or session.get('role') != 'مدیر':
        return redirect('/')
    return render_template_string(HTML_TEMPLATE, page='students')

@app.route('/admin/students/<grade>')
def grade_students(grade):
    if not session.get('logged_in') or session.get('role') != 'مدیر':
        return redirect('/')
    return render_template_string(HTML_TEMPLATE, page='grade_students', grade=grade)

@app.route('/admin/students/<grade>/<field>')
def field_students(grade, field):
    if not session.get('logged_in') or session.get('role') != 'مدیر':
        return redirect('/')
    
    field_mapping = {
        'math': 'ریاضی',
        'science': 'تجربی',
        'humanities': 'انسانی'
    }
    
    field_key = f"{field}_{grade}"
    field_name = field_mapping.get(field, field)
    
    return render_template_string(HTML_TEMPLATE, 
                                page='field_students', 
                                grade=grade, 
                                field=field, 
                                field_key=field_key, 
                                field_name=field_name,
                                students=students)

@app.route('/teacher/attendance')
def teacher_attendance():
    if not session.get('logged_in') or session.get('role') != 'معلم':
        return redirect('/')
    return render_template_string(HTML_TEMPLATE, page='attendance', students=students)

@app.route('/teacher/attendance/date')
def attendance_date():
    if not session.get('logged_in') or session.get('role') != 'معلم':
        return redirect('/')
    return render_template_string(HTML_TEMPLATE, page='attendance_date')

@app.route('/teacher/attendance/submit', methods=['POST'])
def submit_attendance():
    if not session.get('logged_in') or session.get('role') != 'معلم':
        return redirect('/')
    
    day = request.form['day']
    month = request.form['month']
    year = request.form['year']
    weekday = request.form.get('weekday', '')
    
    # بررسی پر بودن فیلدهای اجباری
    if not day or not month or not year:
        return render_template_string(HTML_TEMPLATE, 
                                    page='attendance_date', 
                                    error='فیلدهای اجباری را پر کنید')
    
    # ایجاد اعلان برای مدیر
    absent_students = []
    present_students = []
    
    for index, status in attendance_data.items():
        student = students[session['field_key']][int(index)]
        student_name = f"{student['name']} {student['lastname']}"
        
        if status == 'absent':
            absent_students.append(student_name)
        elif status == 'present':
            present_students.append(student_name)
    
    # تاریخ به صورت فارسی
    persian_date = f"{weekday} - {year}/{month}/{day}" if weekday else f"{year}/{month}/{day}"
    
    # ایجاد اعلان برای مدیر
    admin_announcement = {
        'title': f"فرم حضور و غیاب - {session['name']} {session['lastname']}",
        'content': f"پایه: {session['grade_name']} - رشته: {session['field_name']} - درس: {session['subject']}",
        'date': persian_date,
        'time': datetime.now().strftime('%H:%M'),
        'section': 'حضور و غیاب',
        'absent_students': absent_students,
        'present_students': present_students
    }
    
    announcements.append(admin_announcement)
    
    # ایجاد اعلان برای معلم (سوابق)
    teacher_announcement = {
        'title': f"سوابق حضور و غیاب - {session['name']} {session['lastname']}",
        'content': f"پایه: {session['grade_name']} - رشته: {session['field_name']} - درس: {session['subject']}",
        'date': persian_date,
        'time': datetime.now().strftime('%H:%M'),
        'section': 'سوابق',
        'absent_students': absent_students,
        'present_students': present_students
    }
    
    # پاک کردن انتخاب‌ها
    global attendance_data
    attendance_data = {}
    
    return redirect('/teacher')

@app.route('/edit_profile', methods=['POST'])
def edit_profile():
    if not session.get('logged_in'):
        return redirect('/')
    
    field = request.form['field']
    value = request.form['value']
    
    if field in ['name', 'lastname', 'role']:
        session[field] = value
    
    return redirect(f"/{ 'admin' if session.get('role') == 'مدیر' else 'teacher' }/profile")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)