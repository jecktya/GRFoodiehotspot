import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(layout="centered")
st.title("GPS 테스트 (탑레벨에서만 동작)")

# 1. URL에 lat, lon 파라미터가 없으면 JS로 자동 위치 요청
params = st.query_params
if "lat" not in params or "lon" not in params:
    js = """
    <script>
    if (window.self === window.top && navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                const lat = pos.coords.latitude;
                const lon = pos.coords.longitude;
                const newUrl = window.location.origin + window.location.pathname + `?lat=${lat}&lon=${lon}`;
                window.location.replace(newUrl);
            },
            (err) => {
                console.log("GPS 오류:", err);
            }
        );
    } else {
        console.log("iframe 내부이거나 geolocation 미지원");
    }
    </script>
    """
    html(js, height=0)

    st.markdown(
        "**앱을 최상위 창에서 열려면 [여기를 클릭](https://grfoodiehotspot.streamlit.app/)**  \n"
        "※ 탑레벨(iframe 없이)으로 열면 위치 권한 요청이 동작합니다."
    )
    st.write("위치 요청 중…")
    st.stop()

# 2. lat, lon 파라미터가 있으면 화면에 표시
try:
    lat = float(params["lat"][0])
    lon = float(params["lon"][0])
    st.success(f"위도: {lat:.6f}, 경도: {lon:.6f}")
except:
    st.error("위치 정보를 받아오지 못했습니다.")
