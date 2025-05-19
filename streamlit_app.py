import streamlit as st

# 이미지 URL 정의
category_images = {
    "전체": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/all.jpg",
    "한식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/korean.jpg",
    "중식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/chinese.jpg",
    "일식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/japanese.jpg",
    "양식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/western.jpg",
    "분식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/snack.jpg",
    "카페/디저트": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/dessert.jpg"
}

# 선택 상태 초기화
if "selected_category" not in st.session_state:
    st.session_state.selected_category = "전체"

st.markdown("## 음식 종류를 선택해주세요")

# CSS 스타일 정의 (선택 효과 포함)
st.markdown("""
    <style>
        .image-card {
            border: 2px solid transparent;
            border-radius: 10px;
            padding: 4px;
            transition: transform 0.2s ease;
        }
        .image-card:hover {
            transform: scale(1.03);
            cursor: pointer;
        }
        .selected {
            border: 4px solid #4CAF50 !important;
            box-shadow: 0 0 10px rgba(76, 175, 80, 0.5);
        }
    </style>
""", unsafe_allow_html=True)

# 4열 레이아웃
cols = st.columns(4)

# 카테고리 이미지 렌더링
for idx, (label, img_url) in enumerate(category_images.items()):
    with cols[idx % 4]:
        is_selected = (st.session_state.selected_category == label)
        card_class = "image-card selected" if is_selected else "image-card"
        
        # 실제 클릭 버튼은 위쪽에 숨겨진 텍스트 버튼
        if st.button(f"⠀", key=f"btn_{label}"):  # 유니코드 공백 사용
            st.session_state.selected_category = label

        # HTML로 이미지 + 이름 표시
        st.markdown(f"""
            <div class="{card_class}">
                <img src="{img_url}" width="100%" style="border-radius:8px;">
                <div style="text-align:center; font-weight:bold; margin-top:5px;">{label}</div>
            </div>
        """, unsafe_allow_html=True)

# 선택 결과 텍스트 출력
st.markdown(f"### 🍱 현재 선택된 음식: **{st.session_state.selected_category}**")
