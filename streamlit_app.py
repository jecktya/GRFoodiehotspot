import streamlit as st

# 이미지와 카테고리 정의
category_images = {
    "전체": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/all.jpg",
    "한식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/korean.jpg",
    "중식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/chinese.jpg",
    "일식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/japanese.jpg",
    "양식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/western.jpg",
    "분식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/snack.jpg",
    "카페/디저트": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/dessert.jpg"
}

st.markdown("## 음식 종류를 선택해주세요")

# 세션 초기화
if "selected_category" not in st.session_state:
    st.session_state.selected_category = "전체"

# 선택된 카테고리
selected = st.session_state.selected_category

# 스타일 정의 (선택 시 테두리 강조)
def render_category_button(name, img_url, selected_name):
    border = "5px solid #4CAF50" if name == selected_name else "1px solid #ccc"
    return f"""
    <form action="" method="post">
        <button name="category" value="{name}" style="border:{border}; margin:5px; padding:0; background:none;">
            <img src="{img_url}" width="120" height="90" style="display:block;">
            <div style="text-align:center; font-weight:bold;">{name}</div>
        </button>
    </form>
    """

# 카테고리 표시 (3열씩)
cols = st.columns(3)
for idx, (name, url) in enumerate(category_images.items()):
    with cols[idx % 3]:
        html = render_category_button(name, url, selected)
        st.markdown(html, unsafe_allow_html=True)

# 폼 처리
if st.session_state.get("category"):
    st.session_state.selected_category = st.session_state["category"]

# 하단 텍스트 표시
st.markdown(f"### 🍱 현재 선택된 음식: **{st.session_state.selected_category}**")
