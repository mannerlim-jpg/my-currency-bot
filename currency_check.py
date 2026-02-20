import requests
import smtplib
from email.message import EmailMessage
import os
import csv
from datetime import datetime

# 1. 환율 정보 가져오기
def get_exchange_rate():
    api_key = os.environ.get('EXCHANGE_RATE_API_KEY')
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/AUD"
    response = requests.get(url)
    return round(response.json()['conversion_rates']['KRW'], 2)

# 2. 이력 기록 및 이전 환율 가져오기
def update_history_and_get_last(current_rate):
    file_name = 'history.csv'
    last_rate = float('inf') # 파일이 없으면 무한대로 설정
    
    # 이전 기록 읽기
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            reader = list(csv.reader(f))
            if len(reader) > 1: # 헤더 제외 기록이 있다면
                last_rate = float(reader[-1][1])
    
    # 오늘 기록 추가
    file_exists = os.path.isfile(file_name)
    with open(file_name, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Date', 'Rate'])
        writer.writerow([datetime.now().strftime('%Y-%m-%d %H:%M'), current_rate])
    
    return last_rate

# 3. 상세 이메일 발송
def send_detailed_email(rate, level, plan):
    msg = EmailMessage()
    content = f"""
[호주 환율 지능형 대응 리포트]

현재 환율: {rate}원 (알림 {level}단계 도달)
※ 전날보다 환율이 하락하여 알림을 발송합니다.

■ 이 단계의 대응 전략:
{plan}

■ 기본 체크리스트:
1. 신한 SOL뱅크 앱 접속 및 외화예금 계좌 확인
2. 미성년자(서빈) 한도 확인 (일 3만원 이상 필요시 은행 방문 필수)
3. 목돈 송금 시 와이어바알리 등 대체 수단 가격 비교

※ 본 메일은 설정된 환율 조건 및 하락 조건 충족 시 자동으로 발송되었습니다.
"""
    msg.set_content(content)
    msg['Subject'] = f"[환율하락/알림 {level}] 현재 {rate}원 - 전략 확인"
    msg['From'] = os.environ.get('EMAIL_USER')
    msg['To'] = os.environ.get('EMAIL_RECEIVER')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(os.environ.get('EMAIL_USER'), os.environ.get('EMAIL_PASS'))
        smtp.send_message(msg)

# 메인 로직
try:
    current_rate = get_exchange_rate()
    last_rate = update_history_and_get_last(current_rate)
    
    print(f"오늘 환율: {current_rate} / 어제 환율: {last_rate}")

    # 조건 1: 어제보다 환율이 떨어졌는가?
    is_dropped = current_rate < last_rate
    
    # 조건 2: 설정한 단계에 진입했는가?
    level, plan = None, None
    if current_rate <= 960:
        level, plan = "3단계 (강력 매수)", "- 학비 등 대규모 자금 환전 최적기입니다.\n- 가용 자산을 최대한 AUD로 전환하세요."
    elif current_rate <= 995:
        level, plan = "2단계 (적극 매수)", "- 정착 비용 및 생활비 환전을 추천합니다.\n- 쏠트래블 카드에 분할 충전하세요."
    elif current_rate <= 1015:
        level, plan = "1단계 (주의/소액)", "- 여행용 소액 경비만 먼저 환전하세요.\n- 서빈이 카드 한도 증액을 위해 은행 방문을 준비하세요."

    # 두 조건 모두 충족 시에만 메일 발송
    if is_dropped and level:
        send_detailed_email(current_rate, level, plan)
        print(f"알림 발송 조건 충족: {level}")
    else:
        print("알림 조건 미충족 (환율 상승 또는 기준가 미달)")

except Exception as e:
    print(f"오류 발생: {e}")
