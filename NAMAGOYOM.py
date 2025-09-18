from flask import Flask, render_template_string, request, jsonify, redirect, url_for, session
import re
import json
from datetime import datetime
import os
import base64
import uuid

app = Flask(__name__)
app.secret_key = 'a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2'

# دیتابس ساده برای ذخیره کاربران
users_db = {}

# دیتابس برای مکان‌ها
locations_db = []

# دیتابس برای پیام‌های چت (کلید: tuple(sender, receiver))
chats_db = {}

# دیتابس برای نظرات (کلید: location_id)
comments_db = {}

# دیتابس برای اعلان‌ها (کلید: username)
notifications_db = {}

# لیست شهرها/شهرک‌ها
CITIES = [
    "شهرک صدرا", "شهرک گلستان", "معالی آباد", "شهرک کشن", "شهرک مهدیه",
    "شهرک زینبیه", "شهرک بعثت", "شهرک والفجر", "شهرک صنعتی عفیف آباد",
    "کوی امام رضا", "شهرک گویم", "شهرک بزین", "شهرک رحمت آباد", "شهرک خورشید",
    "شهرک سلامت", "شهرک فرهنگیان", "کوی زاگرس", "کوی پاسداران", "شهرک عرفان",
    "شهرک هنرستان"
]

# دسته‌بندی‌ها و زیر دسته‌ها
CATEGORIES = {
    "🍽️ خوراکی و نوشیدنی": [
        "رستوران‌ها (سنتی، فست فود، بین‌المللی، دریایی، گیاهخواری)",
        "کافه و کافی‌شاپ (کافه‌رستوران، قهوه تخصصی)",
        "بستنی‌فروشی و آبمیوه‌فروشی (بستنی سنتی، بستنی ایتالیایی)",
        "شیرینی‌پزی و نانوایی (نانوایی سنتی، شیرینی‌پزی قنادی)",
        "سفره‌خانه و چایخانه (قهوه خانه سنتی، چایخانه مدرن)",
        "فودکورت و مراکز غذاخوری",
        "کبابی و جگرکی (کباب‌فروشی، جگرکی، دیزی‌سرا)",
        "ساندویچ‌فروشی و پیتزافروشی (پیتزافروشی، ساندویچ‌فروشی محلی)",
        "قنادی و شکلات‌فروشی (شکلات‌فروشی تخصصی، آبنبات‌فروشی)",
        "آجیل‌فروشی و خشکبار (آجیل‌فروشی، خشکبارفروشی)",
        "سوپرمارکت محلی و هایپر",
        "قصابی و مرغ فروشی (قصابی، مرغ‌فروشی، ماهی‌فروشی)",
        "میوه‌فروشی و تره‌بار (میوه‌فروشی، سبزی‌فروشی)",
        "ماهی‌فروشی و غذاهای دریایی",
        "فروشگاه مواد غذایی محلی",
        "عسل‌فروشی و محصولات زنبورداری",
        "محصولات محلی و منطقه‌ای",
        "فروشگاه محصولات ارگانیک",
        "فروشگاه مواد غذایی منجمد",
        "فروشگاه محصولات لبنی و پنیر",
        "نان‌فروشی تخصصی (نان باگت، نان سنگک)",
        "غذاهای محلی و غذاهای قومی"
    ],
    "🛍️ خرید و فروش": [
        "پاساژها و مراکز خرید (مال، مرکز خرید، بازارچه)",
        "سوپرمارکت و هایپرمارکت (زنجیره‌ای، محلی)",
        "فروشگاه زنجیره‌ای",
        "بازار سنتی و بازارچه‌های محلی (بازار روز، بازار هفتگی)",
        "فروشگاه پوشاک و کیف و کفش (لباس مردانه، زنانه، بچگانه)",
        "فروشگاه لوازم خانگی و الکترونیک (لوازم برقی، دیجیتال)",
        "فروشگاه لوازم ورزشی (ورزشی، کوهنوردی، شنا)",
        "کتاب‌فروشی و لوازم التحریر (کتاب‌فروشی عمومی، تخصصی)",
        "مغازه موبایل و لپ‌تاپ (فروش، تعمیر، لوازم جانبی)",
        "گل‌فروشی و گیاهان آپارتمانی (گل‌فروشی، گل‌آرایی)",
        "عینک‌فروشی و اپتیک (عینک‌فروشی، عینک‌سازی)",
        "عطر و ادکلن فروشی (عطر فروشی، محصولات آرایشی)",
        "طلا و جواهر فروشی (طلافروشی، جواهرفروشی)",
        "ساعت‌فروشی (ساعت مچی، دیواری)",
        "لوازم آرایشی و بهداشتی (آرایشی، بهداشتی، مراقبت پوست)",
        "اسباب‌بازی‌فروشی (اسباب‌بازی، بازی فکری)",
        "صنایع‌دستی و سوغاتی‌فروشی (صنایع دستی، سوغات)",
        "دکوراسیون و لوازم منزل (دکوراسیون، لوازم تزئینی)",
        "فرش و گلیم فروشی (فرش‌فروشی، گلیم‌فروشی)",
        "پارچه‌فروشی و خیاطی (پارچه‌فروشی، خیاطی)",
        "چرم‌فروشی و کیف‌سازی (چرم‌فروشی، کیف‌دوزی)",
        "فروشگاه لوازم آشپزخانه (ظروف، لوازم آشپزی)",
        "فروشگاه لوازم باغبانی (لوازم باغبانی، نهال)",
        "فروشگاه حیوانات خانگی (حیوانات، غذای حیوانات)",
        "فروشگاه دوچرخه و اسکوتر (دوچرخه، اسکوتر، لوازم)",
        "فروشگاه ابزارآلات (ابزار صنعتی، دستی)",
        "فروشگاه کامپیوتر و گیم (کامپیوتر، کنسول بازی)",
        "فروشگاه لباس عروس و مراسم",
        "فروشگاه کادو و هدیه",
        "فروشگاه محصولات فرهنگی (سی دی، دی وی دی، آثار هنری)",
        "فروشگاه محصولات دست‌دوم",
        "فروشگاه محصولات سلامت و تندرستی",
        "فروشگاه محصولات روستایی و محلی"
    ],
    "✂️ زیبایی و آرایشی": [
        "آرایشگاه مردانه (آرایشگاه، اصلاح)",
        "آرایشگاه زنانه (آرایش، رنگ مو)",
        "سالن‌های زیبایی و اسپا (اسپا، ماساژ)",
        "مژه و ابرو (اکستنشن مژه، میکروبلیدینگ)",
        "ناخن‌کاری (مانیکور، پدیکور، ناخن مصنوعی)",
        "تتو و میکروپیگمنتیشن (تاتو، میکروپیگمنتیشن)",
        "سالن‌های تاتو و پیرسینگ (پیرسینگ، تاتو حنایی)",
        "مراکز خدمات پوست و مو (پاکسازی پوست، لیزر)",
        "فروشگاه لوازم آرایشی حرفه‌ای",
        "مراکز ماساژ و ریلکسیشن (ماساژ درمانی، ریلکسیشن)",
        "مراکز اپیلاسیون و لیزر",
        "سالن‌های برنزه کردن",
        "مراکز مشاوره زیبایی",
        "آموزشگاه‌های آرایشگری",
        "مراکز خدمات بهداشتی مردانه"
    ],
    "🏥 درمان و سلامت": [
        "بیمارستان و مراکز درمانی (عمومی، تخصصی، خصوصی)",
        "درمانگاه و کلینیک‌های تخصصی (خانواده، زنان، قلب)",
        "داروخانه (شبانه‌روزی، گیاهی)",
        "دندان‌پزشکی و ارتودنسی (عمومی، تخصصی، زیبایی)",
        "آزمایشگاه پزشکی و رادیولوژی (آزمایشگاه، سونوگرافی)",
        "کلینیک زیبایی و لیزر (لیزر، بوتاکس، ژل)",
        "مراکز فیزیوتراپی و کاردرمانی (فیزیوتراپی، کاردرمانی)",
        "دامپزشکی و کلینیک حیوانات (دامپزشکی، حیوانات خانگی)",
        "مراکز توانبخشی (توانبخشی، گفتاردرمانی)",
        "مراکز مشاوره و روانشناسی (مشاوره، روانشناسی)",
        "شنوایی‌سنجی و سمعک (سمعک، شنوایی‌سنجی)",
        "بینایی‌سنجی و عینک‌سازی (بینایی‌سنجی، عینک‌سازی)",
        "پرستاری در منزل (پرستار، پزشک در منزل)",
        "تجهیزات پزشکی (فروش، اجاره)",
        "مراکز اهدای خون",
        "مراکز طب سنتی و گیاهان دارویی",
        "مراکز ماساژ درمانی",
        "مراکز ترک اعتیاد",
        "مراکز خدمات پرستاری",
        "مراکز خدمات پزشکی سیار",
        "مراکز تصویربرداری پزشکی",
        "مراکز خدمات پزشکی ورزشی"
    ],
    "⚽ ورزش و سرگرمی": [
        "باشگاه ورزشی و بدنسازی (بدنسازی، کراسفیت)",
        "استخر و مجموعه ورزشی (استخر، سونا، جکوزی)",
        "سالن فوتسال و بسکتبال (فوتسال، بسکتبال، والیبال)",
        "سینما و تئاتر (سینما، تئاتر، نمایش)",
        "شهربازی و پارک بازی (شهربازی، پارک بازی)",
        "بیلیارد و بولینگ (بیلیارد، بولینگ، دارت)",
        "مراکز تفریحی خانوادگی (تفریحی، بازی)",
        "مراکز فرهنگی و هنری (فرهنگی، هنری)",
        "سالن‌های کنسرت و نمایش (کنسرت، نمایش)",
        "گیم‌نت و مراکز بازی (گیم‌نت، بازی کامپیوتری)",
        "پارک‌های تفریحی و شهربازی (شهربازی، پارک تفریحی)",
        "باشگاه تیراندازی (تیراندازی، کمان‌اندازی)",
        "باشگاه سینما و خانه فیلم",
        "مراکز آموزشی موسیقی (آموزش موسیقی، نوازندگی)",
        "کتابخانه عمومی (عمومی، تخصصی)",
        "نگارخانه و نمایشگاه هنری (نگارخانه، نمایشگاه)",
        "مراکز بازی اتاق فرار",
        "مراکز پینت بال و لیزرتگ",
        "باشگاه‌های رقص و باله",
        "مراکز یوگا و مدیتیشن",
        "باشگاه‌های ورزش‌های رزمی",
        "مراکز اسکیت و رولر",
        "باشگاه‌های بوکس و هنرهای رزمی ترکیبی",
        "مراکز ورزش‌های آبی",
        "باشگاه‌های گلف و تنیس",
        "مراکز ماهیگیری و شکار",
        "باشگاه‌های سوارکاری"
    ],
    "🏨 اقامت و سفر": [
        "هتل و هتل آپارتمان (هتل، هتل آپارتمان)",
        "مسافرخانه و مهمانپذیر (مسافرخانه، مهمانپذیر)",
        "اقامتگاه بوم‌گردی (بوم‌گردی، اقامتگاه محلی)",
        "ویلا و سوئیت اجاره‌ای (ویلا، سوئیت)",
        "کمپینگ و اردوگاه (کمپینگ، اردوگاه)",
        "آژانس مسافرتی و گردشگری (مسافرتی، گردشگری)",
        "ایستگاه قطار و اتوبوس (قطار، اتوبوس)",
        "فرودگاه و پایانه مسافری (فرودگاه، پایانه)",
        "مراکز رزرواسیون (رزرو هتل، بلیط)",
        "خدمات ویزا و پاسپورت (ویزا، پاسپورت)",
        "اجاره خودرو و دوچرخه (اجاره ماشین، دوچرخه)",
        "راهنمایان گردشگری (تورلیدر، راهنما)",
        "مراکز اطلاعات گردشگری",
        "خدمات ترجمه و راهنمای محلی",
        "مراکز کرایه اتومبیل",
        "خدمات انتقال مسافر (حمل و نقل، ترانسفر)",
        "مراکز رزرواسیون آنلاین",
        "خدمات بیمه مسافرتی",
        "مراکز خدمات جهانگردی"
    ],
    "🏛️ خدمات عمومی و اداری": [
        "بانک و خودپرداز (بانک، صرافی)",
        "اداره پست (پست، پیک موتوری)",
        "دفاتر پیشخوان خدمات دولت (پیشخوان، خدمات الکترونیک)",
        "شهرداری و مراکز خدمات شهری (شهرداری، خدمات شهری)",
        "اداره برق، آب، گاز (برق، آب، گاز)",
        "پلیس +۱۰ و مراکز انتظامی (پلیس، انتظامی)",
        "دادگاه و مراجع قضایی (دادگاه، قضایی)",
        "کلانتری و پاسگاه (کلانتری، پاسگاه)",
        "دفاتر اسناد رسمی (اسناد رسمی، دفترخانه)",
        "مراکز صدور گواهینامه (گواهینامه، مدارک)",
        "ادارات دولتی و وزارتخانه‌ها (دولتی، وزارتخانه)",
        "کنسولگری و سفارتخانه‌ها (سفارت، کنسولگری)",
        "مراکز خدمات الکترونیک (خدمات آنلاین، دولت الکترونیک)",
        "مراکز خدمات مشاوره شغلی",
        "دفاتر خدمات مسکن و املاک",
        "مراکز خدمات حقوقی و قضایی",
        "دفاتر خدمات مهاجرتی",
        "مراکز خدمات مالی و حسابداری",
        "دفاتر خدمات بیمه‌ای",
        "مراکز خدمات تعمیرات شهری",
        "دفاتر خدمات پیمانکاری"
    ],
    "🚗 خدمات شهری و حمل‌ونقل": [
        "پمپ بنزین و CNG (بنزین، گاز)",
        "کارواش و خدمات خودرو (کارواش، براق‌سازی)",
        "تعمیرگاه خودرو و موتورسیکلت (تعمیرگاه، مکانیکی)",
        "تاکسی‌سرویس و تاکسی اینترنتی (تاکسی، اسنپ)",
        "پارکینگ عمومی (پارکینگ، جای پارک)",
        "مکانیکی و برق خودرو (مکانیک، برق خودرو)",
        "لاستیک‌فروشی و فروش لوازم یدکی (لاستیک، لوازم یدکی)",
        "خدمات نقاشی و ترمیم خودرو (نقاشی، ترمیم)",
        "مراکز معاینه فنی (معاینه فنی، تست خودرو)",
        "خدمات امداد خودرو (خدمات امدادی، یدک‌کش)",
        "نمایندگی خودرو (نمایندگی، فروش خودرو)",
        "فروشگاه لوازم جانبی خودرو (لوازم جانبی، تزئینات)",
        "خدمات تنظیم موتور و انژکتور",
        "خدمات صافکاری و جلوبندی",
        "خدمات تعویض روغن و فیلتر",
        "خدمات سیستم تهویه و کولر",
        "خدمات تعمیرات تخصصی خودرو",
        "خدمات کارت‌خوان و پرداخت",
        "خدمات پخش محصولات خودرویی",
        "خدمات حمل و نقل معلولین و سالمندان"
    ],
    "📚 آموزش و فرهنگ": [
        "مدرسه و آموزشگاه (دبستان، دبیرستان)",
        "دانشگاه و مراکز آموزش عالی (دانشگاه، موسسه آموزش عالی)",
        "آموزشگاه زبان (زبان انگلیسی، سایر زبان‌ها)",
        "آموزشگاه فنی‌وحرفه‌ای (فنی، حرفه‌ای)",
        "کتابخانه عمومی (عمومی، تخصصی)",
        "فرهنگسرا و خانه فرهنگ (فرهنگسرا، خانه فرهنگ)",
        "موزه و گالری (موزه، گالری هنری)",
        "مراکز آموزشی کامپیوتر (کامپیوتر، برنامه‌نویسی)",
        "مراکز مشاوره تحصیلی (مشاوره، انتخاب رشته)",
        "آموزشگاه‌های هنری (نقاشی، مجسمه‌سازی)",
        "مراکز آموزشی رانندگی (آموزش رانندگی، آیین‌نامه)",
        "مهدکودک و پیش‌دبستانی (مهدکودک، پیش‌دبستانی)",
        "مراکز آموزش علوم مختلف (ریاضی، فیزیک، شیمی)",
        "مراکز آموزش مهارت‌های زندگی",
        "آموزشگاه‌های آشپزی و شیرینی‌پزی",
        "مراکز آموزش خلاقیت کودکان",
        "آموزشگاه‌های کنکور و آزمون",
        "مراکز آموزش از راه دور",
        "آموزشگاه‌های مهارت‌آموزی",
        "مراکز آموزش صنایع دستی",
        "آموزشگاه‌های خیاطی و طراحی لباس",
        "مراکز آموزش عکاسی و فیلمبرداری",
        "آموزشگاه‌های ورزشی تخصصی",
        "مراکز آموزش موسیقی محلی",
        "آموزشگاه‌های زبان اشاره",
        "خدمات آموزش مجازی و آنلاین"
    ],
    "🕌 مذهبی و معنوی": [
        "مسجد و مصلی (مسجد، مصلی)",
        "حسینیه و هیئت (حسینیه، هیئت)",
        "کلیسا و مراکز مسیحی (کلیسا، مراکز مسیحی)",
        "کنیسه و مراکز یهودی (کنیسه، مراکز یهودی)",
        "معابد و پرستشگاه‌ها (معبد، پرستشگاه)",
        "مراکز عرفانی و معنوی (عرفانی، معنوی)",
        "کتابفروشی‌های مذهبی (کتاب مذهبی، نرم افزار مذهبی)",
        "مراکز خیریه و نیکوکاری (خیریه، نیکوکاری)",
        "انتشارات مذهبی (انتشارات، چاپ مذهبی)",
        "مراکز حفظ قرآن و معارف اسلامی",
        "مراکز خدمات حج و زیارت",
        "مراکز مشاوره مذهبی و دینی",
        "مراکز آموزش احکام و معارف",
        "مراکز خدمات اوقاف و امور خیریه",
        "مراکز خدمات مذهبی سیار",
        "مراکز برگزاری مراسم مذهبی"
    ],
    "🌳 طبیعت و تفریح آزاد": [
        "پارک و بوستان (پارک عمومی، بوستان)",
        "باغ وحش و آکواریوم (باغ وحش، آکواریوم)",
        "باغ گیاه‌شناسی (گیاه‌شناسی، گلخانه)",
        "پیست دوچرخه‌سواری (دوچرخه‌سواری، دوچرخه سواری آفرود)",
        "کوهستان و مسیرهای طبیعت‌گردی (کوهنوردی، طبیعت‌گردی)",
        "ساحل و دریاچه (ساحل، دریاچه)",
        "آبشار و چشمه (آبشار، چشمه)",
        "جنگل و منطقه حفاظت شده (جنگل، منطقه حفاظت شده)",
        "کمپینگ و پیکنیک (کمپینگ، پیکنیک)",
        "مراکز اکوتوریسم (اکوتوریسم، گردشگری طبیعت)",
        "پیست اسکی و ورزش‌های زمستانی (اسکی، ورزش زمستانی)",
        "سالن‌های بولدرینگ و صخره‌نوردی (صخره‌نوردی، بولدرینگ)",
        "مراکز ماهیگیری و قایق‌رانی",
        "پارک‌های آبی و استخرهای روباز",
        "مراکز پرنده‌نگری و حیات وحش",
        "مسیرهای پیاده‌روی و کوهپیمایی",
        "مراکز چادرزنی و کاروانینگ",
        "پارک‌های ملی و مناطق گردشگری",
        "مراکز آموزش طبیعت‌گردی",
        "مراکز خدمات تورهای طبیعت"
    ],
    "💼 کسب‌وکار و حرفه‌ای": [
        "دفتر کار و شرکت‌ها (دفتر، شرکت)",
        "کارخانه‌ها و واحدهای تولیدی (کارخانه، تولیدی)",
        "کارگاه‌های صنعتی (کارگاه، صنعتی)",
        "دفاتر املاک و مشاورین املاک (املاک، مشاور املاک)",
        "دفاتر بیمه (بیمه، خدمات بیمه‌ای)",
        "شرکت‌های تبلیغاتی و بازاریابی (تبلیغات، بازاریابی)",
        "مراکز طراحی و چاپ (طراحی، چاپ)",
        "شرکت‌های معماری و عمران (معماری، عمران)",
        "دفاتر حقوقی و وکالت (حقوقی، وکالت)",
        "شرکت‌های مشاوره مدیریت (مشاوره، مدیریت)",
        "مراکز خدمات مالی و حسابداری (مالی، حسابداری)",
        "شرکت‌های فناوری اطلاعات (فناوری اطلاعات، نرم‌افزار)",
        "استودیوهای عکاسی و فیلمبرداری (عکاسی، فیلمبرداری)",
        "مراکز خدمات اداری و کپی (خدمات اداری، کپی)",
        "شرکت‌های حمل و نقل و باربری (حمل نقل، باربری)",
        "خدمات نظافتی و نگهداری (نظافتی، نگهداری)",
        "شرکت‌های رسانه‌ای و انتشاراتی",
        "مراکز تحقیقاتی و توسعه",
        "شرکت‌های مشاوره منابع انسانی",
        "مراکز خدمات مشاوره کسب‌وکار",
        "شرکت‌های طراحی سایت و بهینه‌سازی موتور جستجو",
        "مراکز خدمات ترجمه و مترجم",
        "شرکت‌های خدمات امنیتی",
        "مراکز خدمات پشتیبانی فناوری اطلاعات",
        "شرکت‌های خدمات مشاوره مالیاتی",
        "مراکز خدمات برندینگ و هویت سازی",
        "خدمات مشاوره انرژی و بهینه‌سازی"
    ],
    "🧰 خدمات تخصصی و فنی": [
        "تعمیرگاه لوازم خانگی (تعمیر لوازم، سرویس)",
        "تعمیرگاه موبایل و کامپیوتر (تعمیر موبایل، کامپیوتر)",
        "خدمات برق ساختمان (برق‌کاری، سیم‌کشی)",
        "خدمات لوله‌کشی و تاسیسات (لوله‌کشی، تاسیسات)",
        "خدمات گچ‌بری و رنگ‌کاری (گچ‌بری، رنگ‌کاری)",
        "خدمات کف‌پوش و کاشی‌کاری (کف‌پوش، کاشی‌کاری)",
        "خدمات نجاری و کابینت‌سازی (نجاری، کابینت‌سازی)",
        "خدمات آهنگری و جوشکاری (آهنگری، جوشکاری)",
        "خدمات کلیدسازی و قفل‌سازی (کلیدسازی، قفل‌سازی)",
        "خدمات شیشه‌بری و آینه‌کاری (شیشه‌بری، آینه‌کاری)",
        "خدمات فرش شویی و مبل شویی (فرش‌شویی، مبل‌شویی)",
        "خدمات نظافت منزل و اداره (نظافت، خدمات نظافتی)",
        "خدمات باغبانی و فضای سبز (باغبانی، فضای سبز)",
        "خدمات حشره‌کشی و ضدعفونی (ضدعفونی، سمپاشی)",
        "خدمات امنیتی و نگهبانی (امنیتی، نگهبانی)",
        "خدمات تعمیرات لوازم الکترونیکی",
        "خدمات نصب و راه‌اندازی تجهیزات",
        "خدمات سیم‌کشی شبکه و اینترنت",
        "خدمات تعمیرات صنعتی و ماشین‌آلات",
        "خدمات نصب دوربین و سیستم‌های حفاظتی",
        "خدمات تعمیرات لوازم آشپزخانه",
        "خدمات نصب کفپوش و سقف کاذب",
        "خدمات تعمیرات ابزارآلات دقیق",
        "خدمات نصب آسانسور و پله برقی",
        "خدمات تعمیرات سیستم‌های سرمایشی و گرمایشی",
        "خدمات نصب سیستم‌های اعلام حریق",
        "خدمات تعمیرات ادوات موسیقی",
        "خدمات نصب دیش و سیستم‌های ماهواره‌ای",
        "خدمات تعمیرات لوازم پزشکی",
        "خدمات نصب سیستم‌های هوشمند ساختمان",
        "خدمات بازیافت و محیط زیست",
        "خدمات اجاره تجهیزات و لوازم (مانند اجاره چادر، لباس مراسم، تجهیزات فنی)"
    ]
}

# مسیر پوشه آپلود
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# HTML template for custom alert dialog
CUSTOM_ALERT_HTML = """<div id="customAlert" style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.2); width: 300px; overflow: hidden; z-index: 1000; display: none;"><div style="background: #006769; color: white; padding: 15px; text-align: center; font-size: 18px;">{title}</div><div style="padding: 20px; text-align: center; font-size: 16px;">{message}</div><div style="padding: 10px; display: flex; justify-content: center;"><button onclick="hideCustomAlert()" style="background: #40A578; color: white; border: none; padding: 10px 20px; border-radius: 10px; cursor: pointer;">تایید</button></div></div>"""

# HTML template for registration page (updated with custom alert)
REGISTRATION_HTML = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ثبت نام در گویم نما</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;700&display=swap');
        :root {
            --primary: #006769;
            --secondary: #40A578;
            --success: #4caf50;
            --error: #f44336;
            --background: #f8f9fa;
            --text: #333;
            --light: #fff;
            --shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Vazirmatn', sans-serif;
        }
        body {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background-color: var(--light);
            border-radius: 20px;
            box-shadow: var(--shadow);
            width: 100%;
            max-width: 500px;
            overflow: hidden;
            animation: fadeIn 0.5s ease-out;
        }
        .header {
            background: linear-gradient(to right, var(--primary), var(--secondary));
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            font-size: 28px;
            margin-bottom: 10px;
        }
        .form-container {
            padding: 30px;
        }
        .form-group {
            margin-bottom: 20px;
            position: relative;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: var(--text);
        }
        .form-control {
            width: 100%;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s, box-shadow 0.3s;
        }
        .form-control:focus {
            border-color: var(--primary);
            box-shadow: 0 0 0 2px rgba(0, 103, 105, 0.2);
            outline: none;
        }
        .form-control.error {
            border-color: var(--error);
        }
        .error-message {
            color: var(--error);
            font-size: 12px;
            margin-top: 5px;
            display: none;
        }
        .show-password {
            position: absolute;
            left: 15px;
            top: 40px;
            cursor: pointer;
            color: #777;
        }
        .btn {
            background: linear-gradient(to right, var(--primary), var(--secondary));
            color: white;
            border: none;
            padding: 15px;
            border-radius: 10px;
            width: 100%;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        .btn:active {
            transform: translateY(0);
        }
        .register-link {
            text-align: center;
            margin-top: 20px;
            font-size: 14px;
        }
        .register-link a {
            color: var(--primary);
            text-decoration: none;
            font-weight: 500;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        /* Success Checkmark Animation */
        .success-checkmark {
            width: 100px;
            height: 100px;
            margin: 0 auto 20px;
            position: relative;
        }
        .checkmark-circle {
            stroke-dasharray: 166;
            stroke-dashoffset: 166;
            stroke-width: 2;
            stroke-miterlimit: 10;
            stroke: #4CAF50; /* رنگ سبز برای دایره */
            fill: none; /* دایره توپر نباشد */
            animation: stroke 0.6s cubic-bezier(0.65, 0, 0.45, 1) forwards;
        }
        .checkmark {
            width: 100px;
            height: 100px;
            border-radius: 50%;
            display: block;
            stroke-width: 2;
            stroke: #4CAF50; /* رنگ سبز برای تیک */
            stroke-miterlimit: 10;
            margin: 0 auto;
            box-shadow: inset 0px 0px 0px #4CAF50; /* حذف سایه داخلی */
            animation: fill .4s ease-in-out .4s forwards, scale .3s ease-in-out .9s both;
        }
        .checkmark-check {
            transform-origin: 50% 50%;
            stroke-dasharray: 48;
            stroke-dashoffset: 48;
            animation: stroke 0.3s cubic-bezier(0.65, 0, 0.45, 1) 0.8s forwards;
        }
        @keyframes stroke {
            100% {
                stroke-dashoffset: 0;
            }
        }
        @keyframes scale {
            0%, 100% {
                transform: none;
            }
            50% {
                transform: scale3d(1.1, 1.1, 1);
            }
        }
        @keyframes fill {
            100% {
                box-shadow: inset 0px 0px 0px 30px #4CAF50; /* حذف پر شدن دایره */
            }
        }
        @media (max-width: 576px) {
            .container {
                border-radius: 10px;
            }
            .header {
                padding: 20px;
            }
            .form-container {
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>ثبت نام در گویم نما</h1>
            <p>حساب کاربری خود را ایجاد کنید</p>
        </div>
        <div class="form-container">
            <form id="registrationForm">
                <div class="form-group">
                    <label for="fullname">نام کاربری</label>
                    <input type="text" id="fullname" class="form-control" placeholder="نام کاربری خود را وارد کنید">
                    <div class="error-message" id="fullname-error">لطفاً نام کاربری معتبر وارد کنید (نباید تکراری باشد)</div>
                </div>
                <div class="form-group">
                    <label for="city">شهر</label>
                    <select id="city" class="form-control">
                        <option value="">لطفاً شهر خود را انتخاب کنید</option>
                        {% for city in cities %}
                        <option value="{{ city }}">{{ city }}</option>
                        {% endfor %}
                    </select>
                    <div class="error-message" id="city-error">لطفاً شهر خود را انتخاب کنید</div>
                </div>
                <div class="form-group">
                    <label for="phone">تلفن همراه</label>
                    <input type="tel" id="phone" class="form-control" placeholder="09xxxxxxxxx">
                    <div class="error-message" id="phone-error">لطفاً شماره تلفن معتبر وارد کنید</div>
                </div>
                <div class="form-group">
                    <label for="password">رمز عبور</label>
                    <input type="password" id="password" class="form-control" placeholder="رمز عبور قوی انتخاب کنید">
                    <span class="show-password" id="togglePassword">نمایش</span>
                    <div class="error-message" id="password-error">رمز عبور باید حداقل ۶ کاراکتر داشته باشد</div>
                </div>
                <div class="form-group">
                    <label for="confirmPassword">تکرار رمز عبور</label>
                    <input type="password" id="confirmPassword" class="form-control" placeholder="رمز عبور را تکرار کنید">
                    <div class="error-message" id="confirmPassword-error">رمزهای عبور مطابقت ندارند</div>
                </div>
                <button type="submit" class="btn">ثبت نام</button>
                <div class="register-link">
                    قبلاً حساب دارید؟ <a href="/login">وارد شوید</a>
                </div>
            </form>
        </div>
    </div>
""" + CUSTOM_ALERT_HTML + """
    <script>
        function showCustomAlert(title, message) {
            const alert = document.getElementById('customAlert');
            alert.querySelector('div[style*="background: #006769"]').textContent = title;
            alert.querySelector('div[style*="padding: 20px"]').textContent = message;
            alert.style.display = 'block';
        }
        function hideCustomAlert() {
            document.getElementById('customAlert').style.display = 'none';
        }
        document.addEventListener('DOMContentLoaded', function() {
            const form = document.getElementById('registrationForm');
            const togglePassword = document.getElementById('togglePassword');
            const passwordInput = document.getElementById('password');
            const confirmPasswordInput = document.getElementById('confirmPassword');
            
            // نمایش/مخفی کردن رمز عبور
            togglePassword.addEventListener('click', function() {
                if (passwordInput.type === 'password') {
                    passwordInput.type = 'text';
                    confirmPasswordInput.type = 'text';
                    togglePassword.textContent = 'پنهان';
                } else {
                    passwordInput.type = 'password';
                    confirmPasswordInput.type = 'password';
                    togglePassword.textContent = 'نمایش';
                }
            });
            
            // اعتبارسنجی فرم
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                let isValid = true;
                
                // اعتبارسنجی نام کاربری
                const fullname = document.getElementById('fullname');
                const fullnameError = document.getElementById('fullname-error');
                const usernamePattern = /^[a-zA-Zآ-ی][a-zA-Z0-9آ-ی_]{2,}$/;
                if (!usernamePattern.test(fullname.value)) {
                    fullname.classList.add('error');
                    fullnameError.textContent = 'نام کاربری باید با حرف شروع شود و حداقل ۳ کاراکتر داشته باشد';
                    fullnameError.style.display = 'block';
                    isValid = false;
                } else {
                    fullname.classList.remove('error');
                    fullnameError.style.display = 'none';
                }
                
                // اعتبارسنجی شهر
                const city = document.getElementById('city');
                const cityError = document.getElementById('city-error');
                if (city.value === '') {
                    city.classList.add('error');
                    cityError.style.display = 'block';
                    isValid = false;
                } else {
                    city.classList.remove('error');
                    cityError.style.display = 'none';
                }
                
                // اعتبارسنجی تلفن
                const phone = document.getElementById('phone');
                const phoneError = document.getElementById('phone-error');
                const phonePattern = /^09\\d{9}$/;
                if (!phonePattern.test(phone.value)) {
                    phone.classList.add('error');
                    phoneError.style.display = 'block';
                    isValid = false;
                } else {
                    phone.classList.remove('error');
                    phoneError.style.display = 'none';
                }
                
                // اعتبارسنجی رمز عبور
                const password = document.getElementById('password');
                const passwordError = document.getElementById('password-error');
                if (password.value.length < 6) {
                    password.classList.add('error');
                    passwordError.style.display = 'block';
                    isValid = false;
                } else {
                    password.classList.remove('error');
                    passwordError.style.display = 'none';
                }
                
                // اعتبارسنجی تکرار رمز عبور
                const confirmPassword = document.getElementById('confirmPassword');
                const confirmPasswordError = document.getElementById('confirmPassword-error');
                if (confirmPassword.value !== password.value) {
                    confirmPassword.classList.add('error');
                    confirmPasswordError.style.display = 'block';
                    isValid = false;
                } else {
                    confirmPassword.classList.remove('error');
                    confirmPasswordError.style.display = 'none';
                }
                
                // اگر فرم معتبر است، ارسال شود
                if (isValid) {
                    // ایجاد شیء داده‌ها
                    const formData = {
                        username: fullname.value,
                        city: city.value,
                        phone: phone.value,
                        password: password.value,
                        timestamp: new Date().toISOString()
                    };
                    
                    // ارسال درخواست به سرور
                    fetch('/register', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(formData)
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            // نمایش انیمیشن موفقیت
                            document.querySelector('.form-container').innerHTML = `
                                <div class="success-checkmark">
                                    <svg class="checkmark" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 52 52">
                                        <circle class="checkmark-circle" cx="26" cy="26" r="25" fill="none"/>
                                        <path class="checkmark-check" fill="none" d="M14.1 27.2l7.1 7.2 16.7-16.8"/>
                                    </svg>
                                </div>
                                <h2 style="text-align: center; color: #4caf50;">ثبت نام با موفقیت انجام شد!</h2>
                                <p style="text-align: center; margin-top: 20px;">در حال انتقال به صفحه اصلی...</p>
                            `;
                            
                            // انتقال به صفحه اصلی پس از 3 ثانیه
                            setTimeout(() => {
                                window.location.href = '/main?username=' + encodeURIComponent(data.user.username);
                            }, 3000);
                        } else {
                            if (data.message.includes('تکراری')) {
                                fullname.classList.add('error');
                                fullnameError.textContent = data.message;
                                fullnameError.style.display = 'block';
                            } else {
                                showCustomAlert('خطا', 'خطا در ثبت نام: ' + data.message);
                            }
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        showCustomAlert('خطا', 'خطا در ارسال اطلاعات');
                    });
                }
            });
            
            // اعتبارسنجی در حین تایپ
            const inputs = form.querySelectorAll('input');
            inputs.forEach(input => {
                input.addEventListener('input', function() {
                    this.classList.remove('error');
                    const errorElement = document.getElementById(this.id + '-error');
                    if (errorElement) {
                        errorElement.style.display = 'none';
                    }
                });
            });
        });
    </script>
</body>
</html>
"""

# HTML template for login page (updated with custom alert)
LOGIN_HTML = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ورود به گویم نما</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;700&display=swap');
        :root {
            --primary: #006769;
            --secondary: #40A578;
            --success: #4caf50;
            --error: #f44336;
            --background: #f8f9fa;
            --text: #333;
            --light: #fff;
            --shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Vazirmatn', sans-serif;
        }
        body {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background-color: var(--light);
            border-radius: 20px;
            box-shadow: var(--shadow);
            width: 100%;
            max-width: 500px;
            overflow: hidden;
            animation: fadeIn 0.5s ease-out;
        }
        .header {
            background: linear-gradient(to right, var(--primary), var(--secondary));
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            font-size: 28px;
            margin-bottom: 10px;
        }
        .form-container {
            padding: 30px;
        }
        .form-group {
            margin-bottom: 20px;
            position: relative;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: var(--text);
        }
        .form-control {
            width: 100%;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s, box-shadow 0.3s;
        }
        .form-control:focus {
            border-color: var(--primary);
            box-shadow: 0 0 0 2px rgba(0, 103, 105, 0.2);
            outline: none;
        }
        .form-control.error {
            border-color: var(--error);
        }
        .error-message {
            color: var(--error);
            font-size: 12px;
            margin-top: 5px;
            display: none;
        }
        .show-password {
            position: absolute;
            left: 15px;
            top: 40px;
            cursor: pointer;
            color: #777;
        }
        .btn {
            background: linear-gradient(to right, var(--primary), var(--secondary));
            color: white;
            border: none;
            padding: 15px;
            border-radius: 10px;
            width: 100%;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        .btn:active {
            transform: translateY(0);
        }
        .register-link {
            text-align: center;
            margin-top: 20px;
            font-size: 14px;
        }
        .register-link a {
            color: var(--primary);
            text-decoration: none;
            font-weight: 500;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        /* Success Checkmark Animation */
        .success-checkmark {
            width: 100px;
            height: 100px;
            margin: 0 auto 20px;
            position: relative;
        }
        .checkmark-circle {
            stroke-dasharray: 166;
            stroke-dashoffset: 166;
            stroke-width: 2;
            stroke-miterlimit: 10;
            stroke: #4CAF50; /* رنگ سبز برای دایره */
            fill: none; /* دایره توپر نباشد */
            animation: stroke 0.6s cubic-bezier(0.65, 0, 0.45, 1) forwards;
        }
        .checkmark {
            width: 100px;
            height: 100px;
            border-radius: 50%;
            display: block;
            stroke-width: 2;
            stroke: #4CAF50; /* رنگ سبز برای تیک */
            stroke-miterlimit: 10;
            margin: 0 auto;
            box-shadow: inset 0px 0px 0px #4CAF50; /* حذف سایه داخلی */
            animation: fill .4s ease-in-out .4s forwards, scale .3s ease-in-out .9s both;
        }
        .checkmark-check {
            transform-origin: 50% 50%;
            stroke-dasharray: 48;
            stroke-dashoffset: 48;
            animation: stroke 0.3s cubic-bezier(0.65, 0, 0.45, 1) 0.8s forwards;
        }
        @keyframes stroke {
            100% {
                stroke-dashoffset: 0;
            }
        }
        @keyframes scale {
            0%, 100% {
                transform: none;
            }
            50% {
                transform: scale3d(1.1, 1.1, 1);
            }
        }
        @keyframes fill {
            100% {
                box-shadow: inset 0px 0px 0px 30px #4CAF50; /* حذف پر شدن دایره */
            }
        }
        @media (max-width: 576px) {
            .container {
                border-radius: 10px;
            }
            .header {
                padding: 20px;
            }
            .form-container {
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>ورود به گویم نما</h1>
            <p>برای دسترسی به حساب خود وارد شوید</p>
        </div>
        <div class="form-container">
            <form id="loginForm">
                <div class="form-group">
                    <label for="username">نام کاربری یا شماره تلفن</label>
                    <input type="text" id="username" class="form-control" placeholder="نام کاربری یا شماره تلفن خود را وارد کنید">
                    <div class="error-message" id="username-error">لطفاً نام کاربری یا شماره تلفن معتبر وارد کنید</div>
                </div>
                <div class="form-group">
                    <label for="password">رمز عبور</label>
                    <input type="password" id="password" class="form-control" placeholder="رمز عبور خود را وارد کنید">
                    <span class="show-password" id="togglePassword">نمایش</span>
                    <div class="error-message" id="password-error">لطفاً رمز عبور خود را وارد کنید</div>
                </div>
                <button type="submit" class="btn">ورود</button>
                <div class="register-link">
                    حساب ندارید؟ <a href="/">ثبت نام کنید</a>
                </div>
            </form>
        </div>
    </div>
""" + CUSTOM_ALERT_HTML + """
    <script>
        function showCustomAlert(title, message) {
            const alert = document.getElementById('customAlert');
            alert.querySelector('div[style*="background: #006769"]').textContent = title;
            alert.querySelector('div[style*="padding: 20px"]').textContent = message;
            alert.style.display = 'block';
        }
        function hideCustomAlert() {
            document.getElementById('customAlert').style.display = 'none';
        }
        document.addEventListener('DOMContentLoaded', function() {
            const form = document.getElementById('loginForm');
            const togglePassword = document.getElementById('togglePassword');
            const passwordInput = document.getElementById('password');
            
            // نمایش/مخفی کردن رمز عبور
            togglePassword.addEventListener('click', function() {
                if (passwordInput.type === 'password') {
                    passwordInput.type = 'text';
                    togglePassword.textContent = 'پنهان';
                } else {
                    passwordInput.type = 'password';
                    togglePassword.textContent = 'نمایش';
                }
            });
            
            // اعتبارسنجی فرم
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                let isValid = true;
                
                // اعتبارسنجی نام کاربری/تلفن
                const username = document.getElementById('username');
                const usernameError = document.getElementById('username-error');
                if (username.value.trim() === '') {
                    username.classList.add('error');
                    usernameError.style.display = 'block';
                    isValid = false;
                } else {
                    username.classList.remove('error');
                    usernameError.style.display = 'none';
                }
                
                // اعتبارسنجی رمز عبور
                const password = document.getElementById('password');
                const passwordError = document.getElementById('password-error');
                if (password.value.trim() === '') {
                    password.classList.add('error');
                    passwordError.style.display = 'block';
                    isValid = false;
                } else {
                    password.classList.remove('error');
                    passwordError.style.display = 'none';
                }
                
                // اگر فرم معتبر است، ارسال شود
                if (isValid) {
                    // ایجاد شیء داده‌ها
                    const formData = {
                        username: username.value,
                        password: password.value
                    };
                    
                    // ارسال درخواست به سرور
                    fetch('/login', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(formData)
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            // نمایش انیمیشن موفقیت
                            document.querySelector('.form-container').innerHTML = `
                                <div class="success-checkmark">
                                    <svg class="checkmark" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 52 52">
                                        <circle class="checkmark-circle" cx="26" cy="26" r="25" fill="none"/>
                                        <path class="checkmark-check" fill="none" d="M14.1 27.2l7.1 7.2 16.7-16.8"/>
                                    </svg>
                                </div>
                                <h2 style="text-align: center; color: #4caf50;">ورود موفقیت آمیز!</h2>
                                <p style="text-align: center; margin-top: 20px;">در حال انتقال به صفحه اصلی...</p>
                            `;
                            
                            // انتقال به صفحه اصلی پس از 2 ثانیه
                            setTimeout(() => {
                                window.location.href = '/main?username=' + encodeURIComponent(data.user.username);
                            }, 2000);
                        } else {
                            showCustomAlert('خطا', data.message);
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        showCustomAlert('خطا', 'خطا در ورود');
                    });
                }
            });
            
            // اعتبارسنجی در حین تایپ
            const inputs = form.querySelectorAll('input');
            inputs.forEach(input => {
                input.addEventListener('input', function() {
                    this.classList.remove('error');
                    const errorElement = document.getElementById(this.id + '-error');
                    if (errorElement) {
                        errorElement.style.display = 'none';
                    }
                });
            });
        });
    </script>
</body>
</html>
"""

# HTML template for main page (expanded with all new features)
MAIN_HTML = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>گویم نما</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;700&display=swap');
        :root {
            --primary: #006769;
            --secondary: #40A578;
            --light: #fff;
            --text: #333;
            --gray: #f0f0f0;
            --shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            --border: #006769;
        }
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Vazirmatn', sans-serif;
        }
        body {
            background-color: #f8f9fa;
            color: var(--text);
            padding-bottom: 70px;
        }
        .header {
            background-color: var(--primary);
            color: white;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 100;
        }
        .logo {
            font-weight: bold;
            font-size: 18px;
        }
        .header-icons {
            display: flex;
            gap: 15px;
        }
        .header-icon {
            cursor: pointer;
            font-size: 20px;
        }
        .notification-badge {
            background-color: red;
            color: white;
            border-radius: 50%;
            padding: 2px 6px;
            font-size: 12px;
            position: absolute;
            top: -5px;
            right: -5px;
        }
        .main-content {
            padding: 20px;
        }
        .welcome-section {
            text-align: center;
            margin-bottom: 20px;
        }
        .welcome-section h2 {
            color: var(--primary);
        }
        .content-section {
            display: none;
        }
        .content-section.active {
            display: block;
            animation: fadeIn 0.5s;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        .nav-tabs {
            display: flex;
            background-color: var(--light);
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 20px;
            box-shadow: var(--shadow);
        }
        .nav-tab {
            flex: 1;
            text-align: center;
            padding: 15px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .nav-tab.active {
            background-color: var(--primary);
            color: white;
        }
        .nav-tab:hover:not(.active) {
            background-color: #e0e0e0;
        }
        .locations-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 15px;
        }
        .location-tile {
            background-color: var(--light);
            border-radius: 10px;
            overflow: hidden;
            box-shadow: var(--shadow);
            cursor: pointer;
            transition: transform 0.2s;
        }
        .location-tile:hover {
            transform: scale(1.02);
        }
        .location-image {
            height: 100px;
            background-size: cover;
            background-position: center;
        }
        .location-info {
            padding: 10px;
            font-size: 14px;
        }
        .location-title {
            font-weight: 500;
            margin-bottom: 5px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .location-city {
            color: #666;
            font-size: 12px;
        }
        .back-arrow {
            font-size: 24px;
            cursor: pointer;
            margin-bottom: 20px;
            display: inline-block;
        }
        .location-details {
            background-color: var(--light);
            border-radius: 10px;
            padding: 20px;
            box-shadow: var(--shadow);
        }
        .slider-container {
            position: relative;
            margin-bottom: 20px;
        }
        .slider-images {
            display: flex;
            overflow-x: auto;
            scroll-snap-type: x mandatory;
            scrollbar-width: none; /* Firefox */
        }
        .slider-images::-webkit-scrollbar {
            display: none; /* Chrome, Safari, Opera*/
        }
        .slider-image {
            flex: 0 0 100%;
            scroll-snap-align: start;
        }
        .slider-image img {
            width: 100%;
            height: 200px;
            object-fit: cover;
            border-radius: 10px;
        }
        .slider-counter {
            position: absolute;
            bottom: 10px;
            right: 10px;
            background-color: rgba(0, 0, 0, 0.5);
            color: white;
            padding: 5px 10px;
            border-radius: 10px;
            font-size: 14px;
        }
        .detail-item {
            margin-bottom: 15px;
        }
        .detail-label {
            font-weight: 500;
            color: var(--primary);
            margin-bottom: 5px;
        }
        .detail-value {
            font-size: 16px;
        }
        .location-actions {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        .action-btn {
            flex: 1;
            padding: 10px;
            border: none;
            border-radius: 5px;
            background-color: var(--primary);
            color: white;
            cursor: pointer;
            text-align: center;
            transition: background-color 0.3s;
        }
        .action-btn:hover {
            background-color: #005052;
        }
        .comments-section {
            margin-top: 30px;
        }
        .comments-section h3 {
            margin-bottom: 15px;
            color: var(--primary);
        }
        .comment-form {
            margin-bottom: 20px;
        }
        .comment-textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            resize: vertical;
            margin-bottom: 10px;
        }
        .star-rating {
            display: flex;
            justify-content: center;
            margin-bottom: 10px;
        }
        .star {
            font-size: 24px;
            color: #ddd;
            cursor: pointer;
            transition: color 0.2s;
        }
        .star.filled {
            color: #ffc107;
        }
        .comments-list {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        .comment-item {
            background-color: var(--gray);
            padding: 15px;
            border-radius: 10px;
        }
        .comment-user {
            font-weight: 500;
            margin-bottom: 5px;
        }
        .comment-stars {
            color: #ffc107;
            margin-bottom: 5px;
        }
        .comment-text {
            font-size: 14px;
        }
        .profile-section {
            background-color: var(--light);
            border-radius: 10px;
            padding: 20px;
            box-shadow: var(--shadow);
        }
        .profile-item {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }
        .profile-item:last-child {
            border-bottom: none;
        }
        .profile-label {
            font-weight: 500;
        }
        .profile-value {
            color: #666;
        }
        .edit-form {
            display: none;
            margin-top: 15px;
        }
        .edit-form.active {
            display: block;
        }
        .form-control {
            width: 100%;
            padding: 10px;
            margin-bottom: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        .form-actions {
            display: flex;
            justify-content: flex-end;
            gap: 10px;
        }
        .btn {
            padding: 8px 15px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .btn-primary {
            background-color: var(--primary);
            color: white;
        }
        .btn-secondary {
            background-color: #6c757d;
            color: white;
        }
        .action-button {
            width: 100%;
            padding: 12px;
            margin-bottom: 10px;
            border: none;
            border-radius: 5px;
            background-color: var(--primary);
            color: white;
            cursor: pointer;
            text-align: center;
            font-size: 16px;
        }
        .action-button:hover {
            background-color: #005052;
        }
        .logout-btn {
            background-color: #dc3545;
        }
        .logout-btn:hover {
            background-color: #bd2130;
        }
        .add-container {
            background-color: var(--light);
            border-radius: 10px;
            padding: 20px;
            box-shadow: var(--shadow);
        }
        .add-step {
            display: none;
        }
        .add-step.active {
            display: block;
            animation: slideIn 0.5s;
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(50px); }
            to { opacity: 1; transform: translateX(0); }
        }
        .photo-upload {
            background: var(--gray);
            border: 2px dashed var(--border);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            cursor: pointer;
            margin-bottom: 20px;
        }
        .photo-upload:hover {
            background: #e0e0e0;
        }
        .photo-preview {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        .photo-item {
            position: relative;
            width: 100px;
            height: 100px;
            border-radius: 10px;
            overflow: hidden;
        }
        .photo-item img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        .delete-photo {
            position: absolute;
            top: 5px;
            left: 5px;
            background-color: rgba(255, 0, 0, 0.7);
            color: white;
            border: none;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            cursor: pointer;
            font-size: 12px;
        }
        .set-main-photo {
            position: absolute;
            bottom: 5px;
            left: 5px;
            background-color: rgba(0, 128, 0, 0.7);
            color: white;
            border: none;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            cursor: pointer;
            font-size: 12px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: 500;
        }
        .form-control {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        .nav-buttons {
            display: flex;
            justify-content: space-between;
            margin-top: 20px;
        }
        .step-btn {
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            background-color: var(--primary);
            color: white;
            cursor: pointer;
        }
        .step-btn:disabled {
            background-color: #ccc;
            cursor: not-allowed;
        }
        .notifications-section {
            background-color: var(--light);
            border-radius: 10px;
            padding: 20px;
            box-shadow: var(--shadow);
        }
        .notifications-list {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        .notification-tile {
            background-color: var(--gray);
            padding: 15px;
            border-radius: 10px;
            cursor: pointer;
        }
        .notification-title {
            font-weight: 500;
            margin-bottom: 5px;
        }
        .notification-text {
            font-size: 14px;
            color: #666;
        }
        .chat-list, .chat-messages {
            background-color: var(--light);
            border-radius: 10px;
            padding: 20px;
            box-shadow: var(--shadow);
            margin-bottom: 20px;
            height: 70vh;
            overflow-y: auto;
        }
        .chat-item, .message {
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 5px;
            cursor: pointer;
        }
        .chat-item:hover, .message:hover {
            background-color: #f0f0f0;
        }
        .chat-input {
            display: flex;
            gap: 10px;
        }
        .chat-input input {
            flex: 1;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        .chat-send-btn {
            background-color: var(--primary);
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 5px;
            cursor: pointer;
        }
        .chat-send-btn:hover {
            background-color: #005052;
        }
        .message.sent {
            background-color: #e3f2fd;
            text-align: left;
        }
        .message.received {
            background-color: #f5f5f5;
            text-align: right;
        }
        .bottom-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background-color: var(--light);
            display: flex;
            justify-content: space-around;
            padding: 10px 0;
            box-shadow: 0 -2px 5px rgba(0, 0, 0, 0.1);
            z-index: 100;
        }
        .nav-item {
            text-align: center;
            cursor: pointer;
            flex: 1;
        }
        .nav-item.active {
            color: var(--primary);
        }
        .nav-icon {
            font-size: 20px;
            margin-bottom: 5px;
        }
        .nav-text {
            font-size: 12px;
        }
        @media (max-width: 768px) {
            .locations-list {
                grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
            }
            .location-image {
                height: 80px;
            }
            .location-info {
                padding: 8px;
                font-size: 12px;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">GOYOM NAMA</div>
        <div class="header-icons">
            <div class="header-icon" onclick="showSection('searchSection', null)">🔍</div>
            <div class="header-icon" id="notificationIcon" onclick="showNotifications()">🔔
                {% if notifications_count > 0 %}
                <span class="notification-badge">{{ notifications_count }}</span>
                {% endif %}
            </div>
        </div>
    </div>
    <div class="main-content">
        <div class="welcome-section">
            <h2>خوش آمدید، {{ username }}!</h2>
        </div>
        <div class="nav-tabs">
            <div class="nav-tab active" onclick="switchTab('homeTab', this)">خانه</div>
            <div class="nav-tab" onclick="switchTab('profileTab', this)">پروفایل</div>
            <div class="nav-tab" onclick="switchTab('addTab', this)">اضافه کردن</div>
            <div class="nav-tab" onclick="switchTab('chatTab', this)">چت</div>
        </div>
        <div id="homeTab" class="content-section active">
            <div class="locations-list">
                {% for loc in all_locations %}
                <div class="location-tile" onclick="showLocationDetails('{{ loc.id }}')">
                    <div class="location-image" style="background-image: url('/uploads/{{ loc.photos[0] }}');"></div>
                    <div class="location-info">
                        <div class="location-title">{{ loc.title }}</div>
                        <div class="location-city">{{ loc.city }}</div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        <div id="locationDetailsSection" class="content-section">
            <span class="back-arrow" onclick="showSection('homeTab', document.querySelector('.nav-tab[onclick*=\"homeTab\"]'))">⬅️</span>
            <div class="location-details">
                <div class="slider-container">
                    <div class="slider-images" id="sliderImages">
                        <!-- Images will be loaded here by JS -->
                    </div>
                    <div class="slider-counter" id="sliderCounter">1 / 1</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">عنوان</div>
                    <div class="detail-value" id="locTitle"></div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">توضیحات</div>
                    <div class="detail-value" id="locDesc"></div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">شهرک</div>
                    <div class="detail-value" id="locCity"></div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">آدرس</div>
                    <div class="detail-value" id="locAddress"></div>
                </div>
                <div class="detail-item" id="locPhoneField" style="display: none;">
                    <div class="detail-label">شماره تماس</div>
                    <div class="detail-value" id="locPhone"></div>
                </div>
                <div class="detail-item" id="locShiftsField" style="display: none;">
                    <div class="detail-label">شیفت‌ها</div>
                    <div class="detail-value" id="locShifts"></div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">دسته</div>
                    <div class="detail-value" id="locCategory"></div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">زیر دسته</div>
                    <div class="detail-value" id="locSubcategory"></div>
                </div>
                <div class="location-actions" id="locActions">
                    <!-- Actions will be loaded here by JS -->
                </div>
            </div>
            <div class="comments-section">
                <h3>نظرات</h3>
                <div class="comment-form">
                    <textarea class="comment-textarea" id="commentText" placeholder="نظر خود را بنویسید..."></textarea>
                    <div class="star-rating">
                        <span class="star" onclick="setRating(1)">★</span>
                        <span class="star" onclick="setRating(2)">★</span>
                        <span class="star" onclick="setRating(3)">★</span>
                        <span class="star" onclick="setRating(4)">★</span>
                        <span class="star" onclick="setRating(5)">★</span>
                    </div>
                    <button class="action-btn" onclick="submitComment()">ارسال نظر</button>
                </div>
                <div class="comments-list" id="commentsList">
                    <!-- Comments will be loaded here by JS -->
                </div>
            </div>
        </div>
        <div id="profileTab" class="content-section">
            <div class="profile-section">
                <div class="profile-item">
                    <div class="profile-label">نام کاربری</div>
                    <div class="profile-value" id="profileUsername">{{ username }}</div>
                </div>
                <div class="profile-item">
                    <div class="profile-label">شماره تلفن</div>
                    <div class="profile-value" id="profilePhone">{{ phone }}</div>
                </div>
                <div class="profile-item">
                    <div class="profile-label">شهر</div>
                    <div class="profile-value" id="profileCity">{{ city }}</div>
                </div>
                <div class="profile-item">
                    <div class="profile-label">رمز عبور</div>
                    <div class="profile-value">******</div>
                </div>
                <button class="action-button" onclick="toggleEditForm('usernameForm')">تغییر نام کاربری</button>
                <div class="edit-form" id="usernameForm">
                    <input type="text" class="form-control" id="newUsername" placeholder="نام کاربری جدید">
                    <div class="form-actions">
                        <button class="btn btn-secondary" onclick="toggleEditForm('usernameForm')">لغو</button>
                        <button class="btn btn-primary" onclick="updateUsername()">ذخیره</button>
                    </div>
                </div>
                <button class="action-button" onclick="toggleEditForm('phoneForm')">تغییر شماره تلفن</button>
                <div class="edit-form" id="phoneForm">
                    <input type="text" class="form-control" id="newPhone" placeholder="شماره تلفن جدید">
                    <div class="form-actions">
                        <button class="btn btn-secondary" onclick="toggleEditForm('phoneForm')">لغو</button>
                        <button class="btn btn-primary" onclick="updatePhone()">ذخیره</button>
                    </div>
                </div>
                <button class="action-button" onclick="toggleEditForm('cityForm')">تغییر شهر</button>
                <div class="edit-form" id="cityForm">
                    <select class="form-control" id="newCity">
                        {% for c in cities %}
                        <option value="{{ c }}" {% if c == city %}selected{% endif %}>{{ c }}</option>
                        {% endfor %}
                    </select>
                    <div class="form-actions">
                        <button class="btn btn-secondary" onclick="toggleEditForm('cityForm')">لغو</button>
                        <button class="btn btn-primary" onclick="updateCity()">ذخیره</button>
                    </div>
                </div>
                <button class="action-button" onclick="showMyLocations()">مکان های من</button>
                <button class="action-button logout-btn" onclick="showLogoutConfirm()">خروج از حساب</button>
            </div>
        </div>
        <div id="myLocationsSection" class="content-section">
            <span class="back-arrow" onclick="showSection('profileTab', document.querySelector('.nav-tab[onclick*=\"profileTab\"]'))">⬅️</span>
            <h3>مکان های من</h3>
            <div class="locations-list">
                {% for loc in my_locations %}
                <div class="location-tile" onclick="showLocationDetails('{{ loc.id }}', true)">
                    <div class="location-image" style="background-image: url('/uploads/{{ loc.photos[0] }}');"></div>
                    <div class="location-info">
                        <div class="location-title">{{ loc.title }}</div>
                        <div class="location-city">{{ loc.city }}</div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        <div id="addTab" class="content-section">
            <div class="add-container">
                <div id="addStep1" class="add-step active">
                    <div class="photo-upload" onclick="document.getElementById('photoInput').click()">
                        <span style="font-size: 50px;">+</span>
                        <p>اضافه کردن عکس</p>
                    </div>
                    <input type="file" id="photoInput" multiple accept="image/*" style="display: none;" onchange="previewPhotos()">
                    <div class="photo-preview" id="photoPreview"></div>
                    <div class="form-group">
                        <label for="locTitleInput">عنوان مکان *</label>
                        <input type="text" id="locTitleInput" class="form-control" placeholder="عنوان را وارد کنید">
                    </div>
                    <div class="form-group">
                        <label for="locDescInput">توضیحات</label>
                        <textarea id="locDescInput" class="form-control" placeholder="توضیحات را وارد کنید"></textarea>
                    </div>
                    <div class="form-group">
                        <label for="categorySelect">دسته *</label>
                        <select id="categorySelect" class="form-control" onchange="loadSubcategories()">
                            <option value="">انتخاب دسته</option>
                            {% for cat in categories.keys() %}
                            <option value="{{ cat }}">{{ cat }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="form-group" id="subcategoryField" style="display: none;">
                        <label for="subcategorySelect">زیر دسته *</label>
                        <select id="subcategorySelect" class="form-control">
                            <option value="">انتخاب زیر دسته</option>
                        </select>
                    </div>
                    <div class="nav-buttons">
                        <div></div> <!-- Placeholder for alignment -->
                        <button class="step-btn" onclick="nextStep(1)">بعدی</button>
                    </div>
                </div>
                <div id="addStep2" class="add-step">
                    <div class="form-group">
                        <label for="locCityInput">شهرک *</label>
                        <select id="locCityInput" class="form-control">
                            <option value="">انتخاب شهرک</option>
                            {% for c in cities %}
                            <option value="{{ c }}">{{ c }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="locAddressInput">آدرس *</label>
                        <input type="text" id="locAddressInput" class="form-control" placeholder="آدرس را وارد کنید">
                    </div>
                    <div class="form-group">
                        <label for="locPhoneInput">شماره موبایل</label>
                        <input type="tel" id="locPhoneInput" class="form-control" placeholder="09xxxxxxxxx">
                    </div>
                    <div class="form-group">
                        <label for="morningShift">شیفت صبح</label>
                        <input type="text" id="morningShift" class="form-control" placeholder="مثال: 8:00 تا 14:00">
                    </div>
                    <div class="form-group">
                        <label for="eveningShift">شیفت عصر</label>
                        <input type="text" id="eveningShift" class="form-control" placeholder="مثال: 14:00 تا 22:00">
                    </div>
                    <div class="nav-buttons">
                        <button class="step-btn" onclick="prevStep(2)">برگشت</button>
                        <button class="step-btn" onclick="nextStep(2)">بعدی</button>
                    </div>
                </div>
                <div id="addStep3" class="add-step">
                    <h3>مرور اطلاعات</h3>
                    <div id="reviewData"></div>
                    <div class="nav-buttons">
                        <button class="step-btn" onclick="prevStep(3)">برگشت</button>
                        <button class="step-btn" onclick="submitLocation()">ثبت</button>
                    </div>
                </div>
            </div>
        </div>
        <div id="notificationsSection" class="content-section">
            <span class="back-arrow" onclick="backFromNotifications()">⬅️</span>
            <h3>اعلان‌ها</h3>
            <div class="notifications-section">
                <div class="notifications-list" id="notificationsList">
                    <!-- Notifications will be loaded here by JS -->
                </div>
            </div>
        </div>
        <div id="chatTab" class="content-section">
            <h3>چت</h3>
            <div class="chat-list" id="chatList">
                <!-- Chat list will be loaded here by JS -->
            </div>
        </div>
        <div id="chatRoomSection" class="content-section">
            <span class="back-arrow" onclick="showSection('chatTab', document.querySelector('.nav-tab[onclick*=\"chatTab\"]'))">⬅️</span>
            <h3 id="chatUserTitle"></h3>
            <div class="chat-messages" id="chatMessages">
                <!-- Messages will be loaded here by JS -->
            </div>
            <div class="chat-input">
                <input type="text" id="chatInput" placeholder="پیام خود را بنویسید...">
                <button class="chat-send-btn" onclick="sendMessage()">ارسال</button>
            </div>
        </div>
    </div>
    <div class="bottom-nav">
        <div class="nav-item active" onclick="showSection('homeTab', this)">
            <div class="nav-icon">🏠</div>
            <div class="nav-text">خانه</div>
        </div>
        <div class="nav-item" onclick="showSection('profileTab', this)">
            <div class="nav-icon">👤</div>
            <div class="nav-text">پروفایل</div>
        </div>
        <div class="nav-item" onclick="showSection('addTab', this)">
            <div class="nav-icon">➕</div>
            <div class="nav-text">اضافه کردن</div>
        </div>
        <div class="nav-item" onclick="showSection('chatTab', this)">
            <div class="nav-icon">💬</div>
            <div class="nav-text">چت</div>
        </div>
    </div>
""" + CUSTOM_ALERT_HTML + """
    <script>
        let currentSection = 'homeTab';
        let previousSection = '';
        let addStep = 1;
        let photos = [];
        let mainPhotoIndex = 0;
        let currentLocationId = '';
        let isMyLocation = false;
        let rating = 0;
        let chatPartner = '';
        function showCustomAlert(title, message, actionOk, actionCancel) {
            const alert = document.getElementById('customAlert');
            alert.querySelector('div[style*="background: #006769"]').textContent = title;
            alert.querySelector('div[style*="padding: 20px"]').textContent = message;
            const buttonContainer = alert.querySelector('div[style*="padding: 10px"]');
            buttonContainer.innerHTML = '';
            if (actionCancel) {
                const cancelBtn = document.createElement('button');
                cancelBtn.textContent = 'لغو';
                cancelBtn.style.cssText = 'background: #6c757d; color: white; border: none; padding: 10px 20px; border-radius: 10px; cursor: pointer; margin: 0 5px;';
                cancelBtn.onclick = function() { hideCustomAlert(); eval(actionCancel); };
                buttonContainer.appendChild(cancelBtn);
            }
            const okBtn = document.createElement('button');
            okBtn.textContent = 'تایید';
            okBtn.style.cssText = 'background: #40A578; color: white; border: none; padding: 10px 20px; border-radius: 10px; cursor: pointer; margin: 0 5px;';
            okBtn.onclick = function() { hideCustomAlert(); if (actionOk) eval(actionOk); };
            buttonContainer.appendChild(okBtn);
            alert.style.display = 'block';
        }
        function hideCustomAlert() {
            document.getElementById('customAlert').style.display = 'none';
        }
        function showSection(sectionId, element) {
            previousSection = currentSection;
            currentSection = sectionId;
            document.querySelectorAll('.content-section').forEach(section => {
                section.classList.remove('active');
            });
            document.getElementById(sectionId).classList.add('active');
            if (element && element.classList.contains('nav-item')) {
                document.querySelectorAll('.nav-item').forEach(item => {
                    item.classList.remove('active');
                });
                element.classList.add('active');
            }
            if (element && element.classList.contains('nav-tab')) {
                document.querySelectorAll('.nav-tab').forEach(tab => {
                    tab.classList.remove('active');
                });
                element.classList.add('active');
            }
            if (sectionId === 'chatTab') loadChats();
            if (sectionId === 'addTab') resetAddForm();
        }
        function switchTab(tabId, element) {
            showSection(tabId, element);
        }
        function toggleEditForm(formId) {
            document.getElementById(formId).classList.toggle('active');
        }
        function updateUsername() {
            const newUsername = document.getElementById('newUsername').value;
            fetch('/update_username', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ new_username: newUsername })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    document.querySelector('.welcome-section h2').textContent = `خوش آمدید، ${newUsername}!`;
                    document.getElementById('profileUsername').textContent = newUsername;
                    showCustomAlert('موفقیت', 'نام کاربری تغییر کرد');
                }
            });
            toggleEditForm('usernameForm');
        }
        function updatePhone() {
            const newPhone = document.getElementById('newPhone').value;
            // Similar fetch to /update_phone
            showCustomAlert('موفقیت', 'شماره تلفن تغییر کرد به: ' + newPhone);
            toggleEditForm('phoneForm');
        }
        function updateCity() {
            const newCity = document.getElementById('newCity').value;
            // Similar fetch
            document.getElementById('profileCity').textContent = newCity;
            showCustomAlert('موفقیت', 'شهر تغییر کرد به: ' + newCity);
            toggleEditForm('cityForm');
        }
        function showLogoutConfirm() {
            showCustomAlert('خروج', 'آیا مطمئن هستید که می‌خواهید خارج شوید؟', "window.location.href = '/login'", "hideCustomAlert()");
        }
        function showMyLocations() {
            showSection('myLocationsSection');
            // Fetch my locations if needed
        }
        function previewPhotos() {
            const files = document.getElementById('photoInput').files;
            for (let file of files) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    photos.push(e.target.result); // base64
                    renderPhotos();
                };
                reader.readAsDataURL(file);
            }
        }
        function renderPhotos() {
            const preview = document.getElementById('photoPreview');
            preview.innerHTML = '';
            photos.forEach((photo, index) => {
                const item = document.createElement('div');
                item.className = 'photo-item';
                item.innerHTML = `
                    <img src="${photo}" alt="Photo Preview">
                    <button class="delete-photo" onclick="deletePhoto(${index})">×</button>
                    <button class="set-main-photo" onclick="setMainPhoto(${index})">★</button>
                `;
                preview.appendChild(item);
            });
        }
        function deletePhoto(index) {
            photos.splice(index, 1);
            if (mainPhotoIndex > photos.length - 1) mainPhotoIndex = photos.length - 1;
            renderPhotos();
        }
        function setMainPhoto(index) {
            mainPhotoIndex = index;
            renderPhotos(); // Could add visual feedback
        }
        function loadSubcategories() {
            const cat = document.getElementById('categorySelect').value;
            const subSelect = document.getElementById('subcategorySelect');
            subSelect.innerHTML = '<option value="">انتخاب زیر دسته</option>';
            if (cat) {
                fetch('/get_subcategories', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ category: cat })
                })
                .then(res => res.json())
                .then(data => {
                    data.subcategories.forEach(sub => {
                        subSelect.innerHTML += `<option value="${sub}">${sub}</option>`;
                    });
                });
                document.getElementById('subcategoryField').style.display = 'block';
            } else {
                document.getElementById('subcategoryField').style.display = 'none';
            }
        }
        function nextStep(step) {
            if (step === 1) {
                if (!document.getElementById('locTitleInput').value || !document.getElementById('categorySelect').value || !document.getElementById('subcategorySelect').value) {
                    showCustomAlert('خطا', 'عنوان، دسته و زیر دسته الزامی هستند');
                    return;
                }
                addStep = 2;
            } else if (step === 2) {
                if (!document.getElementById('locCityInput').value || !document.getElementById('locAddressInput').value) {
                    showCustomAlert('خطا', 'شهرک و آدرس الزامی هستند');
                    return;
                }
                addStep = 3;
                // Populate review data
                const reviewData = document.getElementById('reviewData');
                reviewData.innerHTML = `
                    <p><strong>عنوان:</strong> ${document.getElementById('locTitleInput').value}</p>
                    <p><strong>توضیحات:</strong> ${document.getElementById('locDescInput').value || 'ندارد'}</p>
                    <p><strong>شهرک:</strong> ${document.getElementById('locCityInput').value}</p>
                    <p><strong>آدرس:</strong> ${document.getElementById('locAddressInput').value}</p>
                    <p><strong>تلفن:</strong> ${document.getElementById('locPhoneInput').value || 'ندارد'}</p>
                    <p><strong>شیفت صبح:</strong> ${document.getElementById('morningShift').value || 'ندارد'}</p>
                    <p><strong>شیفت عصر:</strong> ${document.getElementById('eveningShift').value || 'ندارد'}</p>
                    <p><strong>دسته:</strong> ${document.getElementById('categorySelect').value}</p>
                    <p><strong>زیردسته:</strong> ${document.getElementById('subcategorySelect').value}</p>
                `;
            }
            document.querySelectorAll('.add-step').forEach(s => s.classList.remove('active'));
            document.getElementById(`addStep${addStep}`).classList.add('active');
        }
        function prevStep(step) {
            addStep = step - 1;
            document.querySelectorAll('.add-step').forEach(s => s.classList.remove('active'));
            document.getElementById(`addStep${addStep}`).classList.add('active');
        }
        function submitLocation() {
            const data = {
                title: document.getElementById('locTitleInput').value,
                description: document.getElementById('locDescInput').value,
                city: document.getElementById('locCityInput').value,
                address: document.getElementById('locAddressInput').value,
                phone: document.getElementById('locPhoneInput').value,
                morning_shift: document.getElementById('morningShift').value,
                evening_shift: document.getElementById('eveningShift').value,
                category: document.getElementById('categorySelect').value,
                subcategory: document.getElementById('subcategorySelect').value,
                photos: photos,
                main_photo: mainPhotoIndex
            };
            fetch('/add_location', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    showCustomAlert('موفقیت', 'مکان ثبت شد', "showSection('homeTab', document.querySelector('.nav-tab[onclick*=\"homeTab\"]'))");
                }
            });
        }
        function resetAddForm() {
            addStep = 1;
            photos = [];
            mainPhotoIndex = 0;
            document.querySelectorAll('.add-step').forEach(s => s.classList.remove('active'));
            document.getElementById('addStep1').classList.add('active');
            document.getElementById('photoPreview').innerHTML = '';
            document.getElementById('locTitleInput').value = '';
            document.getElementById('locDescInput').value = '';
            document.getElementById('categorySelect').value = '';
            document.getElementById('subcategoryField').style.display = 'none';
            document.getElementById('subcategorySelect').value = '';
            document.getElementById('locCityInput').value = '';
            document.getElementById('locAddressInput').value = '';
            document.getElementById('locPhoneInput').value = '';
            document.getElementById('morningShift').value = '';
            document.getElementById('eveningShift').value = '';
        }
        function showLocationDetails(id, isMy = false) {
            currentLocationId = id;
            isMyLocation = isMy;
            fetch(`/get_location/${id}`)
                .then(res => res.json())
                .then(data => {
                    const slider = document.getElementById('sliderImages');
                    slider.innerHTML = '';
                    data.photos.forEach(photo => {
                        slider.innerHTML += `<div class="slider-image"><img src="/uploads/${photo}"></div>`;
                    });
                    document.getElementById('sliderCounter').textContent = `1 / ${data.photos.length}`;
                    document.getElementById('locTitle').textContent = data.title;
                    document.getElementById('locDesc').textContent = data.description || 'بدون توضیحات';
                    document.getElementById('locCity').textContent = data.city;
                    document.getElementById('locAddress').textContent = data.address;
                    if (data.phone) {
                        document.getElementById('locPhone').textContent = data.phone;
                        document.getElementById('locPhoneField').style.display = 'block';
                    } else {
                        document.getElementById('locPhoneField').style.display = 'none';
                    }
                    if (data.morning_shift || data.evening_shift) {
                        document.getElementById('locShifts').textContent = `${data.morning_shift || ''} - ${data.evening_shift || ''}`;
                        document.getElementById('locShiftsField').style.display = 'block';
                    } else {
                        document.getElementById('locShiftsField').style.display = 'none';
                    }
                    document.getElementById('locCategory').textContent = data.category || 'بدون دسته';
                    document.getElementById('locSubcategory').textContent = data.subcategory || 'بدون زیردسته';
                    const actions = document.getElementById('locActions');
                    actions.innerHTML = '';
                    if (isMy) {
                        actions.innerHTML += '<div class="action-btn" onclick="editLocation()">ویرایش</div>';
                    } else {
                        actions.innerHTML += '<div class="action-btn" onclick="scrollToComments()">دادن نظر</div>';
                        actions.innerHTML += '<div class="action-btn" onclick="startChat(\'' + data.owner + '\')">چت</div>';
                    }
                    loadComments(id);
                    showSection('locationDetailsSection');
                });
            const slider = document.getElementById('sliderImages');
            slider.addEventListener('scroll', () => {
                const index = Math.round(slider.scrollLeft / slider.clientWidth) + 1;
                document.getElementById('sliderCounter').textContent = `${index} / ${slider.children.length}`;
            });
        }
        function backToPrevious() {
            showSection(previousSection, document.querySelector(`.nav-item[onclick*="${previousSection}"]`));
        }
        function scrollToComments() {
            document.querySelector('.comments-section').scrollIntoView({ behavior: 'smooth' });
        }
        function setRating(num) {
            rating = num;
            const stars = document.querySelectorAll('.star');
            stars.forEach((star, i) => {
                star.classList.toggle('filled', i < num);
            });
        }
        function submitComment() {
            const text = document.getElementById('commentText').value;
            if (!text || rating === 0) {
                showCustomAlert('خطا', 'نظر و امتیاز الزامی هستند');
                return;
            }
            fetch('/add_comment', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ location_id: currentLocationId, text: text, rating: rating })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('commentText').value = '';
                    setRating(0);
                    loadComments(currentLocationId);
                }
            });
        }
        function loadComments(id) {
            fetch(`/get_comments/${id}`)
                .then(res => res.json())
                .then(data => {
                    const list = document.getElementById('commentsList');
                    list.innerHTML = '';
                    data.comments.forEach(comment => {
                        list.innerHTML += `<div class="comment-item"><div class="comment-user">${comment.user}</div><div class="comment-stars">${'★'.repeat(comment.rating)}${'☆'.repeat(5 - comment.rating)}</div><div class="comment-text">${comment.text}</div></div>`;
                    });
                });
        }
        function showNotifications() {
            fetch('/get_notifications')
                .then(res => res.json())
                .then(data => {
                    const list = document.getElementById('notificationsList');
                    list.innerHTML = '';
                    data.notifications.forEach(notif => {
                        list.innerHTML += `<div class="notification-tile" onclick="handleNotification('${notif.location_id}')"><div class="notification-title">${notif.title}</div><div class="notification-text">${notif.text}</div></div>`;
                    });
                    showSection('notificationsSection');
                });
        }
        function handleNotification(locId) {
            showLocationDetails(locId);
            // Mark as read
            fetch(`/mark_notification_read/${locId}`, { method: 'POST' });
        }
        function backFromNotifications() {
            showSection(previousSection, document.querySelector(`.nav-item[onclick*="${previousSection}"]`));
        }
        function editLocation() {
            fetch(`/get_location/${currentLocationId}`)
                .then(res => res.json())
                .then(data => {
                    // Fill edit form with data
                    // Similar to resetAddForm but set values
                    // Then show editLocationSection
                    showSection('editLocationSection');
                });
        }
        function loadChats() {
            // Load chat list
        }
        function startChat(user) {
            chatPartner = user;
            document.getElementById('chatUserTitle').textContent = user;
            loadMessages();
            showSection('chatRoomSection');
        }
        function loadMessages() {
            // Load messages for chatPartner
            const messages = document.getElementById('chatMessages');
            messages.innerHTML = '';
            // Dummy messages for example
            messages.innerHTML += '<div class="message sent">سلام!</div>';
            messages.innerHTML += '<div class="message received">سلام، چطوری؟</div>';
            messages.scrollTop = messages.scrollHeight;
        }
        function sendMessage() {
            const text = document.getElementById('chatInput').value;
            if (!text) return;
            fetch('/send_message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ receiver: chatPartner, text: text })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('chatInput').value = '';
                    loadMessages();
                }
            });
        }
        // Notification permission
        if (Notification.permission !== 'granted') {
            Notification.requestPermission();
        }
        // Poll for new messages/notifications every 5s
        setInterval(() => {
            if (currentSection === 'chatRoomSection') loadMessages();
            // Check for new notifications
            fetch('/check_new_notifications')
                .then(res => res.json())
                .then(data => {
                    if (data.count > 0) {
                        document.querySelector('.notification-badge').textContent = data.count;
                        if (Notification.permission === 'granted') {
                            new Notification('اعلان جدید در گویم نما');
                        }
                    }
                });
        }, 5000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(REGISTRATION_HTML, cities=CITIES)

@app.route('/register', methods=['POST'])
def register():
    global users_db
    data = request.get_json()
    username = data.get('username')
    city = data.get('city')
    phone = data.get('phone')
    password = data.get('password')
    
    # بررسی تکراری بودن نام کاربری یا شماره تلفن
    for user in users_db.values():
        if user['username'] == username:
            return jsonify({'success': False, 'message': 'نام کاربری تکراری است'})
        if user['phone'] == phone:
            return jsonify({'success': False, 'message': 'شماره تلفن تکراری است'})
    
    # ایجاد کاربر جدید (رمز عبور به صورت متنی ذخیره می‌شود - در عمل باید هش شود)
    new_user = {
        'username': username,
        'city': city,
        'phone': phone,
        'password': password,  # در عمل باید از generate_password_hash استفاده شود
        'timestamp': data.get('timestamp')
    }
    
    users_db[username] = new_user
    
    return jsonify({'success': True, 'user': new_user})

@app.route('/login')
def login():
    return render_template_string(LOGIN_HTML)

@app.route('/login', methods=['POST'])
def login_post():
    global users_db
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # جستجوی کاربر
    user = None
    for u in users_db.values():
        if u['username'] == username or u['phone'] == username:
            user = u
            break
    
    if user and user['password'] == password:  # در عمل باید از check_password_hash استفاده شود
        # session['username'] = username # اگر از session استفاده می‌کردید
        return jsonify({'success': True, 'user': {'username': user['username']}})
    else:
        return jsonify({'success': False, 'message': 'اطلاعات نادرست'})

@app.route('/main')
def main():
    username = request.args.get('username', 'کاربر')
    # if username not in session: # اگر از session استفاده می‌کردید
    #     return redirect('/login')
    user_data = users_db.get(username, {})
    
    my_locations = [loc for loc in locations_db if loc['owner'] == username]
    all_locations = locations_db
    notifications_count = len(notifications_db.get(username, []))
    
    return render_template_string(MAIN_HTML,
                                  username=username,
                                  phone=user_data.get('phone', ''),
                                  city=user_data.get('city', ''),
                                  password=user_data.get('password', '******'),
                                  user_city=user_data.get('city', ''),
                                  cities=CITIES,
                                  categories=CATEGORIES,
                                  my_locations=my_locations,
                                  all_locations=all_locations,
                                  notifications_count=notifications_count)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/add_location', methods=['POST'])
def add_location():
    global locations_db
    data = request.get_json()
    location_id = str(uuid.uuid4())
    photos = []
    for i, photo in enumerate(data['photos']):
        # Decode base64 image
        photo_data = base64.b64decode(photo.split(',')[1])
        filename = f"{location_id}_{i}.jpg"
        with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'wb') as f:
            f.write(photo_data)
        photos.append(filename)
    
    new_loc = {
        'id': location_id,
        'owner': session.get('username', 'unknown'), # در اینجا باید نام کاربری از session یا token بگیرید
        'title': data['title'],
        'description': data['description'],
        'category': data['category'],
        'subcategory': data['subcategory'],
        'city': data['city'],
        'address': data['address'],
        'phone': data['phone'],
        'morning_shift': data['morning_shift'],
        'evening_shift': data['evening_shift'],
        'photos': photos,
        'main_photo': data['main_photo']
    }
    locations_db.append(new_loc)
    
    # Send notifications to users in same city
    for user, udata in users_db.items():
        if udata['city'] == data['city'] and user != session.get('username', 'unknown'):
            notifications_db.setdefault(user, []).append({
                'title': 'مکان جدید',
                'text': f"مکان {data['title']} در شهرک {data['city']} ثبت شد",
                'location_id': location_id,
                'read': False
            })
    
    return jsonify({'success': True})

@app.route('/get_subcategories', methods=['POST'])
def get_subcategories():
    data = request.get_json()
    return jsonify({'subcategories': CATEGORIES.get(data['category'], [])})

@app.route('/get_location/<loc_id>')
def get_location(loc_id):
    loc = next((l for l in locations_db if l['id'] == loc_id), None)
    if loc:
        return jsonify(loc)
    else:
        return jsonify({'error': 'Location not found'}), 404

@app.route('/add_comment', methods=['POST'])
def add_comment():
    global comments_db
    data = request.get_json()
    location_id = data['location_id']
    comment = {
        'user': session.get('username', 'ناشناس'), # در اینجا باید نام کاربری از session یا token بگیرید
        'text': data['text'],
        'rating': data['rating'],
        'timestamp': datetime.now().isoformat()
    }
    comments_db.setdefault(location_id, []).append(comment)
    return jsonify({'success': True})

@app.route('/get_comments/<loc_id>')
def get_comments(loc_id):
    return jsonify({'comments': comments_db.get(loc_id, [])})

@app.route('/get_notifications')
def get_notifications():
    username = session.get('username', 'ناشناس') # در اینجا باید نام کاربری از session یا token بگیرید
    return jsonify({'notifications': notifications_db.get(username, [])})

@app.route('/mark_notification_read/<loc_id>', methods=['POST'])
def mark_notification_read(loc_id):
    username = session.get('username', 'ناشناس') # در اینجا باید نام کاربری از session یا token بگیرید
    notifs = notifications_db.get(username, [])
    for n in notifs:
        if n['location_id'] == loc_id:
            n['read'] = True
    return jsonify({'success': True})

@app.route('/check_new_notifications')
def check_new_notifications():
    username = session.get('username', 'ناشناس') # در اینجا باید نام کاربری از session یا token بگیرید
    notifs = notifications_db.get(username, [])
    count = sum(1 for n in notifs if not n['read'])
    return jsonify({'count': count})

@app.route('/update_username', methods=['POST'])
def update_username():
    global users_db
    data = request.get_json()
    old = session.get('username', 'ناشناس') # در اینجا باید نام کاربری از session یا token بگیرید
    if data['new_username'] not in users_db:
        users_db[data['new_username']] = users_db.pop(old)
        session['username'] = data['new_username'] # در اینجا باید session یا token را به‌روز کنید
        # Update all related data (locations, comments, chats, etc.)
        for loc in locations_db:
            if loc['owner'] == old:
                loc['owner'] = data['new_username']
        for coms in comments_db.values():
            for com in coms:
                if com['user'] == old:
                    com['user'] = data['new_username']
        # Chats keys need update
        new_chats = {}
        for key, msgs in chats_db.items():
            new_key = tuple([data['new_username'] if u == old else u for u in key])
            new_chats[new_key] = msgs
        chats_db.clear()
        chats_db.update(new_chats)
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'نام کاربری تکراری است'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))