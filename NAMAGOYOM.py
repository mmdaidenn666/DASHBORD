import os
import json
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# اطمینان از وجود دایرکتوری uploads
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# مسیر فایل‌های داده
DATA_FILE = 'users.json'
LOCATIONS_FILE = 'locations.json'
COMMENTS_FILE = 'comments.json'
CHAT_FILE = 'chat.json'
NOTIFICATIONS_FILE = 'notifications.json'

# بارگذاری داده‌ها از فایل‌ها یا ایجاد فایل خالی اگر وجود نداشته باشند
def load_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    else:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump([], f)
        return []

# ذخیره داده‌ها در فایل‌ها
def save_data(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# بارگذاری داده‌ها
users = load_data(DATA_FILE)
locations = load_data(LOCATIONS_FILE)
comments = load_data(COMMENTS_FILE)
chat_messages = load_data(CHAT_FILE)
notifications = load_data(NOTIFICATIONS_FILE)

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

# HTML Template برای صفحه اصلی
MAIN_HTML_TEMPLATE = """
<!DOCTYPE html>
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
            --success: #4caf50;
            --error: #f44336;
            --background: #f8f9fa;
            --text: #333;
            --light: #fff;
            --gray: #e9ecef;
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
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 0;
            margin-bottom: 20px;
            border-bottom: 2px solid var(--primary);
        }
        .logo {
            font-size: 24px;
            font-weight: 700;
            color: var(--primary);
        }
        .welcome {
            text-align: center;
            margin-bottom: 30px;
        }
        .welcome h2 {
            color: var(--primary);
            margin-bottom: 10px;
        }
        .content-section {
            display: none;
            background: var(--light);
            border-radius: 15px;
            padding: 30px;
            box-shadow: var(--shadow);
            margin-bottom: 20px;
            animation: fadeIn 0.5s ease-out;
        }
        .content-section.active {
            display: block;
        }
        h3 {
            color: var(--primary);
            margin-bottom: 20px;
            text-align: center;
        }
        .locations-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
        }
        .location-tile {
            background: var(--light);
            border-radius: 10px;
            overflow: hidden;
            box-shadow: var(--shadow);
            cursor: pointer;
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .location-tile:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
        }
        .location-image {
            height: 150px;
            background-size: cover;
            background-position: center;
        }
        .location-info {
            padding: 15px;
        }
        .location-title {
            font-weight: 500;
            margin-bottom: 5px;
            color: var(--text);
        }
        .location-city {
            color: #666;
            font-size: 14px;
        }
        .location-details {
            text-align: right;
        }
        .detail-field {
            margin-bottom: 15px;
        }
        .detail-label {
            font-weight: 500;
            color: var(--primary);
            margin-bottom: 5px;
        }
        .detail-value {
            color: #555;
        }
        .action-buttons {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        .edit-btn, .delete-btn, .back-btn, .submit-btn, .cancel-btn, .save-btn {
            padding: 10px 15px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: 500;
            transition: background 0.3s;
        }
        .edit-btn, .submit-btn, .save-btn {
            background: var(--primary);
            color: white;
        }
        .edit-btn:hover, .submit-btn:hover, .save-btn:hover {
            background: #005052;
        }
        .delete-btn {
            background: var(--error);
            color: white;
        }
        .delete-btn:hover {
            background: #d32f2f;
        }
        .back-btn, .cancel-btn {
            background: var(--gray);
            color: var(--text);
        }
        .back-btn:hover, .cancel-btn:hover {
            background: #d1d1d1;
        }
        .add-container {
            max-width: 600px;
            margin: 0 auto;
        }
        .add-step {
            display: none;
        }
        .add-step.active {
            display: block;
        }
        .photo-upload {
            border: 2px dashed #ccc;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            cursor: pointer;
            margin-bottom: 20px;
            transition: border-color 0.3s;
        }
        .photo-upload:hover {
            border-color: var(--primary);
        }
        .photo-preview {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 20px;
        }
        .preview-item {
            position: relative;
            width: 100px;
            height: 100px;
        }
        .preview-item img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            border-radius: 5px;
        }
        .remove-photo {
            position: absolute;
            top: -5px;
            right: -5px;
            background: var(--error);
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
            bottom: -5px;
            left: -5px;
            background: var(--success);
            color: white;
            border: none;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            cursor: pointer;
            font-size: 12px;
        }
        .form-field {
            margin-bottom: 20px;
        }
        .form-field label {
            display: block;
            margin-bottom: 5px;
            font-weight: 500;
            color: var(--text);
        }
        .form-field input, .form-field textarea, .form-field select {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        .form-field textarea {
            height: 100px;
            resize: vertical;
        }
        .nav-buttons {
            display: flex;
            justify-content: space-between;
            margin-top: 30px;
        }
        .profile-card {
            background: var(--light);
            border-radius: 15px;
            padding: 30px;
            box-shadow: var(--shadow);
            text-align: center;
        }
        .profile-item {
            display: flex;
            justify-content: space-between;
            padding: 15px 0;
            border-bottom: 1px solid #eee;
        }
        .profile-item:last-child {
            border-bottom: none;
        }
        .profile-label {
            font-weight: 500;
            color: var(--primary);
        }
        .profile-value {
            color: #555;
        }
        .edit-form {
            margin-top: 20px;
            text-align: left;
        }
        .form-actions {
            display: flex;
            justify-content: flex-end;
            gap: 10px;
            margin-top: 15px;
        }
        .action-button {
            background: var(--secondary);
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: 500;
            margin: 5px;
            transition: background 0.3s;
        }
        .action-button:hover {
            background: #338a61;
        }
        .my-locations-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
        }
        .back-arrow {
            font-size: 24px;
            cursor: pointer;
            margin-bottom: 20px;
            display: inline-block;
        }
        .bottom-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: var(--light);
            display: flex;
            justify-content: space-around;
            padding: 15px 0;
            box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
            z-index: 1000;
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
            font-size: 24px;
            margin-bottom: 5px;
        }
        .nav-text {
            font-size: 12px;
        }
        .chat-list, .chat-messages {
            height: 70vh;
            overflow-y: auto;
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
        }
        .chat-item, .message {
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 5px;
            cursor: pointer;
        }
        .chat-item:hover, .message:hover {
            background: #f0f0f0;
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
            background: var(--primary);
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 5px;
            cursor: pointer;
        }
        .chat-send-btn:hover {
            background: #005052;
        }
        .message.sent {
            background: #e3f2fd;
            text-align: left;
        }
        .message.received {
            background: #f5f5f5;
            text-align: right;
        }
        .notifications-list {
            max-height: 70vh;
            overflow-y: auto;
        }
        .notification-item {
            padding: 15px;
            border-bottom: 1px solid #eee;
            cursor: pointer;
        }
        .notification-item:hover {
            background: #f9f9f9;
        }
        .notification-item.unread {
            background: #e8f5e9;
        }
        .notification-title {
            font-weight: 500;
            margin-bottom: 5px;
        }
        .notification-message {
            color: #666;
            font-size: 14px;
        }
        .notification-time {
            color: #999;
            font-size: 12px;
            margin-top: 5px;
        }
        /* Comment Section */
        .comments-section {
            margin-top: 30px;
        }
        .comment-form {
            margin-bottom: 20px;
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
            transition: color 0.3s;
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
            background: var(--gray);
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
            color: #666;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @media (max-width: 768px) {
            .bottom-nav {
                padding: 10px 0;
            }
            .nav-icon {
                font-size: 20px;
            }
            .nav-text {
                font-size: 10px;
            }
            .locations-list, .my-locations-list {
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">گویم نما</div>
            <div class="welcome">
                <h2>خوش آمدید، {{ username }}!</h2>
                <p>به اپلیکیشن گویم نما خوش آمدید</p>
            </div>
        </div>

        <div id="homeSection" class="content-section active">
            <h3>صفحه اصلی</h3>
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

        <div id="locationDetailSection" class="content-section">
            <span class="back-arrow" onclick="showSection('homeSection', document.querySelector('.nav-item[onclick*=\"homeSection\"]'))">⬅️</span>
            <h3 id="locTitle"></h3>
            <div class="location-details">
                <div class="detail-field">
                    <div class="detail-label">تصاویر</div>
                    <div id="locPhotos"></div>
                </div>
                <div class="detail-field">
                    <div class="detail-label">توضیحات</div>
                    <div class="detail-value" id="locDesc"></div>
                </div>
                <div class="detail-field">
                    <div class="detail-label">شهرک</div>
                    <div class="detail-value" id="locCity"></div>
                </div>
                <div class="detail-field">
                    <div class="detail-label">آدرس</div>
                    <div class="detail-value" id="locAddress"></div>
                </div>
                <div class="detail-field" id="locPhoneField">
                    <div class="detail-label">شماره موبایل</div>
                    <div class="detail-value" id="locPhone"></div>
                </div>
                <div class="detail-field" id="locShiftsField">
                    <div class="detail-label">شیفت‌ها</div>
                    <div class="detail-value" id="locShifts"></div>
                </div>
                <div class="detail-field">
                    <div class="detail-label">دسته</div>
                    <div class="detail-value" id="locCategory"></div>
                </div>
                <div class="detail-field">
                    <div class="detail-label">زیر دسته</div>
                    <div class="detail-value" id="locSubcategory"></div>
                </div>
                <div class="action-buttons" id="locActions"></div>
            </div>
            <div class="comments-section">
                <h4>نظرات</h4>
                <div class="comment-form">
                    <textarea id="commentText" placeholder="نظر خود را بنویسید"></textarea>
                    <div class="star-rating">
                        <span class="star" onclick="setRating(1)">★</span>
                        <span class="star" onclick="setRating(2)">★</span>
                        <span class="star" onclick="setRating(3)">★</span>
                        <span class="star" onclick="setRating(4)">★</span>
                        <span class="star" onclick="setRating(5)">★</span>
                    </div>
                    <button class="submit-btn" onclick="submitComment()">ارسال نظر</button>
                </div>
                <div class="comments-list" id="commentsList"></div>
            </div>
        </div>

        <div id="profileSection" class="content-section">
            <div class="profile-card">
                <h3>پروفایل کاربری</h3>
                <div class="profile-item">
                    <div class="profile-label">نام کاربری</div>
                    <div class="profile-value" id="profileUsername">{{ username }}</div>
                </div>
                <div class="profile-item">
                    <div class="profile-label">شهر</div>
                    <div class="profile-value" id="profileCity">{{ city }}</div>
                </div>
                <div class="profile-item">
                    <div class="profile-label">شماره تلفن</div>
                    <div class="profile-value" id="profilePhone">{{ phone }}</div>
                </div>
                <div class="profile-item">
                    <div class="profile-label">تاریخ عضویت</div>
                    <div class="profile-value" id="profileTimestamp">{{ timestamp }}</div>
                </div>
                
                <div class="edit-form" id="passwordForm" style="display: none;">
                    <input type="password" id="newPassword" placeholder="رمز عبور جدید" class="form-control">
                    <input type="password" id="confirmNewPassword" placeholder="تکرار رمز عبور" class="form-control" style="margin-top: 10px;">
                    <div class="form-actions">
                        <button class="cancel-btn" onclick="toggleEditForm('passwordForm')">لغو</button>
                        <button class="save-btn" onclick="updatePassword()">ذخیره</button>
                    </div>
                </div>
                
                <div class="profile-actions">
                    <button class="action-button" onclick="showMyLocations()">مکان های من</button>
                    <button class="action-button" onclick="showNotifications()">اعلان ها</button>
                    <button class="action-button" onclick="toggleEditForm('passwordForm')">تغییر رمز عبور</button>
                    <button class="action-button" onclick="logout()">خروج</button>
                </div>
            </div>
        </div>

        <div id="myLocationsSection" class="content-section">
            <span class="back-arrow" onclick="showSection('profileSection', document.querySelector('.nav-item[onclick*=\"profileSection\"]'))">⬅️</span>
            <h3>مکان های من</h3>
            <div class="my-locations-list" id="myLocationsList"></div>
        </div>

        <div id="addSection" class="content-section">
            <h3>افزودن مکان</h3>
            <div class="add-container">
                <div id="addStep1" class="add-step active">
                    <div class="photo-upload" onclick="document.getElementById('photoInput').click()">
                        <span style="font-size: 50px;">+</span>
                        <p>اضافه کردن عکس</p>
                    </div>
                    <input type="file" id="photoInput" multiple accept="image/*" style="display: none;" onchange="previewPhotos()">
                    <div class="photo-preview" id="photoPreview"></div>
                    
                    <div class="form-field">
                        <label class="required">عنوان مکان</label>
                        <input type="text" id="locTitleInput" placeholder="عنوان را وارد کنید">
                    </div>
                    <div class="form-field">
                        <label>توضیحات</label>
                        <textarea id="locDescInput" placeholder="توضیحات را وارد کنید"></textarea>
                    </div>
                    <div class="form-field">
                        <label>دسته</label>
                        <select id="categorySelect" onchange="loadSubcategories()">
                            <option value="">انتخاب دسته</option>
                            {% for cat in categories.keys() %}
                            <option value="{{ cat }}">{{ cat }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="form-field" id="subcategoryField" style="display: none;">
                        <label>زیر دسته</label>
                        <select id="subcategorySelect">
                            <option value="">انتخاب زیر دسته</option>
                        </select>
                    </div>
                    <div class="nav-buttons">
                        <div></div> <!-- Placeholder for alignment -->
                        <button class="next-btn" onclick="nextStep(1)">بعدی</button>
                    </div>
                </div>

                <div id="addStep2" class="add-step">
                    <div class="form-field">
                        <label>شهرک</label>
                        <select id="locCityInput">
                            <option value="">انتخاب شهرک</option>
                            {% for city in cities %}
                            <option value="{{ city }}">{{ city }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="form-field">
                        <label>آدرس</label>
                        <input type="text" id="locAddressInput" placeholder="آدرس را وارد کنید">
                    </div>
                    <div class="form-field">
                        <label>شماره موبایل</label>
                        <input type="tel" id="locPhoneInput" placeholder="09xxxxxxxxx">
                    </div>
                    <div class="form-field">
                        <label>شیفت صبح</label>
                        <input type="text" id="morningShift" placeholder="مثال: 8:00 تا 14:00">
                    </div>
                    <div class="form-field">
                        <label>شیفت عصر</label>
                        <input type="text" id="eveningShift" placeholder="مثال: 14:00 تا 22:00">
                    </div>
                    <div class="nav-buttons">
                        <button class="back-btn" onclick="prevStep(2)">برگشت</button>
                        <button class="next-btn" onclick="nextStep(2)">بعدی</button>
                    </div>
                </div>

                <div id="addStep3" class="add-step">
                    <h4>مرور اطلاعات</h4>
                    <div id="reviewData"></div>
                    <div class="nav-buttons">
                        <button class="back-btn" onclick="prevStep(3)">برگشت</button>
                        <button class="submit-btn" onclick="submitLocation()">ثبت</button>
                    </div>
                </div>
            </div>
        </div>

        <div id="editLocationSection" class="content-section">
            <span class="back-arrow" onclick="showMyLocations()">⬅️</span>
            <h3>ویرایش مکان</h3>
            <!-- Similar to add section but pre-filled -->
            <div class="add-container">
                <!-- ... (duplicate add steps with pre-fill logic in JS) ... -->
            </div>
        </div>

        <div id="notificationsSection" class="content-section">
            <span class="back-arrow" onclick="backFromNotifications()">⬅️</span>
            <h3>اعلان‌ها</h3>
            <div class="notifications-list" id="notificationsList"></div>
        </div>

        <div id="chatSection" class="content-section">
            <h3>چت</h3>
            <div class="chat-list" id="chatList"></div>
        </div>

        <div id="chatRoomSection" class="content-section">
            <span class="back-arrow" onclick="showSection('chatSection', document.querySelector('.nav-item[onclick*=\"chatSection\"]'))">⬅️</span>
            <h3 id="chatUserTitle"></h3>
            <div class="chat-messages" id="chatMessages"></div>
            <div class="chat-input">
                <input type="text" id="chatInput" placeholder="پیام خود را بنویسید...">
                <button class="chat-send-btn" onclick="sendMessage()">ارسال</button>
            </div>
        </div>
    </div>

    <div class="bottom-nav">
        <div class="nav-item" onclick="showSection('profileSection', this)">
            <div class="nav-icon">👤</div>
            <div class="nav-text">پروفایل</div>
        </div>
        <div class="nav-item" onclick="showSection('chatSection', this)">
            <div class="nav-icon">💬</div>
            <div class="nav-text">چت</div>
        </div>
        <div class="nav-item active" onclick="showSection('homeSection', this)">
            <div class="nav-icon">🏠</div>
            <div class="nav-text">صفحه اصلی</div>
        </div>
        <div class="nav-item" onclick="showSection('addSection', this)">
            <div class="nav-icon">➕</div>
            <div class="nav-text">اضافه کردن</div>
        </div>
    </div>

    <script>
        let currentSection = 'homeSection';
        let previousSection = '';
        let addStep = 1;
        let photos = [];
        let mainPhotoIndex = 0;
        let currentLocationId = '';
        let isMyLocation = false;
        let rating = 0;
        let chatPartner = '';

        function showSection(sectionId, element) {
            previousSection = currentSection;
            currentSection = sectionId;
            
            document.querySelectorAll('.content-section').forEach(section => {
                section.classList.remove('active');
            });
            document.getElementById(sectionId).classList.add('active');
            
            document.querySelectorAll('.nav-item').forEach(item => {
                item.classList.remove('active');
            });
            if (element) element.classList.add('active');
        }

        function showLocationDetails(locationId) {
            const location = locations.find(loc => loc.id === locationId);
            if (!location) return;
            
            currentLocationId = locationId;
            isMyLocation = location.owner === '{{ username }}';
            
            document.getElementById('locTitle').textContent = location.title;
            document.getElementById('locDesc').textContent = location.description || 'بدون توضیح';
            document.getElementById('locCity').textContent = location.city;
            document.getElementById('locAddress').textContent = location.address || 'بدون آدرس';
            
            const phoneField = document.getElementById('locPhoneField');
            const phoneValue = document.getElementById('locPhone');
            if (location.phone) {
                phoneField.style.display = 'block';
                phoneValue.textContent = location.phone;
            } else {
                phoneField.style.display = 'none';
            }
            
            const shiftsField = document.getElementById('locShiftsField');
            const shiftsValue = document.getElementById('locShifts');
            if (location.morning_shift || location.evening_shift) {
                shiftsField.style.display = 'block';
                shiftsValue.textContent = `${location.morning_shift || '---'} | ${location.evening_shift || '---'}`;
            } else {
                shiftsField.style.display = 'none';
            }
            
            document.getElementById('locCategory').textContent = location.category || 'بدون دسته';
            document.getElementById('locSubcategory').textContent = location.subcategory || 'بدون زیردسته';
            
            const photosContainer = document.getElementById('locPhotos');
            photosContainer.innerHTML = '';
            location.photos.forEach((photo, index) => {
                const img = document.createElement('img');
                img.src = `/uploads/${photo}`;
                img.alt = `Photo ${index + 1}`;
                img.style.width = '100px';
                img.style.height = '100px';
                img.style.objectFit = 'cover';
                img.style.margin = '5px';
                img.style.borderRadius = '5px';
                photosContainer.appendChild(img);
            });
            
            const actionsContainer = document.getElementById('locActions');
            actionsContainer.innerHTML = '';
            if (isMyLocation) {
                const editBtn = document.createElement('button');
                editBtn.className = 'edit-btn';
                editBtn.textContent = 'ویرایش';
                editBtn.onclick = () => editLocation(locationId);
                actionsContainer.appendChild(editBtn);
                
                const deleteBtn = document.createElement('button');
                deleteBtn.className = 'delete-btn';
                deleteBtn.textContent = 'حذف';
                deleteBtn.onclick = () => deleteLocation(locationId);
                actionsContainer.appendChild(deleteBtn);
            }
            
            loadComments(locationId);
            showSection('locationDetailSection');
        }

        function loadComments(locationId) {
            fetch(`/get_comments/${locationId}`)
                .then(res => res.json())
                .then(data => {
                    const commentsList = document.getElementById('commentsList');
                    commentsList.innerHTML = '';
                    data.comments.forEach(comment => {
                        const commentItem = document.createElement('div');
                        commentItem.className = 'comment-item';
                        const stars = '★'.repeat(comment.rating) + '☆'.repeat(5 - comment.rating);
                        commentItem.innerHTML = `
                            <div class="comment-user">${comment.username}</div>
                            <div class="comment-stars">${stars}</div>
                            <div class="comment-text">${comment.text}</div>
                        `;
                        commentsList.appendChild(commentItem);
                    });
                });
        }

        function setRating(ratingValue) {
            rating = ratingValue;
            const stars = document.querySelectorAll('.star-rating .star');
            stars.forEach((star, index) => {
                if (index < ratingValue) {
                    star.classList.add('filled');
                } else {
                    star.classList.remove('filled');
                }
            });
        }

        function submitComment() {
            const text = document.getElementById('commentText').value;
            if (!text || rating === 0) {
                alert('لطفاً نظر و امتیاز را وارد کنید');
                return;
            }
            
            const data = {
                location_id: currentLocationId,
                text: text,
                rating: rating
            };
            
            fetch('/add_comment', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
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

        function showMyLocations() {
            fetch('/my_locations')
                .then(res => res.json())
                .then(data => {
                    const container = document.getElementById('myLocationsList');
                    container.innerHTML = '';
                    data.locations.forEach(loc => {
                        const locTile = document.createElement('div');
                        locTile.className = 'location-tile';
                        locTile.onclick = () => showLocationDetails(loc.id);
                        locTile.innerHTML = `
                            <div class="location-image" style="background-image: url('/uploads/${loc.photos[0]}');"></div>
                            <div class="location-info">
                                <div class="location-title">${loc.title}</div>
                                <div class="location-city">${loc.city}</div>
                            </div>
                        `;
                        container.appendChild(locTile);
                    });
                    showSection('myLocationsSection');
                });
        }

        function editLocation(locationId) {
            // Implementation for editing location
            alert('ویرایش مکان: ' + locationId);
        }

        function deleteLocation(locationId) {
            if (confirm('آیا مطمئن هستید که می‌خواهید این مکان را حذف کنید؟')) {
                fetch(`/delete_location/${locationId}`, { method: 'DELETE' })
                    .then(res => res.json())
                    .then(data => {
                        if (data.success) {
                            showMyLocations();
                        }
                    });
            }
        }

        function previewPhotos() {
            const input = document.getElementById('photoInput');
            const preview = document.getElementById('photoPreview');
            preview.innerHTML = '';
            
            for (let i = 0; i < input.files.length; i++) {
                const file = input.files[i];
                if (!file.type.match('image.*')) continue;
                
                const reader = new FileReader();
                reader.onload = function(e) {
                    const previewItem = document.createElement('div');
                    previewItem.className = 'preview-item';
                    previewItem.innerHTML = `
                        <img src="${e.target.result}" alt="Preview">
                        <button class="remove-photo" onclick="removePhoto(${photos.length})">×</button>
                        <button class="set-main-photo" onclick="setMainPhoto(${photos.length})">★</button>
                    `;
                    preview.appendChild(previewItem);
                    photos.push(file);
                };
                reader.readAsDataURL(file);
            }
        }

        function removePhoto(index) {
            photos.splice(index, 1);
            previewPhotos(); // Re-render previews
        }

        function setMainPhoto(index) {
            mainPhotoIndex = index;
            // Visual feedback for main photo could be added here
        }

        function loadSubcategories() {
            const category = document.getElementById('categorySelect').value;
            const subcategoryField = document.getElementById('subcategoryField');
            const subcategorySelect = document.getElementById('subcategorySelect');
            
            if (category) {
                subcategoryField.style.display = 'block';
                subcategorySelect.innerHTML = '<option value="">انتخاب زیر دسته</option>';
                const subcategories = {{ categories | tojson }}[category];
                subcategories.forEach(sub => {
                    const option = document.createElement('option');
                    option.value = sub;
                    option.textContent = sub;
                    subcategorySelect.appendChild(option);
                });
            } else {
                subcategoryField.style.display = 'none';
            }
        }

        function nextStep(step) {
            document.getElementById(`addStep${step}`).classList.remove('active');
            document.getElementById(`addStep${step + 1}`).classList.add('active');
            addStep = step + 1;
            
            if (step === 2) {
                // Populate review data
                const reviewData = document.getElementById('reviewData');
                reviewData.innerHTML = `
                    <p><strong>عنوان:</strong> ${document.getElementById('locTitleInput').value}</p>
                    <p><strong>توضیحات:</strong> ${document.getElementById('locDescInput').value || 'ندارد'}</p>
                    <p><strong>شهرک:</strong> ${document.getElementById('locCityInput').value}</p>
                    <p><strong>آدرس:</strong> ${document.getElementById('locAddressInput').value || 'ندارد'}</p>
                    <p><strong>تلفن:</strong> ${document.getElementById('locPhoneInput').value || 'ندارد'}</p>
                    <p><strong>شیفت صبح:</strong> ${document.getElementById('morningShift').value || 'ندارد'}</p>
                    <p><strong>شیفت عصر:</strong> ${document.getElementById('eveningShift').value || 'ندارد'}</p>
                    <p><strong>دسته:</strong> ${document.getElementById('categorySelect').value || 'ندارد'}</p>
                    <p><strong>زیردسته:</strong> ${document.getElementById('subcategorySelect').value || 'ندارد'}</p>
                `;
            }
        }

        function prevStep(step) {
            document.getElementById(`addStep${step}`).classList.remove('active');
            document.getElementById(`addStep${step - 1}`).classList.add('active');
            addStep = step - 1;
        }

        function submitLocation() {
            const formData = new FormData();
            photos.forEach((photo, index) => {
                formData.append('photos', photo);
            });
            formData.append('title', document.getElementById('locTitleInput').value);
            formData.append('description', document.getElementById('locDescInput').value);
            formData.append('city', document.getElementById('locCityInput').value);
            formData.append('address', document.getElementById('locAddressInput').value);
            formData.append('phone', document.getElementById('locPhoneInput').value);
            formData.append('morning_shift', document.getElementById('morningShift').value);
            formData.append('evening_shift', document.getElementById('eveningShift').value);
            formData.append('category', document.getElementById('categorySelect').value);
            formData.append('subcategory', document.getElementById('subcategorySelect').value);
            formData.append('main_photo', mainPhotoIndex);
            
            fetch('/add_location', {
                method: 'POST',
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    alert('مکان با موفقیت ثبت شد');
                    resetAddForm();
                    showSection('homeSection', document.querySelector('.nav-item[onclick*="homeSection"]'));
                }
            });
        }

        function resetAddForm() {
            document.getElementById('addStep3').classList.remove('active');
            document.getElementById('addStep1').classList.add('active');
            addStep = 1;
            photos = [];
            mainPhotoIndex = 0;
            document.getElementById('photoPreview').innerHTML = '';
            document.getElementById('locTitleInput').value = '';
            document.getElementById('locDescInput').value = '';
            document.getElementById('locCityInput').value = '';
            document.getElementById('locAddressInput').value = '';
            document.getElementById('locPhoneInput').value = '';
            document.getElementById('morningShift').value = '';
            document.getElementById('eveningShift').value = '';
            document.getElementById('categorySelect').value = '';
            document.getElementById('subcategoryField').style.display = 'none';
            document.getElementById('subcategorySelect').value = '';
        }

        function showNotifications() {
            fetch('/notifications')
                .then(res => res.json())
                .then(data => {
                    const container = document.getElementById('notificationsList');
                    container.innerHTML = '';
                    data.notifications.forEach(notif => {
                        const notifItem = document.createElement('div');
                        notifItem.className = `notification-item ${notif.read ? '' : 'unread'}`;
                        notifItem.innerHTML = `
                            <div class="notification-title">${notif.title}</div>
                            <div class="notification-message">${notif.message}</div>
                            <div class="notification-time">${new Date(notif.timestamp).toLocaleString('fa-IR')}</div>
                        `;
                        container.appendChild(notifItem);
                    });
                    showSection('notificationsSection');
                });
        }

        function backFromNotifications() {
            showSection('profileSection', document.querySelector('.nav-item[onclick*="profileSection"]'));
        }

        function logout() {
            if (confirm('آیا مطمئن هستید که می‌خواهید خارج شوید؟')) {
                window.location.href = '/logout';
            }
        }

        function toggleEditForm(formId) {
            const form = document.getElementById(formId);
            form.style.display = form.style.display === 'none' ? 'block' : 'none';
        }

        function updatePassword() {
            const newPassword = document.getElementById('newPassword').value;
            const confirmNewPassword = document.getElementById('confirmNewPassword').value;
            
            if (newPassword !== confirmNewPassword) {
                alert('رمزهای عبور مطابقت ندارند');
                return;
            }
            
            fetch('/update_password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ new_password: newPassword })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    alert('رمز عبور با موفقیت تغییر کرد');
                    toggleEditForm('passwordForm');
                    document.getElementById('newPassword').value = '';
                    document.getElementById('confirmNewPassword').value = '';
                }
            });
        }

        // Chat functions would be implemented here
        function showChat() {
            // Implementation for showing chat
        }

        function sendMessage() {
            // Implementation for sending message
        }

        // Initial data
        const locations = {{ all_locations | tojson }};
    </script>
</body>
</html>
"""

# HTML template for registration page (updated with custom alert)
CUSTOM_ALERT_HTML = """
<div id="customAlert" class="custom-alert" style="display:none;">
    <div class="custom-alert-content">
        <span class="close-btn" onclick="hideCustomAlert()">&times;</span>
        <div class="alert-icon">!</div>
        <h3 id="alertTitle"></h3>
        <p id="alertMessage"></p>
        <button class="alert-btn" onclick="handleAlertAction()">تایید</button>
    </div>
</div>
<style>
.custom-alert {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0,0,0,0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 10000;
}
.custom-alert-content {
    background-color: white;
    padding: 30px;
    border-radius: 10px;
    text-align: center;
    position: relative;
    max-width: 90%;
    width: 400px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}
.close-btn {
    position: absolute;
    top: 10px;
    left: 15px;
    font-size: 28px;
    font-weight: bold;
    cursor: pointer;
}
.alert-icon {
    font-size: 48px;
    color: #4CAF50;
    margin-bottom: 20px;
}
#alertTitle {
    margin: 0 0 10px 0;
    font-size: 24px;
    color: #333;
}
#alertMessage {
    margin: 0 0 20px 0;
    font-size: 16px;
    color: #666;
}
.alert-btn {
    background-color: #4CAF50;
    border: none;
    color: white;
    padding: 12px 24px;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 16px;
    margin: 4px 2px;
    cursor: pointer;
    border-radius: 5px;
    transition: background-color 0.3s;
}
.alert-btn:hover {
    background-color: #45a049;
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
</style>
<script>
let alertAction = '';
function showCustomAlert(title, message, action) {
    document.getElementById('alertTitle').textContent = title;
    document.getElementById('alertMessage').textContent = message;
    alertAction = action;
    document.getElementById('customAlert').style.display = 'flex';
}
function hideCustomAlert() {
    document.getElementById('customAlert').style.display = 'none';
}
function handleAlertAction() {
    hideCustomAlert();
    if (alertAction) {
        eval(alertAction);
    }
}
</script>
"""

REGISTRATION_HTML = """
<!DOCTYPE html>
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
                if (fullname.value.trim() === '' || fullname.value.length < 3) {
                    fullname.classList.add('error');
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
                const phoneRegex = /^09\d{9}$/;
                if (!phoneRegex.test(phone.value)) {
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
                                showCustomAlert('خطا', 'خطا در ثبت نام: ' + data.message, 'hideCustomAlert()');
                            }
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        showCustomAlert('خطا', 'خطا در ارسال اطلاعات', 'hideCustomAlert()');
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
LOGIN_HTML = """
<!DOCTYPE html>
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
                            showCustomAlert('خطا', data.message, 'hideCustomAlert()');
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        showCustomAlert('خطا', 'خطا در ورود', 'hideCustomAlert()');
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

@app.route('/')
def index():
    return REGISTRATION_HTML.replace('{% for city in cities %}', '').replace('{% endfor %}', '').replace('{{ city }}', CITIES[0] if CITIES else '')

@app.route('/register', methods=['POST'])
def register():
    global users
    data = request.get_json()
    username = data.get('username')
    city = data.get('city')
    phone = data.get('phone')
    password = data.get('password')
    
    # بررسی تکراری بودن نام کاربری یا شماره تلفن
    for user in users:
        if user['username'] == username:
            return jsonify({'success': False, 'message': 'نام کاربری تکراری است'})
        if user['phone'] == phone:
            return jsonify({'success': False, 'message': 'شماره تلفن تکراری است'})
    
    # هش کردن رمز عبور
    hashed_password = generate_password_hash(password)
    
    # ایجاد کاربر جدید
    new_user = {
        'id': str(uuid.uuid4()),
        'username': username,
        'city': city,
        'phone': phone,
        'password': hashed_password,
        'timestamp': data.get('timestamp')
    }
    
    users.append(new_user)
    save_data(users, DATA_FILE)
    
    return jsonify({'success': True, 'user': new_user})

@app.route('/login')
def login_page():
    return LOGIN_HTML

@app.route('/login', methods=['POST'])
def login():
    global users
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # جستجوی کاربر
    user = None
    for u in users:
        if u['username'] == username or u['phone'] == username:
            user = u
            break
    
    if user and check_password_hash(user['password'], password):
        return jsonify({'success': True, 'user': {'username': user['username']}})
    else:
        return jsonify({'success': False, 'message': 'نام کاربری یا رمز عبور اشتباه است'})

@app.route('/main')
def main_page():
    username = request.args.get('username')
    if not username:
        return redirect(url_for('login_page'))
    
    # پیدا کردن اطلاعات کاربر
    user = next((u for u in users if u['username'] == username), None)
    if not user:
        return redirect(url_for('login_page'))
    
    # بارگذاری مکان‌ها
    all_locations = load_data(LOCATIONS_FILE)
    
    # جایگزین کردن متغیرها در تمپلیت
    html = MAIN_HTML_TEMPLATE.replace('{{ username }}', user['username'])
    html = html.replace('{{ city }}', user['city'])
    html = html.replace('{{ phone }}', user['phone'])
    html = html.replace('{{ timestamp }}', user['timestamp'])
    
    # جایگزین کردن دسته‌بندی‌ها
    categories_html = ''
    for cat, subcats in CATEGORIES.items():
        categories_html += f'<option value="{cat}">{cat}</option>\n'
    html = html.replace('{% for cat in categories.keys() %}', '').replace('{% endfor %}', categories_html)
    
    # جایگزین کردن شهرها
    cities_html = ''
    for city in CITIES:
        cities_html += f'<option value="{city}">{city}</option>\n'
    html = html.replace('{% for city in cities %}', '').replace('{% endfor %}', cities_html)
    
    # جایگزین کردن مکان‌ها
    locations_html = ''
    for loc in all_locations:
        locations_html += f'''
        <div class="location-tile" onclick="showLocationDetails('{loc['id']}')">
            <div class="location-image" style="background-image: url('/uploads/{loc['photos'][0]}');"></div>
            <div class="location-info">
                <div class="location-title">{loc['title']}</div>
                <div class="location-city">{loc['city']}</div>
            </div>
        </div>
        '''
    html = html.replace('{% for loc in all_locations %}', '').replace('{% endfor %}', locations_html)
    
    # جایگزین کردن داده‌های دسته‌بندی برای جاوااسکریپت
    html = html.replace('{{ categories | tojson }}', json.dumps(CATEGORIES, ensure_ascii=False))
    html = html.replace('{{ all_locations | tojson }}', json.dumps(all_locations, ensure_ascii=False))
    
    return html

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/add_location', methods=['POST'])
def add_location():
    global locations
    # دریافت داده‌ها از فرم
    title = request.form.get('title')
    description = request.form.get('description')
    city = request.form.get('city')
    address = request.form.get('address')
    phone = request.form.get('phone')
    morning_shift = request.form.get('morning_shift')
    evening_shift = request.form.get('evening_shift')
    category = request.form.get('category')
    subcategory = request.form.get('subcategory')
    main_photo_index = int(request.form.get('main_photo', 0))
    
    # دریافت فایل‌های عکس
    photos = request.files.getlist('photos')
    photo_filenames = []
    
    for i, photo in enumerate(photos):
        if photo and photo.filename != '':
            filename = secure_filename(f"{uuid.uuid4()}_{photo.filename}")
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            photo_filenames.append(filename)
    
    # اطمینان از اینکه لیست عکس‌ها خالی نیست
    if not photo_filenames:
        return jsonify({'success': False, 'message': 'حداقل یک عکس الزامی است'})
    
    # اطمینان از اینکه عکس اصلی در محدوده صحیح است
    if main_photo_index >= len(photo_filenames):
        main_photo_index = 0
    
    # ایجاد مکان جدید
    new_location = {
        'id': str(uuid.uuid4()),
        'title': title,
        'description': description,
        'city': city,
        'address': address,
        'phone': phone,
        'morning_shift': morning_shift,
        'evening_shift': evening_shift,
        'category': category,
        'subcategory': subcategory,
        'photos': photo_filenames,
        'main_photo': main_photo_index,
        'owner': request.args.get('username'),  # دریافت نام کاربری از پارامترهای درخواست
        'timestamp': datetime.now().isoformat()
    }
    
    locations.append(new_location)
    save_data(locations, LOCATIONS_FILE)
    
    return jsonify({'success': True})

@app.route('/logout')
def logout():
    return redirect(url_for('login_page'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)