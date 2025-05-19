import pyperclip

# ...

for i, item in enumerate(results):
    title = re.sub("<.*?>", "", item["title"])
    address = item['address']
    encoded_address = quote(address)
    map_url = f"https://map.naver.com/v5/search/{encoded_address}"

    st.markdown(f"### {title}")
    st.write(f"📍 주소: {address}")
    st.markdown(f"🗺️ [네이버 지도에서 보기]({map_url})")

    # ✅ 점심 운영 여부
    if is_lunch_open_now():
        st.success("✅ 현재 점심시간 운영 중")
    else:
        st.warning("⛔ 운영시간 외입니다 (점심 기준 11:00~14:00)")

    st.write(f"📞 전화번호: {item['telephone'] or '정보 없음'}")
    st.write(f"🔗 [홈페이지로 이동]({item['link']})")

    # ✅ 공유 복사 버튼
    st.markdown(f"🗣️ 친구에게 공유하기: `{map_url}`")
    if st.button(f"📋 링크 복사 ({i+1})"):
        pyperclip.copy(map_url)
        st.success("링크가 복사되었습니다! 카카오톡에 붙여넣기 해보세요 😊")

    # 이미지
    images = search_images(title)
    if images:
        st.image(images[0]['link'], width=300)

    # 블로그 후기
    with st.expander("📝 블로그 후기 보기"):
        blogs = search_blog_reviews(title)
        for blog in blogs:
            blog_title = re.sub("<.*?>", "", blog["title"])
            st.markdown(f"- [{blog_title}]({blog['link']})")

    st.divider()
