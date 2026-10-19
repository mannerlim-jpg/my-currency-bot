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

# 2. 네이버 금융 환율 JSON API 호출
# 호주 달러(AUD) 전용 단일 엔드포인트
url = "https://m.stock.naver.com/front-api/marketIndex/price?category=exchange&reutersCode=FX_AUDKRW"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://m.stock.naver.com/"
}

response = requests.get(url, headers=headers)

if response.status_code != 200:
    # 혹시 모바일 API 차단 시 PC버전 엔드포인트로 대체 호출
    backup_url = "https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRWAUD"
    response = requests.get(backup_url, headers=headers)
    res_json = response.json()
    item = res_json[0]
    current_price = f"{item.get('basePrice'):,}"
    change_price = f"{item.get('changePrice'):,}"
    change_type = "상승" if item.get('change') == "RISE" else ("하락" if item.get('change') == "FALL" else "보합")
else:
    res_json = response.json()
    result = res_json.get("result", {})
    current_price = result.get("closePrice")
    change_price = result.get("compareToPreviousClosePrice")
    change_type = result.get("compareToPreviousPrice", {}).get("text", "")

# 3. 등락 기호 처리
if "상승" in change_type:
    sign = "[상승]"
elif "하락" in change_type:
    sign = "[하락]"
else:
    sign = "[보합]"

# 한국 시간 기준 타임스탬프
kst = pytz.timezone("Asia/Seoul")
now_kst = datetime.now(kst).strftime("%Y-%m-%d %H:%M")

# 4. Google Chat 메시지 작성
message_text = (
    f"[호주 달러(AUD) 환율 알림]\n"
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
