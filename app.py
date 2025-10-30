
import streamlit as st
import google.generativeai as genai
import pymupdf
import time
import json

# Cấu hình trang
st.set_page_config(
    page_title="Công cụ Đọc Hiểu Sách",
    page_icon="📚",
    layout="wide"
)

# Tiêu đề
st.title("📚 Công Cụ Kiểm Tra Đọc Hiểu Sách")
st.markdown("Upload file PDF và AI sẽ tạo câu hỏi kiểm tra mức độ hiểu của bạn!")

# Sidebar - API Key
with st.sidebar:
    st.header("⚙️ Cài Đặt")
    api_key = st.text_input("Google Gemini API Key", type="password")
    
    if api_key:
        genai.configure(api_key=api_key)
        st.success("✅ API Key đã được cấu hình!")

# Hàm đọc PDF
def read_pdf(uploaded_file):
    """Đọc nội dung từ file PDF"""
    text = ""
    pdf_document = pymupdf.open(stream=uploaded_file.read(), filetype="pdf")
    
    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        text += page.get_text()
    
    pdf_document.close()
    return text

# Hàm sinh câu hỏi (giả lập, không gọi API để tránh quota)
def generate_questions_demo(text_content, num_questions=3):
    """Demo sinh câu hỏi (không gọi API)"""
    # Câu hỏi mẫu để demo giao diện
    demo_questions = [
        {
            "question": "Nội dung chính của tài liệu là gì?",
            "options": {
                "A": "Sinh học tế bào",
                "B": "Hóa học hữu cơ",
                "C": "Vật lý lượng tử",
                "D": "Toán học ứng dụng"
            },
            "correct_answer": "A",
            "explanation": "Dựa vào nội dung tài liệu đã phân tích"
        },
        {
            "question": "Protein có vai trò gì trong tế bào?",
            "options": {
                "A": "Lưu trữ năng lượng",
                "B": "Xúc tác phản ứng",
                "C": "Lưu trữ thông tin di truyền",
                "D": "Tạo màng tế bào"
            },
            "correct_answer": "B",
            "explanation": "Protein có chức năng enzyme xúc tác các phản ứng sinh hóa"
        },
        {
            "question": "DNA và RNA khác nhau ở điểm nào?",
            "options": {
                "A": "Số lượng mạch",
                "B": "Loại đường",
                "C": "Một số base nitơ",
                "D": "Tất cả các đáp án trên"
            },
            "correct_answer": "D",
            "explanation": "DNA có 2 mạch, đường deoxyribose; RNA có 1 mạch, đường ribose, và U thay cho T"
        }
    ]
    
    return demo_questions[:num_questions]

# Main app
uploaded_file = st.file_uploader("📄 Upload file PDF", type=['pdf'])

if uploaded_file:
    # Đọc PDF
    with st.spinner("📖 Đang đọc file PDF..."):
        content = read_pdf(uploaded_file)
    
    st.success(f"✅ Đã đọc thành công! Độ dài: {len(content)} ký tự")
    
    # Hiển thị preview
    with st.expander("👁️ Xem nội dung 500 ký tự đầu"):
        st.text(content[:500])
    
    # Tùy chọn sinh câu hỏi
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        num_questions = st.slider("Số lượng câu hỏi", 1, 10, 3)
    
    with col2:
        difficulty = st.selectbox("Mức độ", ["easy", "medium", "hard"])
    
    # Nút sinh câu hỏi
    if st.button("🤖 Sinh Câu Hỏi", type="primary"):
        with st.spinner("⏳ AI đang tạo câu hỏi..."):
            # Demo mode - không gọi API thật
            questions = generate_questions_demo(content, num_questions)
        
        # Lưu vào session state
        st.session_state.questions = questions
        st.session_state.user_answers = {}
        st.success("✅ Đã tạo câu hỏi thành công!")
    
    # Hiển thị câu hỏi
    if 'questions' in st.session_state:
        st.markdown("---")
        st.header("📝 Câu Hỏi")
        
        for i, q in enumerate(st.session_state.questions):
            st.subheader(f"Câu {i+1}: {q['question']}")
            
            answer = st.radio(
                "Chọn đáp án:",
                list(q['options'].keys()),
                format_func=lambda x: f"{x}. {q['options'][x]}",
                key=f"q_{i}"
            )
            
            st.session_state.user_answers[i] = answer
            st.markdown("---")
        
        # Nút nộp bài
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
            
            # Đánh giá
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
