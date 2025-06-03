import streamlit as st
import requests
import re
import pytz
import pandas as pd
import math
from datetime import datetime
from streamlit.components.v1 import html

# ---------------------------------------------------
# 0. 페이지 설정 (모바일/PC 모두 친화적)
# ---------------------------------------------------
st.set_page_config(layout="centered")

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
def search_restaurants(query: str, display: int = 10, sort: str = "random"):
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
        st.error(f"❗️ 네이버 지역 검색 오류 ({res.status_code}): {errmsg}")
        return []

# ---------------------------------------------------
# 5. 네이버 블로그 글 수 조회 함수
# ---------------------------------------------------
@st.cache_data(ttl=1800, show_spinner=False)
def get_blog_count(keyword: str) -> int:
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

    a = math.sin(d_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# ---------------------------------------------------
# 7. 식당 데이터 가공 & 스코어 계산 함수
# ---------------------------------------------------
def process_and_score(items: list, user_lat: float, user_lon: float, radius_m: int,
                      lvl1: str, lvl2: str, lvl3: str):
    rows = []
    for item in items:
        raw_title = item.get("title", "")
        name = re.sub(r"<[^>]+>", "", raw_title)
        address = item.get("address", "")

        # 위도/경도 (mapy: 위도, mapx: 경도)
        try:
            place_lat = float(item.get("mapy", "0"))
            place_lon = float(item.get("mapx", "0"))
        except:
            continue

        # 거리 계산 및 필터링
        dist = haversine(user_lat, user_lon, place_lat, place_lon)
        if dist > radius_m:
            continue

        # 카테고리 문자열 분리
        cat_str = item.get("category", "")
        hierarchy = [s.strip() for s in cat_str.split(">")]

        # 대-중-소 필터링 (빈 문자열이면 모두 허용)
        if lvl1 and (not hierarchy or hierarchy[0] != lvl1):
            continue
        if lvl2 and (len(hierarchy) < 2 or hierarchy[1] != lvl2):
            continue
        if lvl3 and (len(hierarchy) < 3 or hierarchy[2] != lvl3):
            continue

        blog_count = get_blog_count(name)
        telephone = item.get("telephone", "")
        link = item.get("link", "")

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
# 8. 사용자 위치 감지 로직 (모바일 우선)
# ---------------------------------------------------
params = st.query_params
if "lat" in params and "lon" in params:
    try:
        user_lat = float(params["lat"][0])
        user_lon = float(params["lon"][0])
    except:
        user_lat, user_lon = None, None
else:
    # 모바일/PC 브라우저에 위치 권한 요청용 JS
    js = """
    <script>
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                const lat = pos.coords.latitude;
                const lon = pos.coords.longitude;
                const search = window.location.search;
                const params = new URLSearchParams(search);
                if (!params.has("lat") || !params.has("lon")) {
                    params.set("lat", lat);
                    params.set("lon", lon);
                    window.location.search = params.toString();
                }
            },
            (err) => {
                // 위치 권한 거부 시 안내
                window.parent.postMessage({type: "GEO_FAILED"}, "*");
            }
        );
    } else {
        window.parent.postMessage({type: "GEO_NOT_SUPPORTED"}, "*");
    }
    </script>
    """
    html(js, height=0)
    st.info("🔔 위치 권한을 허용해 주세요.")
    # 위치 권한이 허용되거나 거부될 때까지 여기서 멈춥니다
    st.stop()

# ---------------------------------------------------
# 9. Streamlit UI 시작
# ---------------------------------------------------
st.title("🍱 인기 맛집 검색 (거리 기반 자동 위치 감지)")

if user_lat is None or user_lon is None:
    st.error("❗️ 사용자 위치를 얻을 수 없습니다. 위치 권한을 허용했는지 확인하세요.")
    st.stop()
else:
    st.write(f"🔍 감지된 위치: 위도 {user_lat:.6f}, 경도 {user_lon:.6f}")

# 9.1. 반경 선택 (기본값 10km)
radius_option = st.selectbox("검색 반경 선택", ["1KM", "3KM", "5KM", "10KM"], index=3)
radius_map = {"1KM": 1000, "3KM": 3000, "5KM": 5000, "10KM": 10000}
radius_m = radius_map[radius_option]

# 9.2. 카테고리 대-중-소 선택 (선택 사항)
lvl1 = st.selectbox("대분류 선택 (선택 사항)", [""] + list(FOOD_CATEGORY_HIERARCHY.keys()))
if lvl1:
    lvl2 = st.selectbox("중분류 선택 (선택 사항)", [""] + list(FOOD_CATEGORY_HIERARCHY[lvl1].keys()))
else:
    lvl2 = ""
if lvl1 and lvl2:
    subs = FOOD_CATEGORY_HIERARCHY[lvl1][lvl2]
    if subs:
        lvl3 = st.selectbox("소분류 선택 (선택 사항)", [""] + subs)
    else:
        lvl3 = ""
else:
    lvl3 = ""

# 9.3. 추가 키워드 입력 (선택)
keyword = st.text_input("추가 키워드 입력 (예: 순두부, 김치찌개 등)")

# 9.4. 결과 개수 선택
display_count = st.slider("최대 결과 개수", min_value=5, max_value=30, value=10)

# 9.5. “검색” 버튼
if st.button("검색"):
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        st.error(
            "❗️ 네이버 API 키가 설정되지 않았습니다.\n"
            "Streamlit Cloud Settings → Secrets에서 "
            "`NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET`을 등록해 주세요."
        )
    else:
        # 검색어 조합: (lvl3 or lvl2 or lvl1 or keyword) + 맛집
        terms = []
        if lvl3:
            terms.append(lvl3)
        elif lvl2:
            terms.append(lvl2)
        elif lvl1:
            terms.append(lvl1)
        if keyword.strip():
            terms.append(keyword.strip())
        terms.append("맛집")
        query = " ".join(terms)

        # 네이버 지역 검색 (정렬: random)
        raw_items = search_restaurants(query, display=display_count, sort="random")

        # 가공 및 스코어 계산 (거리 필터 포함)
        df = process_and_score(raw_items, user_lat, user_lon, radius_m, lvl1, lvl2, lvl3)

        if df.empty:
            st.info("조건에 맞는 맛집이 없습니다.")
        else:
            # DataFrame 표시
            st.dataframe(
                df[
                    [
                        "name", "category_level1", "category_level2", "category_level3",
                        "blog_count", "distance_m", "score", "telephone", "address", "naver_link"
                    ]
                ],
                use_container_width=True
            )
            # 상위 5개 카드 형태로 출력
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
