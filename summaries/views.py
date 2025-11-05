from decimal import Decimal
import re

from django.db import transaction
from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import DetailProfile, SummarySnapshot
from .serializers import (DetailProfileSerializer, LedgerSummarySerializer)
from ledgers.models import LedgerEntry
from rates.views import convert_to_krw, convert_from_krw


INCLUDED_CATEGORIES = [
    LedgerEntry.Category.FOOD,
    LedgerEntry.Category.HOUSING,
    LedgerEntry.Category.TRANSPORT,
    LedgerEntry.Category.SHOPPING,
    LedgerEntry.Category.TRAVEL,
    LedgerEntry.Category.STUDY_MATERIALS,
]


KOREAN_COUNTRY_TO_CURRENCY = {
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
    "UK": "GBP",
}


def ok(message, data=None, status_code=status.HTTP_200_OK):
    return Response({"message": message, "data": data}, status=status_code)


def bad(message, error=None, status_code=status.HTTP_400_BAD_REQUEST):
    return Response({"message": message, "error": error}, status=status_code)


def resolve_foreign_currency(exchange_profile):
    if not exchange_profile:
        return "KRW"

    country_name = getattr(exchange_profile, "exchange_country", "") or ""
    name = str(country_name).strip()

    from ledgers.serializers import COUNTRY_TO_CURRENCY
    if name in COUNTRY_TO_CURRENCY:
        return COUNTRY_TO_CURRENCY[name]

    if name in KOREAN_COUNTRY_TO_CURRENCY:
        return KOREAN_COUNTRY_TO_CURRENCY[name]

    return "KRW"


def extract_months(exchange_profile):
    if not exchange_profile:
        return 1

    raw = getattr(exchange_profile, "exchange_period", "") or ""
    matched = re.findall(r"\d+", raw)
    if not matched:
        return 1

    months = int(matched[0])
    if months <= 0:
        return 1
    return months


class DetailProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        detail_profile = self._get_detail_profile_or_none(request.user)
        if not detail_profile:
            return ok("세부 프로필이 없습니다.", None)

        serializer = DetailProfileSerializer(detail_profile)
        return ok("세부 프로필 조회 성공", serializer.data)

    @transaction.atomic
    def post(self, request):
        if self._get_detail_profile_or_none(request.user):
            return bad("이미 세부 프로필이 존재합니다.", status_code=status.HTTP_400_BAD_REQUEST)

        serializer = DetailProfileSerializer(data=request.data)
        if not serializer.is_valid():
            return bad("세부 프로필 생성 실패", serializer.errors)

        detail_profile = serializer.save(user=request.user)
        snapshot = self._create_snapshot(request.user, detail_profile)

        data = {
            "detail_profile_id": detail_profile.id,
            "snapshot_id": snapshot.id,
        }
        return ok("세부 프로필 생성 및 가계부 요약본 스냅샷 생성 완료", data, status.HTTP_201_CREATED)

    @transaction.atomic
    def put(self, request):
        detail_profile = self._get_detail_profile_or_none(request.user)
        if not detail_profile:
            return bad("수정할 세부 프로필이 없습니다.", status_code=status.HTTP_404_NOT_FOUND)

        serializer = DetailProfileSerializer(
            detail_profile,
            data=request.data,
            partial=True,
        )
        if not serializer.is_valid():
            return bad("세부 프로필 수정 실패", serializer.errors)

        detail_profile = serializer.save()
        snapshot = self._create_snapshot(request.user, detail_profile)

        data = {
            "detail_profile_id": detail_profile.id,
            "snapshot_id": snapshot.id,
        }
        return ok("세부 프로필 수정 및 가계부 요약본 스냅샷 생성 완료", data)

    def _get_detail_profile_or_none(self, user):
        try:
            return user.summary_detail_profile
        except DetailProfile.DoesNotExist:
            return None

    def _create_snapshot(self, user, detail_profile):
        exchange_profile = getattr(user, "exchange_profile", None)

        foreign_currency = resolve_foreign_currency(exchange_profile)
        total_foreign, total_krw = self._sum_ledger_for_user(user, foreign_currency)

        months = extract_months(exchange_profile)

        monthly_foreign = (total_foreign / months).quantize(Decimal("0.01"))
        monthly_krw = (total_krw / months).quantize(Decimal("0.01"))

        snapshot = SummarySnapshot.objects.create(
            user=user,
            exchange_profile=exchange_profile,
            detail_profile=detail_profile,
            snapshot_nickname=getattr(user, "nickname", "") or "",
            snapshot_gender=user.get_gender_display() if hasattr(user, "get_gender_display") else "",
            snapshot_exchange_country=getattr(exchange_profile, "exchange_country", "") or "",
            snapshot_exchange_university=getattr(getattr(exchange_profile, "exchange_univ", None), "univ_name", "") or "",
            snapshot_exchange_type=(
                exchange_profile.get_exchange_type_display()
                if exchange_profile and exchange_profile.exchange_type
                else ""
            ),
            snapshot_exchange_semester=getattr(exchange_profile, "exchange_semester", "") or "",
            snapshot_exchange_period=getattr(exchange_profile, "exchange_period", "") or "",
            living_expense_foreign_amount=monthly_foreign,
            living_expense_foreign_currency=foreign_currency,
            living_expense_krw_amount=monthly_krw,
            living_expense_krw_currency="KRW",
        )
        return snapshot


class LedgerSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    LABEL_MAP = {
        LedgerEntry.Category.FOOD: "식비",
        LedgerEntry.Category.HOUSING: "주거비",
        LedgerEntry.Category.TRANSPORT: "교통비",
        LedgerEntry.Category.SHOPPING: "쇼핑비",
        LedgerEntry.Category.TRAVEL: "여행비",
        LedgerEntry.Category.STUDY_MATERIALS: "교재비",
    }

    def get(self, request):
        user = request.user
        exchange_profile = getattr(user, "exchange_profile", None)

        foreign_currency = resolve_foreign_currency(exchange_profile)
        months = extract_months(exchange_profile)

        categories_data, total_foreign, total_krw, total_current_krw = self._build_category_summaries(
            user,
            foreign_currency,
        )

        average_monthly = {
            "foreign_amount": (total_foreign / months).quantize(Decimal("0.01")),
            "foreign_currency": foreign_currency,
            "krw_amount": (total_krw / months).quantize(Decimal("0.01")),
            "krw_currency": "KRW",
            "current_rate_krw_amount": (total_current_krw / months).quantize(Decimal("0.01")),
        }

        base_dispatch_cost = self._empty_dispatch_cost(foreign_currency)

        serializer = LedgerSummarySerializer(
            {
                "average_monthly_living_expense": average_monthly,
                "categories": categories_data,
                "base_dispatch_cost": base_dispatch_cost,
            }
        )
        return ok("가계부 요약본 조회 성공", serializer.data)