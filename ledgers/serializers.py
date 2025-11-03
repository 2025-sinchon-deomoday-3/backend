from rest_framework import serializers
from .models import *


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

    def create(self, validated_data):
        user = self.context["request"].user
        return LedgerEntry.objects.create(user=user, **validated_data)


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