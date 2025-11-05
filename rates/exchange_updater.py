import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import os
import django

# DJANGO_SETTINGS_MODULE만 바꿔서 로컬/배포 전환
#   - 로컬: dongleDongle.settings.dev
#   - 배포: dongleDongle.settings.prod
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dongleDongle.settings.dev")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dongleDongle.settings.dev")
django.setup()

from django.conf import settings
import requests
import pymysql
import schedule
import time
from datetime import datetime

db = settings.DATABASES["default"]
DB_CONFIG = {
    "host": db.get("HOST") or "localhost",
    "user": db.get("USER") or "root",
    "password": db.get("PASSWORD") or "",
    "database": db.get("NAME") or "dongle_db",
    "charset": "utf8mb4",
    # 필요하면 "port": int(db.get("PORT") or 3306),
}

# 환율 API 
API_URL = getattr(settings, "EXCHANGE_API_URL", "https://open.er-api.com/v6/latest/KRW")

# 타겟 통화
TARGET_CURRENCIES = getattr(
    settings,
    "EXCHANGE_TARGETS",
    ["USD", "JPY", "EUR", "CNY", "TWD", "CAD", "GBP", "KRW"],
)

def update_exchange_rates():
    """외부 API에서 환율 불러와 MySQL에 저장/갱신"""
    print(f"\n[{datetime.now()}] 환율 업데이트 시작")

    try:
        # 1. API 호출
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()


        base = data.get("base") or data.get("base_code") or "KRW"
        rates = data.get("rates", {})

        filtered_rates = {k: v for k, v in rates.items() if k in TARGET_CURRENCIES}

        # 2. DB 연결
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # 3. 각 통화에 대해 INSERT OR UPDATE
        for target, rate in filtered_rates.items():
            sql = """
                INSERT INTO rates_exchangerate (base_currency, target_currency, rate, updated_at)
                VALUES (%s, %s, %s, NOW())
                ON DUPLICATE KEY UPDATE 
                    rate = VALUES(rate),
                    updated_at = CURRENT_TIMESTAMP;
            """
            cursor.execute(sql, (base, target, rate))

        # 4️. 커밋 & 종료
        connection.commit()
        cursor.close()
        connection.close()

        print(f"[{datetime.now()}] 환율 업데이트 완료 ({len(rates)}개 갱신)")

    except Exception as e:
        print(f"오류 발생: {e}")


# 1시간마다 갱신 
schedule.every(1).hours.do(update_exchange_rates)

# 처음 한 번 즉시 실행
update_exchange_rates()

print("\n 1시간마다 환율 자동 갱신 중 \n")
while True:
    schedule.run_pending()
    time.sleep(10)