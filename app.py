import streamlit as st
import os
import pandas as pd
from datetime import datetime
import hashlib
import sqlite3
from PIL import Image
import arabic_reshaper
from bidi.algorithm import get_display

# --- تهيئة الصفحة ---
st.set_page_config(
    page_title="منصة إيداع مذكرات التخرج",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- تحميل الخطوط والأنماط CSS ---
def load_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Tajawal&display=swap');
        
        .arabic-ui {
            font-family: 'Tajawal', 'Arial', sans-serif !important;
            direction: rtl !important;
            text-align: right !important;
        }
        
        body {
            font-family: 'Tajawal', 'Arial', sans-serif;
        }
        .main {
            background-color: #f8f9fa;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        .header {
            background: linear-gradient(135deg, #2c3e50, #3498db);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            text-align: center;
        }
        .sidebar .sidebar-content {
            background: linear-gradient(180deg, #2c3e50, #34495e);
            color: white;
            padding: 1rem;
        }
        .card {
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            border-right: 5px solid #3498db;
        }
        .stButton>button {
            width: 100%;
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            border: none;
            padding: 0.75rem;
            border-radius: 8px;
            font-size: 1rem;
            transition: all 0.3s;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .success-msg {
            background-color: #d4edda;
            color: #155724;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            border-right: 5px solid #28a745;
        }
        .error-msg {
            background-color: #f8d7da;
            color: #721c24;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            border-right: 5px solid #dc3545;
        }
        .info-msg {
            background-color: #d1ecf1;
            color: #0c5460;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            border-right: 5px solid #17a2b8;
        }
        .metric-card {
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin: 0.5rem;
            border-top: 4px solid #3498db;
        }
        input, textarea, select {
            text-align: right !important;
            direction: rtl !important;
        }
        @media (max-width: 768px) {
            .header h1 {
                font-size: 1.5rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)

load_css()

# --- وظائف مساعدة للغة العربية ---
def arabic_text(text):
    if not text or not isinstance(text, str):
        return text
    try:
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        return bidi_text
    except Exception as e:
        print(f"Error in arabic_text: {e}")
        return text

# --- تهيئة قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('theses.db')
    c = conn.cursor()
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
    conn.commit()
    conn.close()

init_db()

# --- كلمات السر المشفرة ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

PASSWORDS = {
    "طالب": hash_password("student123"),
    "مشرف": hash_password("supervisor123"),
    "مسؤول": hash_password("admin123")
}

# قائمة الأقسام
sections = ["العلوم البيولوجية", "العلوم الفلاحية", "علوم التغذية", "علم البيئة والمحيط"]

# --- إدارة الجلسة ---
def reset_session():
    keys = list(st.session_state.keys())
    for key in keys:
        del st.session_state[key]

# --- الواجهة الرئيسية ---
def main():
    # --- الشريط الجانبي ---
    with st.sidebar:
        st.markdown(f"<div class='arabic-ui' style='text-align:center; margin-bottom:2rem;'>"
                    f"<h2>{arabic_text('منصة إيداع المذكرات')}</h2>"
                    f"<hr style='border-top:2px solid #3498db;'>"
                    f"</div>", unsafe_allow_html=True)
        
        if st.session_state.get("logged_in"):
            st.markdown(f"<div class='card arabic-ui'>{arabic_text('مرحباً بك، ')} "
                       f"<strong>{arabic_text(st.session_state.role)}</strong></div>", 
                       unsafe_allow_html=True)
            
            if st.button(arabic_text("تسجيل الخروج")):
                reset_session()
                st.experimental_rerun()
        else:
            st.markdown(f"<div class='arabic-ui'>{arabic_text('### تسجيل الدخول')}</div>", unsafe_allow_html=True)
            role = st.selectbox(arabic_text("نوع المستخدم"), ["طالب", "مشرف", "مسؤول"])
            password = st.text_input(arabic_text("كلمة المرور"), type="password")
            
            if st.button(arabic_text("دخول")):
                if hash_password(password) == PASSWORDS.get(role):
                    st.session_state.logged_in = True
                    st.session_state.role = role
                    st.experimental_rerun()
                else:
                    st.error(arabic_text("كلمة المرور غير صحيحة"))

    # --- المحتوى الرئيسي ---
    if not st.session_state.get("logged_in"):
        show_login_page()
    else:
        if st.session_state.role == "طالب":
            show_student_page()
        elif st.session_state.role in ["مشرف", "مسؤول"]:
            show_admin_page()

# --- صفحات التطبيق ---
def show_login_page():
    st.markdown(f"""
    <div class="header arabic-ui">
        <h1>{arabic_text('منصة إيداع مذكرات التخرج')}</h1>
        <h3>{arabic_text('جامعة محمد البشير الإبراهيمي - برج بوعريريج')}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown(f"""
        <div class="card arabic-ui" style="text-align:center;">
            <h3>{arabic_text('مرحباً بكم في المنصة')}</h3>
            <p>{arabic_text('لإيداع مذكرات الترجح، يرجى تسجيل الدخول باستخدام بياناتكم من الشريط الجانبي')}</p>
            <img src="https://via.placeholder.com/300x200?text=University+Logo" width="100%">
        </div>
        """, unsafe_allow_html=True)

def show_student_page():
    st.markdown(f"<div class='header arabic-ui'><h1>{arabic_text('نموذج إيداع مذكرة التخرج')}</h1></div>", 
                unsafe_allow_html=True)
    
    with st.form("student_form", clear_on_submit=True):
        st.markdown(f"<div class='card arabic-ui'>{arabic_text('المعلومات الشخصية')}</div>", 
                   unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            reg_num = st.text_input(arabic_text("رقم التسجيل *"))
            first_name = st.text_input(arabic_text("الاسم *"))
            birth_date = st.date_input(arabic_text("تاريخ الميلاد *"), 
                                      max_value=datetime.now())
        with col2:
            last_name = st.text_input(arabic_text("اللقب *"))
            section = st.selectbox(arabic_text("القسم *"), sections)
            supervisor = st.text_input(arabic_text("اسم المشرف *"))
        
        st.markdown(f"<div class='card arabic-ui'>{arabic_text('معلومات المذكرة')}</div>", 
                   unsafe_allow_html=True)
        
        title = st.text_input(arabic_text("عنوان المذكرة *"))
        file = st.file_uploader(arabic_text("رفع ملف المذكرة (PDF فقط) *"), 
                               type=["pdf"])
        
        st.markdown(f"""
        <div class="info-msg arabic-ui">
            <h4>{arabic_text('شروط الإيداع')}</h4>
            <ul>
                <li>{arabic_text('يجب أن يكون الملف بصيغة PDF')}</li>
                <li>{arabic_text('حجم الملف لا يتجاوز 10MB')}</li>
                <li>{arabic_text('يجب تعبئة جميع الحقول المميزة بعلامة (*)')}</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.form_submit_button(arabic_text("إيداع المذكرة")):
            if all([reg_num, first_name, last_name, section, supervisor, title, file]):
                if file.size > 10 * 1024 * 1024:  # 10MB حد أقصى
                    st.markdown(f"""
                    <div class="error-msg arabic-ui">
                        <h4>{arabic_text('خطأ في الإيداع')}</h4>
                        <p>{arabic_text('حجم الملف كبير جداً (الحد الأقصى 10MB)')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # حفظ الملف
                    section_folder = os.path.join("uploaded_memos", section)
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
                    
                    st.markdown(f"""
                    <div class="success-msg arabic-ui">
                        <h4>{arabic_text('تم الإيداع بنجاح')}</h4>
                        <p>{arabic_text('شكراً لك، تم إيداع مذكرتك بنجاح وسيتم مراجعتها من قبل المشرف')}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="error-msg arabic-ui">
                    <h4>{arabic_text('خطأ في الإيداع')}</h4>
                    <p>{arabic_text('الرجاء تعبئة جميع الحقول المطلوبة ورفع ملف المذكرة')}</p>
                </div>
                """, unsafe_allow_html=True)
    
    # دليل الإيداع
    with st.expander(arabic_text("🛈 دليل إيداع المذكرات")):
        st.markdown(f"""
        <div class="arabic-ui">
            <h4>{arabic_text('خطوات إيداع مذكرة التخرج:')}</h4>
            <ol>
                <li>{arabic_text('قم بتعبئة جميع حقول النموذج')}</li>
                <li>{arabic_text('تأكد من صحة المعلومات المدخلة')}</li>
                <li>{arabic_text('اختر ملف المذكرة بصيغة PDF')}</li>
                <li>{arabic_text('اضغط على زر "إيداع المذكرة"')}</li>
                <li>{arabic_text('ستصلك رسالة تأكيد بنجاح الإيداع')}</li>
            </ol>
            
            <h4>{arabic_text('ملاحظات مهمة:')}</h4>
            <ul>
                <li>{arabic_text('لا يمكن تعديل المذكرة بعد الإيداع')}</li>
                <li>{arabic_text('سيتم إعلامك عند مراجعة المذكرة من قبل المشرف')}</li>
                <li>{arabic_text('يمكنك التواصل مع الدعم الفني عند وجود أي مشكلة')}</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def show_admin_page():
    st.markdown(f"<div class='header arabic-ui'><h1>{arabic_text('لوحة التحكم - المشرفين')}</h1></div>", 
                unsafe_allow_html=True)
    
    conn = sqlite3.connect('theses.db')
    df = pd.read_sql_query("SELECT * FROM theses", conn)
    conn.close()
    
    # --- إحصائيات سريعة ---
    st.markdown(f"<div class='card arabic-ui'>{arabic_text('الإحصائيات')}</div>", 
               unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card arabic-ui">
            <h3>{len(df)}</h3>
            <p>{arabic_text('عدد المذكرات')}</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card arabic-ui">
            <h3>{df['section'].nunique()}</h3>
            <p>{arabic_text('عدد الأقسام')}</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card arabic-ui">
            <h3>{df['supervisor'].nunique()}</h3>
            <p>{arabic_text('عدد المشرفين')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # --- تصفية البيانات ---
    st.markdown(f"<div class='card arabic-ui'>{arabic_text('تصفية المذكرات')}</div>", 
               unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_section = st.selectbox(arabic_text("القسم"), ["الكل"] + sections)
    with col2:
        supervisors = ["الكل"] + sorted(df["supervisor"].unique().tolist())
        selected_supervisor = st.selectbox(arabic_text("المشرف"), supervisors)
    with col3:
        status_options = ["الكل", "pending", "approved", "rejected"]
        selected_status = st.selectbox(arabic_text("الحالة"), status_options)
    
    # تطبيق التصفية
    filtered_df = df.copy()
    if selected_section != "الكل":
        filtered_df = filtered_df[filtered_df["section"] == selected_section]
    if selected_supervisor != "الكل":
        filtered_df = filtered_df[filtered_df["supervisor"] == selected_supervisor]
    if selected_status != "الكل":
        filtered_df = filtered_df[filtered_df["status"] == selected_status]
    
    # --- عرض المذكرات ---
    st.markdown(f"<div class='card arabic-ui'>{arabic_text('المذكرات المقدمة')}</div>", 
               unsafe_allow_html=True)
    
    if filtered_df.empty:
        st.markdown(f"""
        <div class="info-msg arabic-ui">
            <p>{arabic_text('لا توجد مذكرات لعرضها حسب التصفية المحددة')}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for _, row in filtered_df.iterrows():
            with st.expander(f"{row['title']} - {row['status']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"<div class='arabic-ui'><strong>{arabic_text('الطالب')}:</strong> {row['first_name']} {row['last_name']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='arabic-ui'><strong>{arabic_text('رقم التسجيل')}:</strong> {row['reg_num']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='arabic-ui'><strong>{arabic_text('تاريخ الميلاد')}:</strong> {row['birth_date']}</div>", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"<div class='arabic-ui'><strong>{arabic_text('القسم')}:</strong> {row['section']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='arabic-ui'><strong>{arabic_text('المشرف')}:</strong> {row['supervisor']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='arabic-ui'><strong>{arabic_text('تاريخ الإيداع')}:</strong> {row['upload_date']}</div>", unsafe_allow_html=True)
                
                # حالة المذكرة (للمشرفين فقط)
                if st.session_state.role in ["مشرف", "مسؤول"]:
                    status = st.selectbox(
                        arabic_text("تغيير الحالة"),
                        ["pending", "approved", "rejected"],
                        index=["pending", "approved", "rejected"].index(row["status"]),
                        key=f"status_{row['id']}"
                    )
                    
                    if st.button(arabic_text("حفظ التغييرات"), key=f"save_{row['id']}"):
                        conn = sqlite3.connect('theses.db')
                        c = conn.cursor()
                        c.execute("UPDATE theses SET status = ? WHERE id = ?", (status, row["id"]))
                        conn.commit()
                        conn.close()
                        st.success(arabic_text("تم تحديث حالة المذكرة بنجاح"))
                        st.experimental_rerun()
                
                # زر التحميل
                file_path = os.path.join("uploaded_memos", row['section'], row['filename'])
                if os.path.exists(file_path):
                    st.download_button(
                        label=arabic_text("⬇️ تحميل المذكرة"),
                        data=open(file_path, "rb").read(),
                        file_name=row['filename'],
                        mime="application/pdf",
                        key=f"download_{row['id']}"
                    )
                else:
                    st.markdown(f"""
                    <div class="error-msg arabic-ui">
                        <p>{arabic_text('ملف المذكرة غير موجود!')}</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    # --- أدوات الإدارة للمسؤولين ---
    if st.session_state.role == "مسؤول":
        st.markdown(f"<div class='card arabic-ui'>{arabic_text('أدوات الإدارة')}</div>", 
                   unsafe_allow_html=True)
        
        try:
            if st.button(arabic_text("تصدير جميع البيانات إلى Excel")):
                excel_file = "theses_export.xlsx"
                try:
                    import openpyxl
                    df.to_excel(excel_file, index=False, engine='openpyxl')
                    
                    with open(excel_file, "rb") as f:
                        st.download_button(
                            label=arabic_text("⬇️ تحميل ملف Excel"),
                            data=f,
                            file_name="theses_export.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    os.remove(excel_file)
                except ImportError:
                    st.error(arabic_text("""
                    المكتبة المطلوبة غير مثبتة. الرجاء إضافة:
                    ```python
                    pip install openpyxl
                    ```
                    إلى متطلبات المشروع."""))
                except Exception as e:
                    st.error(arabic_text(f"حدث خطأ أثناء التصدير: {str(e)}"))
        except Exception as e:
            st.error(arabic_text(f"خطأ في أدوات الإدارة: {str(e)}"))
        
        if st.button(arabic_text("حذف جميع البيانات"), key="delete_all"):
            st.warning(arabic_text("هذا الإجراء سيحذف جميع البيانات بشكل دائم. تأكد قبل المتابعة."))
            if st.button(arabic_text("تأكيد الحذف"), key="confirm_delete"):
                conn = sqlite3.connect('theses.db')
                c = conn.cursor()
                c.execute("DELETE FROM theses")
                conn.commit()
                conn.close()
                st.success(arabic_text("تم حذف جميع البيانات بنجاح"))
                st.experimental_rerun()

    # --- تذييل الصفحة ---
    st.markdown(f"""
    <div class="arabic-ui" style="text-align: center; margin-top: 2rem; color: #666; font-size: 0.9rem;">
        <hr>
        <p>{arabic_text('منصة إيداع مذكرات التخرج - كلية علوم الطبيعة و الحياة وعلوم الأرض والكون © 2025')}</p>
        <p>{arabic_text('للإبلاغ عن مشاكل تقنية يرجى التواصل على: fsnv@univ-bba.dz')}</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()