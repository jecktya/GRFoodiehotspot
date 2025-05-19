import streamlit as st

# 카테고리 이미지 정의
category_images = {
    "전체": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/all.jpg",
    "한식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/korean.jpg",
    "중식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/chinese.jpg",
    "일식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/japanese.jpg",
    "양식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/western.jpg",
    "분식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/snack.jpg",
    "카페/디저트": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/dessert.jpg"
}

# 초기 선택값 설정
if "selected_category" not in st.session_state:
    st.session_state.selected_category = "전체"

st.markdown("### 🍽️ 음식 종류를 선택하세요")

# CSS: 버튼 숨기고 이미지에 선택 효과
st.markdown("""
    <style>
    .image-form {
        display: inline-block;
        margin-right: 10px;
        text-align: center;
    }
    .image-button {
        border: none;
        background: none;
        padding: 0;
    }
    .category-img {
        width: 120px;
        border-radius: 10px;
        transition: all 0.2s ease;
        border: 3px solid transparent;
    }
    .category-img:hover {
        transform: scale(1.05);
        box-shadow: 0 0 10px rgba(0,0,0,0.2);
        cursor: pointer;
    }
    .selected {
        border-color: #4CAF50;
        box-shadow: 0 0 12px rgba(76,175,80,0.6);
        transform: scale(1.08);
    }
    </style>
""", unsafe_allow_html=True)

# 이미지 선택 UI
st.markdown('<div style="white-space:nowrap; overflow-x:auto;">', unsafe_allow_html=True)

for label, url in category_images.items():
    is_selected = (st.session_state.selected_category == label)
    selected_class = "category-img selected" if is_selected else "category-img"

    with st.form(f"form_{label}"):
        st.markdown(f'<div class="image-form">', unsafe_allow_html=True)
        st.markdown(
            f"""
            <button class="image-button" type="submit">
                <img src="{url}" class="{selected_class}">
            </button>
            <div style="margin-top: 5px; font-weight: bold;">{label}</div>
            """,
            unsafe_allow_html=True
        )
        if st.form_submit_button("", use_container_width=True):
            st.session_state.selected_category = label
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# 결과 표시
st.markdown(f"### 🍱 현재 선택된 음식: **{st.session_state.selected_category}**")
