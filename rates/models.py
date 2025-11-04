from django.db import models
# Create your models here.

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

#환율 모델 
class ExchangeRate(models.Model):
    base_currency = models.CharField(max_length = 10, blank = True)
    target_currency = models.CharField(max_length = 10, choices=CurrencyOption.choices, unique=True) #가장 최신 1건만 유지(통화별)
    rate = models.DecimalField(max_digits = 10, decimal_places = 6)
    updated_at = models.DateTimeField(auto_now=True)

    
