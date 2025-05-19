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

if "selected_category" not in st.session_state:
    st.session_state.selected_category = "전체"

st.markdown("### 🍽️ 음식 종류를 선택하세요")
cols = st.columns(len(category_images))
for i, (label, url) in enumerate(category_images.items()):
    with cols[i]:
        st.image(url, width=100)
        if st.button(label, key=f"catbtn_{label}"):
            st.session_state.selected_category = label
        # 강조 효과
        if st.session_state.selected_category == label:
            st.markdown("<div style='text-align:center; color:#4CAF50; font-weight:bold;'>✔ 선택됨</div>", unsafe_allow_html=True)
st.markdown(f"### ✅ 현재 선택된 음식: **{st.session_state.selected_category}**")
