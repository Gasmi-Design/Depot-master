import streamlit as st
import os
import re
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil
import sqlite3
import hashlib
import hmac
import secrets
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Optional, Tuple
import json

# ---------------------------------------
# تكوين الصفحة وCSS (عربي، RTL)
# ---------------------------------------
st.set_page_config(
    page_title="منصة إيداع مذكرات التخرج",
    layout="centered",
    page_icon="📚"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');

* {
    font-family: 'Cairo', sans-serif !important;
}

body, .main, .block-container, .stApp {
    direction: rtl !important;
    text-align: right !important;
    font-size: 20px !important;
    font-weight: bold !important;
    color: #003366 !important;
    background-color: #f8f9fa !important;
}

/* تصميم الإطار العام */
.main {
    background-color: #ffffff;
    padding: 2rem;
    border-radius: 15px;
    box-shadow: 0 8px 30px rgba(0, 51, 102, 0.1);
    max-width: 1200px;
    margin: 2rem auto;
    border: 1px solid #e0e0e0;
}

/* العناوين h1-h6 */
h1, h2, h3, h4, h5, h6 {
    color: #003366 !important;
    font-weight: 900 !important;
    margin-top: 1.5rem;
    margin-bottom: 1rem;
    text-align: right !important;
}

h1 {
    font-size: 2.8rem !important;
    text-align: center !important;
    background: linear-gradient(135deg, #003366, #4CAF50);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 1.5rem;
}

h2 {
    font-size: 2rem !important;
    border-right: 5px solid #4CAF50;
    padding-right: 15px;
}

h3 {
    font-size: 1.6rem !important;
    color: #2e7d32 !important;
}

h4 {
    font-size: 1.4rem !important;
    text-align: center !important;
    color: #555 !important;
}

/* الحقول */
.stTextInput input, .stSelectbox select, .stTextArea textarea, .stDateInput input {
    font-size: 1.1rem !important;
    font-weight: bold !important;
    color: #003366 !important;
    border: 2px solid #e0e0e0 !important;
    border-radius: 8px !important;
    padding: 10px 15px !important;
    transition: all 0.3s ease !important;
}

.stTextInput input:focus, .stSelectbox select:focus, .stTextArea textarea:focus {
    border-color: #4CAF50 !important;
    box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.2) !important;
}

/* الأزرار */
.stButton button {
    background: linear-gradient(135deg, #4CAF50, #2e7d32);
    color: white;
    padding: 12px 25px;
    font-size: 1.1rem;
    font-weight: bold;
    border-radius: 8px;
    border: none;
    margin-top: 1rem;
    transition: all 0.3s ease;
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
}

.stButton button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
}

.stButton button:active {
    transform: translateY(0);
}

/* أزرار خاصة */
.danger-button {
    background: linear-gradient(135deg, #f44336, #c62828) !important;
}

.warning-button {
    background: linear-gradient(135deg, #ff9800, #ef6c00) !important;
}

.info-button {
    background: linear-gradient(135deg, #2196F3, #1565c0) !important;
}

/* تسجيل الخروج */
.logout-btn {
    margin-top: 3rem;
    padding-top: 2rem;
    border-top: 2px solid #e0e0e0;
    text-align: center;
}

.logout-btn .stButton button {
    background: linear-gradient(135deg, #757575, #424242);
    max-width: 300px;
    margin: 0 auto;
}

/* بطاقات الإحصائيات */
.metric-box {
    background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    text-align: center;
    font-size: 1.1rem;
    font-weight: bold;
    color: #003366;
    border: 1px solid #a5d6a7;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    transition: transform 0.3s ease;
}

.metric-box:hover {
    transform: translateY(-5px);
}

.metric-box h3 {
    font-size: 2.5rem !important;
    margin: 10px 0;
    color: #2e7d32 !important;
}

/* الرسائل */
.success-msg {
    color: #2e7d32;
    background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
    padding: 1.2rem;
    border-radius: 8px;
    margin-bottom: 1.5rem;
    font-weight: bold;
    border-right: 5px solid #4CAF50;
}

.error-msg {
    color: #c62828;
    background: linear-gradient(135deg, #ffebee, #ffcdd2);
    padding: 1.2rem;
    border-radius: 8px;
    margin-bottom: 1.5rem;
    font-weight: bold;
    border-right: 5px solid #f44336;
}

.warning-msg {
    color: #ef6c00;
    background: linear-gradient(135deg, #fff3e0, #ffe0b2);
    padding: 1.2rem;
    border-radius: 8px;
    margin-bottom: 1.5rem;
    font-weight: bold;
    border-right: 5px solid #ff9800;
}

.info-msg {
    color: #1565c0;
    background: linear-gradient(135deg, #e3f2fd, #bbdefb);
    padding: 1.2rem;
    border-radius: 8px;
    margin-bottom: 1.5rem;
    font-weight: bold;
    border-right: 5px solid #2196F3;
}

/* رؤوس expander */
.stExpanderHeader {
    font-size: 1.2rem !important;
    font-weight: bold !important;
    color: #003366 !important;
    background-color: #f5f5f5 !important;
    border-radius: 8px !important;
    padding: 15px !important;
}

/* التبويبات */
.stTabs [data-baseweb="tab-list"] {
    gap: 2px;
    background-color: #f0f0f0;
    padding: 5px;
    border-radius: 10px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 12px 24px;
    font-weight: bold;
}

.stTabs [aria-selected="true"] {
    background-color: #4CAF50 !important;
    color: white !important;
}

/* الجداول */
.dataframe {
    width: 100%;
    border-collapse: collapse;
    margin: 1rem 0;
}

.dataframe th {
    background-color: #4CAF50;
    color: white;
    padding: 12px;
    text-align: right;
}

.dataframe td {
    padding: 10px;
    border-bottom: 1px solid #e0e0e0;
}

.dataframe tr:hover {
    background-color: #f5f5f5;
}

/* تخصيص الـ uploader */
.stFileUploader {
    border: 2px dashed #4CAF50;
    border-radius: 10px;
    padding: 20px;
    text-align: center;
    background-color: #f8fff8;
}

/* تحسين الـ selectbox */
.stSelectbox > div > div {
    border-radius: 8px !important;
    border: 2px solid #e0e0e0 !important;
}

/* التقدم */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #4CAF50, #2e7d32);
}

/* الإشعارات */
.notification {
    background: linear-gradient(135deg, #e3f2fd, #bbdefb);
    padding: 15px;
    border-radius: 8px;
    margin: 10px 0;
    border-right: 4px solid #2196F3;
}

.notification.unread {
    background: linear-gradient(135deg, #fff3e0, #ffe0b2);
    border-right-color: #ff9800;
}

/* البحث */
.search-box {
    background: #f8f9fa;
    padding: 20px;
    border-radius: 10px;
    margin: 20px 0;
    border: 1px solid #e0e0e0;
}

/* الكروت */
.card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    margin: 15px 0;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    border: 1px solid #e0e0e0;
    transition: all 0.3s ease;
}

.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

/* الأيقونات */
.icon {
    font-size: 1.5rem;
    margin-left: 10px;
}

/* الـ footer */
.footer {
    text-align: center;
    margin-top: 3rem;
    padding-top: 2rem;
    border-top: 1px solid #e0e0e0;
    color: #666;
    font-size: 0.9rem;
}

/* التنبيهات */
.alert {
    padding: 15px;
    border-radius: 8px;
    margin: 15px 0;
    animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* الأقسام */
.section {
    background: #f8f9fa;
    padding: 20px;
    border-radius: 10px;
    margin: 20px 0;
    border: 1px solid #e0e0e0;
}

/* الألوان */
.primary-color { color: #003366 !important; }
.secondary-color { color: #4CAF50 !important; }
.accent-color { color: #ff9800 !important; }
.text-muted { color: #666 !important; }

/* المسافات */
.mt-1 { margin-top: 0.5rem !important; }
.mt-2 { margin-top: 1rem !important; }
.mt-3 { margin-top: 1.5rem !important; }
.mt-4 { margin-top: 2rem !important; }
.mt-5 { margin-top: 3rem !important; }

.mb-1 { margin-bottom: 0.5rem !important; }
.mb-2 { margin-bottom: 1rem !important; }
.mb-3 { margin-bottom: 1.5rem !important; }
.mb-4 { margin-bottom: 2rem !important; }
.mb-5 { margin-bottom: 3rem !important; }

.p-1 { padding: 0.5rem !important; }
.p-2 { padding: 1rem !important; }
.p-3 { padding: 1.5rem !important; }
.p-4 { padding: 2rem !important; }
.p-5 { padding: 3rem !important; }

/* responsive */
@media (max-width: 768px) {
    .main {
        padding: 1rem;
        margin: 1rem;
    }
    
    h1 {
        font-size: 2rem !important;
    }
    
    h2 {
        font-size: 1.5rem !important;
    }
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------
# تهيئة القيم الثابتة
# ---------------------------------------
SECTIONS = ["العلوم البيولوجية", "العلوم الفلاحية", "علوم التغذية", "علم البيئة والمحيط"]
PASSWORDS = {
    "مشرف": {
        "salima.belloula": "Qr8$kL2pT9wA",
        "imane.kerbouai": "Nf4@vR7xZ1qS",
        "meriem.nasri": "Sb7%pM3kH8uY",
        "mokhtar.guissous": "Vt6#bC9rQ2eW",
        "farida.belkasmi": "Lp3$gT8nS5yZ",
        "amel.bourahla": "Yz9@hF2mV6kP",
        "nacira.chourghal": "Hx2#rQ7tB4nM",
        "zine_el_abidine.fellahi": "Rm5%kL1wV8sD",
        "hasna.boulkroune": "Ct4$gN9pR2zF",
        "dahbia.tabti": "Pw8#dM6sK1yQ",
        "amira.saiad": "Uz3%vB7nL5cH",
        "sihem.kermiche": "Kb9@tF2rQ6wX",
        "mohamed_djalil.zaafour": "Md6#pS8vR3yL",
        "radia.mebarki": "Rf2$kH7nT9wG",
        "mouloud.ait_mechedal": "Qy7%vB3mL8sA",
        "asma.meziti": "Jp4#rK9tV2hZ",
        "mahieddine.sebbane": "Nt8$gM1pQ6wS",
        "amel.hamma": "Lb3%vF7kR9zX",
        "mounir.saifi": "Vz5#pT2nL8qH",
        "nadjat.iratni": "Gy9$kR4mS1wP",
        "lounis.semara": "Hp2%vB8tQ6nM",
        "faycal.bahlouli": "Kw7#rM3pV9sD",
        "imene.bakhouche": "Sa4$gT8nL1yF",
        "ammar.deffaf": "Pd6%kH2rQ7wN",
        "souad.boumaiza": "Rx3#vM9pT5zL",
        "abdelouahab.bentabet": "Vz1$kP7nL4qS",
        "hichem.mezdour": "Mb8%rT3vK9yH",
        "hadjira.benseghir": "Qf2#pL6nS7wZ",
        "nawel.benbouguerra": "Lc9$gM1rV8tP",
        "sofiane.bechami": "Hz4%vK7pN2qM",
        "anissa.mahleb": "Yp6#rT3mL8wS",
        "yasmina.souagui": "Nx9$kB2pV7rD",
        "abdelaziz.ziad": "Gt3%vM8nL1qP",
        "bachir.loukil": "Rb7#pK4tS9wZ",
        "fatiha.tekkouk": "Pd2%gM6nL8yH",
        "amel.ferahtia": "Qm8%rT1pV3sK",
        "lynda.loucif": "Sx4#kB9vM2qL",
        "noureddine.touati": "Hz7$pR3mT6wN",
        "soraya.hihat": "Ly1%vK8nP4qS",
        "soulef.boussahel": "Vb9#rM2tK7wD",
        "salima.tabti": "Pw3$kL8nV6yR",
        "mohamed.bibak": "Ng5%vT1pR9sZ",
        "asma.bouguerra": "Fc2#pK7mL8wY",
        "abdellali.lazazga": "Qz6$gR3nT1vM",
        "hamida.benradia": "Rt9%kL4pS2wH",
        "abdelouahab.diafat": "Mb3#vT8nK7qP",
        "khelifa.maamri": "Ld1$gP6nR9wS",
        "mounira.dehiri": "Sh8%rK2vM4qZ",
        "mohamed.tiaiba": "Py5#kT9nL3wV",
        "hassina.guergour": "Nq2%vR7pK8sM",
        "amel.salamani": "Kb9#pL1vT6wD",
        "tahar.sedrati": "Vz4$gM8nP3qS",
        "nouari.sadrati": "Fy7%rK2pL9wH",
        "abdelmalek.khoudour": "Qd3#vT6nR8yP",
        "hizia.kelaleche": "Rm1%kP7nL4wS",
        "dahmane.alili": "Tb8#vK2rM5qZ",
        "chelbia.regoui": "Lc6$gR3pT9wN",
        "nor_el_houda.belalmi": "Sa2%vK8nP7qM",
        "tahar.boubellouta": "Hz9#pL4mT1wD",
        "wissem.boutana": "Qp3%kR7nV8yS",
        "sihem.ziouche": "Mb6#vT1pL9qZ",
        "hanane.abed": "Rx8$gK2nP4wM",
        "widad.fatmi": "Ly5%rM9pT1qS",
        "youcef.merzouki": "Nz7#kV3pL6wD",
        "mohamed_tayeb.belhadj": "Gq2%vR8nM4pS",
        "tahar.sayah": "Pf9#kT1vL6wZ",
        "nadia.rouaiguia": "Sd3%gM7pK2qH",
        "bilal.fortas": "Qw6#rL9nT1yP",
        "raouf.amara_korba": "Vz1%pK8mR4wS",
        "sabah.boumerfeg": "Lk7#vT2pN9qD",
        "takiyeddine.bensouilah": "My4%gR8nL1pS",
        "belkacem_aymen.boulaouad": "Np9#kT3vL6wZ",
        "milouda.tamine": "Rb2%vM7pK8qS",
        "ouissem.moumeni": "Hx5#rL1nT9wD",
        "amina.zerroug": "Qn8%kP3vM6yS",
        "khalissa.benbouguerra": "Sz4#gR9nL1pD",
        "chawki_abdallah.bouzid": "Vb7%kT2pM8wQ",
        "hemza.belguerri": "Lf3#vR6nK9pS",
        "hadjer.laoufi": "Py1%gM8nL4qZ",
        "nadia_safia.chenouf": "Mw9#rT3pK6wD",
        "abdelghani.derardja": "Hz2%kL7nV5qS",
        "toufik.harizi": "Rb8#pM1vK4wZ",
        "dahou.moutassem": "Qs3%vT9nL6pH",
        "abdelmaalek.meribai": "Lp5#gR2kT8wS",
        "sofiane.bensefia": "Vz6%pM1nL9qD",
        "chafik_redha.messai": "Ny4#kT7vR2wS",
        "naima.baaziz": "Gh9%rL3pK6wD",
        "zohra.benouadah": "Px2#vM8nL4qS",
        "juba.bellik": "Rf7%kT1pM9wZ",
        "hamoudi.mekhalfi": "Sd3#vR6nL8qP",
        "nassim.sid": "Qk8%pL2vM5wH"
    }
}

# ---------------------------------------
# دوال التشفير والأمان
# ---------------------------------------
PBKDF2_ITERATIONS = 200_000
SALT_BYTES = 16

def hash_password(password: str) -> Tuple[str, str]:
    """توليد salt وهاش مستمد عبر PBKDF2-HMAC-SHA256"""
    salt = secrets.token_bytes(SALT_BYTES)
    hash_bytes = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return salt.hex(), hash_bytes.hex()

def verify_password(password: str, salt_hex: str, hash_hex: str) -> bool:
    """التحقق من صحة كلمة المرور"""
    salt = bytes.fromhex(salt_hex)
    expected = bytes.fromhex(hash_hex)
    calc = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return hmac.compare_digest(calc, expected)

# ---------------------------------------
# إعداد قاعدة البيانات
# ---------------------------------------
BASE_DIR = Path.cwd()
DB_FILE = BASE_DIR / "app.db"
UPLOAD_DIR = BASE_DIR / "uploaded_memos"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR = BASE_DIR / "backups"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

def get_db_conn():
    """إنشاء اتصال بقاعدة البيانات"""
    conn = sqlite3.connect(str(DB_FILE), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """تهيئة قاعدة البيانات"""
    conn = get_db_conn()
    cur = conn.cursor()
    
    # جدول المستخدمين
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        role TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        created_by TEXT,
        created_at TEXT,
        last_login TEXT
    )
    """)
    
    # جدول المذكرات
    cur.execute("""
    CREATE TABLE IF NOT EXISTS memos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reg_num TEXT,
        first_name TEXT,
        last_name TEXT,
        birth_date TEXT,
        section TEXT,
        supervisor TEXT,
        title TEXT,
        file_name TEXT,
        file_path TEXT,
        submitted_by TEXT,
        created_at TEXT,
        updated_at TEXT,
        status TEXT DEFAULT 'معلقة'
    )
    """)
    
    # جدول الإشعارات
    cur.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recipient TEXT,
        message TEXT,
        is_read BOOLEAN DEFAULT 0,
        created_at TEXT
    )
    """)
    
    # جدول السجلات
    cur.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        action TEXT,
        details TEXT,
        ip_address TEXT,
        created_at TEXT
    )
    """)
    
    conn.commit()
    
    # إدراج مشرفي البداية
    if "مشرف" in PASSWORDS:
        for uname, pwd in PASSWORDS["مشرف"].items():
            if not get_user(uname):
                salt, hsh = hash_password(pwd)
                try:
                    cur.execute(
                        "INSERT INTO users (username, role, password_hash, salt, created_by, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                        (uname, "مشرف", hsh, salt, "system", datetime.utcnow().isoformat())
                    )
                except sqlite3.IntegrityError:
                    pass
    
    # إنشاء فهارس للأداء
    cur.execute("CREATE INDEX IF NOT EXISTS idx_memos_section ON memos(section)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_memos_supervisor ON memos(supervisor)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_memos_created_at ON memos(created_at)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_notifications_recipient ON notifications(recipient)")
    
    conn.commit()
    conn.close()
    
    # تحسين قاعدة البيانات
    optimize_database()

def optimize_database():
    """تحسين أداء قاعدة البيانات"""
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("VACUUM")
    conn.commit()
    conn.close()
    return "تم تحسين قاعدة البيانات بنجاح"

# ---------------------------------------
# دوال إدارة المستخدمين
# ---------------------------------------
def get_user(username: str):
    """الحصول على بيانات مستخدم"""
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    return row

def create_user(username: str, password: str, role: str, created_by: str = None):
    """إنشاء مستخدم جديد"""
    if get_user(username):
        raise ValueError("اسم المستخدم موجود بالفعل")
    salt, hsh = hash_password(password)
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (username, role, password_hash, salt, created_by, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (username, role, hsh, salt, created_by, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    log_action(created_by or "system", "create_user", f"إنشاء مستخدم جديد: {username} ({role})")

def update_user_password(username: str, new_password: str):
    """تحديث كلمة مرور المستخدم"""
    if not get_user(username):
        raise ValueError("المستخدم غير موجود")
    salt, hsh = hash_password(new_password)
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("UPDATE users SET password_hash = ?, salt = ? WHERE username = ?", (hsh, salt, username))
    conn.commit()
    conn.close()
    log_action("system", "update_password", f"تحديث كلمة مرور المستخدم: {username}")

def update_last_login(username: str):
    """تحديث وقت آخر دخول"""
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("UPDATE users SET last_login = ? WHERE username = ?", 
                (datetime.utcnow().isoformat(), username))
    conn.commit()
    conn.close()

# ---------------------------------------
# دوال إدارة المذكرات
# ---------------------------------------
def save_memo_db(record: dict):
    """حفظ مذكرة في قاعدة البيانات"""
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO memos (reg_num, first_name, last_name, birth_date, section, supervisor, 
                       title, file_name, file_path, submitted_by, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        record.get("رقم التسجيل"),
        record.get("الاسم"),
        record.get("اللقب"),
        record.get("تاريخ الميلاد"),
        record.get("القسم"),
        record.get("المشرف"),
        record.get("عنوان المذكرة"),
        record.get("اسم الملف"),
        record.get("مسار الملف"),
        record.get("مقدم"),
        record.get("تاريخ الإيداع"),
        record.get("تاريخ الإيداع")
    ))
    memo_id = cur.lastrowid
    conn.commit()
    conn.close()
    
    # إرسال إشعار للمشرف
    send_notification(record.get("المشرف"), "new_memo", 
                     f"تم إيداع مذكرة جديدة: {record.get('عنوان المذكرة')}")
    
    log_action(record.get("مقدم"), "submit_memo", 
               f"إيداع مذكرة جديدة: {record.get('عنوان المذكرة')}")
    
    return memo_id

def load_memos(section: str = None, supervisor: str = None, status: str = None):
    """تحميل المذكرات مع إمكانية التصفية"""
    conn = get_db_conn()
    cur = conn.cursor()
    q = "SELECT * FROM memos"
    params = []
    filters = []
    
    if section and section != "الكل":
        filters.append("section = ?")
        params.append(section)
    if supervisor and supervisor != "الكل":
        filters.append("supervisor = ?")
        params.append(supervisor)
    if status and status != "الكل":
        filters.append("status = ?")
        params.append(status)
    
    if filters:
        q += " WHERE " + " AND ".join(filters)
    q += " ORDER BY created_at DESC"
    
    cur.execute(q, params)
    rows = cur.fetchall()
    conn.close()
    return rows

def get_memos_by_user(username: str):
    """الحصول على مذكرات مستخدم معين"""
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM memos WHERE submitted_by = ? ORDER BY created_at DESC", (username,))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_memo_by_id(memo_id: int):
    """الحصول على مذكرة بواسطة المعرف"""
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM memos WHERE id = ?", (memo_id,))
    row = cur.fetchone()
    conn.close()
    return row

def update_memo_db(memo_id: int, updated: dict):
    """تحديث بيانات مذكرة"""
    conn = get_db_conn()
    cur = conn.cursor()
    
    cols = []
    params = []
    mapping = {
        "reg_num": "reg_num",
        "first_name": "first_name",
        "last_name": "last_name",
        "birth_date": "birth_date",
        "section": "section",
        "supervisor": "supervisor",
        "title": "title",
        "file_name": "file_name",
        "file_path": "file_path",
        "status": "status"
    }
    
    for k, col in mapping.items():
        if k in updated:
            cols.append(f"{col} = ?")
            params.append(updated[k])
    
    if cols:
        cols.append("updated_at = ?")
        params.append(datetime.utcnow().isoformat())
        params.append(memo_id)
        q = f"UPDATE memos SET {', '.join(cols)} WHERE id = ?"
        cur.execute(q, params)
        conn.commit()
        
        # تسجيل التعديل
        memo = get_memo_by_id(memo_id)
        if memo:
            log_action(updated.get("updated_by", "unknown"), "update_memo",
                      f"تعديل المذكرة #{memo_id}: {memo['title']}")
    
    conn.close()

def delete_memo_db(memo_id: int, deleted_by: str):
    """حذف مذكرة"""
    m = get_memo_by_id(memo_id)
    if m:
        # نسخ احتياطي للملف
        backup_memo_file(m["file_path"])
        
        # حذف الملف
        if m["file_path"] and os.path.exists(m["file_path"]):
            try:
                os.remove(m["file_path"])
            except Exception:
                pass
        
        # حذف السجل
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM memos WHERE id = ?", (memo_id,))
        conn.commit()
        conn.close()
        
        # تسجيل الحذف
        log_action(deleted_by, "delete_memo", f"حذف المذكرة #{memo_id}: {m['title']}")
        
        return True
    return False

def update_memo_status(memo_id: int, status: str, updated_by: str):
    """تحديث حالة المذكرة"""
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("UPDATE memos SET status = ?, updated_at = ? WHERE id = ?",
                (status, datetime.utcnow().isoformat(), memo_id))
    conn.commit()
    conn.close()
    
    memo = get_memo_by_id(memo_id)
    if memo:
        # إرسال إشعار للطالب
        send_notification(memo["submitted_by"], "memo_status_changed",
                         f"تم تغيير حالة مذكرتك '{memo['title']}' إلى: {status}")
        
        log_action(updated_by, "update_status",
                  f"تغيير حالة المذكرة #{memo_id} إلى: {status}")

# ---------------------------------------
# دوال الإشعارات
# ---------------------------------------
def send_notification(recipient: str, notification_type: str, message: str = None):
    """إرسال إشعار لمستخدم"""
    notifications = {
        "new_memo": "تم إيداع مذكرة جديدة تحت إشرافك",
        "memo_updated": "تم تحديث مذكرتك",
        "memo_status_changed": "تم تغيير حالة مذكرتك",
        "password_changed": "تم تغيير كلمة المرور الخاصة بك",
        "account_created": "تم إنشاء حساب جديد لك",
        "welcome": "مرحباً بك في منصة إيداع مذكرات التخرج"
    }
    
    if not message:
        message = notifications.get(notification_type, "إشعار جديد")
    
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO notifications (recipient, message, created_at) VALUES (?, ?, ?)",
                (recipient, message, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def get_user_notifications(username: str, unread_only: bool = False):
    """الحصول على إشعارات المستخدم"""
    conn = get_db_conn()
    cur = conn.cursor()
    
    if unread_only:
        cur.execute("SELECT * FROM notifications WHERE recipient = ? AND is_read = 0 ORDER BY created_at DESC", 
                   (username,))
    else:
        cur.execute("SELECT * FROM notifications WHERE recipient = ? ORDER BY created_at DESC", 
                   (username,))
    
    rows = cur.fetchall()
    conn.close()
    return rows

def mark_notification_as_read(notification_id: int):
    """تحديد الإشعار كمقروء"""
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("UPDATE notifications SET is_read = 1 WHERE id = ?", (notification_id,))
    conn.commit()
    conn.close()

def mark_all_notifications_as_read(username: str):
    """تحديد جميع إشعارات المستخدم كمقروءة"""
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("UPDATE notifications SET is_read = 1 WHERE recipient = ?", (username,))
    conn.commit()
    conn.close()

# ---------------------------------------
# دوال السجلات
# ---------------------------------------
def log_action(user: str, action: str, details: str, ip_address: str = "local"):
    """تسجيل نشاط في السجلات"""
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO logs (user, action, details, ip_address, created_at) VALUES (?, ?, ?, ?, ?)",
                (user, action, details, ip_address, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def get_recent_logs(limit: int = 50):
    """الحصول على السجلات الحديثة"""
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM logs ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows

# ---------------------------------------
# دوال النسخ الاحتياطي
# ---------------------------------------
def backup_memo_file(file_path: str):
    """إنشاء نسخة احتياطية من ملف المذكرة"""
    try:
        if os.path.exists(file_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = Path(file_path).name
            backup_filename = f"{Path(file_path).stem}_{timestamp}{Path(file_path).suffix}"
            backup_path = BACKUP_DIR / backup_filename
            shutil.copy2(file_path, backup_path)
            return backup_path
    except Exception as e:
        log_action("system", "backup_failed", f"فشل النسخ الاحتياطي: {str(e)}")
    return None

def create_database_backup():
    """إنشاء نسخة احتياطية من قاعدة البيانات"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"app_backup_{timestamp}.db"
    try:
        shutil.copy2(DB_FILE, backup_file)
        log_action("system", "db_backup", "تم إنشاء نسخة احتياطية من قاعدة البيانات")
        return backup_file
    except Exception as e:
        log_action("system", "db_backup_failed", f"فشل نسخ قاعدة البيانات: {str(e)}")
        return None

# ---------------------------------------
# دوال التقارير والإحصائيات
# ---------------------------------------
def generate_statistics_report():
    """إنشاء تقرير إحصائي مفصل"""
    conn = get_db_conn()
    cur = conn.cursor()
    
    # إحصائيات عامة
    cur.execute("SELECT COUNT(*) as total FROM memos")
    total_memos = cur.fetchone()['total']
    
    cur.execute("SELECT COUNT(DISTINCT section) as sections FROM memos")
    sections_count = cur.fetchone()['sections']
    
    cur.execute("SELECT COUNT(DISTINCT supervisor) as supervisors FROM memos")
    supervisors_count = cur.fetchone()['supervisors']
    
    cur.execute("SELECT COUNT(DISTINCT submitted_by) as students FROM memos")
    students_count = cur.fetchone()['students']
    
    # توزيع المذكرات حسب الشهر
    cur.execute("""
        SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as count
        FROM memos
        GROUP BY month
        ORDER BY month DESC
        LIMIT 6
    """)
    monthly_dist = cur.fetchall()
    
    # أكثر المشرفين نشاطاً
    cur.execute("""
        SELECT supervisor, COUNT(*) as memo_count
        FROM memos
        GROUP BY supervisor
        ORDER BY memo_count DESC
        LIMIT 10
    """)
    top_supervisors = cur.fetchall()
    
    # توزيع المذكرات حسب القسم
    cur.execute("""
        SELECT section, COUNT(*) as count
        FROM memos
        GROUP BY section
        ORDER BY count DESC
    """)
    section_dist = cur.fetchall()
    
    # توزيع المذكرات حسب الحالة
    cur.execute("""
        SELECT status, COUNT(*) as count
        FROM memos
        GROUP BY status
    """)
    status_dist = cur.fetchall()
    
    conn.close()
    
    return {
        "total_memos": total_memos,
        "sections_count": sections_count,
        "supervisors_count": supervisors_count,
        "students_count": students_count,
        "monthly_distribution": monthly_dist,
        "top_supervisors": top_supervisors,
        "section_distribution": section_dist,
        "status_distribution": status_dist
    }

def display_statistics_dashboard():
    """عرض لوحة الإحصائيات"""
    stats = generate_statistics_report()
    
    # بطاقات الإحصائيات
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'''
        <div class="metric-box">
            <h3>{stats["total_memos"]}</h3>
            <div>المذكرات المودعة</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
        <div class="metric-box">
            <h3>{stats["sections_count"]}</h3>
            <div>عدد الأقسام</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'''
        <div class="metric-box">
            <h3>{stats["supervisors_count"]}</h3>
            <div>عدد المشرفين</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        st.markdown(f'''
        <div class="metric-box">
            <h3>{stats["students_count"]}</h3>
            <div>عدد الطلاب</div>
        </div>
        ''', unsafe_allow_html=True)
    
    # مخططات
    if stats["section_distribution"]:
        st.subheader("📊 توزيع المذكرات حسب القسم")
        sections = [row['section'] for row in stats["section_distribution"]]
        counts = [row['count'] for row in stats["section_distribution"]]
        
        fig = go.Figure(data=[
            go.Bar(x=counts, y=sections, orientation='h', marker_color='#4CAF50')
        ])
        fig.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=30, b=10),
            yaxis_title="القسم",
            xaxis_title="عدد المذكرات"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    if stats["monthly_distribution"]:
        st.subheader("📈 توزيع المذكرات خلال الأشهر الماضية")
        months = [row['month'] for row in stats["monthly_distribution"]]
        counts = [row['count'] for row in stats["monthly_distribution"]]
        
        fig2 = go.Figure(data=[
            go.Scatter(x=months, y=counts, mode='lines+markers', 
                      line=dict(color='#2196F3', width=3),
                      marker=dict(size=8, color='#2196F3'))
        ])
        fig2.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=30, b=10),
            xaxis_title="الشهر",
            yaxis_title="عدد المذكرات"
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    if stats["top_supervisors"]:
        st.subheader("🏆 أكثر المشرفين نشاطاً")
        supervisors = [row['supervisor'] for row in stats["top_supervisors"]]
        counts = [row['memo_count'] for row in stats["top_supervisors"]]
        
        df = pd.DataFrame({
            "المشرف": supervisors,
            "عدد المذكرات": counts
        })
        st.dataframe(df, use_container_width=True)

# ---------------------------------------
# دوال البحث المتقدم
# ---------------------------------------
def advanced_search(keyword: str = "", search_type: str = "all", 
                   section: str = "", supervisor: str = "", 
                   start_date: str = "", end_date: str = ""):
    """بحث متقدم في المذكرات"""
    conn = get_db_conn()
    cur = conn.cursor()
    
    query = "SELECT * FROM memos WHERE 1=1"
    params = []
    
    if keyword:
        search_query = f"%{keyword}%"
        if search_type == "title":
            query += " AND (title LIKE ? OR first_name LIKE ? OR last_name LIKE ?)"
            params.extend([search_query, search_query, search_query])
        elif search_type == "reg_num":
            query += " AND reg_num LIKE ?"
            params.append(search_query)
        elif search_type == "supervisor":
            query += " AND supervisor LIKE ?"
            params.append(search_query)
        elif search_type == "student":
            query += " AND (first_name LIKE ? OR last_name LIKE ? OR submitted_by LIKE ?)"
            params.extend([search_query, search_query, search_query])
        else:  # search all
            query += " AND (title LIKE ? OR first_name LIKE ? OR last_name LIKE ? OR supervisor LIKE ? OR reg_num LIKE ? OR section LIKE ?)"
            params.extend([search_query, search_query, search_query, search_query, search_query, search_query])
    
    if section and section != "الكل":
        query += " AND section = ?"
        params.append(section)
    
    if supervisor and supervisor != "الكل":
        query += " AND supervisor = ?"
        params.append(supervisor)
    
    if start_date:
        query += " AND DATE(created_at) >= ?"
        params.append(start_date)
    
    if end_date:
        query += " AND DATE(created_at) <= ?"
        params.append(end_date)
    
    query += " ORDER BY created_at DESC"
    
    cur.execute(query, params)
    results = cur.fetchall()
    conn.close()
    
    return results

# ---------------------------------------
# دوال التحقق من الصحة
# ---------------------------------------
def validate_student_data(data: dict) -> Tuple[bool, str]:
    """التحقق من صحة بيانات الطالب"""
    errors = []
    
    # رقم التسجيل
    if not re.match(r'^[A-Za-z0-9]{6,20}$', data.get('reg_num', '')):
        errors.append("رقم التسجيل يجب أن يكون بين 6 و20 حرف/رقم (أحرف إنجليزية وأرقام فقط)")
    
    # الاسم واللقب
    if not re.match(r'^[\u0600-\u06FF\s]{2,30}$', data.get('first_name', '')):
        errors.append("الاسم يجب أن يحتوي على أحرف عربية فقط (2-30 حرف)")
    
    if not re.match(r'^[\u0600-\u06FF\s]{2,30}$', data.get('last_name', '')):
        errors.append("اللقب يجب أن يحتوي على أحرف عربية فقط (2-30 حرف)")
    
    # تاريخ الميلاد
    if 'birth_date' in data:
        try:
            if isinstance(data['birth_date'], str):
                birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d')
            else:
                birth_date = data['birth_date']
            
            age = datetime.now().year - birth_date.year
            if age < 17 or age > 50:
                errors.append("العمر يجب أن يكون بين 17 و50 سنة")
        except:
            errors.append("تاريخ الميلاد غير صالح")
    
    # عنوان المذكرة
    title = data.get('title', '')
    if len(title) < 10 or len(title) > 200:
        errors.append("عنوان المذكرة يجب أن يكون بين 10 و200 حرف")
    
    return len(errors) == 0, "، ".join(errors)

# ---------------------------------------
# دوال مساعدة
# ---------------------------------------
def safe_filename(name: str) -> str:
    """توليد اسم ملف آمن"""
    name = os.path.basename(name)
    parts = name.rsplit(".", 1)
    if len(parts) == 2:
        base, ext = parts
        ext = "." + ext
    else:
        base = parts[0]
        ext = ""
    base = re.sub(r"[^\w\s\-\.]", "", base)
    base = re.sub(r"\s+", "_", base)
    return base[:200] + ext

def format_datetime(dt: datetime) -> str:
    """تنسيق التاريخ والوقت"""
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def get_supervisor_permissions(username: str) -> Dict:
    """الحصول على صلاحيات المشرف"""
    # يمكن تطوير هذا ليتم تخزينه في قاعدة البيانات
    permissions = {
        "view_all": True,
        "create_students": True,
        "reset_passwords": True,
        "delete_memos": username in ["admin", "superadmin"],
        "manage_supervisors": username in ["admin", "superadmin"],
        "view_logs": username in ["admin", "superadmin"],
        "backup_restore": username in ["admin", "superadmin"]
    }
    return permissions

def check_session_timeout() -> bool:
    """التحقق من انتهاء مدة الجلسة"""
    if 'last_activity' in st.session_state:
        try:
            last_activity = datetime.fromisoformat(st.session_state.last_activity)
            timeout_minutes = 120  # 120 دقيقة
            
            if (datetime.now() - last_activity).total_seconds() > timeout_minutes * 60:
                reset_session()
                st.warning("انتهت مدة الجلسة، يرجى تسجيل الدخول مرة أخرى")
                return False
        except:
            pass
    
    # تحديث وقت النشاط
    st.session_state.last_activity = datetime.now().isoformat()
    return True

# ---------------------------------------
# إدارة جلسة Streamlit
# ---------------------------------------
def reset_session():
    """مسح جلسة المستخدم"""
    app_keys = [
        "login_role", "login_username", "login_password",
        "first_name", "last_name", "reg_num", "birth_date",
        "section", "supervisor", "title", "file",
        "new_username", "new_password", "gen", "sel_student", "new_pwd", "gen2", "editing_memo_id",
        "e_first_name", "e_last_name", "e_reg_num", "e_birth_date", "e_section", "e_supervisor", "e_title", "e_file",
        "search_keyword", "search_type", "search_section", "search_supervisor", "search_start_date", "search_end_date"
    ]
    
    for k in app_keys:
        st.session_state.pop(k, None)
    
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None
    st.session_state.permissions = {}

# تهيئة متغيرات الجلسة
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None
    st.session_state.permissions = {}
    st.session_state.last_activity = datetime.now().isoformat()

# تهيئة قاعدة البيانات
init_db()

# ---------------------------------------
# الواجهة الرئيسية
# ---------------------------------------
with st.container():
    st.markdown('<div class="main">', unsafe_allow_html=True)
    
    # الرأس
    st.markdown("<h1>📚 منصة إيداع مذكرات التخرج</h1>", unsafe_allow_html=True)
    st.markdown("<h4>جامعة محمد البشير الإبراهيمي - برج بوعريريج<br>كلية علوم الطبيعة والحياة وعلوم الأرض والكون</h4>", unsafe_allow_html=True)
    st.markdown("---")
    
    # التحقق من انتهاء الجلسة
    if st.session_state.logged_in and not check_session_timeout():
        st.stop()
    
    if not st.session_state.logged_in:
        # صفحة تسجيل الدخول
        st.subheader("🔐 تسجيل الدخول")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            role = st.selectbox("👤 اختر نوع الدخول:", ["طالب", "مشرف"], key="login_role")
        
        with col2:
            with st.form("login_form"):
                username = st.text_input("👤 اسم المستخدم", key="login_username")
                password = st.text_input("🔐 كلمة المرور:", type="password", key="login_password")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    submitted = st.form_submit_button("تسجيل الدخول", use_container_width=True)
                with col_b:
                    if st.form_submit_button("🔁 إعادة تعيين", use_container_width=True):
                        reset_session()
                
                if submitted:
                    user = get_user(username)
                    if user and user["role"] == role:
                        if verify_password(password, user["salt"], user["password_hash"]):
                            # تحديث آخر دخول
                            update_last_login(username)
                            
                            # إرسال إشعار ترحيب
                            send_notification(username, "welcome", f"مرحباً بك {username}")
                            
                            # تهيئة الجلسة
                            reset_session()  # مسح الحقول القديمة أولاً
                            st.session_state.logged_in = True
                            st.session_state.role = role
                            st.session_state.username = username
                            st.session_state.last_activity = datetime.now().isoformat()
                            
                            # تعيين الصلاحيات
                            if role == "مشرف":
                                st.session_state.permissions = get_supervisor_permissions(username)
                            
                            st.success(f"✅ تم تسجيل الدخول بنجاح. مرحباً بك {username}!")
                            st.experimental_rerun()
                        else:
                            st.error("⚠️ اسم المستخدم أو كلمة السر غير صحيحة")
                            log_action(username, "failed_login", "محاولة دخول فاشلة")
                    else:
                        st.error("⚠️ اسم المستخدم غير موجود أو الدور غير صحيح")
    
    else:
        # بعد تسجيل الدخول
        # عرض الإشعارات غير المقروءة
        notifications = get_user_notifications(st.session_state.username, unread_only=True)
        if notifications:
            with st.expander(f"🔔 إشعارات جديدة ({len(notifications)})", expanded=True):
                for note in notifications:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"**{note['message']}**")
                        st.caption(f"📅 {note['created_at']}")
                    with col2:
                        if st.button("✓", key=f"read_{note['id']}"):
                            mark_notification_as_read(note['id'])
                            st.experimental_rerun()
                if st.button("تحديد الكل كمقروء"):
                    mark_all_notifications_as_read(st.session_state.username)
                    st.experimental_rerun()
        
        if st.session_state.role == "طالب":
            # واجهة الطالب
            st.success(f"🎓 مرحباً بك {st.session_state.username} (طالب)")
            
            # أولاً: عرض المذكرات المودعة
            user_memos = get_memos_by_user(st.session_state.username)
            
            if user_memos:
                st.subheader("📂 مذكراتك المودعة")
                
                for m in user_memos:
                    with st.expander(f"📄 {m['title']} — {m['first_name']} {m['last_name']} (#{m['id']})", expanded=False):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**رقم التسجيل:** {m['reg_num']}")
                            st.markdown(f"**القسم:** {m['section']}")
                            st.markdown(f"**تاريخ الميلاد:** {m['birth_date']}")
                        with col2:
                            st.markdown(f"**المشرف:** {m['supervisor']}")
                            st.markdown(f"**الحالة:** {m['status']}")
                            st.markdown(f"**تاريخ الإيداع:** {m['created_at']}")
                        
                        st.markdown(f"**آخر تحديث:** {m['updated_at'] or m['created_at']}")
                        
                        # تحميل الملف
                        if m['file_path'] and os.path.exists(m['file_path']):
                            try:
                                with open(m['file_path'], "rb") as f:
                                    file_bytes = f.read()
                                st.download_button(
                                    "📥 تحميل المذكرة",
                                    data=file_bytes,
                                    file_name=m['file_name'],
                                    mime="application/pdf",
                                    use_container_width=True
                                )
                            except Exception as e:
                                st.error(f"خطأ عند تحضير الملف للتحميل: {e}")
                        else:
                            st.warning("⚠️ الملف غير متوفر على الخادم")
                        
                        # أزرار التعديل والحذف
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("✏️ تعديل", key=f"edit_{m['id']}", use_container_width=True):
                                st.session_state.editing_memo_id = m['id']
                                st.experimental_rerun()
                        
                        with col_b:
                            if st.button("🗑️ حذف", key=f"del_{m['id']}", use_container_width=True, 
                                       type="secondary"):
                                if delete_memo_db(m['id'], st.session_state.username):
                                    st.success("✅ تم حذف المذكرة")
                                    st.experimental_rerun()
            
            # نموذج التعديل
            if 'editing_memo_id' in st.session_state and st.session_state.editing_memo_id:
                memo = get_memo_by_id(st.session_state.editing_memo_id)
                if memo and memo['submitted_by'] == st.session_state.username:
                    st.subheader("✏️ تعديل المذكرة")
                    
                    with st.form("edit_memo_form"):
                        col1, col2 = st.columns(2)
                        with col1:
                            e_first_name = st.text_input("الاسم", value=memo["first_name"], key="e_first_name")
                        with col2:
                            e_last_name = st.text_input("اللقب", value=memo["last_name"], key="e_last_name")
                        
                        e_reg_num = st.text_input("رقم التسجيل", value=memo["reg_num"], key="e_reg_num")
                        
                        # تاريخ الميلاد
                        try:
                            e_birth_date_default = datetime.strptime(memo["birth_date"], "%Y-%m-%d").date()
                        except:
                            e_birth_date_default = datetime.utcnow().date()
                        
                        e_birth_date = st.date_input("تاريخ الميلاد", value=e_birth_date_default, key="e_birth_date")
                        e_section = st.selectbox("القسم", SECTIONS, 
                                                index=SECTIONS.index(memo["section"]) if memo["section"] in SECTIONS else 0, 
                                                key="e_section")
                        
                        # قائمة المشرفين
                        conn = get_db_conn()
                        cur = conn.cursor()
                        cur.execute("SELECT username FROM users WHERE role = 'مشرف' ORDER BY username")
                        supervisors_db = [r["username"] for r in cur.fetchall()]
                        conn.close()
                        
                        supervisors_list = [""] + supervisors_db
                        selected_index = supervisors_list.index(memo["supervisor"]) if memo["supervisor"] in supervisors_list else 0
                        e_supervisor = st.selectbox("اسم المشرف", supervisors_list, index=selected_index, key="e_supervisor")
                        
                        e_title = st.text_input("عنوان المذكرة", value=memo["title"], key="e_title")
                        
                        st.markdown("---")
                        st.info("⚠️ ملاحظة: ترك حقل الملف فارغاً سيحافظ على الملف الحالي")
                        e_file = st.file_uploader("استبدال ملف المذكرة (PDF فقط)", type=["pdf"], key="e_file")
                        
                        col_a, col_b = st.columns(2)
                        with col_a:
                            submit_edit = st.form_submit_button("💾 حفظ التعديلات", use_container_width=True)
                        with col_b:
                            if st.form_submit_button("🚫 إلغاء", use_container_width=True):
                                st.session_state.pop("editing_memo_id", None)
                                st.experimental_rerun()
                        
                        if submit_edit:
                            # التحقق من البيانات
                            data = {
                                "reg_num": e_reg_num,
                                "first_name": e_first_name,
                                "last_name": e_last_name,
                                "birth_date": e_birth_date.strftime("%Y-%m-%d")
                            }
                            valid, error_msg = validate_student_data(data)
                            
                            if not valid:
                                st.error(f"⚠️ خطأ في التحقق: {error_msg}")
                            elif not e_supervisor:
                                st.error("⚠️ يجب اختيار المشرف من القائمة")
                            elif len(e_title) < 10:
                                st.error("⚠️ عنوان المذكرة قصير جداً (10 أحرف على الأقل)")
                            else:
                                # تحديث البيانات
                                updated = {
                                    "reg_num": e_reg_num,
                                    "first_name": e_first_name,
                                    "last_name": e_last_name,
                                    "birth_date": e_birth_date.strftime("%Y-%m-%d"),
                                    "section": e_section,
                                    "supervisor": e_supervisor,
                                    "title": e_title,
                                    "updated_by": st.session_state.username
                                }
                                
                                # التعامل مع الملف
                                if e_file is not None:
                                    # حذف الملف القديم
                                    try:
                                        if memo["file_path"] and os.path.exists(memo["file_path"]):
                                            backup_memo_file(memo["file_path"])
                                            os.remove(memo["file_path"])
                                    except:
                                        pass
                                    
                                    # حفظ الملف الجديد
                                    section_dir = UPLOAD_DIR / safe_filename(e_section)
                                    section_dir.mkdir(parents=True, exist_ok=True)
                                    new_file_name = f"{e_reg_num}_{safe_filename(e_file.name)}"
                                    new_file_path = str(section_dir / new_file_name)
                                    
                                    with open(new_file_path, "wb") as f:
                                        f.write(e_file.getbuffer())
                                    
                                    updated["file_name"] = new_file_name
                                    updated["file_path"] = new_file_path
                                
                                update_memo_db(memo["id"], updated)
                                
                                # إرسال إشعار للمشرف
                                send_notification(e_supervisor, "memo_updated",
                                                 f"تم تحديث المذكرة: {e_title}")
                                
                                st.success("✅ تم حفظ التعديلات بنجاح")
                                st.session_state.pop("editing_memo_id", None)
                                st.experimental_rerun()
            
            # قيود الإيداع - لا يسمح بأكثر من مذكرة واحدة
            if user_memos:
                st.info("ℹ️ لديك مذكرة مودعة مسبقًا. لا يُسمح بإيداع أكثر من مذكرة واحدة. يمكنك تعديل المذكرة الحالية أو حذفها ثم إنشاء أخرى.")
            else:
                # نموذج إيداع جديد
                st.subheader("📝 إيداع مذكرة جديدة")
                
                with st.form("memo_form", clear_on_submit=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        first_name = st.text_input("الاسم", key="first_name")
                    with col2:
                        last_name = st.text_input("اللقب", key="last_name")
                    
                    reg_num = st.text_input("رقم التسجيل", key="reg_num")
                    birth_date = st.date_input("تاريخ الميلاد", key="birth_date")
                    section = st.selectbox("القسم", SECTIONS, key="section")
                    
                    # قائمة المشرفين
                    conn = get_db_conn()
                    cur = conn.cursor()
                    cur.execute("SELECT username FROM users WHERE role = 'مشرف' ORDER BY username")
                    supervisors_db = [r["username"] for r in cur.fetchall()]
                    conn.close()
                    
                    supervisor_options = [""] + supervisors_db
                    supervisor = st.selectbox("اسم المشرف", supervisor_options, key="supervisor")
                    
                    title = st.text_input("عنوان المذكرة", key="title")
                    
                    st.markdown("---")
                    file = st.file_uploader("رفع ملف المذكرة (PDF فقط، الحد الأقصى: 20MB)", 
                                           type=["pdf"], key="file")
                    
                    submitted = st.form_submit_button("📤 إيداع المذكرة", use_container_width=True)
                    
                    if submitted:
                        # التحقق من البيانات
                        data = {
                            "reg_num": reg_num,
                            "first_name": first_name,
                            "last_name": last_name,
                            "birth_date": birth_date.strftime("%Y-%m-%d"),
                            "title": title
                        }
                        
                        valid, error_msg = validate_student_data(data)
                        
                        if not valid:
                            st.error(f"⚠️ خطأ في التحقق: {error_msg}")
                        elif not all([reg_num, first_name, last_name, section, supervisor, title, file]):
                            st.error("⚠️ يرجى تعبئة جميع الحقول ورفع الملف")
                        elif supervisor == "":
                            st.error("⚠️ يجب اختيار المشرف من القائمة")
                        elif file.size > 20 * 1024 * 1024:  # 20MB
                            st.error("⚠️ حجم الملف كبير جداً (الحد الأقصى: 20MB)")
                        else:
                            # حفظ الملف
                            section_dir = UPLOAD_DIR / safe_filename(section)
                            section_dir.mkdir(parents=True, exist_ok=True)
                            filename = f"{reg_num}_{safe_filename(file.name)}"
                            file_path = section_dir / filename
                            
                            try:
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
                                    "مسار الملف": str(file_path),
                                    "مقدم": st.session_state.username,
                                    "تاريخ الإيداع": format_datetime(datetime.utcnow())
                                }
                                
                                memo_id = save_memo_db(memo_data)
                                st.success(f"✅ تم إيداع المذكرة بنجاح (رقم المذكرة: {memo_id})")
                                st.balloons()
                                st.experimental_rerun()
                                
                            except Exception as e:
                                st.error(f"❌ فشل في إيداع المذكرة: {str(e)}")
                                log_action(st.session_state.username, "submit_failed", 
                                          f"فشل إيداع المذكرة: {str(e)}")
        
        elif st.session_state.role == "مشرف":
            # واجهة المشرف
            st.success(f"👨‍🏫 مرحباً بك {st.session_state.username} (مشرف)")
            
            # إنشاء تبويبات للمشرف
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📊 لوحة التحكم", 
                "👥 إدارة الطلبة", 
                "🔍 البحث والتقارير", 
                "⚙️ الإعدادات", 
                "📋 المذكرات"
            ])
            
            with tab1:
                # لوحة التحكم
                st.subheader("📊 لوحة التحكم الرئيسية")
                
                # عرض الإحصائيات
                display_statistics_dashboard()
                
                # آخر المذكرات المودعة
                st.subheader("🆕 آخر المذكرات المودعة")
                recent_memos = load_memos(limit=10)
                
                if recent_memos:
                    for memo in recent_memos[:5]:
                        with st.expander(f"📄 {memo['title']} - {memo['first_name']} {memo['last_name']}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown(f"**القسم:** {memo['section']}")
                                st.markdown(f"**المشرف:** {memo['supervisor']}")
                                st.markdown(f"**الحالة:** {memo['status']}")
                            with col2:
                                st.markdown(f"**رقم التسجيل:** {memo['reg_num']}")
                                st.markdown(f"**مقدم بواسطة:** {memo['submitted_by']}")
                                st.markdown(f"**التاريخ:** {memo['created_at']}")
                            
                            if memo['file_path'] and os.path.exists(memo['file_path']):
                                with open(memo['file_path'], "rb") as f:
                                    file_bytes = f.read()
                                st.download_button(
                                    "📥 تحميل المذكرة",
                                    data=file_bytes,
                                    file_name=memo['file_name'],
                                    mime="application/pdf"
                                )
                            
                            # تغيير الحالة
                            status_options = ["معلقة", "مقبولة", "مرفوضة", "تحت المراجعة"]
                            current_status = memo['status'] if memo['status'] in status_options else "معلقة"
                            new_status = st.selectbox(
                                "تغيير الحالة",
                                status_options,
                                index=status_options.index(current_status),
                                key=f"status_{memo['id']}"
                            )
                            
                            if new_status != current_status:
                                if st.button("تحديث الحالة", key=f"update_status_{memo['id']}"):
                                    update_memo_status(memo['id'], new_status, st.session_state.username)
                                    st.success(f"✅ تم تحديث الحالة إلى: {new_status}")
                                    st.experimental_rerun()
                else:
                    st.info("لا توجد مذكرات مودعة بعد.")
            
            with tab2:
                # إدارة حسابات الطلبة
                st.subheader("👥 إدارة حسابات الطلبة")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    with st.expander("➕ إنشاء حساب طالب جديد", expanded=True):
                        with st.form("create_student_form"):
                            new_username = st.text_input("اسم المستخدم للطالب")
                            new_password = st.text_input("كلمة المرور الأولية", type="password")
                            gen = st.checkbox("توليد كلمة مرور آمنة تلقائياً")
                            
                            if gen:
                                new_password = secrets.token_urlsafe(12)
                                st.info(f"🔑 كلمة المرور المولدة: `{new_password}`")
                            
                            submit_create = st.form_submit_button("إنشاء الحساب")
                            
                            if submit_create:
                                if not new_username or not new_password:
                                    st.error("⚠️ الرجاء إدخال اسم مستخدم وكلمة مرور")
                                else:
                                    try:
                                        create_user(new_username, new_password, "طالب", 
                                                   created_by=st.session_state.username)
                                        
                                        # إرسال إشعار للطالب
                                        send_notification(new_username, "account_created",
                                                         f"تم إنشاء حساب جديد لك. اسم المستخدم: {new_username}")
                                        
                                        st.success(f"✅ تم إنشاء حساب الطالب '{new_username}' بنجاح")
                                        st.info(f"🔐 كلمة المرور: {new_password} - يرجى تسليمها للطالب بأمان")
                                        
                                    except ValueError as e:
                                        st.error(f"❗ {e}")
                                    except Exception as e:
                                        st.error(f"❌ فشل إنشاء الحساب: {e}")
                
                with col2:
                    with st.expander("🔧 إدارة كلمات المرور", expanded=True):
                        conn = get_db_conn()
                        cur = conn.cursor()
                        cur.execute("SELECT username FROM users WHERE role = 'طالب' ORDER BY username")
                        students = [r["username"] for r in cur.fetchall()]
                        conn.close()
                        
                        if students:
                            sel_student = st.selectbox("اختَر طالباً", [""] + students, key="sel_student")
                            
                            if sel_student:
                                with st.form("reset_pwd_form"):
                                    new_pwd = st.text_input("كلمة المرور الجديدة", type="password", key="new_pwd")
                                    gen2 = st.checkbox("توليد كلمة مرور آمنة تلقائياً", key="gen2")
                                    
                                    if gen2:
                                        new_pwd = secrets.token_urlsafe(12)
                                        st.info(f"🔑 كلمة المرور المولدة: `{new_pwd}`")
                                    
                                    submit_reset = st.form_submit_button("تعيين كلمة المرور")
                                    
                                    if submit_reset:
                                        if not new_pwd:
                                            st.error("⚠️ أدخل كلمة مرور جديدة")
                                        else:
                                            try:
                                                update_user_password(sel_student, new_pwd)
                                                
                                                # إرسال إشعار للطالب
                                                send_notification(sel_student, "password_changed",
                                                                 "تم تغيير كلمة المرور الخاصة بحسابك")
                                                
                                                st.success(f"✅ تم تحديث كلمة مرور الطالب '{sel_student}'")
                                                st.info(f"🔐 كلمة المرور الجديدة: {new_pwd}")
                                                
                                            except Exception as e:
                                                st.error(f"❌ فشل التحديث: {e}")
                        else:
                            st.info("لا يوجد طلاب مسجلين حتى الآن")
                
                # قائمة الطلاب
                st.subheader("📋 قائمة الطلاب المسجلين")
                conn = get_db_conn()
                cur = conn.cursor()
                cur.execute("SELECT username, created_at, last_login FROM users WHERE role = 'طالب' ORDER BY created_at DESC")
                students_list = cur.fetchall()
                conn.close()
                
                if students_list:
                    df = pd.DataFrame(students_list, columns=["اسم المستخدم", "تاريخ الإنشاء", "آخر دخول"])
                    st.dataframe(df, use_container_width=True)
                    
                    # إحصائيات الطلاب
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("عدد الطلاب", len(students_list))
                    with col2:
                        active_students = sum(1 for s in students_list if s['last_login'])
                        st.metric("الطلاب النشطين", active_students)
                    with col3:
                        today = datetime.now().date()
                        new_today = sum(1 for s in students_list if s['created_at'] and 
                                       datetime.fromisoformat(s['created_at']).date() == today)
                        st.metric("مستجدون اليوم", new_today)
                else:
                    st.info("لا توجد سجلات للطلاب")
            
            with tab3:
                # البحث والتقارير
                st.subheader("🔍 البحث المتقدم في المذكرات")
                
                with st.form("search_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        search_keyword = st.text_input("كلمة البحث", key="search_keyword")
                        search_type = st.selectbox("نوع البحث", 
                                                  ["all", "title", "reg_num", "supervisor", "student"], 
                                                  key="search_type")
                        search_section = st.selectbox("القسم", ["الكل"] + SECTIONS, key="search_section")
                    
                    with col2:
                        conn = get_db_conn()
                        cur = conn.cursor()
                        cur.execute("SELECT username FROM users WHERE role = 'مشرف' ORDER BY username")
                        supervisors = ["الكل"] + [r["username"] for r in cur.fetchall()]
                        conn.close()
                        
                        search_supervisor = st.selectbox("المشرف", supervisors, key="search_supervisor")
                        search_start_date = st.date_input("من تاريخ", key="search_start_date")
                        search_end_date = st.date_input("إلى تاريخ", key="search_end_date")
                    
                    search_submitted = st.form_submit_button("🔍 بحث")
                    
                    if search_submitted:
                        results = advanced_search(
                            keyword=search_keyword,
                            search_type=search_type,
                            section=search_section if search_section != "الكل" else "",
                            supervisor=search_supervisor if search_supervisor != "الكل" else "",
                            start_date=search_start_date.strftime("%Y-%m-%d") if search_start_date else "",
                            end_date=search_end_date.strftime("%Y-%m-%d") if search_end_date else ""
                        )
                        
                        if results:
                            st.success(f"✅ تم العثور على {len(results)} نتيجة")
                            
                            # تصدير النتائج
                            export_data = []
                            for r in results:
                                export_data.append({
                                    "رقم التسجيل": r['reg_num'],
                                    "الاسم": r['first_name'],
                                    "اللقب": r['last_name'],
                                    "القسم": r['section'],
                                    "المشرف": r['supervisor'],
                                    "العنوان": r['title'],
                                    "الحالة": r['status'],
                                    "تاريخ الإيداع": r['created_at']
                                })
                            
                            df = pd.DataFrame(export_data)
                            st.dataframe(df, use_container_width=True)
                            
                            # خيارات التصدير
                            col_a, col_b = st.columns(2)
                            with col_a:
                                csv = df.to_csv(index=False).encode('utf-8')
                                st.download_button(
                                    "📥 تحميل كملف CSV",
                                    data=csv,
                                    file_name=f"نتائج_البحث_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                    mime="text/csv"
                                )
                            
                            with col_b:
                                excel_buffer = BytesIO()
                                df.to_excel(excel_buffer, index=False)
                                excel_buffer.seek(0)
                                st.download_button(
                                    "📥 تحميل كملف Excel",
                                    data=excel_buffer,
                                    file_name=f"نتائج_البحث_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )
                        else:
                            st.warning("⚠️ لم يتم العثور على نتائج مطابقة")
            
            with tab4:
                # الإعدادات
                st.subheader("⚙️ إعدادات النظام")
                
                if st.session_state.permissions.get("backup_restore", False):
                    with st.expander("💾 النسخ الاحتياطي"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button("إنشاء نسخة احتياطية", use_container_width=True):
                                backup_file = create_database_backup()
                                if backup_file:
                                    st.success(f"✅ تم إنشاء النسخة الاحتياطية: {backup_file.name}")
                                    
                                    # تحميل النسخة الاحتياطية
                                    with open(backup_file, "rb") as f:
                                        backup_bytes = f.read()
                                    
                                    st.download_button(
                                        "📥 تحميل النسخة الاحتياطية",
                                        data=backup_bytes,
                                        file_name=backup_file.name,
                                        mime="application/octet-stream"
                                    )
                                else:
                                    st.error("❌ فشل في إنشاء النسخة الاحتياطية")
                        
                        with col2:
                            uploaded_backup = st.file_uploader("استعادة من نسخة احتياطية", type=["db"])
                            if uploaded_backup and st.button("استعادة النسخة الاحتياطية", use_container_width=True):
                                try:
                                    # إنشاء نسخة احتياطية من الحالية أولاً
                                    current_backup = create_database_backup()
                                    
                                    # استبدال قاعدة البيانات
                                    with open(DB_FILE, "wb") as f:
                                        f.write(uploaded_backup.getbuffer())
                                    
                                    st.success("✅ تم استعادة النسخة الاحتياطية بنجاح")
                                    st.info(f"💡 تم إنشاء نسخة احتياطية من الحالية: {current_backup.name if current_backup else 'فشل'}")
                                    st.warning("⚠️ يرجى إعادة تحميل الصفحة")
                                    
                                except Exception as e:
                                    st.error(f"❌ فشل في استعادة النسخة الاحتياطية: {e}")
                
                if st.session_state.permissions.get("view_logs", False):
                    with st.expander("📜 سجلات النظام"):
                        logs = get_recent_logs(100)
                        
                        if logs:
                            log_data = []
                            for log in logs:
                                log_data.append({
                                    "المستخدم": log['user'],
                                    "الإجراء": log['action'],
                                    "التفاصيل": log['details'],
                                    "عنوان IP": log['ip_address'],
                                    "الوقت": log['created_at']
                                })
                            
                            df_logs = pd.DataFrame(log_data)
                            st.dataframe(df_logs, use_container_width=True)
                            
                            # تحميل السجلات
                            csv_logs = df_logs.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                "📥 تحميل السجلات",
                                data=csv_logs,
                                file_name=f"سجلات_النظام_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
                        else:
                            st.info("لا توجد سجلات")
                
                with st.expander("🔧 تحسين النظام"):
                    if st.button("تحسين قاعدة البيانات", use_container_width=True):
                        msg = optimize_database()
                        st.success(msg)
                    
                    if st.button("تنظيف الملفات المؤقتة", use_container_width=True):
                        # حساب حجم الملفات
                        total_size = 0
                        for path in UPLOAD_DIR.rglob("*"):
                            if path.is_file():
                                total_size += path.stat().st_size
                        
                        st.info(f"📁 حجم ملفات المذكرات: {total_size / (1024*1024):.2f} MB")
            
            with tab5:
                # إدارة المذكرات
                st.subheader("📋 إدارة المذكرات")
                
                # تصفية المذكرات
                col1, col2, col3 = st.columns(3)
                with col1:
                    filter_section = st.selectbox("القسم", ["الكل"] + SECTIONS, key="filter_section")
                with col2:
                    conn = get_db_conn()
                    cur = conn.cursor()
                    cur.execute("SELECT username FROM users WHERE role = 'مشرف' ORDER BY username")
                    filter_supervisors = ["الكل"] + [r["username"] for r in cur.fetchall()]
                    conn.close()
                    
                    filter_supervisor = st.selectbox("المشرف", filter_supervisors, key="filter_supervisor")
                with col3:
                    filter_status = st.selectbox("الحالة", ["الكل", "معلقة", "مقبولة", "مرفوضة", "تحت المراجعة"], 
                                               key="filter_status")
                
                # عرض المذكرات المصفاة
                filtered_memos = load_memos(
                    section=filter_section if filter_section != "الكل" else None,
                    supervisor=filter_supervisor if filter_supervisor != "الكل" else None,
                    status=filter_status if filter_status != "الكل" else None
                )
                
                st.metric("عدد المذكرات", len(filtered_memos))
                
                if filtered_memos:
                    for memo in filtered_memos:
                        with st.expander(f"📄 {memo['title']} - {memo['first_name']} {memo['last_name']} ({memo['status']})"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown(f"**رقم التسجيل:** {memo['reg_num']}")
                                st.markdown(f"**القسم:** {memo['section']}")
                                st.markdown(f"**تاريخ الميلاد:** {memo['birth_date']}")
                                st.markdown(f"**المشرف:** {memo['supervisor']}")
                            with col2:
                                st.markdown(f"**مقدم بواسطة:** {memo['submitted_by']}")
                                st.markdown(f"**تاريخ الإيداع:** {memo['created_at']}")
                                st.markdown(f"**آخر تحديث:** {memo['updated_at'] or memo['created_at']}")
                                st.markdown(f"**الحالة:** {memo['status']}")
                            
                            # تحميل الملف
                            if memo['file_path'] and os.path.exists(memo['file_path']):
                                with open(memo['file_path'], "rb") as f:
                                    file_bytes = f.read()
                                
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    st.download_button(
                                        "📥 تحميل المذكرة",
                                        data=file_bytes,
                                        file_name=memo['file_name'],
                                        mime="application/pdf",
                                        use_container_width=True
                                    )
                                
                                with col_b:
                                    # تغيير الحالة
                                    status_options = ["معلقة", "مقبولة", "مرفوضة", "تحت المراجعة"]
                                    current_status = memo['status'] if memo['status'] in status_options else "معلقة"
                                    new_status = st.selectbox(
                                        "تغيير الحالة",
                                        status_options,
                                        index=status_options.index(current_status),
                                        key=f"status_filter_{memo['id']}",
                                        label_visibility="collapsed"
                                    )
                                    
                                    if new_status != current_status:
                                        if st.button("تحديث", key=f"update_filter_{memo['id']}", use_container_width=True):
                                            update_memo_status(memo['id'], new_status, st.session_state.username)
                                            st.experimental_rerun()
                            
                            # حذف المذكرة (للمشرفين المصرح لهم فقط)
                            if st.session_state.permissions.get("delete_memos", False):
                                st.markdown("---")
                                if st.button("🗑️ حذف المذكرة", key=f"delete_admin_{memo['id']}", 
                                           type="secondary", use_container_width=True):
                                    if delete_memo_db(memo['id'], st.session_state.username):
                                        st.success("✅ تم حذف المذكرة")
                                        st.experimental_rerun()
                else:
                    st.info("لا توجد مذكرات مطابقة لمعايير التصفية")
        
        # زر تسجيل الخروج
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚪 تسجيل الخروج", use_container_width=True):
                log_action(st.session_state.username, "logout", "تسجيل الخروج")
                reset_session()
                st.success("✅ تم تسجيل الخروج بنجاح")
                st.experimental_rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # التذييل
    st.markdown("---")
    st.markdown("""
    <div class="footer">
        <p>منصة إيداع مذكرات التخرج - كلية علوم الطبيعة والحياة وعلوم الأرض والكون</p>
        <p>جامعة محمد البشير الإبراهيمي - برج بوعريريج</p>
        <p>© 2024 جميع الحقوق محفوظة</p>
        <p style="font-size: 0.8rem; color: #888;">الإصدار 2.0 | آخر تحديث: ديسمبر 2024</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# إضافة استيراد BytesIO للتعامل مع ملفات Excel
import io
BytesIO = io.BytesIO
