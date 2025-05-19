import streamlit as st
import requests
import re
from datetime import datetime
from urllib.parse import quote
import pytz

# 썸네일 이미지
category_images = {
    "전체": "https://yourdomain.com/images/all.png",
    "한식": "https://yourdomain.com/images/korean.png",
    "중식": "https://yourdomain.com/images/chinese.png",
    "일식": "https://yourdomain.com/images/japanese.png",
    "양식": "https://yourdomain.com/images/western.png",
    "분식": "https://yourdomain.com/images/snack.png",
    "카페/디저트": "https://yourdomain.com/images/dessert.png"
}

NAVER_CLIENT_ID = st.secrets["naver_client_id"]
NAVER_CLIENT_SECRET = st.secrets["naver_client_secret"]

# 선택 상태 관리
params = st.experimental_get_query_params()
selected = params.get("cat", ["전체"])[0]
st.experimental_set_query_params(cat=selected)

st.markdown("### 🍽️ 음식 종류를 선택하세요")

# CSS 스타일: 가로 스크롤 + 선택 애니메이션
st.markdown("""
    <style>
    .scroll-menu {
        display: flex;
        overflow-x: auto;
        gap: 16px;
        padding-bottom: 12px;
        white-space: nowrap;
    }
    .card {
        flex: 0 0 auto;
        width: 130px;
        border-radius: 10px;
        border: 2px solid transparent;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        text-align: center;
    }
    .card:hover {
        transform: scale(1.05);
        cursor: pointer;
        box-shadow: 0 0 12px rgba(100, 100, 100, 0.3);
    }
    .selected {
        border: 3px solid #4CAF50 !important;
        box-shadow: 0 0 15px rgba(76, 175, 80, 0.6);
        transform: scale(1.07);
    }
    </style>
""", unsafe_allow_html=True)

# 이미지 카테고리 가로 스크롤 렌더링
st.markdown('<div class="scroll-menu">', unsafe_allow_html=True)
for name, url in category_images.items():
    selected_class = "card selected" if name == selected else "card"
    st.markdown(f"""
    <a href="/?cat={name}" style="text-decoration: none; color: inherit;">
        <div class="{selected_class}">
            <img src="{url}" style="width:100%; border-radius:8px;">
            <div style="margin-top:5px; font-weight:bold;">{name}</div>
        </div>
    </a>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown(f"### 🍱 현재 선택된 음식: **{selected}**")

# 세부 메뉴 입력
sub_category = st.text_input("세부 메뉴 (예: 김치찌개, 파스타 등)", key="sub_category")

# 시간 확인
seoul_tz = pytz.timezone("Asia/Seoul")
def get_seoul_time():
    return datetime.now(seoul_tz)

def is_lunch_open_now():
    now = get_seoul_time().time()
    return datetime.strptime("11:00", "%H:%M").time() <= now <= datetime.strptime("14:00", "%H:%M").time()

st.caption(f"현재 시간: {get_seoul_time().strftime('%Y-%m-%d %H:%M:%S')}")

# NAVER API 함수
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

# 검색 실행
query = f"계룡시 {sub_category} 맛집" if selected == "전체" else f"계룡시 {selected} {sub_category} 맛집"

if sub_category:
    st.write(f"🔍 검색어: {query}")
    results = search_restaurants(query, display=5)

    for i, item in enumerate(results):
        title = re.sub("<.*?>", "", item.get("title", ""))
        address = item.get("address", "")
        map_url = f"https://map.naver.com/v5/search/{quote(address)}"

        st.markdown(f"### {title}")
        st.write(f"📍 주소: {address}")
        st.markdown(f"[🗺️ 지도 보기]({map_url})")

        if is_lunch_open_now():
            st.success("✅ 점심시간 운영 중")
        else:
            st.warning("⏰ 점심시간 외")

        st.write(f"📞 전화번호: {item.get('telephone', '정보 없음')}")
        st.write(f"🔗 [홈페이지로 이동]({item.get('link', '')})")

        st.text_input("📋 공유 링크", value=map_url, key=f"share_{i}")

        images = search_images(title)
        if images:
            st.image(images[0]['link'], width=300)

        with st.expander("📝 블로그 후기 보기"):
            blogs = search_blog_reviews(title)
            for blog in blogs:
                blog_title = re.sub("<.*?>", "", blog.get("title", ""))
                st.markdown(f"- [{blog_title}]({blog['link']})")

        st.divider()
