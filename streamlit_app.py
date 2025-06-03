import streamlit as st
from streamlit_geolocation import geolocation

st.set_page_config(layout="centered")
st.title("streamlit_geolocation 테스트")

st.markdown("""
- 앱을 **탑레벨**(iframe 없이)으로 열면, 페이지 로드 직후 자동으로 위치 권한을 요청합니다.  
- 허용하면 `location` 변수에 위도·경도가 저장됩니다.  
""")

# 페이지가 로드되면 즉시 위치 요청
location = geolocation(timeout=10_000)  # 타임아웃은 밀리초 단위

if location:
    lat = location.get("latitude")
    lon = location.get("longitude")
    if lat is not None and lon is not None:
        st.success(f"위도: {lat:.6f}, 경도: {lon:.6f}")
    else:
        st.warning("위치 정보를 가져오지 못했습니다.")
else:
    st.info("GPS 권한 요청을 기다리는 중이거나, 권한이 거부되었습니다.")
