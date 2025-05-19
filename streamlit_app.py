import streamlit as st
import requests
import re
from datetime import datetime
from urllib.parse import quote
import pytz

# GitHub에서 가져온 음식 이미지
category_images = {
    "전체": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/all.jpg",
    "한식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/korean.jpg",
    "중식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/chinese.jpg",
    "일식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/japanese.jpg",
    "양식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/western.jpg",
    "분식": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/snack.jpg",
    "카페/디저트": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/dessert.jpg"
}

# NAVER API 키는 Streamlit Cloud의 secrets.toml로 관리
NAVER_CLIENT_ID = st.secrets["naver_client_id"]
NAVER_CLIENT_SECRET = st.secrets["naver_client_secret"]

# 카테고리 UI
st.markdown("## 음식 종류를 선택해주세요")

if "selected_category" not in st.session_state:
    st.session_state.selected_category = "전체"

cols = st.columns(len(category_images))
for idx, (cat, img_url) in enumerate(category_images.items()):
    with cols[idx]:
        st.image(img_url, use_column_width=True)
        if st.button(cat, key=f"cat_{idx}"):
            st.session_state.selected_category = cat
        if st.session_state.selected_category == cat:
            st.markdown("<div style='text-align:center; font-weight:bold; color:#4CAF50;'>✔ 선택됨</div>", unsafe_allow_html=True)

main_category = st.session_state.selected_category

# 세부 메뉴 입력
sub_category = st.text_input("세부 메뉴 입력 (예: 김치찌개, 파스타 등)", key="sub_category")

# 현재 시간 (KST)
seoul_tz = pytz.timezone("Asia/Seoul")
def get_seoul_time():
    return datetime.now(seoul_tz)

def is_lunch_open_now():
    now = get_seoul_time().time()
    return datetime.strptime("11:00", "%H:%M").time() <= now <= datetime.strptime("14:00", "%H:%M").time()

st.caption(f"현재 시간: {get_seoul_time().strftime('%Y-%m-%d %H:%M:%S')}")

# NAVER API로 맛집 검색
def search_restaurants(query, display=5):
    url = "https://openapi.naver.com/v1/search/local.json"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {
        "query": query,
        "display": display,
        "start": 1,
        "sort": "random"
    }
    res = requests.get(url, headers=headers, params=params)
    if res.status_code == 200:
        return res.json().get("items", [])
    else:
        st.error(f"검색 실패 - {res.status_code}")
        return []

def search_blog_reviews(query, display=2):
    url = "https://openapi.naver.com/v1/search/blog.json"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {
        "query": query + " 후기",
        "display": display,
        "sort": "sim"
    }
    res = requests.get(url, headers=headers, params=params)
    if res.status_code == 200:
        return res.json().get("items", [])
    return []

def search_images(query, display=1):
    url = "https://openapi.naver.com/v1/search/image"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {
        "query": query,
        "display": display,
        "sort": "sim"
    }
    res = requests.get(url, headers=headers, params=params)
    if res.status_code == 200:
        return res.json().get("items", [])
    return []

# 자동 검색 실행
if main_category == "전체":
    query = f"계룡시 {sub_category} 맛집"
else:
    query = f"계룡시 {main_category} {sub_category} 맛집"

if sub_category:
    st.write(f"🔍 탐색 중: {query}")
    results = search_restaurants(query, display=5)

    for i, item in enumerate(results):
        title = re.sub("<.*?>", "", item.get("title", ""))
        address = item.get("address", "")
        map_url = f"https://map.naver.com/v5/search/{quote(address)}"

        st.markdown(f"### 🍽 {title}")
        st.write(f"📍 주소: {address}")
        st.markdown(f"[🗺 지도 보기]({map_url})")

        if is_lunch_open_now():
            st.success("🕒 점심시간 운영 중")
        else:
            st.warning("⏰ 점심시간이 아닙니다")

        st.write(f"📞 전화: {item.get('telephone', '정보 없음')}")
        st.write(f"[🔗 홈페이지 이동]({item.get('link', '')})")

        st.text_input("🔗 공유할 링크", value=map_url, key=f"share_{i}")

        images = search_images(title)
        if images:
            st.image(images[0].get('link', ''), width=300)

        with st.expander("📝 블로그 후기 보기"):
            blogs = search_blog_reviews(title)
            for blog in blogs:
                blog_title = re.sub("<.*?>", "", blog.get("title", ""))
                st.markdown(f"- [{blog_title}]({blog.get('link', '')})")

        st.divider()
