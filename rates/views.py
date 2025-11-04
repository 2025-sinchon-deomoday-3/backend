from django.shortcuts import render
from .models import *
from decimal import Decimal, ROUND_HALF_UP
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework import permissions
from .serializers import *
from rest_framework.response import Response
# Create your views here.

"""
    # 기준 통화 별 환율 변환 로직 
    1 KRW = rate * 외화 
    amount: 금액
    from_currency: 입력 통화
    to_currency: 변환 통화 
    만약 from = 외화면 무조건 KRW로 변환
    KRW 입력이면 to에 맞춰서 변환 
"""

# 1) 외화 -> 한화 
# 1외화 = 1/rate KRW
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

#3) 하나의 엔드포인트
class ConvertView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        from_currency = request.GET.get("from", "").upper()
        to_currency = request.GET.get("to", "").upper()
        amount = float(request.GET.get("amount", 0))

        if to_currency == "KRW":
            result = convert_to_krw(amount, from_currency)
        elif from_currency == "KRW":
            result = convert_from_krw(amount, to_currency)
        
        if result is None:
            return Response({"error: Rate not Found"}, status=404)

        serializers = ConvertResultSerializer({
            "from_currency": from_currency,
            "to_currency": to_currency,
            "amount": amount,
            "converted": result
        })
        return Response(serializers.data)