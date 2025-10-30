import streamlit as st
import google.generativeai as genai
import pymupdf
import time
import json

# =============================
# App Configuration
# =============================
st.set_page_config(
    page_title="Công cụ Đọc Hiểu Sách - V2",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================
# Custom CSS Styling
# =============================
CUSTOM_CSS = """
<style>
/* Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=Poppins:wght@300;400;600;700&display=swap');

:root {
  --bg-gradient: linear-gradient(120deg, #0f172a 0%, #1e293b 35%, #0ea5e9 100%);
  --panel-bg: rgba(16, 24, 40, 0.7);
  --card-bg: rgba(2, 6, 23, 0.6);
  --accent: #38bdf8;
  --accent-2: #22d3ee;
  --text: #e2e8f0;
  --muted: #94a3b8;
  --success: #10b981;
  --warning: #f59e0b;
  --danger: #ef4444;
}

/* Global */
html, body, [data-testid="stAppViewContainer"] {
  background: var(--bg-gradient) !important;
  color: var(--text) !important;
  font-family: 'Inter', 'Poppins', system-ui, -apple-system, Segoe UI, Roboto, sans-serif !important;
}

/* App container glass effect */
[data-testid="stAppViewContainer"] > .main {
  backdrop-filter: blur(8px);
}

/* Header Title */
h1, h2, h3 {
  color: #e6f1ff !important;
  letter-spacing: 0.3px;
}

/* Fancy Title */
.app-title {
  font-size: 2.2rem;
  font-weight: 800;
  padding: 18px 24px;
  border-radius: 16px;
  background: linear-gradient(120deg, rgba(56, 189, 248, 0.15), rgba(34, 211, 238, 0.1));
  color: #e6f1ff;
  box-shadow: 0 10px 24px rgba(2, 132, 199, 0.25), inset 0 0 0 1px rgba(56,189,248,0.25);
  display: inline-flex;
  align-items: center;
  gap: 12px;
}

.app-title .badge {
  font-size: 0.9rem;
  font-weight: 700;
  padding: 6px 10px;
  border-radius: 12px;
  background: linear-gradient(120deg, #06b6d4, #3b82f6);
  color: white;
}

/* Sidebar */
section[data-testid="stSidebar"] > div {
  background: var(--panel-bg) !important;
  border-right: 1px solid rgba(148, 163, 184, 0.12);
}

/* Cards */
.card {
  background: var(--card-bg);
  border: 1px solid rgba(148, 163, 184, 0.15);
  border-radius: 16px;
  padding: 18px 18px;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.55);
}

/* Buttons */
button[kind="primary"], .stButton > button {
  background: linear-gradient(120deg, #06b6d4, #3b82f6);
  border: none;
  color: white;
  font-weight: 700;
  letter-spacing: .2px;
  padding: 10px 18px;
  border-radius: 12px;
  transition: transform 0.1s ease, box-shadow 0.2s ease;
  box-shadow: 0 8px 18px rgba(59, 130, 246, 0.35);
}

.stButton > button:hover { transform: translateY(-1px); }
.stButton > button:active { transform: translateY(0); box-shadow: none; }

/* File Uploader */
[data-testid="stFileUploader"] {
  border: 1px dashed rgba(148, 163, 184, 0.25);
  background: rgba(2, 6, 23, 0.45);
  border-radius: 16px;
}

/* Pills */
.pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 999px;
  border: 1px solid rgba(148,163,184,0.25);
  background: rgba(2,6,23,0.45);
  color: var(--text);
}

/* Animations */
@keyframes floatIn {
  from { transform: translateY(8px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.fadeIn { animation: floatIn 500ms ease forwards; }

/* Metrics */
.metric {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 6px 12px;
  padding: 12px 16px;
  border-radius: 12px;
  background: rgba(2,6,23,0.5);
  border: 1px solid rgba(56,189,248,0.2);
}
.metric .label { color: var(--muted); font-size: 0.9rem; }
.metric .value { font-size: 1.1rem; font-weight: 700; color: #e6f1ff; }

hr { border-color: rgba(148, 163, 184, 0.2) !important; }
.small { color: var(--muted); font-size: 0.9rem; }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# =============================
# Header
# =============================
st.markdown(
    """
    <div class="app-title fadeIn">📚 Công Cụ Kiểm Tra Đọc Hiểu Sách <span class="badge">V2</span></div>
    """,
    unsafe_allow_html=True,
)

st.markdown("Upload file PDF và AI sẽ tạo câu hỏi kiểm tra mức độ hiểu của bạn!", help="Hỗ trợ PDF tiếng Việt & Anh, tối đa ~30 trang gợi ý.")

# =============================
# Sidebar Settings
# =============================
with st.sidebar:
    st.header("⚙️ Cài Đặt")
    api_key = st.text_input("Google Gemini API Key", type="password", help="Dùng key miễn phí từ makersuite.google.com")

    if api_key:
        genai.configure(api_key=api_key)
        st.success("✅ API Key đã được cấu hình!")

    st.markdown("---")
    st.info("💡 Mỗi lần sinh câu hỏi sẽ đợi 60 giây để tránh vượt quota API miễn phí.")

    st.markdown("---")
    st.subheader("Tùy chọn sinh câu hỏi")
    c1, c2 = st.columns(2)
    with c1:
        num_questions = st.slider("Số câu hỏi", 1, 10, 5)
    with c2:
        difficulty = st.selectbox("Độ khó", ["easy", "medium", "hard"], index=1)

# =============================
# Utils
# =============================
@st.cache_data(show_spinner=False)
def read_pdf(uploaded_file):
    text = ""
    pdf_document = pymupdf.open(stream=uploaded_file.read(), filetype="pdf")

    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        text += page.get_text()
    pdf_document.close()

    return text


def generate_questions_real(text_content, num_questions=3, difficulty="medium"):
    prompt = (
        "Dựa vào nội dung sau, hãy tạo " + str(num_questions) + " câu hỏi trắc nghiệm mức độ " + difficulty + ".\n\n"
    )
    prompt += "Nội dung:\n" + text_content[:4000] + "\n\n"
    prompt += "Yêu cầu:\n"
    prompt += "- Tạo CHÍNH XÁC " + str(num_questions) + " câu hỏi trắc nghiệm\n"
    prompt += "- Mỗi câu có 4 đáp án (A, B, C, D)\n"
    prompt += "- Mức độ: " + difficulty + "\n"
    prompt += "- Trả về CHÍNH XÁC format JSON này (KHÔNG thêm text khác):\n"
    prompt += json.dumps(
        {
            "questions": [
                {
                    "question": "string",
                    "options": ["A", "B", "C", "D"],
                    "answer": "A",
                    "explanation": "string"
                }
            ]
        },
        ensure_ascii=False,
        indent=2,
    )

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)

    try:
        parsed = json.loads(response.text)
    except Exception:
        # Fallback: attempt to extract JSON
        start = response.text.find("{")
        end = response.text.rfind("}") + 1
        parsed = json.loads(response.text[start:end])

    return parsed


# =============================
# Main UI
# =============================
with st.container():
    st.markdown("### 📥 Tải lên tài liệu PDF", help="Kéo thả file PDF vào đây")
    uploader = st.file_uploader("Chọn file PDF", type=["pdf"], label_visibility="collapsed")

    if uploader is not None:
        with st.spinner("Đang đọc nội dung PDF..."):
            text_content = read_pdf(uploader)

        st.success("✅ Đã đọc xong tài liệu!")
        st.markdown("#### 👇 Tùy chọn")
        pill1, pill2, pill3 = st.columns(3)
        with pill1:
            st.markdown(f"<div class='pill'>📄 <b>Số trang:</b> {len(text_content)//1800 + 1}</div>", unsafe_allow_html=True)
        with pill2:
            st.markdown(f"<div class='pill'>🔠 <b>Độ dài:</b> {len(text_content):,} ký tự</div>", unsafe_allow_html=True)
        with pill3:
            st.markdown(f"<div class='pill'>⚙️ <b>Mức độ:</b> {difficulty.title()}</div>", unsafe_allow_html=True)

        st.markdown("---")

        left, right = st.columns([1, 1])
        with left:
            st.markdown("#### 🎯 Sinh câu hỏi trắc nghiệm")
            if st.button("🚀 Tạo câu hỏi với Gemini"):
                if not api_key:
                    st.error("❌ Vui lòng nhập API Key ở thanh bên trái.")
                else:
                    with st.spinner("AI đang tạo câu hỏi... Vui lòng chờ ~60 giây"):
                        time.sleep(1)
                        data = generate_questions_real(text_content, num_questions=num_questions, difficulty=difficulty)

                    st.success("✅ Hoàn tất! Dưới đây là câu hỏi")
                    st.markdown("#### 📝 Kết quả")
                    with st.container(border=True):
                        for i, q in enumerate(data.get("questions", [])[:num_questions], start=1):
                            st.markdown(f"**Câu {i}. {q.get('question','')}**")
                            opts = q.get("options", [])
                            for j, label in enumerate(["A", "B", "C", "D"]):
                                if j < len(opts):
                                    st.markdown(f"- {label}. {opts[j]}")
                            st.markdown(f"✅ Đáp án đúng: **{q.get('answer','')}**")
                            if q.get("explanation"):
                                st.markdown(f"<span class='small'>Giải thích: {q['explanation']}</span>", unsafe_allow_html=True)
                            st.markdown("<hr />", unsafe_allow_html=True)
        with right:
            st.markdown("#### 🔎 Xem nhanh nội dung đã đọc")
            with st.container(border=True):
                st.text_area("", value=text_content[:2500], height=420, label_visibility="collapsed")

    else:
        st.markdown(
            """
            <div class="card fadeIn">
                <h3>Chào mừng bạn! 👋</h3>
                <p>Hãy tải lên file PDF của bạn để bắt đầu tạo bài kiểm tra trắc nghiệm dựa trên nội dung tài liệu. Ứng dụng hỗ trợ tiếng Việt và tiếng Anh.</p>
                <ul>
                    <li>Dùng API Key của bạn từ Google AI Studio</li>
                    <li>Tùy chọn số câu hỏi và độ khó</li>
                    <li>Giao diện hiện đại, hỗ trợ thiết bị di động</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
</textarea>
