import streamlit as st
from streamlit.components.v1 import html

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

# 숨겨진 입력 필드 - JS에서 값 업데이트
category_selected = st.text_input("선택된 카테고리", st.session_state.selected_category, label_visibility="collapsed")
if category_selected and category_selected != st.session_state.selected_category:
    st.session_state.selected_category = category_selected

# JS 클릭 핸들러 삽입
st.components.v1.html(f"""
<script>
function setCategory(category) {{
    const input = window.parent.document.querySelector('input[data-testid="stTextInput"]');
    if (input) {{
        input.value = category;
        input.dispatchEvent(new Event('input', {{ bubbles: true }}));
    }}
}}
</script>

<div style="display: flex; overflow-x: auto; gap: 12px; padding-bottom: 10px;">
    {''.join(f'''
    <div onclick="setCategory('{cat}')" style="cursor: pointer; text-align: center;">
        <img src="{url}" style="width: 120px; border-radius: 10px;
        border: {'4px solid #4CAF50' if cat == st.session_state.selected_category else '2px solid transparent'};
        box-shadow: 0 2px 6px rgba(0,0,0,0.15); transition: 0.2s;">
        <div style="margin-top: 4px; font-weight: bold;">{cat}</div>
    </div>''' for cat, url in category_images.items())}
</div>
""", height=190)

st.markdown(f"### 🍱 현재 선택된 음식: **{st.session_state.selected_category}**")
