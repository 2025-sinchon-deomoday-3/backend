from rest_framework import serializers
from .models import *


#기본 파견비 내 아이템 시리얼라이저 
class BaseBudgetItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseBudgetItem
        fields = ["id", "type", "amount", "currency", "created_at", "updated_at"]


#기본 파견비 시리얼라이저(*Nested Serializer)
class BaseBudgetSerializer(serializers.ModelSerializer):
    items = BaseBudgetItemSerializer(many=True)

    class Meta:
        model = BaseBudget
        fields = ["id", "total_amount_krw", "items", "created_at", "updated_at" ]

    def validate_items(self, value):
        """기본 파견비 항목은 FLIGHT, INSURANCE, VISA, TUITION 모두 필수"""
        required_types = {"FLIGHT", "INSURANCE", "VISA", "TUITION"}
        provided_types = {item.get("type") for item in value}

        missing = required_types - provided_types
        extra = provided_types - required_types

        if missing:
            raise serializers.ValidationError(
                f"다음 항목이 누락되었습니다: {', '.join(missing)}"
            )
        if extra:
            raise serializers.ValidationError(
                f"유효하지 않은 항목이 포함되어 있습니다: {', '.join(extra)}"
            )

        if len(value) != 4:
            raise serializers.ValidationError("기본 파견비 항목은 정확히 4개여야 합니다.")

        return value

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        base_budget = BaseBudget.objects.create(**validated_data)

        for item_data in items_data:
            BaseBudgetItem.objects.create(base_budget=base_budget, **item_data)

        base_budget.update_total()
        return base_budget



#생활비 내 아이템 시리얼라이저 
class LivingBudgetItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = LivingBudgetItem
        fields = ["id", "type", "amount", "created_at", "updated_at"]


#생활비 시리얼라이저(*Nested Serializer)
class LivingBudgetSerializer(serializers.ModelSerializer):
    items = LivingBudgetItemSerializer(many=True)

    class Meta:
        model = LivingBudget
        fields = ["id", "total_amount", "items", "created_at", "updated_at"]

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        living_budget = LivingBudget.objects.create(**validated_data)

        for item_data in items_data:
            LivingBudgetItem.objects.create(living_budget=living_budget, **item_data)

        return living_budget

        
    def update(self, instance, validated_data):
        items_data = validated_data.pop("items")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data is not None:
            for item_data in items_data:
                item_type = item_data.get("type")
                amount = item_data.get("amount")

                item_obj = instance.items.filter(type=item_type).first()
                if item_obj:
                    item_obj.amount = amount
                    item_obj.save()
                else:
                    LivingBudgetItem.objects.create(living_budget=instance, **item_data)

        return instance

            
#예산안 시리얼라이저(*Nested Serializer)
class BudgetSerializer(serializers.ModelSerializer):
    #수정해야 함 
    base_budget = BaseBudgetSerializer(required=False)
    living_budget = LivingBudgetSerializer(required=False)

    class Meta:
        model = Budget
        fields = ["id", "user", "base_budget", "living_budget", "created_at", "updated_at"]

    
    def create(self, validated_data):
        base_budget_data = validated_data.pop("base_budget", None)
        living_budget_data = validated_data.pop("living_budget", None)

        budget = Budget.objects.create(**validated_data)

        base_budget_data["budget"] = budget
        living_budget_data["budget"] = budget

        if base_budget_data:
            base_budget_data["budget"] = budget
            BaseBudgetSerializer().create(base_budget_data)

        if living_budget_data:
            living_budget_data["budget"] = budget
            LivingBudgetSerializer().create(living_budget_data)

        return budget

    def update(self, instance, validated_data):
        base_budget_data = validated_data.pop("base_budget", None)
        living_budget_data = validated_data.pop("living_budget", None)

        if base_budget_data:
            base_budget_serializer = BaseBudgetSerializer(instance.base_budget, data=base_budget_data, partial=True)
            base_budget_serializer.is_valid(raise_exception=True)
            base_budget_serializer.save()

        if living_budget_data:
            living_budget_serializer = LivingBudgetSerializer(instance.living_budget, data=living_budget_data, partial=True)
            living_budget_serializer.is_valid(raise_exception=True)
            living_budget_serializer.save()

        instance.save()
        return instance

