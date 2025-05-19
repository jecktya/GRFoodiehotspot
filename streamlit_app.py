import streamlit as st
from streamlit.components.v1 import html

# 이미지 카테고리
category_images = {
    "전체": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/all.jpg",
    "한식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/korean.jpg",
    "중식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/chinese.jpg",
    "일식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/japanese.jpg",
    "양식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/western.jpg",
    "분식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/snack.jpg",
    "카페/디저트": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/dessert.jpg"
}

# 세션 상태로 선택 저장
if "selected_category" not in st.session_state:
    st.session_state.selected_category = "전체"

# 숨겨진 입력창 → JS가 이 값을 바꿔줌
selected = st.text_input("선택된 카테고리", st.session_state.selected_category, label_visibility="collapsed", key="selected_category_input")
if selected and selected != st.session_state.selected_category:
    st.session_state.selected_category = selected

# 렌더링 HTML
html_code = """
<script>
function setCategory(cat) {
    const input = window.parent.document.querySelector('input[data-testid="stTextInput"]');
    if (input) {
        input.value = '';
        input.dispatchEvent(new Event('input', { bubbles: true }));
        setTimeout(() => {
            input.value = cat;
            input.dispatchEvent(new Event('input', { bubbles: true }));
        }, 10);
    }
}
</script>
<div style="display:flex; gap:12px; overflow-x:auto; padding:8px 0;">
"""

for label, url in category_images.items():
    border = "#4CAF50" if label == st.session_state.selected_category else "transparent"
    html_code += f"""
    <div onclick="setCategory('{label}')" style="text-align:center; cursor:pointer;">
        <img src="{url}" style="width:120px; border-radius:10px;
            border:4px solid {border}; box-shadow:0 2px 6px rgba(0,0,0,0.1); transition:0.2s;">
        <div style="margin-top:5px; font-weight:bold;">{label}</div>
    </div>
    """

html_code += "</div>"

st.markdown("### 🍽️ 음식 종류를 선택하세요")
html(html_code, height=220)
st.markdown(f"### 🍱 현재 선택된 음식: **{st.session_state.selected_category}**")
