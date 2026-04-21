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

if os.path.exists(history_file):
    with open(history_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        if lines:
            try:
                last_line = lines[-1].strip()
                last_rate = float(last_line.split(',')[1])
            except (IndexError, ValueError):
                pass

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

# 4. 시간대 설정 (KST)
kst = pytz.timezone('Asia/Seoul')
now = datetime.datetime.now(kst).strftime('%m-%d %H:%M')

# 5. [핵심 수정항목] 커밋 메시지 제목과 본문(링크) 구성
# 제목: 구글 챗 말풍선 제목에 표시됩니다.
commit_title = f"[{now}] 환율 {current_rate}원{trend_msg} / {level}"

# 본문: 제목 아래에 표시되며, 클릭 가능한 링크를 포함합니다.
# 사용자님의 GitHub 저장소 경로(mannerlim-jpg/my-currency-bot)를 반영했습니다.
csv_link = "👉 상세 기록 확인: https://github.com/mannerlim-jpg/my-currency-bot/blob/main/history.csv"

# 제목과 본문을 결합 (빈 줄 '\n\n'이 매우 중요합니다)
full_commit_message = f"{commit_title}\n\n{csv_link}"

print(f"생성된 제목: {commit_title}")

# 6. 텍스트 파일 및 히스토리 CSV 업데이트
# 커밋 메시지용 파일에는 제목과 본문 전체를 씁니다.
with open('commit_message.txt', 'w', encoding='utf-8') as f:
    f.write(full_commit_message)

# 히스토리 파일에는 기존처럼 데이터만 추가합니다.
with open(history_file, 'a', encoding='utf-8') as f:
    f.write(f"{now},{current_rate}\n")
