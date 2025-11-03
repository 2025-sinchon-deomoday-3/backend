from django.db import models
# Create your models here.

#환율 모델 
class ExchangeRate(models.Model):
    base_currency = models.CharField(max_length = 10, blank = True)
    target_currency = models.CharField(max_length = 10, blank = True) 
    rate = models.DecimalField(max_digits = 10, decimal_places = 6)
    effective_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    #중복 저장 방지 
    class Meta:
        unique_together = ('base_currency', 'target_currency', 'effective_at')

