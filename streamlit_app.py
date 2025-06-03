import streamlit as st
import requests
import re
import pandas as pd
import math
from streamlit.components.v1 import html

# ----------------------------------------
# 1. 페이지 설정
# ----------------------------------------
st.set_page_config(layout="centered")

# ----------------------------------------
# 2. NAVER API 키 (secrets.toml에 저장)
# ----------------------------------------
try:
    NAVER_CLIENT_ID = st.secrets["NAVER_CLIENT_ID"]
    NAVER_CLIENT_SECRET = st.secrets["NAVER_CLIENT_SECRET"]
except KeyError:
    NAVER_CLIENT_ID = None
    NAVER_CLIENT_SECRET = None

# ----------------------------------------
# 3. 거리 계산 함수 (Haversine)
# ----------------------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # 지구 반지름 (미터)
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(d_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# ----------------------------------------
# 4. 네이버 지역 검색 (API 호출)
# ----------------------------------------
@st.cache_data(ttl=1800)
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
        errmsg = res.json().get("errorMessage", "")
        st.error(f"❗️ 네이버 검색 오류 ({res.status_code}): {errmsg}")
        return []

# ----------------------------------------
# 5. 블로그 언급 수 조회 (스코어링용)
# ----------------------------------------
@st.cache_data(ttl=1800)
def get_blog_count(keyword: str) -> int:
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        return 0
    url = "https://openapi.naver.com/v1/search/blog.json"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {"query": f"{keyword} 후기", "display": 1, "sort": "sim"}
    res = requests.get(url, headers=headers, params=params).json()
    return res.get("total", 0)

# ----------------------------------------
# 6. 결과 가공 & 거리 필터 & 점수 매기기
# ----------------------------------------
def process_and_score(items: list, user_lat: float, user_lon: float, radius_m: int):
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
        telephone = item.get("telephone", "")
        link = item.get("link", "")
        rows.append({
            "name": name,
            "address": address,
            "telephone": telephone or "정보 없음",
            "naver_link": link or "",
            "blog_count": blog_count,
            "distance_m": dist,
            "score": blog_count
        })
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    return df.sort_values(by="score", ascending=False).reset_index(drop=True)

# ----------------------------------------
# 7. 세션 상태 초기화 (위도/경도 키)
# ----------------------------------------
if "user_lat" not in st.session_state:
    st.session_state["user_lat"] = None
if "user_lon" not in st.session_state:
    st.session_state["user_lon"] = None

# ----------------------------------------
# 8. URL 쿼리(param)에 lat, lon 없으면 탑레벨에서 JS 실행해 자동 위치 요청
# ----------------------------------------
params = st.query_params
if "lat" not in params or "lon" not in params:
    # 페이지 로드 시 즉시 실행되는 JS 코드 (탑레벨에서만 위치권한 요청)
    js = """
    <script>
    // iframe 내부가 아니면(=탑레벨일 때) 바로 위치 권한 요청
    if (window.self === window.top) {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                function(pos) {
                    const lat = pos.coords.latitude;
                    const lon = pos.coords.longitude;
                    const newUrl = window.location.origin + window.location.pathname + `?lat=${lat}&lon=${lon}`;
                    window.location.replace(newUrl);
                },
                function(err) {
                    console.log("GPS 권한 거부 또는 오류:", err);
                }
            );
        } else {
            console.log("Geolocation not supported.");
        }
    } else {
        console.log("iframe 내부이므로 자동 위치 요청을 건너뜀.");
    }
    </script>
    """
    html(js, height=0)

# ----------------------------------------
# 9. URL 쿼리에서 lat, lon 파싱 → 세션에 저장
# ----------------------------------------
if "lat" in params and "lon" in params:
    try:
        st.session_state["user_lat"] = float(params["lat"][0])
        st.session_state["user_lon"] = float(params["lon"][0])
    except:
        st.session_state["user_lat"] = None
        st.session_state["user_lon"] = None

# ----------------------------------------
# 10. 확보된 위치 표시 혹은 IP 기반 폴백
# ----------------------------------------
user_lat = st.session_state["user_lat"]
user_lon = st.session_state["user_lon"]

if user_lat is None or user_lon is None:
    # IP 기반 위치 시도 (한국 범위 확인)
    try:
        resp = requests.get("http://ip-api.com/json/").json()
        if resp.get("status") == "success":
            lat_ip, lon_ip = resp["lat"], resp["lon"]
            if 33.0 <= lat_ip <= 43.0 and 124.0 <= lon_ip <= 132.0:
                user_lat, user_lon = lat_ip, lon_ip
                st.info(f"IP 기반 위치: 위도 {user_lat:.6f}, 경도 {user_lon:.6f}")
    except:
        pass

if user_lat is None or user_lon is None:
    st.error("❗️ 위치를 자동으로 받아오지 못했습니다. 앱을 탑레벨(iframe 없이)으로 열거나, 브라우저 위치 권한을 확인하세요.")
    st.stop()
else:
    st.success(f"현재 위치: 위도 {user_lat:.6f}, 경도 {user_lon:.6f}")

# ----------------------------------------
# 11. 검색 옵션 설정 (반경, 키워드, 개수)
# ----------------------------------------
radius_option = st.selectbox("검색 반경 선택", ["1KM","3KM","5KM","10KM"], index=3)
radius_map = {"1KM":1000,"3KM":3000,"5KM":5000,"10KM":10000}
radius_m = radius_map[radius_option]

keyword = st.text_input("추가 키워드 (선택)")
display_count = st.slider("최대 결과 개수", min_value=5, max_value=30, value=10)

# ----------------------------------------
# 12. 맛집 검색 버튼 & 로직
# ----------------------------------------
if st.button("맛집 검색"):
    st.write(f"🔍 위치 기준: 위도 {user_lat:.6f}, 경도 {user_lon:.6f}")

    # 검색어 조합 (예: “맛집” + 추가 키워드)
    terms = []
    if keyword.strip():
        terms.append(keyword.strip())
    terms.append("맛집")
    query = " ".join(terms)

    raw_items = search_restaurants(query, display=display_count, sort="distance")
    df = process_and_score(raw_items, user_lat, user_lon, radius_m)

    if df.empty:
        st.info("조건에 맞는 맛집이 없습니다.")
    else:
        st.dataframe(
            df[["name","address","telephone","blog_count","distance_m","score","naver_link"]],
            use_container_width=True
        )
        st.markdown("### 🔥 TOP 5")
        for i, row in df.head(5).iterrows():
            st.markdown(f"#### {i+1}. {row['name']}")
            st.write(f"• **주소**: {row['address']}")
            st.write(f"• **거리**: {row['distance_m']:.0f} m")
            st.write(f"• **블로그 언급량**: {row['blog_count']}")
            st.write(f"• 📞 전화번호: {row['telephone']}")
            if row["naver_link"]:
                st.markdown(f"• 🔗 [네이버 정보 보기]({row['naver_link']})")
            st.divider()
