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

st.markdown("""
    <style>
    .cat-img {
        border: 4px solid transparent;
        border-radius: 14px;
        margin-bottom: 10px;
        transition: 0.15s all;
        box-shadow: 0 1px 6px rgba(0,0,0,0.10);
    }
    .cat-img.selected {
        border-color: #4CAF50 !important;
        box-shadow: 0 0 18px rgba(76,175,80,0.19);
        transform: scale(1.07);
    }
    .cat-btn {
        margin-top: -12px;
        margin-bottom: 6px;
        width: 100%;
        font-size: 1em;
        font-weight: bold;
        border-radius: 7px;
        border: 2px solid #e0e0e0;
        background: #f6fff6;
        color: #232323;
        transition: 0.13s;
    }
    .cat-btn.selected {
        border-color: #4CAF50;
        background: #E7FCEB;
        color: #249a3a;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("### 🍽️ 음식 종류를 선택하세요")

cols = st.columns(len(category_images))
for i, (label, url) in enumerate(category_images.items()):
    with cols[i]:
        selected = st.session_state.selected_category == label
        # 그림: 캡션 없이
        st.markdown(
            f'<img src="{url}" class="cat-img{" selected" if selected else ""}"/>',
            unsafe_allow_html=True
        )
        # 버튼: 라벨 표시, 선택되면 스타일 적용
        btn = st.button(
            label,
            key=f"catbtn_{label}",
            help=f"{label} 카테고리 선택",
        )
        if btn:
            st.session_state.selected_category = label

st.markdown(
    f"<div style='text-align:center; margin-top:18px;'><b style='color:#4CAF50; font-size:1.3em'>✔ {st.session_state.selected_category} 선택됨</b></div>",
    unsafe_allow_html=True
)
