import os
from datetime import datetime
import pytz
import requests

# 1. Google Chat 웹훅 URL 로드
GOOGLE_CHAT_WEBHOOK = (
    os.environ.get("GOOGLE_CHAT_WEBHOOK")
    or os.environ.get("GOOGLE_CHAT_WEBHOOK_URL")
    or os.environ.get("CHAT_WEBHOOK_URL")
    or os.environ.get("WEBHOOK_URL")
)

# 2. 네이버 페이 증권 환율 API 호출
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

current_price = aud_data.get("closePrice")
change_price = aud_data.get("compareToPreviousClosePrice")
fluctuation_type = aud_data.get("compareToPreviousPrice", {}).get("text", "")

# 4. 등락 기호 처리 (안전한 분기문 처리)
if "상승" in fluctuation_type:
    sign = "[상승]"
elif "하락" in fluctuation_type:
    sign = "[하락]"
else:
    sign = "[보합]"

# 한국 시간 기준 타임스탬프
kst = pytz.timezone("Asia/Seoul")
now_kst = datetime.now(kst).strftime("%Y-%m-%d %H:%M")

# 5. Google Chat 메시지 작성
message_text = (
    f"[호주 달러(AUD) 환율 알림]\n"
    f"- 기준 시간: {now_kst}\n"
    f"- 현재 환율: {current_price}원\n"
    f"- 전일 대비: {sign} {fluctuation_type} {change_price}원"
)

print(message_text)

# 6. Google Chat 웹훅 발송
if GOOGLE_CHAT_WEBHOOK:
    payload = {"text": message_text}
    res = requests.post(GOOGLE_CHAT_WEBHOOK, json=payload)
    if res.status_code == 200:
        print("Google Chat 알림 전송 성공!")
    else:
        print(f"전송 실패 (상태 코드 {res.status_code}): {res.text}")
        res.raise_for_status()
else:
    print("경고: Google Chat 웹훅 URL 환경변수가 설정되어 있지 않습니다.")
