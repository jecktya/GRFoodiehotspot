import streamlit as st

category_images = {
    "전체": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/all.jpg",
    "한식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/korean.jpg",
    "중식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/chinese.jpg",
    "일식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/japanese.jpg",
    "양식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/western.jpg",
    "분식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/snack.jpg",
    "카페/디저트": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/dessert.jpg"
}

st.markdown("### 🍽️ 음식 종류를 선택하세요")

# 선택 UI (라디오박스)
selected_category = st.radio(
    "카테고리",
    list(category_images.keys()),
    horizontal=True,
    index=None,  # 아무것도 선택 안 된 상태가 기본
)

# 아무것도 선택 안하면 그림 안 보임
if selected_category is not None:
    st.markdown("---")
    st.markdown(
        f"<div style='display:flex; flex-direction:column; align-items:center;'>"
        f"<img src='{category_images[selected_category]}' style='width:240px; border-radius:15px; border:4px solid #4CAF50; box-shadow:0 2px 18px rgba(76,175,80,0.10); margin-bottom:12px;'>"
        f"<div style='font-size:1.2em; color:#4CAF50; font-weight:bold; margin-top:7px;'>{selected_category}</div>"
        f"</div>",
        unsafe_allow_html=True
    )

