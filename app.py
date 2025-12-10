import streamlit as st
from pypdf import PdfReader
import docx
import textwrap

# ==============================
# إعداد الصفحة + CSS
# ==============================
st.set_page_config(
    page_title="مساعد علّمني لمراجعة الحقائب التدريبية (بدون API)",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
html, body, [class*="css"] {
    font-family: "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
}

/* حاوية المحتوى */
.main .block-container {
    padding-top: 1.2rem;
    padding-bottom: 2.2rem;
    padding-left: 2.5rem;
    padding-right: 2.5rem;
    background: #f3f4f6;
    border-radius: 24px;
}

/* ترويسة */
.header-card {
    background: linear-gradient(135deg, #1d4ed8, #1e40af);
    color: #f9fafb;
    padding: 1.4rem 1.8rem;
    border-radius: 18px;
    box-shadow: 0 16px 34px rgba(15, 23, 42, 0.35);
    margin-bottom: 1.2rem;
}
.header-title {
    font-size: 1.7rem;
    font-weight: 800;
    margin-bottom: 0.25rem;
}
.header-subtitle {
    font-size: 0.96rem;
    opacity: 0.95;
}

/* كارت رئيسي */
.card {
    background: #ffffff;
    border-radius: 18px;
    padding: 1.2rem 1.3rem;
    box-shadow: 0 10px 25px rgba(15, 23, 42, 0.07);
    border: 1px solid rgba(148, 163, 184, 0.25);
    margin-bottom: 1rem;
}

/* عنونة صغيرة */
.section-label {
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #6b7280;
    margin-bottom: 0.05rem;
}

/* نص مساعدة */
.help-text {
    font-size: 0.78rem;
    color: #6b7280;
}

/* Textarea */
textarea, .stTextArea textarea {
    border-radius: 12px !important;
}

/* سايدبار */
[data-testid="stSidebar"] {
    background: #0b1120 !important;
}
.sidebar-title {
    font-size: 1.1rem;
    font-weight: 800;
    color: #e5e7eb;
    margin-bottom: 0.3rem;
}
.sidebar-subtitle {
    font-size: 0.85rem;
    color: #9ca3af;
    margin-bottom: 0.9rem;
}
.sidebar-footer {
    font-size: 0.75rem;
    color: #6b7280;
    margin-top: 1rem;
}

/* أزرار */
.stButton > button {
    border-radius: 999px !important;
    padding: 0.6rem 1.4rem !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    border: none !important;
    cursor: pointer !important;
    transition: 0.2s ease-in-out !important;
}
.primary-btn button {
    background-color: #2563eb !important;
    color: #ffffff !important;
    box-shadow: 0 6px 16px rgba(37, 99, 235, 0.45) !important;
}
.primary-btn button:hover {
    background-color: #1e40af !important;
    transform: translateY(-2px) !important;
}
.secondary-btn button {
    background-color: #e5e7eb !important;
    color: #111827 !important;
}
.secondary-btn button:hover {
    background-color: #d1d5db !important;
    transform: translateY(-2px) !important;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ==============================
# سايدبار
# ==============================
with st.sidebar:
    st.markdown('<div class="sidebar-title">مؤسسة علّمني للتعليم والتدريب</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sidebar-subtitle">'
        'منصة تفاعلية لمراجعة الحقائب التدريبية وفق إطار جودة تربوي معتمد – بدون استخدام أي API مدفوع.'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown(
        '<div class="sidebar-footer">الإصدار 1.0 – للاستخدام الداخلي داخل فرق علّمني التصميمية والتدريبية.</div>',
        unsafe_allow_html=True,
    )

# ==============================
# ترويسة
# ==============================
st.markdown(
    """
    <div class="header-card">
        <div class="header-title">🎓 مساعد علّمني لمراجعة وتقييم الحقائب التدريبية (بدون API)</div>
        <div class="header-subtitle">
            ارفع الحقيبة التدريبية بنسختها الكاملة، استخرج النص تلقائيًا، ثم قيِّم الحقيبة تفاعليًا
            عبر نموذج معايير جودة منظم، لتحصل في النهاية على تقرير نصي مهني جاهز للنسخ أو الحفظ.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ==============================
# دوال قراءة الملفات
# ==============================
def read_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""
    for i, page in enumerate(reader.pages, start=1):
        try:
            page_text = page.extract_text() or ""
        except Exception:
            page_text = ""
        text += f"\n\n----- صفحة {i} -----\n\n{page_text}"
    return text.strip(), len(reader.pages)


def read_docx(uploaded_file):
    document = docx.Document(uploaded_file)
    paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
    text = "\n".join(paragraphs).strip()
    # تقدير عدد الصفحات (تقريبي) على أساس 600 كلمة للصفحة
    words = len(text.split())
    pages_est = max(1, words // 600)
    return text, pages_est


if "manual_text" not in st.session_state:
    st.session_state["manual_text"] = ""
if "manual_stats" not in st.session_state:
    st.session_state["manual_stats"] = {}

# ==============================
# كارت رفع الحقيبة
# ==============================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-label">Upload</div>', unsafe_allow_html=True)
st.markdown("### 📁 رفع الحقيبة واستخراج النص")

uploaded_file = st.file_uploader(
    "اختر ملف الحقيبة التدريبية (PDF أو DOCX)",
    type=["pdf", "docx"],
    help="يمكنك رفع الحقيبة كاملة حتى لو كانت 200 صفحة أو أكثر.",
)

col_u1, col_u2 = st.columns([0.5, 0.5])
with col_u1:
    st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
    extract_btn = st.button("📥 استخراج النص من الحقيبة / تحديثه")
    st.markdown("</div>", unsafe_allow_html=True)

with col_u2:
    show_text = st.checkbox("عرض النص المستخرج لمراجعته", value=False)

if extract_btn:
    if uploaded_file is None:
        st.warning("من فضلك ارفع ملف الحقيبة أولًا.")
    else:
        try:
            if uploaded_file.name.lower().endswith(".pdf"):
                text, pages = read_pdf(uploaded_file)
            else:
                text, pages = read_docx(uploaded_file)

            st.session_state["manual_text"] = text
            words = len(text.split())
            st.session_state["manual_stats"] = {
                "pages": pages,
                "words": words,
            }
            st.success(f"تم استخراج النص بنجاح. عدد الصفحات التقريبي: {pages} – عدد الكلمات: {words:,}")
        except Exception as e:
            st.error(f"حدث خطأ أثناء قراءة الملف: {e}")

if show_text:
    st.markdown("#### 📄 النص المستخرج من الحقيبة")
    st.text_area(
        "",
        value=st.session_state["manual_text"],
        height=220,
        key="manual_text_area",
        help="يمكنك تعديل النص يدويًا إذا رغبت، لكن التقييم التفاعلي لا يعتمد على الذكاء الاصطناعي.",
    )
    # نحدّث النسخة الداخلية لو المستخدم غيّر في النص
    st.session_state["manual_text"] = st.session_state["manual_text_area"]

if st.session_state["manual_stats"]:
    stats = st.session_state["manual_stats"]
    st.markdown("#### 📊 لمحة سريعة عن الحقيبة")
    st.write(f"- عدد الصفحات (فعلي/تقديري): **{stats['pages']} صفحة**")
    st.write(f"- عدد الكلمات: **{stats['words']:,} كلمة تقريبًا**")

st.markdown("</div>", unsafe_allow_html=True)

# ==============================
# نموذج التقييم (بدون AI)
# ==============================

# تعريف المجالات والمؤشرات الكبرى (دمجنا البنود التفصيلية داخل مؤشرات رئيسية)
DOMAINS = {
    "المجال الأول: الأهداف": [
        "وجود هدف عام واضح يعكس احتياجات المتدربين.",
        "توافر نواتج تعلم مصاغة بطريقة سلوكية قابلة للقياس.",
        "تنوع نواتج التعلم (معرفية – مهارية – وجدانية) وتتابعها المنطقي.",
    ],
    "المجال الثاني: المحتوى": [
        "ارتباط موضوعات المحتوى بالهدف العام ونواتج التعلم.",
        "ملاءمة المحتوى لخصائص المتدربين وبيئة عملهم وخلوه من التمييز.",
        "تنظيم المحتوى (تدرج، عدم تكرار، حداثة، تكامل بين النظرية والتطبيق).",
    ],
    "المجال الثالث: الأنشطة والأساليب والوسائل التدريبية": [
        "تنوع الأنشطة وارتباطها بنواتج التعلم وتدرجها.",
        "مراعاة الأنشطة لخبرات المتدربين وخصائص تعلم الكبار.",
        "تنوع الأساليب والوسائل التدريبية وملاءمتها للأهداف والمحتوى والمتدربين.",
    ],
    "المجال الرابع: المادة التدريبية": [
        "وجود دليل مدرب ودليل متدرب منظمين (مقدمة، فهرس، أجندة، أنشطة...).",
        "توافر مادة مرجعية وأوراق عمل وعروض تقديمية وأدوات تقييم مرتبطة بالبرنامج.",
        "سلامة اللغة والإخراج الفني (تصميم الغلاف، تنسيق الخطوط، الأشكال التوضيحية...).",
    ],
    "المجال الخامس: التقويم": [
        "وجود تقويم قبلي، بنائي، ونهائي لقياس تحقق الأهداف.",
        "تنوع أدوات التقييم (اختبارات، ملاحظة، استبيانات، تقويم منتجات المتدربين).",
        "وضوح آلية حساب فاعلية البرنامج (أو على الأقل وجود تصور لقياس الأثر).",
    ],
}

SCORES_LABELS = {
    0: "0 – غير متوفر",
    1: "1 – متوفر بدرجة ضعيفة",
    2: "2 – متوفر بدرجة متوسطة",
    3: "3 – متوفر بدرجة عالية",
}

if "ratings" not in st.session_state:
    st.session_state["ratings"] = {}

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-label">Interactive review</div>', unsafe_allow_html=True)
st.markdown("### 📝 التقييم التفاعلي للحقيبة (بدون ذكاء اصطناعي)")

st.markdown(
    '<div class="help-text">اختر درجة لكل مؤشر، وأضف ملاحظاتك. الأداة ستقوم بتجميع تقرير نصي نهائي بناءً على اختياراتك.</div>',
    unsafe_allow_html=True,
)

tabs = st.tabs(list(DOMAINS.keys()))

for tab, (domain_name, indicators) in zip(tabs, DOMAINS.items()):
    with tab:
        st.subheader(domain_name)
        for idx, indicator in enumerate(indicators):
            key_prefix = f"{domain_name}_{idx}"
            cols = st.columns([0.6, 0.4])
            with cols[0]:
                st.markdown(f"**• {indicator}**")
            with cols[1]:
                score = st.selectbox(
                    "الدرجة",
                    options=list(SCORES_LABELS.keys()),
                    format_func=lambda x: SCORES_LABELS[x],
                    key=f"score_{key_prefix}",
                )
            comment = st.text_area(
                "ملاحظات / أمثلة من الحقيبة (يمكن ذكر أرقام الصفحات)",
                key=f"comment_{key_prefix}",
                height=70,
            )
            st.session_state["ratings"][key_prefix] = {
                "domain": domain_name,
                "indicator": indicator,
                "score": score,
                "comment": comment,
            }
            st.markdown("---")

st.markdown("</div>", unsafe_allow_html=True)

# ==============================
# توليد تقرير نصي من التقييم اليدوي
# ==============================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-label">Report</div>', unsafe_allow_html=True)
st.markdown("### 📑 توليد تقرير التقييم النهائي (من اختياراتك)")

col_r1, col_r2 = st.columns([0.4, 0.6])
with col_r1:
    st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
    generate_report_btn = st.button("📄 توليد التقرير النصي")
    st.markdown("</div>", unsafe_allow_html=True)

with col_r2:
    st.markdown(
        '<div class="help-text">سيتم استخدام الدرجات والملاحظات التي أدخلتها لكل مجال ومؤشر لبناء تقرير واحد منسق يمكنك نسخه إلى ملف Word أو PDF.</div>',
        unsafe_allow_html=True,
    )

report_area = st.empty()

def build_text_report():
    ratings = st.session_state.get("ratings", {})
    if not ratings:
        return "لم يتم إدخال أي تقييمات بعد."

    # حساب متوسط درجة كل مجال
    domain_scores = {}
    domain_indicators = {}
    for item in ratings.values():
        d = item["domain"]
        domain_scores.setdefault(d, []).append(item["score"])
        domain_indicators.setdefault(d, []).append(item)

    lines = []
    lines.append("تقرير مراجعة الحقيبة التدريبية")
    lines.append("================================")
    stats = st.session_state.get("manual_stats", {})
    if stats:
        lines.append(f"- عدد الصفحات (فعلي/تقديري): {stats.get('pages', 'غير محدد')}")
        lines.append(f"- عدد الكلمات التقريبية: {stats.get('words', 'غير محدد')}")
    lines.append("")

    # ملخص تنفيذي بسيط
    lines.append("أولًا: ملخص تنفيذي عن جودة الحقيبة")
    for domain, scores in domain_scores.items():
        avg = sum(scores) / len(scores)
        lines.append(f"- {domain}: متوسط الدرجة = {avg:.2f} من 3")
    lines.append("")

    # تفاصيل كل مجال
    for domain, items in domain_indicators.items():
        lines.append("")
        lines.append(f"ثانيًا: {domain}")
        for item in items:
            score_label = SCORES_LABELS[item['score']]
            lines.append(f"• المؤشر: {item['indicator']}")
            lines.append(f"  - الدرجة: {score_label}")
            comment = item["comment"].strip()
            if comment:
                wrapped = textwrap.wrap(comment, width=90)
                lines.append("  - ملاحظات المقيم:")
                for w in wrapped:
                    lines.append("    " + w)
            else:
                lines.append("  - ملاحظات المقيم: (لم تُسجل ملاحظات)")
            lines.append("")

    return "\n".join(lines)

if generate_report_btn:
    report_text = build_text_report()
    report_area.markdown("#### 🧾 نص التقرير النهائي (يمكنك نسخه كما هو)")
    report_area.text_area(
        "",
        value=report_text,
        height=350,
    )

st.markdown("</div>", unsafe_allow_html=True)
