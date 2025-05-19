import streamlit as st
import requests
import re
from datetime import datetime
from urllib.parse import quote
import pytz  # ✅ 서울 시간대 적용을 위한 pytz 추가

# ✅ NAVER API 키: 평평한 구조로 Secrets에서 불러오기
NAVER_CLIENT_ID = st.secrets["naver_client_id"]
NAVER_CLIENT_SECRET = st.secrets["naver_client_secret"]

# 🔍 네이버 지역 검색
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
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()["items"]
    else:
        st.error(f"❌ 네이버 API 호출 실패 - 상태 코드: {response.status_code}")
        st.text(response.text)
        return []

# 📝 블로그 후기 검색
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
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()["items"]
    return []

# 🖼️ 이미지 검색
def search_images(query, display=1):
    url = "https://openapi.naver.com/v1/search/image"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {
        "query": query,
        "display": display,
        "start": 1,
        "sort": "sim",
        "filter": "medium"
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()["items"]
    return []

# ✅ 서울 시간대 기준 점심시간 여부 판단
def is_lunch_open_now():
    seoul_tz = pytz.timezone("Asia/Seoul")
    now = datetime.now(seoul_tz).time()
    return datetime.strptime("11:00", "%H:%M").time() <= now <= datetime.strptime("14:00", "%H:%M").time()

# ✅ 현재 시간 표시용 (서울 기준)
def get_seoul_time_str():
    seoul_tz = pytz.timezone("Asia/Seoul")
    now = datetime.now(seoul_tz)
    return now.strftime("%Y-%m-%d %H:%M:%S")

# 🌐 UI 시작
st.title("🍱 계룡시 점심 맛집 추천기")
st.caption(f"🕒 현재 대한민국 서울 시간: {get_seoul_time_str()}")

main_category = st.selectbox(
    "음식 종류 선택",
    ["한식", "중식", "일식", "양식", "분식", "카페/디저트"],
    key="main_category"
)

sub_category = st.text_input(
    "세부 메뉴 (예: 김치찌개, 파스타 등)",
    key="sub_category"
)

if st.button("맛집 검색", key="search_button"):
    query = f"계룡시 {main_category} {sub_category} 맛집"
    st.write(f"🔍 검색어: {query}")
    results = search_restaurants(query, display=5)

    for i, item in enumerate(results):
        title = re.sub("<.*?>", "", item["title"])
        address = item['address']
        encoded_address = quote(address)
        map_url = f"https://map.naver.com/v5/search/{encoded_address}"

        st.markdown(f"### {title}")
        st.write(f"📍 주소: {address}")
        st.markdown(f"🗺️ [네이버 지도에서 보기]({map_url})")

        if is_lunch_open_now():
            st.success("✅ 현재 점심시간 운영 중")
        else:
            st.warning("⛔ 운영시간 외입니다 (점심 기준 11:00~14:00)")

        st.write(f"📞 전화번호: {item['telephone'] or '정보 없음'}")
        st.write(f"🔗 [홈페이지로 이동]({item['link']})")

        st.text_input("📋 친구에게 보낼 링크 복사", value=map_url, key=f"share_link_{i}")

        images = search_images(title)
        if images:
            st.image(images[0]['link'], width=300)

        with st.expander("📝 블로그 후기 보기"):
            blogs = search_blog_reviews(title)
            for blog in blogs:
                blog_title = re.sub("<.*?>", "", blog["title"])
