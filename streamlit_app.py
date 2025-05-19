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
    .selected-cat {
        border: 4px solid #4CAF50 !important;
        box-shadow: 0 0 12px rgba(76,175,80,0.15);
        border-radius: 12px;
        margin-bottom: 2px;
        transition: 0.18s all;
    }
    .cat-img {
        border: 3px solid #e0e0e0;
        border-radius: 12px;
        margin-bottom: 2px;
        transition: 0.15s all;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("### 🍽️ 음식 종류를 선택하세요")

cols = st.columns(len(category_images))
for i, (label, url) in enumerate(category_images.items()):
    with cols[i]:
        if st.session_state.selected_category == label:
            st.image(url, use_container_width=True, output_format="PNG", caption=label, clamp=True, channels="RGB")
            st.markdown('<div class="selected-cat"></div>', unsafe_allow_html=True)
        else:
            st.image(url, use_container_width=True, output_format="PNG", caption=label, clamp=True, channels="RGB")
        if st.button(" ", key=f"btn_{label}"):
            st.session_state.selected_category = label

st.markdown(f"<div style='text-align:center; margin-top:16px;'><b style='color:#4CAF50;font-size:1.3em;'>✔ {st.session_state.selected_category} 선택됨</b></div>", unsafe_allow_html=True)
