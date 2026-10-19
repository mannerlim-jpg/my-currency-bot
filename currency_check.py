import json
import requests

# 네이버 페이 증권 환율 API 직접 호출 (HTML 크롤링보다 훨씬 안정적)
url = "https://m.stock.naver.com/front-api/marketIndex/prices?category=exchange&reutersCode=FX_USDKRW,FX_AUDKRW"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers)
data = response.json()

# AUD 환율 데이터 추출
aud_data = None
for item in data.get("result", []):
    if item.get("reutersCode") == "FX_AUDKRW":
        aud_data = item
        break

if aud_data:
    current_price = aud_data.get("closePrice")  # 현재 환율 (예: '905.50')
    change_price = aud_data.get("compareToPreviousClosePrice")  # 전일 대비 변동폭
    change_type = aud_data.get("compareToPreviousPrice", {}).get("text")  # 상승/하락 여부
    
    print(f"현재 호주 달러(AUD) 환율: {current_price}원 ({change_type} {change_price})")
    
    # ----------------------------------------------------
    # 기존 코드의 알림 전송 로직(텔레그램/디스코드 등)을 여기에 연결
    # ----------------------------------------------------
else:
    raise ValueError("호주 달러(AUD) 환율 정보를 찾을 수 없습니다.")
