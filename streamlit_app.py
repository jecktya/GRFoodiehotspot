import streamlit as st
import requests
from datetime import datetime
import re

# 👉 네이버 API 인증 정보
NAVER_CLIENT_ID = "YOUR_CLIENT_ID"
NAVER_CLIENT_SECRET = "YOUR_CLIENT_SECRET"

# 🔍 지역 검색 API
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
        st.error("맛집 정보를 불러오는 데 실패했습니다.")
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

# 👉 Streamlit UI
st.title("🍱 계룡시 점심 맛집 추천기")

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
        st.markdown(f"### {title}")
        st.write(f"📍 주소: {item['address']}")
        st.write(f"📞 전화번호: {item['telephone'] or '정보 없음'}")
        st.write(f"🔗 [홈페이지로 이동]({item['link']})")

        # 이미지
        images = search_images(title)
        if images:
            st.image(images[0]['link'], width=300)

        # 블로그 후기
        with st.expander("📝 블로그 후기 보기"):
            blogs = search_blog_reviews(title)
            for blog in blogs:
                blog_title = re.sub("<.*?>", "", blog["title"])
                st.markdown(f"- [{blog_title}]({blog['link']})")

        st.divider()
