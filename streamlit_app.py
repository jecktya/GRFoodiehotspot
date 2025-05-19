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

# 이미지+텍스트 HTML로 묶기
options = []
for label, url in category_images.items():
    options.append(f'<img src="{url}" width="120"><br><span style="font-weight:bold">{label}</span>')

# 초기값 세팅
default_idx = list(category_images.keys()).index(st.session_state.get("selected_category", "전체"))

# radio로 그림+텍스트 한 줄
choice = st.radio(
    "🍽️ 음식 종류를 선택하세요",
    options,
    index=default_idx,
    format_func=lambda x: "",  # 옵션 텍스트 숨김
)

# 선택값 다시 변환 (radio는 str 그대로 반환)
selected_idx = options.index(choice)
selected_label = list(category_images.keys())[selected_idx]
st.session_state.selected_category = selected_label

# 강조 스타일
st.markdown(
    f"<div style='text-align:center; margin-top:18px;'><b style='color:#4CAF50; font-size:1.3em'>✔ {selected_label} 선택됨</b></div>",
    unsafe_allow_html=True
)

