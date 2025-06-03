import streamlit as st
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events

st.set_page_config(layout="centered")
st.title("GPS 테스트 (streamlit-bokeh-events)")

# 세션 상태에 위도/경도 저장용 변수 초기화
if "gps_lat" not in st.session_state:
    st.session_state["gps_lat"] = None
if "gps_lon" not in st.session_state:
    st.session_state["gps_lon"] = None

st.markdown("""
- **Get Location** 버튼을 누르면 브라우저에서 GPS 권한을 요청합니다.
- 권한을 허용하면 위도/경도가 화면에 표시됩니다.
""")

if st.button("Get Location"):
    # CustomJS로 navigator.geolocation 호출 → 'return_geolocation' 이벤트 발생
    js = """
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                const lat = pos.coords.latitude;
                const lon = pos.coords.longitude;
                document.dispatchEvent(new CustomEvent("return_geolocation", {
                    detail: { latitude: lat, longitude: lon }
                }));
            },
            (err) => {
                document.dispatchEvent(new CustomEvent("return_geolocation", { detail: null }));
            }
        );
    } else {
        document.dispatchEvent(new CustomEvent("return_geolocation", { detail: null }));
    }
    """
    result = streamlit_bokeh_events(
        CustomJS(code=js),
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
        else:
            st.warning("GPS 권한이 없거나 오류가 발생했습니다.")

lat = st.session_state["gps_lat"]
lon = st.session_state["gps_lon"]

if lat is not None and lon is not None:
    st.success(f"위도: {lat:.6f}, 경도: {lon:.6f}")
else:
    st.info("아직 위치 정보가 없습니다. 'Get Location' 버튼을 눌러 시도해 주세요.")
