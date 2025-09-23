from flask import Flask, render_template_string, request, session, redirect, url_for, jsonify
import os
import jdatetime
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# داده‌های کاربران و اعلانات
users = {
    'admin': {
        'name': 'مدیر',
        'lastname': 'سیستم',
        'role': 'مدیر',
        'password': 'dabirstan012345'
    }
}

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

# داده‌های معلمان
teachers = {}

# داده‌های حضور و غیاب (در حافظه)
attendance_data = {}

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
        .btn-students { background: linear-gradient(45deg, #32cd32, #228b22); }
        .btn-attendance { background: linear-gradient(45deg, #ff6b6b, #ff8e53); }
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
            transition: transform 0.3s ease-out;
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
        .add-student-btn {
            position: fixed;
            bottom: 100px;
            right: 30px;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(45deg, #00eeff, #0066ff);
            border: none;
            color: white;
            font-size: 2rem;
            cursor: pointer;
            box-shadow: 0 10px 25px rgba(0, 238, 255, 0.4);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            z-index: 998;
        }
        .add-student-btn:hover {
            transform: translateY(-5px) scale(1.1);
            box-shadow: 0 15px 35px rgba(0, 238, 255, 0.6);
        }
        .add-student-btn:active {
            transform: translateY(2px) scale(0.95);
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
            cursor: pointer;
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
        .card-btn {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            border: none;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 1.2rem;
            font-weight: bold;
        }
        .edit-card-btn {
            background: linear-gradient(45deg, #ffcc00, #ff6600);
            color: white;
        }
        .delete-card-btn {
            background: linear-gradient(45deg, #ff0066, #ff00cc);
            color: white;
        }
        .card-btn:hover {
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
        /* حضور و غیاب */
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
        .attendance-actions {
            display: flex;
            gap: 15px;
            margin-top: 30px;
            justify-content: center;
        }
        .attendance-action-btn {
            padding: 15px 25px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        .submit-attendance-btn {
            background: linear-gradient(45deg, #00ff99, #00cc66);
            color: white;
        }
        .clear-attendance-btn {
            background: linear-gradient(45deg, #ff0066, #ff00cc);
            color: white;
        }
        .attendance-btn {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            border: 2px solid #ccc;
            background: transparent;
            cursor: pointer;
            margin-left: 10px;
            transition: all 0.3s ease;
        }
        .attendance-btn.absent {
            background: #ff4444;
            border-color: #ff4444;
        }
        .attendance-btn.present {
            background: #00ff00;
            border-color: #00ff00;
        }
        /* جستجوی تاریخ */
        .search-form {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin: 20px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        .search-buttons {
            display: flex;
            gap: 15px;
            margin-top: 20px;
            justify-content: center;
        }
        .search-btn {
            padding: 12px 25px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        .search-submit-btn {
            background: linear-gradient(45deg, #00eeff, #0066ff);
            color: white;
        }
        .search-back-btn {
            background: linear-gradient(45deg, #666666, #999999);
            color: white;
        }
        /* نوار اعلان جدید */
        .new-announcements-badge {
            position: absolute;
            top: -5px;
            right: -5px;
            background: #ff0000;
            color: white;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.7rem;
            font-weight: bold;
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
            .add-student-btn {
                bottom: 120px;
                right: 20px;
                width: 50px;
                height: 50px;
                font-size: 1.5rem;
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
            .card-btn {
                width: 35px;
                height: 35px;
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
            {% elif request.endpoint == 'login_teacher' %}
                <button class="back-btn" onclick="window.location.href='/'">← بازگشت</button>
                <div class="header">
                    <h1>ورود معلمان</h1>
                </div>
                <div class="form-container">
                    <form method="POST">
                        <div class="form-group">
                            <label for="teacher_name">نام:</label>
                            <input type="text" id="teacher_name" name="teacher_name" value="{{ request.form.teacher_name or '' }}" required>
                        </div>
                        <div class="form-group">
                            <label for="teacher_lastname">نام خانوادگی:</label>
                            <input type="text" id="teacher_lastname" name="teacher_lastname" value="{{ request.form.teacher_lastname or '' }}" required>
                        </div>
                        <div class="form-group">
                            <label for="teacher_grade">پایه:</label>
                            <select id="teacher_grade" name="teacher_grade" required>
                                <option value="">انتخاب کنید</option>
                                <option value="10" {{ 'selected' if request.form.teacher_grade == '10' }}>دهم</option>
                                <option value="11" {{ 'selected' if request.form.teacher_grade == '11' }}>یازدهم</option>
                                <option value="12" {{ 'selected' if request.form.teacher_grade == '12' }}>دوازدهم</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="teacher_field">رشته:</label>
                            <select id="teacher_field" name="teacher_field" required disabled>
                                <option value="">ابتدا پایه را انتخاب کنید</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="teacher_subject">درس:</label>
                            <input type="text" id="teacher_subject" name="teacher_subject" value="{{ request.form.teacher_subject or '' }}" required disabled>
                        </div>
                        <div class="form-group">
                            <label for="teacher_password">رمز ورود:</label>
                            <input type="password" id="teacher_password" name="teacher_password" required>
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
                    <div class="profile-item">
                        <div>
                            <div class="profile-label">مرتبه:</div>
                            <div class="profile-value" id="role-value">{{ session.role }}</div>
                        </div>
                        <button class="edit-btn" onclick="editField('role', '{{ session.role }}')">✎</button>
                    </div>
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
                            <div class="announcement-content">{{ announcement.content|safe }}</div>
                            <div class="announcement-meta">
                                <div>تاریخ: {{ announcement.date }}</div>
                                <div>زمان: {{ announcement.time }}</div>
                                {% if announcement.section %}<div>بخش: {{ announcement.section }}</div>{% endif %}
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
                        <div class="student-card" onclick="showStudentDetails({{ loop.index0 }}, '{{ field_key }}')">
                            <div class="student-card-header">
                                <div class="student-name">{{ student.name }} {{ student.lastname }}</div>
                                <div class="student-card-actions">
                                    <button class="card-btn edit-card-btn" onclick="event.stopPropagation(); editStudent({{ loop.index0 }}, '{{ field_key }}')">✎</button>
                                    <button class="card-btn delete-card-btn" onclick="event.stopPropagation(); deleteStudent({{ loop.index0 }}, '{{ field_key }}')">🗑️</button>
                                </div>
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
                <button class="add-student-btn" onclick="showAddStudentModal()">+</button>
            {% elif page == 'student_details' %}
                <button class="back-btn" onclick="window.location.href='/admin/students/{{ grade }}/{{ field }}'">← بازگشت</button>
                <div class="header">
                    <h1>اطلاعات دانش آموز</h1>
                </div>
                <div class="student-details-container">
                    {% set student = students[field_key][student_index] %}
                    <div class="student-detail-item">
                        <div class="student-detail-label">نام دانش آموز:</div>
                        <div class="student-detail-value">{{ student.name }}</div>
                    </div>
                    <div class="student-detail-item">
                        <div class="student-detail-label">نام خانوادگی دانش آموز:</div>
                        <div class="student-detail-value">{{ student.lastname }}</div>
                    </div>
                    <div class="student-detail-item">
                        <div class="student-detail-label">کد ملی دانش آموز:</div>
                        <div class="student-detail-value">{{ student.national_id }}</div>
                    </div>
                    <div class="student-detail-item">
                        <div class="student-detail-label">شماره دانش آموز:</div>
                        <div class="student-detail-value">{{ student.student_phone or 'ثبت نشده' }}</div>
                    </div>
                    <div class="student-detail-item">
                        <div class="student-detail-label">شماره پدر:</div>
                        <div class="student-detail-value">{{ student.father_phone or 'ثبت نشده' }}</div>
                    </div>
                    <div class="student-detail-item">
                        <div class="student-detail-label">شماره مادر:</div>
                        <div class="student-detail-value">{{ student.mother_phone or 'ثبت نشده' }}</div>
                    </div>
                </div>
            {% elif page == 'add_student' %}
                <button class="back-btn" onclick="window.location.href='/admin/students/{{ grade }}/{{ field }}'">← بازگشت</button>
                <div class="header">
                    <h1>افزودن دانش آموز</h1>
                </div>
                <div class="form-container">
                    <form method="POST" action="/admin/students/{{ grade }}/{{ field }}/add">
                        <div class="form-group">
                            <label for="name">نام دانش آموز (اجباری):</label>
                            <input type="text" id="name" name="name" value="{{ request.form.name or '' }}" required>
                        </div>
                        <div class="form-group">
                            <label for="lastname">نام خانوادگی دانش آموز (اجباری):</label>
                            <input type="text" id="lastname" name="lastname" value="{{ request.form.lastname or '' }}" required>
                        </div>
                        <div class="form-group">
                            <label for="national_id">کد ملی دانش آموز (اجباری):</label>
                            <input type="text" id="national_id" name="national_id" value="{{ request.form.national_id or '' }}" required>
                        </div>
                        <div class="form-group">
                            <label for="student_phone">شماره دانش آموز (اختیاری):</label>
                            <input type="text" id="student_phone" name="student_phone" value="{{ request.form.student_phone or '' }}">
                        </div>
                        <div class="form-group">
                            <label for="father_phone">شماره پدر (اختیاری):</label>
                            <input type="text" id="father_phone" name="father_phone" value="{{ request.form.father_phone or '' }}">
                        </div>
                        <div class="form-group">
                            <label for="mother_phone">شماره مادر (اختیاری):</label>
                            <input type="text" id="mother_phone" name="mother_phone" value="{{ request.form.mother_phone or '' }}">
                        </div>
                        {% if error %}
                            <div class="error">{{ error }}</div>
                        {% endif %}
                        <button type="submit" class="submit-btn">تایید</button>
                    </form>
                </div>
            {% elif page == 'edit_student' %}
                <button class="back-btn" onclick="window.location.href='/admin/students/{{ grade }}/{{ field }}'">← بازگشت</button>
                <div class="header">
                    <h1>ویرایش دانش آموز</h1>
                </div>
                <div class="form-container">
                    {% set student = students[field_key][student_index] %}
                    <form method="POST" action="/admin/students/{{ grade }}/{{ field }}/edit/{{ student_index }}">
                        <div class="form-group">
                            <label for="name">نام دانش آموز (اجباری):</label>
                            <input type="text" id="name" name="name" value="{{ student.name }}" required>
                        </div>
                        <div class="form-group">
                            <label for="lastname">نام خانوادگی دانش آموز (اجباری):</label>
                            <input type="text" id="lastname" name="lastname" value="{{ student.lastname }}" required>
                        </div>
                        <div class="form-group">
                            <label for="national_id">کد ملی دانش آموز (اجباری):</label>
                            <input type="text" id="national_id" name="national_id" value="{{ student.national_id }}" required>
                        </div>
                        <div class="form-group">
                            <label for="student_phone">شماره دانش آموز (اختیاری):</label>
                            <input type="text" id="student_phone" name="student_phone" value="{{ student.student_phone or '' }}">
                        </div>
                        <div class="form-group">
                            <label for="father_phone">شماره پدر (اختیاری):</label>
                            <input type="text" id="father_phone" name="father_phone" value="{{ student.father_phone or '' }}">
                        </div>
                        <div class="form-group">
                            <label for="mother_phone">شماره مادر (اختیاری):</label>
                            <input type="text" id="mother_phone" name="mother_phone" value="{{ student.mother_phone or '' }}">
                        </div>
                        {% if error %}
                            <div class="error">{{ error }}</div>
                        {% endif %}
                        <button type="submit" class="submit-btn">تایید</button>
                    </form>
                </div>
            {% elif page == 'attendance' %}
                <button class="back-btn" onclick="window.location.href='/teacher'">← بازگشت</button>
                <div class="header">
                    <h1>حضور و غیاب</h1>
                </div>
                <div class="grid-buttons">
                    <button class="btn btn-grade" onclick="window.location.href='/teacher/attendance/10'">پایه دهم</button>
                    <button class="btn btn-grade" onclick="window.location.href='/teacher/attendance/11'">پایه یازدهم</button>
                    <button class="btn btn-grade" onclick="window.location.href='/teacher/attendance/12'">پایه دوازدهم</button>
                </div>
            {% elif page == 'attendance_grade' %}
                <button class="back-btn" onclick="window.location.href='/teacher/attendance'">← بازگشت</button>
                <div class="header">
                    <h1>پایه {{ grade }}</h1>
                </div>
                <div class="grid-buttons">
                    <button class="btn btn-field" onclick="window.location.href='/teacher/attendance/{{ grade }}/math'">رشته ریاضی</button>
                    <button class="btn btn-field" onclick="window.location.href='/teacher/attendance/{{ grade }}/science'">رشته تجربی</button>
                    <button class="btn btn-field" onclick="window.location.href='/teacher/attendance/{{ grade }}/humanities'">رشته انسانی</button>
                </div>
            {% elif page == 'attendance_field' %}
                <button class="back-btn" onclick="window.location.href='/teacher/attendance/{{ grade }}'">← بازگشت</button>
                <div class="header">
                    <h1>{{ field_name }} پایه {{ grade }}</h1>
                </div>
                <div class="student-count">
                    <span class="student-count-icon">👤</span>
                    <span>تعداد دانش آموزان: <span id="studentCount">{{ students[field_key]|length }}</span></span>
                </div>
                <div class="attendance-stats">
                    <div class="absent-count">غائب: <span id="absentCount">0</span></div>
                    <div class="present-count">حاضر: <span id="presentCount">0</span></div>
                </div>
                {% if students[field_key] %}
                    <div class="students-grid">
                        {% for student in students[field_key] %}
                        <div class="student-card">
                            <div class="student-card-header">
                                <div class="student-name">{{ student.name }} {{ student.lastname }}</div>
                                <div class="student-card-actions">
                                    <button class="attendance-btn absent-btn" data-index="{{ loop.index0 }}" onclick="toggleAttendance({{ loop.index0 }}, 'absent')">✗</button>
                                    <button class="attendance-btn present-btn" data-index="{{ loop.index0 }}" onclick="toggleAttendance({{ loop.index0 }}, 'present')">✓</button>
                                </div>
                            </div>
                            <div class="student-info">
                                <div class="student-info-item student-national-id">کد ملی: {{ student.national_id }}</div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                    <div class="attendance-actions">
                        <button class="attendance-action-btn submit-attendance-btn" onclick="showSubmitAttendanceModal()">ارسال فرم حضور و غیاب</button>
                        <button class="attendance-action-btn clear-attendance-btn" onclick="showClearAttendanceModal()">پاک کردن انتخاب شدگان</button>
                    </div>
                {% else %}
                    <div class="welcome-text">
                        <p>هنوز هیچ دانش آموزی ثبت نشده است</p>
                    </div>
                {% endif %}
            {% elif page == 'submit_attendance' %}
                <button class="back-btn" onclick="window.location.href='/teacher/attendance/{{ grade }}/{{ field }}'">← بازگشت</button>
                <div class="header">
                    <h1>ثبت تاریخ حضور و غیاب</h1>
                </div>
                <div class="form-container">
                    <form method="POST" action="/teacher/attendance/{{ grade }}/{{ field }}/submit">
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
            {% elif page == 'search_announcements' %}
                <button class="back-btn" onclick="window.location.href='/{{ 'admin' if session.role == 'مدیر' else 'teacher' }}/announcements'">← بازگشت</button>
                <div class="header">
                    <h1>جستجوی اعلانات</h1>
                </div>
                <div class="search-form">
                    <form method="POST" action="/{{ 'admin' if session.role == 'مدیر' else 'teacher' }}/announcements/search">
                        <div class="form-group">
                            <label for="search_day">روز:</label>
                            <select id="search_day" name="search_day">
                                <option value="">انتخاب کنید</option>
                                {% for i in range(1, 32) %}
                                <option value="{{ i }}">{{ i }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="search_month">ماه:</label>
                            <select id="search_month" name="search_month">
                                <option value="">انتخاب کنید</option>
                                {% for i in range(1, 13) %}
                                <option value="{{ i }}">{{ i }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="search_year">سال:</label>
                            <select id="search_year" name="search_year">
                                <option value="">انتخاب کنید</option>
                                {% for i in range(1404, 1451) %}
                                <option value="{{ i }}">{{ i }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="search_weekday">روز هفته (اختیاری):</label>
                            <select id="search_weekday" name="search_weekday">
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
                        <div class="search-buttons">
                            <button type="submit" class="search-btn search-submit-btn">جستجو</button>
                            <button type="button" class="search-btn search-back-btn" onclick="window.location.href='/{{ 'admin' if session.role == 'مدیر' else 'teacher' }}/announcements'">برگشت به اعلانات</button>
                        </div>
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
                    <button class="btn btn-announcement" onclick="window.location.href='/{{ 'admin' if session.role == 'مدیر' else 'teacher' }}/announcements'">
                        اعلانات
                        {% if session.new_announcements %}
                        <span class="new-announcements-badge">{{ session.new_announcements }}</span>
                        {% endif %}
                    </button>
                    {% if session.role == 'مدیر' %}
                    <button class="btn btn-students" onclick="window.location.href='/admin/students'">دانش آموزان</button>
                    {% else %}
                    <button class="btn btn-attendance" onclick="window.location.href='/teacher/attendance'">حضور و غیاب</button>
                    {% endif %}
                </div>
            {% endif %}
        {% endif %}
    </div>
    {% if session.get('logged_in') and page not in ['add_student', 'edit_student', 'submit_attendance'] %}
        <div class="toolbar" id="toolbar">
            <a href="/{{ 'admin' if session.role == 'مدیر' else 'teacher' }}" class="toolbar-item {{ 'active' if page not in ['profile', 'announcements', 'students', 'grade_students', 'field_students', 'student_details', 'add_student', 'edit_student', 'attendance', 'attendance_grade', 'attendance_field', 'search_announcements'] }}">
                <div class="toolbar-icon">🏠</div>
                <span>صفحه اصلی</span>
            </a>
            <a href="/{{ 'admin' if session.role == 'مدیر' else 'teacher' }}/announcements" class="toolbar-item {{ 'active' if page == 'announcements' or page == 'search_announcements' }}">
                <div class="toolbar-icon">📢</div>
                <span>اعلانات</span>
                {% if session.new_announcements %}
                <span class="new-announcements-badge">{{ session.new_announcements }}</span>
                {% endif %}
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
    <!-- مودال حذف دانش آموز -->
    <div id="deleteStudentModal" class="modal">
        <div class="modal-content">
            <h3>آیا مطمئن هستید می‌خواهید اطلاعات دانش آموز را پاک کنید؟</h3>
            <div class="modal-buttons">
                <button class="modal-btn modal-btn-yes" onclick="confirmDeleteStudent()">بله</button>
                <button class="modal-btn modal-btn-no" onclick="closeModal('deleteStudentModal')">خیر</button>
            </div>
        </div>
    </div>
    <!-- مودال ارسال حضور و غیاب -->
    <div id="submitAttendanceModal" class="modal">
        <div class="modal-content">
            <h3>آیا مطمئن هستید می‌خواهید فرم حضور و غیاب را ارسال کنید؟</h3>
            <div class="modal-buttons">
                <button class="modal-btn modal-btn-yes" onclick="confirmSubmitAttendance()">بله</button>
                <button class="modal-btn modal-btn-no" onclick="closeModal('submitAttendanceModal')">خیر</button>
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
        let selectedAttendance = {};
        
        // تابع برای پنهان کردن تولبار
        function hideToolbar() {
            const toolbar = document.getElementById('toolbar');
            if (toolbar) {
                toolbar.classList.add('hidden');
            }
        }
        
        // تابع برای نمایش تولبار
        function showToolbar() {
            const toolbar = document.getElementById('toolbar');
            if (toolbar) {
                toolbar.classList.remove('hidden');
            }
        }
        
        // پنهان کردن تولبار در صفحات خاص
        document.addEventListener('DOMContentLoaded', function() {
            const currentPage = '{{ page }}';
            const pagesToHideToolbar = ['add_student', 'edit_student', 'submit_attendance'];
            if (pagesToHideToolbar.includes(currentPage)) {
                hideToolbar();
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
        
        function showAddStudentModal() {
            window.location.href = window.location.pathname + '/add';
        }
        
        function editStudent(index, field) {
            window.location.href = window.location.pathname + '/edit/' + index;
        }
        
        function deleteStudent(index, field) {
            pendingDeleteIndex = index;
            pendingDeleteField = field;
            document.getElementById('deleteStudentModal').style.display = 'flex';
        }
        
        function confirmDeleteStudent() {
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = '/admin/students/' + pendingDeleteField + '/delete/' + pendingDeleteIndex;
            document.body.appendChild(form);
            form.submit();
        }
        
        function showStudentDetails(index, field) {
            window.location.href = window.location.pathname + '/details/' + index;
        }
        
        // حضور و غیاب
        function toggleAttendance(index, type) {
            const absentBtn = document.querySelector(`.absent-btn[data-index="${index}"]`);
            const presentBtn = document.querySelector(`.present-btn[data-index="${index}"]`);
            
            if (type === 'absent') {
                if (selectedAttendance[index] === 'absent') {
                    // غیرفعال کردن
                    absentBtn.classList.remove('absent');
                    delete selectedAttendance[index];
                } else {
                    // فعال کردن غائب
                    absentBtn.classList.add('absent');
                    presentBtn.classList.remove('present');
                    selectedAttendance[index] = 'absent';
                }
            } else if (type === 'present') {
                if (selectedAttendance[index] === 'present') {
                    // غیرفعال کردن
                    presentBtn.classList.remove('present');
                    delete selectedAttendance[index];
                } else {
                    // فعال کردن حاضر
                    presentBtn.classList.add('present');
                    absentBtn.classList.remove('absent');
                    selectedAttendance[index] = 'present';
                }
            }
            
            updateAttendanceCounts();
        }
        
        function updateAttendanceCounts() {
            let absentCount = 0;
            let presentCount = 0;
            
            for (let key in selectedAttendance) {
                if (selectedAttendance[key] === 'absent') {
                    absentCount++;
                } else if (selectedAttendance[key] === 'present') {
                    presentCount++;
                }
            }
            
            document.getElementById('absentCount').textContent = absentCount;
            document.getElementById('presentCount').textContent = presentCount;
        }
        
        function showSubmitAttendanceModal() {
            // بررسی اینکه آیا حداقل یک دانش آموز انتخاب شده است
            if (Object.keys(selectedAttendance).length === 0) {
                alert('لطفاً حداقل یک دانش آموز را انتخاب کنید.');
                return;
            }
            document.getElementById('submitAttendanceModal').style.display = 'flex';
        }
        
        function confirmSubmitAttendance() {
            // ارسال داده‌های حضور و غیاب به سرور
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = window.location.pathname + '/submit_form';
            
            // اضافه کردن داده‌های انتخاب شده به فرم
            for (let key in selectedAttendance) {
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'attendance[' + key + ']';
                input.value = selectedAttendance[key];
                form.appendChild(input);
            }
            
            document.body.appendChild(form);
            form.submit();
        }
        
        function showClearAttendanceModal() {
            if (Object.keys(selectedAttendance).length === 0) {
                alert('هیچ دانش آموزی انتخاب نشده است.');
                return;
            }
            document.getElementById('clearAttendanceModal').style.display = 'flex';
        }
        
        function confirmClearAttendance() {
            // پاک کردن تمام انتخاب‌ها
            selectedAttendance = {};
            
            // پاک کردن کلاس‌های فعال از دکمه‌ها
            document.querySelectorAll('.attendance-btn').forEach(btn => {
                btn.classList.remove('absent', 'present');
            });
            
            // به‌روزرسانی شمارنده‌ها
            updateAttendanceCounts();
            
            // بستن مودال
            closeModal('clearAttendanceModal');
        }
        
        // بستن مودال‌ها با کلیک خارج از آن‌ها
        window.onclick = function(event) {
            const modals = ['logoutModal', 'deleteAnnouncementModal', 'deleteStudentModal', 'submitAttendanceModal', 'clearAttendanceModal'];
            modals.forEach(modalId => {
                const modal = document.getElementById(modalId);
                if (event.target === modal) {
                    modal.style.display = 'none';
                }
            });
        }
        
        // اسکریپت برای فرم ورود معلمان
        document.addEventListener('DOMContentLoaded', function() {
            const teacherGradeSelect = document.getElementById('teacher_grade');
            const teacherFieldSelect = document.getElementById('teacher_field');
            const teacherSubjectInput = document.getElementById('teacher_subject');
            
            if (teacherGradeSelect && teacherFieldSelect) {
                teacherGradeSelect.addEventListener('change', function() {
                    const grade = this.value;
                    teacherFieldSelect.disabled = !grade;
                    teacherSubjectInput.disabled = true;
                    
                    // پاک کردن گزینه‌های قبلی
                    teacherFieldSelect.innerHTML = '<option value="">انتخاب کنید</option>';
                    
                    if (grade) {
                        // اضافه کردن گزینه‌های رشته بر اساس پایه
                        const fields = {
                            '10': [
                                { value: 'math', text: 'ریاضی' },
                                { value: 'science', text: 'تجربی' },
                                { value: 'humanities', text: 'انسانی' }
                            ],
                            '11': [
                                { value: 'math', text: 'ریاضی' },
                                { value: 'science', text: 'تجربی' },
                                { value: 'humanities', text: 'انسانی' }
                            ],
                            '12': [
                                { value: 'math', text: 'ریاضی' },
                                { value: 'science', text: 'تجربی' },
                                { value: 'humanities', text: 'انسانی' }
                            ]
                        };
                        
                        fields[grade].forEach(field => {
                            const option = document.createElement('option');
                            option.value = field.value;
                            option.text = field.text;
                            teacherFieldSelect.appendChild(option);
                        });
                    }
                });
                
                teacherFieldSelect.addEventListener('change', function() {
                    teacherSubjectInput.disabled = !this.value;
                });
            }
        });
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
            session['user_type'] = 'admin'
            return redirect('/admin')
        else:
            return render_template_string(HTML_TEMPLATE, error='رمز ورود اشتباه است', page='login_admin')
    return render_template_string(HTML_TEMPLATE, page='login_admin')

@app.route('/login/teacher', methods=['GET', 'POST'])
def login_teacher():
    if request.method == 'POST':
        name = request.form['teacher_name']
        lastname = request.form['teacher_lastname']
        grade = request.form['teacher_grade']
        field = request.form['teacher_field']
        subject = request.form['teacher_subject']
        password = request.form['teacher_password']
        
        # بررسی فیلدهای اجباری
        if not name or not lastname or not grade or not field or not subject:
            return render_template_string(HTML_TEMPLATE, error='فیلدهای اجباری را پر کنید', page='login_teacher')
        
        if password == 'Dabirjavad01':
            # ایجاد کلید منحصر به فرد برای معلم
            teacher_key = f"{name}_{lastname}_{grade}_{field}_{subject}"
            
            # بررسی اینکه آیا معلم قبلاً ثبت نام کرده است
            if teacher_key in teachers:
                # اگر معلم قبلاً ثبت نام کرده باشد، اجازه ورود می‌دهیم
                session['logged_in'] = True
                session['name'] = name
                session['lastname'] = lastname
                session['grade'] = grade
                session['field'] = field
                session['subject'] = subject
                session['role'] = 'معلم'
                session['user_type'] = 'teacher'
                session['teacher_key'] = teacher_key
                return redirect('/teacher')
            else:
                # اگر معلم جدید است، اطلاعاتش را ذخیره می‌کنیم
                teachers[teacher_key] = {
                    'name': name,
                    'lastname': lastname,
                    'grade': grade,
                    'field': field,
                    'subject': subject
                }
                session['logged_in'] = True
                session['name'] = name
                session['lastname'] = lastname
                session['grade'] = grade
                session['field'] = field
                session['subject'] = subject
                session['role'] = 'معلم'
                session['user_type'] = 'teacher'
                session['teacher_key'] = teacher_key
                return redirect('/teacher')
        else:
            return render_template_string(HTML_TEMPLATE, error='رمز ورود اشتباه است', page='login_teacher')
    return render_template_string(HTML_TEMPLATE, page='login_teacher')

@app.route('/admin')
def admin_panel():
    if not session.get('logged_in') or session.get('user_type') != 'admin':
        return redirect('/')
    return render_template_string(HTML_TEMPLATE, page='admin')

@app.route('/teacher')
def teacher_panel():
    if not session.get('logged_in') or session.get('user_type') != 'teacher':
        return redirect('/')
    return render_template_string(HTML_TEMPLATE, page='teacher')

@app.route('/admin/profile')
def admin_profile():
    if not session.get('logged_in') or session.get('user_type') != 'admin':
        return redirect('/')
    return render_template_string(HTML_TEMPLATE, page='profile')

@app.route('/teacher/profile')
def teacher_profile():
    if not session.get('logged_in') or session.get('user_type') != 'teacher':
        return redirect('/')
    return render_template_string(HTML_TEMPLATE, page='profile')

@app.route('/admin/announcements')
def admin_announcements():
    if not session.get('logged_in') or session.get('user_type') != 'admin':
        return redirect('/')
    return render_template_string(HTML_TEMPLATE, page='announcements', announcements=announcements)

@app.route('/teacher/announcements')
def teacher_announcements():
    if not session.get('logged_in') or session.get('user_type') != 'teacher':
        return redirect('/')
    return render_template_string(HTML_TEMPLATE, page='announcements', announcements=announcements)

@app.route('/admin/announcements/search', methods=['POST'])
def admin_search_announcements():
    if not session.get('logged_in') or session.get('user_type') != 'admin':
        return redirect('/')
    
    day = request.form.get('search_day')
    month = request.form.get('search_month')
    year = request.form.get('search_year')
    weekday = request.form.get('search_weekday')
    
    # فیلتر کردن اعلانات بر اساس تاریخ
    filtered_announcements = []
    for announcement in announcements:
        # اینجا باید منطق فیلتر کردن را پیاده کنید
        # فرض می‌کنیم که تاریخ در فیلد date به فرمت "1404/09/01" ذخیره شده است
        if announcement.get('date'):
            date_parts = announcement['date'].split('/')
            if len(date_parts) == 3:
                ann_year, ann_month, ann_day = date_parts
                match = True
                if day and day != ann_day:
                    match = False
                if month and month != ann_month:
                    match = False
                if year and year != ann_year:
                    match = False
                # برای روز هفته فعلاً چک نمی‌کنیم چون در داده‌ها نیست
                if match:
                    filtered_announcements.append(announcement)
    
    return render_template_string(HTML_TEMPLATE, page='announcements', announcements=filtered_announcements)

@app.route('/teacher/announcements/search', methods=['POST'])
def teacher_search_announcements():
    if not session.get('logged_in') or session.get('user_type') != 'teacher':
        return redirect('/')
    
    day = request.form.get('search_day')
    month = request.form.get('search_month')
    year = request.form.get('search_year')
    weekday = request.form.get('search_weekday')
    
    # فیلتر کردن اعلانات بر اساس تاریخ
    filtered_announcements = []
    for announcement in announcements:
        # اینجا باید منطق فیلتر کردن را پیاده کنید
        # فرض می‌کنیم که تاریخ در فیلد date به فرمت "1404/09/01" ذخیره شده است
        if announcement.get('date'):
            date_parts = announcement['date'].split('/')
            if len(date_parts) == 3:
                ann_year, ann_month, ann_day = date_parts
                match = True
                if day and day != ann_day:
                    match = False
                if month and month != ann_month:
                    match = False
                if year and year != ann_year:
                    match = False
                # برای روز هفته فعلاً چک نمی‌کنیم چون در داده‌ها نیست
                if match:
                    filtered_announcements.append(announcement)
    
    return render_template_string(HTML_TEMPLATE, page='announcements', announcements=filtered_announcements)

@app.route('/admin/students')
def admin_students():
    if not session.get('logged_in') or session.get('user_type') != 'admin':
        return redirect('/')
    return render_template_string(HTML_TEMPLATE, page='students')

@app.route('/admin/students/<grade>')
def grade_students(grade):
    if not session.get('logged_in') or session.get('user_type') != 'admin':
        return redirect('/')
    return render_template_string(HTML_TEMPLATE, page='grade_students', grade=grade)

@app.route('/admin/students/<grade>/<field>')
def field_students(grade, field):
    if not session.get('logged_in') or session.get('user_type') != 'admin':
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

@app.route('/admin/students/<grade>/<field>/details/<int:index>')
def student_details(grade, field, index):
    if not session.get('logged_in') or session.get('user_type') != 'admin':
        return redirect('/')
    field_key = f"{field}_{grade}"
    if index >= len(students[field_key]):
        return redirect(f'/admin/students/{grade}/{field}')
    return render_template_string(HTML_TEMPLATE, 
                                page='student_details', 
                                grade=grade, 
                                field=field, 
                                field_key=field_key,
                                student_index=index,
                                students=students)

@app.route('/admin/students/<grade>/<field>/add', methods=['GET', 'POST'])
def add_student(grade, field):
    if not session.get('logged_in') or session.get('user_type') != 'admin':
        return redirect('/')
    field_key = f"{field}_{grade}"
    if request.method == 'POST':
        name = request.form['name']
        lastname = request.form['lastname']
        national_id = request.form['national_id']
        student_phone = request.form.get('student_phone', '')
        father_phone = request.form.get('father_phone', '')
        mother_phone = request.form.get('mother_phone', '')
        # بررسی فیلدهای اجباری
        if not name or not lastname or not national_id:
            return render_template_string(HTML_TEMPLATE, 
                                        page='add_student', 
                                        grade=grade, 
                                        field=field,
                                        error='فیلدهای اجباری را پر کنید')
        
        # بررسی تکراری بودن کد ملی
        for student in students[field_key]:
            if student['national_id'] == national_id:
                return render_template_string(HTML_TEMPLATE, 
                                            page='add_student', 
                                            grade=grade, 
                                            field=field,
                                            error='دانش آموزی با این کد ملی قبلاً ثبت شده است')
        
        # اضافه کردن دانش آموز
        new_student = {
            'name': name,
            'lastname': lastname,
            'national_id': national_id,
            'student_phone': student_phone,
            'father_phone': father_phone,
            'mother_phone': mother_phone
        }
        students[field_key].append(new_student)
        return redirect(f'/admin/students/{grade}/{field}')
    return render_template_string(HTML_TEMPLATE, 
                                page='add_student', 
                                grade=grade, 
                                field=field)

@app.route('/admin/students/<grade>/<field>/edit/<int:index>', methods=['GET', 'POST'])
def edit_student(grade, field, index):
    if not session.get('logged_in') or session.get('user_type') != 'admin':
        return redirect('/')
    field_key = f"{field}_{grade}"
    if index >= len(students[field_key]):
        return redirect(f'/admin/students/{grade}/{field}')
    if request.method == 'POST':
        name = request.form['name']
        lastname = request.form['lastname']
        national_id = request.form['national_id']
        student_phone = request.form.get('student_phone', '')
        father_phone = request.form.get('father_phone', '')
        mother_phone = request.form.get('mother_phone', '')
        # بررسی فیلدهای اجباری
        if not name or not lastname or not national_id:
            return render_template_string(HTML_TEMPLATE, 
                                        page='edit_student', 
                                        grade=grade, 
                                        field=field,
                                        field_key=field_key,
                                        student_index=index,
                                        students=students,
                                        error='فیلدهای اجباری را پر کنید')
        
        # بررسی تکراری بودن کد ملی (به جز برای دانش آموز فعلی)
        for i, student in enumerate(students[field_key]):
            if i != index and student['national_id'] == national_id:
                return render_template_string(HTML_TEMPLATE, 
                                            page='edit_student', 
                                            grade=grade, 
                                            field=field,
                                            field_key=field_key,
                                            student_index=index,
                                            students=students,
                                            error='دانش آموزی با این کد ملی قبلاً ثبت شده است')
        
        # ویرایش دانش آموز
        students[field_key][index] = {
            'name': name,
            'lastname': lastname,
            'national_id': national_id,
            'student_phone': student_phone,
            'father_phone': father_phone,
            'mother_phone': mother_phone
        }
        return redirect(f'/admin/students/{grade}/{field}')
    return render_template_string(HTML_TEMPLATE, 
                                page='edit_student', 
                                grade=grade, 
                                field=field,
                                field_key=field_key,
                                student_index=index,
                                students=students)

@app.route('/admin/students/<field_key>/delete/<int:index>', methods=['POST'])
def delete_student(field_key, index):
    if not session.get('logged_in') or session.get('user_type') != 'admin':
        return redirect('/')
    if index < len(students[field_key]):
        students[field_key].pop(index)
    # استخراج grade و field از field_key
    parts = field_key.split('_')
    field = parts[0]
    grade = parts[1]
    return redirect(f'/admin/students/{grade}/{field}')

@app.route('/teacher/attendance')
def teacher_attendance():
    if not session.get('logged_in') or session.get('user_type') != 'teacher':
        return redirect('/')
    return render_template_string(HTML_TEMPLATE, page='attendance')

@app.route('/teacher/attendance/<grade>')
def attendance_grade(grade):
    if not session.get('logged_in') or session.get('user_type') != 'teacher':
        return redirect('/')
    return render_template_string(HTML_TEMPLATE, page='attendance_grade', grade=grade)

@app.route('/teacher/attendance/<grade>/<field>')
def attendance_field(grade, field):
    if not session.get('logged_in') or session.get('user_type') != 'teacher':
        return redirect('/')
    field_mapping = {
        'math': 'ریاضی',
        'science': 'تجربی',
        'humanities': 'انسانی'
    }
    field_key = f"{field}_{grade}"
    field_name = field_mapping.get(field, field)
    return render_template_string(HTML_TEMPLATE, 
                                page='attendance_field', 
                                grade=grade, 
                                field=field, 
                                field_key=field_key, 
                                field_name=field_name,
                                students=students)

@app.route('/teacher/attendance/<grade>/<field>/submit_form', methods=['POST'])
def submit_attendance_form(grade, field):
    if not session.get('logged_in') or session.get('user_type') != 'teacher':
        return redirect('/')
    
    # دریافت داده‌های حضور و غیاب
    attendance_data = request.form.get('attendance')
    if not attendance_data:
        return redirect(f'/teacher/attendance/{grade}/{field}')
    
    field_key = f"{field}_{grade}"
    return render_template_string(HTML_TEMPLATE, 
                                page='submit_attendance', 
                                grade=grade, 
                                field=field,
                                field_key=field_key)

@app.route('/teacher/attendance/<grade>/<field>/submit', methods=['POST'])
def submit_attendance(grade, field):
    if not session.get('logged_in') or session.get('user_type') != 'teacher':
        return redirect('/')
    
    day = request.form['day']
    month = request.form['month']
    year = request.form['year']
    weekday = request.form.get('weekday', '')
    
    # بررسی فیلدهای اجباری
    if not day or not month or not year:
        field_key = f"{field}_{grade}"
        return render_template_string(HTML_TEMPLATE, 
                                    page='submit_attendance', 
                                    grade=grade, 
                                    field=field,
                                    field_key=field_key,
                                    error='فیلدهای اجباری را پر کنید')
    
    # ایجاد پیام اعلان
    teacher_name = session['name']
    teacher_lastname = session['lastname']
    teacher_grade = session['grade']
    teacher_field = session['field']
    teacher_subject = session['subject']
    
    field_mapping = {
        'math': 'ریاضی',
        'science': 'تجربی',
        'humanities': 'انسانی'
    }
    field_name = field_mapping.get(teacher_field, teacher_field)
    
    # دریافت داده‌های حضور و غیاب از session یا بازسازی آن‌ها
    # برای سادگی، فرض می‌کنیم داده‌ها در session ذخیره شده‌اند
    # در عمل باید این داده‌ها را از صفحه قبل دریافت کنید
    present_students = []
    absent_students = []
    
    # اینجا باید منطق واقعی برای دریافت لیست حاضران و غایبان را پیاده کنید
    # فعلاً یک مثال ساده:
    present_students = ["محمدرضا محمدی", "ارشیا محمدی"]
    absent_students = ["اریان برومندی"]
    
    # ایجاد محتوای اعلان
    announcement_content = f"""
    <p><strong>نام معلم:</strong> {teacher_name} {teacher_lastname}</p>
    <p><strong>پایه:</strong> {teacher_grade}</p>
    <p><strong>رشته:</strong> {field_name}</p>
    <p><strong>درس:</strong> {teacher_subject}</p>
    <br>
    <p><strong>تاریخ:</strong> {weekday} - {year}/{month}/{day}</p>
    <br>
    <div style="display: flex; justify-content: space-between;">
        <div style="color: #ff4444;">
            <p><strong>غائبین:</strong></p>
            <ul>
                {''.join([f'<li>{student}</li>' for student in absent_students])}
            </ul>
        </div>
        <div style="color: #00ff00;">
            <p><strong>حاضرین:</strong></p>
            <ul>
                {''.join([f'<li>{student}</li>' for student in present_students])}
            </ul>
        </div>
    </div>
    """
    
    # اضافه کردن اعلان برای مدیر
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    announcement = {
        'title': f"فرم حضور و غیاب - {teacher_name} {teacher_lastname}",
        'content': announcement_content,
        'date': f"{year}/{month}/{day}",
        'time': current_time,
        'section': 'حضور و غیاب'
    }
    announcements.append(announcement)
    
    # اضافه کردن اعلان برای معلم (سوابق)
    teacher_announcement = {
        'title': f"سوابق حضور و غیاب - {year}/{month}/{day}",
        'content': announcement_content,
        'date': f"{year}/{month}/{day}",
        'time': current_time,
        'section': 'سوابق'
    }
    # برای سادگی، فرض می‌کنیم اعلان‌های معلم در یک لیست جداگانه ذخیره می‌شوند
    # در عمل می‌توانید از یک ساختار داده پیچیده‌تر استفاده کنید
    # مثلاً یک دیکشنری که کلید آن teacher_key است
    
    return redirect('/teacher')

@app.route('/edit_profile', methods=['POST'])
def edit_profile():
    if not session.get('logged_in'):
        return redirect('/')
    field = request.form['field']
    value = request.form['value']
    if field in ['name', 'lastname', 'role']:
        session[field] = value
    return redirect(f'/{session["user_type"]}/profile')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
