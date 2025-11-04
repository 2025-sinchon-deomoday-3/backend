# summaries/serializers.py
from rest_framework import serializers
from .models import DetailProfile


# 가계부 요약본 세부 프로필 등록
class DetailProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetailProfile
        fields = [
            "id",
            "monthly_spend_in_korea",
            "meal_frequency",
            "dineout_per_week",
            "coffee_per_week",
            "smoking_per_day",
            "drinking_per_week",
            "shopping_per_month",
            "culture_per_month",
            "residence_type",
            "commute",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_monthly_spend_in_korea(self, value):
        if value is None:
            raise serializers.ValidationError("한국에서의 월 지출은 필수입니다.")
        if value < 0:
            raise serializers.ValidationError("월 지출은 0 이상이어야 합니다.")
        return value
