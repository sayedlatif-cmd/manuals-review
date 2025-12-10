import streamlit as st
from pypdf import PdfReader
import docx
import textwrap
from collections import defaultdict

# ==============================
# إعداد الصفحة + CSS
# ==============================
st.set_page_config(
    page_title="مساعد علّمني لمراجعة الحقائب التدريبية (تقييم تلقائي بدون API)",
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

/* كارت */
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
        'تقييم تلقائي للحقائب التدريبية باستخدام قواعد تحليل نصية داخلية، بدون أي API خارجي أو كلفة مالية.'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown(
        '<div class="sidebar-footer">الإصدار 1.0 – نموذج أولي للتقييم الآلي وفق إطار جودة علّمني.</div>',
        unsafe_allow_html=True,
    )

# ==============================
# ترويسة
# ==============================
st.markdown(
    """
    <div class="header-card">
        <div class="header-title">🎓 مساعد علّمني – تقييم تلقائي للحقائب التدريبية (بدون API)</div>
        <div class="header-subtitle">
            ارفع الحقيبة التدريبية كاملة، وسيقوم النظام بتحليل النص تلقائيًا
            والبحث عن مؤشرات الجودة في جميع الصفحات، ثم يصدر تقريرًا تفاعليًا
            يوضح الدرجات لكل مجال ونقاط القوة والفجوات مع أمثلة من الحقيبة.
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
    words = len(text.split())
    pages_est = max(1, words // 600)
    # نضيف فواصل صفحات تقديرية
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
    show_text = st.checkbox("عرض النص المستخرج لمراجعته (اختياري)", value=False)

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
            st.success(f"تم استخراج النص بنجاح. عدد الصفحات (فعلي/تقديري): {pages} – عدد الكلمات: {words:,}")
        except Exception as e:
            st.error(f"حدث خطأ أثناء قراءة الملف: {e}")

if show_text and st.session_state["manual_text"]:
    st.markdown("#### 📄 النص المستخرج من الحقيبة")
    st.text_area(
        "",
        value=st.session_state["manual_text"],
        height=220,
        key="manual_text_area",
        help="يمكنك تعديل النص يدويًا إذا رغبت.",
    )
    st.session_state["manual_text"] = st.session_state["manual_text_area"]

if st.session_state["manual_stats"]:
    stats = st.session_state["manual_stats"]
    st.markdown("#### 📊 لمحة سريعة عن الحقيبة")
    st.write(f"- عدد الصفحات (فعلي/تقديري): **{stats['pages']} صفحة**")
    st.write(f"- عدد الكلمات: **{stats['words']:,} كلمة تقريبًا**")

st.markdown("</div>", unsafe_allow_html=True)

# ==============================
# معايير التقييم القاعدية (Rule-based)
# ==============================

# لكل مؤشر: كلمات مفتاحية وأحيانًا تعبيرات بسيطة
INDICATORS = [
    {
        "domain": "المجال الأول: الأهداف",
        "title": "وجود هدف عام واضح يعبر عما يسعى البرنامج إلى تحقيقه",
        "keywords": ["الهدف العام", "يهدف البرنامج", "يهدف هذا البرنامج", "الهدف الرئيس"],
    },
    {
        "domain": "المجال الأول: الأهداف",
        "title": "توافر نواتج تعلم مصاغة سلوكيًا وقابلة للقياس",
        "keywords": ["نواتج التعلم", "بنهاية هذه الدورة", "بنهاية هذا البرنامج", "يتوقع أن يكون المتدرب قادرا على"],
    },
    {
        "domain": "المجال الأول: الأهداف",
        "title": "تنوع نواتج التعلم (معرفية – مهارية – وجدانية)",
        "keywords": ["معرفية", "مهارية", "وجدانية", "مهارات", "اتجاهات"],
    },
    {
        "domain": "المجال الثاني: المحتوى",
        "title": "ارتباط موضوعات المحتوى بالهدف العام ونواتج التعلم",
        "keywords": ["محاور البرنامج", "موضوعات الحقيبة", "محتوى البرنامج", "وحدات التدريب"],
    },
    {
        "domain": "المجال الثاني: المحتوى",
        "title": "ملاءمة المحتوى لخصائص المتدربين وبيئة عملهم",
        "keywords": ["الفئة المستهدفة", "خصائص المتدربين", "بيئة العمل", "احتياجات التدريب"],
    },
    {
        "domain": "المجال الثاني: المحتوى",
        "title": "تنظيم المحتوى وتدرجه وحداثته",
        "keywords": ["يتدرج من", "مقدمة", "خاتمة", "أحدث الاتجاهات", "مستجدات", "محاور متسلسلة"],
    },
    {
        "domain": "المجال الثالث: الأنشطة والأساليب والوسائل التدريبية",
        "title": "تنوع الأنشطة التدريبية وارتباطها بالأهداف",
        "keywords": ["نشاط", "أنشطة", "تدريب عملي", "تمرين", "ورشة عمل"],
    },
    {
        "domain": "المجال الثالث: الأنشطة والأساليب والوسائل التدريبية",
        "title": "مراعاة الأنشطة لخبرات المتدربين وتعليم الكبار",
        "keywords": ["تعليم الكبار", "خبرات المتدربين", "مواقف حياتية", "تجارب المتدربين"],
    },
    {
        "domain": "المجال الثالث: الأنشطة والأساليب والوسائل التدريبية",
        "title": "تنوع أساليب ووسائل التدريب واستخدام عروض وأوراق عمل",
        "keywords": ["محاضرة قصيرة", "مناقشة", "عصف ذهني", "لعب أدوار", "عمل تعاوني", "أوراق عمل", "عرض تقديمي"],
    },
    {
        "domain": "المجال الرابع: المادة التدريبية",
        "title": "وجود دليل مدرب منظم (مقدمة، فهرس، أجندة، إرشادات)",
        "keywords": ["دليل المدرب", "إرشادات للمدرب", "أجندة العمل", "فهرس المحتويات"],
    },
    {
        "domain": "المجال الرابع: المادة التدريبية",
        "title": "وجود دليل متدرب ومادة مرجعية وأوراق عمل",
        "keywords": ["دليل المتدرب", "المادة المرجعية", "مرجع", "مراجع إضافية"],
    },
    {
        "domain": "المجال الرابع: المادة التدريبية",
        "title": "سلامة اللغة والإخراج الفني والتصميم البصري",
        "keywords": ["أخطاء إملائية", "إخراج", "تصميم الغلاف", "هوامش", "تنسيق"],
    },
    {
        "domain": "المجال الخامس: التقويم",
        "title": "وجود تقويم قبلي وبنائي ونهائي",
        "keywords": ["اختبار قبلي", "اختبار بعدي", "تقويم بنائي", "تقييم قبلي", "تقييم نهائي"],
    },
    {
        "domain": "المجال الخامس: التقويم",
        "title": "تنوع أدوات التقييم (اختبارات، ملاحظة، استبيانات…) ",
        "keywords": ["اختبار", "استبانة", "استبيان", "بطاقة ملاحظة", "أداة تقييم"],
    },
    {
        "domain": "المجال الخامس: التقويم",
        "title": "الإشارة إلى قياس أثر البرنامج أو فاعليته",
        "keywords": ["قياس الأثر", "فاعلية البرنامج", "متابعة بعدية", "متابعة ميدانية"],
    },
]

SCORE_LABELS = {
    0: "0 – غير متوفر في النص",
    1: "1 – متوفر بدرجة ضعيفة (ذكر محدود أو عام جدًا)",
    2: "2 – متوفر بدرجة متوسطة (أكثر من إشارة ومواضع متفرقة)",
    3: "3 – متوفر بدرجة عالية وواضحة في أكثر من موضع",
}

# ==============================
# دوال التحليل القاعدي
# ==============================
def find_keyword_matches(text, keyword, window=80):
    """ترجع أمثلة مقتطفة حول الكلمة المفتاحية داخل النص."""
    matches = []
    start = 0
    while True:
        idx = text.find(keyword, start)
        if idx == -1:
            break
        snippet_start = max(0, idx - window // 2)
        snippet_end = min(len(text), idx + window // 2)
        snippet = text[snippet_start:snippet_end].replace("\n", " ")
        matches.append(snippet.strip())
        start = idx + len(keyword)
        if len(matches) >= 5:  # نكتفي بعدد معقول من الأمثلة
            break
    return matches


def score_indicator(text, indicator):
    """يعطي درجة 0–3 لكل مؤشر حسب عدد الكلمات المفتاحية والأمثلة."""
    text_norm = text  # ممكن لاحقا نضيف تنظيف (حذف تشكيل/مسافات...)
    total_matches = 0
    all_snippets = []

    for kw in indicator["keywords"]:
        snippets = find_keyword_matches(text_norm, kw)
        total_matches += len(snippets)
        all_snippets.extend([f"...{s}..." for s in snippets])

    if total_matches == 0:
        score = 0
    elif total_matches == 1:
        score = 1
    elif 2 <= total_matches <= 4:
        score = 2
    else:
        score = 3

    explanation_parts = []
    if total_matches == 0:
        explanation_parts.append("لم يتم العثور على عبارات واضحة تشير إلى هذا المؤشر في نص الحقيبة.")
    else:
        explanation_parts.append(f"تم العثور على حوالي {total_matches} موضع/مواضع تحتوي على عبارات مرتبطة بالمؤشر.")
        if score >= 2:
            explanation_parts.append("تتوزع هذه العبارات في أكثر من جزء من الحقيبة، مما يشير إلى حضور جيد لهذا المؤشر.")

    explanation = " ".join(explanation_parts)
    return {
        "score": score,
        "score_label": SCORE_LABELS[score],
        "matches_count": total_matches,
        "examples": all_snippets[:5],
        "explanation": explanation,
    }


def analyze_manual(text):
    """يحلل النص الكامل للحقيبة ويعيد بنية منظمة للتقرير."""
    domains = defaultdict(list)
    for ind in INDICATORS:
        result = score_indicator(text, ind)
        domains[ind["domain"]].append({
            "title": ind["title"],
            **result,
        })

    domain_summaries = []
    for domain_name, items in domains.items():
        scores = [it["score"] for it in items]
        avg = sum(scores) / len(scores) if scores else 0
        domain_summaries.append((domain_name, avg, items))

    # حساب متوسط كلي
    if domain_summaries:
        overall = sum(d[1] for d in domain_summaries) / len(domain_summaries)
    else:
        overall = 0.0

    # ملخص تنفيذي بسيط حسب الدرجة
    if overall >= 2.5:
        overall_msg = "الحقيبة تحقق معظم معايير الجودة بدرجة عالية، مع بعض فرص التحسين المحددة في المجالات المختلفة."
    elif overall >= 1.5:
        overall_msg = "الحقيبة متوسطة الجودة؛ يتوافر عدد من عناصر القوة، لكن توجد فجوات واضحة تحتاج إلى معالجة لتحسين الأهداف والمحتوى والأنشطة والتقويم."
    else:
        overall_msg = "الحقيبة تحتاج إلى تطوير جذري في عدة مجالات أساسية؛ كثير من مؤشرات الجودة إما غائبة أو ضعيفة الحضور في النص."

    return {
        "overall_score": overall,
        "overall_message": overall_msg,
        "domains": domain_summaries,
    }

# ==============================
# زر التحليل التلقائي والتقرير التفاعلي
# ==============================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-label">Auto review</div>', unsafe_allow_html=True)
st.markdown("### 🤖 تحليل تلقائي وإصدار تقرير تفاعلي")

st.markdown(
    '<div class="help-text">سيتم تحليل النص كاملًا باستخدام قواعد نصية ثابتة؛ نفس الحقيبة ستحصل دائمًا على نفس التقييم لضمان عدم التحيّز.</div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
analyze_btn = st.button("🚀 بدء التحليل التلقائي للحقيبة")
st.markdown("</div>", unsafe_allow_html=True)

report_container = st.container()

if analyze_btn:
    if not st.session_state["manual_text"].strip():
        st.warning("من فضلك ارفع الحقيبة واضغط على زر استخراج النص أولًا.")
    else:
        with st.spinner("⏳ جاري تحليل النص الكامل للحقيبة وفق معايير الجودة..."):
            analysis = analyze_manual(st.session_state["manual_text"])

        with report_container:
            # تبويبات للتقرير
            tab1, tab2 = st.tabs(["🔍 الملخص التنفيذي", "📊 التقييم التفصيلي حسب المجالات"])

            # ملخص
            with tab1:
                st.subheader("🔍 ملخص عام لجودة الحقيبة")
                st.write(analysis["overall_message"])
                st.markdown(f"**متوسط الدرجة الكلية:** {analysis['overall_score']:.2f} من 3")
                stats = st.session_state.get("manual_stats", {})
                if stats:
                    st.markdown("---")
                    st.markdown("**بيانات عن حجم الحقيبة:**")
                    st.write(f"- عدد الصفحات (فعلي/تقديري): {stats.get('pages', 'غير متاح')}")
                    st.write(f"- عدد الكلمات التقريبية: {stats.get('words', 'غير متاح')}")

            # المجالات
            with tab2:
                st.subheader("📊 التقييم التفصيلي للمجالات والمؤشرات")
                for domain_name, avg, items in analysis["domains"]:
                    with st.expander(f"{domain_name} – متوسط الدرجة: {avg:.2f} من 3", expanded=True):
                        for it in items:
                            st.markdown(f"### • {it['title']}")
                            st.markdown(f"- **الدرجة:** {it['score']} ({it['score_label']})")
                            st.markdown(f"- **تفسير آلي للدرجة:** {it['explanation']}")
                            if it["examples"]:
                                st.markdown("**📌 أمثلة من نص الحقيبة:**")
                                for ex in it["examples"]:
                                    wrapped = textwrap.fill(ex, width=90)
                                    st.markdown(f"> {wrapped}")
                            else:
                                st.markdown("**📌 أمثلة من نص الحقيبة:** لم يتم العثور على أمثلة صريحة لهذا المؤشر.")
                            st.markdown("---")

st.markdown("</div>", unsafe_allow_html=True)
