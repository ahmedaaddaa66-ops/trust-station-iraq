import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="منصة محطة الثقة", page_icon="🛡️", layout="centered")

st.title("🛡️ منصة محطة الثقة (Trust Station)")
st.write("نظام حماية المتاجر من العملاء غير الملتزمين")

# القائمة الجانبية للتنقل بين الصفحات
menu = st.sidebar.selectbox("القائمة الرئيسية", ["فحص رقم عميل", "تسجيل بلاغ جديد", "تسجيل متجر جديد", "تسجيل الدخول"])

# 1. صفحة فحص العميل
if menu == "فحص رقم عميل":
    st.header("🔍 فحص حالة رقم العميل")
    phone = st.text_input("أدخل رقم هاتف العميل:")
    
    if st.button("فحص الرقم"):
        if phone:
            response = requests.get(f"{API_URL}/check_customer/{phone}")
            if response.status_code == 200:
                data = response.json()
                if data["status"] == "safe":
                    st.success(data["message"])
                else:
                    st.warning(data["message"])
                    st.write("أسباب البلاغات السابقة:")
                    for reason in data.get("reasons", []):
                        st.write(f"- {reason}")
            else:
                st.error("حدث خطأ أثناء الاتصال بالخادم.")
        else:
            st.warning("الرجاء إدخال رقم الهاتف أولاً.")

# 2. صفحة تسجيل بلاغ جديد
elif menu == "تسجيل بلاغ جديد":
    st.header("📝 تسجيل بلاغ بحق عميل غير ملتزم")
    with st.form("report_form"):
        customer_phone = st.text_input("رقم هاتف العميل:")
        reason = st.text_area("سبب البلاغ (مثال: رفض استلام الطلب):")
        email = st.text_input("البريد الإلكتروني لمتجرك:")
        password = st.text_input("كلمة المرور:", type="password")
        
        submit = st.form_submit_button("إرسال البلاغ")
        
        if submit:
            payload = {
                "customer_phone": customer_phone,
                "reason": reason,
                "email": email,
                "password": password
            }
            response = requests.post(f"{API_URL}/add_report", json=payload)
            if response.status_code == 200:
                st.success(response.json()["message"])
            else:
                st.error(response.json().get("detail", "فشل إرسال البلاغ. تأكد من صحة بيانات متجرك."))

# 3. صفحة تسجيل متجر جديد
elif menu == "تسجيل متجر جديد":
    st.header("🏪 انضم إلينا كمتجر جديد")
    with st.form("signup_form"):
        shop_name = st.text_input("اسم المتجر:")
        email = st.text_input("البريد الإلكتروني:")
        phone_number = st.text_input("رقم هاتف المتجر:")
        password = st.text_input("كلمة المرور:", type="password")
        
        submit = st.form_submit_button("إنشاء الحساب")
        
        if submit:
            payload = {
                "shop_name": shop_name,
                "email": email,
                "phone_number": phone_number,
                "password": password
            }
            response = requests.post(f"{API_URL}/signup", json=payload)
            if response.status_code == 200:
                st.success(response.json()["message"])
            else:
                st.error(response.json().get("detail", "حدث خطأ أثناء التسجيل."))

# 4. صفحة تسجيل الدخول
elif menu == "تسجيل الدخول":
    st.header("🔐 دخول المتاجر")
    with st.form("login_form"):
        email = st.text_input("البريد الإلكتروني:")
        password = st.text_input("كلمة المرور:", type="password")
        
        submit = st.form_submit_button("دخول")
        
        if submit:
            payload = {
                "email": email,
                "password": password
            }
            response = requests.post(f"{API_URL}/login", json=payload)
            if response.status_code == 200:
                st.success(response.json()["message"])
            else:
                st.error(response.json().get("detail", "البريد أو كلمة المرور غير صحيحة."))