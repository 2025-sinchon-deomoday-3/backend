from rest_framework import serializers
from .models import *
from rates.views import convert_to_krw, convert_from_krw
from decimal import Decimal

COUNTRY_TO_CURRENCY = {
    "한국": "KRW",
    "미국": "USD",
    "일본": "JPY",
    "독일": "EUR",
    "프랑스": "EUR",
    "중국": "CNY",
    "대만": "TWD",
    "캐나다": "CAD",
    "이탈리아": "EUR",
    "네덜란드": "EUR",
    "영국": "GBP",

    "USA": "USD",
    "JAPAN": "JPY",
    "KOREA": "KRW",
    "CHINA": "CNY",
    "TAIWAN": "TWD",
    "CANADA": "CAD",
    "UK": "GBP",
    "FRANCE": "EUR",
    "GERMANY": "EUR",
    "NETHERLANDS": "EUR",
    "ITALY": "EUR",
}


class LedgerEntryCreateSerializer(serializers.ModelSerializer):
    date = serializers.DateField(format="%Y-%m-%d", input_formats=["%Y-%m-%d"])
    amount = serializers.DecimalField(max_digits=18, decimal_places=2, min_value=0)

    payment_method = serializers.ChoiceField(
        choices=LedgerEntry.PaymentMethod.choices,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = LedgerEntry
        fields = (
            "entry_type",
            "date",
            "payment_method",
            "category",
            "amount",
            "currency_code",
        )
        extra_kwargs = {
            "payment_method": {"required": False, "allow_null": True},
        }

    def validate(self, data):
        entry_type = data.get("entry_type")
        payment_method = data.get("payment_method")

        if entry_type == LedgerEntry.EntryType.EXPENSE and not payment_method:
            raise serializers.ValidationError(
                {"payment_method": "지출(EXPENSE)일 경우 결제수단은 필수입니다."}
            )

        if entry_type == LedgerEntry.EntryType.INCOME and payment_method is not None:
            raise serializers.ValidationError(
                {"payment_method": "수입(INCOME)일 경우 결제수단을 비워두세요."}
            )

        amount = data.get("amount")
        if amount is None or amount <= 0:
            raise serializers.ValidationError({"amount": "amount는 0보다 커야 합니다."})

        currency_code = data.get("currency_code")
        if not currency_code:
            raise serializers.ValidationError({"currency_code": "통화 코드를 입력하세요."})
        data["currency_code"] = str(currency_code).upper()

        return data

    def _convert_amount(self, user, original_amount: Decimal, original_currency: str):
        # 원화 -> 교환국 통화
        if original_currency == "KRW":
            exchange_profile = getattr(user, "exchange_profile", None)
            if exchange_profile is None:
                return None, None

            country_name = exchange_profile.exchange_country
            if not country_name:
                return None, None

            country_name = country_name.strip()

            target_currency = COUNTRY_TO_CURRENCY.get(country_name)
            if target_currency is None:
                return None, None

            if target_currency == "KRW":
                return None, None

            converted_amount = convert_from_krw(original_amount, target_currency)
            if converted_amount is None:
                return None, None

            return converted_amount, target_currency

        # 외화 → KRW
        converted_amount = convert_to_krw(original_amount, original_currency)
        if converted_amount is None:
            return None, None

        return converted_amount, "KRW"


    def create(self, validated_data):
        user = self.context["request"].user
        original_amount: Decimal = validated_data["amount"]
        original_currency: str = validated_data["currency_code"]

        converted_amount, converted_currency = self._convert_amount(
            user, original_amount, original_currency
        )

        entry = LedgerEntry.objects.create(
            user=user,
            **validated_data,
            amount_converted=converted_amount,
            converted_currency_code=converted_currency,
        )
        return entry

    def update(self, instance, validated_data):
        user = self.context["request"].user

        amount = validated_data.get("amount", instance.amount)
        currency_code = validated_data.get("currency_code", instance.currency_code)

        converted_amount, converted_currency = self._convert_amount(
            user, amount, currency_code
        )

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.amount_converted = converted_amount
        instance.converted_currency_code = converted_currency
        instance.save()
        return instance


class LedgerEntrySimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = LedgerEntry
        fields = [
            "id",
            "entry_type",
            "date",
            "payment_method",
            "category",
            "amount",
            "currency_code",
            "amount_converted",
            "converted_currency_code",
        ]


class ThisMonthSummarySerializer(serializers.Serializer):
    month = serializers.CharField()
    foreign_currency = serializers.CharField()
    income_foreign = serializers.DecimalField(max_digits=18, decimal_places=2)
    income_krw = serializers.DecimalField(max_digits=18, decimal_places=2)
    expense_foreign = serializers.DecimalField(max_digits=18, decimal_places=2)
    expense_krw = serializers.DecimalField(max_digits=18, decimal_places=2)

    def to_representation(self, instance):
        return {
            "month": instance["month"],
            "expense": {
                "foreign_amount": instance["expense_foreign"],
                "foreign_currency": instance["foreign_currency"],
                "krw_amount": instance["expense_krw"],
                "krw_currency": "KRW",
            },
            "income": {
                "foreign_amount": instance["income_foreign"],
                "foreign_currency": instance["foreign_currency"],
                "krw_amount": instance["income_krw"],
                "krw_currency": "KRW",
            },
        }


class BudgetDiffWithKrwSerializer(serializers.Serializer):
    foreign_amount = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True)
    foreign_currency = serializers.CharField()
    krw_amount = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True)
    krw_currency = serializers.CharField()


class BudgetDiffForeignOnlySerializer(serializers.Serializer):
    foreign_amount = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True)
    foreign_currency = serializers.CharField()


class MonthlyCategoryItemSerializer(serializers.Serializer):
    code = serializers.CharField()
    label = serializers.CharField()
    foreign_amount = serializers.DecimalField(max_digits=18, decimal_places=2)
    foreign_currency = serializers.CharField()
    krw_amount = serializers.DecimalField(max_digits=18, decimal_places=2)
    krw_currency = serializers.CharField()
    budget_diff = BudgetDiffForeignOnlySerializer()


class MonthlyLivingExpenseSerializer(serializers.Serializer):
    foreign_amount = serializers.DecimalField(max_digits=18, decimal_places=2)
    foreign_currency = serializers.CharField()
    krw_amount = serializers.DecimalField(max_digits=18, decimal_places=2)
    krw_currency = serializers.CharField()


class BaseDispatchCostSerializer(serializers.Serializer):
    airfare = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True)
    insurance = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True)
    visa = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True)
    tuition = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True)


class MonthlyCategoryDashboardSerializer(serializers.Serializer):
    month = serializers.CharField()
    living_expense = MonthlyLivingExpenseSerializer()
    living_expense_budget_diff = BudgetDiffWithKrwSerializer()
    categories = MonthlyCategoryItemSerializer(many=True)
    base_dispatch_cost = BaseDispatchCostSerializer()