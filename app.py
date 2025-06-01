import streamlit as st
import os
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="منصة إيداع مذكرات التخرج", layout="centered")

# === إعداد CSS لتحسين الواجهة ===
st.markdown("""
<style>
    .main {
        background-color: #f5f7fa;
        padding: 3rem 2rem;
        border-radius: 15px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        max-width: 500px;
        margin: 3rem auto;
        font-family: 'Arial', sans-serif;
        color: #333;
    }
    .header {
        text-align: center;
        margin-bottom: 2rem;
    }
    h1 {
        color: #2c3e50;
        margin-bottom: 0.5rem;
        font-weight: 800;
        font-size: 2.2rem;
    }
    h4 {
        color: #34495e;
        margin-top: 0;
        margin-bottom: 1.5rem;
        font-weight: 500;
        line-height: 1.5;
        font-size: 1.3rem;
    }
    .login-box {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-top: 1.5rem;
    }
    .login-title {
        font-size: 1.5rem;
        color: #2980b9;
        text-align: center;
        margin-bottom: 1.5rem;
        font-weight: 700;
    }
    label, .stTextInput > div > input, .stSelectbox > div > div {
        font-size: 1.2rem !important;
        text-align: right !important;
        direction: rtl !important;
    }
    .stTextInput > div > input {
        text-align: right !important;
        padding: 0.75rem !important;
        font-size: 1.1rem !important;
    }
    button {
        width: 100%;
        background-color: #2980b9;
        color: white;
        padding: 0.75rem;
        font-size: 1.2rem;
        border-radius: 8px;
        border: none;
        margin-top: 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    button:hover {
        background-color: #3498db;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .university-logo {
        text-align: center;
        margin-bottom: 1rem;
    }
    .info-box {
        background: linear-gradient(135deg, #e6f2ff, #cce5ff);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        border-left: 5px solid #2980b9;
        font-size: 1.2rem;
        line-height: 1.8;
        text-align: right;
        direction: rtl;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    }
    .info-title {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 1rem;
        text-align: right;
    }
    /* بقية الأنماط الأصلية تبقى كما هي */
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
</style>
""", unsafe_allow_html=True)

# بقية الكود الأصلي يبقى كما هو حتى قسم الصفحة الرئيسية
# ... [الكود الأصلي يبقى كما هو حتى هنا]

# الصفحة الرئيسية وواجهة المستخدم
with st.container():
    st.markdown('<div class="main">', unsafe_allow_html=True)
    
    # الجزء المعدل من الصفحة الرئيسية
    st.markdown("""
    <div class="header">
        <div class="university-logo">
            <h1>📚 منصة إيداع مذكرات التخرج</h1>
            <h4>جامعة محمد البشير الإبراهيمي - برج بوعريريج<br>
            كلية علوم الطبيعة و الحياة وعلوم الأرض والكون</h4>
        </div>
    </div>
    
    <div class="info-box">
        <div class="info-title">🛈 معلومات هامة:</div>
        • يجب أن يكون الملف بصيغة PDF فقط<br>
        • الحد الأقصى لحجم الملف: 10 ميجابايت<br>
        • التأكد من صحة المعلومات قبل الإرسال النهائي
    </div>
    
    <div class="login-box">
        <div class="login-title">🔐 تسجيل الدخول إلى المنصة</div>
    """, unsafe_allow_html=True)

    # تهيئة المتغيرات الجلسية
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.username = None
        st.session_state.rerun_flag = False

    if not st.session_state.logged_in:
        role = st.selectbox("👤 اختر نوع الدخول:", ["طالب", "مشرف"])
        username = st.text_input("👤 اسم المستخدم")
        password = st.text_input("🔐 كلمة المرور:", type="password")
        
        if st.button("الدخول إلى المنصة"):
            if (role == "طالب" and username in PASSWORDS["طالب"] and password == PASSWORDS["طالب"][username]) or \
               (role == "مشرف" and username in PASSWORDS["مشرف"] and password == PASSWORDS["مشرف"][username]):
                st.session_state.logged_in = True
                st.session_state.role = role
                st.session_state.username = username
                rerun()
            else:
                st.error("⚠️ اسم المستخدم أو كلمة السر غير صحيحة، يرجى المحاولة مرة أخرى.")
    
    st.markdown("</div>", unsafe_allow_html=True)  # إغلاق login-box
    
    # بقية الكود الأصلي يبقى كما هو
    # ... [بقية الكود الأصلي]

    st.markdown('</div>', unsafe_allow_html=True)  # إغلاق main