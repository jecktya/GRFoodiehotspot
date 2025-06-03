import streamlit as st
import requests
import re
import pandas as pd
import math
from bokeh.models import CustomJS
from bokeh.events import Event
from streamlit_bokeh_events import streamlit_bokeh_events

# ----------------------------------------
# 1. 스트림릿 페이지 설정
# ----------------------------------------
st.set_page_config(layout="centered")

# ----------------------------------------
# 2. NAVER API 키 (secrets.toml에 설정해 두셔야 합니다)
# ----------------------------------------
try:
    NAVER_CLIENT_ID = st.secrets["NAVER_CLIENT_ID"]
    NAVER_CLIENT_SECRET = st.secrets["NAVER_CLIENT_SECRET"]
except KeyError:
    NAVER_CLIENT_ID = None
    NAVER_CLIENT_SECRET = None

# ----------------------------------------
# 3. 음식 카테고리 대-중-소 구조
# ----------------------------------------
FOOD_CATEGORY_HIERARCHY = {
    "한식": {"전통한식": [], "김치찌개/된장찌개": [], "삼겹살": [], "불고기/갈비": []},
    "중식": {"중국집": [], "짜장면/짬뽕": []},
    "일식": {"초밥": [], "돈까스/우동/덮밥": []},
    "양식": {"파스타/스테이크": [], "피자/햄버거": []},
    "분식": {"떡볶이": [], "김밥/라면": []},
    "카페/디저트": {"카페": [], "빙수/요거트": []},
    "치킨": {"치킨전문점": []},
    "피자": {"피자전문점": []},
    "족발/보쌈": {"족발/보쌈전문점": []},
    "패스트푸드": {"패스트푸드": []},
    "뷔페": {"뷔페": []},
    "주점/호프": {"호프/요리주점": []}
}

# ----------------------------------------
# 4. 네이버 지역 검색 함수
# ----------------------------------------
@st.cache_data(ttl=1800, show_spinner=False)
def search_restaurants(query: str, display: int = 10, sort: str = "distance"):
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        return []
    url = "https://openapi.naver.com/v1/search/local.json"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {"query": query, "display": display, "start": 1, "sort": sort}
    res = requests.get(url, headers=headers, params=params)
    if res.status_code == 200:
        return res.json().get("items", [])
    else:
        try:
            errmsg = res.json().get("errorMessage", "")
        except:
            errmsg = ""
        st.error(f"❗️ 네이버 검색 오류 ({res.status_code}): {errmsg}")
        return []

# ----------------------------------------
# 5. 블로그 언급 수 조회 (스코어링용)
# ----------------------------------------
@st.cache_data(ttl=1800, show_spinner=False)
def get_blog_count(keyword: str) -> int:
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        return 0
    url = "https://openapi.naver.com/v1/search/blog.json"
    headers = {
        "X-Naver-Client-Id":     NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {"query": f"{keyword} 후기", "display": 1, "sort": "sim"}
    res = requests.get(url, headers=headers, params=params).json()
    return res.get("total", 0)

# ----------------------------------------
# 6. 거리 계산 (Haversine)
# ----------------------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # 지구 반지름 (미터)
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(d_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# ----------------------------------------
# 7. 검색 결과 가공 및 스코어링
# ----------------------------------------
def process_and_score(items: list, user_lat: float, user_lon: float, radius_m: int,
                      lvl1: str, lvl2: str, lvl3: str):
    rows = []
    for item in items:
        name = re.sub(r"<[^>]+>", "", item.get("title", ""))
        address = item.get("address", "")
        try:
            place_lat = float(item.get("mapy", "0"))
            place_lon = float(item.get("mapx", "0"))
        except:
            continue
        dist = haversine(user_lat, user_lon, place_lat, place_lon)
        if dist > radius_m:
            continue
        hierarchy = [s.strip() for s in item.get("category", "").split(">")]
        if lvl1 and (not hierarchy or hierarchy[0] != lvl1):
            continue
        if lvl2 and (len(hierarchy) < 2 or hierarchy[1] != lvl2):
            continue
        if lvl3 and (len(hierarchy) < 3 or hierarchy[2] != lvl3):
            continue
        blog_count = get_blog_count(name)
        telephone = item.get("telephone", "")
        link = item.get("link", "")
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
            "score": blog_count
        })
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    return df.sort_values(by="score", ascending=False).reset_index(drop=True)

# ----------------------------------------
# 8. IP 기반 폴백 (한국 범위 벗어나면 None 반환)
# ----------------------------------------
def get_user_location_ip():
    try:
        resp = requests.get("http://ip-api.com/json/").json()
        if resp.get("status") == "success":
            lat_ip, lon_ip = resp["lat"], resp["lon"]
            # 한국 범위: 위도 33~43, 경도 124~132
            if 33.0 <= lat_ip <= 43.0 and 124.0 <= lon_ip <= 132.0:
                return lat_ip, lon_ip
    except:
        pass
    return None, None

# ----------------------------------------
# 9. 세션 상태에 GPS 저장할 키 초기화
# ----------------------------------------
if "gps_lat" not in st.session_state:
    st.session_state["gps_lat"] = None
if "gps_lon" not in st.session_state:
    st.session_state["gps_lon"] = None

# ----------------------------------------
# 10. UI – 제목 및 안내
# ----------------------------------------
st.title("🍱 인기 맛집 검색 (GPS + IP 폴백)")

st.markdown(
    """
    - 모바일/PC 브라우저에서 “Allow location access” 팝업이 뜨면 반드시 허용해 주세요.  
    -  
    - GPS가 허용되지 않으면, IP 기반 위치를 쓰거나 한국 범위를 벗어나면 수동 입력폼을 띄웁니다.
    """
)

# ----------------------------------------
# 11. 검색 옵션
# ----------------------------------------
radius_option = st.selectbox("검색 반경 선택", ["1KM", "3KM", "5KM", "10KM"], index=3)
radius_map = {"1KM": 1000, "3KM": 3000, "5KM": 5000, "10KM": 10000}
radius_m = radius_map[radius_option]

lvl1 = st.selectbox("대분류 선택 (선택 사항)", [""] + list(FOOD_CATEGORY_HIERARCHY.keys()))
if lvl1:
    lvl2 = st.selectbox("중분류 선택 (선택 사항)", [""] + list(FOOD_CATEGORY_HIERARCHY[lvl1].keys()))
else:
    lvl2 = ""
if lvl1 and lvl2:
    subs = FOOD_CATEGORY_HIERARCHY[lvl1][lvl2]
    lvl3 = st.selectbox("소분류 선택 (선택 사항)", [""] + subs) if subs else ""
else:
    lvl3 = ""

keyword = st.text_input("추가 키워드 입력 (선택)")
display_count = st.slider("최대 결과 개수", min_value=5, max_value=30, value=10)

# ----------------------------------------
# 12. “GPS로 위치 가져오기” 버튼
# ----------------------------------------
if st.button("GPS로 위치 가져오기"):
    # Bokeh CustomJS 이벤트로 JS 실행 → 브라우저의 navigator.geolocation 호출
    js_code = """
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                const lat = pos.coords.latitude;
                const lon = pos.coords.longitude;
                const coords = {latitude: lat, longitude: lon};
                document.dispatchEvent(new CustomEvent("return_geolocation", {detail: coords}));
            },
            (err) => {
                document.dispatchEvent(new CustomEvent("return_geolocation", {detail: null}));
            }
        );
    } else {
        document.dispatchEvent(new CustomEvent("return_geolocation", {detail: null}));
    }
    """
    # streamlit_bokeh_events로 해당 JS 코드 실행 후, 이벤트 리스닝
    result = streamlit_bokeh_events(
        CustomJS(code=js_code),
        events="return_geolocation",
        key="get_location",
        refresh_on_update=False,
        override_height=0,
        debounce_time=100,
    )
    # 이벤트 결과가 있으면 세션 상태에 저장
    if result and "return_geolocation" in result:
        coords = result["return_geolocation"]
        if coords is not None:
            st.session_state["gps_lat"] = coords["latitude"]
            st.session_state["gps_lon"] = coords["longitude"]
        else:
            st.warning("GPS 권한을 받지 못했습니다. IP 기반 폴백이나 수동 입력을 해주세요.")

# ----------------------------------------
# 13. 현재 위치(확보된) 표시 or IP 폴백
# ----------------------------------------
user_lat = st.session_state["gps_lat"]
user_lon = st.session_state["gps_lon"]

if user_lat is None or user_lon is None:
    # GPS 못 받았으면 IP로 대체
    ip_loc = get_user_location_ip()
    if ip_loc != (None, None):
        user_lat, user_lon = ip_loc
        st.info(f"IP 기반 위치: 위도 {user_lat:.6f}, 경도 {user_lon:.6f}")
    else:
        # 한국 범위 내 IP도 안 잡히면 수동 입력 유도
        st.warning("자동으로 위치를 인식할 수 없습니다. 직접 위도/경도를 입력해 주세요.")
        user_lat = st.number_input("위도 입력", format="%.6f", key="manual_lat")
        user_lon = st.number_input("경도 입력", format="%.6f", key="manual_lon")
        if user_lat == 0.0 and user_lon == 0.0:
            st.stop()
        st.success(f"수동 입력 위치: 위도 {user_lat:.6f}, 경도 {user_lon:.6f}")

else:
    st.success(f"GPS로 감지된 위치: 위도 {user_lat:.6f}, 경도 {user_lon:.6f}")

# ----------------------------------------
# 14. “검색” 버튼 로직
# ----------------------------------------
if st.button("맛집 검색"):
    st.write(f"🔍 위치 기준: 위도 {user_lat:.6f}, 경도 {user_lon:.6f}")

    # 검색어 조합
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

    # 네이버 지역 검색 (거리 순 정렬)
    raw_items = search_restaurants(query, display=display_count, sort="distance")

    # 결과 가공 & 거리 필터링
    df = process_and_score(raw_items, user_lat, user_lon, radius_m, lvl1, lvl2, lvl3)

    if df.empty:
        st.info("조건에 맞는 맛집이 없습니다.")
    else:
        st.dataframe(
            df[[
                "name", "category_level1", "category_level2", "category_level3",
                "blog_count", "distance_m", "score", "telephone", "address", "naver_link"
            ]],
            use_container_width=True
        )
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
