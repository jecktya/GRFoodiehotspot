import streamlit as st
import requests
import math
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
- GPS가 불가능하거나 권한이 거부되면 즉시 IP 기반 위치를 시도합니다.
""")

# --- 1. "Get Location" 버튼 클릭 시 GPS 요청 ---
if st.button("Get Location"):
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

# --- 2. GPS 또는 IP 폴백 처리 ---
lat = st.session_state["gps_lat"]
lon = st.session_state["gps_lon"]

# GPS 시도 후에도 좌표가 없으면 즉시 IP 기반 위치로 대체
if st.session_state["tried_gps"] and (lat is None or lon is None):
    try:
        resp = requests.get("http://ip-api.com/json/").json()
        if resp.get("status") == "success":
            lat_ip, lon_ip = resp["lat"], resp["lon"]
            st.session_state["gps_lat"] = lat_ip
            st.session_state["gps_lon"] = lon_ip
            lat, lon = lat_ip, lon_ip
            st.info(f"GPS를 못 받았습니다. IP 기반 위치 사용: 위도 {lat:.6f}, 경도 {lon:.6f}")
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
