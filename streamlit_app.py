import streamlit as st
import requests
import re
from datetime import datetime
from urllib.parse import quote
import pytz

# 해당 커피드에서 보여줄 음식 콘텐츠 이미지 URL
category_images = {
    "전체": "https://i.imgur.com/B3mb5Xy.png",
    "한식": "https://i.imgur.com/Zs1UOWQ.jpg",
    "중식": "https://i.imgur.com/tqR3Fzm.jpg",
    "일식": "https://i.imgur.com/bnWnReA.jpg",
    "양식": "https://i.imgur.com/1fWgXre.jpg",
    "분식": "https://i.imgur.com/dmJv99K.jpg",
    "카페/디저트": "https://i.imgur.com/MGqjJHd.jpg"
}

# 배포할 NAVER API KEY (Streamlit Cloud Secrets에서 직접 검색)
NAVER_CLIENT_ID = st.secrets["naver_client_id"]
NAVER_CLIENT_SECRET = st.secrets["naver_client_secret"]

# 친화한 UI - 음식 카테고리 선택 (이미지 카드)
st.markdown("### 택시보는 림러브 음식 종류 선택")

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
sub_category = st.text_input("세부 메뉴 (예: 김치찌개, 파스타 등)", key="sub_category")

# 현재 시간 (KST)
seoul_tz = pytz.timezone("Asia/Seoul")
def get_seoul_time():
    return datetime.now(seoul_tz)

def is_lunch_open_now():
    now = get_seoul_time().time()
    return datetime.strptime("11:00", "%H:%M").time() <= now <= datetime.strptime("14:00", "%H:%M").time()

st.caption(f"현재 시간: {get_seoul_time().strftime('%Y-%m-%d %H:%M:%S')}")

# NAVER Search API

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

# 검색 버튼 누르지 않고 다영 시간에 따라 자동 검색
if main_category == "전체":
    query = f"계룡시 {sub_category} 맛집"
else:
    query = f"계룡시 {main_category} {sub_category} 맛집"

if sub_category:
    st.write(f"탐색: {query}")
    results = search_restaurants(query, display=5)

    for i, item in enumerate(results):
        title = re.sub("<.*?>", "", item.get("title", ""))
        address = item.get("address", "")
        map_url = f"https://map.naver.com/v5/search/{quote(address)}"

        st.markdown(f"### {title}")
        st.write(f"포함: {address}")
        st.markdown(f"[리트 구경에서 보기]({map_url})")

        if is_lunch_open_now():
            st.success("점심시간 운영 중")
        else:
            st.warning("점심 시간 외")

        st.write(f"통화: {item.get('telephone', '정보 없음')}")
        st.write(f"[홈페이지 이동]({item.get('link', '')})")

        st.text_input("공유할 리눅크", value=map_url, key=f"share_{i}")

        images = search_images(title)
        if images:
            st.image(images[0]['link'], width=300)

        with st.expander("보조 후기"):
            blogs = search_blog_reviews(title)
            for blog in blogs:
                blog_title = re.sub("<.*?>", "", blog.get("title", ""))
                st.markdown(f"- [{blog_title}]({blog['link']})")

        st.divider()
