import streamlit as st
import requests
import re
import pytz
import pandas as pd
import math
from datetime import datetime

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
# 3. 음식 카테고리 대-중-소 계층 구조 사전
# ---------------------------------------------------
FOOD_CATEGORY_HIERARCHY = {
    "한식": {
        "전통한식": [],
        "김치찌개/된장찌개": [],
        "삼겹살": [],
        "불고기/갈비": []
    },
    "중식": {
        "중국집": [],
        "짜장면/짬뽕": []
    },
    "일식": {
        "초밥": [],
        "돈까스/우동/덮밥": []
    },
    "양식": {
        "파스타/스테이크": [],
        "피자/햄버거": []
    },
    "분식": {
        "떡볶이": [],
        "김밥/라면": []
    },
    "카페/디저트": {
        "카페": [],
        "빙수/요거트": []
    },
    "치킨": {
        "치킨전문점": []
    },
    "피자": {
        "피자전문점": []
    },
    "족발/보쌈": {
        "족발/보쌈전문점": []
    },
    "패스트푸드": {
        "패스트푸드": []
    },
    "뷔페": {
        "뷔페": []
    },
    "주점/호프": {
        "호프/요리주점": []
    }
}


# ---------------------------------------------------
# 4. 네이버 지역 검색 함수 (맛집 검색)
# ---------------------------------------------------
@st.cache_data(ttl=1800, show_spinner=False)
def search_restaurants(query: str, display: int = 10, sort: str = "review"):
    """
    - sort: "random", "comment", "review", "distance"
    """
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
    res = requests.get(url, headers=headers, params=params)
    if res.status_code == 200:
        return res.json().get("items", [])
    else:
        try:
            errmsg = res.json().get("errorMessage", "")
        except:
            errmsg = ""
        st.error(f"네이버 지역 검색 오류 ({res.status_code}): {errmsg}")
        return []


# ---------------------------------------------------
# 5. 네이버 블로그 글 수 조회 함수
# ---------------------------------------------------
@st.cache_data(ttl=1800, show_spinner=False)
def get_blog_count(keyword: str) -> int:
    """
    “keyword 후기” 로 블로그 검색 시 total 값을 가져와서
    블로그 게시글 수(언급량)를 리턴
    """
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        return 0

    url = "https://openapi.naver.com/v1/search/blog.json"
    headers = {
        "X-Naver-Client-Id":     NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {
        "query":   f"{keyword} 후기",
        "display": 1,
        "sort":    "sim"
    }
    res = requests.get(url, headers=headers, params=params).json()
    return res.get("total", 0)


# ---------------------------------------------------
# 6. 두 좌표 사이 거리 계산 (Haversine, 미터)
# ---------------------------------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # 지구 반지름 (미터)
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = math.sin(d_phi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(d_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


# ---------------------------------------------------
# 7. 식당 데이터 가공 & 스코어 계산 함수
# ---------------------------------------------------
def process_and_score(items: list, user_lat: float, user_lon: float, radius_m: int):
    """
    - items: 네이버 API items 리스트
    - FOOD_CATEGORY_HIERARCHY 기반으로 필터링 (선택 안 했으면 전체)
    - category 필드를 “대분류 > 중분류 > 소분류” 로 분리
    - 블로그 언급량(blog_count) 추가
    - user_lat/user_lon + radius_m에 따라 거리(dist) 필터링
    - score = blog_count
    """
    rows = []
    for item in items:
        # 1) HTML 태그 제거한 식당명
        raw_title = item.get("title", "")
        name = re.sub(r"<[^>]+>", "", raw_title)

        # 2) 주소
        address = item.get("address", "")

        # 3) 좌표 (mapy: 위도, mapx: 경도)
        try:
            place_lat = float(item.get("mapy", "0"))
            place_lon = float(item.get("mapx", "0"))
        except:
            continue

        # 4) 거리 계산 및 필터링
        dist = haversine(user_lat, user_lon, place_lat, place_lon)
        if dist > radius_m:
            continue

        # 5) category 문자열 → ["대분류", "중분류", "소분류"]
        cat_str = item.get("category", "")
        hierarchy = [s.strip() for s in cat_str.split(">")]

        # 6) 대분류/중분류/소분류 필터링 (None이면 모든 카테고리 허용)
        if selected_level1 != "— 선택 —":
            if not hierarchy or hierarchy[0] != selected_level1:
                continue
            if selected_level2 and hierarchy[1] != selected_level2:
                continue
            if selected_level3 and hierarchy[2] != selected_level3:
                continue

        # 7) 블로그 언급량 조회
        blog_count = get_blog_count(name)

        # 8) 기본 정보
        telephone = item.get("telephone", "")
        link = item.get("link", "")

        # 9) score 계산 (블로그 언급량)
        score = blog_count

        rows.append({
            "name": name,
            "address": address,
            "telephone": telephone or "정보 없음",
            "naver_link": link or "",
            "category_level1": hierarchy[0] if hierarchy else "",
            "category_level2": hierarchy[1] if len(hierarchy) >= 2 else "",
            "category_level3": hierarchy[2] if len(hierarchy) >= 3 else "",
            "blog_count": blog_count,
            "distance_m": dist,
            "score": score
        })

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df = df.sort_values(by="score", ascending=False).reset_index(drop=True)
    return df


# ---------------------------------------------------
# 8. Streamlit UI 시작
# ---------------------------------------------------
st.title("🍱 인기 맛집 검색 (거리 기반)")

# 8.1. 사용자 GPS 입력 (필수)
st.markdown("### 현재 위치 좌표 입력")
user_lat = st.number_input("위도 (latitude)", format="%.6f")
user_lon = st.number_input("경도 (longitude)", format="%.6f")

# 8.2. 반경 선택 (기본값 10km)
radius_option = st.selectbox("검색 반경 선택",
                             ["1KM", "3KM", "5KM", "10KM"], index=3)
radius_map = {"1KM": 1000, "3KM": 3000, "5KM": 5000, "10KM": 10000}
radius_m = radius_map[radius_option]

# 8.3. 카테고리 대-중-소 선택 (선택 사항)
selected_level1 = st.selectbox("대분류 선택", ["— 선택 —"] + list(FOOD_CATEGORY_HIERARCHY.keys()))
if selected_level1 in FOOD_CATEGORY_HIERARCHY:
    selected_level2 = st.selectbox("중분류 선택", [""] + list(FOOD_CATEGORY_HIERARCHY[selected_level1].keys()))
else:
    selected_level2 = ""
if selected_level1 in FOOD_CATEGORY_HIERARCHY and selected_level2 in FOOD_CATEGORY_HIERARCHY[selected_level1]:
    subs = FOOD_CATEGORY_HIERARCHY[selected_level1][selected_level2]
    if subs:
        selected_level3 = st.selectbox("소분류 선택", [""] + subs)
    else:
        selected_level3 = ""
else:
    selected_level3 = ""

# 8.4. 추가 키워드 입력 (선택)
keyword = st.text_input("추가 키워드 입력 (예: 순두부, 김치찌개 등)")

# 8.5. 결과 개수 선택
display_count = st.slider("최대 결과 개수", min_value=5, max_value=30, value=10)

# 8.6. “검색” 버튼
if st.button("검색"):
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        st.error(
            "❗️ 네이버 API 키가 설정되지 않았습니다.\n"
            "Streamlit Cloud Settings → Secrets에서 "
            "`NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET`을 등록해 주세요."
        )
    elif user_lat == 0 or user_lon == 0:
        st.error("❗️ 위치 검색을 위해 위도와 경도를 모두 입력해주세요.")
    else:
        # 1) 검색어 조합: “(level2 or level1 or keyword) + 맛집”
        terms = []
        if selected_level3:
            terms.append(selected_level3)
        elif selected_level2:
            terms.append(selected_level2)
        elif selected_level1 != "— 선택 —":
            terms.append(selected_level1)
        if keyword.strip():
            terms.append(keyword.strip())
        terms.append("맛집")
        query = " ".join(terms)

        # 2) 네이버 지역 검색 (정렬: 리뷰 수 순)
        raw_items = search_restaurants(query, display=display_count, sort="review")

        # 3) 가공 및 스코어 계산 (거리 필터 포함)
        df = process_and_score(raw_items, user_lat, user_lon, radius_m)

        if df.empty:
            st.info("조건에 맞는 맛집이 없습니다.")
        else:
            # 4) DataFrame 표시
            st.dataframe(
                df[
                    [
                        "name", "category_level1", "category_level2", "category_level3",
                        "blog_count", "distance_m", "score", "telephone", "address", "naver_link"
                    ]
                ],
                use_container_width=True
            )
            # 5) 상위 5개 카드 형태로 출력
            st.markdown("### 🔥 TOP 5")
            top5 = df.head(5)
            for i, row in top5.iterrows():
                st.markdown(f"#### {i+1}. {row['name']}")
                st.write(f"• **카테고리**: {row['category_level1']} / {row['category_level2']} / {row['category_level3']}")
                st.write(f"• **거리**: {row['distance_m']:.0f} m")
                st.write(f"• **블로그 언급량**: {row['blog_count']}")
                st.write(f"• 📞 전화번호: {row['telephone']}")
                st.write(f"• 📍 주소: {row['address']}")
                if row["naver_link"]:
                    st.markdown(f"• 🔗 [네이버 정보 보기]({row['naver_link']})")
                st.divider()
