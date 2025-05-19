import streamlit as st

# 이미지 카테고리 정의
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

# 이미지 버튼을 컬럼으로 나열
cols = st.columns(len(category_images))

for idx, (label, url) in enumerate(category_images.items()):
    with cols[idx]:
        # 버튼처럼 보이는 이미지 + 클릭 시 선택값 변경
        if st.button(f" ", key=f"btn_{label}"):  # 유니코드 공백으로 버튼 텍스트 숨김
            st.session_state.selected_category = label

        # 선택된 항목은 강조 테두리
        selected_style = (
            "border:4px solid #4CAF50; border-radius:10px; box-shadow:0 0 10px rgba(76,175,80,0.5);"
            if st.session_state.selected_category == label else
            "border:1px solid transparent; border-radius:10px;"
        )

        st.markdown(
            f"""
            <div style="{selected_style} padding:3px;">
                <img src="{url}" width="100%" style="border-radius:10px;">
                <div style="text-align:center; font-weight:bold; margin-top:5px;">{label}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown(f"### 🍱 현재 선택된 음식: **{st.session_state.selected_category}**")
