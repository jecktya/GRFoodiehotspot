st.markdown("## 음식 종류를 선택해주세요")

category_images = {
    "전체": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/all.jpg",
    "한식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/korean.jpg",
    "중식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/chinese.jpg",
    "일식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/japanese.jpg",
    "양식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/western.jpg",
    "분식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/snack.jpg",
    "카페/디저트": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/dessert.jpg"
}

# 카테고리 선택을 위한 시각적 이미지 + radio UI
cols = st.columns(len(category_images))
selected_category = st.session_state.get("selected_category", "전체")

for idx, (label, img_url) in enumerate(category_images.items()):
    with cols[idx]:
        st.image(img_url, use_container_width=True)
        if st.radio("선택", options=["", label], key=f"radio_{idx}", label_visibility="collapsed") == label:
            selected_category = label
            st.session_state.selected_category = label

# 선택된 카테고리 표시
st.markdown(f"### 🍱 현재 선택된 음식: **{selected_category}**")
