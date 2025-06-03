import streamlit as st
import requests
import re
import pytz
from datetime import datetime
from urllib.parse import quote

# ---------------------------------------------------
# 1. Streamlit Secrets에서 NAVER API 키 가져오기
# ---------------------------------------------------
try:
    NAVER_CLIENT_ID = st.secrets["NAVER_CLIENT_ID"]
    NAVER_CLIENT_SECRET = st.secrets["NAVER_CLIENT_SECRET"]
except KeyError:
    NAVER_CLIENT_ID = None
    NAVER_CLIENT_SECRET = None

# ---------------------------------------------------
# 2. 서울(KST) 시간대 설정
# ---------------------------------------------------
KST = pytz.timezone("Asia/Seoul")


# ---------------------------------------------------
# 3. 카테고리별 이미지 URL 딕셔너리
# ---------------------------------------------------
category_images = {
    "한식":       "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/korean.jpg",
    "중식":       "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/chinese.jpg",
    "일식":       "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/japanese.jpg",
    "양식":       "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/western.jpg",
    "분식":       "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/snack.jpg",
    "카페/디저트": "https://raw.githubusercontent.com/jecktya/GRFoodiehotspot/main/food/dessert.jpg"
}


# ---------------------------------------------------
# 4. 네이버 지역 검색 (맛집 검색) 함수
# ---------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def search_restaurants(query: str, display: int = 5, sort: str = "random"):
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        return []

    url = "https://openapi.naver.com/v1/search/local.json"
    headers = {
        "X-Naver-Client-Id":     NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {
        "query":   query,
        "display": display,
        "start":   1,
        "sort":    sort
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get("items", [])
    else:
        try:
            err_msg = response.json().get("errorMessage", "")
        except:
            err_msg = ""
        st.error(f"지역 검색 API 오류 ({response.status_code}): {err_msg}")
        return []


# ---------------------------------------------------
# 5. 네이버 블로그 후기 검색 함수
# ---------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def search_blog_reviews(query: str, display: int = 2):
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        return []

    url = "https://openapi.naver.com/v1/search/blog.json"
    headers = {
        "X-Naver-Client-Id":     NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {
        "query":   f"{query} 후기",
        "display": display,
        "sort":    "sim"
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get("items", [])
    return []


# ---------------------------------------------------
# 6. 네이버 이미지 검색 함수
# ---------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def search_images(query: str, display: int = 1):
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        return []

    url = "https://openapi.naver.com/v1/search/image"
    headers = {
        "X-Naver-Client-Id":     NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {
        "query":   query,
        "display": display,
        "start":   1,
        "sort":    "sim",
        "filter":  "medium"
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get("items", [])
    return []


# ---------------------------------------------------
# 7. 현재 점심시간(11:00~14:00) 여부 판단 함수
# ---------------------------------------------------
def is_lunch_open_now() -> bool:
    now_kst = datetime.now(KST).time()
    start_lunch = datetime.strptime("11:00", "%H:%M").time()
    end_lunch   = datetime.strptime("14:00", "%H:%M").time()
    return start_lunch <= now_kst <= end_lunch


# ---------------------------------------------------
# 8. Streamlit 앱 제목
# ---------------------------------------------------
st.title("🍱 계룡시 점심 맛집 추천기")


# ---------------------------------------------------
# 9. 사이드바: 검색 옵션 UI
# ---------------------------------------------------
with st.sidebar:
    st.header("검색 옵션")

    # 9.1. “아무것도 선택되지 않은 상태”를 위해 안내 문구를 첫 번째 옵션으로 추가
    category_options = ["— 카테고리 선택 —"] + list(category_images.keys())
    selected_category = st.selectbox(
        label="음식 종류",
        options=category_options,
        index=0
    )

    # 9.2. 선택된 카테고리에 따른 이미지 미리보기
    if selected_category in category_images:
        st.markdown("---")
        st.markdown(
            f"""
            <div style="display:flex; flex-direction:column; align-items:center;">
                <img src="{category_images[selected_category]}" 
                     style="width:240px; border-radius:15px; 
                            border:4px solid #4CAF50; 
                            box-shadow:0 2px 18px rgba(76,175,80,0.10); 
                            margin-bottom:12px;">
                <div style="font-size:1.2em; color:#4CAF50; 
                            font-weight:bold; margin-top:7px;">
                    {selected_category}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 9.3. 세부 메뉴 입력 (선택)
    sub_category = st.text_input("세부 메뉴 (예: 김치찌개, 파스타 등)", "")

    # 9.4. 결과 개수 선택
    display_count = st.slider(
        "결과 개수 선택", 
        min_value=1, 
        max_value=10, 
        value=5
    )

    # 9.5. 정렬 기준 선택
    sort_option = st.selectbox(
        "정렬 기준", 
        ["random", "comment", "review"], 
        index=0
    )

    # 9.6. 검색 버튼
    search_btn = st.button("맛집 검색")


# ---------------------------------------------------
# 10. 검색 버튼 클릭 시 처리
# ---------------------------------------------------
if search_btn:
    # 10.1. 카테고리가 “— 카테고리 선택 —” 일 때 안내 메시지
    if selected_category not in category_images:
        st.warning("먼저 '음식 종류'를 선택해 주세요.")
    else:
        # 10.2. Secret이 누락된 경우에는 더 이상 진행하지 않고 에러 메시지 출력
        if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
            st.error(
                "❗️ 네이버 API 키가 설정되지 않았습니다.\n"
                "Streamlit Cloud의 Settings → Secrets 탭에서 "
                "`NAVER_CLIENT_ID`와 `NAVER_CLIENT_SECRET`을 등록해 주세요."
            )
        else:
            # 10.3. 쿼리 생성: 예) "계룡시 한식 김치찌개 맛집", sub_category가 비었으면 "계룡시 한식 맛집"
            if sub_category.strip() == "":
                query = f"계룡시 {selected_category} 맛집"
            else:
                query = f"계룡시 {selected_category} {sub_category} 맛집"

            st.write(f"🔍 검색어: **{query}**")

            # 10.4. 네이버 지역 검색 API 호출
            results = search_restaurants(query, display=display_count, sort=sort_option)

            # 10.5. 검색 결과가 없을 때
            if not results:
                st.info("🔎 검색 결과가 없습니다. 다른 키워드로 시도해 보세요.")
            else:
                # 10.6. 현재 시각(KST) 표시 및 점심시간 여부
                now_str    = datetime.now(KST).strftime("%Y-%m-%d %H:%M")
                lunch_flag = is_lunch_open_now()
                st.write(f"🕒 현재 시각 (KST): {now_str}")

                # 10.7. 결과를 2열 그리드로 배치
                cols = st.columns(2)
                for idx, item in enumerate(results):
                    col = cols[idx % 2]
                    with col:
                        # 10.7.1. 제목(HTML 태그 제거)
                        title_raw   = item.get("title", "")
                        title_clean = re.sub(r"<[^>]+>", "", title_raw)
                        st.markdown(f"### {title_clean}")

                        # 10.7.2. 주소 및 네이버 지도 링크
                        address = item.get("address", "")
                        if address:
                            encoded_address = quote(address)
                            map_url = f"https://map.naver.com/v5/search/{encoded_address}"
                            st.write(f"📍 주소: {address}")
                            st.markdown(f"🗺️ [지도에서 보기]({map_url})")
                        else:
                            st.write("📍 주소 정보 없음")

                        # 10.7.3. 점심시간 운영 여부
                        if lunch_flag:
                            st.success("✅ 현재 점심시간 운영 중 (11:00~14:00)")
                        else:
                            st.warning("⛔ 점심시간이 아닙니다 (11:00~14:00)")

                        # 10.7.4. 전화번호
                        phone = item.get("telephone", "")
                        st.write(f"📞 전화번호: {phone if phone else '정보 없음'}")

                        # 10.7.5. 홈페이지 링크
                        link = item.get("link", "")
                        if link:
                            st.markdown(f"🔗 [홈페이지로 이동]({link})")
                        else:
                            st.write("🔗 홈페이지 정보 없음")

                        # 10.7.6. 공유 링크 복사 (지도 URL)
                        if address:
                            st.text_input(
                                "📋 공유 링크 복사", 
                                value=map_url, 
                                key=f"share_{idx}"
                            )
                        else:
                            st.text_input(
                                "📋 공유 링크 복사", 
                                value="주소 정보 없음", 
                                key=f"share_{idx}"
                            )

                        # 10.7.7. 이미지 표시 (네이버 이미지 검색 API)
                        images = search_images(title_clean)
                        if images and images[0].get("link"):
                            # use_column_width 대신 use_container_width=True 로 변경
                            st.image(
                                images[0]["link"], 
                                caption=f"{title_clean} 이미지 예시", 
                                use_container_width=True
                            )
                        else:
                            st.write("🖼️ 이미지 정보 없음")

                        # 10.7.8. 블로그 후기 보기(확장 패널)
                        with st.expander("📝 블로그 후기 보기"):
                            blogs = search_blog_reviews(title_clean)
                            if not blogs:
                                st.write("후기 정보 없음")
                            else:
                                for blog in blogs:
                                    blog_title_raw = blog.get("title", "")
                                    blog_title     = re.sub(r"<[^>]+>", "", blog_title_raw)
                                    blog_link      = blog.get("link", "")
                                    if blog_link:
                                        st.markdown(f"- [{blog_title}]({blog_link})")
                                    else:
                                        st.write(f"- {blog_title} (링크 없음)")

                        st.divider()
