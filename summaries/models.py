# summaries/models.py
from django.conf import settings
from django.db import models


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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} 세부 프로필"


class SummarySnapshot(models.Model):
    """
    기록 시점 환율 고정
    한달평균생활비, 기본파견비용)도 여기 저장.
    """
    CURRENCY_USD = "USD"
    CURRENCY_KRW = "KRW"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="summary_snapshots")
    exchange_profile = models.ForeignKey("accounts.ExchangeProfile", on_delete=models.SET_NULL, null=True, blank=True, related_name="summary_snapshots")
    detail_profile = models.ForeignKey(DetailProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name="summary_snapshots")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} 요약본"


# class LivingCostItem(models.Model):
#     """
#     한달평균생활비
#     가계부에서 가져오기 -> 근데 평균을 곁들인...
#     현재 환율 기준으로도 보여줘야 함
#     """

#     snapshot = models.ForeignKey(
#         SummarySnapshot,
#         on_delete=models.CASCADE,
#         related_name="living_cost_items",
#     )

#     # 현재 환율 기준
#     applied_rate = models.DecimalField(max_digits=12, decimal_places=4, help_text="이 항목 계산에 실제로 쓴 환율")


# class DispatchCostItem(models.Model):
#     """
#     기본파견비용
#     예산안에서 불러오기
#     현재 환율 기준으로도 보여줘야 함
#     """
#     snapshot = models.ForeignKey(SummarySnapshot, on_delete=models.CASCADE, related_name="dispatch_cost_items")


class SummaryNote(models.Model):
    snapshot = models.OneToOneField(SummarySnapshot, on_delete=models.CASCADE, related_name="note")
    content = models.TextField(blank=True)

    def __str__(self):
        return f"남긴 한 마디 {self.snapshot_id}"
