import streamlit as st
import os
import pandas as pd
from datetime import datetime

# تهيئة إعدادات الصفحة
st.set_page_config(page_title="منصة إيداع مذكرات التخرج", layout="centered")

# === إعداد CSS احترافي شامل ===
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');

body, .main, .block-container {
    direction: rtl !important;
    text-align: right !important;
    font-size: 20px !important;
    font-weight: bold !important;
    color: #003366 !important;
    font-family: 'Cairo', sans-serif !important;
    background-color: #f0f4f8 !important;
}

/* تصميم الإطار العام */
.main {
    background-color: #ffffff;
    padding: 3rem 2rem;
    border-radius: 15px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
    max-width: 950px;
    margin: 2rem auto;
}

/* العناوين h1-h6 */
h1, h2, h3, h4, h5, h6 {
    color: #003366 !important;
    font-weight: 900 !important;
    margin-top: 1rem;
    margin-bottom: 1rem;
}

h1 {
    font-size: 38px !important;
    text-align: center;
}

h2 {
    font-size: 30px !important;
}

h3 {
    font-size: 26px !important;
}

h4 {
    font-size: 22px !important;
    text-align: center;
}

/* الحقول */
.stTextInput input, .stSelectbox select, .stTextArea textarea {
    font-size: 1.2rem !important;
    font-weight: bold !important;
    color: #003366 !important;
    border-radius: 8px !important;
    padding: 0.5rem 0.75rem !important;
    background-color: #fdfdfd !important;
    border: 1px solid #ccc !important;
}

/* الأزرار */
.stButton button {
    width: 100%;
    background-color: #4CAF50;
    color: white;
    padding: 0.85rem;
    font-size: 1.1rem;
    font-weight: bold;
    border-radius: 8px;
    border: none;
    margin-top: 1rem;
    transition: background-color 0.3s;
}

.stButton button:hover {
    background-color: #388e3c;
}

/* تسجيل الخروج */
.logout-btn {
    margin-top: 2rem;
    text-align: center;
}

/* بطاقات الإحصائيات */
.metric-box {
    background: #e3f2fd;
    border-radius: 10px;
    padding: 1.2rem;
    margin-bottom: 1rem;
    text-align: center;
    font-size: 1.2rem;
    font-weight: bold;
    color: #003366;
}

/* الرسائل */
.success-msg {
    color: #2e7d32;
    background-color: #e8f5e9;
    padding: 1rem;
    border-radius: 6px;
    margin-bottom: 1rem;
    font-weight: bold;
}

.error-msg {
    color: #c62828;
    background-color: #ffebee;
    padding: 1rem;
    border-radius: 6px;
    margin-bottom: 1rem;
    font-weight: bold;
}

/* رؤوس expander */
.stExpanderHeader {
    font-size: 1.2rem !important;
    font-weight: bold !important;
    color: #003366 !important;
}
</style>

""", unsafe_allow_html=True)

# قاعدة بيانات كلمات المرور
PASSWORDS = {
    "طالب": {
        "student1": "pass123",
        "student2": "pass456",
        "student3": "pass789"
    },
    "مشرف": {
        "Biologie": "sup123",
        "Agronomie": "sup456",
        "Alimentaire": "sup789",
        "Ecologie": "sup7896"
    }
}

# إعداد مجلد التحميل
UPLOAD_DIR = "uploaded_memos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# الأقسام المتاحة
sections = ["العلوم البيولوجية", "العلوم الفلاحية", "علوم التغذية", "علم البيئة والمحيط"]
data_file = "data.csv"

# تهيئة ملف البيانات إذا لم يكن موجوداً
if not os.path.exists(data_file):
    df_init = pd.DataFrame(columns=[
        "رقم التسجيل", "الاسم", "اللقب", "تاريخ الميلاد", 
        "القسم", "المشرف", "عنوان المذكرة", "اسم الملف", "تاريخ الإيداع"
    ])
    df_init.to_csv(data_file, index=False, encoding="utf-8")

# وظائف مساعدة
def reset_session():
    st.session_state.clear()
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None

def save_memo(data):
    df = pd.read_csv(data_file)
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(data_file, index=False, encoding="utf-8")

# تهيئة حالة الجلسة
if 'logged_in' not in st.session_state:
    reset_session()

# واجهة المستخدم الرئيسية
with st.container():
    st.markdown('<div class="main">', unsafe_allow_html=True)
    st.markdown("<h1>📚 منصة إيداع مذكرات التخرج</h1>", unsafe_allow_html=True)
    st.markdown("<h4>جامعة محمد البشير الإبراهيمي - برج بوعريريج<br>كلية علوم الطبيعة والحياة وعلوم الأرض والكون</h4>", unsafe_allow_html=True)

    if not st.session_state.logged_in:
        # واجهة تسجيل الدخول
        role = st.selectbox("👤 اختر نوع الدخول:", ["طالب", "مشرف"], key="login_role")
        
        with st.form("login_form"):
            
            username = st.text_input("👤 اسم المستخدم", key="login_username")
            password = st.text_input("🔐 كلمة المرور:", type="password", key="login_password")
            submitted = st.form_submit_button("تسجيل الدخول")
        
        if submitted:
            if (role == "طالب" and username in PASSWORDS["طالب"] and password == PASSWORDS["طالب"][username]) or \
               (role == "مشرف" and username in PASSWORDS["مشرف"] and password == PASSWORDS["مشرف"][username]):
                st.session_state.logged_in = True
                st.session_state.role = role
                st.session_state.username = username
                st.rerun()
            else:
                st.error("⚠️ اسم المستخدم أو كلمة السر غير صحيحة")
    
    else:
        # واجهة بعد تسجيل الدخول
        if st.session_state.role == "طالب":
            st.success(f"مرحباً بك {st.session_state.username} (طالب)")
            
            with st.form("memo_form", clear_on_submit=True):
                st.subheader("📝 نموذج إيداع المذكرة")
                
                col1, col2 = st.columns(2)
                with col1:
                    first_name = st.text_input("الاسم", key="first_name")
                with col2:
                    last_name = st.text_input("اللقب", key="last_name")
                
                reg_num = st.text_input("رقم التسجيل", key="reg_num")
                birth_date = st.date_input("تاريخ الميلاد", key="birth_date")
                section = st.selectbox("القسم", sections, key="section")
                supervisor = st.text_input("اسم المشرف", key="supervisor")
                title = st.text_input("عنوان المذكرة", key="title")
                file = st.file_uploader("رفع ملف المذكرة (PDF فقط)", type=["pdf"], key="file")
                
                submitted = st.form_submit_button("إيداع المذكرة")
                
                if submitted:
                    if all([reg_num, first_name, last_name, section, supervisor, title, file]):
                        # حفظ الملف
                        section_dir = os.path.join(UPLOAD_DIR, section)
                        os.makedirs(section_dir, exist_ok=True)
                        filename = f"{reg_num}_{file.name}"
                        file_path = os.path.join(section_dir, filename)
                        
                        with open(file_path, "wb") as f:
                            f.write(file.getbuffer())
                        
                        # حفظ البيانات
                        memo_data = {
                            "رقم التسجيل": reg_num,
                            "الاسم": first_name,
                            "اللقب": last_name,
                            "تاريخ الميلاد": birth_date.strftime("%Y-%m-%d"),
                            "القسم": section,
                            "المشرف": supervisor,
                            "عنوان المذكرة": title,
                            "اسم الملف": filename,
                            "تاريخ الإيداع": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        save_memo(memo_data)
                        st.success("✅ تم إيداع المذكرة بنجاح")
                    else:
                        st.error("⚠️ يرجى تعبئة جميع الحقول ورفع الملف")

        elif st.session_state.role == "مشرف":
            st.success(f"مرحباً بك {st.session_state.username} (مشرف)")
            
            # عرض الإحصائيات
            st.subheader("📊 لوحة التحكم")
            
            df = pd.read_csv(data_file)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f'<div class="metric-box">المذكرات المودعة<br><b>{len(df)}</b></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="metric-box">عدد الأقسام<br><b>{df["القسم"].nunique()}</b></div>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div class="metric-box">عدد المشرفين<br><b>{df["المشرف"].nunique()}</b></div>', unsafe_allow_html=True)
            
            # أدوات التصفية
            st.subheader("🔍 تصفية المذكرات")
            
            col1, col2 = st.columns(2)
            with col1:
                selected_section = st.selectbox("القسم", ["الكل"] + sections)
            with col2:
                supervisors = ["الكل"] + sorted(df["المشرف"].unique().tolist())
                selected_supervisor = st.selectbox("المشرف", supervisors)
            
            # تطبيق التصفية
            filtered_df = df.copy()
            if selected_section != "الكل":
                filtered_df = filtered_df[filtered_df["القسم"] == selected_section]
            if selected_supervisor != "الكل":
                filtered_df = filtered_df[filtered_df["المشرف"] == selected_supervisor]
            
            # عرض النتائج
            st.subheader(f"📄 المذكرات ({len(filtered_df)})")
            
            if filtered_df.empty:
                st.info("لا توجد مذكرات متاحة حسب معايير التصفية المحددة")
            else:
                for _, row in filtered_df.iterrows():
                    with st.expander(f"{row['عنوان المذكرة']} - {row['الاسم']} {row['اللقب']}"):
                        st.markdown(f"**رقم التسجيل:** {row['رقم التسجيل']}")
                        st.markdown(f"**القسم:** {row['القسم']}")
                        st.markdown(f"**المشرف:** {row['المشرف']}")
                        st.markdown(f"**تاريخ الإيداع:** {row['تاريخ الإيداع']}")
                        
                        file_path = os.path.join(UPLOAD_DIR, row['القسم'], row['اسم الملف'])
                        if os.path.exists(file_path):
                            st.download_button(
                                label="تحميل المذكرة",
                                data=open(file_path, "rb").read(),
                                file_name=row['اسم الملف'],
                                mime="application/pdf"
                            )
                        else:
                            st.error("الملف غير موجود في النظام")

        # زر تسجيل الخروج
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button("تسجيل الخروج"):
            reset_session()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)