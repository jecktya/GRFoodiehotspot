import streamlit as st

# 이미지 카테고리
category_images = {
    "전체": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/all.jpg",
    "한식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/korean.jpg",
    "중식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/chinese.jpg",
    "일식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/japanese.jpg",
    "양식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/western.jpg",
    "분식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/snack.jpg",
    "카페/디저트": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/dessert.jpg"
}

# 선택 초기화
if "selected_category" not in st.session_state:
    st.session_state.selected_category = "전체"

# CSS: 클릭 효과 및 강조
st.markdown("""
    <style>
    .scroll {
        display: flex;
        overflow-x: auto;
        gap: 16px;
        padding: 10px 0;
        white-space: nowrap;
    }
    .cat-img {
        border: 3px solid transparent;
        border-radius: 10px;
        transition: all 0.2s ease;
        width: 130px;
    }
    .cat-img:hover {
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

# 헤더
st.markdown("### 🍽️ 음식 종류를 선택하세요")

# 이미지 버튼 구현
st.markdown('<div class="scroll">', unsafe_allow_html=True)
for cat, img_url in category_images.items():
    selected_class = "cat-img selected" if cat == st.session_state.selected_category else "cat-img"

    # 클릭을 감지할 숨겨진 form
    with st.form(f"form_{cat}", clear_on_submit=True):
        st.markdown(f"""
        <input type="submit" value="" style="border:none;background:none;padding:0;">
        <img src="{img_url}" class="{selected_class}">
        <div style="text-align:center; font-weight:bold;">{cat}</div>
        """, unsafe_allow_html=True)
        if st.form_submit_button("", use_container_width=True):
            st.session_state.selected_category = cat
st.markdown('</div>', unsafe_allow_html=True)

# 현재 선택 표시
st.markdown(f"### 🍱 현재 선택된 음식: **{st.session_state.selected_category}**")
