import streamlit as st
import os
import re
import pandas as pd
from datetime import datetime
from pathlib import Path
import tempfile
import shutil

# تهيئة إعدادات الصفحة
st.set_page_config(page_title="منصة إيداع مذكرات التخرج", layout="centered")

# === إعداد CSS لتحسين الواجهة ===
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
}

/* تصميم الإطار العام */
.main {
    background-color: #f5f5f5;
    padding: 3rem 2rem;
    border-radius: 10px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    max-width: 900px;
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
    font-size: 36px !important;
    text-align: center;
}

h2 {
    font-size: 28px !important;
}

h3 {
    font-size: 24px !important;
}

h4 {
    font-size: 22px !important;
    text-align: center;
}

/* الحقول */
.stTextInput input, .stSelectbox select, .stTextArea textarea {
    font-size: 1.1rem !important;
    font-weight: bold !important;
    color: #003366 !important;
}

/* الأزرار */
.stButton button {
    width: 100%;
    background-color: #4CAF50;
    color: white;
    padding: 0.75rem;
    font-size: 1.1rem;
    font-weight: bold;
    border-radius: 6px;
    border: none;
    margin-top: 1rem;
    transition: background-color 0.3s;
}

.stButton button:hover {
    background-color: #45a049;
}

/* تسجيل الخروج */
.logout-btn {
    margin-top: 2rem;
    text-align: center;
}

/* بطاقات الإحصائيات */
.metric-box {
    background: #e8f5e9;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
    text-align: center;
    font-size: 1.1rem;
    font-weight: bold;
    color: #003366;
}

/* الرسائل */
.success-msg {
    color: #2e7d32;
    background-color: #e8f5e9;
    padding: 1rem;
    border-radius: 4px;
    margin-bottom: 1rem;
    font-weight: bold;
}

.error-msg {
    color: #c62828;
    background-color: #ffebee;
    padding: 1rem;
    border-radius: 4px;
    margin-bottom: 1rem;
    font-weight: bold;
}

/* رؤوس expander */
.stExpanderHeader {
    font-size: 1.1rem !important;
    font-weight: bold !important;
    color: #003366 !important;
}
</style>

""", unsafe_allow_html=True)

# قاع��ة بيانات كلمات المرور (ملاحظة: تخزين كلمات المرور في النص صريح ليس آمناً للإنتاج)
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

# إعداد مجلد التحميل وملف البيانات
BASE_DIR = Path.cwd()
UPLOAD_DIR = BASE_DIR / "uploaded_memos"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

DATA_FILE = BASE_DIR / "data.csv"

# أعمدة ملف البيانات المتوقعة
CSV_COLUMNS = [
    "رقم التسجيل", "الاسم", "اللقب", "تاريخ الميلاد",
    "القسم", "المشرف", "عنوان المذكرة", "اسم الملف", "تاريخ الإيداع"
]

# تهيئة ملف البيانات إذا لم يكن موجوداً أو فارغاً
if not DATA_FILE.exists() or DATA_FILE.stat().st_size == 0:
    df_init = pd.DataFrame(columns=CSV_COLUMNS)
    # استخدم utf-8-sig لتحسين التوافق مع Excel إذا لزم الأمر
    df_init.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")

# وظائف مساعدة
def safe_filename(name: str) -> str:
    """
    ترجع اسم ملف آمن عن طريق استبدال الأحرف غير المسموح بها.
    نحافظ على الامتداد كما هو.
    """
    name = os.path.basename(name)  # إزالة أي أجزاء مسار
    parts = name.rsplit(".", 1)
    if len(parts) == 2:
        base, ext = parts
        ext = "." + ext
    else:
        base = parts[0]
        ext = ""
    # السماح للأحرف والحروف والأرقام والشرطات والشرطات السفلية والمسافات المحدودة
    base = re.sub(r"[^\w\s\-]", "", base)
    base = re.sub(r"\s+", "_", base)
    # تقليم الطول لتجنب مشاكل النظام
    return base[:200] + ext

def load_data() -> pd.DataFrame:
    try:
        df = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
        # التأكد من وجود الأعمدة المتوقعة
        for col in CSV_COLUMNS:
            if col not in df.columns:
                df[col] = ""
        return df[CSV_COLUMNS]
    except Exception:
        # إذا فشل القراءة، نعيد DataFrame فارغ بالأعمدة المطلوبة
        return pd.DataFrame(columns=CSV_COLUMNS)

def save_memo(record: dict):
    """
    يضيف سجل جديد إلى ملف CSV بطريقة أكثر أماناً (كتابة مؤقتة ثم استبدال).
    """
    df = load_data()
    df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
    # كتابة إلى ملف مؤقت ثم استبدال
    with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8-sig", newline="") as tmp:
        df.to_csv(tmp.name, index=False, encoding="utf-8-sig")
        tmp_path = tmp.name
    shutil.move(tmp_path, DATA_FILE)

def reset_session():
    # إعادة تهيئة مفاتيح الجلسة الأساسية
    keys = list(st.session_state.keys())
    for k in keys:
        del st.session_state[k]
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None

# تهيئة حالة الجلسة إذا لم تكن موجودة
if 'logged_in' not in st.session_state:
    reset_session()

# الأقسام المتاحة
sections = ["العلوم البيولوجية", "العلوم الفلاحية", "علوم التغذية", "علم البيئة والمحيط"]

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
            valid = False
            if role == "طالب":
                valid = username in PASSWORDS.get("طالب", {}) and password == PASSWORDS["طالب"].get(username)
            elif role == "مشرف":
                valid = username in PASSWORDS.get("مشرف", {}) and password == PASSWORDS["مشرف"].get(username)

            if valid:
                st.session_state.logged_in = True
                st.session_state.role = role
                st.session_state.username = username
                st.experimental_rerun()
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
                    if not all([reg_num, first_name, last_name, section, supervisor, title, file]):
                        st.error("⚠️ يرجى تعبئة جميع الحقول ورفع الملف")
                    else:
                        # حفظ الملف بشكل آمن
                        section_dir = UPLOAD_DIR / safe_filename(section)
                        section_dir.mkdir(parents=True, exist_ok=True)
                        filename = f"{reg_num}_{safe_filename(file.name)}"
                        file_path = section_dir / filename
                        try:
                            # اكتب الملف إلى المسار
                            with open(file_path, "wb") as f:
                                f.write(file.getbuffer())
                        except Exception as e:
                            st.error(f"خطأ عند حفظ الملف: {e}")
                        else:
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
                            try:
                                save_memo(memo_data)
                                st.success("✅ تم إيداع المذكرة بنجاح")
                            except Exception as e:
                                st.error(f"فشل في حفظ بيانات المذكرة: {e}")

        elif st.session_state.role == "مشرف":
            st.success(f"مرحباً بك {st.session_state.username} (مشرف)")

            # عرض الإحصائيات
            st.subheader("📊 لوحة التحكم")

            df = load_data()

            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f'<div class="metric-box">المذكرات المودعة<br><b>{len(df)}</b></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="metric-box">عدد الأقسام<br><b>{df["القسم"].nunique() if not df.empty else 0}</b></div>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div class="metric-box">عدد المشرفين<br><b>{df["المشرف"].nunique() if not df.empty else 0}</b></div>', unsafe_allow_html=True)

            # أدوات التصفية
            st.subheader("🔍 تصفية المذكرات")

            col1, col2 = st.columns(2)
            with col1:
                selected_section = st.selectbox("القسم", ["الكل"] + sections)
            with col2:
                supervisors = ["الكل"]
                if not df.empty:
                    supervisors += sorted(df["المشرف"].dropna().unique().tolist())
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
                        file_path = UPLOAD_DIR / safe_filename(row['القسم']) / row['اسم الملف']
                        if file_path.exists():
                            try:
                                with open(file_path, "rb") as f:
                                    file_bytes = f.read()
                                st.download_button(
                                    label="تحميل المذكرة",
                                    data=file_bytes,
                                    file_name=row['اسم الملف'],
                                    mime="application/pdf"
                                )
                            except Exception as e:
                                st.error(f"خطأ عند تحضير الملف للتحميل: {e}")
                        else:
                            st.error("الملف غير موجود في النظام")

        # زر تسجيل الخروج
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button("تسجيل الخروج"):
            reset_session()
            st.experimental_rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
