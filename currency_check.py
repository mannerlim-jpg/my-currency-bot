import requests
from bs4 import BeautifulSoup
import datetime
import pytz

# 1. 네이버 금융에서 환율 추출
url = "https://finance.naver.com/marketindex/exchangeList.naver"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
td_tit = soup.find('a', string=lambda text: text and '호주 AUD' in text).parent
rate_str = td_tit.find_next_sibling('td', class_='sale').text
rate = float(rate_str.replace(',', ''))

# 2. 환율 구간별 전략 판별
if rate <= 960: level = "🟢3단계 강력매수"
elif rate <= 995: level = "🟡2단계 적극매수"
elif rate <= 1015: level = "🟠1단계 주의/소액"
else: level = "🔴관망"

# 3. 깃허브 커밋 메시지용 텍스트 생성
kst = pytz.timezone('Asia/Seoul')
now = datetime.datetime.now(kst).strftime('%m-%d %H:%M')
commit_msg = f"[{now}] 호주환율 {rate}원 ({level})"

print(f"생성된 메시지: {commit_msg}")

# 깃허브 액션(스케줄러)에서 이 메시지를 읽어갈 수 있게 텍스트 파일로 저장
with open('commit_message.txt', 'w', encoding='utf-8') as f:
    f.write(commit_msg)

# 깃허브가 '파일이 변경되었다'고 인식하도록 더미 기록(history) 남기기
with open('history.csv', 'a', encoding='utf-8') as f:
    f.write(f"{now},{rate}\n")
