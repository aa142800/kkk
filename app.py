from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask import session
from datetime import datetime
from flask import Flask, render_template, request, session, redirect, url_for, jsonify, flash
import json
import os

# إنشاء تطبيق Flask:
# هنا نقوم بإنشاء كائن من نوع Flask، وهو النواة الأساسية لتطبيق الويب.
# __name__ هو اسم الملف الحالي، ويستخدم Flask هذا الاسم لتحديد مكان ملفات التطبيق مثل القوالب (templates) والملفات الثابتة (static).
app = Flask(__name__)

app.secret_key = "your_secret_key_here"  # استخدم مفتاحًا فريدًا وسريًا
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
BACKGROUND_FILE = 'background.txt'
RESTAURANT_INFO_FILE = 'restaurant_info.json'  # ملف جديد لتخزين معلومات المطعم

# إنشاء مجلد الصور إذا لم يكن موجودًا
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# تحميل المسار الأخير للصورة المحفوظة
def load_background():
    """
    هذه الدالة تقوم بتحميل مسار الخلفية (الصورة) المخزنة مسبقًا.
    - يتم التحقق من وجود ملف background.txt الذي يحتوي على مسار الصورة.
    - إذا كان الملف موجودًا، يتم قراءة المسار وفحص ما إذا كانت الصورة لا تزال موجودة في المسار.
    - إذا لم يكن الملف موجودًا أو إذا كانت الصورة غير موجودة، يتم إرجاع صورة افتراضية (default.jpg).
    """
    if os.path.exists(BACKGROUND_FILE):
        with open(BACKGROUND_FILE, 'r', encoding='utf-8') as f:
            path = f.read().strip()
            return path if os.path.exists(path) else 'static/uploads/default.jpg'
    return 'static/uploads/default.jpg'

# حفظ المسار الجديد للصورة
def save_background(path):
    """
    هذه الدالة تقوم بحفظ مسار الصورة الجديدة إلى ملف background.txt.
    - يتم كتابة المسار الجديد للصورة في الملف.
    - هذا المسار يمكن استخدامه لاحقًا لعرض الصورة كخلفية للموقع.
    """
    with open(BACKGROUND_FILE, 'w', encoding='utf-8') as f:
        f.write(path)

# تحميل معلومات المطعم
def load_restaurant_info():
    """تحميل معلومات المطعم من ملف JSON"""
    # التحقق من وجود ملف JSON الخاص بمعلومات المطعم
    if os.path.exists(RESTAURANT_INFO_FILE):
        # فتح ملف JSON وقراءة البيانات منه
        with open(RESTAURANT_INFO_FILE, 'r', encoding='utf-8') as f:
            info = json.load(f)  # قراءة بيانات المطعم من الملف
            
            # إضافة قيم افتراضية إذا لم تكن الخصائص موجودة
            info.setdefault('font_size', '24px')  # حجم الخط الافتراضي للنصوص
            info.setdefault('font_color', '#000000')  # لون الخط الافتراضي للنصوص
            info.setdefault('font_family', 'Arial')  # نوع الخط الافتراضي للنصوص
            
            # تحميل إعدادات خط الفئة إذا كانت موجودة
            try:
                # فتح ملف الإعدادات الخاص بخط الفئة وقراءة البيانات منه
                with open('category_font_settings.json', 'r') as font_file:
                    font_settings = json.load(font_file)  # قراءة إعدادات خط الفئة
                    
                    # تعيين حجم خط الفئة مع استبدال الوحدة "px" إذا كانت موجودة
                    info['category_font_size'] = font_settings.get('font_size', '20px').replace('px', '')
                    
                    # تعيين نوع خط الفئة باستخدام القيمة من الإعدادات أو القيمة الافتراضية
                    info['category_font_family'] = font_settings.get('font_family', 'Noto Naskh Arabic')
            except FileNotFoundError:
                # في حالة عدم وجود ملف إعدادات خط الفئة، تعيين القيم الافتراضية
                info['category_font_size'] = '20'
                info['category_font_family'] = 'Noto Naskh Arabic'
            
            return info  # إرجاع بيانات المطعم بعد التعديلات
    # في حالة عدم وجود ملف JSON، يتم إرجاع قيم افتراضية
    return {
        "name": "اسم المطعم",  # اسم المطعم الافتراضي
        "logo": "static/uploads/default_logo.png",  # شعار المطعم الافتراضي
        "font_size": "24px",  # حجم الخط الافتراضي للنصوص
        "font_color": "#000000",  # لون الخط الافتراضي للنصوص
        "font_family": "Arial",  # نوع الخط الافتراضي للنصوص
        "category_font_size": "20",  # حجم خط الفئة الافتراضي
        "category_font_family": "Noto Naskh Arabic"  # نوع خط الفئة الافتراضي
    }

# حفظ معلومات المطعم
def save_restaurant_info(info):
    # حفظ بيانات المطعم في ملف JSON
    with open(RESTAURANT_INFO_FILE, 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=4)  # كتابة البيانات بصيغة JSON مع تجنب ترميز الأحرف غير ASCII وتنسيق النص

# تحميل مسار الخلفية عند بدء تشغيل التطبيق
background_image = load_background()

# تحميل معلومات المطعم عند بدء تشغيل التطبيق
restaurant_info = load_restaurant_info()

def load_menu():
    """تحميل القائمة من ملف JSON"""
    try:
        # فتح ملف القائمة وتحميل البيانات منه
        with open('menu.json', 'r', encoding='utf-8') as file:
            return json.load(file)  # قراءة بيانات القائمة من الملف
    except FileNotFoundError:
        return {}  # إذا لم يكن الملف موجودًا، يتم إرجاع قائمة فارغة

def save_menu(menu):
    """حفظ القائمة في ملف JSON"""
    # حفظ بيانات القائمة في ملف JSON
    with open('menu.json', 'w', encoding='utf-8') as file:
        json.dump(menu, file, ensure_ascii=False, indent=4)  # كتابة بيانات القائمة بصيغة JSON مع تجنب ترميز الأحرف غير ASCII وتنسيق النص

from datetime import datetime

#222================================================================================================

@app.route('/')
def index():
    """عرض القائمة الرئيسية"""
    lang = request.args.get('lang', 'ar')  # الحصول على لغة الواجهة من معلمات الطلب (الافتراضي: العربية)
    menu = load_menu()  # تحميل بيانات القائمة من ملف JSON
    
    # تحميل مسار الخلفية وتحويله إلى مسار يمكن استخدامه في HTML
    bg_image = url_for('static', filename=load_background().replace('static/', ''))
    
    # إضافة معلمة زمنية لتجنب التخزين المؤقت للخلفية في المتصفح
    timestamp = datetime.now().timestamp()
    
    # عرض الصفحة الرئيسية باستخدام قالب HTML وإرسال البيانات اللازمة
    return render_template('index.html', menu=menu, lang=lang, bg_image=bg_image, restaurant_info=restaurant_info, timestamp=timestamp)

@app.route('/update_restaurant_info', methods=['POST'])
def update_restaurant_info():
    """وظيفة الكود: تحديث معلومات المطعم بناءً على البيانات المرسلة من النموذج."""
    global restaurant_info  # استخدام المتغير العام لتخزين معلومات المطعم
    name_ar = request.form.get('name_ar')  # اسم المطعم بالعربية (إجباري)
    name_en = request.form.get('name_en')  # اسم المطعم بالإنجليزية (اختياري)
    logo = request.files.get('logo')  # ملف الشعار الجديد
    
    if name_ar:
        restaurant_info['name'] = name_ar  # تحديث اسم المطعم بالعربية إذا تم إدخاله
    if name_en:  # تحديث الاسم بالإنجليزية فقط إذا تم إدخاله
        restaurant_info['name_en'] = name_en
    if logo:  # إذا تم تحميل شعار جديد
        logo_filename = os.path.join(app.config['UPLOAD_FOLDER'], logo.filename)  # تحديد مسار حفظ الشعار
        logo.save(logo_filename)  # حفظ الشعار في المجلد المخصص
        restaurant_info['logo'] = f'static/uploads/{logo.filename}'  # تحديث مسار الشعار في بيانات المطعم
    
    save_restaurant_info(restaurant_info)  # حفظ المعلومات المحدثة في ملف JSON
    return jsonify({"success": True, "message": "تم تحديث معلومات المطعم بنجاح!"})  # إرجاع رسالة نجاح بصيغة JSON

@app.route('/add_item', methods=['POST'])
def add_item():
    """وظيفة الكود: إضافة صنف جديد إلى القائمة بناءً على البيانات المرسلة من النموذج."""
    category_ar = request.form.get('category')  # الفئة المختارة من القائمة الحالية
    new_category_ar = request.form.get('new_category_ar')  # الفئة الجديدة (عربي)
    new_category_en = request.form.get('new_category_en')  # الفئة الجديدة (إنجليزي)
    name_ar = request.form.get('name_ar')  # اسم الصنف بالعربية
    name_en = request.form.get('name_en')  # اسم الصنف بالإنجليزية
    price = request.form.get('price')  # سعر الصنف
    calories = request.form.get('calories', '')  # السعرات الحرارية (اختياري)
    description_ar = request.form.get('description_ar', '')  # وصف الصنف بالعربية (اختياري)
    description_en = request.form.get('description_en', '')  # وصف الصنف بالإنجليزية (اختياري)
    image = request.files.get('image')  # صورة الصنف

    # تحديد الفئة النهائية
    if new_category_ar and new_category_en:  # إذا تم إدخال فئة جديدة
        category_ar = new_category_ar  # استخدام الفئة الجديدة بالعربية
        category_en = new_category_en  # استخدام الفئة الجديدة بالإنجليزية
    elif category_ar:  # إذا تم اختيار فئة موجودة
        menu = load_menu()  # تحميل القائمة الحالية
        category_en = menu[category_ar]['name_en']  # الحصول على اسم الفئة بالإنجليزية من القائمة
    else:  # إذا لم يتم تحديد فئة
        return jsonify({"error": "Category is required"}), 400  # إرجاع خطأ يفيد بضرورة تحديد الفئة

    # التحقق من الحقول الإجبارية
    if not all([name_ar, name_en, price, image]):  # التحقق من وجود جميع الحقول الإجبارية
        return jsonify({"error": "Missing required fields"}), 400  # إرجاع خطأ إذا كانت هناك حقول مفقودة

    # حفظ الصورة
    image_filename = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)  # تحديد مسار حفظ الصورة
    image.save(image_filename)  # حفظ الصورة في المجلد المخصص

    # تحديث القائمة
    menu = load_menu()  # تحميل القائمة الحالية
    if category_ar not in menu:  # إذا كانت الفئة غير موجودة في القائمة
        menu[category_ar] = {'name_en': category_en, 'items': []}  # إنشاء الفئة الجديدة وإضافة قسم للعناصر
    menu[category_ar]['items'].append({  # إضافة الصنف الجديد إلى الفئة
        'name': name_ar,
        'name_en': name_en,
        'price': price,
        'calories': calories or '',  # استخدام القيمة إذا كانت موجودة، أو تركها فارغة
        'description_ar': description_ar or '',  # استخدام القيمة إذا كانت موجودة، أو تركها فارغة
        'description_en': description_en or '',  # استخدام القيمة إذا كانت موجودة، أو تركها فارغة
        'image': image_filename  # مسار الصورة المحفوظة
    })
    save_menu(menu)  # حفظ القائمة المحدثة في ملف JSON
    return jsonify({"message": "تمت إضافة الصنف بنجاح!"}), 201  # إرجاع رسالة نجاح بصيغة JSON
#====================================================================

@app.route('/delete_item', methods=['POST'])
def delete_item():
    """وظيفة الكود: حذف صنف معين من قائمة الطعام بناءً على الفئة والاسم."""
    data = request.get_json()  # استقبال البيانات من الطلب بصيغة JSON
    category_ar = data.get('category')  # الحصول على اسم الفئة بالعربية
    item_name = data.get('item_name')  # الحصول على اسم الصنف المراد حذفه

    # التأكد من وجود الفئة والصنف في القائمة
    menu = load_menu()  # تحميل القائمة الحالية
    if category_ar in menu:  # التحقق من وجود الفئة في القائمة
        items = menu[category_ar]['items']  # الحصول على عناصر الفئة
        # البحث عن الصنف في القائمة وحذفه
        for item in items:
            if item['name'] == item_name:  # التحقق من أن اسم الصنف يطابق
                items.remove(item)  # حذف الصنف من القائمة
                save_menu(menu)  # حفظ القائمة المحدثة
                return jsonify({"message": "تم حذف الصنف بنجاح!"}), 200  # إرجاع رسالة نجاح
    return jsonify({"error": "الصنف غير موجود"}), 404  # إرجاع خطأ إذا لم يتم العثور على الصنف


@app.route('/get_category_color', methods=['GET'])
def get_category_color():
    """وظيفة الكود: الحصول على لون الفئة الحالي أو إرجاع اللون الافتراضي إذا لم يكن موجودًا."""
    try:
        with open('category_color.txt', 'r') as f:  # فتح ملف لون الفئة للقراءة
            color = f.read().strip()  # قراءة اللون من الملف وإزالة المسافات الزائدة
        return jsonify({'color': color})  # إرجاع اللون الحالي
    except FileNotFoundError:
        return jsonify({'color': '#ff0000'})  # إرجاع اللون الافتراضي (أحمر) إذا لم يكن الملف موجودًا


@app.route('/delete_category', methods=['POST'])
def delete_category():
    """وظيفة الكود: حذف فئة كاملة من قائمة الطعام بناءً على اسم الفئة."""
    data = request.get_json()  # استقبال البيانات من الطلب بصيغة JSON
    category_ar = data.get('category')  # الحصول على اسم الفئة المراد حذفها

    menu = load_menu()  # تحميل القائمة الحالية
    if category_ar in menu:  # التحقق من وجود الفئة في القائمة
        del menu[category_ar]  # حذف الفئة بالكامل
        save_menu(menu)  # حفظ القائمة المحدثة
        return jsonify({"message": "تم حذف الفئة بنجاح!"}), 200  # إرجاع رسالة نجاح
    return jsonify({"error": "الفئة غير موجودة"}), 404  # إرجاع خطأ إذا لم يتم العثور على الفئة


@app.route('/upload_background', methods=['POST'])
def upload_background():
    """وظيفة الكود: رفع خلفية جديدة وتحديث إعدادات الفئات مثل اللون وخصائص الخط."""
    background_file = request.files.get('background')  # الحصول على ملف الخلفية الجديد
    category_color = request.form.get('category_color', None)  # الحصول على لون الفئة الجديد
    category_font_color = request.form.get('category_font_color', None)  # الحصول على لون خط الفئة الجديد
    category_font_size = request.form.get('category_font_size', None)  # الحصول على حجم خط الفئة الجديد
    category_font_family = request.form.get('category_font_family', None)  # الحصول على نوع خط الفئة الجديد
    
    # حفظ الخلفية (إذا تم رفعها)
    if background_file:
        background_filename = os.path.join(app.config['UPLOAD_FOLDER'], background_file.filename)  # تحديد مسار حفظ الخلفية
        background_file.save(background_filename)  # حفظ ملف الخلفية
        save_background(background_filename)  # تحديث مسار الخلفية في النظام
    
    # حفظ لون الفئة (إذا تم إرساله)
    if category_color:
        save_category_color(category_color)  # حفظ لون الفئة في ملف
    
    # حفظ خصائص خط الفئة (إذا تم إرسالها)
    if category_font_color:
        save_category_font_color(category_font_color)  # حفظ لون خط الفئة في ملف
    
    # حفظ حجم ونوع الخط في ملف جديد
    if category_font_size or category_font_family:
        font_settings = {}
        try:
            with open('category_font_settings.json', 'r') as f:  # تحميل إعدادات الخط الحالية
                font_settings = json.load(f)
        except FileNotFoundError:
            pass
        
        if category_font_size:
            font_settings['font_size'] = f"{category_font_size}px"  # تحديث حجم الخط
        if category_font_family:
            font_settings['font_family'] = category_font_family  # تحديث نوع الخط
        
        with open('category_font_settings.json', 'w') as f:  # حفظ الإعدادات المحدثة
            json.dump(font_settings, f)
    
    return jsonify({'success': True, 'message': 'تم التحديث بنجاح!', 'timestamp': datetime.now().timestamp()})  # إرجاع رسالة نجاح


@app.route('/get_category_font_settings', methods=['GET'])
def get_category_font_settings():
    """وظيفة الكود: الحصول على إعدادات خط الفئة الحالية أو إرجاع القيم الافتراضية إذا لم تكن موجودة."""
    try:
        with open('category_font_settings.json', 'r') as f:  # تحميل إعدادات خط الفئة
            settings = json.load(f)
            return jsonify({
                'font_size': settings.get('font_size', '20px'),  # الحصول على حجم الخط أو إرجاع القيمة الافتراضية
                'font_family': settings.get('font_family', 'Noto Naskh Arabic')  # الحصول على نوع الخط أو إرجاع القيمة الافتراضية
            })
    except FileNotFoundError:
        return jsonify({
            'font_size': '20px',  # القيمة الافتراضية لحجم الخط
            'font_family': 'Noto Naskh Arabic'  # القيمة الافتراضية لنوع الخط
        })

#================================================================================================
def save_category_color(color):
    # حفظ اللون في قاعدة البيانات أو ملف
    with open('category_color.txt', 'w') as f:
        f.write(color)


# حفظ لون خط الفئة (جديدة)
def save_category_font_color(color):
    with open('category_font_color.txt', 'w') as f:
        f.write(color)

@app.route('/get_category_font_color', methods=['GET'])
def get_category_font_color():
    try:
        with open('category_font_color.txt', 'r') as f:
            color = f.read().strip()
        return jsonify({'color': color})
    except FileNotFoundError:
        return jsonify({'color': '#000000'})  # اللون الافتراضي أسود


@app.route('/update_restaurant_name_style', methods=['POST'])
def update_restaurant_name_style():
    """تحديث خصائص اسم المطعم (حجم الخط، لون الخط، نوع الخط)"""
    global restaurant_info

    # استقبال البيانات من النموذج
    font_size = request.form.get('font_size')
    font_color = request.form.get('font_color')
    font_family = request.form.get('font_family')

    # التحقق من وجود البيانات
    if not all([font_size, font_color, font_family]):
        return jsonify({"success": False, "error": "جميع الحقول مطلوبة"}), 400

    # تحديث خصائص اسم المطعم
    restaurant_info['font_size'] = font_size
    restaurant_info['font_color'] = font_color
    restaurant_info['font_family'] = font_family

    # حفظ التغييرات في ملف restaurant_info.json
    save_restaurant_info(restaurant_info)

    return jsonify({"success": True, "message": "تم تحديث خصائص اسم المطعم بنجاح!"})


#===================================================================================================


# تعريف المتغيرات العالمية
ADMIN_USERNAME = "admin"  # اسم المستخدم الخاص بالمشرف
ADMIN_PASSWORD = "admin_password"  # كلمة المرور الرئيسية (يمكن تغييرها فقط من الكود)

RESTAURANT_USERNAME = "restaurant"  # اسم المستخدم الخاص بالمطعم
RESTAURANT_PASSWORD = "admin"  # كلمة المرور الخاصة بالمطعم


# مسار ملفات بيانات الاعتماد
ADMIN_CREDENTIALS_FILE = "admin_credentials.txt"
RESTAURANT_CREDENTIALS_FILE = "restaurant_credentials.txt"

# دالة لقراءة بيانات الاعتماد من ملف
def read_credentials(file_path):
    if not os.path.exists(file_path):
        return None, None
    with open(file_path, 'r') as f:
        lines = f.readlines()
        username = lines[0].strip()
        password = lines[1].strip()
    return username, password

# دالة لكتابة بيانات الاعتماد إلى ملف
def write_credentials(file_path, username, password):
    with open(file_path, 'w') as f:
        f.write(f"{username}\n{password}\n")
# تسجيل الدخول
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # التحقق من بيانات المشرف
        admin_username, admin_password = read_credentials(ADMIN_CREDENTIALS_FILE)
        if username == admin_username and password == admin_password:
            session['logged_in'] = True
            session['is_admin'] = True
            return redirect(url_for('admin_home'))  # توجيه المشرف إلى صفحة الوسيط الخاصة به
        # التحقق من بيانات المطعم
        restaurant_username, restaurant_password = read_credentials(RESTAURANT_CREDENTIALS_FILE)
        if username == restaurant_username and password == restaurant_password:
            session['logged_in'] = True
            session['is_admin'] = False
            return redirect(url_for('admin_panel'))  # توجيه المطعم مباشرة إلى لوحة التحكم
        else:
            return render_template('login.html', error="خطأ في اسم المستخدم أو كلمة المرور")
    return render_template('login.html')

# قراءة بيانات الاعتماد عند بدء التشغيل
ADMIN_USERNAME, ADMIN_PASSWORD = read_credentials(ADMIN_CREDENTIALS_FILE)
if ADMIN_USERNAME is None or ADMIN_PASSWORD is None:
    ADMIN_USERNAME, ADMIN_PASSWORD = "admin", "admin_password"
    write_credentials(ADMIN_CREDENTIALS_FILE, ADMIN_USERNAME, ADMIN_PASSWORD)

RESTAURANT_USERNAME, RESTAURANT_PASSWORD = read_credentials(RESTAURANT_CREDENTIALS_FILE)
if RESTAURANT_USERNAME is None or RESTAURANT_PASSWORD is None:
    RESTAURANT_USERNAME, RESTAURANT_PASSWORD = "restaurant", "admin"
    write_credentials(RESTAURANT_CREDENTIALS_FILE, RESTAURANT_USERNAME, RESTAURANT_PASSWORD)



# تسجيل الخروج
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/change_password_page')
def change_password_page():
    # التحقق من أن المستخدم مسجل الدخول
    if not session.get('logged_in'):
        # إذا لم يكن المستخدم مسجل الدخول، يتم إعادة توجيهه إلى صفحة تسجيل الدخول
        return redirect(url_for('login'))
    
    # إذا كان المستخدم مسجل الدخول، يتم عرض صفحة تغيير كلمة المرور
    return render_template('change_password.html')

# تحديث كلمة المرور
@app.route('/change_password', methods=['POST'])
def change_password():
    if not session.get('logged_in'):
        return jsonify({"success": False, "error": "غير مصرح لك"}), 403
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    # إذا كان المستخدم هو المشرف
    if session.get('is_admin'):
        admin_username, admin_password = read_credentials(ADMIN_CREDENTIALS_FILE)
        if current_password == admin_password:
            write_credentials(ADMIN_CREDENTIALS_FILE, admin_username, new_password)
            flash("تم تحديث كلمة المرور الرئيسية بنجاح!", "success")
            return redirect(url_for('change_password_page'))
        else:
            flash("كلمة المرور الحالية غير صحيحة", "error")
            return redirect(url_for('change_password_page'))
    # إذا كان المستخدم صاحب المطعم
    else:
        restaurant_username, restaurant_password = read_credentials(RESTAURANT_CREDENTIALS_FILE)
        if current_password == restaurant_password:
            write_credentials(RESTAURANT_CREDENTIALS_FILE, restaurant_username, new_password)
            flash("تم تحديث كلمة المرور بنجاح!", "success")
            return redirect(url_for('login'))
        else:
            flash("كلمة المرور الحالية غير صحيحة", "error")
            return redirect(url_for('login'))

# صفحة تغيير كلمة المرور
@app.route('/update_credentials', methods=['POST'])
def update_credentials():
    if not session.get('logged_in') or not session.get('is_admin'):
        return jsonify({"success": False, "error": "غير مصرح لك"}), 403

    new_username = request.form.get('new_username')
    new_password = request.form.get('new_password')

    # قراءة بيانات المطعم الحالية
    restaurant_username, restaurant_password = read_credentials(RESTAURANT_CREDENTIALS_FILE)

    # تحديث البيانات إذا كانت هناك قيم جديدة
    if new_username:
        restaurant_username = new_username
    if new_password:
        restaurant_password = new_password

    # كتابة البيانات المحدثة إلى ملف
    write_credentials(RESTAURANT_CREDENTIALS_FILE, restaurant_username, restaurant_password)
    return jsonify({"success": True, "message": "تم تحديث بيانات المطعم بنجاح!"})
# صفحة المشرف الرئيسية
@app.route('/admin_home')
def admin_home():
    if not session.get('logged_in') or not session.get('is_admin'):
        return redirect(url_for('login'))  # إعادة التوجيه إذا لم يكن المستخدم مشرفًا
    return render_template('admin_home.html')

# صفحة تحديث بيانات المطعم
@app.route('/update_restaurant_credentials_page')
def update_restaurant_credentials_page():
    if not session.get('logged_in') or not session.get('is_admin'):
        return redirect(url_for('login'))  # إعادة التوجيه إذا لم يكن المستخدم مشرفًا
    return render_template('update_restaurant_credentials.html')

# تحديث بيانات الأمان
# تحديث بيانات المطعم
@app.route('/update_restaurant_credentials', methods=['POST'])
def update_restaurant_credentials():
    if not session.get('logged_in') or not session.get('is_admin'):
        return jsonify({"success": False, "error": "غير مصرح لك"}), 403

    current_username = request.form.get('current_username')
    current_password = request.form.get('current_password')
    new_username = request.form.get('new_username')
    new_password = request.form.get('new_password')

    # قراءة بيانات المطعم الحالية
    restaurant_username, restaurant_password = read_credentials(RESTAURANT_CREDENTIALS_FILE)

    # التحقق من صحة البيانات الحالية
    if current_username == restaurant_username and current_password == restaurant_password:
        # تحديث البيانات إذا كانت هناك قيم جديدة
        if new_username:
            restaurant_username = new_username
        if new_password:
            restaurant_password = new_password

        # كتابة البيانات المحدثة إلى ملف
        write_credentials(RESTAURANT_CREDENTIALS_FILE, restaurant_username, restaurant_password)
        return jsonify({"success": True, "message": "تم تحديث بيانات المطعم بنجاح!"})
    else:
        return jsonify({"success": False, "error": "بيانات المطعم الحالية غير صحيحة"}), 400

# لوحة التحكم
@app.route('/admin')
def admin_panel():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # تحميل القائمة
    menu = load_menu()

    # جلب لون الفئة ولون خط الفئة من الملفات
    try:
        with open('category_color.txt', 'r') as f:
            category_color = f.read().strip()
    except FileNotFoundError:
        category_color = '#ff0000'  # اللون الافتراضي أحمر

    try:
        with open('category_font_color.txt', 'r') as f:
            category_font_color = f.read().strip()
    except FileNotFoundError:
        category_font_color = '#000000'  # اللون الافتراضي أسود

    # إنشاء كائن settings يحتوي على جميع الإعدادات
    settings = {
        "category_color": category_color,
        "category_font_color": category_font_color
    }

    return render_template(
        'dashboard.html',
        menu=menu,
        restaurant_info=restaurant_info,
        settings=settings  # تمرير كائن settings إلى القالب
    )

# الحصول على خلفية الصفحة
@app.route('/get_background', methods=['GET'])
def get_background():
    background_path = load_background()
    return jsonify({
        'background': background_path,
        'timestamp': datetime.now().timestamp()
    })




if __name__ == '__main__':
    #app.run(host="0.0.0.0", port=10000, debug=False)
  #  app.run(host="192.168.100.90",port=5000,debug=False)
    app.run(debug=True)