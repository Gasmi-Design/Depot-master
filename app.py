import streamlit as st
import os
import pandas as pd
from datetime import datetime
import base64

# إعدادات الصفحة
st.set_page_config(
    page_title="منصة إيداع مذكرات التخرج",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# === إعداد CSS مخصص مع تحسينات جمالية ===
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# إنشاء ملف CSS إذا لم يكن موجوداً
if not os.path.exists("styles.css"):
    with open("styles.css", "w", encoding="utf-8") as f:
        f.write("""
:root {
    --primary-color: #3498db;
    --secondary-color: #2980b9;
    --accent-color: #e74c3c;
    --light-bg: #f8f9fa;
    --dark-text: #2c3e50;
    --light-text: #7f8c8d;
    --success-color: #2ecc71;
    --warning-color: #f39c12;
    --border-radius: 12px;
    --box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    --transition: all 0.3s ease;
}

* {
    font-family: 'Tajawal', 'Segoe UI', sans-serif;
}

.main-container {
    background-color: white;
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow);
    padding: 2.5rem;
    margin: 2rem auto;
    max-width: 800px;
}

.header {
    text-align: center;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #eee;
}

.header h1 {
    color: var(--primary-color);
    font-weight: 700;
    margin-bottom: 0.5rem;
}

.header h4 {
    color: var(--light-text);
    font-weight: 400;
    line-height: 1.6;
}

.stButton>button {
    background-color: var(--primary-color);
    color: white;
    border: none;
    border-radius: var(--border-radius);
    padding: 0.75rem 1.5rem;
    font-size: 1rem;
    font-weight: 500;
    transition: var(--transition);
    width: 100%;
}

.stButton>button:hover {
    background-color: var(--secondary-color);
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(0,0,0,0.1);
}

.stTextInput>div>div>input, .stSelectbox>div>div>select {
    border-radius: var(--border-radius) !important;
    border: 1px solid #ddd !important;
    padding: 0.75rem !important;
}

.stTextInput>div>div>input:focus, .stSelectbox>div>div>select:focus {
    border-color: var(--primary-color) !important;
    box-shadow: 0 0 0 2px rgba(52,152,219,0.2) !important;
}

.card {
    background: white;
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow);
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    transition: var(--transition);
}

.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
}

.card-title {
    color: var(--primary-color);
    font-weight: 600;
    margin-bottom: 0.75rem;
}

.metric-container {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 2rem;
}

.metric {
    flex: 1;
    background: linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%);
    border-radius: var(--border-radius);
    padding: 1.5rem;
    text-align: center;
    box-shadow: var(--box-shadow);
}

.metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--primary-color);
    margin: 0.5rem 0;
}

.metric-label {
    font-size: 0.9rem;
    color: var(--light-text);
}

.success-message {
    background-color: rgba(46, 204, 113, 0.1);
    border-left: 4px solid var(--success-color);
    padding: 1rem;
    border-radius: 0 var(--border-radius) var(--border-radius) 0;
    margin: 1rem 0;
}

.error-message {
    background-color: rgba(231, 76, 60, 0.1);
    border-left: 4px solid var(--accent-color);
    padding: 1rem;
    border-radius: 0 var(--border-radius) var(--border-radius) 0;
    margin: 1rem 0;
}

.tabs {
    display: flex;
    margin-bottom: 1.5rem;
    border-bottom: 1px solid #eee;
}

.tab {
    padding: 0.75rem 1.5rem;
    cursor: pointer;
    border-bottom: 3px solid transparent;
    transition: var(--transition);
}

.tab.active {
    border-bottom: 3px solid var(--primary-color);
    color: var(--primary-color);
    font-weight: 600;
}

.tab:hover:not(.active) {
    border-bottom: 3px solid #ddd;
}

/* تأثيرات للعناصر التفاعلية */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.animated {
    animation: fadeIn 0.5s ease forwards;
}

/* تصميم متجاوب */
@media (max-width: 768px) {
    .main-container {
        padding: 1.5rem;
        margin: 1rem;
    }
    
    .metric-container {
        flex-direction: column;
    }
}
""")

local_css("styles.css")

# === وظائف مساعدة ===
def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url(data:image/png;base64,{encoded_string.decode()});
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
            background-repeat: no-repeat;
            background-color: #f5f7fa;
            background-blend-mode: overlay;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# === قاعدة بيانات كلمات المرور ===
PASSWORDS = {
    "طالب": {
        "student1": "pass123",
        "student2": "pass456",
        "student3": "pass789"
    },
    "مشرف": {
        "supervisor1": "sup123",
        "supervisor2": "sup456",
        "dr_ahmed": "ahmed123"  # مثال لمشرف مع اسم محدد
    }
}

UPLOAD_DIR = "uploaded_memos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

sections = ["العلوم البيولوجية", "العلوم الفلاحية", "علوم التغذية", "علم البيئة والمحيط"]
data_file = "data.csv"

if not os.path.exists(data_file):
    df_init = pd.DataFrame(columns=[
        "رقم التسجيل", "الاسم", "اللقب", "تاريخ الميلاد", 
        "القسم", "المشرف", "عنوان المذكرة", "اسم الملف", 
        "تاريخ الإيداع", "حالة المراجعة", "ملاحظات المشرف"
    ])
    df_init.to_csv(data_file, index=False, encoding="utf-8")

def reset_state():
    keys = list(st.session_state.keys())
    for key in keys:
        del st.session_state[key]

def rerun():
    st.session_state["rerun_flag"] = not st.session_state.get("rerun_flag", False)

# === واجهة المستخدم ===
def login_page():
    with st.container():
        st.markdown("""
        <div class="main-container animated">
            <div class="header">
                <h1>🎓 منصة إيداع مذكرات التخرج</h1>
                <h4>جامعة محمد البشير الإبراهيمي - برج بوعريريج<br>
                كلية علوم الطبيعة و الحياة وعلوم الأرض والكون</h4>
            </div>
        """, unsafe_allow_html=True)
        
        role = st.selectbox("👤 اختر نوع الدخول:", ["طالب", "مشرف"], key="login_role")
        username = st.text_input("👤 اسم المستخدم", key="login_username")
        password = st.text_input("🔐 كلمة المرور", type="password", key="login_password")
        
        if st.button("تسجيل الدخول", key="login_btn"):
            if (role == "طالب" and username in PASSWORDS["طالب"] and password == PASSWORDS["طالب"][username]) or \
               (role == "مشرف" and username in PASSWORDS["مشرف"] and password == PASSWORDS["مشرف"][username]):
                st.session_state.logged_in = True
                st.session_state.role = role
                st.session_state.username = username
                st.session_state.current_page = "dashboard"
                rerun()
            else:
                st.error("اسم المستخدم أو كلمة المرور غير صحيحة. يرجى المحاولة مرة أخرى.")
        
        st.markdown("""
            <div style="text-align: center; margin-top: 2rem; color: #7f8c8d;">
                <p>نسيت كلمة المرور؟ يرجى التواصل مع الدعم الفني</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

def student_dashboard():
    with st.container():
        st.markdown(f"""
        <div class="main-container animated">
            <div class="header">
                <h1>مرحباً بك، {st.session_state.username}</h1>
                <h4>منصة إيداع مذكرات التخرج - لوحة الطالب</h4>
            </div>
        """, unsafe_allow_html=True)
        
        # تبويبات لوحة الطالب
        tabs = st.session_state.get("student_tabs", "إيداع مذكرة")
        if tabs == "إيداع مذكرة":
            with st.form("student_form", clear_on_submit=True):
                st.markdown("### 📝 نموذج إيداع المذكرة")
                
                col1, col2 = st.columns(2)
                with col1:
                    reg_num = st.text_input("🔢 رقم التسجيل الجامعي*")
                    first_name = st.text_input("👤 الاسم الأول*")
                    section = st.selectbox("🏫 القسم العلمي*", sections)
                with col2:
                    last_name = st.text_input("👤 اللقب*")
                    birth_date = st.date_input("📅 تاريخ الميلاد*", max_value=datetime.now())
                    supervisor = st.text_input("👨‍🏫 اسم المشرف الأكاديمي*")
                
                title = st.text_input("📄 عنوان المذكرة*")
                file = st.file_uploader("📎 رفع ملف المذكرة (PDF فقط)*", type=["pdf"])
                
                st.markdown("<small>الحقول المميزة بعلامة (*) إلزامية</small>", unsafe_allow_html=True)
                
                if st.form_submit_button("📤 تقديم المذكرة"):
                    if all([reg_num, first_name, last_name, section, supervisor, title, file]):
                        section_folder = os.path.join(UPLOAD_DIR, section)
                        os.makedirs(section_folder, exist_ok=True)

                        filename = f"{reg_num}_{first_name}_{last_name}_{file.name}"
                        file_path = os.path.join(section_folder, filename)

                        with open(file_path, "wb") as f:
                            f.write(file.getbuffer())

                        df = pd.read_csv(data_file)
                        new_row = {
                            "رقم التسجيل": reg_num,
                            "الاسم": first_name,
                            "اللقب": last_name,
                            "تاريخ الميلاد": birth_date.strftime("%Y-%m-%d"),
                            "القسم": section,
                            "المشرف": supervisor,
                            "عنوان المذكرة": title,
                            "اسم الملف": filename,
                            "تاريخ الإيداع": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "حالة المراجعة": "قيد المراجعة",
                            "ملاحظات المشرف": ""
                        }
                        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                        df.to_csv(data_file, index=False, encoding="utf-8")

                        st.success("✅ تم إيداع المذكرة بنجاح وسيتم مراجعتها من قبل المشرف.")
                    else:
                        st.error("⚠️ يرجى ملء جميع الحقول الإلزامية وتحميل ملف المذكرة.")
        
        st.markdown("</div>", unsafe_allow_html=True)

def supervisor_dashboard():
    with st.container():
        st.markdown(f"""
        <div class="main-container animated">
            <div class="header">
                <h1>مرحباً بك، {st.session_state.username}</h1>
                <h4>منصة إيداع مذكرات التخرج - لوحة المشرفين</h4>
            </div>
        """, unsafe_allow_html=True)
        
        # تبويبات لوحة المشرف
        tabs = st.session_state.get("supervisor_tabs", "المذكرات")
        if tabs == "المذكرات":
            df = pd.read_csv(data_file)
            
            # إحصائيات سريعة
            st.markdown("### 📊 لوحة التحكم")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("""
                <div class="metric">
                    <div class="metric-value">{}</div>
                    <div class="metric-label">المذكرات الكلية</div>
                </div>
                """.format(len(df)), unsafe_allow_html=True)
            with col2:
                st.markdown("""
                <div class="metric">
                    <div class="metric-value">{}</div>
                    <div class="metric-label">تحت المراجعة</div>
                </div>
                """.format(len(df[df["حالة المراجعة"] == "قيد المراجعة"])), unsafe_allow_html=True)
            with col3:
                st.markdown("""
                <div class="metric">
                    <div class="metric-value">{}</div>
                    <div class="metric-label">مقبولة</div>
                </div>
                """.format(len(df[df["حالة المراجعة"] == "مقبولة"])), unsafe_allow_html=True)
            
            # أدوات التصفية
            st.markdown("### 🔍 تصفية المذكرات")
            filter_col1, filter_col2, filter_col3 = st.columns(3)
            with filter_col1:
                selected_section = st.selectbox("القسم", ["الكل"] + sections)
            with filter_col2:
                selected_status = st.selectbox("حالة المراجعة", ["الكل", "قيد المراجعة", "مقبولة", "مرفوضة"])
            with filter_col3:
                selected_supervisor = st.selectbox("المشرف", ["الكل"] + sorted(df["المشرف"].unique()))
            
            # تطبيق التصفية
            filtered_df = df.copy()
            if selected_section != "الكل":
                filtered_df = filtered_df[filtered_df["القسم"] == selected_section]
            if selected_status != "الكل":
                filtered_df = filtered_df[filtered_df["حالة المراجعة"] == selected_status]
            if selected_supervisor != "الكل":
                filtered_df = filtered_df[filtered_df["المشرف"] == selected_supervisor]
            
            # عرض المذكرات
            st.markdown(f"### 📄 المذكرات ({len(filtered_df)})")
            
            if filtered_df.empty:
                st.markdown("""
                <div class="card">
                    <p style="text-align: center; color: var(--light-text);">لا توجد مذكرات متاحة حسب معايير التصفية المحددة</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                for idx, row in filtered_df.iterrows():
                    with st.expander(f"📌 {row['عنوان المذكرة']} - {row['حالة المراجعة']}", expanded=False):
                        st.markdown(f"""
                        <div class="card">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 1rem;">
                                <div>
                                    <p><strong>الطالب:</strong> {row['الاسم']} {row['اللقب']}</p>
                                    <p><strong>رقم التسجيل:</strong> {row['رقم التسجيل']}</p>
                                    <p><strong>القسم:</strong> {row['القسم']}</p>
                                </div>
                                <div>
                                    <p><strong>المشرف:</strong> {row['المشرف']}</p>
                                    <p><strong>تاريخ الإيداع:</strong> {row['تاريخ الإيداع']}</p>
                                    <p><strong>الحالة:</strong> {row['حالة المراجعة']}</p>
                                </div>
                            </div>
                            
                            <div style="margin-top: 1rem;">
                        """, unsafe_allow_html=True)
                        
                        file_path = os.path.join(UPLOAD_DIR, row['القسم'], row['اسم الملف'])
                        if os.path.exists(file_path):
                            st.download_button(
                                label="⬇️ تحميل المذكرة",
                                data=open(file_path, "rb").read(),
                                file_name=row['اسم الملف'],
                                mime="application/pdf"
                            )
                        else:
                            st.error("الملف غير متوفر!")
                        
                        # للمشرفين فقط: إضافة ملاحظات وتغيير الحالة
                        if st.session_state.role == "مشرف":
                            with st.form(f"review_form_{idx}"):
                                status = st.selectbox(
                                    "تغيير حالة المراجعة",
                                    ["قيد المراجعة", "مقبولة", "مرفوضة"],
                                    index=["قيد المراجعة", "مقبولة", "مرفوضة"].index(row['حالة المراجعة']),
                                    key=f"status_{idx}"
                                )
                                notes = st.text_area(
                                    "ملاحظات المشرف",
                                    value=row.get('ملاحظات المشرف', ''),
                                    key=f"notes_{idx}"
                                )
                                
                                if st.form_submit_button("حفظ التغييرات"):
                                    df.at[idx, 'حالة المراجعة'] = status
                                    df.at[idx, 'ملاحظات المشرف'] = notes
                                    df.to_csv(data_file, index=False, encoding="utf-8")
                                    st.success("تم تحديث حالة المذكرة بنجاح!")
                                    st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

# === إدارة حالة التطبيق ===
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None
    st.session_state.current_page = "login"

if not st.session_state.logged_in:
    login_page()
else:
    if st.session_state.role == "طالب":
        student_dashboard()
    elif st.session_state.role == "مشرف":
        supervisor_dashboard()
    
    # زر تسجيل الخروج
    st.markdown("""
    <div style="text-align: center; margin-top: 2rem;">
        <form>
            <button type="submit" name="logout" style="background-color: var(--accent-color); width: auto; padding: 0.5rem 1.5rem;">
                🚪 تسجيل الخروج
            </button>
        </form>
    </div>
    """, unsafe_allow_html=True)
    
    if st.query_params().get("logout"):
        reset_state()
        st.query_params.clear()
        st.rerun()