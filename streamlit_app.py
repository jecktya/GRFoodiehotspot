import streamlit as st

# 이미지 정의
category_images = {
    "전체": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/all.jpg",
    "한식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/korean.jpg",
    "중식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/chinese.jpg",
    "일식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/japanese.jpg",
    "양식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/western.jpg",
    "분식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/snack.jpg",
    "카페/디저트": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/dessert.jpg"
}

# 초기 선택 상태
if "selected_category" not in st.session_state:
    st.session_state.selected_category = "전체"

# 스타일
st.markdown("""
    <style>
    .scroll-row {
        display: flex;
        gap: 16px;
        overflow-x: auto;
        padding-bottom: 16px;
    }
    .image-button {
        width: 120px;
        border-radius: 10px;
        border: 3px solid transparent;
        transition: 0.2s all ease-in-out;
    }
    .image-button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 10px rgba(0,0,0,0.2);
        cursor: pointer;
    }
    .selected {
        border-color: #4CAF50 !important;
        box-shadow: 0 0 10px rgba(76,175,80,0.5);
        transform: scale(1.07);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("### 🍽️ 음식 종류를 선택하세요")
st.markdown('<div class="scroll-row">', unsafe_allow_html=True)

# 렌더링
for label, url in category_images.items():
    with st.form(f"form_{label}"):
        is_selected = label == st.session_state.selected_category
        img_class = "image-button selected" if is_selected else "image-button"

        st.markdown(
            f"""
            <button type="submit" style="border:none;background:none;padding:0;margin:0;">
                <img src="{url}" class="{img_class}">
                <div style="text-align:center; font-weight:bold; margin-top:4px;">{label}</div>
            </button>
            """,
            unsafe_allow_html=True
        )

        if st.form_submit_button(label="", use_container_width=True):
            st.session_state.selected_category = label

st.markdown('</div>', unsafe_allow_html=True)
st.markdown(f"### 🍱 현재 선택된 음식: **{st.session_state.selected_category}**")
