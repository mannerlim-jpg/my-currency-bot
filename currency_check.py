import os
from datetime import datetime
import pytz
import requests

# 1. Yahoo Finance API 호출 (글로벌 서비스로 해외 IP 차단 없음)
url = "https://query1.finance.yahoo.com/v8/finance/chart/AUDKRW=X"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

response = requests.get(url, headers=headers)
response.raise_for_status()
data = response.json()

# 2. 데이터 추출 (현재가 및 전일종가)
try:
    result = data['chart']['result'][0]['meta']
    current_price = result['regularMarketPrice']
    previous_close = result['chartPreviousClose']
except (KeyError, IndexError, TypeError):
    raise ValueError("Yahoo Finance에서 환율 정보를 파싱할 수 없습니다.")

change = current_price - previous_close

# 3. 등락 기호 확인
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

# (참고) 과거 알림에 있던 '매수 단계' 텍스트를 위한 예시 로직 (필요에 따라 금액 기준 수정 가능)
if current_price < 920:
    status = "🟢 1단계 적극매수"
elif current_price < 940:
    status = "🟡 2단계 분할매수"
else:
    status = "🔴 3단계 관망"

# 4. 커밋 메시지 텍스트 작성 (예: [10-21 08:10] 환율 927.61원 (🔻 10.69원 하락) / 🟡 2단계 분할매수)
commit_msg = f"[{now_kst_short}] 환율 {current_price:,.2f}원 ({sign} {abs(change):,.2f}원 {change_type}) / {status}"

print("생성된 커밋 메시지:", commit_msg)

# 5. GitHub Actions 워크플로가 읽을 수 있도록 파일로 저장
with open("commit_message.txt", "w", encoding="utf-8") as f:
    f.write(commit_msg)

# 6. 워크플로의 'git add history.csv' 단계에서 에러가 나지 않도록 이력 파일에도 기록 추가
with open("history.csv", "a", encoding="utf-8") as f:
    f.write(f"{now_kst_short},{current_price:,.2f},{change:,.2f}\n")
