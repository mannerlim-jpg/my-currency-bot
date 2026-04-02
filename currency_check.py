import requests
from bs4 import BeautifulSoup
import datetime
import pytz
import os

# 1. 네이버 금융에서 현재 환율 추출
url = "https://finance.naver.com/marketindex/exchangeList.naver"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
td_tit = soup.find('a', string=lambda text: text and '호주 AUD' in text).parent
rate_str = td_tit.find_next_sibling('td', class_='sale').text
current_rate = float(rate_str.replace(',', ''))

# 2. history.csv에서 이전 환율 읽어오기 및 변동 폭 계산
history_file = 'history.csv'
last_rate = None
trend_msg = ""

# 파일이 존재하면 열어서 가장 마지막 줄의 데이터를 가져옴
if os.path.exists(history_file):
    with open(history_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        if lines:
            try:
                # 마지막 줄을 쉼표(,)로 쪼개서 두 번째 값(환율)을 추출
                last_line = lines[-1].strip()
                last_rate = float(last_line.split(',')[1])
            except (IndexError, ValueError):
                pass # 파일 형식이 다르거나 첫 실행이라 비교할 숫자가 없으면 패스

# 변동 추이 텍스트 생성
if last_rate is not None:
    diff = current_rate - last_rate
    if diff > 0:
        trend_msg = f" (🔺{diff:.2f}원 상승)"
    elif diff < 0:
        trend_msg = f" (🔻{abs(diff):.2f}원 하락)"
    else:
        trend_msg = " (변동 없음)"

# 3. 환율 구간별 전략 판별
if current_rate <= 960: level = "🟢3단계 강력매수"
elif current_rate <= 995: level = "🟡2단계 적극매수"
elif current_rate <= 1015: level = "🟠1단계 주의/소액"
else: level = "🔴관망"

# 4. 깃허브 커밋 메시지용 텍스트 최종 결합
kst = pytz.timezone('Asia/Seoul')
now = datetime.datetime.now(kst).strftime('%m-%d %H:%M')

# 조합 결과 예시: [04-02 13:39] 환율 1047.18원 (🔻2.50원 하락) / 🔴관망
commit_msg = f"[{now}] 환율 {current_rate}원{trend_msg} / {level}"
print(f"생성된 메시지: {commit_msg}")

# 5. 텍스트 파일 및 히스토리 CSV 업데이트
with open('commit_message.txt', 'w', encoding='utf-8') as f:
    f.write(commit_msg)

with open(history_file, 'a', encoding='utf-8') as f:
    f.write(f"{now},{current_rate}\n")
