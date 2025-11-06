from django.db import models
from django.conf import settings
from rates.utils import convert_to_krw

# Create your models here.
#예산안
class Budget(models.Model):
    #사용자<->예산안 1:1 
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True,
                             on_delete=models.SET_NULL, related_name="budget")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    budget = models.OneToOneField(Budget, on_delete=models.CASCADE, related_name="base_budget")
    total_amount_krw = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    #기본 파견비 합산 함수(한화 기준) 
    def update_total(self):
        total = sum(item.get_krw_amount() for item in self.items.all())
        self.total_amount_krw = total
        self.save()
        return total #한화 총액 반환


#기본 파견비와 1:N으로 연결
class BaseBudgetItem(models.Model):
    #선택 입력 항목 
    class BaseItem(models.TextChoices):
        FLIGHT = "FLIGHT", "항공권"
        INSURANCE = "INSURANCE", "보험료"
        VISA = "VISA", "비자"
        TUITION = "TUITION", "등록금"

    base_budget = models.ForeignKey(BaseBudget, on_delete=models.CASCADE, related_name="items")
    type = models.CharField(max_length=10, choices=BaseItem.choices)
    amount = models.DecimalField(max_digits=20, decimal_places=6)
    currency = models.CharField(max_length=5, choices=CurrencyOption.choices)
    exchange_amount = models.DecimalField(max_digits=20, decimal_places=6, null=True) #한화 변환 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # 통화가 KRW가 아닐 때만 환전
        if self.currency != "KRW":
            converted = convert_to_krw(self.amount, self.currency)
            self.exchange_amount = converted if converted is not None else None
        else:
            self.exchange_amount = self.amount

        super().save(*args, **kwargs)

    #한화 변환 함수(rates.util에서 가져옴)
    def get_amount_in_krw(self):
        return convert_to_krw(self.amount, self.currency)

    #한화 변환 함수(for 합산) 
    # KRW가 아닌 경우에 get_amount_in_krw 함수 -> 한화로 변환
    def get_krw_amount(self):
        if self.currency != "KRW":
            return self.get_amount_in_krw()
        return self.amount
    
# 예산안 내 생활비 
class LivingBudget(models.Model):
    budget = models.OneToOneField(Budget, on_delete=models.CASCADE, related_name="living_budget")
    total_amount = models.IntegerField(default=0) #한 달 생활비(필수 입력) 
    # total_amount_krw = models.DecimalField(max_digits=20, decimal_places=2, default=0) #선택 입력 값까지 합산  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_amount(self):
        return self.total_amount


#생활비와 1:N으로 연결 / 무조건 원화로 입력 
class LivingBudgetItem(models.Model):
    class LivingItem(models.TextChoices):
        FOOD = "FOOD", "식비"
        HOUSING = "HOUSING", "주거비"
        TRANSPORT = "TRANSPORT", "교통비"
        SHOPPING = "SHOPPING", "쇼핑비"
        TRAVEL = "TRAVEL", "여행비"
        STUDY_MATERIALS = "STUDY_MATERIALS", "교재비"
        ALLOWANCE = "ALLOWANCE", "용돈"
        ETC = "ETC", "기타"

    living_budget = models.ForeignKey(LivingBudget, on_delete=models.CASCADE, related_name="items")
    type = models.CharField(max_length=20, choices=LivingItem.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=6)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    #한화 변환 함수(for 합산) 
    def get_krw_amount(self):
        return self.amount

    

    



