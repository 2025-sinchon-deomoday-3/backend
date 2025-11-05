# summaries/models.py
from django.conf import settings
from django.db import models
from decimal import Decimal


class DetailProfile(models.Model):
    class MealFrequency(models.TextChoices):
        ONE_PER_DAY = "1", "하루 1회"
        TWO_PER_DAY = "2", "하루 2회"
        THREE_PER_DAY = "3", "하루 3회"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="summary_detail_profile")
    monthly_spend_in_korea = models.DecimalField(max_digits=12, decimal_places=0, help_text="한국에서의 월 지출 (KRW 기준)")
    meal_frequency = models.CharField(max_length=2, choices=MealFrequency.choices, blank=True, null=True)
    dineout_per_week = models.PositiveIntegerField(default=0)
    coffee_per_week = models.PositiveIntegerField(default=0)
    smoking_per_day = models.PositiveIntegerField(default=0)
    drinking_per_week = models.PositiveIntegerField(default=0)
    shopping_per_month = models.PositiveIntegerField(default=0)
    culture_per_month = models.PositiveIntegerField(default=0)
    residence_type = models.CharField(max_length=100, blank=True, help_text="거주유형 직접 입력")
    commute = models.BooleanField(default=False, help_text="통학여부(통학하면 True)")

    summary_note = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} 세부 프로필"


class SummarySnapshot(models.Model):
    """
    가계부 요약본 -> 가계부 요약 게시했을 때
    그 시점의 환산 결과(한달 평균 생활비) 저장!! 현재 환율도 보여줘야하므로
    그 시점의 프로필/파견정보/한마디 저장
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="snapshots_user")
    exchange_profile = models.ForeignKey("accounts.ExchangeProfile", on_delete=models.SET_NULL, null=True, blank=True, related_name="snapshots_exchange_profile")
    detail_profile = models.ForeignKey(DetailProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name="snapshots_detail_profile")

    # 프로필 부분
    snapshot_nickname = models.CharField(max_length=50, blank=True)
    snapshot_gender = models.CharField(max_length=20, blank=True)
    snapshot_exchange_country = models.CharField(max_length=50, blank=True)
    snapshot_exchange_university = models.CharField(max_length=120, blank=True)
    snapshot_exchange_type = models.CharField(max_length=20, blank=True)
    snapshot_exchange_semester = models.CharField(max_length=40, blank=True)
    snapshot_exchange_period = models.CharField(max_length=40, blank=True)

    # 한 달 평균 생활비 부분
    living_expense_foreign_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    living_expense_foreign_currency = models.CharField(max_length=5, blank=True, help_text="교환국 통화 코드 (USD, JPY ...)")
    living_expense_krw_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    living_expense_krw_currency = models.CharField(max_length=3, default="KRW")

    # 기본 파견비용 부분
    base_dispatch_foreign_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    base_dispatch_krw_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} 가계부 요약본 ({self.created_at.date()})"