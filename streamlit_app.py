import streamlit as st
import requests
import re
import pytz
import pandas as pd
from datetime import datetime
from urllib.parse import quote

# ---------------------------------------------------
# 1. Streamlit Secrets에서 NAVER API 키 가져오기
# ---------------------------------------------------
try:
    NAVER_CLIENT_ID = st.secrets["NAVER_CLIENT_ID"]
    NAVER_CLIENT_SECRET = st.secrets["NAVER_CLIENT_SECRET"]
except KeyError:
    NAVER_CLIENT_ID = None
    NAVER_CLIENT_SECRET = None

# ---------------------------------------------------
# 2. 서울(KST) 시간대 설정
# ---------------------------------------------------
KST = pytz.timezone("Asia/Seoul")


# ---------------------------------------------------
# 3. “음식” 관련 카테고리 대분류 리스트
# ---------------------------------------------------
FOOD_CATEGORIES = [
    "한식", "중식", "일식", "양식", "분식",
    "카페/디저트", "치킨", "피자", "족발/보쌈",
    "패스트푸드", "뷔페", "주점/호프"
]

# ---------------------------------------------------
# 4. 네이버 지역 검색 함수 (맛집 검색)
# ---------------------------------------------------
@st.cache_data(ttl=1800, show_spinner=False)
def search_restaurants(query: str, display: int = 10, sort: str = "review"):
    """
    - sort: "random", "comment", "review", "distance"
    """
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        return []

    url = "https://openapi.naver.com/v1/search/local.json"
    headers = {
        "X-Naver-Client-Id":     NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {
        "query":   query,
        "display": display,
        "start":   1,
        "sort":    sort
    }
    res = requests.get(url, headers=headers, params=params)
    if res.status_code == 200:
        return res.json().get("items", [])
    else:
        try:
            errmsg = res.json().get("errorMessage", "")
        except:
            errmsg = ""
        st.error(f"네이버 지역 검색 오류 ({res.status_code}): {errmsg}")
        return []


# ---------------------------------------------------
# 5. 네이버 블로그 글 수 조회 함수
# ---------------------------------------------------
@st.cache_data(ttl=1800, show_spinner=False)
def get_blog_count(keyword: str) -> int:
    """
    “keyword 후기” 로 블로그 검색 시 total 값을 가져와서
    블로그 게시글 수(언급량)를 리턴
    """
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        return 0

    url = "https://openapi.naver.com/v1/search/blog.json"
    headers = {
        "X-Naver-Client-Id":     NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {
        "query":   f"{keyword} 후기",
        "display": 1,    # 실제 게시물은 하나만 받아도 total을 쓸 수 있음
        "sort":    "sim"
    }
    res = requests.get(url, headers=headers, params=params).json()
    return res.get("total", 0)


# ---------------------------------------------------
# 6. 현재 점심시간 여부 판단 함수
# ---------------------------------------------------
def is_lunch_open_now() -> bool:
    now_kst = datetime.now(KST).time()
    start_lunch = datetime.strptime("11:00", "%H:%M").time()
    end_lunch   = datetime.strptime("14:00", "%H:%M").time()
    return start_lunch <= now_kst <= end_lunch


# ---------------------------------------------------
# 7. 식당 데이터 가공 & 스코어 계산 함수
# ---------------------------------------------------
def process_and_score(items: list) -> pd.DataFrame:
    """
    - items: 네이버 API items 리스트
    - FOOD_CATEGORIES 기반으로 필터링
    - category 필드를 “대분류 > 중분류 > 소분류” 로 분리
    - 블로그 언급량(blog_count) 추가
    - 최종 score = blog_count (가중치는 필요 시 조정 가능)
    """
    rows = []
    for item in items:
        # 1) HTML 태그 제거한 식당명
        raw_title = item.get("title", "")
        name = re.sub(r"<[^>]+>", "", raw_title)

        # 2) 주소
        address = item.get("address", "")

        # 3) category 문자열 → ["대분류", "중분류", "소분류"]
        cat_str = item.get("category", "")
        hierarchy = [s.strip() for s in cat_str.split(">")]

        # 4) 대분류만 음식 카테고리인지 필터링
        if not hierarchy or hierarchy[0] not in FOOD_CATEGORIES:
            continue

        # 5) 블로그 언급량 조회
        blog_count = get_blog_count(name)

        # 6) 기본 정보(네이버 제공)를 함께 수집
        telephone = item.get("telephone", "")
        link = item.get("link", "")

        # 7) score 계산 (블로그 언급량 그대로 사용)
        score = blog_count

        rows.append({
            "name": name,
            "address": address,
            "telephone": telephone or "정보 없음",
            "naver_link": link or "",
            "category_level1": hierarchy[0],
            "category_level2": hierarchy[1] if len(hierarchy) >= 2 else "",
            "category_level3": hierarchy[2] if len(hierarchy) >= 3 else "",
            "blog_count": blog_count,
            "score": score
        })

    # DataFrame으로 변환
    df = pd.DataFrame(rows)
    # score 내림차순 정렬
    df = df.sort_values(by="score", ascending=False).reset_index(drop=True)
    return df


# ---------------------------------------------------
# 8. Streamlit UI 시작
# ---------------------------------------------------
st.title("🍱 계룡시 인기 맛집 (음식 카테고리만)")

# 8.1. 검색 옵션: “세부 키워드” 입력 (예: “김치찌개”)
keyword = st.text_input("원하는 메뉴나 키워드를 입력하세요 (선택)", "")

# 8.2. 결과 개수 선택
display_count = st.slider("결과 개수", min_value=5, max_value=20, value=10)

# 8.3. 검색 버튼
if st.button("검색"):
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        st.error(
            "❗️ 네이버 API 키가 설정되지 않았습니다.\n"
            "Streamlit Cloud Settings → Secrets에서 "
            "`NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET`을 등록해 주세요."
        )
    else:
        # 1) 검색어 조합: “계룡시” + keyword(없으면 “맛집”만)
        if keyword.strip():
            query = f"계룡시 {keyword.strip()} 맛집"
        else:
            query = "계룡시 맛집"

        # 2) 네이버 지역 검색 (기본 정렬: 리뷰 수 순)
        raw_items = search_restaurants(query, display=display_count, sort="review")

        # 3) 가공 및 스코어 계산 → DataFrame 반환
        df = process_and_score(raw_items)

        if df.empty:
            st.info("조건에 맞는 음식 카테고리 맛집이 없습니다.")
        else:
            # 4) DataFrame 표시 (인터랙티브 테이블)
            st.dataframe(
                df[
                    [
                        "name", "category_level1", "category_level2", "category_level3",
                        "blog_count", "score", "telephone", "address", "naver_link"
                    ]
                ],
                use_container_width=True
            )

            # 5) 상위 5개를 별도 카드 형태로 강조 출력
            st.markdown("### 🔥 TOP 5 인기 맛집")
            top5 = df.head(5)
            for i, row in top5.iterrows():
                st.markdown(f"#### {i+1}. {row['name']}")
                st.write(f"• **카테고리(대/중/소)**: {row['category_level1']} / {row['category_level2']} / {row['category_level3']}")
                st.write(f"• **블로그 언급량**: {row['blog_count']}")
                st.write(f"• **통합 점수(블로그 언급량 기준)**: {row['score']}")
                st.write(f"• 📞 전화번호: {row['telephone']}")
                st.write(f"• 📍 주소: {row['address']}")
                if row["naver_link"]:
                    st.markdown(f"• 🔗 [네이버 정보 보기]({row['naver_link']})")
                st.divider()
