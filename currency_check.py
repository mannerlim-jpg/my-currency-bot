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

# 2. Yahoo Finance API 호출 (글로벌 서비스로 해외 IP 차단 없음)
url = "https://query1.finance.yahoo.com/v8/finance/chart/AUDKRW=X"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

response = requests.get(url, headers=headers)
response.raise_for_status()
data = response.json()

# 3. 데이터 추출 (현재가 및 전일종가)
try:
    result = data['chart']['result'][0]['meta']
    current_price = result['regularMarketPrice']
    previous_close = result['chartPreviousClose']
except (KeyError, IndexError, TypeError):
    raise ValueError("Yahoo Finance에서 환율 정보를 파싱할 수 없습니다.")

change = current_price - previous_close

# 4. 등락 기호 확인
if change > 0:
    change_type = '상승'
    sign = '🔺'
elif change < 0:
    change_type = '하락'
    sign = '🔻'
else:
    change_type = '보합'
    sign = '➖'

# 한국 시간 기준 타임스탬프 (월-일 시:분)
kst = pytz.timezone("Asia/Seoul")
now_kst_short = datetime.now(kst).strftime("%m-%d %H:%M")

# 5. 스마트폰 푸시 알림에서 바로 보이도록 첫 줄에 핵심 내용 배치
message_text = (
    f"🇦🇺 [{now_kst_short}] 환율 {current_price:,.2f}원 ({sign}{abs(change):,.2f}원)\n"
    f"호주 달러(AUD) 알림이 도착했습니다."
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
