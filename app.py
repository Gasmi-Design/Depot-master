import streamlit as st
import os
import pandas as pd
from datetime import datetime
import hashlib
import sqlite3
from PIL import Image

# === إعدادات الصفحة ===
st.set_page_config(page_title="منصة إيداع مذكرات التخرج", layout="centered", page_icon="📚")

# === إعداد CSS لتحسين الواجهة ===
st.markdown("""
<style>
    .main {
        background-color: #f5f7fa;
        padding: 3rem 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        max-width: 800px;
        margin: 2rem auto;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #333;
    }
    h1 {
        text-align: center;
        color: #2c3e50;
        margin-bottom: 0.3rem;
        font-weight: 700;
    }
    h4 {
        text-align: center;
        color: #34495e;
        margin-top: 0;
        margin-bottom: 2rem;
        font-weight: 500;
        line-height: 1.3;
    }
    label, .stTextInput > div > input, .stSelectbox > div > div {
        font-size: 1.1rem !important;
    }
    button {
        width: 100%;
        background-color: #2980b9;
        color: white;
        padding: 0.65rem;
        font-size: 1.1rem;
        border-radius: 6px;
        border: none;
        margin-top: 1rem;
        transition: all 0.3s;
    }
    button:hover {
        background-color: #3498db;
        cursor: pointer;
        transform: translateY(-2px);
    }
    .logout-btn {
        margin-top: 2rem;
        text-align: center;
    }
    .metric-container {
        display: flex;
        justify-content: space-around;
        margin-bottom: 1rem;
        flex-wrap: wrap;
    }
    .metric {
        background: #eaf2f8;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem;
        flex-grow: 1;
        text-align: center;
        font-weight: 600;
        color: #2c3e50;
        min-width: 120px;
    }
    .success-box {
        background-color: #d4edda;
        color: #155724;
        padding: 15px;
        border-radius: 5px;
        margin: 15px 0;
    }
    .error-box {
        background-color: #f8d7da;
        color: #721c24;
        padding: 15px;
        border-radius: 5px;
        margin: 15px 0;
    }
    .info-box {
        background-color: #d1ecf1;
        color: #0c5460;
        padding: 15px;
        border-radius: 5px;
        margin: 15px 0;
    }
</style>
""", unsafe_allow_html=True)

# === وظائف مساعدة ===
def hash_password(password):
    """تشفير كلمة المرور باستخدام SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

# كلمات السر المشفرة
PASSWORDS = {
    "طالب": hash_password("student123"),
    "مشرف": hash_password("supervisor123"),
    "مسؤول": hash_password("admin123")  # دور جديد للإدارة
}

# === إعداد قاعدة البيانات ===
def init_db():
    """تهيئة قاعدة البيانات SQLite"""
    conn = sqlite3.connect('theses.db')
    c = conn.cursor()
    
    # جدول المذكرات
    c.execute('''CREATE TABLE IF NOT EXISTS theses
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  reg_num TEXT NOT NULL,
                  first_name TEXT NOT NULL,
                  last_name TEXT NOT NULL,
                  birth_date TEXT NOT NULL,
                  section TEXT NOT NULL,
                  supervisor TEXT NOT NULL,
                  title TEXT NOT NULL,
                  filename TEXT NOT NULL,
                  upload_date TEXT NOT NULL,
                  status TEXT DEFAULT 'pending')''')
    
    # جدول المستخدمين (لتوسيع النظام لاحقاً)
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  role TEXT NOT NULL)''')
    
    conn.commit()
    conn.close()

# استدعاء تهيئة قاعدة البيانات
init_db()

# === إعداد مجلد التحميلات ===
UPLOAD_DIR = "uploaded_memos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# الأقسام المتاحة
sections = ["العلوم البيولوجية", "العلوم الفلاحية", "علوم التغذية", "علم البيئة والمحيط"]

# === وظائف إدارة الحالة ===
def reset_state():
    """إعادة تعيين حالة الجلسة"""
    keys = list(st.session_state.keys())
    for key in keys:
        if key != "rerun_flag":  # الحفاظ على علامة إعادة التشغيل
            del st.session_state[key]

def rerun():
    """إعادة تحميل الصفحة"""
    st.session_state["rerun_flag"] = not st.session_state.get("rerun_flag", False)

# === الواجهة الرئيسية ===
with st.container():
    st.markdown('<div class="main">', unsafe_allow_html=True)
    
    # إضافة شعار الجامعة
    try:
        logo = Image.open("university_logo.png")
        st.image(logo, width=150, use_column_width=False)
    except:
        pass
    
    st.markdown("<h1>📥 منصة إيداع مذكرات التخرج</h1>", unsafe_allow_html=True)
    st.markdown("<h4>جامعة محمد البشير الإبراهيمي - برج بوعريريج<br>كلية علوم الطبيعة و الحياة وعلوم الأرض والكون</h4>", unsafe_allow_html=True)

    # تهيئة متغيرات الجلسة
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.user_id = None
        st.session_state.rerun_flag = False

    if not st.session_state.logged_in:
        # واجهة تسجيل الدخول
        role = st.selectbox("👤 اختر نوع الدخول:", ["طالب", "مشرف", "مسؤول"])
        password = st.text_input("🔐 أدخل كلمة السر:", type="password")
        
        if st.button("دخول"):
            hashed_input = hash_password(password)
            if hashed_input == PASSWORDS.get(role):
                st.session_state.logged_in = True
                st.session_state.role = role
                st.session_state.user_id = role.lower()  # يمكن استبدالها ب ID حقيقي من قاعدة البيانات
                rerun()
            else:
                st.markdown('<div class="error-box">⚠️ كلمة السر غير صحيحة، حاول مرة أخرى.</div>', unsafe_allow_html=True)
                
        # رابط استعادة كلمة السر (وهمي في هذه المرحلة)
        st.markdown("[نسيت كلمة السر؟](#)", unsafe_allow_html=True)
    else:
        # واجهة بعد تسجيل الدخول
        st.markdown(f'<div class="success-box">✅ تم تسجيل الدخول كـ {st.session_state.role}</div>', unsafe_allow_html=True)
        
        if st.session_state.role == "طالب":
            # واجهة الطالب
            with st.form("student_form", clear_on_submit=True):
                st.subheader("📝 معلومات الطالب والمذكرة")
                
                col1, col2 = st.columns(2)
                with col1:
                    reg_num = st.text_input("🔢 رقم التسجيل*", help="الرقم الجامعي للطالب")
                    first_name = st.text_input("👤 الاسم*")
                    birth_date = st.date_input("📅 تاريخ الميلاد*", max_value=datetime.now())
                with col2:
                    last_name = st.text_input("👤 اللقب*")
                    section = st.selectbox("🏫 القسم*", sections)
                    supervisor = st.text_input("👨‍🏫 اسم المشرف*")
                
                title = st.text_input("📄 عنوان المذكرة*", help="العنوان الكامل للمذكرة")
                file = st.file_uploader("📎 تحميل ملف المذكرة (PDF فقط)*", type=["pdf"], accept_multiple_files=False)
                
                # شروط الإيداع
                st.markdown("""
                <div class="info-box">
                    <strong>شروط إيداع المذكرة:</strong>
                    <ul>
                        <li>يجب أن يكون الملف بصيغة PDF</li>
                        <li>يجب ألا يتجاوز حجم الملف 10MB</li>
                        <li>يجب تعبئة جميع الحقول المميزة بعلامة (*)</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
                submitted = st.form_submit_button("📤 إيداع المذكرة")
                if submitted:
                    if all([reg_num, first_name, last_name, section, supervisor, title, file]):
                        if file.size > 10 * 1024 * 1024:  # 10MB حد أقصى
                            st.markdown('<div class="error-box">⚠️ حجم الملف كبير جداً (الحد الأقصى 10MB)</div>', unsafe_allow_html=True)
                        else:
                            # حفظ الملف
                            section_folder = os.path.join(UPLOAD_DIR, section)
                            os.makedirs(section_folder, exist_ok=True)
                            
                            filename = f"{reg_num}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                            file_path = os.path.join(section_folder, filename)
                            
                            with open(file_path, "wb") as f:
                                f.write(file.getbuffer())
                            
                            # حفظ البيانات في قاعدة البيانات
                            conn = sqlite3.connect('theses.db')
                            c = conn.cursor()
                            c.execute('''INSERT INTO theses 
                                      (reg_num, first_name, last_name, birth_date, section, supervisor, title, filename, upload_date, status)
                                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                      (reg_num, first_name, last_name, birth_date.strftime("%Y-%m-%d"), 
                                       section, supervisor, title, filename, 
                                       datetime.now().strftime("%Y-%m-%d %H:%M"), "pending"))
                            conn.commit()
                            conn.close()
                            
                            st.markdown('<div class="success-box">✅ تم إيداع المذكرة بنجاح وسيتم مراجعتها من قبل المشرف.</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="error-box">⚠️ يرجى ملء جميع الحقول المطلوبة وتحميل ملف المذكرة.</div>', unsafe_allow_html=True)
            
            # دليل الإيداع
            with st.expander("🛈 دليل إيداع المذكرات"):
                st.markdown("""
                **خطوات إيداع مذكرة التخرج:**
                1. قم بتعبئة جميع حقول النموذج
                2. تأكد من صحة المعلومات المدخلة
                3. اختر ملف المذكرة بصيغة PDF
                4. اضغط على زر "إيداع المذكرة"
                5. ستصلك رسالة تأكيد بنجاح الإيداع
                
                **ملاحظات مهمة:**
                - لا يمكن تعديل المذكرة بعد الإيداع
                - سيتم إعلامك عند مراجعة المذكرة من قبل المشرف
                - يمكنك التواصل مع الدعم الفني عند وجود أي مشكلة
                """)
        
        elif st.session_state.role in ["مشرف", "مسؤول"]:
            # واجهة المشرف/المسؤول
            conn = sqlite3.connect('theses.db')
            df = pd.read_sql_query("SELECT * FROM theses", conn)
            conn.close()
            
            # لوحة الإحصائيات
            st.subheader("📊 لوحة التحكم والإحصائيات")
            
            col1, col2, col3 = st.columns(3)
            col1.markdown(f"<div class='metric'>📚 عدد المذكرات<br><b>{len(df)}</b></div>", unsafe_allow_html=True)
            col2.markdown(f"<div class='metric'>📁 الأقسام<br><b>{df['section'].nunique()}</b></div>", unsafe_allow_html=True)
            col3.markdown(f"<div class='metric'>👨‍🏫 المشرفين<br><b>{df['supervisor'].nunique()}</b></div>", unsafe_allow_html=True)
            
            # تصفية البيانات
            st.subheader("🔍 تصفية المذكرات")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                selected_section = st.selectbox("القسم:", ["الكل"] + sections)
            with col2:
                supervisors = ["الكل"] + sorted(df["supervisor"].unique().tolist())
                selected_supervisor = st.selectbox("المشرف:", supervisors)
            with col3:
                status_options = ["الكل", "pending", "approved", "rejected"]
                selected_status = st.selectbox("الحالة:", status_options)
            
            # تطبيق التصفية
            filtered_df = df.copy()
            if selected_section != "الكل":
                filtered_df = filtered_df[filtered_df["section"] == selected_section]
            if selected_supervisor != "الكل":
                filtered_df = filtered_df[filtered_df["supervisor"] == selected_supervisor]
            if selected_status != "الكل":
                filtered_df = filtered_df[filtered_df["status"] == selected_status]
            
            # عرض المذكرات
            st.subheader("📄 المذكرات المقدمة")
            
            if filtered_df.empty:
                st.markdown('<div class="info-box">لا توجد مذكرات لعرضها حسب التصفية المحددة.</div>', unsafe_allow_html=True)
            else:
                for _, row in filtered_df.iterrows():
                    with st.expander(f"{row['title']} - {row['status']}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**الطالب:** {row['first_name']} {row['last_name']}")
                            st.markdown(f"**رقم التسجيل:** {row['reg_num']}")
                            st.markdown(f"**تاريخ الميلاد:** {row['birth_date']}")
                        with col2:
                            st.markdown(f"**القسم:** {row['section']}")
                            st.markdown(f"**المشرف:** {row['supervisor']}")
                            st.markdown(f"**تاريخ الإيداع:** {row['upload_date']}")
                        
                        # حالة المذكرة (للمشرفين فقط)
                        if st.session_state.role in ["مشرف", "مسؤول"]:
                            status = st.selectbox(
                                "تغيير الحالة:",
                                ["pending", "approved", "rejected"],
                                index=["pending", "approved", "rejected"].index(row["status"]),
                                key=f"status_{row['id']}"
                            )
                            
                            if st.button("حفظ التغييرات", key=f"save_{row['id']}"):
                                conn = sqlite3.connect('theses.db')
                                c = conn.cursor()
                                c.execute("UPDATE theses SET status = ? WHERE id = ?", (status, row["id"]))
                                conn.commit()
                                conn.close()
                                st.success("تم تحديث حالة المذكرة بنجاح")
                                rerun()
                        
                        # زر التحميل
                        file_path = os.path.join(UPLOAD_DIR, row['section'], row['filename'])
                        if os.path.exists(file_path):
                            st.download_button(
                                label="⬇️ تحميل المذكرة",
                                data=open(file_path, "rb").read(),
                                file_name=row['filename'],
                                mime="application/pdf",
                                key=f"download_{row['id']}"
                            )
                        else:
                            st.markdown('<div class="error-box">ملف المذكرة غير موجود!</div>', unsafe_allow_html=True)
            
            # ميزات إضافية للمسؤولين
            if st.session_state.role == "مسؤول":
                st.subheader("⚙️ أدوات الإدارة")
                
                if st.button("تصدير جميع البيانات إلى Excel"):
                    excel_file = "theses_export.xlsx"
                    df.to_excel(excel_file, index=False)
                    st.download_button(
                        label="⬇️ تحميل ملف Excel",
                        data=open(excel_file, "rb").read(),
                        file_name="theses_export.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                
                if st.button("حذف جميع البيانات", key="delete_all"):
                    st.warning("هذا الإجراء سيحذف جميع البيانات بشكل دائم. تأكد قبل المتابعة.")
                    if st.button("تأكيد الحذف", key="confirm_delete"):
                        conn = sqlite3.connect('theses.db')
                        c = conn.cursor()
                        c.execute("DELETE FROM theses")
                        conn.commit()
                        conn.close()
                        st.success("تم حذف جميع البيانات بنجاح")
                        rerun()
        
        # زر تسجيل الخروج
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button("🚪 تسجيل خروج"):
            reset_state()
            rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # تذييل الصفحة
    st.markdown("""
    <div style="text-align: center; margin-top: 2rem; color: #666; font-size: 0.9rem;">
        <hr>
        <p>منصة إيداع مذكرات التخرج - جامعة محمد البشير الإبراهيمي © 2023</p>
        <p>للإبلاغ عن مشاكل تقنية يرجى التواصل على: support@univ-bba.dz</p>
    </div>
    """, unsafe_allow_html=True)