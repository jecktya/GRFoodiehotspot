import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(layout="centered")
st.title("GPS 테스트 페이지")

# 1. URL 쿼리에 lat, lon이 없으면 JS로 자동 위치 요청
params = st.query_params
if "lat" not in params or "lon" not in params:
    js_code = """
    <script>
    if (window.self === window.top) {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (pos) => {
                    const lat = pos.coords.latitude;
                    const lon = pos.coords.longitude;
                    const newUrl = window.location.origin + window.location.pathname + `?lat=${lat}&lon=${lon}`;
                    window.location.replace(newUrl);
                },
                (err) => {
                    console.log("GPS 권한 거부 또는 오류:", err);
                }
            );
        } else {
            console.log("Geolocation 미지원");
        }
    } else {
        console.log("iframe 내부이므로 자동 요청 건너뜀");
    }
    </script>
    """
    html(js_code, height=0)
    st.write("GPS 정보를 요청 중입니다…")
    st.stop()

# 2. 쿼리에 lat, lon이 있으면 표시
try:
    lat = float(params.get("lat")[0])
    lon = float(params.get("lon")[0])
    st.success(f"위도: {lat:.6f}, 경도: {lon:.6f}")
except:
    st.error("위치 정보를 파싱하지 못했습니다.")
