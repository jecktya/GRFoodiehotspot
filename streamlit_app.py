import streamlit as st
import requests
import datetime

# 👉 네이버 API 인증 정보
NAVER_CLIENT_ID = "YOUR_CLIENT_ID"
NAVER_CLIENT_SECRET = "YOUR_CLIENT_SECRET"

# 👉 지역 검색 함수
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
        st.error("네이버 API 호출 실패")
        return []

# 👉 Streamlit UI
st.title("🍽 계룡시 점심시간 맛집 추천")

# 카테고리 선택
main_category = st.selectbox("음식 종류 선택", ["한식", "중식", "일식", "양식", "분식", "카페/디저트"])
sub_category = st.text_input("세부 메뉴 (예: 김치찌개, 파스타 등)")

# 검색 버튼
if st.button("맛집 검색"):
    query = f"계룡시 {main_category} {sub_category} 맛집"
    st.write(f"🔍 검색어: {query}")
    results = search_restaurants(query, display=10)

    for item in results:
        st.markdown(f"### {item['title'].replace('<b>', '').replace('</b>', '')}")
        st.write(f"📍 주소: {item['address']}")
        st.write(f"📞 전화번호: {item['telephone'] or '정보 없음'}")
        st.write(f"🔗 [홈페이지로 이동]({item['link']})")
        st.divider()
import streamlit as st
import requests
import datetime

# 👉 네이버 API 인증 정보
NAVER_CLIENT_ID = "YOUR_CLIENT_ID"
NAVER_CLIENT_SECRET = "YOUR_CLIENT_SECRET"

# 👉 지역 검색 함수
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
        st.error("네이버 API 호출 실패")
        return []

# 👉 Streamlit UI
st.title("🍽 계룡시 점심시간 맛집 추천")

# 카테고리 선택
main_category = st.selectbox("음식 종류 선택", ["한식", "중식", "일식", "양식", "분식", "카페/디저트"])
sub_category = st.text_input("세부 메뉴 (예: 김치찌개, 파스타 등)")

# 검색 버튼
if st.button("맛집 검색"):
    query = f"계룡시 {main_category} {sub_category} 맛집"
    st.write(f"🔍 검색어: {query}")
    results = search_restaurants(query, display=10)

    for item in results:
        st.markdown(f"### {item['title'].replace('<b>', '').replace('</b>', '')}")
        st.write(f"📍 주소: {item['address']}")
        st.write(f"📞 전화번호: {item['telephone'] or '정보 없음'}")
        st.write(f"🔗 [홈페이지로 이동]({item['link']})")
        st.divider()
