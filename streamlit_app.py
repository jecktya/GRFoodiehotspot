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

# 초기 선택 상태
if "selected_category" not in st.session_state:
    st.session_state.selected_category = "전체"

st.markdown("### 🍽️ 음식 종류를 선택하세요")

# CSS 스타일링
st.markdown("""
<style>
.image-card {
    width: 120px;
    border-radius: 10px;
    border: 3px solid transparent;
    transition: all 0.2s ease;
}
.image-card:hover {
    transform: scale(1.05);
    box-shadow: 0 0 10px rgba(0,0,0,0.2);
    cursor: pointer;
}
.image-card.selected {
    border-color: #4CAF50;
    box-shadow: 0 0 12px rgba(76,175,80,0.6);
    transform: scale(1.08);
}
</style>
""", unsafe_allow_html=True)

# UI 렌더링
cols = st.columns(len(category_images))
for idx, (label, url) in enumerate(category_images.items()):
    with cols[idx]:
        with st.form(f"form_{label}"):
            is_selected = st.session_state.selected_category == label
            css_class = "image-card selected" if is_selected else "image-card"

            st.markdown(
                f"<img src='{url}' class='{css_class}'>"
                f"<div style='text-align:center; font-weight:bold; margin-top:4px;'>{label}</div>",
                unsafe_allow_html=True
            )

            submitted = st.form_submit_button(" ", use_container_width=True)
            if submitted:
                st.session_state.selected_category = label

# 현재 선택 표시
st.markdown(f"### 🍱 현재 선택된 음식: **{st.session_state.selected_category}**")
