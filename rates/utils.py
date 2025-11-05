from decimal import Decimal, ROUND_HALF_UP
from .models import *
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework import permissions
from .serializers import *
from rest_framework.response import Response

# 예산안용 함수 저장 파일 

# 1) 외화 -> 한화 
def convert_to_krw(amount, from_currency):
    try:
        krw_to_foreign = ExchangeRate.objects.get(target_currency=from_currency).rate
        converted = Decimal(amount) / Decimal(krw_to_foreign)
        return converted.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except ObjectDoesNotExist:
        return None
    

#2) 한화 -> 외화
def convert_from_krw(amount, to_currency):
    try:
        krw_to_foreign = ExchangeRate.objects.get(target_currency=to_currency).rate
        converted = Decimal(amount) * Decimal(krw_to_foreign)
        return converted.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except ObjectDoesNotExist:
        return None