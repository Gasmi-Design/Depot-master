import streamlit as st
import os
import re
import pandas as pd
from datetime import datetime
from pathlib import Path
import tempfile
import shutil
import sqlite3
import hashlib
import hmac
import secrets

# ---------------------------------------
# تكوين الصفحة وCSS (عربي، RTL)
# ---------------------------------------
st.set_page_config(page_title="منصة إيداع مذكرات التخرج", layout="centered")

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

# ---------------------------------------
# بيانات أولية: قائمة المشرفين (كما في النسخة الأصلية)
# سيتم نقل هذه الحسابات إلى قاعدة بيانات SQLite مشفّرة عند التشغيل الأول
# ---------------------------------------
PASSWORDS = {
    "مشرف": {
        "salima.belloula": "Qr8$kL2pT9wA",
        "imane.kerbouai": "Nf4@vR7xZ1qS",
        "meriem.nasri": "Sb7%pM3kH8uY",
        "mokhtar.guissous": "Vt6#bC9rQ2eW",
        "farida.belkasmi": "Lp3#vT8nS5yZ",
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
        "nadjat.iratni": "Gy9#rK4mS1wP",
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
        "abdellali.lazazga": "Qz6#gR3nT1vM",
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
# دوال تشفير كلمات المرور باستخدام PBKDF2 (موجودة في المكتبة القياسية — لا تعتمد على حزم خارجية)
# ---------------------------------------
PBKDF2_ITERATIONS = 200_000  # قيمة آمنة لمعظم الاستخدامات
SALT_BYTES = 16

def hash_password(password: str):
    """
    توليد salt وهاش مستمد عبر PBKDF2-HMAC-SHA256
    نعيد tuple (salt_hex, hash_hex)
    """
    salt = secrets.token_bytes(SALT_BYTES)
    hash_bytes = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return salt.hex(), hash_bytes.hex()

def verify_password(password: str, salt_hex: str, hash_hex: str) -> bool:
    salt = bytes.fromhex(salt_hex)
    expected = bytes.fromhex(hash_hex)
    calc = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return hmac.compare_digest(calc, expected)

# ---------------------------------------
# إعداد قاعدة بيانات SQLite لتخزين المستخدمين والمذكرات
# ---------------------------------------
BASE_DIR = Path.cwd()
DB_FILE = BASE_DIR / "app.db"
UPLOAD_DIR = BASE_DIR / "uploaded_memos"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def get_db_conn():
    conn = sqlite3.connect(str(DB_FILE), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_conn()
    cur = conn.cursor()
    # جدول المستخدمين
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        role TEXT NOT NULL, -- 'مشرف' أو 'طالب'
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        created_by TEXT,
        created_at TEXT
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
        created_at TEXT
    )
    """)
    conn.commit()

    # إدراج مشرفي البداية بأمان (تجاهل الإدخالات المكررة)
    if "مشرف" in PASSWORDS:
        for uname, pwd in PASSWORDS["مشرف"].items():
            salt, hsh = hash_password(pwd)
            try:
                cur.execute(
                    "INSERT OR IGNORE INTO users (username, role, password_hash, salt, created_by, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (uname, "مشرف", hsh, salt, "system", datetime.utcnow().isoformat())
                )
            except sqlite3.IntegrityError:
                # في حال حدث سباق أو إدخال مكرر، نتجاهله
                pass
    conn.commit()
    conn.close()

init_db()

# ---------------------------------------
# دوال إدارة المستخدمين والمذكرات في DB
# ---------------------------------------
def get_user(username: str):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    return row

def create_user(username: str, password: str, role: str, created_by: str = None):
    if get_user(username):
        raise ValueError("اسم المستخدم موجود بالفعل")
    salt, hsh = hash_password(password)
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (username, role, password_hash, salt, created_by, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (username, role, hsh, salt, created_by, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def update_user_password(username: str, new_password: str):
    if not get_user(username):
        raise ValueError("المستخدم غير موجود")
    salt, hsh = hash_password(new_password)
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("UPDATE users SET password_hash = ?, salt = ? WHERE username = ?", (hsh, salt, username))
    conn.commit()
    conn.close()

def save_memo_db(record: dict):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO memos (reg_num, first_name, last_name, birth_date, section, supervisor, title, file_name, file_path, submitted_by, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        record.get("تاريخ الإيداع")
    ))
    conn.commit()
    conn.close()

def load_memos(section: str = None, supervisor: str = None):
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
    if filters:
        q += " WHERE " + " AND ".join(filters)
    q += " ORDER BY created_at DESC"
    cur.execute(q, params)
    rows = cur.fetchall()
    conn.close()
    return rows

# ---------------------------------------
# دوال لإدارة مذكرات المستخدم (عرض/تحديث/حذف)
# ---------------------------------------
def get_memos_by_user(username: str):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM memos WHERE submitted_by = ? ORDER BY created_at DESC", (username,))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_memo_by_id(memo_id: int):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM memos WHERE id = ?", (memo_id,))
    row = cur.fetchone()
    conn.close()
    return row

def update_memo_db(memo_id: int, updated: dict):
    """
    updated expects keys matching columns: reg_num, first_name, last_name, birth_date,
    section, supervisor, title, file_name, file_path
    """
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
        "file_path": "file_path"
    }
    for k, col in mapping.items():
        if k in updated:
            cols.append(f"{col} = ?")
            params.append(updated[k])
    if not cols:
        conn.close()
        return
    params.append(memo_id)
    q = f"UPDATE memos SET {', '.join(cols)} WHERE id = ?"
    cur.execute(q, params)
    conn.commit()
    conn.close()

def delete_memo_db(memo_id: int):
    # يحذف السجل والملف المربوط إن وُجد
    m = get_memo_by_id(memo_id)
    if m and m["file_path"]:
        try:
            if os.path.exists(m["file_path"]):
                os.remove(m["file_path"])
        except Exception:
            pass
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM memos WHERE id = ?", (memo_id,))
    conn.commit()
    conn.close()

# ---------------------------------------
# دوال مساعدة صغيرة
# ---------------------------------------
def safe_filename(name: str) -> str:
    name = os.path.basename(name)
    parts = name.rsplit(".", 1)
    if len(parts) == 2:
        base, ext = parts
        ext = "." + ext
    else:
        base = parts[0]
        ext = ""
    base = re.sub(r"[^\w\s\-]", "", base)
    base = re.sub(r"\s+", "_", base)
    return base[:200] + ext

def format_datetime(dt: datetime):
    return dt.strftime("%Y-%m-%d %H:%M:%S")

# ---------------------------------------
# إدارة جلسة Streamlit بأمان (نُعيد تهيئة القيم الافتراضية بدل الحذف)
# ---------------------------------------
def reset_session():
    """
    إعادة تهيئة حالة الجلسة بأمان:
    - لا نحذف مفاتيح الويجت، بل نعيد تعيين مفاتيح التطبيق المعروفة إلى قيم افتراضية.
    - ثم نضبط حالة الدخول إلى False.
    """
    # قيم افتراضية آمنة للمفاتيح المعروفة
    defaults = {
        "login_role": "طالب",
        "login_username": "",
        "login_password": "",
        "first_name": "",
        "last_name": "",
        "reg_num": "",
        "birth_date": datetime.utcnow().date(),
        "section": "",
        "supervisor": "",
        "title": "",
        "file": None,
        "new_username": "",
        "new_password": "",
        "gen": False,
        "sel_student": "",
        "new_pwd": "",
        "gen2": False,
        "editing_memo_id": None,
        # مفاتيح نموذج التعديل
        "e_first_name": "",
        "e_last_name": "",
        "e_reg_num": "",
        "e_birth_date": datetime.utcnow().date(),
        "e_section": "",
        "e_supervisor": "",
        "e_title": "",
        "e_file": None
    }

    for k, v in defaults.items():
        st.session_state[k] = v

    # مفاتيح التحكم في الجلسة
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None

# ---------------------------------------
# محتوى الواجهة
# ---------------------------------------
sections = ["العلوم البيولوجية", "العلوم الفلاحية", "علوم التغذية", "علم البيئة والمحيط"]

with st.container():
    st.markdown('<div class="main">', unsafe_allow_html=True)
    st.markdown("<h1>📚 منصة إيداع مذكرات التخرج</h1>", unsafe_allow_html=True)
    st.markdown("<h4>جامعة محمد البشير الإبراهيمي - برج بوعريريج<br>كلية علوم الطبيعة والحياة وعلوم الأرض والكون</h4>", unsafe_allow_html=True)

    if not st.session_state.logged_in:
        role = st.selectbox("👤 اختر نوع الدخول:", ["طالب", "مشرف"], key="login_role")

        with st.form("login_form"):
            username = st.text_input("👤 اسم المستخدم", key="login_username")
            password = st.text_input("🔐 كلمة المرور:", type="password", key="login_password")
            submitted = st.form_submit_button("تسجيل الدخول")

        if submitted:
            user = get_user(username)
            if user and user["role"] == role:
                if verify_password(password, user["salt"], user["password_hash"]):
                    # ضبط قيم افتراضية لحقول النماذج (بدلاً من حذف المفاتيح) لتجنّب عدم تناسق الويجت أثناء rerun
                    safe_defaults = {
                        "first_name": "",
                        "last_name": "",
                        "reg_num": "",
                        "birth_date": datetime.utcnow().date(),
                        "section": "",
                        "supervisor": "",
                        "title": "",
                        "file": None
                    }
                    for k, v in safe_defaults.items():
                        st.session_state[k] = v

                    st.session_state.logged_in = True
                    st.session_state.role = role
                    st.session_state.username = username
                    st.experimental_rerun()
                else:
                    st.error("⚠️ اسم المستخدم أو كلمة السر غير صحيحة")
            else:
                st.error("⚠️ اسم المستخدم غير موجود أو الدور غير صحيح")

    else:
        # بعد تسجيل الدخول
        if st.session_state.role == "طالب":
            st.success(f"مرحباً بك {st.session_state.username} (طالب)")

            # أولاً: اعرض المذكرات التي أرسلها هذا المستخدم مسبقًا (إن وجدت)
            user_memos = get_memos_by_user(st.session_state.username)
            if user_memos:
                st.subheader("📂 مذكراتك المودعة")
                for m in user_memos:
                    with st.expander(f"{m['title']} — {m['first_name']} {m['last_name']} (#{m['id']})"):
                        st.markdown(f"**رقم التسجيل:** {m['reg_num']}")
                        st.markdown(f"**القسم:** {m['section']}")
                        st.markdown(f"**المشرف:** {m['supervisor']}")
                        st.markdown(f"**تاريخ الإيداع:** {m['created_at']}")
                        if m['file_path'] and os.path.exists(m['file_path']):
                            try:
                                with open(m['file_path'], "rb") as f:
                                    file_bytes = f.read()
                                st.download_button("تحميل المذكرة", data=file_bytes, file_name=m['file_name'], mime="application/pdf")
                            except Exception as e:
                                st.error(f"خطأ عند تحضير الملف للتحميل: {e}")
                        else:
                            st.warning("الملف غير متوفر على الخادم")

                        # أزرار تعديل / حذف
                        col_a, col_b = st.columns([1,1])
                        if col_a.button("✏️ تعديل هذه المذكرة", key=f"edit_{m['id']}"):
                            # احفظ id الذي سيتم تعديله في حالة الجلسة ونعدّل العرض
                            st.session_state.editing_memo_id = m['id']
                            st.experimental_rerun()
                        if col_b.button("🗑️ حذف المذكرة", key=f"del_{m['id']}"):
                            delete_memo_db(m['id'])
                            st.success("تم حذف المذكرة")
                            st.experimental_rerun()

            # إذا الطالب يحق له تعديل سجل محدد نعرض نموذج التعديل
            if 'editing_memo_id' in st.session_state and st.session_state.editing_memo_id:
                memo = get_memo_by_id(st.session_state.editing_memo_id)
                if memo:
                    st.subheader("✏️ تعديل المذكرة")
                    with st.form("edit_memo_form"):
                        col1, col2 = st.columns(2)
                        with col1:
                            e_first_name = st.text_input("الاسم", value=memo["first_name"], key="e_first_name")
                        with col2:
                            e_last_name = st.text_input("اللقب", value=memo["last_name"], key="e_last_name")
                        e_reg_num = st.text_input("رقم التسجيل", value=memo["reg_num"], key="e_reg_num")
                        # تحويل النص إلى تاريخ
                        try:
                            e_birth_date_default = datetime.strptime(memo["birth_date"], "%Y-%m-%d").date()
                        except Exception:
                            e_birth_date_default = datetime.utcnow().date()
                        e_birth_date = st.date_input("تاريخ الميلاد", value=e_birth_date_default, key="e_birth_date")
                        e_section = st.selectbox("القسم", sections, index=sections.index(memo["section"]) if memo["section"] in sections else 0, key="e_section")

                        # مشرف: اختر من القائمة
                        conn = get_db_conn()
                        cur = conn.cursor()
                        cur.execute("SELECT username FROM users WHERE role = 'مشرف' ORDER BY username")
                        supervisors_db = [r["username"] for r in cur.fetchall()]
                        conn.close()
                        supervisors_list = [""] + supervisors_db
                        selected_index = supervisors_list.index(memo["supervisor"]) if memo["supervisor"] in supervisors_list else 0
                        e_supervisor = st.selectbox("اسم المشرف", supervisors_list, index=selected_index, key="e_supervisor")

                        e_title = st.text_input("عنوان المذكرة", value=memo["title"], key="e_title")
                        e_file = st.file_uploader("استبدال ملف المذكرة (PDF فقط) - اتركه فارغاً إن لم تريد تغييره", type=["pdf"], key="e_file")
                        submit_edit = st.form_submit_button("حفظ التعديلات")
                    if submit_edit:
                        # تعامل مع استبدال الملف إنّ وُجد
                        new_file_name = memo["file_name"]
                        new_file_path = memo["file_path"]
                        if e_file is not None:
                            # احذف القديم وحفظ الجديد
                            try:
                                if memo["file_path"] and os.path.exists(memo["file_path"]):
                                    os.remove(memo["file_path"])
                            except Exception:
                                pass
                            section_dir = UPLOAD_DIR / safe_filename(e_section)
                            section_dir.mkdir(parents=True, exist_ok=True)
                            new_file_name = f"{e_reg_num}_{safe_filename(e_file.name)}"
                            new_file_path = str(section_dir / new_file_name)
                            with open(new_file_path, "wb") as f:
                                f.write(e_file.getbuffer())

                        updated = {
                            "reg_num": e_reg_num,
                            "first_name": e_first_name,
                            "last_name": e_last_name,
                            "birth_date": e_birth_date.strftime("%Y-%m-%d"),
                            "section": e_section,
                            "supervisor": e_supervisor,
                            "title": e_title,
                            "file_name": new_file_name,
                            "file_path": new_file_path
                        }
                        update_memo_db(memo["id"], updated)
                        st.success("✅ تم حفظ التعديلات")
                        # إنهاء وضع التحرير
                        st.session_state.pop("editing_memo_id", None)
                        st.experimental_rerun()

            # قيود: لا نسمح بإيداع أكثر من مذكرة واحدة لكل طالب (يمكن تعديل هذا السلوك لاحقًا)
            if user_memos:
                st.info("ℹ️ لديك مذكرة مودعة مسبقًا. لا يُسمح بإيداع أكثر من مذكرة واحدة. يمكنك تعديل المذكرة الحالية أو حذفها ثم إنشاء أخرى.")
            else:
                # نوفر نموذج إيداع جديد فقط إذا لم يكن لدى الطالب مذكرة مسبقًا
                st.subheader("📝 إيداع مذكرة جديدة")
                with st.form("memo_form", clear_on_submit=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        first_name = st.text_input("الاسم", key="first_name")
                    with col2:
                        last_name = st.text_input("اللقب", key="last_name")

                    reg_num = st.text_input("رقم التسجيل", key="reg_num")
                    birth_date = st.date_input("تاريخ الميلاد", key="birth_date")
                    section = st.selectbox("القسم", sections, key="section")

                    conn = get_db_conn()
                    cur = conn.cursor()
                    cur.execute("SELECT username FROM users WHERE role = 'مشرف' ORDER BY username")
                    supervisors_db = [r["username"] for r in cur.fetchall()]
                    conn.close()

                    supervisor_options = [""] + supervisors_db
                    supervisor = st.selectbox("اسم المشرف", supervisor_options, key="supervisor")

                    title = st.text_input("عنوان المذكرة", key="title")
                    file = st.file_uploader("رفع ملف المذكرة (PDF فقط)", type=["pdf"], key="file")

                    submitted = st.form_submit_button("إيداع المذكرة")

                    if submitted:
                        if not all([reg_num, first_name, last_name, section, supervisor, title, file]):
                            st.error("⚠️ يرجى تعبئة جميع الحقول ورفع الملف. تأكد من اختيار المشرف من القائمة.")
                        else:
                            section_dir = UPLOAD_DIR / safe_filename(section)
                            section_dir.mkdir(parents=True, exist_ok=True)
                            filename = f"{reg_num}_{safe_filename(file.name)}"
                            file_path = section_dir / filename
                            try:
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
                                    "مسار الملف": str(file_path),
                                    "مقدم": st.session_state.username,
                                    "تاريخ الإيداع": format_datetime(datetime.utcnow())
                                }
                                try:
                                    save_memo_db(memo_data)
                                    st.success("✅ تم إيداع المذكرة بنجاح")
                                    st.experimental_rerun()
                                except Exception as e:
                                    st.error(f"فشل في حفظ بيانات المذكرة: {e}")

        elif st.session_state.role == "مشرف":
            st.success(f"مرحباً بك {st.session_state.username} (مشرف)")

            st.subheader("🛠️ إدارة حسابات الطلبة")
            with st.expander("إنشاء حساب طالب جديد"):
                with st.form("create_student_form"):
                    new_username = st.text_input("اسم المستخدم للطالب (مثال: student123)")
                    new_password = st.text_input("كلمة المرور الأولية (سوف تُخزَّن مشفّرة)", type="password")
                    gen = st.checkbox("توليد كلمة مرور آمنة تلقائياً")
                    if gen:
                        # توليد كلمة مرور آمنة بسيطة (يمكن تحسينها لاحقاً)
                        new_password = secrets.token_urlsafe(10)
                        st.info(f"كلمة المرور المولدة: {new_password} - الرجاء تسليمها للطالب آمنًا")

                    submit_create = st.form_submit_button("إنشاء الحساب")
                if submit_create:
                    if not new_username or not new_password:
                        st.error("⚠️ الرجاء إدخال اسم مستخدم وكلمة مرور")
                    else:
                        try:
                            create_user(new_username, new_password, "طالب", created_by=st.session_state.username)
                            st.success("✅ تم إنشاء حساب الطالب بنجاح — سلّم بيانات الدخول للطالب بأمان")
                        except ValueError as e:
                            st.error(f"❗ {e}")
                        except Exception as e:
                            st.error(f"فشل إنشاء الحساب: {e}")

            with st.expander("إدارة كلمات مرور الطلبة"):
                conn = get_db_conn()
                cur = conn.cursor()
                cur.execute("SELECT username FROM users WHERE role = 'طالب' ORDER BY username")
                students = [r["username"] for r in cur.fetchall()]
                conn.close()
                if students:
                    sel_student = st.selectbox("اختَر طالباً لتغيير كلمة المرور", [""] + students)
                    if sel_student:
                        with st.form("reset_pwd_form"):
                            new_pwd = st.text_input("كلمة المرور الجديدة", type="password")
                            gen2 = st.checkbox("توليد كلمة مرور آمنة تلقائياً", key="gen2")
                            if gen2:
                                new_pwd = secrets.token_urlsafe(10)
                                st.info(f"كلمة المرور المولدة: {new_pwd} - سلّمها للطالب بأمان")
                            submit_reset = st.form_submit_button("تعيين كلمة المرور")
                        if submit_reset:
                            if not new_pwd:
                                st.error("⚠️ أدخل كلمة مرور جديدة")
                            else:
                                try:
                                    update_user_password(sel_student, new_pwd)
                                    st.success("✅ تم تحديث كلمة المرور — سلّمها للطالب بأمان")
                                except Exception as e:
                                    st.error(f"فشل التحديث: {e}")
                else:
                    st.info("لا يوجد طلاب مسجلين حتى الآن")

            # لوحة تحكم المذكرات
            st.subheader("📊 لوحة التحكم")
            memos = load_memos()
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f'<div class="metric-box">المذكرات المودعة<br><b>{len(memos)}</b></div>', unsafe_allow_html=True)
            with col2:
                sections_count = len(set([r["section"] for r in memos if r["section"]]))
                st.markdown(f'<div class="metric-box">عدد الأقسام<br><b>{sections_count}</b></div>', unsafe_allow_html=True)
            with col3:
                supervisors_count = len(set([r["supervisor"] for r in memos if r["supervisor"]]))
                st.markdown(f'<div class="metric-box">عدد المشرفين<br><b>{supervisors_count}</b></div>', unsafe_allow_html=True)

            # تصفية و عرض
            st.subheader("🔍 تصفية المذكرات")
            col1, col2 = st.columns(2)
            with col1:
                selected_section = st.selectbox("القسم", ["الكل"] + sections)
            with col2:
                # احصل على المشرفين من جدول users لعرض جميع المشرفين
                conn = get_db_conn()
                cur = conn.cursor()
                cur.execute("SELECT username FROM users WHERE role = 'مشرف' ORDER BY username")
                supervisors = ["الكل"] + [r["username"] for r in cur.fetchall()]
                conn.close()
                selected_supervisor = st.selectbox("المشرف", supervisors)

            filtered = load_memos(section=selected_section, supervisor=selected_supervisor)

            st.subheader(f"📄 المذكرات ({len(filtered)})")
            if not filtered:
                st.info("لا توجد مذكرات حسب معايير التصفية")
            else:
                for row in filtered:
                    with st.expander(f"{row['title']} - {row['first_name']} {row['last_name']}"):
                        st.markdown(f"**رقم التسجيل:** {row['reg_num']}")
                        st.markdown(f"**القسم:** {row['section']}")
                        st.markdown(f"**المشرف:** {row['supervisor']}")
                        st.markdown(f"**مقدم:** {row['submitted_by']}")
                        st.markdown(f"**تاريخ الإيداع:** {row['created_at']}")
                        file_path = row['file_path']
                        if file_path and os.path.exists(file_path):
                            try:
                                with open(file_path, "rb") as f:
                                    file_bytes = f.read()
                                st.download_button(
                                    label="تحميل المذكرة",
                                    data=file_bytes,
                                    file_name=row['file_name'],
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
