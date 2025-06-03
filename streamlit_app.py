import streamlit as st
import requests
import re
import pandas as pd
import math
from streamlit.components.v1 import html

# ----------------------------------------
# 페이지 전반 설정
# ----------------------------------------
st.set_page_config(layout="centered")

# ----------------------------------------
# 1. Streamlit Secrets에서 NAVER API 키 가져오기
# ----------------------------------------
try:
    NAVER_CLIENT_ID = st.secrets["NAVER_CLIENT_ID"]
    NAVER_CLIENT_SECRET = st.secrets["NAVER_CLIENT_SECRET"]
except KeyError:
    NAVER_CLIENT_ID = None
    NAVER_CLIENT_SECRET = None

# ----------------------------------------
# 2. 음식 카테고리 대-중-소 계층 구조 사전
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
# 3. 네이버 지역 검색 함수
# ----------------------------------------
@st.cache_data(ttl=1800, show_spinner=False)
def search_restaurants(query: str, display: int = 10, sort: str = "random"):
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
        st.error(f"❗️ 네이버 지역 검색 오류 ({res.status_code}): {errmsg}")
        return []

# ----------------------------------------
# 4. 네이버 블로그 글 수 조회 함수
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
# 5. 두 좌표 사이 거리 계산 (Haversine)
# ----------------------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # 지구 반지름 (미터)
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# ----------------------------------------
# 6. 데이터 가공 & 스코어 계산
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
# 7. 네이버 Reverse Geocode: 위도/경도 → 행정동
# ----------------------------------------
@st.cache_data(ttl=1800, show_spinner=False)
def reverse_geocode_to_dong(lat: float, lon: float) -> str:
    """
    네이버 Map Reverse Geocode API를 사용해
    위도/경도로부터 ‘읍/면/동’(area3.name) 명칭을 반환합니다.
    """
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        return ""
    url = "https://naveropenapi.apigw.ntruss.com/map-reversegeocode/v2/gc"
    headers = {
        "X-NCP-APIGW-API-KEY-ID": NAVER_CLIENT_ID,
        "X-NCP-APIGW-API-KEY":    NAVER_CLIENT_SECRET
    }
    params = {
        "coords": f"{lon},{lat}",
        "output": "json",
        "orders": "admcode"
    }
    res = requests.get(url, headers=headers, params=params)
    if res.status_code != 200:
        return ""
    data = res.json().get("results", [])
    if not data:
        return ""
    region = data[0].get("region", {})
    dong_name = region.get("area3", {}).get("name", "")
    return dong_name or ""

# ----------------------------------------
# 8. 네이버 Geocode: 행정동 → 위도/경도
# ----------------------------------------
@st.cache_data(ttl=1800, show_spinner=False)
def geocode_dong_to_coords(dong_query: str):
    """
    네이버 Map Geocode API를 사용해
    ‘행정동’ 이름으로 위도/경도를 반환합니다.
    """
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        return None, None
    url = "https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode"
    headers = {
        "X-NCP-APIGW-API-KEY-ID": NAVER_CLIENT_ID,
        "X-NCP-APIGW-API-KEY":    NAVER_CLIENT_SECRET
    }
    params = {"query": dong_query}
    res = requests.get(url, headers=headers, params=params)
    if res.status_code != 200:
        return None, None
    addrs = res.json().get("addresses", [])
    if not addrs:
        return None, None
    # 첫번째 결과 사용
    lat = float(addrs[0].get("y", "0"))
    lon = float(addrs[0].get("x", "0"))
    return lat, lon

# ----------------------------------------
# 9. 사용자 위치 가져오기 (GPS → IP 폴백)
# ----------------------------------------
def get_user_location():
    params = st.query_params
    # (1) URL 파라미터에 lat, lon 있으면 GPS 사용
    if "lat" in params and "lon" in params:
        try:
            return float(params["lat"][0]), float(params["lon"][0])
        except:
            pass
    # (2) IP 기반으로 대략 위치
    try:
        resp = requests.get("http://ip-api.com/json/").json()
        if resp.get("status") == "success":
            return resp["lat"], resp["lon"]
    except:
        pass
    return None, None

# ----------------------------------------
# 10. 현재 사용자 위치
# ----------------------------------------
user_lat, user_lon = get_user_location()
if user_lat is None or user_lon is None:
    user_lat, user_lon = 0.0, 0.0

# ----------------------------------------
# 11. UI – 제목 및 위치 표시
# ----------------------------------------
st.title("🍱 인기 맛집 검색 (행정동 기반)")

# 11.1. ‘새 창으로 열기’ 버튼 (탑레벨 실행 유도)
st.markdown(
    "[💡 새 창으로 전체화면 열기](#){target=\"_blank\"}  \n"
    "※ 탑레벨(iframe 없이)에서 열면 GPS 권한 요청이 정상 동작할 수 있습니다.",
    unsafe_allow_html=True
)

# 11.2. 행정동 이름 계산
dong_name = ""
if user_lat == 0.0 and user_lon == 0.0:
    st.markdown("**현재 위치:** (허용되지 않음 / IP 확인 중)")
else:
    # IP 기반 좌표가 한국 범위(위도 33~43, 경도 124~132) 내에 있는지 확인
    if 33.0 <= user_lat <= 43.0 and 124.0 <= user_lon <= 132.0:
        dong_name = reverse_geocode_to_dong(user_lat, user_lon)
    # 범위 밖이면 자동으로 비워두고 사용자 입력 유도
    if dong_name:
        st.markdown(f"**현재 위치:** {dong_name} (위도 {user_lat:.6f}, 경도 {user_lon:.6f})")
    else:
        st.markdown(f"**현재 위치:** (IP 기반 위치: 위도 {user_lat:.6f}, 경도 {user_lon:.6f})")

# 11.3. 위치가 한국 범위 밖이거나 행정동을 못 받을 때, 수동 입력폼
manual_lat = manual_lon = None
if not dong_name and (user_lat == 0.0 and user_lon == 0.0 or not (33.0 <= user_lat <= 43.0 and 124.0 <= user_lon <= 132.0)):
    st.warning("자동으로 행정동을 감지할 수 없습니다. 직접 읍/면/동을 입력해 주세요.")
    manual_dong = st.text_input("읍/면/동 입력 (예: 강남구 역삼동)")
    if manual_dong:
        lat_temp, lon_temp = geocode_dong_to_coords(manual_dong)
        if lat_temp and lon_temp:
            user_lat, user_lon = lat_temp, lon_temp
            dong_name = manual_dong
            st.success(f"입력된 위치: {dong_name} (위도 {user_lat:.6f}, 경도 {user_lon:.6f})")
        else:
            st.error("해당 읍/면/동은 찾을 수 없습니다. 다시 입력해 주세요.")

# ----------------------------------------
# 12. UI – 검색 옵션
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
# 13. “검색” 버튼 로직
# ----------------------------------------
if st.button("검색"):
    # 13.1. GPS 권한 요청 (탑레벨에서만 작동)
    if user_lat == 0.0 and user_lon == 0.0:
        js = """
        <script>
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (pos) => {
                    const lat = pos.coords.latitude;
                    const lon = pos.coords.longitude;
                    const { protocol, host, pathname } = window.location;
                    const newUrl = `${protocol}//${host}${pathname}?lat=${lat}&lon=${lon}`;
                    window.parent.location.href = newUrl;
                },
                (err) => {
                    window.parent.postMessage({type: "GEO_FAILED"}, "*");
                }
            );
        } else {
            window.parent.postMessage({type: "GEO_NOT_SUPPORTED"}, "*");
        }
        </script>
        """
        html(js, height=0)
        st.info("🔔 위치 권한을 허용해 주세요 또는 IP 기반 위치/수동 입력이 사용됩니다.")
        st.stop()

    # 13.2. 확정된 ‘위도/경도 / 행정동’ 표시
    st.write(f"🔍 감지된 위치: {dong_name or '불명'} (위도 {user_lat:.6f}, 경도 {user_lon:.6f})")

    # 13.3. 검색어 조합
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

    # 13.4. 네이버 지역 검색
    raw_items = search_restaurants(query, display=display_count, sort="random")

    # 13.5. 결과 가공 및 거리 필터
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
