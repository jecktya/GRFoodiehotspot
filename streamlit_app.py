import streamlit as st
from streamlit.components.v1 import html

# 이미지 카테고리 정의
category_images = {
    "전체": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/all.jpg",
    "한식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/korean.jpg",
    "중식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/chinese.jpg",
    "일식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/japanese.jpg",
    "양식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/western.jpg",
    "분식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/snack.jpg",
    "카페/디저트": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/dessert.jpg"
}

# 초기값 설정
if "selected_category" not in st.session_state:
    st.session_state.selected_category = "전체"

# 선택 결과 출력
st.markdown("### 🍽️ 음식 종류를 선택하세요")

# 스타일 정의
st.markdown("""
    <style>
    .scroll-container {
        display: flex;
        overflow-x: auto;
        gap: 12px;
        padding-bottom: 12px;
    }
    .image-button {
        border: none;
        background: none;
        padding: 0;
        margin: 0;
        cursor: pointer;
    }
    .image-button img {
        width: 120px;
        border-radius: 10px;
        border: 3px solid transparent;
        transition: all 0.2s ease;
    }
    .image-button img:hover {
        transform: scale(1.05);
        box-shadow: 0 0 10px rgba(0,0,0,0.2);
    }
    .image-button img.selected {
        border-color: #4CAF50;
        box-shadow: 0 0 12px rgba(76,175,80,0.6);
        transform: scale(1.08);
    }
    </style>
""", unsafe_allow_html=True)

# 폼 내에서 버튼으로 감싸서 완전히 통합 (Streamlit Cloud 친화적)
st.markdown('<div class="scroll-container">', unsafe_allow_html=True)

for label, url in category_images.items():
    with st.form(key=f"form_{label}"):
        # 버튼 안에 이미지 + 텍스트 함께 넣기
        img_class = "selected" if st.session_state.selected_category == label else ""
        submitted = st.form_submit_button(
            label=f"""
            <button class="image-button" type="submit">
                <img src="{url}" class="{img_class}">
                <div style='text-align:center; font-weight:bold; margin-top:4px;'>{label}</div>
            </button>
            """,
            use_container_width=True
        )
        if submitted:
            st.session_state.selected_category = label

st.markdown("</div>", unsafe_allow_html=True)
st.markdown(f"### 🍱 현재 선택된 음식: **{st.session_state.selected_category}**")
