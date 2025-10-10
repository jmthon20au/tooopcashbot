import telebot
from telebot import types
import json
import os
import threading
import time
import pytz
from datetime import datetime, timedelta
timezone = pytz.timezone('Africa/Cairo')
owner = '@A_E20877' # يوزر المالك
FACTORY_RESET_PASSWORD = "ali"
bot_name = 'بوت توب كاش الاستثماري'   
TOKEN = "8467223117:AAGJvP6PGNqwRUEWyrbg2_o4m0VjpIUmNDU" # توكنك
ADMIN_ID = "5466254246" # ايدي الادمن (للوحة التحكم الرئيسية)
ADMINo_ID = 5466254246  # ايديك حتى تطلع عندك لوحة المتصدرين بالنقاط .
CHANNEL_ID = "5466254246"  # قناة الاشعارات الدخول
CHANNEL_ID2 = "-1003126012684" # قناة العدادات و القروض و التحويل و الوكلاء
CHANNEL_ID3 = "-1003161825371" #اثباتات السحب والمتجر 
WITHDRAWAL_ADMIN_ID = "8206491309" # آيدي المشرف المسؤول عن طلبات السحب والموافقة عليها (جديد)
bot = telebot.TeleBot(TOKEN)
user_transfer_data = {} 
TRANSFER_FEE = 5000 # عمولة التحويل الثابتة
SHOP_ADMIN_ID = "8206491309" #مشرف قسم المتجر
EDIT_FILE = 'edit.json'
coupon_temp_data = {} 
def load_edit_settings():
    """تحميل بيانات الإعدادات الإضافية من edit.json."""
    if not os.path.exists(EDIT_FILE):
        return {}
    try:
        # قراءة البيانات مع دعم UTF-8
        with open(EDIT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {} # إرجاع قاموس فارغ في حال وجود خطأ
def load_agents():
    """تحميل بيانات الوكلاء من agents.json."""
    if not os.path.exists(AGENTS_FILE):
        return {}
    try:
        # قراءة البيانات مع دعم UTF-8 للأحرف العربية
        with open(AGENTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {} # إرجاع قاموس فارغ في حال وجود خطأ في الملف

def save_agents(agents_data):
    """حفظ بيانات الوكلاء إلى agents.json."""
    # ensure_ascii=False للحفاظ على الأحرف العربية، و indent=4 للتنسيق
    with open(AGENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(agents_data, f, indent=4, ensure_ascii=False)
user_states = {} 
def initialize_files():
    """تهيئة الملفات JSON إذا لم تكن موجودة."""
    files = ["users.json", "products.json", "a.json", "edit.json", "config.json", "bot_status.json", "coupons.json", "withdrawals.json"]
    for filename in files:
        if not os.path.exists(filename):
            with open(filename, "w") as f:
                # إعطاء قيمة ابتدائية مناسبة لكل ملف
                if filename == "edit.json":
                    json.dump({"referral_points": 50}, f)
                elif filename == "config.json":
                    json.dump({"auto_send_enabled": True}, f)
                elif filename == "bot_status.json":
                    json.dump({"active": True, "reason": "البوت في وضع التشغيل", "resume_time": ""}, f)
                else:
                    json.dump({}, f)

initialize_files()
def load_json(filename):
    """تحميل البيانات من ملف JSON."""
    with open(filename, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_json(filename, data):
    """حفظ البيانات إلى ملف JSON."""
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

# دوال التحميل والحفظ المخصصة
def load_users(): return load_json("users.json")
def save_users(data): save_json("users.json", data)

def load_products(): return load_json("products.json")
def save_products(data): save_json("products.json", data)

def load_a_json(): 
    data = load_json("a.json")
    # التأكد من أن المفاتيح هي سلاسل نصية
    return {str(k): v for k, v in data.items()}

def save_a_json(data): save_json("a.json", data)

def load_edit(): return load_json("edit.json")
def save_edit(data): save_json("edit.json", data)

def load_config(): return load_json("config.json")
def save_config(data): save_json("config.json", data)

def load_bot_status(): return load_json("bot_status.json")
def save_bot_status(data): save_json("bot_status.json", data)

def load_coupons(): return load_json("coupons.json")
def save_coupons(data): save_json("coupons.json", data)

def load_withdrawals(): return load_json("withdrawals.json")
def save_withdrawals(data): save_json("withdrawals.json", data)

# --- منطق العداد التلقائي (الذي يستخدم ملف a.json) ---
def get_rank(points):
    """تحديد الرتبة بناءً على النقاط."""
    if points < 100: return "مبتدئ"
    elif points < 500: return "متوسط"
    elif points < 1000: return "متقدم"
    else: return "محترف"

def auto_add_points():
    """إضافة النقاط التلقائية من عداد a.json كل 5 ثوانٍ."""
    while True:
        try:
            config = load_config()
            if not config.get("auto_send_enabled", True):
                time.sleep(5)
                continue

            a_data = load_a_json()
            users = load_users()

            for uid, pts in a_data.items():
                if uid in users and pts > 0:
                    users[uid]["points"] += pts
                    try:
                        bot.send_message(uid, f"تمت إضافة {pts} نقطة إلى رصيدك من العداد التلقائي.\nرصيدك الحالي: {users[uid]['points']}\nتصنيفك: {get_rank(users[uid]['points'])}")
                    except Exception:
                        pass

            save_users(users)

        except Exception as e:
            print(f"خطأ في التحديث التلقائي: {e}")

        time.sleep(86400)

# تشغيل العداد في خلفية منفصلة
threading.Thread(target=auto_add_points, daemon=True).start()
# تشغيل مدقق القروض في خلفية منفصلة
import os
# ... (باقي الاستدعاءات)

# 🚨 هام: تأكد من أن متغير ADMIN_ID مُعرَّف
@bot.message_handler(func=lambda message: message.text == "📋 عرض جميع الإعدادات" and str(message.from_user.id) == ADMIN_ID)
def display_all_settings(message):
    chat_id = message.chat.id
    
    # 1. تحميل البيانات
    agents_data = load_agents() # استخدام دالة تحميل الوكلاء الموجودة
    settings_data = load_edit_settings()
    
    # 2. استخلاص القيم
    agents_count = len(agents_data)
    
    # قيم من ملف edit.json (افتراض أسماء المفاتيح)
    daily_gift = settings_data.get('daily_gift_points', 'غير محدد') 
    invite_link = settings_data.get('referral_points', 'غير محدد')
    
    # قيم من المتغيرات العامة (كما أرسلتها)
    bot_owner = owner
    bot_name_val = bot_name
    transfer_fee = TRANSFER_FEE 
    
    # 3. تنسيق رسالة الإعدادات (باستخدام HTML لتنسيق الغامق والنسخ)
    settings_message = (
        "⚙️ <b>جميع إعدادات البوت الحالية</b> ⚙️\n\n"
        
        "--- <b>معلومات البوت الأساسية</b> ---\n"
        f"<b>اسم البوت:</b> <code>{bot_name}</code>\n"
        f"<b>توكن البوت (TOKEN):</b> <code>{TOKEN}</code>\n"
        f"<b>يوزر المالك:</b> <code>{owner}</code>\n"
        f"<b>كلمة سر إعادة المصنع:</b> <code>{FACTORY_RESET_PASSWORD}</code>\n\n"
        
        "--- <b>آيديات المشرفين والقنوات</b> ---\n"
        f"<b>آيدي الأدمن الرئيسي (ADMIN_ID):</b> <code>{ADMIN_ID}</code>\n"
        f"<b>آيدي الأدمن (ADMINo_ID):</b> <code>{ADMINo_ID}</code>\n"
        f"<b>مشرف السحب (WITHDRAWAL_ADMIN_ID):</b> <code>{WITHDRAWAL_ADMIN_ID}</code>\n"
        f"<b>مشرف المتجر (SHOP_ADMIN_ID):</b> <code>{SHOP_ADMIN_ID}</code>\n"
        f"<b>قناة الإشعارات (CHANNEL_ID):</b> <code>{CHANNEL_ID}</code>\n"
        f"<b>قناة الشراء (CHANNEL_ID2):</b> <code>{CHANNEL_ID2}</code>\n"
        "--- <b>إعدادات النظام والوكلاء</b> ---\n"
        f"<b>عمولة التحويل الثابتة:</b> <code>{TRANSFER_FEE}</code> نقطة\n"
        f"<b>عدد الوكلاء النشطين:</b> <code>{agents_count}</code> وكيل\n\n"
        "--- <b>إعدادات الهدايا والدعوات (edit.json)</b> ---\n"
        f"<b>قيمة الهدية اليومية:</b> <code>{daily_gift}</code> نقطة\n"
        f"<b>رابط الدعوة:</b> <code>{invite_link}</code>\n"
    )
    
    # 4. إرسال الرسالة
    bot.send_message(chat_id, settings_message, parse_mode="HTML")
@bot.message_handler(func=lambda message: message.text == "📄 جلب الملفات" and str(message.from_user.id) == ADMIN_ID)
def send_all_files(message):
    chat_id = message.chat.id
    
    # قائمة بأسماء الملفات التي تريد إرسالها (يمكنك تعديل هذه القائمة)
    # الملفات التي عادة ما تهم المطور هي ملفات الكود (.py) وملفات التخزين (.json)
    files_to_send = [
        'main.py',   # ملف البوت الرئيسي
        'agents.json',   # ملف الوكلاء الذي نعدل عليه
        'users.json',    # ملف بيانات المستخدمين (إذا كان موجوداً لديك)
        'products.json',     # ملف السلع (إذا كان موجوداً لديك)
        'edit.json',
        'config.json',
        'loan.json',
        'withdrawals.json'
        'a.json'
    ]
    
    # وصف لكل ملف يتم إرساله
    file_descriptions = {
        'main.py': "ملف الكود الرئيسي للبوت الذي يحتوي على جميع الدوال والمعالجات.",
        'agents.json': "ملف قاعدة بيانات الوكلاء. يحتوي على آيدياتهم، أسمائهم، أدوارهم، وأرصدتهم وروابطهم.",
        'users.json': "ملف قاعدة بيانات المستخدمين (الأعضاء) يحتوي على نقاطهم ومعلوماتهم.",
        'products.json': "ملف قاعدة بيانات السلع المتوفرة في المتجر.",
        'edit.json': "الهدية اليومية و رابط الاحالة",
        'config.json': "ملف تشغيل ارسال العدادت",
        'loan.json': "ملف القروض ",
        'withdrawals.json': "ملف عمليات السحب",
        'a.json':  " ملفات عدادات المسثمرين"
    }

    files_found = 0
    bot.send_message(chat_id, "⏳ جاري محاولة جلب وإرسال الملفات المطلوبة...")

    for filename in files_to_send:
        if os.path.exists(filename):
            try:
                # محاولة فتح الملف وإرساله
                with open(filename, 'rb') as f:
                    # الحصول على الوصف أو استخدام وصف افتراضي
                    caption = f"📄 **اسم الملف:** `{filename}`\n\n**الوصف:** {file_descriptions.get(filename, 'لا يوجد وصف محدد لهذا الملف.')}"
                    
                    # استخدام send_document لإرسال الملف
                    bot.send_document(
                        chat_id, 
                        f, 
                        caption=caption, 
                        parse_mode="Markdown"
                    )
                    files_found += 1
            except Exception as e:
                # إبلاغ الأدمن إذا فشل إرسال ملف معين
                bot.send_message(chat_id, f"❌ **خطأ:** فشل إرسال ملف `{filename}`. السبب: {e}", parse_mode="Markdown")
        
    
    if files_found > 0:
        bot.send_message(chat_id, f"✅ **تم إرسال {files_found} ملف/ملفات بنجاح.**", parse_mode="Markdown")
    else:
        bot.send_message(chat_id, "⚠️ **تنبيه:** لم يتم العثور على أي من ملفات الكود أو قواعد البيانات في مسار تشغيل البوت.")
##
import sys 
# 🚨 هام: ضع هذا السطر لحل مشكلة الترميز بعد import sys
sys.stdout.reconfigure(encoding='utf-8') 
# ... باقي استيراداتك مثل telebot, threading, time, datetime, pytz ...

# --- 1. الثوابت وإدارة الملفات الجديدة (ضعها مع الثوابت الأخرى) ---
LOAN_TIERS = {
    # المفتاح:   الرصيد المطلوب (العداد),  مبلغ القرض (النقاط),   التسمية
    "L80K":   {"required": 1000, "loan_amount": 80000, "label": "80,000 نقطة"},
    "L120K":  {"required": 1500, "loan_amount": 120000, "label": "120,000 نقطة"},
    "L200K":  {"required": 2500, "loan_amount": 200000, "label": "200,000 نقطة"},
    "L400K":  {"required": 5000, "loan_amount": 400000, "label": "400,000 نقطة"},
    "L800K":  {"required": 10000, "loan_amount": 800000, "label": "800,000 نقطة"},
    "L2M":    {"required": 25000, "loan_amount": 2000000, "label": "2,000,000 نقطة"},
    "L4M":    {"required": 50000, "loan_amount": 4000000, "label": "4,000,000 نقطة"},
}
SUPPORT_LINK = "https://t.me/altaee_z" # رابط الدعم الفني الذي طلبته

# دوال التحميل والحفظ لملفات a.json و loan.json
def load_a(): 
    data = load_json("a.json")
    return {str(k): v for k, v in data.items()}

def save_a(data): 
    save_json("a.json", data)

def load_loans(): 
    data = load_json("loan.json")
    return {str(k): v for k, v in data.items()}

def save_loans(data): 
    save_json("loan.json", data)
    
# --- 2. قائمة القروض ومعالجات الأزرار (Callbacks) ---

@bot.callback_query_handler(func=lambda call: call.data == "loans_menu")
def loans_menu_callback(call):
    if not is_bot_active(call.message):
        return bot.answer_callback_query(call.id, "❌ البوت متوقف مؤقتاً.")
    
    user_id = str(call.from_user.id)
    a_data = load_a() 
    current_counter = a_data.get(user_id, 0)
    loans = load_loans()
    users = load_users()
    active_loans = [loan for loan in loans.get(user_id, []) if loan['status'] == 'active']
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    text = (
        "🏦 **قسم القروض والنقاط** 🏦\n\n"
        f"عدادك الحالي (a.json): **{current_counter:,} نقطة**\n"
        f"رصيدك الحالي (النقاط): **{users.get(user_id, {}).get('points', 0):,} نقطة**\n\n"
    )

    if active_loans:
        due_date_str = active_loans[0]['due_date']
        text += (f"⚠️ **لديك قرض نشط حالياً** بقيمة {active_loans[0]['amount']:,} نقطة.\n"
                 f"تاريخ الاستحقاق: {due_date_str}.\n\n"
                 f"لا يمكنك طلب قرض جديد حتى يتم تسديد القرض الحالي.")
        markup.add(types.InlineKeyboardButton("⬅️ رجوع للقائمة الرئيسية", callback_data="back_to_main_menu"))

    else:
        text += ("اختر القرض المناسب لك. يجب أن يكون عدادك الحالي **أعلى أو يساوي** العداد المطلوب. فترة التسديد: **30 يوماً**.")
        for key, loan_info in LOAN_TIERS.items():
            required = loan_info['required']
            if current_counter >= required:
                button_text = f"✅ قرض {loan_info['label']} (يتطلب عداد {required:,})"
                callback_data = f"confirm_loan:{key}" 
            else:
                button_text = f"❌ قرض {loan_info['label']} (يتطلب عداد {required:,})"
                callback_data = "no_action" 
            markup.add(types.InlineKeyboardButton(button_text, callback_data=callback_data))

        markup.add(types.InlineKeyboardButton("⬅️ رجوع للقائمة الرئيسية", callback_data="back_to_main_menu"))
    
    try:
        bot.edit_message_text(chat_id=call.message.chat.id, 
                              message_id=call.message.message_id,
                              text=text, 
                              reply_markup=markup,
                              parse_mode='Markdown')
    except telebot.apihelper.ApiTelegramException as e:
        if "message is not modified" not in str(e):
             bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode='Markdown')

    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_loan:"))
def confirm_loan_callback(call):
    user_id = str(call.from_user.id)
    _, loan_key = call.data.split(":")
    loan_info = LOAN_TIERS.get(loan_key)
    if not loan_info:
        return bot.answer_callback_query(call.id, "❌ خطأ في بيانات القرض.")

    required = loan_info['required']
    loan_amount = loan_info['loan_amount']
    loan_label = loan_info['label']

    a_data = load_a()
    current_counter = a_data.get(user_id, 0)
    
    if current_counter < required:
        bot.answer_callback_query(call.id, "❌ العداد غير كافٍ للحصول على هذا القرض.")
        return loans_menu_callback(call)

    text = (
        f"🚨 **تأكيد طلب قرض: {loan_label}** 🚨\n\n"
        f"**المبلغ الذي سيضاف إلى رصيدك (نقاط):** **{loan_amount:,} نقطة**\n"
        f"**العداد المطلوب (a.json):** {required:,} نقطة\n"
        f"**فترة التسديد:** 30 يوماً.\n\n" 
        "**ملاحظة هامة:** في تاريخ الاستحقاق، سيتم خصم **نفس مبلغ القرض** من نقاطك. إذا كانت نقاطك غير كافية، سيتم **حظر حسابك بشكل رسمي (banned: true)**."
    )
    
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton(f"✅ نعم، أحصل على {loan_label}", callback_data=f"take_loan:{loan_key}"),
        types.InlineKeyboardButton("❌ إلغاء والعودة", callback_data="loans_menu")
    )
    
    try:
        bot.edit_message_text(chat_id=call.message.chat.id, 
                              message_id=call.message.message_id,
                              text=text, 
                              reply_markup=markup,
                              parse_mode='Markdown')
    except Exception:
        bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode='Markdown')
        
    bot.answer_callback_query(call.id) 
    
    
@bot.callback_query_handler(func=lambda call: call.data.startswith("take_loan:"))
def take_loan_callback(call):
    user_id = str(call.from_user.id)
    _, loan_key = call.data.split(":")
    loan_info = LOAN_TIERS.get(loan_key)
    
    if not loan_info:
        return bot.answer_callback_query(call.id, "❌ خطأ في بيانات القرض.")

    required = loan_info['required']
    loan_amount = loan_info['loan_amount']
    
    users = load_users()
    loans = load_loans()
    u = users.get(user_id, {})
    
    active_loans = [loan for loan in loans.get(user_id, []) if loan['status'] == 'active']
    
    if active_loans:
        return bot.answer_callback_query(call.id, "❌ لديك قرض نشط مسبقاً. يرجى التسديد قبل طلب جديد.")

    # 1. تحديث رصيد المستخدم (إضافة مبلغ القرض)
    users[user_id] = users.get(user_id, {})
    users[user_id]['points'] = users[user_id].get('points', 0) + loan_amount
    save_users(users)
    
    issue_date = datetime.now(timezone)
    # 🚨 التعديل: تغيير المدة من دقيقة إلى 30 يوماً
    due_date = issue_date + timedelta(days=30) 
    
    # حفظ التاريخ بتنسيق يتضمن المنطقة الزمنية (%z)
    issue_date_str = issue_date.strftime('%Y-%m-%d %H:%M:%S%z') 
    due_date_str = due_date.strftime('%Y-%m-%d %H:%M:%S%z')
    
    # 2. تسجيل القرض في ملف loan.json
    loan_record = {
        "id": str(int(time.time() * 1000)),
        "user_id": user_id,
        "amount": loan_amount,
        "required_counter": required, 
        "issue_date": issue_date_str,
        "due_date": due_date_str, 
        "status": "active",
        "reminders_sent": 0 
    }
    
    if user_id not in loans:
        loans[user_id] = []
        
    loans[user_id].append(loan_record)
    save_loans(loans)

    # 3. إرسال إشعار للمستخدم وتحديث الرسالة
    msg_to_user = (
        f"🎉 **تم منحك قرض بنجاح!** 🎉\n\n"
        f"**المبلغ الممنوح:** **{loan_amount:,} نقطة**\n"
        f"**رصيدك الجديد:** **{users[user_id]['points']:,} نقطة**\n"
        f"**تاريخ الاستحقاق (التسديد):** {due_date.strftime('%Y-%m-%d | %H:%M:%S')}\n\n"
        "⚠️ سيتم خصم المبلغ تلقائياً في تاريخ الاستحقاق (بعد 30 يوماً). في حال عدم كفاية الرصيد، سيتم حظر حسابك."
    )
    
    try:
        bot.edit_message_text(f"🏦 **قسم القروض والنقاط** 🏦\n\n{msg_to_user}", 
                          call.message.chat.id, call.message.message_id, parse_mode='Markdown', 
                          reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("⬅️ العودة للقائمة", callback_data="back_to_main_menu")))
    except Exception:
        bot.send_message(call.message.chat.id, msg_to_user, parse_mode='Markdown')
        
    bot.answer_callback_query(call.id, "✅ تم الحصول على القرض بنجاح!")
    
    # 4. نشر العملية في قناة التحويلات (CHANNEL_ID2)
    user_name = u.get('name', 'مستخدم')
    username = u.get('username', 'لا يوجد')
    channel_msg = (
        f"💸 **عملية قرض جديدة (30 يوماً):**\n\n"
        f"**المقترض:** {user_name} (@{username})\n"
        f"**آيدي المقترض:** <code>{user_id}</code>\n"
        f"**مبلغ القرض:** {loan_amount:,} نقطة\n"
    )
    try:
        bot.send_message(CHANNEL_ID2, channel_msg, parse_mode="HTML")
    except Exception as e:
        print(f"فشل إرسال إشعار القرض إلى القناة: {e}")

# --- 3. دالة فحص وتسديد القروض الخلفية (Loan Repayment Checker) ---

def loan_repayment_checker():
    """التحقق من مواعيد استحقاق القروض (الخصم أو الحظر) وإرسال التذكيرات."""
    while True:
        try:
            loans = load_loans()
            users = load_users()
            now = datetime.now(timezone).replace(microsecond=0)
            
            loans_modified = False
            users_modified = False
            new_loans_data = {} 
            
            for user_id, user_loans in loans.items():
                updated_user_loans = []
                
                for loan in user_loans:
                    
                    if loan['status'] == 'active':
                        due_date_str = loan['due_date']
                        
                        # قراءة التاريخ بتنسيق المنطقة الزمنية
                        due_date = datetime.strptime(due_date_str, '%Y-%m-%d %H:%M:%S%z') 
                        
                        loan_amount = loan['amount']
                        time_to_due = due_date - now
                        
                        # 1. إرسال التذكير (قبل 24 ساعة) - يمكنك إزالة هذا الجزء أو تعديل مدته لاحقاً
                        if timedelta(hours=1) < time_to_due <= timedelta(days=1, minutes=5) and loan.get('reminders_sent', 0) == 0:
                             # منطق إرسال التذكير (يمكنك وضع الكود هنا)
                            try:
                                bot.send_message(user_id, 
                                                f"⚠️ **تذكير: موعد تسديد القرض يقترب!** ⚠️\n\n"
                                                f"يستحق سداد قرضك البالغ **{loan_amount:,} نقطة** خلال أقل من 24 ساعة.\n"
                                                "يرجى التأكد من أن رصيدك كافٍ لتجنب الحظر.", 
                                                parse_mode='Markdown')
                                loan['reminders_sent'] = 1
                                loans_modified = True
                            except Exception: pass
                        
                        # 2. معالجة الاستحقاق (تاريخ الاستحقاق أو تجاوزه)
                        if now >= due_date:
                            
                            if user_id in users:
                                user_points = users[user_id].get('points', 0)
                                user_data = users[user_id]
                                user_name = user_data.get('name', 'مستخدم')
                                username = user_data.get('username', 'لا يوجد')
                                
                                # أ. حالة النقاط كافية: الخصم والتسديد
                                if user_points >= loan_amount:
                                    users[user_id]['points'] -= loan_amount
                                    loan['status'] = 'paid'
                                    users_modified = True
                                    loans_modified = True
                                    
                                    # إشعار للمستخدم
                                    try:
                                        bot.send_message(user_id, 
                                                         f"✅ **تم تسديد القرض بنجاح!** ✅\n\nتم خصم **{loan_amount:,} نقطة** تلقائياً.\nرصيدك الحالي: **{users[user_id]['points']:,} نقطة**.", 
                                                         parse_mode='Markdown')
                                    except Exception: pass
                                        
                                    # إشعار للقناة
                                    channel_msg = (
                                        f"💰 **تم تسديد قرض:**\n\n**المستخدم:** {user_name} (@{username})\n**آيدي:** <code>{user_id}</code>\n**المبلغ المسدد:** {loan_amount:,} نقطة"
                                    )
                                    bot.send_message(CHANNEL_ID2, channel_msg, parse_mode="HTML")
                                    
                                # ب. حالة النقاط غير كافية: الحظر
                                else:
                                    loan['status'] = 'defaulted'
                                    loans_modified = True
                                    
                                    # تعيين الحظر في users.json
                                    users[user_id]['banned'] = True 
                                    users_modified = True
                                    
                                    # إشعار للمستخدم
                                    ban_message = (
                                        f"🚫 **تم حظر حسابك!** 🚫\n\n**السبب:** عدم تسديد القرض المستحق بقيمة **{loan_amount:,} نقطة**.\n"
                                        f"رصيدك الحالي: {user_points:,} نقطة (غير كافٍ).\n"
                                        f"لرفع الحظر تواصل مع **الدعم الفني**."
                                    )
                                    markup_ban = types.InlineKeyboardMarkup()
                                    markup_ban.add(types.InlineKeyboardButton("💬 الدعم الفني", url=SUPPORT_LINK))
                                    
                                    try:
                                        bot.send_message(user_id, ban_message, parse_mode='Markdown', reply_markup=markup_ban)
                                    except Exception: pass
                                        
                                    # إشعار للقناة
                                    channel_msg = (
                                        f"🚨 **حظر بسبب عدم التسديد!** 🚨\n\n**المستخدم:** {user_name} (@{username})\n**آيدي:** <code>{user_id}</code>\n**مبلغ القرض:** {loan_amount:,} نقطة"
                                    )
                                    bot.send_message(CHANNEL_ID2, channel_msg, parse_mode="HTML")
                        
                    updated_user_loans.append(loan)

                new_loans_data[user_id] = updated_user_loans
                
            if loans_modified:
                save_loans(new_loans_data)
                
            if users_modified:
                save_users(users)
                
        except Exception as e:
            # هذا السطر مهم للإبقاء عليه لمعرفة أي خطأ غير متوقع
            print(f"خطأ غير متوقع في التحقق من القروض: {e}")

        # فترة التحديث: 3 ثواني
        time.sleep(3) 

# --- 4. سطر تشغيل الدالة (يجب أن يكون في نهاية الملف) ---

# 🚨 هام: هذا السطر لتشغيل الفحص الخلفي
# threading.Thread(target=loan_repayment_checker, daemon=True).start()          
##       
def get_badge(user_data):
    """تحديد الشارة بناءً على الإحصائيات."""
    if user_data.get('referrals', 0) >= 50: return "أسطورة الدعوات"
    elif user_data.get('purchases', 0) >= 10: return "مسوّق ذهبي"
    elif user_data.get('points', 0) >= 500: return "صاحب نقاط"
    else: return "مستخدم عادي"

def update_user_rank(user_id):
    """دالة وهمية يمكن استخدامها لتحديث حالة المستخدم إذا لزم الأمر."""
    pass
    

    
def is_bot_active(message):
    """التحقق من حالة إيقاف/تشغيل البوت."""
    status = load_bot_status()
    if not status.get("active", True):
        bot.send_message(
            message.chat.id,
            f"❌ البوت متوقف مؤقتاً.\nالسبب: {status.get('reason', 'غير معروف')}\nيعود للعمل في: {status.get('resume_time', 'غير معروف')}"
        )
        return False
    return True
    
# --- الأزرار الشفافة الجديدة (Main Menu) ---
def get_main_menu_markup(user_id):
    """إنشاء أزرار المنيو الرئيسية الشفافة."""
    main_menu_markup = types.InlineKeyboardMarkup(row_width=2)
    users = load_users()
    u = users.get(str(user_id), {})
    
    # تحديد نص زر الهدية اليومية
    gift_text = "🎁 الهدية اليومية"
    if u.get("last_claim"):
        try:
            last_claim_time = datetime.strptime(u["last_claim"], "%Y-%m-%d %H:%M:%S")
            time_diff = datetime.now() - last_claim_time
            if time_diff < timedelta(days=1):
                time_remaining = timedelta(days=1) - time_diff
                hours_left, remainder = divmod(time_remaining.seconds, 3600)
                minutes_left, _ = divmod(remainder, 60)
                gift_text = f"🎁 متبقي: {hours_left} س {minutes_left} د"
        except Exception:
            pass

    main_menu_markup.add(
        types.InlineKeyboardButton("شراء عداد", callback_data="show_products_menu"),
        types.InlineKeyboardButton("مشترياتي", callback_data="show_purchases_inline"),
        types.InlineKeyboardButton("اهداء عداد", callback_data="gift_counter")
    )
    main_menu_markup.add(
    )
    main_menu_markup.add(
        types.InlineKeyboardButton("🛒 المتجر الالكتروني", callback_data="shop_menu"),
        types.InlineKeyboardButton("اعرض سلعتك", callback_data="offer")
    )
    main_menu_markup.add(
        types.InlineKeyboardButton(gift_text, callback_data="claim_daily_gift_inline"),
        types.InlineKeyboardButton("تجربة الكوبون", callback_data="ask_for_coupon_inline"),

        
    )
    main_menu_markup.add(
        types.InlineKeyboardButton("⬅️ تحويل نقاط ➡️", callback_data="transfer_points_inline"),
        types.InlineKeyboardButton("الوكلاء", callback_data="show_agents_list"),
        types.InlineKeyboardButton("💵 القروض 💵", callback_data="loans_menu") 
    )         
    main_menu_markup.add(
        types.InlineKeyboardButton("💰 سحب أرباحي", callback_data="withdrawal_menu"),
        types.InlineKeyboardButton("الاثباتات", url="https://t.me/Topcash124")
    )        

    main_menu_markup.add(
        types.InlineKeyboardButton("الاحكام و السياسات", callback_data="about_us_inline"),
        types.InlineKeyboardButton("الضمانات", callback_data="guarantees")
    )
    main_menu_markup.add(
        types.InlineKeyboardButton("💬 الدعم الفني", url="https://t.me/Topcash121"),
        types.InlineKeyboardButton("📢 القناة", url="https://t.me/topcash2005")
    )
   
    return main_menu_markup

WITHDRAWAL_METHODS = {
    #mastercaed
    "mastercard_10": {"label": "ماستركارد 10$", "amount": 10, "cost": 50000, "fields": ["card_long", "card_short"]},
    "mastercard_25": {"label": "ماستركارد 25$", "amount": 25, "cost": 125000, "fields": ["card_long", "card_short"]},
    "mastercard_50": {"label": "ماستركارد 50$", "amount": 50, "cost": 250000, "fields": ["card_long", "card_short"]},
    "mastercard_100": {"label": "ماستركارد 100$", "amount": 100, "cost": 500000, "fields": ["card_long", "card_short"]},
    "mastercard_150": {"label": "ماستركارد 150$", "amount": 150, "cost": 750000, "fields": ["card_long", "card_short"]},
    #zaincash
    "zaincash_10": {"label": "زين كاش 10$", "amount": 10, "cost": 55000, "fields": ["phone"]},
    "zaincash_25": {"label": "زين كاش 25$", "amount": 25, "cost": 137000, "fields": ["phone"]},
    "zaincash_50": {"label": "زين كاش 50$", "amount": 50, "cost": 275000, "fields": ["phone"]},
    "zaincash_100": {"label": "زين كاش 100$", "amount": 100, "cost": 550000, "fields": ["phone"]},
    "zaincash_150": {"label": "زين كاش 150$", "amount": 150, "cost": 825000, "fields": ["phone"]},
    #ather
    "ether_balance_5": {"label": "رصيد اثير 5$", "amount": 5, "cost": 23000, "fields": ["phone"]},
    "ether_balance_10": {"label": "رصيد اثير 10$", "amount": 10, "cost": 45000, "fields": ["phone"]},
    "ether_balance_15": {"label": "رصيد اثير 15$", "amount": 15, "cost": 67000, "fields": ["phone"]},
    #asia
    "asia_balance_5": {"label": "رصيد اسيا 5$", "amount": 5, "cost": 24000, "fields": ["phone"]},
    "asia_balance_10": {"label": "رصيد اسيا 10$", "amount": 10, "cost": 46000, "fields": ["phone"]},
    "asia_balance_15": {"label": "رصيد اسيا 15$", "amount": 15, "cost": 67500, "fields": ["phone"]},
    #USDT
    "usdt_okx_10": {"label": "USDT 10$ (OKX - TRC20)", "amount": 10, "cost": 60000, "fields": ["okx_id", "trc20_address"]},
    "usdt_okx_25": {"label": "USDT 25$ (OKX - TRC20)", "amount": 25, "cost": 135000, "fields": ["okx_id", "trc20_address"]},
    "usdt_okx_50": {"label": "USDT 50$ (OKX - TRC20)", "amount": 50, "cost": 260000, "fields": ["okx_id", "trc20_address"]},
    
}

# مسارات نصوص الحقول (للسؤال)
FIELD_PROMPTS = {
    "card_long": "الرجاء إرسال **الماستر كارد الطويل** (رقم البطاقة الكامل):",
    "card_short": "الرجاء إرسال **الماستر كارد القصير (CVV/CVC)**:",
    "phone": "الرجاء إرسال **رقم الهاتف** المرتبط بطريقة السحب (مثال: 964771XXXXXXX):",
    "okx_id": "الرجاء إرسال **آيدي حسابك في منصة OKX**:",
    "trc20_address": "الرجاء إرسال **عنوان محفظة TRC20** لاستلام USDT:",
}
user_purchase_data = {}         # لحفظ بيانات المستخدم أثناء تجميع الحقول
pending_purchase_requests = {}  # لطلبات الشراء المعلقة بانتظار موافقة المشرف
user_rejection_data = {}        # لحفظ بيانات الرفض المؤقتة للمشرف
STORE_PRODUCTS = {
    # خدمات تلجرام - تلجرام مميز
    "premium_3m": {
        "label": "اشتراك تلجرام مميز (3 أشهر)", "cost": 80000, "category": "telegram",
        "fields": ["telegram_username"], "admin_id": SHOP_ADMIN_ID 
    },
    "premium_6m": {
        "label": "اشتراك تلجرام مميز (6 أشهر)", "cost": 106000, "category": "telegram",
        "fields": ["telegram_username"], "admin_id": SHOP_ADMIN_ID 
    },
    "premium_12m": {
        "label": "اشتراك تلجرام مميز (سنة كاملة)", "cost": 187000, "category": "telegram",
        "fields": ["telegram_username"], "admin_id": SHOP_ADMIN_ID 
    },
    
    # خدمات تلجرام - نجوم تلجرام (المتطلب: يوزر أو رابط منشور)
    "stars_100": {
        "label": "نجوم تلجرام (100 نجمة)", "cost": 13000, "category": "telegram",
        "fields": ["telegram_user_or_link"], "admin_id": SHOP_ADMIN_ID
    },
    "stars_500": {
        "label": "نجوم تلجرام (500 نجمة)", "cost": 13000, "category": "telegram",
        "fields": ["telegram_user_or_link"], "admin_id": SHOP_ADMIN_ID
    },
    "stars_1000": {
        "label": "نجوم تلجرام (1000 نقطة)", "cost": 127000, "category": "telegram",
        "fields": ["telegram_user_or_link"], "admin_id": SHOP_ADMIN_ID
    },
    
    # شحن ألعاب - شدات ببجي (المتطلب: آيدي واسم اللعبة)
    "pubg_120uc": {
        "label": "شدات ببجي (120 شدة)", "cost": 17000, "category": "games",
        "fields": ["game_id", "game_name"], "admin_id": SHOP_ADMIN_ID
    },
    "pubg_180uc": {
        "label": "شدات ببجي (180 شدة)", "cost": 25000, "category": "games",
        "fields": ["game_id", "game_name"], "admin_id": SHOP_ADMIN_ID
    },
    "pubg_336uc": {
        "label": "شدات ببجي (336 شدة)", "cost": 40000, "category": "games",
        "fields": ["game_id", "game_name"], "admin_id": SHOP_ADMIN_ID
    },
    "pubg_688uc": {
        "label": "شدات ببجي (688 شدة)", "cost": 62000, "category": "games",
        "fields": ["game_id", "game_name"], "admin_id": SHOP_ADMIN_ID
    },
    "pubg_1170uc": {
        "label": "شدات ببجي (1170 شدة)", "cost": 110000, "category": "games",
        "fields": ["game_id", "game_name"], "admin_id": SHOP_ADMIN_ID
    },
}
##
# دوال إهداء عداد بصيغة رقمية في a.json (ID: number)
# تم إزالة التاريخ والوقت تمامًا من جميع الرسائل

GIFT_FEE_PERCENTAGE = 0.20  # 20% عمولة
MIN_GIFT_AMOUNT = 100        # حد أدنى للإهداء
user_gift_data = {}

import json, os

def load_counters():
    if not os.path.exists('a.json'):
        return {}
    try:
        with open('a.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        return {}

    counters = {}
    for k, v in data.items():
        if isinstance(v, (int, float, str)):
            try:
                counters[str(k)] = int(v)
            except Exception:
                counters[str(k)] = 0
        elif isinstance(v, dict) and 'counter' in v:
            counters[str(k)] = int(v.get('counter', 0))
        else:
            counters[str(k)] = 0
    return counters

def save_counters(counters):
    safe = {str(k): int(v) for k, v in counters.items()}
    with open('a.json', 'w', encoding='utf-8') as f:
        json.dump(safe, f, indent=4, ensure_ascii=False)

def get_main_reply_keyboard():
    return types.ReplyKeyboardRemove()

@bot.callback_query_handler(func=lambda call: call.data == 'gift_counter')
def handle_gift_counter_inline_start(call):
    bot.answer_callback_query(call.id)
    sender_id = str(call.message.chat.id)

    counters = load_counters()
    current_balance = counters.get(sender_id, 0)

    if current_balance < MIN_GIFT_AMOUNT:
        bot.send_message(call.message.chat.id, f"❌ لا يمكنك الإهداء إذا كان رصيدك أقل من {MIN_GIFT_AMOUNT} عداد.")
        return

    user_gift_data[sender_id] = {'target_id': None}
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('إلغاء الإهداء'))

    bot.send_message(call.message.chat.id,
                     f"رصيدك الحالي: {current_balance}\nأرسل آيدي المستخدم الذي تريد إهداءه.",
                     reply_markup=markup)
    bot.register_next_step_handler(call.message, process_target_id_gift)

def process_target_id_gift(message):
    sender_id = str(message.chat.id)

    if message.text == 'إلغاء الإهداء':
        user_gift_data.pop(sender_id, None)
        bot.send_message(message.chat.id, '✅ تم إلغاء عملية الإهداء.', reply_markup=get_main_reply_keyboard())
        return

    target_id = message.text.strip()
    if not target_id.isdigit() or target_id == sender_id:
        bot.send_message(message.chat.id, '❌ الآيدي غير صالح. أرسل آيدي صحيح لمستخدم آخر.')
        bot.register_next_step_handler(message, process_target_id_gift)
        return

    counters = load_counters()
    if target_id not in counters:
        bot.send_message(message.chat.id, f"⚠️ لم يتم العثور على آيدي {target_id} في a.json — سيتم إضافته تلقائياً عند الإهداء.")

    user_gift_data[sender_id]['target_id'] = target_id
    bot.send_message(message.chat.id, f"✅ تم تحديد المستلم (آيدي: {target_id}).\nأرسل كمية العدادات التي تريد إهداءها (الحد الأدنى {MIN_GIFT_AMOUNT}).", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, process_amount_gift)

def process_amount_gift(message):
    sender_id = str(message.chat.id)

    if message.text == 'إلغاء الإهداء':
        user_gift_data.pop(sender_id, None)
        bot.send_message(message.chat.id, '✅ تم إلغاء عملية الإهداء.', reply_markup=get_main_reply_keyboard())
        return

    try:
        amount = int(message.text.strip())
    except Exception:
        bot.send_message(message.chat.id, '❌ يجب إدخال رقم صحيح.')
        bot.register_next_step_handler(message, process_amount_gift)
        return

    if amount < MIN_GIFT_AMOUNT:
        bot.send_message(message.chat.id, f"❌ الحد الأدنى للإهداء هو {MIN_GIFT_AMOUNT} عداد.")
        bot.register_next_step_handler(message, process_amount_gift)
        return

    counters = load_counters()
    sender_balance = counters.get(sender_id, 0)
    target_id = user_gift_data.get(sender_id, {}).get('target_id')

    if not target_id:
        bot.send_message(message.chat.id, '❌ لم يتم تحديد المستلم. ابدأ العملية من جديد.')
        user_gift_data.pop(sender_id, None)
        return

    fee = int(amount * GIFT_FEE_PERCENTAGE)
    total = amount + fee

    if total > sender_balance:
        bot.send_message(message.chat.id, f"❌ رصيدك غير كافٍ. تحتاج إلى {total} عداد (المبلغ + عمولة 20%).")
        user_gift_data.pop(sender_id, None)
        return

    sender_old = sender_balance
    target_old = counters.get(target_id, 0)

    counters[sender_id] = sender_balance - total
    counters[target_id] = counters.get(target_id, 0) + amount

    save_counters(counters)

    sender_new = counters[sender_id]
    target_new = counters[target_id]

    sender_name = message.from_user.first_name or 'مستخدم'
    sender_username = message.from_user.username or 'غير متوفر'

    bot.send_message(message.chat.id,
                     f"🎉 تم الإهداء بنجاح!\n\n💸 المبلغ: {amount}\n💰 العمولة: {fee}\n💳 رصيدك السابق: {sender_old}\n💵 رصيدك الجديد: {sender_new}",
                     reply_markup=get_main_reply_keyboard())

    try:
        bot.send_message(int(target_id),
                         f"🎁 تم إهداؤك {amount} عداد من {sender_name} (آيدي: {sender_id})!\n\n💰 رصيدك السابق: {target_old}\n➕ المبلغ المضاف: {amount}\n💸 عمولة المرسل: {fee}\n💳 رصيدك الجديد: {target_new}")
    except Exception:
        pass

    try:
        bot.send_message(CHANNEL_ID2,
                         f"🎁 عملية إهداء عداد:\n👤 المُهدي: {sender_name} (@{sender_username}) [آيدي: {sender_id}]\n🎯 المستلم: [آيدي: {target_id}]\n💸 الكمية: {amount}\n💰 العمولة: {fee}\n💳 رصيد المستلم قبل: {target_old}\n💳 بعد: {target_new}", parse_mode='HTML')
    except Exception:
        pass

    user_gift_data.pop(sender_id, None)

##
@bot.callback_query_handler(func=lambda call: call.data == "offer")
def send_offer_item_info(call):
    """معالجة ضغطة زر 'اعرض سلعتك' لإظهار النص والروابط."""
    
    # النص الذي سيظهر للمستخدم
    message_text = (
    "🛍️ **اعرض سلعتك الآن بكل حرية!**\n\n"
    "مقابل **500 توب فقط**، احصل على فرصة عرض سلعتك لمدة **24 ساعة كاملة** داخل المنصة ✨\n"
    "بشكل مميز، بدون أي قيود أو شروط — **اجعل الجميع يشاهد منتجك الآن** 🚀"
    )
    
    # إنشاء الأزرار
    markup = types.InlineKeyboardMarkup()
    
    # 1. زر الرابط (القناة)
    btn_channel_link = types.InlineKeyboardButton("📤 مراسلة القناة", url="https://t.me/Topcash128") 
    
    # 2. زر الرجوع
    btn_back = types.InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main_menu")
    
    # إضافة الأزرار في سطرين منفصلين
    markup.add(btn_channel_link) 
    markup.add(btn_back) 
    
    try:
        # تعديل رسالة المنيو الحالية بالنص الجديد والأزرار
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=message_text,
            reply_markup=markup,
            parse_mode='Markdown'
        )
    except Exception:
        # في حال فشل التعديل، نرسل رسالة جديدة
        bot.send_message(
            call.message.chat.id,
            text=message_text,
            reply_markup=markup,
            parse_mode='Markdown'
        )
        
    bot.answer_callback_query(call.id)
@bot.callback_query_handler(func=lambda call: call.data == "guarantees")
def guarantees_callback_handler(call):
    """معالجة ضغط زر الضمانات."""
    try:
        send_guarantees_message(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"Error handling guarantees: {e}")
def get_guarantees_markup():
    """إنشاء لوحة مفاتيح وزر الرجوع لرسالة الضمانات."""
    markup = types.InlineKeyboardMarkup()
    # يتم افتراض أن زر الضمانات موجود في القائمة الرئيسية (main_menu)، 
    # إذا كانت القائمة السابقة مختلفة، يرجى تغيير callback_data إلى ما يناسبك.
    markup.add(types.InlineKeyboardButton("➡️ رجوع", callback_data="back_to_main_menu")) 
    return markup

def send_guarantees_message(chat_id, message_id):
    """إرسال رسالة شروط وأحكام الضمانات."""
    
    # النص التفصيلي كما طلبته
    guarantees_text = (
        "📑 **شروط وأحكام عقد الاستثمار المضمون – مختصر**\n\n"
        "1️⃣ **مدة العقد:** الاستثمار لمدة سنة واحدة فقط.\n\n"
        "2️⃣ **الضمان:** الإدارة تلتزم بضمان قانوني وإلكتروني لمدة سنة عبر المالك مباشرة.\n\n"
        "3️⃣ **التحويلات المالية:** لا تتجاوز قيمة التحويلات 💸 **10,000 نقطة** خلال فترة العقد، ويجوز زيادتها فقط بموافقة خطية مسبقة من إدارة البوت.\n\n"
        "4️⃣ **نشاط الحساب:** يجب أن يكون الحساب 📲 نشط خلال آخر 45 يوم من توقيع العقد.\n\n"
        "5️⃣ **الأرباح:** تصرف شهريًا 💵 بالدينار أو الدولار 💲 أو تحفظ بالبوت.\n\n"
        "6️⃣ **الالتزامات:** المستثمر لا يطالب بأرباح إضافية خارج العقد، والإدارة غير مسؤولة ⚠️ عن خسائر بسبب مخالفته.\n\n"
        "7️⃣ **المخاطر:** الأرباح غير ثابتة 📉 وتعتمد على نشاط الحساب، مع **ضمان أصل رأس المال فقط**.\n\n"
        "8️⃣ **فسخ العقد:** يمكن لأي طرف فسخ العقد بشرط إشعار مسبق ⏳ قبل 30 يوم.\n\n"
        "9️⃣ **القوانين:** العقد يخضع ⚖️ للقوانين المحلية النافذة.\n\n"
        "🔟 **فائدة الضمان:**\n"
        "في حال حدوث ظروف طارئة 🚨 أو توقف المشروع لأي سبب (مثل مشاكل السيولة 💧، إيقاف النشاط من قبل الجهات الرسمية 🏛️، أو أي عارض خارج عن إرادة الإدارة)، فإن الاستثمار بالضمان يضمن للمستثمر ✅ حقه الاستثماري السنوي وفق الشروط والأحكام المذكورة أعلاه، دون أن يمتد إلى التزامات إضافية خارج إطار العقد.\n\n\n"
        "🔹 **ملاحظة:** هذا العداد يختلف عن العداد العادي. عند شرائك لأول مرة يجب إبلاغ الوكيل بأنك تريد استثمار بالضمان، ليتم تفعيل العداد وتسجيلك في الضمان."
    )
    
    bot.edit_message_text(
        chat_id=chat_id, 
        message_id=message_id, 
        text=guarantees_text, 
        reply_markup=get_guarantees_markup(),
        parse_mode="Markdown"
    )        
@bot.callback_query_handler(func=lambda call: call.data == 'show_agents_list')
def show_agents_list(call):
    agents = load_agents()
    
    if not agents:
        bot.answer_callback_query(call.id, "❌ لا يوجد وكلاء متاحون حالياً.")
        return

    agents_list_markup = types.InlineKeyboardMarkup()

    # إنشاء زر لكل وكيل
    for agent_id, agent_data in agents.items():
        button_text = f"👤 {agent_data['name']} ({agent_data['role']})"
        # هذا الزر سيحمل آيدي الوكيل لمعرفة معلوماته
        callback_data = f"agent_details_{agent_id}" 
        agents_list_markup.add(
            types.InlineKeyboardButton(button_text, callback_data=callback_data)
        )
        
    # زر للعودة إلى القائمة الرئيسية (افترضنا أن لديك دالة /start أو ما شابه)
    agents_list_markup.add(
        types.InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_main_menu")
    )

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="👥 **اختر الوكيل الذي تود التواصل معه:**",
        reply_markup=agents_list_markup,
        parse_mode="Markdown"
    )
@bot.callback_query_handler(func=lambda call: call.data.startswith('agent_details_'))
def show_agent_details(call):
    # استخلاص آيدي الوكيل من بيانات الزر (مثال: agent_details_1234567890)
    agent_id = call.data.split('_')[2]
    agents = load_agents()
    
    if agent_id in agents:
        agent = agents[agent_id]
        
        # التأكد من وجود الروابط
        account_link = agent.get('account_link', 'https://t.me/NOT_AVAILABLE')
        channel_link = agent.get('channel_link', 'https://t.me/NOT_AVAILABLE')
        
        message_text = (
            f"**معلومات الوكيل: {agent['name']}**\n\n"
            f"**الدور:** {agent['role']}\n"
        )
        
        # إنشاء أزرار روابط مباشرة
        details_markup = types.InlineKeyboardMarkup(row_width=1)
        
        # إضافة زر رابط الحساب
        details_markup.add(
            types.InlineKeyboardButton("📞 التواصل مع الوكيل (حسابه)", url=account_link)
        )
        
        # إضافة زر رابط القناة
        details_markup.add(
            types.InlineKeyboardButton("📺 قناة الوكيل", url=channel_link)
        )
        
        # زر للعودة لقائمة الوكلاء
        details_markup.add(
            types.InlineKeyboardButton("🔙 رجوع لقائمة الوكلاء", callback_data="show_agents_list")
        )
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=message_text,
            reply_markup=details_markup,
            parse_mode="Markdown"
        )
    else:
        bot.answer_callback_query(call.id, "❌ لم يتم العثور على معلومات هذا الوكيل.")    
##
@bot.message_handler(func=lambda message: message.text == "انشاء كوبون" and str(message.chat.id) == ADMIN_ID)
def start_create_coupon(message):
    """بدء عملية إنشاء الكوبون وطلب الرمز."""
    global coupon_temp_data
    # مسح أي بيانات سابقة
    if message.chat.id in coupon_temp_data:
        del coupon_temp_data[message.chat.id]
        
    msg = bot.send_message(message.chat.id, "⬇️ **لإنشاء كوبون جديد (الخطوة 1/4):**\nالرجاء إرسال **رمز الكوبون** (مثال: SALE2024).")
    bot.register_next_step_handler(msg, get_coupon_code)

def get_coupon_code(message):
    """الخطوة 2/4: استلام رمز الكوبون وطلب عدد النقاط."""
    global coupon_temp_data
    admin_id = message.chat.id
    code = message.text.strip()
    
    # تحقق من وجود الرمز بالفعل
    if code in load_coupons():
        msg = bot.send_message(admin_id, "❌ هذا الرمز موجود بالفعل. الرجاء إرسال **رمز كوبون** جديد.")
        bot.register_next_step_handler(msg, get_coupon_code)
        return
        
    coupon_temp_data[admin_id] = {'code': code}
    
    msg = bot.send_message(admin_id, f"✅ تم حفظ الرمز: **{code}**.\n\n**الخطوة 2/4:** كم هي **عدد النقاط** التي يمنحها الكوبون؟")
    bot.register_next_step_handler(msg, get_coupon_points)

def get_coupon_points(message):
    """الخطوة 3/4: استلام عدد النقاط وطلب الحد الأقصى للاستخدام."""
    global coupon_temp_data
    admin_id = message.chat.id
    
    if admin_id not in coupon_temp_data:
        bot.send_message(admin_id, "❌ خطأ في العملية. الرجاء البدء من جديد.")
        return
        
    try:
        points = int(message.text.strip())
        if points <= 0: raise ValueError
    except ValueError:
        msg = bot.send_message(admin_id, "❌ عدد النقاط يجب أن يكون رقماً صحيحاً وموجباً. حاول مرة أخرى.")
        bot.register_next_step_handler(msg, get_coupon_points)
        return
        
    coupon_temp_data[admin_id]['points'] = points
    
    msg = bot.send_message(admin_id, f"✅ تم حفظ النقاط: {points}.\n\n**الخطوة 3/4:** كم هو **الحد الأقصى لعدد المستخدمين** الذين يمكنهم استخدام الكوبون؟")
    bot.register_next_step_handler(msg, get_coupon_max_uses)

def get_coupon_max_uses(message):
    """الخطوة 4/4: استلام الحد الأقصى للاستخدام وطلب مدة الانتهاء."""
    global coupon_temp_data
    admin_id = message.chat.id
    
    if admin_id not in coupon_temp_data:
        bot.send_message(admin_id, "❌ خطأ في العملية. الرجاء البدء من جديد.")
        return

    try:
        max_uses = int(message.text.strip())
        if max_uses <= 0: raise ValueError
    except ValueError:
        msg = bot.send_message(admin_id, "❌ الحد الأقصى يجب أن يكون رقماً صحيحاً وموجباً. حاول مرة أخرى.")
        bot.register_next_step_handler(msg, get_coupon_max_uses)
        return
        
    coupon_temp_data[admin_id]['max_uses'] = max_uses
    
    # الطلب الأخير: مدة الانتهاء بالساعات أو الأيام
    msg = bot.send_message(admin_id, f"✅ تم حفظ الحد الأقصى: {max_uses}.\n\n**الخطوة الأخيرة:** كم هي **مدة صلاحية الكوبون**؟\n(مثال: **7d** لـ 7 أيام، أو **48h** لـ 48 ساعة).\nإذا لم ترد تعيين مدة، أرسل 0.")
    bot.register_next_step_handler(msg, get_coupon_expiry)

def get_coupon_expiry(message):
    """معالجة مدة الانتهاء وإتمام إنشاء الكوبون."""
    global coupon_temp_data
    admin_id = message.chat.id
    
    if admin_id not in coupon_temp_data:
        bot.send_message(admin_id, "❌ خطأ في العملية. الرجاء البدء من جديد.")
        return

    expiry_input = message.text.strip().lower()
    expires_at = None
    
    try:
        if expiry_input == '0':
            expires_at = "لا يوجد"
        else:
            unit = expiry_input[-1] 
            value = int(expiry_input[:-1]) 
            
            if unit == 'd':
                delta = timedelta(days=value)
            elif unit == 'h':
                delta = timedelta(hours=value)
            else:
                raise ValueError("الوحدة غير صالحة.")

            # حساب تاريخ الانتهاء بناءً على الوقت الحالي في المنطقة الزمنية
            now = datetime.now(timezone)
            expiry_datetime = now + delta
            expires_at = expiry_datetime.strftime("%Y-%m-%d %H:%M:%S")

    except ValueError:
        msg = bot.send_message(admin_id, f"❌ صيغة المدة غير صحيحة. يجب أن تكون: [رقم]d أو [رقم]h. حاول مرة أخرى.")
        bot.register_next_step_handler(msg, get_coupon_expiry)
        return
    except Exception as e:
        msg = bot.send_message(admin_id, f"❌ حدث خطأ في معالجة المدة ({str(e)}). حاول مرة أخرى.")
        bot.register_next_step_handler(msg, get_coupon_expiry)
        return

    # إتمام الإنشاء
    finalize_coupon(admin_id, expires_at)

def finalize_coupon(admin_id, expires_at):
    """حفظ الكوبون في ملف الكوبونات."""
    global coupon_temp_data
    data = coupon_temp_data[admin_id]
    
    coupons = load_coupons()
    code = data['code']
    
    coupons[code] = {
        "points": data['points'],
        "max_uses": data['max_uses'],
        "expires_at": expires_at,
        "used_by": []
    }
    save_coupons(coupons)
    
    bot.send_message(admin_id, 
                     f"✅ **تم إنشاء الكوبون بنجاح**:\n\n"
                     f"🎫 **الرمز:** `{code}`\n"
                     f"💰 **النقاط:** {data['points']}\n"
                     f"🔄 **الحد الأقصى للاستخدام:** {data['max_uses']} مرات\n"
                     f"🗓️ **تاريخ الانتهاء:** {expires_at}",
                     parse_mode="Markdown")
                     
    del coupon_temp_data[admin_id]
# ***************************************************************
# --- معالج الرجوع للقائمة الرئيسية (إرسال /start جديد) ---
@bot.callback_query_handler(func=lambda call: call.data == "back_to_main_menu")
def back_to_main_menu_handler(call):
    # 1. إظهار إشعار سريع للمستخدم
    bot.answer_callback_query(call.id, "رجوع للقائمة الرئيسية...")
    
    # 2. حذف الرسالة التي تحتوي على الزر الحالي
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception as e:
        # إذا فشل الحذف، نتجاهل الخطأ ونستمر بالإرسال
        pass 

    # 3. محاكاة أمر /start باستخدام دالة start الأصلية
    
    # إنشاء كائن رسالة مؤقت (Temporary Message Object)
    class TempMessage:
        def __init__(self, chat_id, from_user):
            self.chat = types.Chat(chat_id, 'private')
            self.from_user = from_user
            self.text = '/start' # النص الذي سيتم قراءته في دالة start

    temp_message = TempMessage(call.message.chat.id, call.from_user)
    
    # استدعاء دالة start الأصلية الخاصة بك
    start(temp_message)
# روابط المتاجر الخارجية (تبقى كما هي)
STORE_LINKS = {
    "alsiraj": {"label": "مكتبة السراج", "url": "https://t.me/S_OOOCI"},
    "alqimma": {"label": "متجر القمة", "url": "https://t.me/u_tto"},
    "bano": {"label": "متجر بانو", "url": "https://t.me/cozmatik10"},
    "zahraa": {"label": "مركز الزهراء للهواتف النقالة", "url": "https://t.me/Topcash110"},
    "wldan": {"label": "مكتبة ولدان القرطاسية", "url": "https://t.me/Topcash112"}
}

# تحديث الحقول المطلوبة (يُضاف إلى قاموس FIELD_PROMPTS)
FIELD_PROMPTSS = { # استبدل القاموس القديم بهذا أو قم بتحديثه
    "telegram_username": "الرجاء إرسال **يوزر حسابك في تلجرام (@username)** لشراء الخدمة:",
    "telegram_user_or_link": "الرجاء إرسال **يوزر حسابك (@username) أو رابط المنشور** لشراء الخدمة:",
    "game_id": "الرجاء إرسال **آيدي حسابك في اللعبة (Player ID)** لشحن الشدات:",
    "game_name": "الرجاء إرسال **اسم حسابك في اللعبة (In-Game Name)**:",
    # ... (قد يحتوي على حقول أخرى مثل "amount" أو "payment_method")
}
# --- 1. قائمة المتجر الرئيسية (المتجر الالكتروني) ---
@bot.callback_query_handler(func=lambda call: call.data == "shop_menu")
def shop_menu_callback(call):
    if not is_bot_active(call.message):
        return bot.answer_callback_query(call.id, "❌ البوت متوقف مؤقتاً.")
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    markup.add(types.InlineKeyboardButton("خدمات تلجرام", callback_data="shop_category:telegram"))
    markup.add(types.InlineKeyboardButton("شحن العاب", callback_data="shop_category:games"))
    markup.add(types.InlineKeyboardButton("المتاجر (روابط خارجية)", callback_data="shop_stores"))
    
    markup.add(types.InlineKeyboardButton("⬅️ رجوع للقائمة الرئيسية", callback_data="back_to_main_menu"))
    
    bot.edit_message_text(chat_id=call.message.chat.id, 
                          message_id=call.message.message_id,
                          text="🛒 **المتجر الإلكتروني**\n\nاختر فئة المنتجات:", 
                          reply_markup=markup,
                          parse_mode='Markdown')
    bot.answer_callback_query(call.id)

# --- 2. قوائم الفئات (خدمات تلجرام، شحن العاب) ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("shop_category:"))
def shop_category_callback(call):
    category = call.data.split(":")[1]
    user_id = str(call.from_user.id)
    users = load_users()
    u = users.get(user_id, {})
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    for key, item in STORE_PRODUCTS.items():
        if item["category"] == category:
            # هنا يتم تمرير SHOP_ADMIN_ID دائمًا
            callback_data = f"buy_item:{key}:{item['cost']}:{item['admin_id']}"
            markup.add(types.InlineKeyboardButton(f"{item['label']} بسعر {item['cost']} نقطة", callback_data=callback_data))

    markup.add(types.InlineKeyboardButton("⬅️ رجوع لقائمة المتجر", callback_data="shop_menu"))
    
    category_name = "خدمات تلجرام" if category == "telegram" else "شحن الألعاب"
    
    bot.edit_message_text(chat_id=call.message.chat.id, 
                          message_id=call.message.message_id,
                          text=f"رصيدك الحالي: {u.get('points', 0)} نقطة.\n\nاختر من قائمة **{category_name}**:", 
                          reply_markup=markup,
                          parse_mode='Markdown')
    bot.answer_callback_query(call.id)

# --- 3. قائمة المتاجر الخارجية (روابط) ---
@bot.callback_query_handler(func=lambda call: call.data == "shop_stores")
def shop_stores_callback(call):
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    for store_key, store_info in STORE_LINKS.items():
        markup.add(types.InlineKeyboardButton(store_info["label"], url=store_info["url"]))

    markup.add(types.InlineKeyboardButton("⬅️ رجوع لقائمة المتجر", callback_data="shop_menu"))
    
    bot.edit_message_text(chat_id=call.message.chat.id, 
                          message_id=call.message.message_id,
                          text="🛍️ **المتاجر**\n\nاضغط على الزر للانتقال إلى المتجر الخارجي:", 
                          reply_markup=markup,
                          parse_mode='Markdown')
    bot.answer_callback_query(call.id)
# --- 4. بدء عملية الشراء (التحقق من الرصيد) ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_item:"))
def start_purchase_process(call):
    user_id = str(call.from_user.id)
    users = load_users()
    u = users.get(user_id, {})
    global user_purchase_data
    
    try:
        _, item_key, cost_str, admin_target = call.data.split(":")
        cost = int(cost_str)
    except ValueError:
        return bot.answer_callback_query(call.id, "❌ خطأ في تحليل بيانات الشراء.")

    if item_key not in STORE_PRODUCTS:
        return bot.answer_callback_query(call.id, "❌ المنتج غير متوفر حالياً.")
    
    item = STORE_PRODUCTS[item_key]

    if u.get("points", 0) < cost:
        return bot.answer_callback_query(call.id, f"❌ رصيدك ({u.get('points',0)} نقطة) غير كافٍ لشراء {item['label']} ({cost} نقطة).")
    
    # تم توحيد الآيدي إلى SHOP_ADMIN_ID
    actual_admin_id = SHOP_ADMIN_ID 

    user_purchase_data[user_id] = {
        "item_key": item_key,
        "item_label": item["label"],
        "cost": cost,
        "fields_required": item["fields"],
        "fields_collected": {},
        "current_field_index": 0,
        "admin_id": actual_admin_id
    }
    
    bot.answer_callback_query(call.id, f"بدء شراء {item['label']}.")
    
    first_field = item["fields"][0]
    prompt = FIELD_PROMPTSS.get(first_field, "أدخل البيانات المطلوبة:")
    msg = bot.send_message(call.message.chat.id, prompt, parse_mode="Markdown")
    
    bot.register_next_step_handler(msg, collect_purchase_field)

# --- 5. دالة تجميع الحقول بالتتابع ---
def collect_purchase_field(message):
    user_id = str(message.from_user.id)
    global user_purchase_data
    
    if user_id not in user_purchase_data:
        bot.send_message(message.chat.id, "❌ انتهت صلاحية الطلب أو لم يبدأ بشكل صحيح. ابدأ من قائمة المتجر.")
        return
        
    tp = user_purchase_data[user_id]
    idx = tp.get("current_field_index", 0)
    fields = tp.get("fields_required", [])
    
    if idx < len(fields):
        field_name = fields[idx]
        tp['fields_collected'][field_name] = message.text.strip()
        tp['current_field_index'] = idx + 1
        
    if tp['current_field_index'] < len(fields):
        next_field = fields[tp['current_field_index']]
        prompt = FIELD_PROMPTSS.get(next_field, "أدخل البيانات المطلوبة:")
        msg = bot.send_message(message.chat.id, prompt, parse_mode="Markdown")
        bot.register_next_step_handler(msg, collect_purchase_field)
        return
        
    item_label = tp.get("item_label", "منتج")
    cost = tp.get("cost", 0)
    collected = tp.get("fields_collected", {})
    
    fields_summary = ""
    for k, v in collected.items():
        field_prompt = FIELD_PROMPTSS.get(k, k).split(':')[0] 
        fields_summary += f"\n• {field_prompt}: **{v}**"
        
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("✅ تأكيد وإرسال الطلب", callback_data="confirm_final_purchase"),
               types.InlineKeyboardButton("❌ إلغاء", callback_data="cancel_purchase_confirm"))
               
    bot.send_message(message.chat.id,
                     f"**تأكيد طلب الشراء**\n\nالمنتج: {item_label}\nالنقاط المطلوب خصمها: {cost}\nالتفاصيل:{fields_summary}\n\nاضغط ✅ للتأكيد، وسيتم **إرسال الطلب للمشرف** بانتظار موافقته.",
                     parse_mode="Markdown", reply_markup=markup)

# --- 6. الإلغاء ---
@bot.callback_query_handler(func=lambda call: call.data == "cancel_purchase_confirm")
def cancel_purchase_confirm_callback(call):
    user_id = str(call.from_user.id)
    global user_purchase_data
    
    if user_id in user_purchase_data:
        del user_purchase_data[user_id]
        
    bot.edit_message_text("❌ تم إلغاء عملية الشراء. لم يتم خصم أي نقاط.", call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id, "تم إلغاء الطلب.")

# --- 7. التأكيد النهائي (إرسال الطلب للمشرف) ---
@bot.callback_query_handler(func=lambda call: call.data == "confirm_final_purchase")
def submit_purchase_request(call):
    user_id = str(call.from_user.id)
    global user_purchase_data
    global pending_purchase_requests
    users = load_users()
    
    if user_id not in user_purchase_data:
        return bot.answer_callback_query(call.id, "❌ انتهت صلاحية الطلب. ابدأ من جديد.")
        
    u = users.get(user_id, {})
    tp = user_purchase_data[user_id]
    cost = tp.get("cost", 0)
    
    if u.get("points", 0) < cost:
        del user_purchase_data[user_id]
        return bot.answer_callback_query(call.id, "❌ رصيدك غير كافٍ. تم إلغاء الطلب.")

    request_id = str(int(time.time() * 1000)) 
    
    request_data = {
        "user_id": user_id,
        "item_label": tp["item_label"],
        "cost": cost,
        "details": tp["fields_collected"],
        "admin_id": SHOP_ADMIN_ID,
        "request_time": datetime.now().strftime('%Y-%m-%d | %H:%M:%S') 
    }
    pending_purchase_requests[request_id] = request_data
    
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                          text=f"✅ **تم إرسال طلبك بنجاح!**\n\nتم إرسال طلب شراء **{tp['item_label']}** بقيمة **{cost}** نقطة.\nسيتم مراجعته والموافقة عليه من قبل المشرف قريباً.\nرقم الطلب: <code>{request_id}</code>.", 
                          parse_mode="HTML")
    bot.answer_callback_query(call.id, "تم إرسال الطلب بانتظار الموافقة.")
    
    admin_id_target = SHOP_ADMIN_ID
    collected_details = tp["fields_collected"]
    
    details_text = ""
    for k, v in collected_details.items():
        field_prompt = FIELD_PROMPTSS.get(k, k).split(':')[0].replace('الرجاء إرسال ', '') 
        details_text += f"\n• {field_prompt}: **{v}**"
        
    admin_msg = (
        f"💰 **طلب شراء جديد من المتجر الإلكتروني (بانتظار الموافقة)** 💰\n\n"
        f"**رقم الطلب:** <code>{request_id}</code>\n"
        f"**المنتج:** {tp['item_label']}\n"
        f"**النقاط المطلوبة:** {cost}\n"
        f"**المشتري:** <code>{user_id}</code> - {u.get('name', 'مستخدم')} (@{u.get('username', 'لا يوجد')})\n"
        f"**التفاصيل المطلوبة:{details_text}"
    )

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("✅ موافقة وخصم النقاط", callback_data=f"purchase_approve:{request_id}"),
        types.InlineKeyboardButton("❌ رفض الطلب (مع السبب)", callback_data=f"purchase_reject_ask:{request_id}")
    )
    
    try:
        bot.send_message(admin_id_target, admin_msg, parse_mode="HTML", reply_markup=markup)
    except Exception as e:
        bot.send_message(ADMIN_ID, f"⚠️ فشل إرسال إشعار الشراء ({tp['item_label']}) إلى المشرف: {admin_id_target}. (الخطأ: {e})", parse_mode="HTML")
        
    del user_purchase_data[user_id]


# --- 8. معالجات المشرف لطلبات الشراء (محدثة) ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("purchase_approve:") or call.data.startswith("purchase_reject_ask:"))
def purchase_admin_handler(call):
    admin_id = str(call.from_user.id)
    
    # التحقق من أن المستخدم ضاغط الزر هو المشرف المسموح له (ADMIN_ID هو المشرف العام و SHOP_ADMIN_ID هو مشرف المتجر)
    allowed_admins = [str(ADMIN_ID), str(SHOP_ADMIN_ID)]
    if admin_id not in allowed_admins: 
        return bot.answer_callback_query(call.id, "❌ ليس لديك صلاحية للقيام بهذا الإجراء.")
        
    global pending_purchase_requests
    global user_rejection_data
    
    action, request_id = call.data.split(":")
    
    if request_id not in pending_purchase_requests:
        return bot.edit_message_text("❌ انتهت صلاحية هذا الطلب أو تم التعامل معه مسبقاً.", call.message.chat.id, call.message.message_id)

    request_data = pending_purchase_requests[request_id]
    user_id = request_data["user_id"]
    cost = request_data["cost"]
    item_label = request_data["item_label"]
    admin_name = call.from_user.first_name
    users = load_users()
    u = users.get(user_id, {})

    if action == "purchase_approve":
        if u.get("points", 0) < cost:
            bot.send_message(call.message.chat.id, f"⚠️ لا يمكن الموافقة. رصيد المستخدم <code>{user_id}</code> غير كافٍ ({u.get('points', 0)} نقطة).", parse_mode="HTML")
            bot.edit_message_text(call.message.text + f"\n\n**⚠️ فشل الخصم:** رصيد غير كافٍ.", call.message.chat.id, call.message.message_id, parse_mode="HTML")
            del pending_purchase_requests[request_id]
            return
            
        # 1. خصم النقاط
        users[user_id]['points'] -= cost
        users[user_id]['purchases'] = users[user_id].get('purchases', 0) + 1 
        save_users(users)
        
        # 2. إشعار المستخدم بالموافقة
        try:
            bot.send_message(user_id, f"✅ **تمت الموافقة على طلب الشراء!**\n\nوافق المشرف **{admin_name}** على طلبك لشراء **{item_label}**.\nتم خصم **{cost}** نقطة من رصيدك.\nرصيدك الحالي: {users[user_id]['points']} نقطة.\nسيتم تزويدك بالخدمة/الشحن قريباً.", parse_mode="Markdown")
        except:
             pass 

        # 3. نشر العملية في القناة المخصصة للمتجر
        try:
            bot.send_message(CHANNEL_ID3, 
                             f"🥳 **عملية شراء جديدة ناجحة!**\n\n**المنتج:** {item_label}\n**النقاط المخصومة:** {cost}\n**المشتري:** <code>{user_id}</code>\n\n**بواسطة المشرف:** {admin_name}", 
                             parse_mode="HTML")
        except Exception as e:
            bot.send_message(ADMIN_ID, f"⚠️ فشل نشر عملية الشراء في قناة المتجر. (الخطأ: {e})", parse_mode="HTML")

        # 4. تحديث رسالة المشرف
        bot.edit_message_text(call.message.text + f"\n\n**✅ تمت الموافقة والخصم**\nتم الخصم بنجاح من رصيد المستخدم.\nالمشرف: {admin_name}", call.message.chat.id, call.message.message_id, parse_mode="HTML")

        # 5. مسح الطلب المعلق
        del pending_purchase_requests[request_id]
        
    elif action == "purchase_reject_ask":
        # 1. طلب السبب من المشرف
        user_rejection_data[admin_id] = {"request_id": request_id, "message_id": call.message.message_id}
        
        # إنشاء زر إلغاء عملية الرفض
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("إلغاء عملية الرفض", callback_data="cancel_admin_action"))
        
        # سنعدل الرسالة الأصلية لطلب السبب لتجنب فقدان السياق
        bot.edit_message_text(call.message.text + "\n\n**❌ الرجاء إرسال سبب رفض طلب الشراء للمستخدم في رسالة منفصلة:**", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML")
        
        # وننتظر الخطوة التالية
        bot.register_next_step_handler(call.message, process_purchase_rejection)
        bot.answer_callback_query(call.id, "الرجاء إدخال السبب في رسالة جديدة.")
        return # لا نمسح الطلب المعلق هنا

    bot.answer_callback_query(call.id, f"تم التعامل مع الطلب بنجاح ({'موافقة' if action == 'purchase_approve' else 'رفض'}).")

# --- 9. معالجة سبب الرفض (جديد) ---
def process_purchase_rejection(message):
    admin_id = str(message.from_user.id)
    global user_rejection_data
    global pending_purchase_requests
    
    if admin_id not in user_rejection_data:
        bot.send_message(message.chat.id, "❌ انتهت صلاحية إدخال سبب الرفض أو لم تبدأ عملية الرفض.")
        return

    data = user_rejection_data[admin_id]
    request_id = data["request_id"]
    original_message_id = data["message_id"]

    if request_id not in pending_purchase_requests:
        bot.send_message(message.chat.id, "❌ الطلب الأصلي غير موجود أو تمت معالجته بالفعل.")
        del user_rejection_data[admin_id]
        return
        
    request_data = pending_purchase_requests[request_id]
    user_id = request_data["user_id"]
    item_label = request_data["item_label"]
    admin_name = message.from_user.first_name
    rejection_reason = message.text.strip()

    # 1. إشعار المستخدم بالرفض وسبب الرفض
    try:
        bot.send_message(user_id, 
                         f"❌ **تم رفض طلب الشراء!**\n\nنأسف، رفض المشرف **{admin_name}** طلبك لشراء **{item_label}**.\n**سبب الرفض:** {rejection_reason}\n\nلم يتم خصم أي نقاط من رصيدك.", 
                         parse_mode="Markdown")
    except:
         bot.send_message(admin_id, f"⚠️ فشل إرسال إشعار الرفض للمستخدم <code>{user_id}</code>.", parse_mode="HTML")
         
    # 2. تحديث رسالة المشرف الأصلية (بإضافة حالة الرفض والسبب)
    try:
        bot.edit_message_text(f"**❌ تم الرفض**\n**المنتج:** {item_label}\n**للمستخدم:** <code>{user_id}</code>\n**المشرف:** {admin_name}\n**السبب المُرسَل:** {rejection_reason}", 
                              message.chat.id, original_message_id, parse_mode="HTML", reply_markup=None)
    except:
         bot.send_message(admin_id, f"⚠️ فشل تحديث رسالة المشرف الأصلية رقم {original_message_id}.", parse_mode="HTML")

    bot.send_message(admin_id, f"✅ تم إرسال سبب الرفض للمستخدم <code>{user_id}</code>.", parse_mode="HTML")
    
    # 3. مسح الطلب المعلق وبيانات الرفض
    del pending_purchase_requests[request_id]
    del user_rejection_data[admin_id]
    
# --- 10. إلغاء عملية إدخال السبب ---
@bot.callback_query_handler(func=lambda call: call.data == "cancel_admin_action")
def cancel_admin_action_callback(call):
    admin_id = str(call.from_user.id)
    global user_rejection_data
    
    if admin_id in user_rejection_data:
        # نستعيد الرسالة الأصلية قبل طلب السبب
        original_message_id = user_rejection_data[admin_id]["message_id"]
        
        # إعادة الرسالة الأصلية إلى حالتها قبل طلب السبب (مع أزرار الموافقة/الرفض)
        request_id = user_rejection_data[admin_id]["request_id"]
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("✅ موافقة وخصم النقاط", callback_data=f"purchase_approve:{request_id}"),
            types.InlineKeyboardButton("❌ رفض الطلب (مع السبب)", callback_data=f"purchase_reject_ask:{request_id}")
        )
        
        # تحديث الرسالة الأصلية وإزالة طلب السبب
        try:
             # نفترض أن النص الأصلي ما زال متاحاً في الرسالة قبل التعديل لطلب السبب
             bot.edit_message_text(call.message.text.replace("\n\n**❌ الرجاء إرسال سبب رفض طلب الشراء للمستخدم في رسالة منفصلة:**", ""), 
                                   call.message.chat.id, original_message_id, reply_markup=markup, parse_mode="HTML")
        except:
             # إذا فشل التحديث (ربما تم تعديل النص الأصلي بالكامل)، نرسل رسالة جديدة
             bot.send_message(call.message.chat.id, "✅ تم إلغاء عملية الرفض. يرجى البحث عن الرسالة الأصلية.", reply_markup=markup)
             
        del user_rejection_data[admin_id]
        bot.answer_callback_query(call.id, "تم الإلغاء بنجاح.")
    else:
        bot.answer_callback_query(call.id, "لا توجد عملية رفض قيد التنفيذ للإلغاء.")

####
# ملاحظة: يجب أن تكون user_transfer_data معرفة كـ global dict في بداية ملفك (موجودة في ملفاتك المرفقة).
@bot.callback_query_handler(func=lambda call: call.data == "cancel_transfer")
def cancel_transfer_process(call):
    user_id = str(call.from_user.id)
    
    # 1. إزالة البيانات المؤقتة لضمان إنهاء العملية
    if user_id in user_transfer_data:
        del user_transfer_data[user_id]
        
    # 2. تعديل الرسالة لإبلاغ المستخدم بالإلغاء
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="❌ **تم إلغاء عملية تحويل النقاط.**\n\n يمكنك بدء عملية جديدة من القائمة الرئيسية.",
        parse_mode='Markdown'
    )
    # 3. إزالة المعالج التالي المسجل (مهم جداً لإنهاء العملية)
    bot.clear_step_handler_by_chat_id(call.message.chat.id)
    bot.answer_callback_query(call.id, "تم إلغاء العملية.")
@bot.callback_query_handler(func=lambda call: call.data == "transfer_points_inline")
def start_transfer_points(call):
    # 1. إنشاء زر الإلغاء (Inline Keyboard)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌ إلغاء العملية والرجوع", callback_data="cancel_transfer"))
    
    # 2. إرسال رسالة طلب المبلغ وبدء تسلسل المحادثة
    msg = bot.send_message(
        call.message.chat.id, 
        "🏦 **بدء عملية تحويل النقاط:**\n\n"
        "يرجى إرسال **المبلغ** الذي تود تحويله (أرقام صحيحة).\n"
        f"**ملاحظة:** يتم استقطاع عمولة ثابتة قدرها **{TRANSFER_FEE}** نقطة من رصيدك عند إتمام التحويل.",
        parse_mode='Markdown',
        reply_markup=markup # 🚨 تم إضافة لوحة المفاتيح هنا 🚨
    )
    
    # تعيين الدالة التالية للمعالجة وتخزين المبلغ
    bot.register_next_step_handler(msg, process_transfer_amount)
    
    # الإجابة على الاستعلام CallbackQuery حتى لا تبقى أيقونة التحميل ظاهرة
    bot.answer_callback_query(call.id)

# ----------------------------------------------------
# 2. معالج استلام المبلغ (تم تحسين التحقق)
# ----------------------------------------------------
def process_transfer_amount(message):
    user_id = str(message.chat.id)
    global user_transfer_data 
    users = load_users()
    
    # التحقق من أن المبلغ رقم صحيح وموجب
    try:
        amount = int(message.text.strip())
        if amount <= 0:
            bot.send_message(user_id, "❌ **خطأ:** يرجى إدخال مبلغ موجب.")
            return # إنهاء العملية
    except ValueError:
        msg = bot.send_message(user_id, "❌ **خطأ:** يرجى إدخال مبلغ صحيح (أرقام فقط).")
        bot.register_next_step_handler(msg, process_transfer_amount)
        return

    # التحقق من أن الرصيد كافٍ (المبلغ + العمولة)
    required_points = amount + TRANSFER_FEE
    current_points = users.get(user_id, {}).get('points', 0)
    
    if current_points < required_points:
        bot.send_message(user_id, 
                         f"❌ **فشل التحويل:** رصيدك الحالي هو **{current_points}** نقطة.\n"
                         f"المجموع المطلوب للتحويل: **{required_points}** نقطة (شامل العمولة). الرصيد غير كافٍ.")
        return # إنهاء العملية

    # حفظ المبلغ وبدء طلب الآيدي
    user_transfer_data[user_id] = {'amount': amount}
    msg = bot.send_message(user_id, 
                           "✅ المبلغ مقبول. يرجى الآن إرسال **آيدي المستخدم** (ID) الذي تريد التحويل إليه. (أرقام فقط)")
    bot.register_next_step_handler(msg, process_target_id)

# ----------------------------------------------------
# 3. معالج استلام الآيدي وتأكيد التحويل (تم تحسين التحقق)
# ----------------------------------------------------
def process_target_id(message):
    sender_id = str(message.chat.id)
    
    # تحقق من أن المستخدم بدأ التسلسل
    if sender_id not in user_transfer_data:
        bot.send_message(sender_id, "❌ **خطأ:** يرجى إعادة بدء عملية التحويل من القائمة الرئيسية.")
        return

    target_id = message.text.strip()
    
    # التحقق من أن الآيدي رقم صحيح
    if not target_id.isdigit():
        msg = bot.send_message(sender_id, "❌ **خطأ:** يجب أن يكون آيدي المستلم أرقاماً فقط.")
        bot.register_next_step_handler(msg, process_target_id)
        return
        
    # منع التحويل للنفس
    if target_id == sender_id:
        bot.send_message(sender_id, "❌ **خطأ:** لا يمكنك التحويل إلى حسابك الشخصي.")
        # مسح البيانات المؤقتة لإنهاء العملية
        if sender_id in user_transfer_data: del user_transfer_data[sender_id]
        return
        
    users = load_users()
    
    # التحقق من وجود المستلم
    if target_id not in users:
        bot.send_message(sender_id, f"❌ **فشل:** لم يتم العثور على مستخدم بالآيدي **{target_id}** في قاعدة البيانات.")
        # مسح البيانات المؤقتة لإنهاء العملية
        if sender_id in user_transfer_data: del user_transfer_data[sender_id]
        return

    # بيانات التحويل
    amount = user_transfer_data[sender_id]['amount']
    target_user = users[target_id]
    
    # بناء رسالة التأكيد
    confirm_text = (
        "🔍 **تأكيد التحويل:**\n\n"
        f"**المبلغ المُحول:** {amount} نقطة\n"
        f"**عمولة التحويل:** {TRANSFER_FEE} نقطة\n"
        f"**المستقطع من حسابك:** {amount + TRANSFER_FEE} نقطة\n\n"
        f"**معلومات المستلم:**\n"
        f"  - **الاسم:** {target_user.get('name', 'غير متوفر')}\n"
        f"  - **الآيدي:** `{target_id}`\n"
        f"  - **نقاطه الحالية:** {target_user.get('points', 0)} نقطة\n\n"
        "**هل أنت متأكد من إتمام العملية؟**"
    )

    # إنشاء زر التأكيد والإلغاء
    markup = types.InlineKeyboardMarkup()
    # تم ترميز الآيدي والمبلغ في الـ callback_data
    confirm_btn = types.InlineKeyboardButton("✅ تأكيد التحويل", 
                                             callback_data=f"confirm_transfer_{target_id}_{amount}")
    cancel_btn = types.InlineKeyboardButton("❌ إلغاء", callback_data="cancel_transfer")
    markup.add(confirm_btn, cancel_btn)
    
    # إرسال رسالة التأكيد
    bot.send_message(sender_id, confirm_text, reply_markup=markup, parse_mode='Markdown')

# ----------------------------------------------------
# 4. معالج التأكيد النهائي وتنفيذ التحويل (تم تعزيز التحقق)
# ----------------------------------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_transfer_'))
def finalize_transfer(call):
    
    sender_id = str(call.message.chat.id)
    
    # تحليل بيانات الـ callback
    try:
        # البيانات تأتي بالصيغة: confirm_transfer_TARGETID_AMOUNT
        _, _, target_id, amount_str = call.data.split('_')
        amount = int(amount_str)
    except ValueError:
        bot.answer_callback_query(call.id, "خطأ في تحليل بيانات التحويل. يرجى المحاولة مرة أخرى.")
        return
        
    users = load_users()
    
    # التحقق من أن المستلم موجود قبل الخصم
    if target_id not in users:
        # تغيير من edit_message_text إلى send_message
        bot.send_message(call.message.chat.id, 
                              "❌ **فشل التحويل:** لم يتم العثور على المستلم في قاعدة البيانات.",
                              parse_mode='Markdown')
        bot.answer_callback_query(call.id, "فشل: المستلم غير موجود.")
        return
    
    # تحقق أخير من الرصيد قبل الخصم (تحقق حاسم)
    required_points = amount + TRANSFER_FEE
    current_points = users.get(sender_id, {}).get('points', 0)

    if current_points < required_points:
        # تغيير من edit_message_text إلى send_message
        bot.send_message(call.message.chat.id, 
                              "❌ **فشل التحويل:** رصيدك أصبح غير كافٍ لإتمام العملية بعد التحقق الأخير.",
                              parse_mode='Markdown')
        bot.answer_callback_query(call.id, "فشل: الرصيد غير كافٍ.")
        return
        
    # --- تنفيذ التحويل (يتم التنفيذ فقط إذا كانت جميع الشروط أعلاه صحيحة) ---
    
    # 1. خصم النقاط والعمولة من المُحوِل
    users[sender_id]['points'] -= required_points
    
    # 2. إضافة النقاط للمستلم
    users[target_id]['points'] += amount
    save_users(users)
    
    # 3. إرسال إشعار للمستلم
    sender_name = users[sender_id].get('name', f"المستخدم {sender_id}")
    try:
        bot.send_message(
            target_id, 
            f"🎉 **لقد استلمت تحويلاً!**\n\n"
            f"  - **الكمية:** **{amount}** نقطة.\n"
            f"  - **من:** **{sender_name}**.\n"
            f"  - **رصيدك الجديد:** **{users[target_id]['points']}** نقطة.",
            parse_mode='Markdown'
        )
    except Exception as e:
        # في حال حظر المستلم للبوت
        print(f"فشل إرسال إشعار للمستلم {target_id}: {e}")
        
    # 4. إرسال إشعار إتمام للمُحوِل (تغيير من edit_message_text إلى send_message)
    bot.send_message(
        call.message.chat.id, 
        f"✅ **تم التحويل بنجاح!**\n\n"
        f"  - **المبلغ المُحول:** {amount} نقطة.\n"
        f"  - **العمولة المستقطعة:** {TRANSFER_FEE} نقطة.\n"
        f"  - **رصيدك الجديد:** {users[sender_id]['points']} نقطة.",
        parse_mode='Markdown'
    )
    
    # **جديد:** محاولة حذف رسالة التأكيد القديمة لتنظيف الدردشة
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception as e:
        print(f"فشل حذف رسالة التأكيد: {e}")

    # 5. حفظ سجل التحويل في القناة (CHANNEL_ID)
    current_time_str = datetime.now(timezone).strftime('%Y-%m-%d | %H:%M:%S') if timezone else datetime.now().strftime('%Y-%m-%d | %H:%M:%S')
    log_message = (
        "💵 **سجل تحويل نقاط جديد** 💵\n\n"
        f"**تاريخ التحويل:** {current_time_str}\n"
        f"**الكمية المُحولة:** {amount} نقطة\n"
        f"**العمولة المستقطعة:** {TRANSFER_FEE} نقطة\n"
        f"**الآيدي المُحوِل:** `{sender_id}` | [{users[sender_id].get('name', 'غير متوفر')}]\n"
        f"**الآيدي المستلم:** `{target_id}` | [{users[target_id].get('name', 'غير متوفر')}]"
    )
    bot.send_message(CHANNEL_ID2, log_message, parse_mode='Markdown') 
    
    # 6. مسح البيانات المؤقتة
    global user_transfer_data
    if sender_id in user_transfer_data:
        del user_transfer_data[sender_id]
        
    bot.answer_callback_query(call.id, "تم إتمام التحويل!")

# ----------------------------------------------------
# 5. معالج الإلغاء
# ----------------------------------------------------
@bot.callback_query_handler(func=lambda call: call.data == "cancel_transfer")
def cancel_transfer(call):
    sender_id = str(call.message.chat.id)
    
    global user_transfer_data
    # مسح البيانات المؤقتة
    if sender_id in user_transfer_data:
        del user_transfer_data[sender_id]
        
    # تعديل الرسالة للإعلام بالإلغاء (تغيير من edit_message_text إلى send_message)
    bot.send_message(call.message.chat.id, 
                          "🚫 **تم إلغاء عملية التحويل.** يمكنك البدء من جديد متى شئت.",
                          parse_mode='Markdown')
                          
    # **جديد:** محاولة حذف رسالة التأكيد القديمة لتنظيف الدردشة
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception as e:
        print(f"فشل حذف رسالة الإلغاء: {e}")
        
    bot.answer_callback_query(call.id, "تم الإلغاء.")

# ---Handlers: عرض قائمة السحب والاختيار---
@bot.callback_query_handler(func=lambda call: call.data == "withdrawal_menu")
def withdrawal_menu_callback(call):
    if not is_bot_active(call.message):
        return bot.answer_callback_query(call.id, "❌ البوت متوقف مؤقتاً.")
    user_id = str(call.from_user.id)
    users = load_users()
    u = users.get(user_id, {})
    if u.get("banned", False):
        return bot.answer_callback_query(call.id, "❌ لقد تم حظرك من استخدام هذا البوت.")
    markup = types.InlineKeyboardMarkup(row_width=1)
    # عرض طرق السحب (مجموعات)
    markup.add(types.InlineKeyboardButton("💳 ماستر كارد", callback_data="wd_group_mastercard"))
    markup.add(types.InlineKeyboardButton("📱 زين كاش", callback_data="wd_group_zain"))
    markup.add(types.InlineKeyboardButton("⛓️ رصيد اثير", callback_data="wd_group_ether"))
    markup.add(types.InlineKeyboardButton("₮ USDT (OKX - TRC20)", callback_data="wd_group_usdt"))
    markup.add(types.InlineKeyboardButton("🌏 رصيد اسيا", callback_data="wd_group_asia"))
    markup.add(types.InlineKeyboardButton("⬅️ رجوع للقائمة الرئيسية", callback_data="back_to_main_menu"))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="اختر طريقة السحب التي تفضلها:", reply_markup=markup)
    bot.answer_callback_query(call.id)

# لكل مجموعة نعرض الفئات المتاحة منها
@bot.callback_query_handler(func=lambda call: call.data.startswith("wd_group_"))
def wd_group_choose(call):
    group = call.data.replace("wd_group_", "")
    user_id = str(call.from_user.id)
    users = load_users()
    u = users.get(user_id, {})
    markup = types.InlineKeyboardMarkup(row_width=1)

    # بناء قائمة الفئات ذات الصلة بالمجموعة
    if group == "mastercard":
        keys = ["mastercard_10", "mastercard_25", "mastercard_50", "mastercard_100", "mastercard_150"]
    elif group == "zain":
        keys = ["zaincash_10", "zaincash_25", "zaincash_50", "zaincash_100", "zaincash_150"]
    elif group == "ether":
        keys = ["ether_balance_5", "ether_balance_10", "ether_balance_15"]
    elif group == "usdt":
        keys = ["usdt_okx_10", "usdt_okx_25", "usdt_okx_50"]
    elif group == "asia":
        keys = ["asia_balance_5", "asia_balance_10", "asia_balance_15"]
    else:
        keys = []

    for k in keys:
        item = WITHDRAWAL_METHODS[k]
        markup.add(types.InlineKeyboardButton(f"سحب {item['amount']}$ بسعر {item['cost']} نقطة ", callback_data=f"start_withdraw:{k}"))

    markup.add(types.InlineKeyboardButton("⬅️ رجوع لقائمة السحب", callback_data="withdrawal_menu"))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=f"رصيدك الحالي: {u.get('points', 0)} نقطة.\n\nاختر فئة السحب:", reply_markup=markup)
    bot.answer_callback_query(call.id)

# بدء عملية السحب: نتحقق من الرصيد ونحفظ temp_withdrawal مع قائمة الحقول
@bot.callback_query_handler(func=lambda call: call.data.startswith("start_withdraw:"))
def start_withdrawal_process(call):
    user_id = str(call.from_user.id)
    users = load_users()
    u = users.get(user_id, {})
    option_key = call.data.split(":")[1]
    if option_key not in WITHDRAWAL_METHODS:
        return bot.answer_callback_query(call.id, "❌ خيار سحب غير صحيح.")
    option = WITHDRAWAL_METHODS[option_key]
    if u.get("points", 0) < option["cost"]:
        return bot.answer_callback_query(call.id, f"❌ رصيدك ({u.get('points',0)} نقطة) غير كافٍ لسحب {option['amount']}$ ({option['cost']} نقطة).")
    # أنشئ temp_withdrawal مع الحقول المطلوبة وتابع الخطوة الأولى
    u['temp_withdrawal'] = {
        "method_key": option_key,
        "method_label": option["label"],
        "cost": option["cost"],
        "fields_required": option["fields"],
        "fields_collected": {},
        "current_field_index": 0
    }
    save_users(users)
    bot.answer_callback_query(call.id, f"بدء سحب {option['amount']}$ — {option['label']}.")
    # اسأل أول حقل
    first_field = option["fields"][0]
    prompt = FIELD_PROMPTS.get(first_field, "أدخل البيانات المطلوبة:")
    msg = bot.send_message(call.message.chat.id, prompt, parse_mode="Markdown")
    bot.register_next_step_handler(msg, collect_withdraw_field)

# دالة عامة تجمع الحقول بالتتابع لأي طريقة سحب
def collect_withdraw_field(message):
    user_id = str(message.from_user.id)
    users = load_users()
    if user_id not in users:
        bot.send_message(message.chat.id, "❌ حدث خطأ: المستخدم غير مسجل. ابدأ من جديد.")
        return
    u = users[user_id]
    if 'temp_withdrawal' not in u:
        bot.send_message(message.chat.id, "❌ انتهت صلاحية الطلب أو لم يبدأ بشكل صحيح. ابدأ من قائمة السحب.")
        return
    tw = u['temp_withdrawal']
    idx = tw.get("current_field_index", 0)
    fields = tw.get("fields_required", [])
    # خزّن الإجابة للحقل الحالي
    if idx < len(fields):
        field_name = fields[idx]
        tw['fields_collected'][field_name] = message.text.strip()
        tw['current_field_index'] = idx + 1
        save_users(users)
    # إذا لا يزال هناك حقول متبقية فاسأل التالية
    if tw['current_field_index'] < len(fields):
        next_field = fields[tw['current_field_index']]
        prompt = FIELD_PROMPTS.get(next_field, "أدخل البيانات المطلوبة:")
        msg = bot.send_message(message.chat.id, prompt, parse_mode="Markdown")
        bot.register_next_step_handler(msg, collect_withdraw_field)
        return
    # جميع الحقول تم جمعها -> عرض صفحة التأكيد مع زري تأكيد/إلغاء
    option_label = tw.get("method_label", "طريقة سحب")
    cost = tw.get("cost", 0)
    collected = tw.get("fields_collected", {})
    # بناء نص ملخص الحقول المجمعة
    fields_summary = ""
    for k, v in collected.items():
        fields_summary += f"\n• {k}: `{v}`"
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("✅ تأكيد الإرسال", callback_data="confirm_final_withdrawal"),
               types.InlineKeyboardButton("❌ إلغاء", callback_data="cancel_withdrawal_confirm"))
    bot.send_message(message.chat.id,
                     f"**تأكيد طلب السحب**\n\nطريقة: {option_label}\nالنقاط المطلوب خصمها: {cost}\nالتفاصيل:{fields_summary}\n\nاضغط ✅ للتأكيد وسيتم خصم النقاط فورًا وإرسال الطلب للمشرف.",
                     parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "cancel_withdrawal_confirm")
def cancel_withdrawal_confirm_callback(call):
    user_id = str(call.from_user.id)
    users = load_users()
    if 'temp_withdrawal' in users.get(user_id, {}):
        del users[user_id]['temp_withdrawal']
        save_users(users)
    bot.edit_message_text("❌ تم إلغاء عملية السحب. لم يتم خصم أي نقاط.", call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id, "تم إلغاء الطلب.")

# عند الضغط على تأكيد -> نخصم النقاط فورًا، نخزن الطلب ونرسل للمشرف مع أزرار موافقة/رفض
@bot.callback_query_handler(func=lambda call: call.data == "confirm_final_withdrawal")
def final_withdrawal_submission(call):
    user_id = str(call.from_user.id)
    users = load_users()
    if user_id not in users:
        return bot.answer_callback_query(call.id, "❌ خطأ: المستخدم غير موجود.")
    u = users[user_id]
    if 'temp_withdrawal' not in u:
        return bot.answer_callback_query(call.id, "❌ انتهت صلاحية الطلب. ابدأ من جديد.")
    tw = u['temp_withdrawal']
    cost = tw.get("cost", 0)
    if u.get("points", 0) < cost:
        del u['temp_withdrawal']
        save_users(users)
        return bot.answer_callback_query(call.id, "❌ رصيدك غير كافٍ. تم إلغاء الطلب.")
    # خصم النقاط فورًا (حجز)
    users[user_id]['points'] -= cost
    save_users(users)
    # تسجيل الطلب
    withdrawals = load_withdrawals()
    withdrawal_id = f"W{int(time.time())}{user_id[-4:]}"
    request_data = {
        "id": withdrawal_id,
        "user_id": user_id,
        "username": u.get("username", "لا يوجد"),
        "name": u.get("name", "مستخدم"),
        "method_key": tw.get("method_key"),
        "method_label": tw.get("method_label"),
        "details": tw.get("fields_collected", {}),
        "cost": cost,
        "status": "Pending",
        "deducted": True,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    withdrawals[withdrawal_id] = request_data
    save_withdrawals(withdrawals)
    # إعلام المستخدم بنجاح الحجز
    try:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f"✅ تم خصم {cost} نقطة من رصيدك كحجز لطلب السحب رقم `{withdrawal_id}`.\nسيتم مراجعة الطلب من قبل المشرف.\nرصيدك الحالي: {users[user_id]['points']} نقطة.",
                              parse_mode="Markdown")
    except Exception:
        pass
    bot.answer_callback_query(call.id, "تم خصم النقاط وإرسال الطلب للمشرف.")
    # احذف temp_withdrawal من المستخدم
    del users[user_id]['temp_withdrawal']
    save_users(users)
    # إرسال إشعار للمشرف مع أزرار موافقة/رفض
    admin_markup = types.InlineKeyboardMarkup(row_width=2)
    admin_markup.add(types.InlineKeyboardButton("✅ موافقة", callback_data=f"approve_wd:{withdrawal_id}"),
                     types.InlineKeyboardButton("❌ إلغاء", callback_data=f"reject_wd:{withdrawal_id}"))
    # بناء رسالة تفصيلية للمشرف (نعرض الحقول بطريقة مقروءة)
    details = request_data["details"]
    details_text = ""
    for k, v in details.items():
        details_text += f"\n• {k}: {v}"
    admin_msg = (f"🔔 طلب سحب جديد 🔔\n\nرقم الطلب: `{withdrawal_id}`\nالتاريخ: {request_data['timestamp']}\n\n"
                 f"مستخدم: <code>{user_id}</code> - {request_data['name']} (@{request_data['username']})\n"
                 f"طريقة: {request_data['method_label']}\nالنقاط المحجوزة: {cost}\nالتفاصيل:{details_text}")
    try:
        bot.send_message(WITHDRAWAL_ADMIN_ID, admin_msg, parse_mode="HTML", reply_markup=admin_markup)
    except telebot.apihelper.ApiTelegramException:
        bot.send_message(ADMIN_ID, f"⚠️ فشل إرسال طلب السحب رقم {withdrawal_id} إلى المشرف {WITHDRAWAL_ADMIN_ID}.")

# معالجة موافقة/رفض المشرف (كما في النسخة السابقة)
@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_wd:") or call.data.startswith("reject_wd:"))
def handle_admin_withdrawal_action(call):
    admin_id = str(call.from_user.id)
    if admin_id != WITHDRAWAL_ADMIN_ID and admin_id != ADMIN_ID:
        return bot.answer_callback_query(call.id, "❌ ليس لديك صلاحية الموافقة/الإلغاء على السحوبات.")
    action, withdrawal_id = call.data.split(":")
    withdrawals = load_withdrawals()
    if withdrawal_id not in withdrawals:
        return bot.edit_message_text("❌ لم يتم العثور على هذا الطلب أو تم التعامل معه مسبقاً.", call.message.chat.id, call.message.message_id)
    request_data = withdrawals[withdrawal_id]
    user_id = request_data["user_id"]
    users = load_users()
    # منع إعادة التعامل مع نفس الطلب
    if request_data.get("status") != "Pending":
        return bot.answer_callback_query(call.id, f"⚠️ هذا الطلب تم التعامل معه بالفعل ({request_data.get('status')}).")
    if action == "approve_wd":
        # إذا كانت النقاط محجوزة (deducted=True) فلا نخصم مرة أخرى، فقط نغيّر الحالة إلى Approved
        request_data["status"] = "Approved"
        request_data["response_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        withdrawals[withdrawal_id] = request_data
        save_withdrawals(withdrawals)
 # ********** إضافة إشعار القناة هنا **********
        user_info = users.get(user_id, {})
        
        channel_msg = (
            f"💰 **تم قبول طلب سحب جديد!**\n\n"
            f"✨ **الحالة:** ✅ **تمت الموافقة**\n"
            f"👤 **المستخدم:** {user_info.get('name', 'غير معروف')} (@{user_info.get('username', 'لا يوجد')})\n"
            f"💳 **آيدي المستخدم:** <code>{user_id}</code>\n"
            f"💸 **المبلغ المطلوب:** {request_data.get('amount_label', 'غير محدد')}\n"
            f"💰 **تكلفة النقاط (المخصومة):** {request_data['cost']} نقطة\n"
            f"⚙️ **طريقة السحب:** {request_data['method_label']}\n"
        )
        try:
            # افتراض أن CHANNEL_ID2 هو القناة المناسبة للمعاملات المالية
            bot.send_message(CHANNEL_ID3, channel_msg, parse_mode="HTML")
        except Exception as e:
            print(f"Failed to send approval message to channel: {e}")
        # **********************************************
        
        # إشعار المستخدم
        try:
            bot.send_message(user_id, f"✅ تم قبول طلب السحب `{withdrawal_id}` وسيتم تنفيذ التحويل.\nالمبلغ: {request_data['method_label']}\nتم حجز: {request_data['cost']} نقطة.\nرصيدك الحالي: {users.get(user_id,{}).get('points',0)} نقطة.")
        except Exception:
            pass
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"✅ تم الموافقة على طلب {withdrawal_id}.")
        bot.answer_callback_query(call.id, "تمت الموافقة.")
    elif action == "reject_wd":
        # نطلب من المشرف سبب الرفض — وسيتم استرجاع النقاط إذا كانت قد خصمت
        msg = bot.send_message(call.message.chat.id, f"أرسل **سبب إلغاء** طلب السحب رقم `{withdrawal_id}`. (سيتم استرجاع النقاط تلقائياً للمستخدم إن كانت قد خصمت).", parse_mode="Markdown")
        bot.register_next_step_handler(msg, finalize_rejection, withdrawal_id, call.message.message_id, call.message.chat.id)
        bot.answer_callback_query(call.id, "أرسل سبب الإلغاء.")

def finalize_rejection(message, withdrawal_id, original_msg_id, original_chat_id):
    rejection_reason = message.text.strip()
    withdrawals = load_withdrawals()
    users = load_users()
    if withdrawal_id not in withdrawals:
        bot.send_message(original_chat_id, "❌ لم يتم العثور على هذا الطلب أو تم التعامل معه مسبقاً.")
        return
    request_data = withdrawals[withdrawal_id]
    user_id = request_data["user_id"]
    cost = request_data["cost"]
    # تحديث حالة الطلب
    request_data["status"] = "Rejected"
    request_data["rejection_reason"] = rejection_reason
    request_data["response_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # استرجاع النقاط إذا كانت قد خصمت
    if request_data.get("deducted", False) and user_id in users:
        users[user_id]["points"] += cost
        save_users(users)
        try:
            bot.send_message(user_id, f"❌ تم إلغاء طلب السحب `{withdrawal_id}`.\nالسبب: {rejection_reason}\nتم استرجاع {cost} نقطة إلى رصيدك.\nرصيدك الحالي: {users[user_id]['points']} نقطة.")
        except Exception:
            pass
        # تحديث رسالة المشرف الأصلية
        bot.edit_message_text(chat_id=original_chat_id, message_id=original_msg_id,
                              text=f"❌ تم إلغاء طلب السحب رقم `{withdrawal_id}`.\nتم استرجاع {cost} نقطة للمستخدم.\nالسبب: {rejection_reason}")
    else:
        bot.edit_message_text(chat_id=original_chat_id, message_id=original_msg_id,
                              text=f"❌ تم إلغاء طلب السحب رقم `{withdrawal_id}`.\nالسبب: {rejection_reason} (لم تُخصم نقاط).")
    withdrawals[withdrawal_id] = request_data
    save_withdrawals(withdrawals)

# --- تكملة الدوال الأساسية ---

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    users = load_users()

    # التحقق من الحظر
    if users.get(user_id, {}).get("banned", False):
        bot.send_message(message.chat.id, "❌ لقد تم حظرك من استخدام هذا البوت.")
        return

    # التحقق من حالة البوت
    if not is_bot_active(message):
        return

    # استخراج الإحالة
    args = message.text.split()
    ref = args[1] if len(args) > 1 and args[1].isdigit() else None
    
    # تحديد ما إذا كان المستخدم الحالي هو الأدمن المُعين
    is_admin = (user_id == ADMIN_ID)

    if user_id not in users:
        # تسجيل مستخدم جديد
        users[user_id] = {
            "name": message.from_user.first_name or "مستخدم",
            "username": message.from_user.username or "لا يوجد",
            "points": 0,
            "purchases": 0,
            "referrals": 0,
            "banned": False,
            "role": "admin" if is_admin else "user",
            "last_claim": None,
            "daily_gifts": 0,
            "purchases_list": []
        }
        
        if is_admin:
            bot.send_message(message.chat.id, "🎉 **تهانينا!** تم التعرف عليك كأدمن البوت.", parse_mode="Markdown")

        save_users(users)

        # منطق الإحالة
        if ref and ref in users and ref != user_id:
            settings = load_edit()
            ref_points = settings.get("referral_points", 50)
            users[ref]["points"] += ref_points
            users[ref]["referrals"] += 1
            rank = get_rank(users[ref]["points"])
            update_user_rank(user_id)
            try:
                bot.send_message(ref, f"""ربحت {ref_points} نقطة من دعوة المستخدم {users[user_id]['name']}\nتصنيفك الآن: {rank}\n""")
            except telebot.apihelper.ApiTelegramException:
                print(f"لا يمكن إرسال رسالة تنبيه الإحالة للمستخدم {ref}")

        # إشعار للقناة
        name = users[user_id]['name']
        username = users[user_id]['username']
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        notif_msg = f"مستخدم جديد دخل البوت\n\nالاسم: {name}\nالمعرف: @{username}\nالآيدي: {user_id}\nالتاريخ والوقت: {time_now}"
        try:
            bot.send_message(CHANNEL_ID, notif_msg)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"خطأ في إرسال إشعار القناة: {e}")

    u = users[user_id]
    badge = get_badge(u)


    main_menu_markup = get_main_menu_markup(user_id)

    bot.send_message(message.chat.id, f"""
<b>✨ مرحباً {u['name']}!</b>

<b>📋 معلومات حسابك:</b>
<b>🆔 الآيدي:</b> <code>{user_id}</code>
<b>👤 الاسم:</b> {u['name']}
<b>🔎 المعرف:</b> @{u['username']}
<b>💰 رصيدك:</b> {u['points']} نقطة
<b>🛒 السلع المشتراة:</b> {u['purchases']}
<b>🤝 عدد الدعوات:</b> {u['referrals']}
<b>🎁 الهدايا اليومية:</b> {u.get("daily_gifts", 0)}

<b>🔗 رابط الدعوة الخاص بك:</b>
<code>https://t.me/{bot.get_me().username}?start={user_id}</code>

<b>🏅 شارتك:</b> {get_badge(u)}
""",
            reply_markup=main_menu_markup,
            parse_mode="HTML",
            disable_web_page_preview=True
        )
RULES_MESSAGE = """
**📜 ملاحظات وقوانين هامة للحفاظ على حسابك:**

1. **شراء النقاط:** ممنوع شراء النقاط من غير الوكلاء المدرجة أسماؤهم في البوت، والمخالفة تؤدي إلى **حضر الطرفين**.

2. **استلام النقاط:** يمنع استلام كميات كبيرة أو غير اعتيادية من حسابات وهمية أو حقيقية، وستؤدي المخالفة إلى **حضر الطرفين**.

3. **التحايل والانتحال:** أي محاولة للتحايل على الوكلاء أو قسم الدعم أو الانتحال كأحد أفراد الإدارة تؤدي إلى **الحضر الدائم**.

4. **التعامل مع القروض:** إرسال أو استلام النقاط من أصحاب القروض يؤدي إلى **إنذارات وحضر أسبوعي**.

5. **المطورين والمشاريع الأخرى:** ممنوع استثمار أي دعم أو مشاريع لمطورين آخرين داخل البوت بأي شكل كان.

6. **التسقيط والإساءة:** أي محاولة تسقيط أو تشويه سمعة المستخدمين أو الإدارة تُعاقب بـ**الحضر الشهري أو السنوي**.

7. **مسؤولية الحساب والأرباح:** المتجر غير مسؤول عن أي مشاكل تتعلق بحسابك في تيليجرام، وأرباح المتجر قابلة للصعود والنزول حسب طبيعة الاستثمار.

8. **تفعيل الحساب:** في حال لم يقم المستخدم بالسحب خلال مدة أقصاها **45 يوم**، يتم حظر الحساب بشكل تلقائي.
"""

# --- معالج الـ Callback لـ "من نحن؟" (تم التعديل) ---
@bot.callback_query_handler(func=lambda call: call.data == "about_us_inline")
def handle_about_us_query(call):
    # 1. الحصول على التاريخ والوقت الفعلي
    now = datetime.now(timezone)
    current_time_str = now.strftime("%Y-%m-%d | %H:%M:%S")

    # 2. إعداد الرسالة النهائية (القوانين + التحديث)
    final_message = RULES_MESSAGE + f"\n\nآخر تحديث لهذه القوانين: **{current_time_str}**"

    # 3. إنشاء لوحة المفاتيح InlineKeyboardMarkup
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # أزرار الروابط الخارجية
    btn_channel = types.InlineKeyboardButton("📢 قناة البوت", url="https://t.me/topcash2005") 
    btn_withdraw_channel = types.InlineKeyboardButton("💰 قناة السحب", url="https://t.me/Topcash124") 
    btn_owner = types.InlineKeyboardButton("🧑‍💻 المالك", url="https://t.me/A_E20877")
    btn_back = types.InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main_menu")
    
    # زر الرجوع (callback_data)
    
    # إضافة الأزرار إلى لوحة المفاتيح
    markup.add(btn_channel, btn_withdraw_channel) 
    markup.add(btn_owner, btn_back) 

    # 4. إرسال الرسالة الجديدة
    bot.send_message(
        chat_id=call.message.chat.id,
        text=final_message,
        reply_markup=markup, 
        parse_mode='Markdown' # للاستفادة من التنسيق الغامق (**)
    )
            
    # 5. إنهاء الاستعلام
    bot.answer_callback_query(call.id, "تم عرض القوانين الهامة.")


@bot.callback_query_handler(func=lambda call: call.data == "claim_daily_gift_inline")
def claim_daily_gift_callback(call):
    if not is_bot_active(call.message):
        return bot.answer_callback_query(call.id, "❌ البوت متوقف مؤقتاً.")
        
    user_id = str(call.from_user.id)
    users = load_users()
    settings = load_edit()

    if user_id not in users or users[user_id].get("banned", False):
        return bot.answer_callback_query(call.id, "❌ لقد تم حظرك من استخدام هذا البوت.")

    u = users[user_id]
    rank = get_rank(u["points"])

    if "daily_gifts" not in u:
        u["daily_gifts"] = 0

    now = datetime.now()
    last_claim_str = u.get("last_claim")
    can_claim = True

    if last_claim_str:
        last_claim_time = datetime.strptime(last_claim_str, "%Y-%m-%d %H:%M:%S")
        if now - last_claim_time < timedelta(days=1):
            can_claim = False
            time_remaining = timedelta(days=1) - (now - last_claim_time)
            hours_left, remainder = divmod(time_remaining.seconds, 3600)
            minutes_left, _ = divmod(remainder, 60)
    
    if can_claim:
        daily_gift_amount = settings.get("daily_gift_points", 10) 

        u["points"] += daily_gift_amount
        u["last_claim"] = now.strftime("%Y-%m-%d %H:%M:%S")
        u["daily_gifts"] += 1

        save_users(users)

        bot.answer_callback_query(call.id, f"🎁 تهانينا! حصلت على {daily_gift_amount} نقطة.", show_alert=True)
        # تعديل رسالة المنيو الرئيسية لتحديث زر الهدية
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=get_main_menu_markup(user_id))
    else:
        bot.answer_callback_query(call.id, f"⏳ الوقت المتبقي: {hours_left} س و {minutes_left} د.", show_alert=True)

# معالج عرض السلع
@bot.callback_query_handler(func=lambda call: call.data == "show_products_menu")
def buy_product_callback(call):
    if not is_bot_active(call.message):
        return bot.answer_callback_query(call.id, "❌ البوت متوقف مؤقتاً.")
        
    user_id = str(call.from_user.id)
    users = load_users()
    if user_id not in users or users[user_id].get("banned", False):
        return bot.answer_callback_query(call.id, "❌ لقد تم حظرك من استخدام هذا البوت.")
        
    products = load_products()

    if not products:
        bot.answer_callback_query(call.id, "لا توجد سلع حالياً.")
        return

    markup = types.InlineKeyboardMarkup(row_width=1)
    for name, data in products.items():
        markup.add(types.InlineKeyboardButton(f"{name} - {data['price']} نقطة", callback_data=f"select_buy:{name}"))
        
    markup.add(types.InlineKeyboardButton("⬅️ رجوع للقائمة الرئيسية", callback_data="back_to_main_menu"))
         
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="اختر السلعة التي تريد شراءها:", 
        reply_markup=markup
    )
    bot.answer_callback_query(call.id)

# معالج اختيار سلعة محددة للشراء
@bot.callback_query_handler(func=lambda call: call.data.startswith("select_buy:"))
def handle_select_purchase(call):
    item_full_name = call.data.split(":")[1]
    products = load_products()
    
    if item_full_name in products:
        price = products[item_full_name]["price"]
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("✅ نعم", callback_data=f"confirm_buy:{item_full_name}"),
            types.InlineKeyboardButton("❌ لا", callback_data="back_to_main_menu")
        )
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"هل تريد شراء {item_full_name} مقابل {price} نقطة؟", 
            reply_markup=markup
        )
    else:
        bot.answer_callback_query(call.id, "السلعة غير موجودة.")

# معالج تأكيد الشراء (منطق إضافة العداد إلى a.json)
@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_buy:"))
def confirm_purchase(call):
    user_id = str(call.from_user.id)
    users = load_users()
    products = load_products()

    if user_id not in users or users[user_id].get("banned", False):
        return bot.answer_callback_query(call.id, "❌ لقد تم حظرك من استخدام هذا البوت.")

    item_full_name = call.data.split(":")[1]
    
    if item_full_name not in products:
        return bot.answer_callback_query(call.id, "❌ السلعة غير موجودة.")

    product_data = products[item_full_name]
    price = product_data["price"]

    if users[user_id]["points"] >= price:
        
        # --- خصم النقاط وتحديث المشتريات ---
        users[user_id]["points"] -= price
        users[user_id]["purchases"] += 1
        users[user_id].setdefault("purchases_list", []).append({
            "item": item_full_name,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        # --- منطق سلعة العداد (a.json) ---
        item_name_display = item_full_name
        counter_value = product_data.get("counter", 0)
        
        if product_data.get("is_counter", False) and counter_value > 0:
            a_data = load_a_json()
            current_count = a_data.get(user_id, 0)
            a_data[user_id] = current_count + counter_value
            save_a_json(a_data)
            
            item_name_display = f"{item_full_name} (عداد: +{counter_value} - الإجمالي: {a_data[user_id]})"
        
        save_users(users)
        
        # تعديل الرسالة
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("⬅️ رجوع للقائمة الرئيسية", callback_data="back_to_main_menu"))
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"✅ تم شراء *{item_name_display}* بنجاح!\n" 
                 f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                 f"رصيدك المتبقي: {users[user_id]['points']} نقطة.",
            reply_markup=markup,
            parse_mode="Markdown"
        )
        
        # إشعار للقناة
        bot.send_message(
            CHANNEL_ID2,
            f"""🛒 تم شراء سلعة جديدة:
السلعة: {item_name_display}
السعر: {price} نقطة
من: {users[user_id]['name']} (@{users[user_id].get('username', 'لا يوجد')})
الآيدي: <code>{user_id}</code>
📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}""",
            parse_mode="HTML"
        )
        bot.answer_callback_query(call.id, "✅ تم الشراء بنجاح.")

    else:
        bot.edit_message_text(
            "❌ رصيدك غير كافي لإتمام عملية الشراء.",
            call.message.chat.id,
            call.message.message_id
        )
        bot.answer_callback_query(call.id, "❌ رصيدك غير كافي.")

# معالج مشترياتي
@bot.callback_query_handler(func=lambda call: call.data == "show_purchases_inline")
def show_purchases_callback(call):
    if not is_bot_active(call.message):
        return bot.answer_callback_query(call.id, "❌ البوت متوقف مؤقتاً.")
        
    user_id = str(call.from_user.id)
    users = load_users()
    if user_id not in users or users[user_id].get("banned", False):
        return bot.answer_callback_query(call.id, "❌ لقد تم حظرك من استخدام هذا البوت.")
        
    purchases = users[user_id].get("purchases_list", [])
    
    msg = ""
    if not purchases:
        msg = "لم تقم بأي عملية شراء بعد."
    else:
        msg = "🧾 سجل مشترياتك:\n\n"
        for p in purchases:
            msg += f"- {p['item']} | {p['date']}\n"
            
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("⬅️ رجوع للقائمة الرئيسية", callback_data="back_to_main_menu"))
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=msg,
        reply_markup=markup
    )
    bot.answer_callback_query(call.id)
    

# معالج الكوبون (يطلب إرسال النص)
@bot.callback_query_handler(func=lambda call: call.data == "ask_for_coupon_inline")
def ask_for_coupon_callback(call):
    if not is_bot_active(call.message):
        return bot.answer_callback_query(call.id, "❌ البوت متوقف مؤقتاً.")
        
    user_id = str(call.from_user.id)
    users = load_users()
    if user_id not in users or users[user_id].get("banned", False):
        return bot.answer_callback_query(call.id, "❌ لقد تم حظرك من استخدام هذا البوت.")
        
    # إرسال رسالة جديدة لتسجيل الخطوة التالية
    msg = bot.send_message(call.message.chat.id, "أرسل رمز الكوبون الذي تريد استخدامه:")
    bot.register_next_step_handler(msg, redeem_coupon_code)
    bot.answer_callback_query(call.id)


def redeem_coupon_code(message):
    """تفعيل الكوبون."""
    code = message.text.strip()
    user_id = str(message.from_user.id)
    users = load_users()
    coupons = load_coupons()

    if code in coupons:
        coupon = coupons[code]

        if user_id in coupon.get("used_by", []):
            bot.send_message(message.chat.id, "❌ لقد استخدمت هذا الكوبون من قبل.")
            return
        
        if len(coupon.get("used_by", [])) >= coupon.get("max_uses", float('inf')):
            bot.send_message(message.chat.id, "❌ تم استهلاك الكوبون بالكامل.")
            return
        
        # ********** 🚨 منطق التحقق من الانتهاء المعدل 🚨 **********
        expires_at_str = coupon.get("expires_at")
        
        # الشرط الجديد: نتجاهل التحقق إذا كانت القيمة "لا يوجد" أو غير موجودة أصلاً
        if expires_at_str and expires_at_str != "لا يوجد":
            try:
                # يجب التأكد من استيراد datetime وتعيين timezone في بداية الملف
                expire_time = datetime.strptime(expires_at_str, "%Y-%m-%d %H:%M:%S")
                
                # ملاحظة: إذا كنت تستخدم توقيت المنطقة الزمنية (timezone)، استخدم هذا السطر:
                # expire_time = datetime.strptime(expires_at_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone)
                # now = datetime.now(timezone) 
                
                if datetime.now() > expire_time:
                    bot.send_message(message.chat.id, "❌ انتهت صلاحية هذا الكوبون.")
                    return
            except ValueError:
                # يمكن إضافة معالجة بسيطة للخطأ هنا، لكن الكود سيستمر في العمل إذا حدث خطأ غير متوقع في التاريخ
                pass 
        # *********************************************************

        # يتم حذف كتلة try-except KeyError السابقة لأننا نتحقق الآن من القيمة
            
        users[user_id]["points"] += coupon["points"]
        coupon.setdefault("used_by", []).append(user_id)
        
        save_users(users)
        save_coupons(coupons)

        badge = get_badge(users[user_id])
        bot.send_message(message.chat.id, f"✅ تم تفعيل الكوبون!\nتمت إضافة {coupon['points']} نقطة.\nرصيدك الحالي: {users[user_id]['points']}")

        bot.send_message(
            CHANNEL_ID,
            f"🎫 كوبون مستخدم!\n"
            f"الاسم: {message.from_user.first_name}\n"
            f"اليوزر: @{message.from_user.username or 'لا يوجد'}\n"
            f"الآيدي: <code>{user_id}</code>\n"
            f"النقاط المضافة: {coupon['points']}\n"
            f"الشارة: {badge}",
            parse_mode="HTML"
        )
    else:
        bot.send_message(message.chat.id, "❌ الكوبون غير صحيح.")

# --- منطق الأدمن والإدارة (Admin Panel) ---

@bot.message_handler(commands=["admin"])
def admin_panel(message):
    user_id = str(message.from_user.id)
    users = load_users()

    if user_id != ADMIN_ID and users.get(user_id, {}).get("role") != "admin":
        bot.send_message(message.chat.id, "❌ ليس لديك صلاحية الوصول إلى لوحة التحكم.")
        return

    # استخدام ReplyKeyboardMarkup هنا لأنه يمثل لوحة تحكم الأدمن
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("إيقاف البوت", "تشغيل البوت")
    markup.add("🔒 حظر مستخدم", "🔓 إلغاء الحظر")
    markup.add("🆕 إضافة سلعة", "🗑 حذف سلعة")
    markup.add("🚫 إيقاف الإرسال", "✅ تفعيل الإرسال")
    markup.add("➕ إضافة وكيل", "➖ إزالة وكيل")
    markup.add("➕ إضافة عداد","➖ مسح عداد")
    markup.add("➕ تعيين نقاط الدعوة", "🎁 تعيين نقاط الهدية")
    markup.add("➕ إرسال نقاط","خصم نقاط")
    markup.add("تصفير الكل")
    markup.add("اذاعة", "رفع ادمن")
    markup.add("📨 ارسال الى مستخدم")
    markup.add("🧼 تصفير الدعوة")
    markup.add("سجل الكوبون","انشاء كوبون")
    markup.add("📊 عرض الإحصائيات")
    markup.add("📋 عرض جميع الإعدادات")
    markup.add("📄 جلب الملفات")
    markup.add("إعادة ضبط المصنع")
    
     
    bot.send_message(message.chat.id, f"""<b>⚙️ لوحة التحكم - الأدمن</b>

مرحباً بك في لوحة التحكم الخاصة بالأدمن.

<b>📊 الأوامر المتاحة:</b>
• 🏆 لعرض المتصدرين بالنقاط: /top
• 📁 لعرض ملف الأعضاء: /userss
• ℹ️ لعرض معلومات مستخدم عن طريق الآيدي: /info
• 💸 لإرسال نقاط لمستخدم معين كـ مرسل: /send

<b>🆔 آيديك:</b> <code>{user_id}</code>
""", reply_markup=markup, parse_mode="HTML")
# 🚨 هام: تأكد من وجود المتغيرات: ADMIN_ID و user_states و load_agents

@bot.message_handler(func=lambda message: message.text in ["➕ إضافة وكيل", "➖ إزالة وكيل"] and str(message.from_user.id) == ADMIN_ID)
def agent_management_reply_buttons(message):
    chat_id = message.chat.id
    
    if message.text == '➕ إضافة وكيل':
        # بدء عملية الإضافة (كما في الخطوة السابقة)
        user_states[chat_id] = {'state': 'waiting_for_agent_id', 'data': {}}
        bot.send_message(chat_id, "✅ **بدء إضافة وكيل**\n\nالرجاء إرسال **آيدي** الوكيل الجديد (مثل 1234567890).")
    
    elif message.text == '➖ إزالة وكيل':
        # بدء عملية الإزالة (كما في الخطوة السابقة)
        agents = load_agents()
        if not agents:
            bot.send_message(chat_id, "❌ لا يوجد وكلاء لإزالتهم حاليًا.")
            return

        # عرض قائمة الوكلاء الحاليين
        agent_list = "\n".join([f"• {data['name']} (ID: `{agent_id}`)" for agent_id, data in agents.items()])
        
        user_states[chat_id] = {'state': 'waiting_for_agent_id_to_remove'}
        bot.send_message(chat_id, 
            text=f"🗑️ **بدء إزالة وكيل**\n\nالرجاء إرسال **آيدي** الوكيل المراد حذفه.\n\n**الوكلاء الحاليون:**\n{agent_list}\n\n**تحذير:** لا يمكن التراجع عن هذه العملية.",
            parse_mode="Markdown"
        )
@bot.callback_query_handler(func=lambda call: call.data in ['admin_add_agent', 'admin_remove_agent'])
def agent_management_callbacks(call):
    # التأكد من أن المستخدم هو الأدمن
    if str(call.from_user.id) != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ أنت لست المسؤول.")
        return

    chat_id = call.message.chat.id
    
    if call.data == 'admin_add_agent':
        # بدء عملية الإضافة
        user_states[chat_id] = {'state': 'waiting_for_agent_id', 'data': {}}
        bot.edit_message_text(
            chat_id=chat_id, 
            message_id=call.message.message_id, 
            text="✅ **بدء إضافة وكيل**\n\nالرجاء إرسال **آيدي** الوكيل الجديد (مثل 1234567890).",
            reply_markup=None # إزالة الأزرار لمنع التفاعل أثناء الإدخال
        )
    
    elif call.data == 'admin_remove_agent':
        # بدء عملية الإزالة
        agents = load_agents()
        if not agents:
            bot.answer_callback_query(call.id, "❌ لا يوجد وكلاء لإزالتهم حاليًا.")
            return

        # عرض قائمة الوكلاء الحاليين لمساعدة الأدمن
        agent_list = "\n".join([f"• {data['name']} (ID: `{agent_id}`)" for agent_id, data in agents.items()])
        
        user_states[chat_id] = {'state': 'waiting_for_agent_id_to_remove'}
        bot.edit_message_text(
            chat_id=chat_id, 
            message_id=call.message.message_id, 
            text=f"🗑️ **بدء إزالة وكيل**\n\nالرجاء إرسال **آيدي** الوكيل المراد حذفه.\n\n**الوكلاء الحاليون:**\n{agent_list}\n\n**تحذير:** لا يمكن التراجع عن هذه العملية.",
            parse_mode="Markdown",
            reply_markup=None
        )

# ----------------------------------------------------------------------
# 2. معالج رسائل المستخدم (Message Handler)
# ----------------------------------------------------------------------

@bot.message_handler(func=lambda message: message.chat.id in user_states and str(message.from_user.id) == ADMIN_ID)
def agent_management_message_handler(message):
    chat_id = message.chat.id
    user_state = user_states.get(chat_id, {})
    
    # --- عملية إضافة وكيل (متعددة الخطوات) ---
    if user_state.get('state') == 'waiting_for_agent_id':
        try:
            agent_id = str(int(message.text.strip()))
            agents = load_agents()
            
            if agent_id in agents:
                bot.send_message(chat_id, f"❌ **خطأ:** الوكيل بالآيدي `{agent_id}` موجود بالفعل باسم: {agents[agent_id]['name']}. تم إلغاء العملية.")
                del user_states[chat_id]
                return
            
            user_state['data']['id'] = agent_id
            user_state['state'] = 'waiting_for_agent_name'
            bot.send_message(chat_id, "☑️ تم استلام الآيدي.\nالآن، الرجاء إرسال **اسم** الوكيل (مثل وكيل مبيعات احمد).")
            
        except ValueError:
            bot.send_message(chat_id, "❌ **خطأ:** الآيدي يجب أن يكون رقماً صحيحاً. حاول مرة أخرى.")
            
    elif user_state.get('state') == 'waiting_for_agent_name':
        agent_name = message.text.strip()
        if not agent_name:
            bot.send_message(chat_id, "❌ **خطأ:** لا يمكن أن يكون الاسم فارغاً. حاول مرة أخرى.")
            return

        user_state['data']['name'] = agent_name
        user_state['state'] = 'waiting_for_agent_role'
        user_state['data']['balance'] = 99999999999999999 # الرصيد الافتراضي
        
        bot.send_message(chat_id, "☑️ تم استلام الاسم.\nالآن، الرجاء إرسال **دور** الوكيل (مثل agent, shop_admin, المدير).")

    elif user_state.get('state') == 'waiting_for_agent_role':
        agent_role = message.text.strip()
        if not agent_role:
            bot.send_message(chat_id, "❌ **خطأ:** لا يمكن أن يكون الدور فارغاً. حاول مرة أخرى.")
            return

        user_state['data']['role'] = agent_role
        user_state['state'] = 'waiting_for_agent_account_link' # ⬅️ الخطوة الجديدة الأولى
        bot.send_message(chat_id, "☑️ تم استلام الدور.\nالآن، الرجاء إرسال **رابط حساب** الوكيل الخاص به (مثلاً: https://t.me/username).")

    elif user_state.get('state') == 'waiting_for_agent_account_link': # ⬅️ الخطوة الجديدة الثانية
        account_link = message.text.strip()
        if not account_link:
            bot.send_message(chat_id, "❌ **خطأ:** لا يمكن أن يكون رابط الحساب فارغاً. حاول مرة أخرى.")
            return

        user_state['data']['account_link'] = account_link
        user_state['state'] = 'waiting_for_agent_channel_link' # ⬅️ الخطوة النهائية للإضافة
        bot.send_message(chat_id, "☑️ تم استلام رابط الحساب.\n\nأخيراً، الرجاء إرسال **رابط قناة** الوكيل (إذا لم يكن لديه قناة، أرسل `لا يوجد`).")


    elif user_state.get('state') == 'waiting_for_agent_channel_link': # ⬅️ خطوة الحفظ النهائية
        channel_link = message.text.strip()
        
        # معالجة إدخال "لا يوجد"
        if channel_link == 'لا يوجد':
             channel_link_to_save = 'N/A'
        elif not channel_link:
             # إذا أرسل فراغاً، يمكن افتراض عدم وجود رابط أو استخدام رابط الحساب
             channel_link_to_save = 'N/A' 
        else:
             channel_link_to_save = channel_link
        
        # تجميع البيانات
        new_agent_id = user_state['data']['id']
        new_agent_data = {
            'name': user_state['data']['name'],
            'balance': user_state['data']['balance'],
            'role': user_state['data']['role'],
            # 🆕 إضافة الروابط الجديدة
            'account_link': user_state['data']['account_link'], 
            'channel_link': channel_link_to_save
        }
        
        # حفظ الوكيل الجديد في ملف agents.json
        agents = load_agents()
        agents[new_agent_id] = new_agent_data
        save_agents(agents)
        
        confirmation_msg = (
            "✅ <b>تمت إضافة الوكيل بنجاح!</b>\n\n"
            f"<b>الآيدي:</b> <code>{new_agent_id}</code>\n"
            f"<b>الاسم:</b> {new_agent_data['name']}\n"
            f"<b>الدور:</b> {new_agent_data['role']}\n"
            f"<b>رابط الحساب:</b> <code>{new_agent_data['account_link']}</code>\n"
            f"<b>رابط القناة:</b> <code>{new_agent_data['channel_link']}</code>\n"
            f"<b>الرصيد الافتراضي:</b> <code>{new_agent_data['balance']}</code>"
        )
        # 🚨 إرسال الرسالة بوضعية HTML لتطبيق تنسيق الغامق والنسخ
        bot.send_message(chat_id, confirmation_msg, parse_mode="HTML")
        del user_states[chat_id] # مسح الحالة والانتهاء من العملية
        
    # --- عملية إزالة وكيل (لم تتغير) ---
    elif user_state.get('state') == 'waiting_for_agent_id_to_remove':
        try:
            agent_id_to_remove = str(int(message.text.strip()))
            agents = load_agents()
            
            if agent_id_to_remove not in agents:
                bot.send_message(chat_id, f"❌ **خطأ:** الوكيل بالآيدي `{agent_id_to_remove}` غير موجود في الملف. حاول مرة أخرى.")
                return

            removed_agent_name = agents[agent_id_to_remove]['name']

            # إزالة الوكيل والحفظ في ملف agents.json
            del agents[agent_id_to_remove]
            save_agents(agents)
            
            bot.send_message(chat_id, 
                             f"✅ **تمت إزالة الوكيل بنجاح!**\n\n"
                             f"تم حذف الوكيل: **{removed_agent_name}** بالآيدي `{agent_id_to_remove}`.")
            del user_states[chat_id] # مسح الحالة والانتهاء من العملية

        except ValueError:
            bot.send_message(chat_id, "❌ **خطأ:** الآيدي يجب أن يكون رقماً صحيحاً. حاول مرة أخرى.")

@bot.message_handler(func=lambda m: m.text in [ "🔒 حظر مستخدم", "🔓 إلغاء الحظر", "➕ إرسال نقاط", "🆕 إضافة سلعة", "🗑 حذف سلعة", "📊 عرض الإحصائيات", "خصم نقاط", "اذاعة", "رفع ادمن", "تصفير الكل","سجل الكوبون","➕ إضافة عداد","➖ مسح عداد" ,"🚫 إيقاف الإرسال", "✅ تفعيل الإرسال","انشاء كوبون","إيقاف البوت", "تشغيل البوت","إعادة ضبط المصنع","➕ تعيين نقاط الدعوة", "🎁 تعيين نقاط الهدية","📋 عرض جميع الإعدادات","🧼 تصفير الدعوة","📨 ارسال الى مستخدم", "➕ إضافة وكيل", "➖ إزالة وكيل", "📄 جلب الملفات"])
def handle_admin_actions(message):
    """معالج للتعامل مع جميع إجراءات الأدمن من الأزرار."""
    user_id = str(message.from_user.id)
    users = load_users()

    if user_id != ADMIN_ID and users.get(user_id, {}).get("role") != "admin":
        bot.send_message(message.chat.id, "❌ لا تملك صلاحية تنفيذ هذا الإجراء.")
        return
        
    action = message.text

    if action == "🆕 إضافة سلعة":
        msg = "أرسل اسم السلعة ثم فراغ ثم السعر (مثال: ساعة 100).\n*لإضافة سلعة عداد:* أرسل `عداد [القيمة] [السعر]` مثل: `عداد 100 1600`"
        bot.send_message(message.chat.id, msg)
        bot.register_next_step_handler(message, add_product)

    elif action == "تصفير الكل":
        reset_all_users_points(message)    
    elif action == "➕ إضافة عداد":
        bot.send_message(message.chat.id, "أرسل الآيدي متبوعاً بعدد النقاط التي تريد *إضافتها* لعداد a.json، مثلًا:\n`123456789 100`", parse_mode="Markdown")
        bot.register_next_step_handler(message, add_to_json)

    elif action == "➖ مسح عداد":
        bot.send_message(message.chat.id, "أرسل آيدي المستخدم لمسح قيمة عداده في a.json.")
        bot.register_next_step_handler(message, clear_a_json_count)
        
    elif action == "إعادة ضبط المصنع":
        msg = bot.send_message(message.chat.id, "⚠️ تحذير: سيتم مسح جميع البيانات (نقاط، مشتريات، إعدادات) وإعادة تعيين البوت.\nأرسل كلمة السر (`علي`) لتأكيد العملية.")
        bot.register_next_step_handler(msg, factory_reset_confirmation)

    elif action == "🔒 حظر مستخدم":
        msg = bot.send_message(message.chat.id, "أرسل آيدي المستخدم الذي تريد حظره:")
        bot.register_next_step_handler(msg, ban_user)
        
    elif action == "🔓 إلغاء الحظر":
        msg = bot.send_message(message.chat.id, "أرسل آيدي المستخدم الذي تريد إلغاء حظره:")
        bot.register_next_step_handler(msg, unban_user)

    elif action == "➕ إرسال نقاط":
        msg = bot.send_message(message.chat.id, "أرسل آيدي المستخدم وعدد النقاط التي تريد إرسالها (مثال: 12345 500):")
        bot.register_next_step_handler(msg, send_points_to_user)

    elif action == "خصم نقاط":
        msg = bot.send_message(message.chat.id, "أرسل آيدي المستخدم وعدد النقاط التي تريد خصمها (مثال: 12345 500):")
        bot.register_next_step_handler(msg, deduct_points)
        
    elif action == "رفع ادمن":
        msg = bot.send_message(message.chat.id, "أرسل آيدي المستخدم لتعيينه كـ 'ادمن' مساعد:")
        bot.register_next_step_handler(msg, promote_admin)

    elif action == "🗑 حذف سلعة":
        products = load_products()
        if not products:
            bot.send_message(message.chat.id, "لا توجد سلع لحذفها.")
            return

        product_list = "\n".join([f"- {name}" for name in products.keys()])
        msg = bot.send_message(message.chat.id, f"أرسل اسم السلعة التي تريد حذفها بالضبط:\n{product_list}")
        bot.register_next_step_handler(msg, delete_product)

    elif action == "اذاعة":
        msg = bot.send_message(message.chat.id, "أرسل رسالة الإذاعة التي تريد إرسالها لجميع المستخدمين:")
        bot.register_next_step_handler(msg, broadcast_message)

    elif action == "📨 ارسال الى مستخدم":
        msg = bot.send_message(message.chat.id, "أرسل آيدي المستخدم ثم الرسالة (مثال: 12345 مرحبا بك):")
        bot.register_next_step_handler(msg, send_message_to_user)
        
    elif action == "🧼 تصفير الدعوة":
        msg = bot.send_message(message.chat.id, "أرسل آيدي المستخدم لتصفير عداد دعواته:")
        bot.register_next_step_handler(msg, clear_referrals)

    elif action == "➕ تعيين نقاط الدعوة":
        msg = bot.send_message(message.chat.id, "أرسل قيمة نقاط الدعوة الجديدة:")
        bot.register_next_step_handler(msg, set_referral_points)

    elif action == "🎁 تعيين نقاط الهدية":
        msg = bot.send_message(message.chat.id, "أرسل قيمة نقاط الهدية اليومية الجديدة:")
        bot.register_next_step_handler(msg, set_daily_gift_points)

    elif action == "🚫 إيقاف الإرسال":
        bot.send_message(message.chat.id, "تم إيقاف الإرسال التلقائي للعدادات.")
        config = load_config()
        config["auto_send_enabled"] = False
        save_config(config)

    elif action == "✅ تفعيل الإرسال":
        bot.send_message(message.chat.id, "تم تفعيل الإرسال التلقائي للعدادات.")
        config = load_config()
        config["auto_send_enabled"] = True
        save_config(config)

    elif action == "إيقاف البوت":
        msg = bot.send_message(message.chat.id, "🛑 أرسل سبب إيقاف البوت:")
        bot.register_next_step_handler(msg, get_stop_reason)

    elif action == "تشغيل البوت":
        bot.send_message(message.chat.id, "تم إعادة تشغيل البوت.")
        status = load_bot_status()
        status["active"] = True
        status["reason"] = "البوت في وضع التشغيل"
        status["resume_time"] = ""
        save_bot_status(status)

    elif action == "📊 عرض الإحصائيات":
        display_stats(message)
def reset_all_users_points(message):
    users = load_users()
    for uid in users:
        users[uid]["points"] = 0
    save_users(users)

    for uid in users:
        try:
            bot.send_message(uid, "⚠️ تم تصفير رصيدك من النقاط من قبل الإدارة.")
        except:
            continue

    bot.send_message(message.chat.id, "✅ تم تصفير النقاط لجميع المستخدمين وإبلاغهم.")
def delete_product(message):
    item_name = message.text.strip()
    products = load_products()

    if item_name in products:
        del products[item_name]
        save_products(products)
        bot.send_message(message.chat.id, f"✅ تم حذف السلعة: {item_name}")
    else:
        bot.send_message(message.chat.id, "❌ لم يتم العثور على السلعة بهذا الاسم.")

def factory_reset_confirmation(message):
    if message.text.strip().lower() == FACTORY_RESET_PASSWORD:
        # مسح جميع الملفات وإعادة إنشائها
        files_to_reset = ["users.json", "products.json", "a.json", "edit.json", "config.json", "bot_status.json", "coupons.json", "withdrawals.json"]
        for f in files_to_reset:
            if os.path.exists(f):
                os.remove(f)
        
        initialize_files() # إعادة إنشاء الملفات بالقيم الافتراضية
        
        bot.send_message(message.chat.id, "✅ تم إعادة ضبط المصنع بنجاح. تم مسح جميع بيانات المستخدمين والسلع والإعدادات.")
    else:
        bot.send_message(message.chat.id, "❌ كلمة السر غير صحيحة. تم إلغاء عملية إعادة ضبط المصنع.")

def get_stop_reason(message):
    reason = message.text.strip()
    msg = bot.send_message(message.chat.id, "⏱️ أرسل مدة الإيقاف (بالثواني أو الساعات):")
    bot.register_next_step_handler(msg, get_stop_duration, reason)

def get_stop_duration(message, reason):
    try:
        duration_input = message.text.strip()
        if duration_input.endswith("s"):
            seconds = int(duration_input[:-1])
        elif duration_input.endswith("h"):
            seconds = int(duration_input[:-1]) * 3600
        else:
            seconds = int(duration_input)
    except:
        bot.send_message(message.chat.id, "❌ أرسل وقت صحيح، مثل: 60s أو 1h أو فقط رقم.")
        return

    resume_time = (datetime.now() + timedelta(seconds=seconds)).strftime("%Y-%m-%d %H:%M:%S")
    save_bot_status({"active": False, "reason": reason, "resume_time": resume_time})

    msg = f"""❌ تم إيقاف البوت مؤقتاً.
السبب: {reason}
⏳ يعود للعمل في: {resume_time}"""

    # نشر للمستخدمين والقناة
    users = load_users()
    for uid in users:
        try:
            bot.send_message(uid, msg)
        except:
            continue
    bot.send_message(CHANNEL_ID, msg)

def display_stats(message):
    users = load_users()
    total_users = len(users)
    total_points = sum(u.get("points", 0) for u in users.values())
    total_purchases = sum(u.get("purchases", 0) for u in users.values())
    
    a_data = load_a_json()
    total_a_points = sum(a_data.values())

    msg = f"""
📊 **إحصائيات البوت:**

👥 إجمالي المستخدمين: *{total_users}*
💰 إجمالي النقاط الموزعة: *{total_points}* نقطة
🛒 إجمالي المشتريات المنجزة: *{total_purchases}* عملية
➕ إجمالي نقاط العداد (a.json): *{total_a_points}* نقطة
"""
    bot.send_message(message.chat.id, msg, parse_mode="Markdown")

def display_settings(message):
    edit_settings = load_edit()
    config_settings = load_config()
    
    msg = f"""
📋 **إعدادات البوت الحالية:**

**إعدادات النقاط:**
• نقاط الدعوة (referral_points): *{edit_settings.get("referral_points", "غير محدد")}*
• نقاط الهدية اليومية (daily_gift_points): *{edit_settings.get("daily_gift_points", "غير محدد")}*

**إعدادات العداد (a.json):**
• حالة الإرسال التلقائي (auto_send_enabled): *{'مفعل' if config_settings.get('auto_send_enabled', True) else 'متوقف'}*
"""
    bot.send_message(message.chat.id, msg, parse_mode="Markdown")

def set_referral_points(message):
    try:
        points = int(message.text.strip())
        edit = load_edit()
        edit["referral_points"] = points
        save_edit(edit)
        bot.send_message(message.chat.id, f"✅ تم تعيين نقاط الدعوة الجديدة إلى: {points} نقطة.")
    except ValueError:
        bot.send_message(message.chat.id, "❌ خطأ: يجب أن تكون قيمة صحيحة.")

def set_daily_gift_points(message):
    try:
        points = int(message.text.strip())
        edit = load_edit()
        edit["daily_gift_points"] = points
        save_edit(edit)
        bot.send_message(message.chat.id, f"✅ تم تعيين نقاط الهدية اليومية الجديدة إلى: {points} نقطة.")
    except ValueError:
        bot.send_message(message.chat.id, "❌ خطأ: يجب أن تكون قيمة صحيحة.")

# الدالة المخصصة لإضافة العداد إلى a.json
def add_to_json(message):
    try:
        parts = message.text.split()
        if len(parts) != 2:
            bot.send_message(message.chat.id, "صيغة غير صحيحة. يجب أن تكون: [آيدي المستخدم] [عدد النقاط للعداد].")
            return

        target_user_id = parts[0]
        points_to_add = int(parts[1])

        a_data = load_a_json()
        
        current_count = a_data.get(target_user_id, 0)
        a_data[target_user_id] = current_count + points_to_add
        
        save_a_json(a_data)

        bot.send_message(message.chat.id, f"✅ تم إضافة {points_to_add} نقطة إلى عداد المستخدم `{target_user_id}` في ملف a.json.\nالقيمة الإجمالية الآن: {a_data[target_user_id]}", parse_mode="Markdown")
        
    except ValueError:
        bot.send_message(message.chat.id, "❌ خطأ: العداد يجب أن يكون رقماً صحيحاً.")
    except Exception as e:
        bot.send_message(message.chat.id, f"حدث خطأ غير متوقع: {str(e)}")

# الدالة المخصصة لمسح عداد a.json
def clear_a_json_count(message):
    target_user_id = message.text.strip()
    a_data = load_a_json()
    
    if target_user_id in a_data:
        a_data[target_user_id] = 0 # أو del a_data[target_user_id] حسب الرغبة، نختار التصفير
        save_a_json(a_data)
        bot.send_message(message.chat.id, f"✅ تم مسح عداد المستخدم `{target_user_id}` في ملف a.json. القيمة أصبحت 0.")
    else:
        bot.send_message(message.chat.id, f"❌ المستخدم `{target_user_id}` ليس لديه قيمة في ملف a.json.")

# دالة إضافة السلعة (تم تعديلها لدعم منطق العداد)
def add_product(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.send_message(message.chat.id, "صيغة غير صحيحة. يجب أن تكون: [اسم السلعة] [السعر] أو [عداد القيمة] [السعر].")
            return

        price = int(parts[-1])
        item_full_name = " ".join(parts[:-1]) 
        
        counter_value = 0
        is_counter_item = False
        
        # منطق التحقق من صيغة العداد: "عداد [القيمة]"
        name_parts = item_full_name.split()
        if len(name_parts) >= 2 and name_parts[0].lower() == "عداد":
             try:
                # القيمة تكون في الجزء التالي مباشرة
                counter_value = int(name_parts[1]) 
                is_counter_item = True
             except ValueError:
                 pass 

        products = load_products()
        
        products[item_full_name.strip()] = {
            "price": price, 
            "is_counter": is_counter_item, 
            "counter": counter_value
        }
        save_products(products)

        bot.send_message(message.chat.id, f"✅ تم إضافة السلعة: {item_full_name.strip()} بسعر {price} نقطة. (سلعة عداد: {'نعم' if is_counter_item else 'لا'})")

    except ValueError:
        bot.send_message(message.chat.id, "❌ خطأ: السعر أو العداد يجب أن يكون رقماً صحيحاً.")
    except Exception as e:
        bot.send_message(message.chat.id, f"حدث خطأ غير متوقع: {str(e)}")
        
# --- الدوال الأساسية المتبقية (Top, Info, Help, Broadcast, إلخ) ---
# يجب أن يكون هذا المعالج موجوداً لكي تبدأ العملية

@bot.message_handler(commands=['top'])
def top_users(message):
    users = load_users()
    
    # تحويل البيانات إلى قائمة قابلة للفرز
    user_list = []
    for uid, data in users.items():
        user_list.append({
            "id": uid,
            "name": data.get("name", "مستخدم"),
            "points": data.get("points", 0),
            "username": data.get("username", "لا يوجد")
        })

    # فرز المستخدمين بناءً على النقاط
    user_list.sort(key=lambda x: x["points"], reverse=True)

    msg = "🏆 **قائمة المتصدرين بالنقاط:** 🏆\n\n"
    
    for i, user in enumerate(user_list[:10]): # عرض أول 10 متصدرين
        emoji = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"*{i + 1}*"
        
        username_display = f"@{user['username']}" if user['username'] != "لا يوجد" else user['name']
        
        msg += f"{emoji} {username_display} | {user['points']} نقطة\n"

    bot.send_message(message.chat.id, msg, parse_mode="HTML")


@bot.message_handler(commands=['info'])
def get_user_info(message):
    msg = bot.send_message(message.chat.id, "أرسل آيدي المستخدم الذي تريد الحصول على معلوماته:")
    bot.register_next_step_handler(msg, show_user_info)

def show_user_info(message):
    target_id = message.text.strip()
    users = load_users()
    
    if target_id in users:
        u = users[target_id]
        badge = get_badge(u)
        
        # استخراج قيمة العداد من a.json
        a_data = load_a_json()
        counter_value = a_data.get(target_id, 0)
        
        info_msg = f"""
        <b>ℹ️ معلومات المستخدم:</b>

🆔 الآيدي: <code>{target_id}</code>
👤 الاسم: {u.get('name', 'غير معروف')}
🔎 المعرف: @{u.get('username', 'لا يوجد')}

<b>بيانات النقاط والإحصائيات:</b>
💰 الرصيد: {u.get('points', 0)} نقطة
🤝 الدعوات: {u.get('referrals', 0)}
🛒 المشتريات: {u.get('purchases', 0)}
🏅 الشارة: {badge}

<b>حالة العداد (a.json):</b>
🔢 قيمة العداد التلقائي: {counter_value} نقطة

<b>الحالة الإدارية:</b>
🚫 محظور: {'نعم' if u.get('banned', False) else 'لا'}
⭐ الدور: {u.get('role', 'user')}
        """
        bot.send_message(message.chat.id, info_msg, parse_mode="HTML")
    else:
        bot.send_message(message.chat.id, f"❌ لم يتم العثور على مستخدم بالآيدي: {target_id}")


def ban_user(message):
    target_id = message.text.strip()
    users = load_users()
    if target_id in users:
        users[target_id]["banned"] = True
        save_users(users)
        bot.send_message(message.chat.id, f"✅ تم حظر المستخدم ذو الآيدي: {target_id}")
        try:
            bot.send_message(target_id, "❌ لقد تم حظرك من استخدام هذا البوت.")
        except telebot.apihelper.ApiTelegramException: pass
    else:
        bot.send_message(message.chat.id, f"❌ لا يوجد مستخدم بالآيدي: {target_id}")

def unban_user(message):
    target_id = message.text.strip()
    users = load_users()
    if target_id in users:
        users[target_id]["banned"] = False
        save_users(users)
        bot.send_message(message.chat.id, f"✅ تم إلغاء حظر المستخدم ذو الآيدي: {target_id}")
        try:
            bot.send_message(target_id, "✅ تم إلغاء الحظر، يمكنك الآن استخدام البوت.")
        except telebot.apihelper.ApiTelegramException: pass
    else:
        bot.send_message(message.chat.id, f"❌ لا يوجد مستخدم بالآيدي: {target_id}")

def send_points_to_user(message):
    try:
        target_id, points_str = message.text.split()
        points = int(points_str)
        users = load_users()
        if target_id in users:
            users[target_id]["points"] += points
            save_users(users)
            bot.send_message(message.chat.id, f"✅ تم إرسال {points} نقطة للمستخدم: {target_id}")
            try:
                bot.send_message(target_id, f"🎉 تم إضافة {points} نقطة إلى رصيدك من قبل الأدمن.\nرصيدك الحالي: {users[target_id]['points']}")
            except telebot.apihelper.ApiTelegramException: pass
        else:
            bot.send_message(message.chat.id, f"❌ لا يوجد مستخدم بالآيدي: {target_id}")
    except ValueError:
        bot.send_message(message.chat.id, "❌ صيغة غير صحيحة. يجب أن تكون: [آيدي المستخدم] [عدد النقاط].")

def deduct_points(message):
    try:
        target_id, points_str = message.text.split()
        points = int(points_str)
        users = load_users()
        if target_id in users:
            users[target_id]["points"] = max(0, users[target_id]["points"] - points)
            save_users(users)
            bot.send_message(message.chat.id, f"✅ تم خصم {points} نقطة من المستخدم: {target_id}")
            try:
                bot.send_message(target_id, f"⚠️ تم خصم {points} نقطة من رصيدك من قبل الأدمن.\nرصيدك الحالي: {users[target_id]['points']}")
            except telebot.apihelper.ApiTelegramException: pass
        else:
            bot.send_message(message.chat.id, f"❌ لا يوجد مستخدم بالآيدي: {target_id}")
    except ValueError:
        bot.send_message(message.chat.id, "❌ صيغة غير صحيحة. يجب أن تكون: [آيدي المستخدم] [عدد النقاط].")

def promote_sender(message):
    target_id = message.text.strip()
    users = load_users()
    if target_id in users:
        users[target_id]["role"] = "sender"
        save_users(users)
        bot.send_message(message.chat.id, f"✅ تم تعيين المستخدم {target_id} كـ 'مرسل'.")
    else:
        bot.send_message(message.chat.id, f"❌ لا يوجد مستخدم بالآيدي: {target_id}")

def demote_sender(message):
    target_id = message.text.strip()
    users = load_users()
    if target_id in users:
        users[target_id]["role"] = "user"
        save_users(users)
        bot.send_message(message.chat.id, f"✅ تم إزالة صلاحية 'المرسل' من المستخدم {target_id}.")
    else:
        bot.send_message(message.chat.id, f"❌ لا يوجد مستخدم بالآيدي: {target_id}")

def promote_admin(message):
    target_id = message.text.strip()
    users = load_users()
    if target_id in users:
        users[target_id]["role"] = "admin"
        save_users(users)
        bot.send_message(message.chat.id, f"✅ تم تعيين المستخدم {target_id} كـ 'ادمن' مساعد.")
    else:
        bot.send_message(message.chat.id, f"❌ لا يوجد مستخدم بالآيدي: {target_id}")

def broadcast_message(message):
    broadcast_text = message.text
    users = load_users()
    success_count = 0
    fail_count = 0
    
    for uid in users.keys():
        try:
            bot.send_message(uid, broadcast_text)
            success_count += 1
        except telebot.apihelper.ApiTelegramException:
            fail_count += 1
    
    bot.send_message(message.chat.id, f"✅ تم الانتهاء من الإذاعة.\nتم الإرسال بنجاح إلى: {success_count}\nفشل الإرسال إلى: {fail_count}")

def send_message_to_user(message):
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) != 2:
            bot.send_message(message.chat.id, "صيغة غير صحيحة. يجب أن تكون: [آيدي المستخدم] [الرسالة].")
            return

        target_id = parts[0]
        msg_text = parts[1]
        
        try:
            bot.send_message(target_id, f"📬 رسالة خاصة من الأدمن:\n\n{msg_text}")
            bot.send_message(message.chat.id, f"✅ تم إرسال الرسالة بنجاح للمستخدم: {target_id}")
        except telebot.apihelper.ApiTelegramException as e:
            bot.send_message(message.chat.id, f"❌ فشل إرسال الرسالة للمستخدم {target_id}. قد يكون المستخدم قد حظر البوت. (الخطأ: {e})")
            
    except Exception as e:
        bot.send_message(message.chat.id, f"حدث خطأ غير متوقع: {str(e)}")

def clear_referrals(message):
    target_id = message.text.strip()
    users = load_users()
    if target_id in users:
        users[target_id]["referrals"] = 0
        save_users(users)
        bot.send_message(message.chat.id, f"✅ تم تصفير عداد دعوات المستخدم {target_id}.")
    else:
        bot.send_message(message.chat.id, f"❌ لا يوجد مستخدم بالآيدي: {target_id}")
        
@bot.message_handler(commands=['userss'])
def send_users_txt(message):
    users = load_users()
    file_content = "قائمة المستخدمين:\n\n"

    for uid, data in users.items():
        name = data.get('name', 'غير معروف')
        username = f"@{data.get('username')}" if data.get('username') else "لا يوجد"
        points = data.get('points', 0)
        file_content += f"الاسم: {name}\nالمعرف: {username}\nالآيدي: {uid}\nالنقاط: {points}\n\n"

    # الحفظ داخل ملف مؤقت
    with open("users_list.txt", "w", encoding="utf-8") as f:
        f.write(file_content)

    # إرسال الملف
    with open("users.json", "rb") as f:
        bot.send_document(message.chat.id, f)
####3
# --- دوال إدارة بيانات الوكلاء (Agents) ---
AGENTS_FILE = 'agents.json'

def load_agents():
    """تحميل بيانات الوكلاء من ملف JSON."""
    if not os.path.exists(AGENTS_FILE):
        return {}
    with open(AGENTS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_agents(agents_data):
    """حفظ بيانات الوكلاء في ملف JSON."""
    with open(AGENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(agents_data, f, indent=4, ensure_ascii=False)

# لحفظ بيانات التحويل المؤقتة للوكلاء: {sender_id: {'target_id': ID, 'amount': X}}
agent_temp_data = {}
# --- دالة معالج الأمر /agent (لعرض معلومات الوكيل) ---
@bot.message_handler(commands=['agent'])
def agent_info_command(message):
    user_id = str(message.from_user.id)
    agents = load_agents()
    
    # 1. التحقق من أن المستخدم وكيل
    if user_id not in agents:
        bot.send_message(message.chat.id, "❌ عذراً، هذا الأمر مخصص للوكلاء فقط.")
        return

    agent_data = agents[user_id]
    
    # 2. بناء رسالة المعلومات
    agent_msg = f"""
<b>✨ مرحباً بك أيها الوكيل {agent_data.get('name', 'الوكيل')}!</b>

<b>📋 معلومات حساب الوكيل:</b>
<b>🆔 آيدي الوكيل:</b> <code>{user_id}</code>
<b>👤 الاسم:</b> {agent_data.get('name', 'غير معروف')}
<b>🔎 المعرف:</b> @{message.from_user.username or 'لا يوجد'}

<b>💰 رصيد التحويل المتاح:</b> {agent_data.get('balance', 0)} نقطة
<b>⭐ الدور:</b> {agent_data.get('role', 'Agent')}

<b>التعليمات:</b>
لبدء إرسال النقاط، استخدم الأمر:
<code>/send</code>
"""
    
    # 3. إرسال الرسالة
    bot.send_message(message.chat.id, 
                     agent_msg,
                     parse_mode="HTML",
                     disable_web_page_preview=True)
# --- 1. دالة معالج الأمر /send (البدء بطلب الآيدي) ---
@bot.message_handler(commands=['send'])
def start_send_process(message):
    sender_id = str(message.from_user.id)
    agents = load_agents()
    
    # التحقق من أن المرسل وكيل (موجود في agents.json)
    if sender_id not in agents:
        bot.send_message(message.chat.id, "❌ عذراً، لا تمتلك صلاحية استخدام هذا الأمر. هذا الأمر مخصص للوكلاء فقط.")
        return

    agent_data = agents[sender_id]
    
    # إعداد بيانات الوكيل المؤقتة
    agent_temp_data[sender_id] = {'target_id': None, 'amount': None, 'agent_name': agent_data.get('name', 'وكيل')}

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌ إلغاء العملية", callback_data="cancel_agent_send"))

    msg = bot.send_message(message.chat.id, 
                           f"💰 **بدء إرسال النقاط**\n\nرصيدك المتاح للتحويل: **{agent_data.get('balance', 0)}** نقطة.\n\nالرجاء إرسال **آيدي المستخدم** الذي تريد التحويل له:", 
                           reply_markup=markup,
                           parse_mode="Markdown")
                           
    bot.register_next_step_handler(msg, get_target_id)


# --- معالج إلغاء العملية (Callback) ---
@bot.callback_query_handler(func=lambda call: call.data == "cancel_agent_send")
def cancel_agent_send_callback(call):
    sender_id = str(call.from_user.id)
    if sender_id in agent_temp_data:
        del agent_temp_data[sender_id]
        bot.edit_message_text("❌ تم إلغاء عملية إرسال النقاط.", call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id, "تم الإلغاء.")
    else:
        bot.answer_callback_query(call.id, "لا توجد عملية إرسال نشطة للإلغاء.")
# --- 2. استلام الآيدي وعرض معلومات المستلم ---
def get_target_id(message):
    sender_id = str(message.from_user.id)
    users = load_users()
    
    if sender_id not in agent_temp_data:
        return bot.send_message(message.chat.id, "❌ انتهت صلاحية العملية. يرجى البدء مجدداً بالأمر /send.")

    target_id = message.text.strip()
    
    if not target_id.isdigit():
        msg = bot.send_message(message.chat.id, "❌ الآيدي غير صحيح. يجب أن يكون رقماً. أعد إرسال الآيدي:")
        return bot.register_next_step_handler(msg, get_target_id)
        
    if target_id not in users:
        msg = bot.send_message(message.chat.id, f"❌ لا يوجد مستخدم بالآيدي: **{target_id}** في قاعدة بيانات البوت. أعد إرسال الآيدي:")
        return bot.register_next_step_handler(msg, get_target_id)

    # حفظ الآيدي المستهدف مؤقتاً
    agent_temp_data[sender_id]['target_id'] = target_id
    u = users[target_id]
    
    # عرض معلومات المستخدم المستهدف
    info_msg = (
        f"✅ **تم تحديد المستلم:**\n\n"
        f"🆔 الآيدي: <code>{target_id}</code>\n"
        f"👤 الاسم: {u.get('name', 'غير معروف')}\n"
        f"🔎 المعرف: @{u.get('username', 'لا يوجد')}\n\n"
        f"💰 رصيده الحالي: **{u.get('points', 0)}** نقطة."
    )
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌ إلغاء العملية", callback_data="cancel_agent_send"))
    
    msg = bot.send_message(message.chat.id, 
                           info_msg + "\n\nالآن، **كم عدد النقاط** التي تريد إرسالها؟ (أرسل رقم فقط)", 
                           reply_markup=markup,
                           parse_mode="HTML")
                           
    bot.register_next_step_handler(msg, get_amount_and_confirm)
# --- 3. استلام النقاط وتنفيذ التحويل ---
def get_amount_and_confirm(message):
    sender_id = str(message.from_user.id)
    agents = load_agents()
    users = load_users()
    
    if sender_id not in agent_temp_data:
        return bot.send_message(message.chat.id, "❌ انتهت صلاحية العملية. يرجى البدء مجدداً بالأمر /send.")
        
    try:
        amount = int(message.text.strip())
        if amount <= 0:
            raise ValueError
    except ValueError:
        msg = bot.send_message(message.chat.id, "❌ قيمة النقاط غير صحيحة. يجب أن تكون عدداً موجباً. أعد إرسال عدد النقاط:")
        return bot.register_next_step_handler(msg, get_amount_and_confirm)

    target_id = agent_temp_data[sender_id]['target_id']
    agent_data = agents[sender_id]
    
    # التحقق من رصيد الوكيل المخصص للتحويل
    agent_balance = agent_data.get('balance', 0)
    if agent_balance < amount:
        del agent_temp_data[sender_id]
        return bot.send_message(message.chat.id, 
                                f"❌ فشلت العملية! رصيدك كوكيل ({agent_balance} نقطة) غير كافٍ لإرسال **{amount}** نقطة.", 
                                parse_mode="Markdown")

    # --- تنفيذ عملية الإرسال (الخصم والإضافة) ---
    try:
        # 1. خصم النقاط من رصيد الوكيل (في agents.json)
        agents[sender_id]['balance'] -= amount
        save_agents(agents)
        
        # 2. إضافة النقاط للمستلم (في users.json)
        users[target_id]['points'] += amount
        save_users(users)

        # 3. إشعار المرسل (الوكيل)
        bot.send_message(message.chat.id, 
                         f"✅ **تم التحويل بنجاح!**\n\nتم إرسال **{amount}** نقطة إلى المستخدم <code>{target_id}</code>.\nرصيدك المتبقي كوكيل: **{agents[sender_id]['balance']}** نقطة.", 
                         parse_mode="HTML")

        # 4. إشعار المستلم
        try:
            agent_name = agent_data.get('name', 'وكيل/مدير')
            bot.send_message(target_id, 
                             f"💰 **تم استلام نقاط!**\n\nقام الوكيل **{agent_name}** بإرسال **{amount}** نقطة لحسابك.\nرصيدك الجديد: **{users[target_id]['points']}** نقطة.", 
                             parse_mode="Markdown")
        except Exception:
            pass

        # 5. تسجيل العملية في القناة (الإشراف)
        channel_msg = (
            f"**💸 عملية إرسال نقاط جديدة (وكيل):**\n\n"
            f"**الوكيل المُرسل:** {agent_data.get('name', 'غير معروف')} (@{message.from_user.username or 'لا يوجد'})\n"
            f"**آيدي الوكيل:** <code>{sender_id}</code>\n"
            f"**رصيده المتبقي:** {agents[sender_id]['balance']}\n"
            f"**--------------------**\n"
            f"**المستلم:** {users[target_id].get('name', 'غير معروف')} (@{users[target_id].get('username', 'لا يوجد')})\n"
            f"**آيدي المستلم:** <code>{target_id}</code>\n"
            f"**عدد النقاط المُرسلة:** {amount}\n"
        )
        bot.send_message(CHANNEL_ID2, channel_msg, parse_mode="HTML")

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ حدث خطأ غير متوقع أثناء عملية الإرسال: {str(e)}")
        
    finally:
        # مسح البيانات المؤقتة بعد الانتهاء
        if sender_id in agent_temp_data:
            del agent_temp_data[sender_id]
##
AGENTS_FILE = 'agents.json'
def load_agents():
    """تحميل بيانات الوكلاء من agents.json."""
    if not os.path.exists(AGENTS_FILE):
        return {}
    try:
        # قراءة البيانات مع دعم UTF-8 للأحرف العربية
        with open(AGENTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {} # إرجاع قاموس فارغ في حال وجود خطأ في الملف

def save_agents(agents_data):
    """حفظ بيانات الوكلاء إلى agents.json."""
    # ensure_ascii=False للحفاظ على الأحرف العربية، و indent=4 للتنسيق
    with open(AGENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(agents_data, f, indent=4, ensure_ascii=False)
# #            
threading.Thread(target=loan_repayment_checker, daemon=True).start()                            
# --- تشغيل البوت ---
if __name__ == "__main__":

    bot.polling(none_stop=True)
