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
PASSWORDS = {
    "طالب": {
        "student1": "pass123",
        "student2": "pass456",
        "student3": "pass789"
    },
    "مشرف": {
        BELLOULA;SALIMA;salima.belloula;Qr8$kL2pT9wA
KERBOUAI;Imane;imane.kerbouai;Nf4@vR7xZ1qS
NASRI;Meriem;meriem.nasri;Sb7%pM3kH8uY
GUISSOUS;Mokhtar;mokhtar.guissous;Vt6#bC9rQ2eW
BELKASMI;FARIDA;farida.belkasmi;Lp3$gT8nS5yZ
BOURAHLA;AMEL;amel.bourahla;Yz9@hF2mV6kP
CHOURGHAL;Nacira;nacira.chourghal;Hx2#rQ7tB4nM
FELLAHI;ZINE EL ABIDINE;zine_el_abidine.fellahi;Rm5%kL1wV8sD
BOULKROUNE;Hasna;hasna.boulkroune;Ct4$gN9pR2zF
TABTI;Dahbia;dahbia.tabti;Pw8#dM6sK1yQ
SAIAD;AMIRA;amira.saiad;Uz3%vB7nL5cH
KERMICHE;SIHEM;sihem.kermiche;Kb9@tF2rQ6wX
ZAAFOUR;Mohamed djalil;mohamed_djalil.zaafour;Md6#pS8vR3yL
Mebarki;Radia;radia.mebarki;Rf2$kH7nT9wG
AIT MECHEDAL;MOULOUD;mouloud.ait_mechedal;Qy7%vB3mL8sA
MEZITI;ASMA;asma.meziti;Jp4#rK9tV2hZ
Sebbane;Mahieddine;mahieddine.sebbane;Nt8$gM1pQ6wS
HAMMA;AMEL;amel.hamma;Lb3%vF7kR9zX
SAIFI;Mounir;mounir.saifi;Vz5#pT2nL8qH
IRATNI;Nadjat;nadjat.iratni;Gy9$kR4mS1wP
SEMARA;Lounis;lounis.semara;Hp2%vB8tQ6nM
BAHLOULI;Faycal;faycal.bahlouli;Kw7#rM3pV9sD
BAKHOUCHE;Imene;imene.bakhouche;Sa4$gT8nL1yF
DEFFAF;Ammar;ammar.deffaf;Pd6%kH2rQ7wN
BOUMAIZA;Souad;souad.boumaiza;Rx3#vM9pT5zL
BENTABET;Abdelouahab;abdelouahab.bentabet;Vz1$kP7nL4qS
MEZDOUR;Hichem;hichem.mezdour;Mb8%rT3vK9yH
BENSEGHIR;HADJIRA;hadjira.benseghir;Qf2#pL6nS7wZ
BENBOUGUERRA;Nawel;nawel.benbouguerra;Lc9$gM1rV8tP
BECHAMI;Sofiane;sofiane.bechami;Hz4%vK7pN2qM
MAHLEB;ANISSA;anissa.mahleb;Yp6#rT3mL8wS
SOUAGUI;YASMINA;yasmina.souagui;Nx9$kB2pV7rD
ZIAD;Abdelaziz;abdelaziz.ziad;Gt3%vM8nL1qP
Loukil;Bachir;bachir.loukil;Rb7#pK4tS9wZ
TEKKOUK;Fatiha;fatiha.tekkouk;Pd2$gM6nL8yH
Ferahtia ;Amel;amel.ferahtia;Qm8%rT1pV3sK
loucif;lynda;lynda.loucif;Sx4#kB9vM2qL
TOUATI;NOUREDDINE;noureddine.touati;Hz7$pR3mT6wN
HIHAT;Soraya;soraya.hihat;Ly1%vK8nP4qS
BOUSSAHEL;SOULEF;soulef.boussahel;Vb9#rM2tK7wD
TABTI;SALIMA;salima.tabti;Pw3$kL8nV6yR
BIBAK;MOHAMED;mohamed.bibak;Ng5%vT1pR9sZ
BOUGUERRA;Asma;asma.bouguerra;Fc2#pK7mL8wY
LAZAZGA;Abdellali;abdellali.lazazga;Qz6$gR3nT1vM
BENRADIA;HAMIDA;hamida.benradia;Rt9%kL4pS2wH
DIAFAT;Abdelouahab;abdelouahab.diafat;Mb3#vT8nK7qP
MAAMRI;KHELIFA;khelifa.maamri;Ld1$gP6nR9wS
DEHIRI;MOUNIRA;mounira.dehiri;Sh8%rK2vM4qZ
TIAIBA;Mohamed;mohamed.tiaiba;Py5#kT9nL3wV
GUERGOUR;HASSINA;hassina.guergour;Nq2%vR7pK8sM
SALAMANI;Amel;amel.salamani;Kb9#pL1vT6wD
SEDRATI;Tahar;tahar.sedrati;Vz4$gM8nP3qS
SADRATI;NOUARI;nouari.sadrati;Fy7%rK2pL9wH
KHOUDOUR;Abdelmalek;abdelmalek.khoudour;Qd3#vT6nR8yP
KELALECHE;HIZIA;hizia.kelaleche;Rm1%kP7nL4wS
ALILI;DAHMANE;dahmane.alili;Tb8#vK2rM5qZ
REGOUI;CHELBIA;chelbia.regoui;Lc6$gR3pT9wN
BELALMI;NOR EL HOUDA;nor_el_houda.belalmi;Sa2%vK8nP7qM
BOUBELLOUTA;Tahar;tahar.boubellouta;Hz9#pL4mT1wD
BOUTANA;Wissem;wissem.boutana;Qp3%kR7nV8yS
ZIOUCHE;SIHEM;sihem.ziouche;Mb6#vT1pL9qZ
ABED;Hanane;hanane.abed;Rx8$gK2nP4wM
FATMI;WIDAD;widad.fatmi;Ly5%rM9pT1qS
MERZOUKI;YOUCEF;youcef.merzouki;Nz7#kV3pL6wD
BELHADJ;Mohamed Tayeb;mohamed_tayeb.belhadj;Gq2%vR8nM4pS
SAYAH;TAHAR;tahar.sayah;Pf9#kT1vL6wZ
ROUAIGUIA;NADIA;nadia.rouaiguia;Sd3%gM7pK2qH
FORTAS;Bilal;bilal.fortas;Qw6#rL9nT1yP
AMARA KORBA;RAOUF;raouf.amara_korba;Vz1%pK8mR4wS
BOUMERFEG;Sabah;sabah.boumerfeg;Lk7#vT2pN9qD
BENSOUILAH;TAKIYEDDINE;takiyeddine.bensouilah;My4%gR8nL1pS
BOULAOUAD;Belkacem aymen;belkacem_aymen.boulaouad;Np9#kT3vL6wZ
TAMINE;Milouda;milouda.tamine;Rb2%vM7pK8qS
MOUMENI;OUISSEM;ouissem.moumeni;Hx5#rL1nT9wD
ZERROUG;AMINA;amina.zerroug;Qn8%kP3vM6yS
BENBOUGUERRA;Khalissa;khalissa.benbouguerra;Sz4#gR9nL1pD
BOUZID;Chawki abdallah;chawki_abdallah.bouzid;Vb7%kT2pM8wQ
BELGUERRI;Hemza;hemza.belguerri;Lf3#vR6nK9pS
LAOUFI;HADJER;hadjer.laoufi;Py1%gM8nL4qZ
CHENOUF;NADIA SAFIA;nadia_safia.chenouf;Mw9#rT3pK6wD
DERARDJA;Abdelghani;abdelghani.derardja;Hz2%kL7nV5qS
HARIZI;Toufik;toufik.harizi;Rb8#pM1vK4wZ
MOUTASSEM;Dahou;dahou.moutassem;Qs3%vT9nL6pH
MERIBAI;Abdelmaalek;abdelmaalek.meribai;Lp5#gR2kT8wS
BENSEFIA;Sofiane;sofiane.bensefia;Vz6%pM1nL9qD
MESSAI;Chafik redha;chafik_redha.messai;Ny4#kT7vR2wS
BAAZIZ;Naima;naima.baaziz;Gh9%rL3pK6wD
BENOUADAH;ZOHRA;zohra.benouadah;Px2#vM8nL4qS
BELLIK;Juba;juba.bellik;Rf7%kT1pM9wZ
MEKHALFI;Hamoudi;hamoudi.mekhalfi;Sd3#vR6nL8qP
SID;Nassim;nassim.sid;Qk8%pL2vM5wH
    }
}

name=app_passwords_snippet.py
# استبدل أو أدمج هذا القاموس مع PASSWORDS في app.py
PASSWORDS["مشرف"] = {
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
    "fatiha.tekkouk": "Pd2$gM6nL8yH",
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
ملاحظات مهمة:
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
