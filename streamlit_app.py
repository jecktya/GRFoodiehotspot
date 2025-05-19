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

# 상태 초기화
if "selected_category" not in st.session_state:
    st.session_state.selected_category = "전체"

# 콤보박스 - 그림 클릭과 동기화됨
category_list = list(category_images.keys())
current_index = category_list.index(st.session_state.selected_category)
combo = st.selectbox("🍱 콤보로 선택하기", category_list, index=current_index)
st.session_state.selected_category = combo

# 이미지 버튼 UI
st.markdown("### 또는 그림을 클릭해서 선택하세요:")
cols = st.columns(len(category_images))
for i, (label, url) in enumerate(category_images.items()):
    with cols[i]:
        with st.form(f"form_{label}"):
            st.image(url, caption=label, use_container_width=True)
            if st.form_submit_button(" "):  # 공백 버튼
                st.session_state.selected_category = label  # 상태만 바꾸면 자동 반영됨

# 선택된 항목 출력
st.markdown(f"### ✅ 현재 선택된 음식 종류: **{st.session_state.selected_category}**")
