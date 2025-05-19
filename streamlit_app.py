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

# 선택된 카테고리 유지
selected_category = st.radio(
    "🍽️ 음식 종류를 선택하세요",
    list(category_images.keys()),
    horizontal=True
)

# 그림+선택 강조 렌더링
cols = st.columns(len(category_images))
for i, (label, url) in enumerate(category_images.items()):
    with cols[i]:
        border = "4px solid #4CAF50" if label == selected_category else "3px solid #e0e0e0"
        st.markdown(
            f'<img src="{url}" style="width:110px;border-radius:12px;border:{border};margin-bottom:4px;box-shadow:0 1px 6px rgba(0,0,0,0.09);" />',
            unsafe_allow_html=True
        )
        st.markdown(
            f"<div style='text-align:center;font-weight:bold;'>{label}</div>",
            unsafe_allow_html=True
        )

st.markdown(
    f"<div style='text-align:center; margin-top:18px;'><b style='color:#4CAF50; font-size:1.3em'>✔ {selected_category} 선택됨</b></div>",
    unsafe_allow_html=True
)
