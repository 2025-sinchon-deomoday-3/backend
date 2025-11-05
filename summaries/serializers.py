from rest_framework import serializers
from .models import DetailProfile


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
            "summary_note",
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


class LedgerCategorySummarySerializer(serializers.Serializer):
    code = serializers.CharField()
    label = serializers.CharField()
    foreign_amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    foreign_currency = serializers.CharField()
    krw_amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    krw_currency = serializers.CharField()
    # 현재 환율 기준 원화... <- 항상 다르게
    current_rate_krw_amount = serializers.DecimalField(max_digits=14, decimal_places=2)


class AverageMonthlyExpenseSerializer(serializers.Serializer):
    foreign_amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    foreign_currency = serializers.CharField()
    krw_amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    krw_currency = serializers.CharField()
    current_rate_krw_amount = serializers.DecimalField(max_digits=14, decimal_places=2)


class BaseDispatchCostItemSerializer(serializers.Serializer):
    foreign_amount = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
        required=False,
        allow_null=True,
    )
    foreign_currency = serializers.CharField(required=False, allow_null=True)
    krw_amount = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
        required=False,
        allow_null=True,
    )
    krw_currency = serializers.CharField()
    current_rate_krw_amount = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
        required=False,
        allow_null=True,
    )


class LedgerSummarySerializer(serializers.Serializer):
    average_monthly_living_expense = AverageMonthlyExpenseSerializer()
    categories = LedgerCategorySummarySerializer(many=True)
    base_dispatch_cost = serializers.DictField(child=BaseDispatchCostItemSerializer())