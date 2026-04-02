import requests
from bs4 import BeautifulSoup
import os
import json
from datetime import datetime
import pytz

# 1. 네이버 금융에서 국내 은행(하나은행) 기준 호주 환율 추출
def get_domestic_aud_rate():
    try:
        url = "https://finance.naver.com/marketindex/exchangeList.naver"
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # '호주 AUD' 항목을 찾아 매매기준율 추출
        td_tit = soup.find('a', string=lambda text: text and '호주 AUD' in text).parent
        rate_str = td_tit.find_next_sibling('td', class_='sale').text
        
        # 쉼표 제거 후 실수형으로 변환
        return float(rate_str.replace(',', ''))
    except Exception as e:
        print(f"환율 스크래핑 오류: {e}")
        return None

# 2. 구글 챗 스페이스로 메시지 발송
def send_google_chat(rate):
    webhook_url = os.environ.get('GOOGLE_CHAT_WEBHOOK')
    if not webhook_url:
        print("오류: GOOGLE_CHAT_WEBHOOK 환경변수가 없습니다.")
        return

    # 서울 시간 기준 현재 날짜
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst).strftime('%Y년 %m월 %d일 %H:%M')

    # 환율 구간별 전략 판별
    if rate <= 960:
        level_msg = "🟢 [3단계] 강력 매수 구간"
        plan = "- 학비 등 대규모 자금 환전 최적기입니다.\n- 가용 자산을 최대한 AUD로 전환하세요."
    elif rate <= 995:
        level_msg = "🟡 [2단계] 적극 매수 구간"
        plan = "- 정착 비용 및 생활비 환전을 추천합니다.\n- 쏠트래블 카드에 분할 충전하세요."
    elif rate <= 1015:
        level_msg = "🟠 [1단계] 주의/소액 구간"
        plan = "- 당장 필요한 소액 경비만 먼저 환전하세요.\n- 서빈이 카드 한도 증액을 위해 은행 방문을 준비하세요."
    else:
        level_msg = "🔴 관망 구간"
        plan = "- 환율이 다소 높습니다. 긴급한 송금이 아니라면 대기하세요."

    # 구글 챗 전송용 텍스트
    message_text = f"""
*🇦🇺 오늘의 호주 환율 리포트*
(기준 시각: {now})

▶ 현재 네이버/하나은행 기준 환율: *{rate}원*
상태: {level_msg}

*■ 가족 대응 전략*
{plan}
"""

    message_data = {"text": message_text}
    
    try:
        response = requests.post(
            webhook_url,
            data=json.dumps(message_data),
            headers={'Content-Type': 'application/json; charset=UTF-8'}
        )
        response.raise_for_status()
        print("구글 챗 메시지 발송 성공!")
    except Exception as e:
        print(f"구글 챗 발송 실패: {e}")

# 3. 메인 실행 로직
if __name__ == "__main__":
    current_rate = get_domestic_aud_rate()
    
    if current_rate:
        print(f"추출된 현재 환율: {current_rate}")
        send_google_chat(current_rate)
    else:
        print("환율 정보를 가져오지 못해 종료합니다.")
