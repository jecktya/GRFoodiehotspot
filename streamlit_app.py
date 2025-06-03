import streamlit as st
import requests
import math
import re
import pandas as pd
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events

st.set_page_config(layout="centered")
st.title("GPS 및 IP 기반 위치 테스트")

# 세션 상태 초기화
if "gps_lat" not in st.session_state:
    st.session_state["gps_lat"] = None
if "gps_lon" not in st.session_state:
    st.session_state["gps_lon"] = None
if "tried_gps" not in st.session_state:
    st.session_state["tried_gps"] = False

st.markdown("""
- **Get Location** 버튼을 누르면 브라우저에서 GPS 권한을 요청합니다.
- 만약 GPS가 불가능하거나 권한이 거부되면, IP 기반 위치를 자동으로 시도합니다.
""")

# --- 1. "Get Location" 버튼 클릭 시 GPS 요청 ---
if st.button("Get Location"):
    # 단 한 번만 GPS 시도를 하도록 플래그 설정
    st.session_state["tried_gps"] = True

    js_code = """
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                const lat = pos.coords.latitude;
                const lon = pos.coords.longitude;
                document.dispatchEvent(
                    new CustomEvent("return_geolocation", {detail: {latitude: lat, longitude: lon}})
                );
            },
            (err) => {
                document.dispatchEvent(new CustomEvent("return_geolocation", {detail: null}));
            }
        );
    } else {
        document.dispatchEvent(new CustomEvent("return_geolocation", {detail: null}));
    }
    """
    result = streamlit_bokeh_events(
        CustomJS(code=js_code),
        events="return_geolocation",
        key="get_location",
        refresh_on_update=False,
        override_height=0,
        debounce_time=100,
    )
    if result and "return_geolocation" in result:
        coords = result["return_geolocation"]
        if coords:
            st.session_state["gps_lat"] = coords["latitude"]
            st.session_state["gps_lon"] = coords["longitude"]

# --- 2. GPS 결과 또는 IP 폴백 처리 ---
lat = st.session_state["gps_lat"]
lon = st.session_state["gps_lon"]

if st.session_state["tried_gps"] and (lat is None or lon is None):
    # GPS 시도 후에도 좌표가 없으면 IP 폴백 자동 실행
    try:
        resp = requests.get("http://ip-api.com/json/").json()
        if resp.get("status") == "success":
            lat_ip, lon_ip = resp["lat"], resp["lon"]
            # 간단히 한국 범위 예시 (선택적)
            if 33.0 <= lat_ip <= 43.0 and 124.0 <= lon_ip <= 132.0:
                lat, lon = lat_ip, lon_ip
                st.session_state["gps_lat"] = lat
                st.session_state["gps_lon"] = lon
                st.info(f"GPS를 못 받았습니다. IP 기반 위치 사용: 위도 {lat:.6f}, 경도 {lon:.6f}")
            else:
                st.warning("IP 기반 위치가 한국 범위를 벗어났습니다. 정확한 위치를 얻으려면 탑레벨에서 GPS 허용 후 다시 시도하세요.")
        else:
            st.error("IP 기반 위치를 가져오지 못했습니다.")
    except:
        st.error("IP-API 요청 중 오류가 발생했습니다.")

# --- 3. 위치 표시 ---
lat = st.session_state["gps_lat"]
lon = st.session_state["gps_lon"]

if lat is not None and lon is not None:
    st.success(f"현재 위치: 위도 {lat:.6f}, 경도 {lon:.6f}")
else:
    st.info("아직 위치 정보가 없습니다. 'Get Location' 버튼을 눌러 시도해 주세요.")

# --- 4. 추가 테스트: 입력한 좌표로 반경 내 맛집 검색 (옵션) ---
st.markdown("---")
st.header("추가: 입력한 좌표 기반 맛집 검색 테스트")

# 네이버 API 키 확인
try:
    NAVER_CLIENT_ID = st.secrets["NAVER_CLIENT_ID"]
    NAVER_CLIENT_SECRET = st.secrets["NAVER_CLIENT_SECRET"]
except KeyError:
    NAVER_CLIENT_ID = None
    NAVER_CLIENT_SECRET = None

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(d_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

@st.cache_data(ttl=1800)
def search_restaurants(query: str, display: int = 10, sort: str = "distance"):
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        return []
    url = "https://openapi.naver.com/v1/search/local.json"
    headers = {
        "X-Naver-Client-Id":     NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {"query": query, "display": display, "start": 1, "sort": sort}
    res = requests.get(url, headers=headers, params=params)
    if res.status_code == 200:
        return res.json().get("items", [])
    else:
        return []

@st.cache_data(ttl=1800)
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

def process_and_score(items, user_lat, user_lon, radius_m):
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
        blog_count = get_blog_count(name)
        rows.append({
            "name": name,
            "address": address,
            "blog_count": blog_count,
            "distance_m": dist
        })
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    return df.sort_values(by="blog_count", ascending=False).reset_index(drop=True)

# 사용자가 입력한 좌표(혹은 위에서 확보된 좌표) 사용
test_lat = st.session_state["gps_lat"] if st.session_state["gps_lat"] else st.number_input("테스트용 위도 입력", format="%.6f")
test_lon = st.session_state["gps_lon"] if st.session_state["gps_lon"] else st.number_input("테스트용 경도 입력", format="%.6f")

radius_km = st.selectbox("검색 반경", ["1KM", "3KM", "5KM", "10KM"], index=3)
radius_map = {"1KM":1000, "3KM":3000, "5KM":5000, "10KM":10000}
radius_m = radius_map[radius_km]

if st.button("맛집 검색 테스트"):
    if not test_lat or not test_lon:
        st.error("먼저 위도와 경도를 확보 또는 입력해 주세요.")
    else:
        query = "맛집"
        raw_items = search_restaurants(query, display=20, sort="distance")
        df = process_and_score(raw_items, test_lat, test_lon, radius_m)
        if df.empty:
            st.info("해당 반경 내 맛집이 없습니다.")
        else:
            st.dataframe(df[["name","address","blog_count","distance_m"]], use_container_width=True)
            st.markdown("### TOP 5")
            for i, row in df.head(5).iterrows():
                st.markdown(f"#### {i+1}. {row['name']}")
                st.write(f"• 주소: {row['address']}")
                st.write(f"• 거리: {row['distance_m']:.0f} m")
                st.write(f"• 블로그 언급수: {row['blog_count']}")
                st.divider()
