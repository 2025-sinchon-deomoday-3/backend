from django.db import models
from django.conf import settings


class LedgerEntry(models.Model):
    class EntryType(models.TextChoices):
        EXPENSE = "EXPENSE", "지출"
        INCOME = "INCOME", "수입"
    
    class PaymentMethod(models.TextChoices):
        CASH = "CASH", "현금"
        CARD = "CARD", "카드"
    
    class Category(models.TextChoices):
        FOOD = "FOOD", "식비"
        HOUSING = "HOUSING", "주거비"
        TRANSPORT = "TRANSPORT", "교통비"
        SHOPPING = "SHOPPING", "쇼핑비"
        TRAVEL = "TRAVEL", "여행비"
        STUDY_MATERIALS = "STUDY_MATERIALS", "교재비"
        ALLOWANCE = "ALLOWANCE", "용돈"

    entry_type = models.CharField(max_length=10, choices=EntryType.choices)
    date = models.DateField()
    payment_method = models.CharField(max_length=10, choices=PaymentMethod.choices, null=True, blank=True)
    category = models.CharField(max_length=20, choices=Category.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # 추후 환율 DB 연동 시 수정 필요
    # currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name="ledger_entries")
    # exchange_rate = models.ForeignKey(ExchangeRate, on_delete=models.CASCADE, related_name="ledger_entries_rate")
    amount_converted = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Ledger(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ledgers_user")
    ledger_entries = models.ManyToManyField(LedgerEntry, related_name="ledgers_entries", blank=True)
    month = models.DateField(help_text="LedgerEntry에서 몇 월인지 참고")