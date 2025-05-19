import streamlit as st

# 이미지 목록
category_images = {
    "전체": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/all.jpg",
    "한식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/korean.jpg",
    "중식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/chinese.jpg",
    "일식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/japanese.jpg",
    "양식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/western.jpg",
    "분식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/snack.jpg",
    "카페/디저트": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/dessert.jpg"
}

# 선택 상태 초기화
if "selected_category" not in st.session_state:
    st.session_state.selected_category = "전체"

# 스타일 정의
st.markdown("""
    <style>
    .scroll-container {
        display: flex;
        overflow-x: auto;
        padding-bottom: 10px;
        gap: 16px;
    }
    .image-button {
        border: none;
        background: none;
        padding: 0;
    }
    .image-card {
        border: 3px solid transparent;
        border-radius: 10px;
        transition: all 0.3s ease;
        width: 130px;
    }
    .image-card:hover {
        transform: scale(1.05);
        cursor: pointer;
        box-shadow: 0 0 10px rgba(0,0,0,0.2);
    }
    .selected {
        border-color: #4CAF50;
        box-shadow: 0 0 12px rgba(76,175,80,0.6);
        transform: scale(1.08);
    }
    </style>
""", unsafe_allow_html=True)

# 헤더
st.markdown("### 🍽️ 음식 종류를 선택하세요")
st.markdown('<div class="scroll-container">', unsafe_allow_html=True)

# 이미지 버튼 렌더링
for label, url in category_images.items():
    is_selected = (st.session_state.selected_category == label)
    css_class = "image-card selected" if is_selected else "image-card"

    # 이미지 버튼 감지
    if st.button(f"img_btn_{label}", key=f"btn_{label}"):
        st.session_state.selected_category = label

    # 이미지 렌더링 (마크다운만)
    st.markdown(f"""
        <button class="image-button" onclick="document.getElementById('{label}').click()">
            <img src="{url}" class="{css_class}">
            <div style="text-align:center; font-weight:bold;">{label}</div>
        </button>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# 선택 결과 표시
st.markdown(f"### 🍱 현재 선택된 음식: **{st.session_state.selected_category}**")
