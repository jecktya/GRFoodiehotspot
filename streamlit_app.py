import streamlit as st

# 썸네일 이미지
category_images = {
    "전체": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/all.jpg",
    "한식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/korean.jpg",
    "중식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/chinese.jpg",
    "일식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/japanese.jpg",
    "양식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/western.jpg",
    "분식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/snack.jpg",
    "카페/디저트": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/dessert.jpg"
}

# 초기 선택값
if "selected_category" not in st.session_state:
    st.session_state.selected_category = "전체"

st.markdown("### 🍽️ 음식 종류를 선택하세요")

# CSS 스타일 (애니메이션 + 강조)
st.markdown("""
    <style>
    .card {
        display: inline-block;
        width: 130px;
        margin-right: 12px;
        border-radius: 10px;
        border: 2px solid transparent;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        text-align: center;
    }
    .card:hover {
        transform: scale(1.05);
        cursor: pointer;
        box-shadow: 0 0 12px rgba(100, 100, 100, 0.3);
    }
    .selected {
        border: 3px solid #4CAF50 !important;
        box-shadow: 0 0 15px rgba(76, 175, 80, 0.6);
        transform: scale(1.07);
    }
    .scroll-container {
        overflow-x: auto;
        white-space: nowrap;
        padding-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# 이미지 클릭형 메뉴
st.markdown('<div class="scroll-container">', unsafe_allow_html=True)

cols = st.columns(len(category_images))
for idx, (label, url) in enumerate(category_images.items()):
    with cols[idx]:
        # 이미지 클릭용 버튼
        if st.button("", key=f"cat_{label}"):
            st.session_state.selected_category = label

        # 강조 여부
        card_class = "card selected" if st.session_state.selected_category == label else "card"
        st.markdown(f"""
            <div class="{card_class}">
                <img src="{url}" width="100%" style="border-radius:8px;">
                <div style="margin-top:5px; font-weight:bold;">{label}</div>
            </div>
        """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# 선택 결과
st.markdown(f"### 🍱 현재 선택된 음식: **{st.session_state.selected_category}**")
