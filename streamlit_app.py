import streamlit as st

# 이미지 데이터
category_images = {
    "전체": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/all.jpg",
    "한식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/korean.jpg",
    "중식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/chinese.jpg",
    "일식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/japanese.jpg",
    "양식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/western.jpg",
    "분식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/snack.jpg",
    "카페/디저트": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/dessert.jpg"
}

# 상태 초기화
if "selected_category" not in st.session_state:
    st.session_state.selected_category = "전체"

st.markdown("### 🍽️ 음식 종류를 선택하세요")

# CSS: 완전한 버튼 대체 (이미지를 눌렀을 때만 반응 + 강조 효과)
st.markdown("""
    <style>
    .cat-container {
        display: flex;
        overflow-x: auto;
        gap: 16px;
        padding: 10px 0;
    }
    .cat-form {
        display: inline-block;
        border: none;
        background: none;
    }
    .cat-img {
        width: 120px;
        border-radius: 10px;
        border: 3px solid transparent;
        transition: transform 0.2s ease;
    }
    .cat-img:hover {
        transform: scale(1.05);
        cursor: pointer;
        box-shadow: 0 0 10px rgba(0,0,0,0.15);
    }
    .selected {
        border-color: #4CAF50 !important;
        box-shadow: 0 0 12px rgba(76,175,80,0.6);
        transform: scale(1.08);
    }
    </style>
""", unsafe_allow_html=True)

# 가로 스크롤 UI
st.markdown('<div class="cat-container">', unsafe_allow_html=True)

# 이미지가 곧 버튼
for cat, img_url in category_images.items():
    is_selected = st.session_state.selected_category == cat
    css_class = "cat-img selected" if is_selected else "cat-img"

    with st.form(f"form_{cat}"):
        submitted = st.form_submit_button(
            label=f"""<img src="{img_url}" class="{css_class}"><div style='text-align:center; font-weight:bold; margin-top:4px;'>{cat}</div>""",
            use_container_width=False
        )
        if submitted:
            st.session_state.selected_category = cat

st.markdown("</div>", unsafe_allow_html=True)

# 선택 결과 표시
st.markdown(f"### 🍱 현재 선택된 음식: **{st.session_state.selected_category}**")
