import streamlit as st
import os
import pandas as pd
from datetime import datetime
import shutil

st.set_page_config(page_title="منصة إيداع مذكرات التخرج", layout="centered")

# === إعداد CSS لتحسين الواجهة ===
st.markdown("""
<style>
    .main {
        background-color: #f5f7fa;
        padding: 3rem 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        max-width: 480px;
        margin: 4rem auto 2rem auto;
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
        text-align: right !important;
        direction: rtl !important;
    }
    .stTextInput > div > input {
        text-align: right !important;
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
    }
    button:hover {
        background-color: #3498db;
        cursor: pointer;
    }
    .logout-btn {
        margin-top: 2rem;
        text-align: center;
    }
    .metric-container {
        display: flex;
        justify-content: space-around;
        margin-bottom: 1rem;
    }
    .metric {
        background: #eaf2f8;
        border-radius: 8px;
        padding: 1rem 1.5rem;
        width: 30%;
        text-align: center;
        font-weight: 600;
        color: #2c3e50;
    }
    .student-form {
        direction: rtl;
        text-align: right;
    }
    .student-form .stTextInput, 
    .student-form .stSelectbox, 
    .student-form .stDateInput,
    .student-form .stFileUploader {
        text-align: right;
        direction: rtl;
    }
    .warning {
        color: #e74c3c;
        font-weight: bold;
        text-align: center;
        margin: 1rem 0;
    }
    .delete-btn {
        background-color: #e74c3c !important;
        margin-top: 0.5rem !important;
    }
    .delete-btn:hover {
        background-color: #c0392b !important;
    }
    .file-actions {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    .memo-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        background: white;
    }
</style>
""", unsafe_allow_html=True)

import streamlit as st
import os
import pandas as pd
from datetime import datetime
import shutil

st.set_page_config(page_title="منصة إيداع مذكرات التخرج", layout="centered")

# === إعداد CSS لتحسين الواجهة ===
st.markdown("""
<style>
    .main {
        background-color: #f5f7fa;
        padding: 3rem 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        max-width: 480px;
        margin: 4rem auto 2rem auto;
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
        text-align: right !important;
        direction: rtl !important;
    }
    .stTextInput > div > input {
        text-align: right !important;
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
    }
    button:hover {
        background-color: #3498db;
        cursor: pointer;
    }
    .logout-btn {
        margin-top: 2rem;
        text-align: center;
    }
    .metric-container {
        display: flex;
        justify-content: space-around;
        margin-bottom: 1rem;
    }
    .metric {
        background: #eaf2f8;
        border-radius: 8px;
        padding: 1rem 1.5rem;
        width: 30%;
        text-align: center;
        font-weight: 600;
        color: #2c3e50;
    }
    .student-form {
        direction: rtl;
        text-align: right;
    }
    .student-form .stTextInput, 
    .student-form .stSelectbox, 
    .student-form .stDateInput,
    .student-form .stFileUploader {
        text-align: right;
        direction: rtl;
    }
    .warning {
        color: #e74c3c;
        font-weight: bold;
        text-align: center;
        margin: 1rem 0;
    }
    .delete-btn {
        background-color: #e74c3c !important;
        margin-top: 0.5rem !important;
    }
    .delete-btn:hover {
        background-color: #c0392b !important;
    }
    .file-actions {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    .memo-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        background: white;
    }
</style>
""", unsafe_allow_html=True)

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

UPLOAD_DIR = "uploaded_memos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

sections = ["العلوم البيولوجية", "العلوم الفلاحية", "علوم التغذية", "علم البيئة والمحيط"]
data_file = "data.csv"

if not os.path.exists(data_file):
    df_init = pd.DataFrame(columns=["رقم التسجيل", "الاسم", "اللقب", "تاريخ الميلاد", "القسم", "المشرف", "عنوان المذكرة", "اسم الملف", "تاريخ الإيداع"])
    df_init.to_csv(data_file, index=False, encoding="utf-8")

def reset_state():
    keys = list(st.session_state.keys())
    for key in keys:
        del st.session_state[key]

def rerun():
    st.session_state["rerun_flag"] = not st.session_state.get("rerun_flag", False)

def is_student_registered(reg_num):
    if not os.path.exists(data_file):
        return False
    df = pd.read_csv(data_file)
    return reg_num in df["رقم التسجيل"].values

def delete_memo(reg_num, section, filename):
    try:
        file_path = os.path.join(UPLOAD_DIR, section, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        df = pd.read_csv(data_file)
        df = df[df["رقم التسجيل"] != reg_num]
        df.to_csv(data_file, index=False, encoding="utf-8")
        return True
    except Exception as e:
        st.error(f"حدث خطأ أثناء حذف المذكرة: {str(e)}")
        return False

def handle_delete(reg_num, section, filename):
    success = delete_memo(reg_num, section, filename)
    if success:
        st.experimental_rerun()

# الصفحة الرئيسية وواجهة المستخدم
with st.container():
    st.markdown('<div class="main">', unsafe_allow_html=True)
    st.markdown("<h1>📥 منصة إيداع مذكرات التخرج</h1>", unsafe_allow_html=True)
    st.markdown("<h4>جامعة محمد البشير الإبراهيمي - برج بوعريريج<br>كلية علوم الطبيعة و الحياة وعلوم الأرض والكون</h4>", unsafe_allow_html=True)

    # تهيئة المتغيرات الجلسية
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.username = None
        st.session_state.rerun_flag = False

    if not st.session_state.logged_in:
        role = st.selectbox("👤 اختر نوع الدخول:", ["طالب", "مشرف"])
        username = st.text_input("👤 اسم المستخدم")
        password = st.text_input("🔐 أدخل كلمة السر:", type="password")
        
        if st.button("دخول"):
            if (role == "طالب" and username in PASSWORDS["طالب"] and password == PASSWORDS["طالب"][username]) or \
               (role == "مشرف" and username in PASSWORDS["مشرف"] and password == PASSWORDS["مشرف"][username]):
                st.session_state.logged_in = True
                st.session_state.role = role
                st.session_state.username = username
                rerun()
            else:
                st.error("⚠️ اسم المستخدم أو كلمة السر غير صحيحة، حاول مرة أخرى.")
    else:
        if st.session_state.role == "طالب":
            st.success(f"✅ تم تسجيل الدخول كطالب - {st.session_state.username}")
            
            # تحقق إذا كان الطالب قد سجل مذكرة بالفعل
            df = pd.read_csv(data_file)
            student_registered = is_student_registered(st.session_state.username)
            
            if student_registered:
                st.markdown('<div class="warning">⚠️ لقد قمت بتسجيل مذكرة مسبقاً ولا يمكنك تسجيل أكثر من مذكرة واحدة</div>', unsafe_allow_html=True)
                student_data = df[df["رقم التسجيل"] == st.session_state.username].iloc[0]
                
                with st.expander("عرض بيانات المذكرة المسجلة", expanded=True):
                    st.markdown(f"**الاسم:** {student_data['الاسم']} {student_data['اللقب']}")
                    st.markdown(f"**رقم التسجيل:** {student_data['رقم التسجيل']}")
                    st.markdown(f"**القسم:** {student_data['القسم']}")
                    st.markdown(f"**المشرف:** {student_data['المشرف']}")
                    st.markdown(f"**عنوان المذكرة:** {student_data['عنوان المذكرة']}")
                    st.markdown(f"**تاريخ الإيداع:** {student_data['تاريخ الإيداع']}")
                    
                    file_path = os.path.join(UPLOAD_DIR, student_data['القسم'], student_data['اسم الملف'])
                    if os.path.exists(file_path):
                        st.download_button(
                            label="⬇️ تحميل المذكرة", 
                            data=open(file_path, "rb").read(), 
                            file_name=student_data['اسم الملف'], 
                            mime="application/pdf"
                        )
                    else:
                        st.error("ملف المذكرة غير موجود!")
            else:
                with st.form("student_form"):
                    st.markdown('<div class="student-form">', unsafe_allow_html=True)
                    st.subheader("📝 معلومات الطالب")

                    reg_num = st.text_input("🔢 رقم التسجيل", value=st.session_state.username, disabled=True)
                    first_name = st.text_input("👤 الاسم")
                    last_name = st.text_input("👤 اللقب")
                    birth_date = st.date_input("📅 تاريخ الميلاد")
                    section = st.selectbox("🏫 القسم", sections)
                    supervisor = st.text_input("👨‍🏫 اسم المشرف")
                    title = st.text_input("📄 عنوان المذكرة")
                    file = st.file_uploader("📎 تحميل ملف المذكرة (PDF)", type=["pdf"])

                    submitted = st.form_submit_button("📤 إيداع")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    if submitted:
                        if all([reg_num, first_name, last_name, section, supervisor, title, file]):
                            if is_student_registered(reg_num):
                                st.error("⚠️ هذا الرقم مسجل بالفعل، لا يمكن تسجيل أكثر من مذكرة واحدة لكل طالب")
                            else:
                                section_folder = os.path.join(UPLOAD_DIR, section)
                                os.makedirs(section_folder, exist_ok=True)

                                filename = f"{reg_num}_{file.name}"
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
                                    "تاريخ الإيداع": datetime.now().strftime("%Y-%m-%d %H:%M")
                                }
                                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                                df.to_csv(data_file, index=False, encoding="utf-8")

                                st.success("✅ تم إيداع المذكرة بنجاح.")
                                st.experimental_rerun()
                        else:
                            st.error("⚠️ يرجى ملء جميع الحقول وتحميل ملف.")

        elif st.session_state.role == "مشرف":
            st.success(f"✅ تم تسجيل الدخول كمشرف - {st.session_state.username}")

            df = pd.read_csv(data_file)

            st.subheader("📊 إحصائيات")
            col1, col2, col3 = st.columns(3)
            col1.markdown(f"<div class='metric'>📚 عدد المذكرات الكلي<br><b>{len(df)}</b></div>", unsafe_allow_html=True)
            col2.markdown(f"<div class='metric'>📁 عدد الأقسام<br><b>{df['القسم'].nunique()}</b></div>", unsafe_allow_html=True)
            col3.markdown(f"<div class='metric'>👨‍🏫 عدد المشرفين<br><b>{df['المشرف'].nunique()}</b></div>", unsafe_allow_html=True)

            st.subheader("🔍 تصفية وبحث")
            selected_section = st.selectbox("اختر قسمًا:", ["الكل"] + sections)
            selected_supervisor = st.selectbox("اختر مشرفًا:", ["الكل"] + sorted(df["المشرف"].unique()))

            filtered_df = df.copy()
            if selected_section != "الكل":
                filtered_df = filtered_df[filtered_df["القسم"] == selected_section]
            if selected_supervisor != "الكل":
                filtered_df = filtered_df[filtered_df["المشرف"] == selected_supervisor]

            st.subheader("📄 قائمة المذكرات")

            if filtered_df.empty:
                st.info("لا توجد مذكرات لعرضها حسب التصفية المحددة.")
            else:
                for idx, row in filtered_df.iterrows():
                    with st.expander(f"📌 {row['عنوان المذكرة']} - {row['الاسم']} {row['اللقب']}", expanded=False):
                        st.markdown(f"**الاسم:** {row['الاسم']} {row['اللقب']}")
                        st.markdown(f"**رقم التسجيل:** {row['رقم التسجيل']}")
                        st.markdown(f"**القسم:** {row['القسم']}")
                        st.markdown(f"**المشرف:** {row['المشرف']}")
                        st.markdown(f"**عنوان المذكرة:** {row['عنوان المذكرة']}")
                        st.markdown(f"**تاريخ الإيداع:** {row['تاريخ الإيداع']}")
                        
                        file_path = os.path.join(UPLOAD_DIR, row['القسم'], row['اسم الملف'])
                        file_exists = os.path.exists(file_path)
                        
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            if file_exists:
                                st.download_button(
                                    label="⬇️ تحميل المذكرة", 
                                    data=open(file_path, "rb").read(), 
                                    file_name=row['اسم الملف'], 
                                    mime="application/pdf",
                                    key=f"download_{row['رقم التسجيل']}"
                                )
                            else:
                                st.error("ملف المذكرة غير موجود!")
                        
                        with col2:
         if st.button("🗑️ حذف", key=f"delete_{row['رقم التسجيل']}"):
         handle_delete(row['رقم التسجيل'], row['القسم'], row['اسم الملف'])

                                pass

        # زر الخروج في الأسفل
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button("🚪 تسجيل خروج"):
            reset_state()
            rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)