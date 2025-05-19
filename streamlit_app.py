import streamlit as st

# 이미지 목록
category_images = {
    "전체": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/all.jpg",
    "한식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/korean.jpg",
    "중식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/chinese.jpg",
    "일식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/japanese.jpg",
    "양식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/western.jpg",
    "분식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/snack.jpg",
    "카페/디저트": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/dessert.jpg"
}

# 초기 선택
if "selected_category" not in st.session_state:
    st.session_state.selected_category = "전체"

# 선택 처리
def update_selection(cat):
    st.session_state.selected_category = cat

# 스타일
st.markdown("""
    <style>
    .scroll-menu {
        display: flex;
        overflow-x: auto;
        gap: 12px;
        padding: 10px 0;
        white-space: nowrap;
    }
    .img-btn {
        border: none;
        background: none;
        padding: 0;
    }
    .img-card {
        width: 120px;
        border-radius: 10px;
        border: 2px solid transparent;
        transition: all 0.2s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .img-card:hover {
        transform: scale(1.05);
        cursor: pointer;
        box-shadow: 0 0 10px rgba(0,0,0,0.2);
    }
    .img-card.selected {
        border: 3px solid #4CAF50;
        box-shadow: 0 0 12px rgba(76, 175, 80, 0.6);
        transform: scale(1.08);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="scroll-menu">', unsafe_allow_html=True)

for cat, url in category_images.items():
    # JS-Free 이미지 버튼처럼 보이게 하려면 form 사용
    with st.form(f"form_{cat}"):
        is_selected = (st.session_state.selected_category == cat)
        class_name = "img-card selected" if is_selected else "img-card"
        st.markdown(f"""
        <button type="submit" class="img-btn">
            <img src="{url}" class="{class_name}">
            <div style="text-align:center; font-weight:bold; margin-top:5px;">{cat}</div>
        </button>
        """, unsafe_allow_html=True)
        if st.form_submit_button(label="", use_container_width=True):
            update_selection(cat)

st.markdown("</div>", unsafe_allow_html=True)

# 선택된 항목 출력
st.markdown(f"### 🍱 현재 선택된 음식: **{st.session_state.selected_category}**")
