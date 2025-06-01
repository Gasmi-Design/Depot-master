import streamlit as st
import os
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="منصة إيداع المذكرات", layout="wide")

# تحديد اللغة
if "lang" not in st.session_state:
    st.session_state.lang = "ar"

lang = st.selectbox("🌐 Language / اللغة", ["العربية", "Français"], index=0 if st.session_state.lang == "ar" else 1)
st.session_state.lang = "ar" if lang == "العربية" else "fr"

# قاموس الترجمة
T = {
    "ar": {
        "title": "📚 منصة إيداع مذكرات التخرج",
        "univ": "جامعة محمد البشير الإبراهيمي - برج بوعريريج<br>كلية علوم الطبيعة والحياة وعلوم الأرض والكون",
        "login": "تسجيل الدخول",
        "logout": "تسجيل الخروج",
        "student": "طالب",
        "supervisor": "مشرف",
        "username": "رقم التسجيل",
        "password": "كلمة المرور",
        "welcome": "مرحباً بك",
        "submit": "إيداع المذكرة",
        "name": "الاسم",
        "lastname": "اللقب",
        "regnum": "رقم التسجيل",
        "birthdate": "تاريخ الميلاد",
        "section": "القسم",
        "supervisor_name": "اسم المشرف",
        "title_memo": "عنوان المذكرة",
        "upload": "تحميل ملف المذكرة (PDF فقط)",
        "filter_memo": "تصفية المذكرات",
        "memo_list": "قائمة المذكرات",
        "no_memo": "لا توجد مذكرات حسب التصفية المحددة.",
        "download": "تحميل المذكرة"
    },
    "fr": {
        "title": "📚 Plateforme de dépôt des mémoires",
        "univ": "Université Mohamed El Bachir El Ibrahimi - Bordj Bou Arreridj<br>Faculté SNV et Sciences de la Terre",
        "login": "Connexion",
        "logout": "Déconnexion",
        "student": "Étudiant",
        "supervisor": "Encadrant",
        "username": "N° d'inscription",
        "password": "Mot de passe",
        "welcome": "Bienvenue",
        "submit": "Soumettre le mémoire",
        "name": "Prénom",
        "lastname": "Nom",
        "regnum": "N° d'inscription",
        "birthdate": "Date de naissance",
        "section": "Filière",
        "supervisor_name": "Nom de l'encadrant",
        "title_memo": "Titre du mémoire",
        "upload": "Télécharger le fichier mémoire (PDF uniquement)",
        "filter_memo": "Filtrer les mémoires",
        "memo_list": "Liste des mémoires",
        "no_memo": "Aucun mémoire ne correspond à ce filtre.",
        "download": "Télécharger"
    }
}

# إعداد CSS للتنسيق والمحاذاة حسب اللغة
direction = "rtl" if st.session_state.lang == "ar" else "ltr"
align = "right" if direction == "rtl" else "left"

st.markdown(f"""
<style>
    .block-container {{
        direction: {direction};
        text-align: {align};
        font-family: 'Cairo', sans-serif;
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }}
    h1, h4 {{ text-align: center; }}
</style>
""", unsafe_allow_html=True)

# المتغيرات الثابتة
STUDENT_PASSWORD = "student123"
SUPERVISOR_PASSWORD = "supervisor123"
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

with st.container():
    st.markdown(f"<h1>{T[st.session_state.lang]['title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h4>{T[st.session_state.lang]['univ']}</h4>", unsafe_allow_html=True)

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.rerun_flag = False

    if not st.session_state.logged_in:
        role = st.selectbox("👤 " + T[st.session_state.lang]['login'], [T[st.session_state.lang]['student'], T[st.session_state.lang]['supervisor']])
        password = st.text_input("🔐 " + T[st.session_state.lang]['password'], type="password")
        if st.button(T[st.session_state.lang]['login']):
            is_student = role == T[st.session_state.lang]['student']
            is_supervisor = role == T[st.session_state.lang]['supervisor']
            if (is_student and password == STUDENT_PASSWORD) or (is_supervisor and password == SUPERVISOR_PASSWORD):
                st.session_state.logged_in = True
                st.session_state.role = "طالب" if is_student else "مشرف"
                rerun()
            else:
                st.error("❌ " + T[st.session_state.lang]['password'] + " غير صحيحة.")

    else:
        if st.session_state.role == "طالب":
            st.success("✅ " + T[st.session_state.lang]['welcome'] + " " + T[st.session_state.lang]['student'])
            with st.form("student_form"):
                st.subheader("📝 " + T[st.session_state.lang]['submit'])
                col1, col2 = st.columns(2)
                with col1:
                    reg_num = st.text_input("🔢 " + T[st.session_state.lang]['regnum'])
                    first_name = st.text_input("👤 " + T[st.session_state.lang]['name'])
                    section = st.selectbox("🏫 " + T[st.session_state.lang]['section'], sections)
                with col2:
                    last_name = st.text_input("👤 " + T[st.session_state.lang]['lastname'])
                    birth_date = st.date_input("📅 " + T[st.session_state.lang]['birthdate'])
                    supervisor = st.text_input("👨‍🏫 " + T[st.session_state.lang]['supervisor_name'])
                title = st.text_input("📄 " + T[st.session_state.lang]['title_memo'])
                file = st.file_uploader("📎 " + T[st.session_state.lang]['upload'], type=["pdf"])
                submitted = st.form_submit_button(T[st.session_state.lang]['submit'])
                if submitted:
                    if all([reg_num, first_name, last_name, section, supervisor, title, file]):
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
                        st.success("✅ تمت العملية بنجاح.")
                    else:
                        st.error("⚠️ يرجى ملء جميع الحقول.")

        elif st.session_state.role == "مشرف":
            st.success("✅ " + T[st.session_state.lang]['welcome'] + " " + T[st.session_state.lang]['supervisor'])
            df = pd.read_csv(data_file)
            st.subheader("📊 إحصائيات")
            col1, col2, col3 = st.columns(3)
            col1.metric("📚 مذكرات", len(df))
            col2.metric("📁 الأقسام", df['القسم'].nunique())
            col3.metric("👨‍🏫 مشرفين", df['المشرف'].nunique())
            st.subheader("🔍 " + T[st.session_state.lang]['filter_memo'])
            selected_section = st.selectbox(T[st.session_state.lang]['section'], ["الكل"] + sections)
            selected_supervisor = st.selectbox(T[st.session_state.lang]['supervisor_name'], ["الكل"] + sorted(df["المشرف"].unique()))
            filtered_df = df.copy()
            if selected_section != "الكل":
                filtered_df = filtered_df[filtered_df["القسم"] == selected_section]
            if selected_supervisor != "الكل":
                filtered_df = filtered_df[filtered_df["المشرف"] == selected_supervisor]
            st.subheader("📄 " + T[st.session_state.lang]['memo_list'])
            if filtered_df.empty:
                st.info(T[st.session_state.lang]['no_memo'])
            else:
                for idx, row in filtered_df.iterrows():
                    with st.expander(f"📌 {row['عنوان المذكرة']}"):
                        st.markdown(f"**{T[st.session_state.lang]['name']}:** {row['الاسم']} {row['اللقب']}")
                        st.markdown(f"**{T[st.session_state.lang]['regnum']}**: {row['رقم التسجيل']}")
                        st.markdown(f"**{T[st.session_state.lang]['section']}**: {row['القسم']}")
                        st.markdown(f"**{T[st.session_state.lang]['supervisor_name']}**: {row['المشرف']}")
                        st.markdown(f"**📅 تاريخ الإيداع:** {row['تاريخ الإيداع']}")
                        file_path = os.path.join(UPLOAD_DIR, row['القسم'], row['اسم الملف'])
                        if os.path.exists(file_path):
                            st.download_button(label=f"⬇️ {T[st.session_state.lang]['download']}", data=open(file_path, "rb").read(), file_name=row['اسم الملف'], mime="application/pdf")
                        else:
                            st.error("❌ الملف غير موجود")

        if st.button("🚪 " + T[st.session_state.lang]['logout']):
            reset_state()
            rerun()
