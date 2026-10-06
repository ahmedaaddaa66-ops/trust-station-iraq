from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import hashlib

app = FastAPI()

# نماذج البيانات (Pydantic Models)
class MerchantCreate(BaseModel):
    shop_name: str
    email: str
    phone_number: str
    password: str

class MerchantLogin(BaseModel):
    email: str
    password: str

class ReportCreate(BaseModel):
    customer_phone: str
    reason: str
    email: str
    password: str

# دالة تشفير كلمة المرور
def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

# دالة إنشاء الجداول
def init_db():
    conn = sqlite3.connect('truststation.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS merchants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shop_name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone_number TEXT UNIQUE,
            password_hash TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_phone TEXT NOT NULL,
            reason TEXT NOT NULL,
            merchant_id INTEGER
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# 1. مسار البحث عن العميل
@app.get("/check_customer/{phone_number}")
def check_customer(phone_number: str):
    conn = sqlite3.connect('truststation.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT reason FROM reports WHERE customer_phone = ?", (phone_number,))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return {"status": "safe", "message": "الرقم آمن، لا توجد عليه بلاغات سابقة."}
    
    report_count = len(rows)
    reasons = list(set([row[0] for row in rows]))
    
    return {
        "status": "warning",
        "message": f"تحذير! أبلغت عنه {report_count} متاجر أخرى.",
        "reasons": reasons
    }

# 2. مسار تسجيل متجر جديد
@app.post("/signup")
def signup(merchant: MerchantCreate):
    conn = sqlite3.connect('truststation.db')
    cursor = conn.cursor()
    
    hashed_pw = hash_password(merchant.password)
    
    try:
        cursor.execute(
            "INSERT INTO merchants (shop_name, email, phone_number, password_hash) VALUES (?, ?, ?, ?)",
            (merchant.shop_name, merchant.email, merchant.phone_number, hashed_pw)
        )
        conn.commit()
        merchant_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="البريد الإلكتروني أو رقم الهاتف مستخدم مسبقاً.")
    
    conn.close()
    return {"status": "success", "message": "تم إنشاء حساب المتجر بنجاح!", "merchant_id": merchant_id}

# 3. مسار تسجيل الدخول للمتجر
@app.post("/login")
def login(creds: MerchantLogin):
    conn = sqlite3.connect('truststation.db')
    cursor = conn.cursor()
    
    hashed_pw = hash_password(creds.password)
    
    cursor.execute(
        "SELECT id, shop_name FROM merchants WHERE email = ? AND password_hash = ?",
        (creds.email, hashed_pw)
    )
    merchant = cursor.fetchone()
    conn.close()
    
    if not merchant:
        raise HTTPException(status_code=401, detail="البريد الإلكتروني أو كلمة المرور غير صحيحة.")
    
    return {
        "status": "success", 
        "message": f"مرحباً بك عودةً، {merchant[1]}!", 
        "merchant_id": merchant[0]
    }

# 4. مسار إضافة بلاغ جديد (الآمن والمرتبط بالمصادقة)
@app.post("/add_report")
def add_report(report: ReportCreate):
    conn = sqlite3.connect('truststation.db')
    cursor = conn.cursor()
    
    # التحقق من بيانات المتجر أولاً
    hashed_pw = hash_password(report.password)
    cursor.execute(
        "SELECT id FROM merchants WHERE email = ? AND password_hash = ?",
        (report.email, hashed_pw)
    )
    merchant = cursor.fetchone()
    
    if not merchant:
        conn.close()
        raise HTTPException(status_code=401, detail="فشل المصادقة: البريد أو كلمة المرور للمتجر غير صحيحة.")
    
    merchant_id = merchant[0]
    
    # تسجيل البلاغ برقم الـ ID الحقيقي للمتجر
    cursor.execute(
        "INSERT INTO reports (customer_phone, reason, merchant_id) VALUES (?, ?, ?)",
        (report.customer_phone, report.reason, merchant_id)
    )
    conn.commit()
    conn.close()
    
    return {"status": "success", "message": "تم تسجيل البلاغ بنجاح برعاية متجرك الموثوق."}