import os
from datetime import datetime
import pytz
import requests
from bs4 import BeautifulSoup

# 1. Google Chat 웹훅 URL 로드
GOOGLE_CHAT_WEBHOOK = (
    os.environ.get("GOOGLE_CHAT_WEBHOOK")
    or os.environ.get("GOOGLE_CHAT_WEBHOOK_URL")
    or os.environ.get("CHAT_WEBHOOK_URL")
    or os.environ.get("WEBHOOK_URL")
)

# 2. 네이버 금융 PC 웹페이지 스크래핑 (API 방식보다 차단 확률이 낮음)
url = "https://finance.naver.com/marketindex/exchangeDetail.naver?marketindexCd=FX_AUDKRW"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers)
response.raise_for_status()

# 3. HTML 파싱 및 데이터 추출
soup = BeautifulSoup(response.text, 'html.parser')
spot_con = soup.select_one('.spot .spt_con')

if not spot_con:
    raise ValueError("환율 정보를 찾을 수 없습니다. (HTML 구조 변경 가능성)")

current_price = spot_con.select_one('strong').text.strip()
change_price = spot_con.select_one('em').text.strip()

# 등락 기호 확인
class_list = spot_con.get('class', [])
if 'up' in class_list:
    change_type = '상승'
    sign = '[상승]'
elif 'down' in class_list:
    change_type = '하락'
    sign = '[하락]'
else:
    change_type = '보합'
    sign = '[보합]'

# 한국 시간 기준 타임스탬프
kst = pytz.timezone("Asia/Seoul")
now_kst = datetime.now(kst).strftime("%Y-%m-%d %H:%M")

# 4. Google Chat 메시지 작성
message_text = (
    f"🇦🇺 [호주 달러(AUD) 환율 알림]\n"
    f"- 기준 시간: {now_kst}\n"
    f"- 현재 환율: {current_price}원\n"
    f"- 전일 대비: {sign} {change_type} {change_price}원"
)

print(message_text)

# 5. Google Chat 웹훅 발송
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
