import os
from datetime import datetime
import pytz
import requests

# 1. Google Chat 웹훅 URL 로드
# GitHub Actions Secrets 또는 워크플로 env에 등록된 변수명을 순서대로 확인합니다.
GOOGLE_CHAT_WEBHOOK = (
    os.environ.get("GOOGLE_CHAT_WEBHOOK")
    or os.environ.get("GOOGLE_CHAT_WEBHOOK_URL")
    or os.environ.get("CHAT_WEBHOOK_URL")
    or os.environ.get("WEBHOOK_URL")
)

# 2. 네이버 페이 증권 환율 API 호출 (JSON 방식)
url = "https://m.stock.naver.com/front-api/marketIndex/prices?category=exchange&reutersCode=FX_USDKRW,FX_AUDKRW"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers)
response.raise_for_status()
data = response.json()

# 3. AUD 환율 데이터 추출
aud_data = None
for item in data.get("result", []):
    if item.get("reutersCode") == "FX_AUDKRW":
        aud_data = item
        break

if not aud_data:
    raise ValueError("호주 달러(AUD) 환율 정보를 가져오지 못했습니다.")

current_price = aud_data.get("closePrice")  # 현재 환율
change_price = aud_data.get("compareToPreviousClosePrice")  # 변동폭
fluctuation_type = aud_data.get("compareToPreviousPrice", {}).get("text", "")  # 상승/하락

# 한국 시간 기준 타임스탬프
kst = pytz.timezone("Asia/Seoul")
now_kst = datetime.now(kst).strftime("%Y-%m-%d %H:%M")

# 전일 대비 기호
sign = "🔺" if "상승" in fluctuation_type else ("🔻" if "하락
