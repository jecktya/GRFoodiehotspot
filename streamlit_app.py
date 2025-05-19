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

selected = st.text_input("선택된 카테고리", st.session_state.selected_category, label_visibility="collapsed", key="selected_input")
if selected and selected != st.session_state.selected_category:
    st.session_state.selected_category = selected

html_code = """
<script>
window.addEventListener("DOMContentLoaded", function() {
    const items = document.querySelectorAll('[data-cat]');
    const input = window.parent.document.querySelector('input[data-testid="stTextInput"]');
    items.forEach(el => {
        el.addEventListener("click", () => {
            if (input) {
                input.value = "";
                input.dispatchEvent(new Event("input", { bubbles: true }));
                setTimeout(() => {
                    input.value = el.dataset.cat;
                    input.dispatchEvent(new Event("input", { bubbles: true }));
                }, 50);
            }
        });
    });
});
</script>
<div style="display:flex; gap:12px; overflow-x:auto; padding:10px 0;">
"""

for label, url in category_images.items():
    is_selected = (label == st.session_state.selected_category)
    border = "#4CAF50" if is_selected else "transparent"
    html_code += f"""
    <div data-cat="{label}" style="text-align:center; cursor:pointer;">
        <img src="{url}" style="width:120px; border-radius:10px; border:4px solid {border}; box-shadow:0 2px 6px rgba(0,0,0,0.1); transition:0.2s;">
        <div style="margin-top:5px; font-weight:bold;">{label}</div>
    </div>
    """

html_code += "</div>"

st.markdown("### 🍽️ 음식 종류를 선택하세요")
html(html_code, height=230)
st.markdown(f"### 🍱 현재 선택된 음식: **{st.session_state.selected_category}**")
