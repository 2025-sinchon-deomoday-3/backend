from rest_framework import serializers
from .models import *

#변환 결과 serilaizer 
class ConvertResultSerializer(serializers.Serializer):
    from_currency = serializers.CharField()
    to_currency = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    converted = serializers.DecimalField(max_digits=10, decimal_places=2)
