from django.db import models
from django.conf import base

# Create your models here.
#예산안
class Budget(models.Model):
    user = models.ForeignKey(base.AUTH_USER_MODEL, null=True,
                             on_delete=models.SET_NULL, related_name="delivery_logs")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

#기본 파견비 - 카테고리 옵션
# class CategoryOption(models.TextChoices):
#     FLIGHT = "FLIGHT", "항공권"
#     INSURANCE = "INSURANCE", "보험료"
#     VISA = "VISA", "비자"
#     TUITION = "TUITION", "등록금"

#생활비 - 지출 카테고리 
# class LivingExpenseOption(models.TextChoices):
#     FOOD = "FOOD", "식비"
#     TRANSPORT = "TRANSPORT", "교통비"
#     HOUSING = "HOUSING", "주거비"
#     SHOPPING = "SHOPPING", "쇼핑비"
#     CULTURE = "CULTURE", "문화생활"

#통화 옵션
class CurrencyOption(models.TextChoices):
    KRW = "KRW", "대한민국 원 (KRW)"
    USD = "USD", "미국 달러 (USD)"
    JPY = "JPY", "일본 엔 (JPY)"
    EUR = "EUR", "유럽 유로 (EUR)"
    CNY = "CNY", "중국 위안 (CNY)"
    TWD = "TWD", "대만 달러 (TWD)"
    GBP = "GBP", "영국 파운드 (GBP)"
    CAD = "CAD", "캐나다 달러 (CAD)"

#예산안 내 기본 파견비
class BaseBudget(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name="기본 생활비 예산")
    category = models.CharField(max_length=10, choices=CategoryOption.choices) 
    amount = models.DecimalField(max_digits=100, decimal_places=6)
    currency = models.CharField(max_length=5, choices=CurrencyOption.choices)
    exchange_rate = models.DecimalField(max_digits = 10, decimal_places = 6) #환율(입력 시점)
    created_at = models.DateTimeField(auto_now_add=True)

#예산안 내 생활비 
# class LivingBudget(models.Model):
#     budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name="생할비 예산")
#     total_amount = models.IntegerField(max_length=3000, null=False)
#     foodgit 
#     transport
#     housing
#     shopping
#     culture
    

    



