import streamlit as st

# 이미지 + 이름 정의
category_images = {
    "전체": "https://.../all.jpg",
    "한식": "https://.../korean.jpg",
    "중식": "https://.../chinese.jpg",
    # 생략
}

if "selected_category" not in st.session_state:
    st.session_state.selected_category = "전체"

# 콤보와 공유되는 상태
current = st.session_state.selected_category
new_selected = st.selectbox("🍱 콤보로 선택하기", list(category_images.keys()), index=list(category_images.keys()).index(current))
if new_selected != st.session_state.selected_category:
    st.session_state.selected_category = new_selected

# 이미지 UI (form으로 감싸 클릭 처리)
cols = st.columns(len(category_images))
for i, (label, url) in enumerate(category_images.items()):
    with cols[i]:
        with st.form(f"form_{label}"):
            st.image(url, caption=label, use_container_width=True)
            if st.form_submit_button("선택"):
                st.session_state.selected_category = label
                st.experimental_rerun()

# 선택값 출력
st.markdown(f"### ✅ 선택된 항목: **{st.session_state.selected_category}**")
