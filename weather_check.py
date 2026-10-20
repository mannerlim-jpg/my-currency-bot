import os
from datetime import datetime
import pytz
import requests

# 1. 분당구 정자동 위도/경도
LAT, LON = 37.3827, 127.1189

# 2. Open-Meteo API 호출 (무료, 오늘부터 7일간 데이터)
url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&daily=weathercode,temperature_2m_max,temperature_2m_min&timezone=Asia%2FSeoul"

response = requests.get(url)
response.raise_for_status()
data = response.json()

daily = data.get("daily", {})
dates = daily.get("time", [])
weathercodes = daily.get("weathercode", [])
temps_max = daily.get("temperature_2m_max", [])
temps_min = daily.get("temperature_2m_min", [])

# WMO 기상 코드를 직관적인 이모지로 변환
def get_weather_emoji(code):
    if code in [0, 1]: return "☀️"
    elif code in [2]: return "⛅"
    elif code in [3]: return "☁️"
    elif code in [45, 48]: return "🌫️" # 안개
    elif code in [51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82]: return "☔" # 비
    elif code in [71, 73, 75, 77, 85, 86]: return "❄️" # 눈
    elif code in [95, 96, 99]: return "⚡" # 뇌우
    return "🌈"

weekdays = ["월", "화", "수", "목", "금", "토", "일"]
forecast_str = ""
min_temps, max_temps = [], []

# 3. 7일간의 날씨 요약 텍스트 만들기
for i in range(7):
    date_obj = datetime.strptime(dates[i], "%Y-%m-%d")
    weekday = weekdays[date_obj.weekday()]
    emoji = get_weather_emoji(weathercodes[i])
    
    forecast_str += f"{weekday}{emoji} "
    min_temps.append(temps_min[i])
    max_temps.append(temps_max[i])

# 주간 전체 최저, 최고 기온 계산 (반올림)
week_min = round(min(min_temps))
week_max = round(max(max_temps))

# 4. 커밋 메시지 구성 (제목 + 본문 링크)
title = f"[분당 주간날씨] {forecast_str.strip()} ({week_min}℃ ~ {week_max}℃)"
detail_link = "https://weather.naver.com/today/02135115"

# 두 줄 바꿈(\n\n)을 사용하여 제목과 본문을 분리합니다.
commit_msg = f"{title}\n\n상세 날씨(시간대별 예보 및 강수량) 확인하기:\n{detail_link}"

print("생성된 메시지:\n", commit_msg)

# 5. 워크플로가 읽을 수 있도록 파일로 저장
with open("weather_commit_msg.txt", "w", encoding="utf-8") as f:
    f.write(commit_msg)
