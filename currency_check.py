import os
from datetime import datetime
import pytz
import requests

# 1. Yahoo Finance API 호출 (최근 7일간의 데이터 포함하여 가져오기)
url = "https://query1.finance.yahoo.com/v8/finance/chart/AUDKRW=X?range=7d&interval=1d"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

response = requests.get(url, headers=headers)
response.raise_for_status()
data = response.json()

# 2. 데이터 추출 및 계산 (현재가, 전일종가, 1주일 평균)
try:
    # 현재 환율 및 전일 종가
    meta = data['chart']['result'][0]['meta']
    current_price = meta['regularMarketPrice']
    previous_close = meta['chartPreviousClose']
    
    # 1주일 평균 환율 계산 (최근 7일 종가 데이터 평균)
    indicators = data['chart']['result'][0]['indicators']['quote'][0]
    closes = indicators.get('close', [])
    
    # None 값(장이 열리지 않아 데이터가 없는 날짜) 제외
    valid_closes = [c for c in closes if c is not None]
    
    if valid_closes:
        avg_7d = sum(valid_closes) / len(valid_closes)
    else:
        avg_7d = current_price # 만약 데이터가 비어있을 경우 현재가로 임시 대체

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

# 4. 매수 단계 판단 로직 (최근 6개월 하락장 반영)
# ※ 서빈님 학비/체류비 송금 계획에 맞춰 언제든 금액(915, 930)을 변경하실 수 있습니다.
if current_price < 915:
    status = "🟢 1단계 적극매수"
elif current_price < 930:
    status = "🟡 2단계 분할매수"
else:
    status = "🔴 3단계 관망"

# 5. 커밋 메시지 텍스트 작성 (구글 챗 제목에 한눈에 보이게 배치)
# 예: [10-21 08:30] 환율 927.61원 (🔻 10.69원 하락) / <1주전 평균: 935.20원> / 🟡 2단계 분할매수
commit_msg = f"[{now_kst_short}] 환율 {current_price:,.2f}원 ({sign} {abs(change):,.2f}원 {change_type}) / <1주전 평균: {avg_7d:,.2f}원> / {status}"

print("생성된 커밋 메시지:", commit_msg)

# 6. GitHub Actions 워크플로가 읽을 수 있도록 파일로 저장
with open("commit_message.txt", "w", encoding="utf-8") as f:
    f.write(commit_msg)

# 7. 워크플로의 'git add history.csv' 단계 에러 방지용 이력 기록
with open("history.csv", "a", encoding="utf-8") as f:
    f.write(f"{now_kst_short},{current_price:,.2f},{change:,.2f},{avg_7d:,.2f}\n")
