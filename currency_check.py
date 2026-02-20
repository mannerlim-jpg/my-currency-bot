import requests
import smtplib
from email.message import EmailMessage
import os

def get_exchange_rate():
    # 무료 API 서비스 사용
    api_key = os.environ.get('EXCHANGE_RATE_API_KEY')
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/AUD"
    response = requests.get(url)
    return response.json()['conversion_rates']['KRW']

def send_email(rate):
    msg = EmailMessage()
    msg.set_content(f"현재 호주 달러(AUD) 환율: {rate}원\n아드님 송금 타이밍을 확인하세요!")
    msg['Subject'] = f"[환율알림] 현재 {rate}원"
    msg['From'] = os.environ.get('EMAIL_USER')
    msg['To'] = os.environ.get('EMAIL_RECEIVER')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(os.environ.get('EMAIL_USER'), os.environ.get('EMAIL_PASS'))
        smtp.send_message(msg)

# 메인 로직
try:
    current_rate = get_exchange_rate()
    # 900원 이하일 때만 알림 (필요시 숫자 수정 가능)
    if current_rate <= 1100:
        send_email(current_rate)
        print(f"알림 발송 완료: {current_rate}")
    else:
        print(f"현재 환율({current_rate})이 설정값보다 높습니다.")
except Exception as e:
    print(f"오류 발생: {e}")
