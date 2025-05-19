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

# 상태 초기화
if "selected_category" not in st.session_state:
    st.session_state.selected_category = "전체"

st.markdown("### 🍽️ 음식 종류를 선택하세요")

# CSS 스타일
st.markdown("""
    <style>
    div[data-testid="column"] > div {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .selected {
        border: 4px solid #4CAF50;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(76,175,80,0.5);
    }
    .category-img {
        border-radius: 10px;
        transition: transform 0.2s ease;
    }
    .category-img:hover {
        transform: scale(1.05);
        cursor: pointer;
        box-shadow: 0 0 10px rgba(0,0,0,0.2);
    }
    </style>
""", unsafe_allow_html=True)

# 이미지 버튼 렌더링 (한 줄 스크롤 아님, 간단히 열 배치)
cols = st.columns(len(category_images))

for idx, (label, url) in enumerate(category_images.items()):
    with cols[idx]:
        clicked = st.button(" ", key=f"btn_{label}")
        if clicked:
            st.session_state.selected_category = label

        # 선택 시 강조 클래스 부여
        selected_class = "selected" if st.session_state.selected_category == label else ""
        st.markdown(f"""
            <img src="{url}" width="100%" class="category-img {selected_class}">
            <div style="text-align:center; font-weight:bold; margin-top:4px;">{label}</div>
        """, unsafe_allow_html=True)

# 선택 결과 출력
st.markdown(f"### 🍱 현재 선택된 음식: **{**
