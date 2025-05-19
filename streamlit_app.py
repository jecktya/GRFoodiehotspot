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

# CSS
st.markdown("""
<style>
.image-form-container {
    display: flex;
    gap: 16px;
    overflow-x: auto;
    padding-bottom: 10px;
}
.image-button {
    border: none;
    background: none;
    padding: 0;
    cursor: pointer;
}
.image-button img {
    width: 120px;
    border-radius: 10px;
    border: 3px solid transparent;
    transition: 0.2s all ease-in-out;
}
.image-button img:hover {
    transform: scale(1.05);
    box-shadow: 0 0 10px rgba(0,0,0,0.2);
}
.image-button img.selected {
    border-color: #4CAF50;
    box-shadow: 0 0 12px rgba(76,175,80,0.6);
    transform: scale(1.07);
}
</style>
""", unsafe_allow_html=True)

# 렌더링: form + image = 버튼
html_block = '<div class="image-form-container">'
for label, url in category_images.items():
    selected_class = "selected" if label == st.session_state.selected_category else ""
    html_block += f"""
    <form method="POST">
        <button class="image-button" name="select" value="{label}" type="submit">
            <img src="{url}" class="{selected_class}">
            <div style="text-align:center; font-weight:bold; margin-top:4px;">{label}</div>
        </button>
    </form>
    """
html_block += "</div>"

# 수동 처리 (Streamlit이 POST form 값을 자동으로 처리하지 않기 때문)
selected = st.experimental_get_query_params().get("select", [None])[0]
if selected in category_images:
    st.session_state.selected_category = selected

# 렌더링
st.components.v1.html(html_block, height=250)
st.markdown(f"### ✅ 현재 선택된 음식: **{st.session_state.selected_category}**")
