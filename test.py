import requests

# 네이버 API 인증 정보 입력
NAVER_CLIENT_ID = "YOUR_CLIENT_ID"
NAVER_CLIENT_SECRET = "YOUR_CLIENT_SECRET"

# 요청 설정
headers = {
    "X-Naver-Client-Id": NAVER_CLIENT_ID,
    "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
}
params = {"query": "계룡시 한식", "display": 1}

# API 호출
res = requests.get("https://openapi.naver.com/v1/search/local.json", headers=headers, params=params)

# 결과 출력
print("Status Code:", res.status_code)
print("Response:")
print(res.text)
