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

# 콤보 UI
category = st.selectbox("🍱 콤보로 선택하기", list(category_images.keys()), key="combo")

# 이미지 클릭 시 자바스크립트로 콤보 선택
html_code = """
<script>
function selectCategory(cat) {
    const selects = window.parent.document.querySelectorAll('select');
    selects.forEach(combo => {
        for (let i = 0; i < combo.options.length; i++) {
            if (combo.options[i].text === cat) {
                combo.selectedIndex = i;
                combo.dispatchEvent(new Event('change', { bubbles: true }));
                break;
            }
        }
    });
}
</script>
<div style="display:flex; gap:16px; overflow-x:auto; padding-top:12px;">
"""

for label, img_url in category_images.items():
    html_code += f"""
    <div onclick="selectCategory('{label}')" style="text-align:center; cursor:pointer;">
        <img src="{img_url}" style="width:100px; border-radius:10px; border:2px solid #ccc;">
        <div style="margin-top:4px;">{label}</div>
    </div>
    """

html_code += "</div>"

st.markdown("### 🖱️ 아래 이미지를 클릭하면 콤보 선택이 바뀝니다")
html(html_code, height=230)

# 결과 표시
st.success(f"✅ 현재 선택된 음식 종류: **{category}**")
