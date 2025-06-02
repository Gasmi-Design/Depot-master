import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import os
from datetime import datetime

# --- إعداد المستخدمين (مثال) ---
credentials = {
    "usernames": {
        "student1": {
            "name": "طالب 1",
            "password": "$2b$12$X0OWVC4GHnZAzA/yiZcNYOPblUwU9BC5IGGv2bwkM0ltm07qlYZmG"  # pass123
        },
        "supervisor1": {
            "name": "مشرف 1",
            "password": "$2b$12$A9h0aPv89dNKYO7URNTQDuClzKUxJNT2RW04xyqSBoQikmyRRAeYq"  # sup123
        }
    }
}

# --- إعداد صفحة ستريملت ---
st.set_page_config(page_title="منصة إيداع مذكرات التخرج", layout="centered")

# --- تهيئة المصادقة ---
authenticator = stauth.Authenticate(
    credentials,
    "graduation_memo_app", "auth_token",
    cookie_expiry_days=1
)

name, authentication_status, username = authenticator.login("تسجيل الدخول", "main")

# --- مسارات ---
UPLOAD_DIR = "uploaded_memos"
os.makedirs(UPLOAD_DIR, exist_ok=True)
data_file = "data.csv"
sections = ["العلوم البيولوجية", "العلوم الفلاحية", "علوم التغذية", "علم البيئة والمحيط"]

if not os.path.exists(data_file):
    df_init = pd.DataFrame(columns=[
        "رقم التسجيل", "الاسم", "اللقب", "تاريخ الميلاد",
        "القسم", "المشرف", "عنوان المذكرة", "اسم الملف", "تاريخ الإيداع"
    ])
    df_init.to_csv(data_file, index=False, encoding="utf-8")


# --- الوظائف المساعدة ---
def save_memo(data):
    df = pd.read_csv(data_file)
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(data_file, index=False, encoding="utf-8")


# --- واجهة المستخدم ---
if authentication_status:
    authenticator.logout("تسجيل الخروج", "sidebar")
    st.markdown("<h1 style='text-align:center;'>📚 منصة إيداع مذكرات التخرج</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align:center;'>جامعة محمد البشير الإبراهيمي - كلية علوم الطبيعة والحياة</h4>", unsafe_allow_html=True)

    # طالب
    if username.startswith("student"):
        st.success(f"مرحباً بك {name} (طالب)")

        with st.form("memo_form", clear_on_submit=True):
            st.subheader("📝 نموذج إيداع المذكرة")

            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("الاسم")
            with col2:
                last_name = st.text_input("اللقب")

            reg_num = st.text_input("رقم التسجيل")
            birth_date = st.date_input("تاريخ الميلاد")
            section = st.selectbox("القسم", sections)
            supervisor = st.text_input("اسم المشرف")
            title = st.text_input("عنوان المذكرة")
            file = st.file_uploader("رفع ملف المذكرة (PDF فقط)", type=["pdf"])

            submitted = st.form_submit_button("إيداع المذكرة")

            if submitted:
                if all([reg_num, first_name, last_name, section, supervisor, title, file]):
                    section_dir = os.path.join(UPLOAD_DIR, section)
                    os.makedirs(section_dir, exist_ok=True)

                    filename = f"{reg_num}_{file.name}"
                    file_path = os.path.join(section_dir, filename)

                    with open(file_path, "wb") as f:
                        f.write(file.getbuffer())

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

    # مشرف
    elif username.startswith("supervisor"):
        st.success(f"مرحباً بك {name} (مشرف)")
        st.subheader("📊 لوحة التحكم")

        df = pd.read_csv(data_file)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📄 عدد المذكرات", len(df))
        with col2:
            st.metric("🧪 الأقسام", df["القسم"].nunique())
        with col3:
            st.metric("👨‍🏫 المشرفون", df["المشرف"].nunique())

        st.subheader("🔍 تصفية المذكرات")

        col1, col2 = st.columns(2)
        with col1:
            selected_section = st.selectbox("القسم", ["الكل"] + sections)
        with col2:
            supervisors = ["الكل"] + sorted(df["المشرف"].unique().tolist())
            selected_supervisor = st.selectbox("المشرف", supervisors)

        filtered_df = df.copy()
        if selected_section != "الكل":
            filtered_df = filtered_df[filtered_df["القسم"] == selected_section]
        if selected_supervisor != "الكل":
            filtered_df = filtered_df[filtered_df["المشرف"] == selected_supervisor]

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
                        with open(file_path, "rb") as f:
                            st.download_button(
                                label="تحميل المذكرة",
                                data=f.read(),
                                file_name=row['اسم الملف'],
                                mime="application/pdf"
                            )
                    else:
                        st.error("الملف غير موجود في النظام")

else:
    if authentication_status is False:
        st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")
    elif authentication_status is None:
        st.info("👈 الرجاء إدخال بيانات الدخول")

