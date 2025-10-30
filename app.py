import streamlit as st
import google.generativeai as genai
import pymupdf
import time
import json

st.set_page_config(page_title="Công cụ Đọc Hiểu Sách", page_icon="📚", layout="wide")
st.title("📚 Công Cụ Kiểm Tra Đọc Hiểu Sách")
st.markdown("Upload file PDF và AI sẽ tạo câu hỏi kiểm tra mức độ hiểu của bạn!")

with st.sidebar:
    st.header("⚙️ Cài Đặt")
    api_key = st.text_input("Google Gemini API Key", type="password")
    if api_key:
        genai.configure(api_key=api_key)
        st.success("✅ API Key đã được cấu hình!")
    st.markdown("---")
    st.info("💡 Mỗi lần sinh câu hỏi sẽ đợi 60 giây để tránh vượt quota API miễn phí.")

def read_pdf(uploaded_file):
    text = ""
    pdf_document = pymupdf.open(stream=uploaded_file.read(), filetype="pdf")
    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        text += page.get_text()
    pdf_document.close()
    return text

def generate_questions_real(text_content, num_questions=3, difficulty="medium"):
    prompt = "Dựa vào nội dung sau, hãy tạo " + str(num_questions) + " câu hỏi trắc nghiệm mức độ " + difficulty + ".\n\n"
    prompt += "Nội dung:\n" + text_content[:3000] + "\n\n"
    prompt += "Yêu cầu:\n"
    prompt += "- Tạo CHÍNH XÁC " + str(num_questions) + " câu hỏi trắc nghiệm\n"
    prompt += "- Mỗi câu có 4 đáp án (A, B, C, D)\n"
    prompt += "- Mức độ: " + difficulty + "\n"
    prompt += "- Trả về CHÍNH XÁC format JSON này (KHÔNG thêm text khác):\n"
    prompt += '[{"question": "Câu hỏi?", "options": {"A": "Đáp án A", "B": "Đáp án B", "C": "Đáp án C", "D": "Đáp án D"}, "correct_answer": "A", "explanation": "Giải thích"}]'
    
    try:
        with st.spinner("⏳ Đợi 60 giây để tránh vượt quota API..."):
            time.sleep(60)
        model = genai.GenerativeModel("models/gemini-2.5-pro")
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Tìm JSON trong response
        start = response_text.find('[')
        end = response_text.rfind(']') + 1
        if start >= 0 and end > start:
            json_text = response_text[start:end]
            questions = json.loads(json_text)
            return questions
        else:
            questions = json.loads(response_text)
            return questions
    except Exception as e:
        st.error(f"❌ Lỗi: {e}")
        st.error(f"Response: {response_text if 'response_text' in locals() else 'N/A'}")
        return None

uploaded_file = st.file_uploader("📄 Upload file PDF", type=['pdf'])

if uploaded_file:
    with st.spinner("📖 Đang đọc file PDF..."):
        content = read_pdf(uploaded_file)
    st.success(f"✅ Đã đọc thành công! Độ dài: {len(content)} ký tự")
    with st.expander("👁️ Xem nội dung 500 ký tự đầu"):
        st.text(content[:500])
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        num_questions = st.slider("Số lượng câu hỏi", 1, 5, 3)
    with col2:
        difficulty = st.selectbox("Mức độ", ["easy", "medium", "hard"])
    if st.button("🤖 Sinh Câu Hỏi Bằng AI", type="primary"):
        if not api_key:
            st.error("❌ Vui lòng nhập API key ở sidebar!")
        else:
            questions = generate_questions_real(content, num_questions, difficulty)
            if questions:
                st.session_state.questions = questions
                st.session_state.user_answers = {}
                st.success("✅ Đã tạo câu hỏi thành công!")
    if 'questions' in st.session_state:
        st.markdown("---")
        st.header("📝 Câu Hỏi")
        for i, q in enumerate(st.session_state.questions):
            st.subheader(f"Câu {i+1}: {q['question']}")
            answer = st.radio("Chọn đáp án:", list(q['options'].keys()), format_func=lambda x: f"{x}. {q['options'][x]}", key=f"q_{i}")
            st.session_state.user_answers[i] = answer
            st.markdown("---")
        if st.button("✅ Nộp Bài", type="primary"):
            st.header("🎯 Kết Quả")
            correct = 0
            for i, q in enumerate(st.session_state.questions):
                user_ans = st.session_state.user_answers.get(i)
                is_correct = user_ans == q['correct_answer']
                if is_correct:
                    correct += 1
                    st.success(f"✅ Câu {i+1}: Đúng!")
                else:
                    st.error(f"❌ Câu {i+1}: Sai! Đáp án đúng: {q['correct_answer']}")
                st.info(f"💡 Giải thích: {q['explanation']}")
            score = (correct / len(st.session_state.questions)) * 100
            st.markdown("---")
            st.metric("Điểm số", f"{score:.1f}%")
            if score >= 80:
                st.balloons()
                st.success("🎉 Xuất sắc! Bạn đã hiểu rất tốt nội dung!")
            elif score >= 60:
                st.info("👍 Khá tốt! Hãy đọc kỹ thêm một chút.")
            else:
                st.warning("📖 Bạn nên đọc lại tài liệu kỹ hơn!")
else:
    st.info("👆 Hãy upload file PDF để bắt đầu!")
