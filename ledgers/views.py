from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, date as date_type
from collections import defaultdict
from datetime import date
from django.db.models import QuerySet
from rates.views import convert_to_krw, convert_from_krw

from .serializers import *
from .models import *
from budgets.models import Budget, LivingBudget, BaseBudget, BaseBudgetItem
from decimal import Decimal

# 생활비용 (용돈, 기타는 제외)
LIVING_CATEGORIES = {
    "FOOD",
    "HOUSING",
    "TRANSPORT",
    "SHOPPING",
    "TRAVEL",
    "STUDY_MATERIALS",
}

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
}


def ok(message, data=None, status=200):
    return Response({"message": message, "data": data}, status=status)


def bad(message, error=None, status=400):
    return Response({"message": message, "error": error}, status=status)


class LedgerEntryCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LedgerEntryCreateSerializer(
            data=request.data,
            context={"request": request},
        )
        if not serializer.is_valid():
            return bad("유효성 검사 실패", serializer.errors, status=400)

        entry = serializer.save()

        month_first = entry.date.replace(day=1)
        ledger, _ = Ledger.objects.get_or_create(user=request.user, month=month_first)
        ledger.ledger_entries.add(entry)

        data = LedgerEntrySimpleSerializer(entry).data
        return ok("등록 완료", data, status=201)


class MyLedgerAllDateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = (
            LedgerEntry.objects
            .filter(user=request.user)
            .order_by("-date", "-created_at")
        )

        months = defaultdict(list)
        for e in qs:
            month_key = e.date.replace(day=1)
            months[month_key].append(e)

        month_blocks = []
        for month_key in sorted(months.keys(), reverse=True):
            days_map = defaultdict(list)
            for e in months[month_key]:
                days_map[e.date].append(e)

            days = []
            for day in sorted(days_map.keys(), reverse=True):
                items = LedgerEntrySimpleSerializer(days_map[day], many=True).data
                days.append(
                    {
                        "date": day.isoformat(),
                        "weekday_ko": _weekday_ko(day),
                        "items": items,
                    }
                )

            month_blocks.append(
                {
                    "month": month_key.strftime("%Y-%m"),
                    "days": days,
                }
            )

        return ok("내 가계부 전체 조회 성공", month_blocks)


def _weekday_ko(d: date_type) -> str:
    names = ["월", "화", "수", "목", "금", "토", "일"]
    return names[d.weekday()]


class MyLedgerAllCategoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = date.today()
        month_start = today.replace(day=1)

        # 이번달만 조회
        entries = (
            LedgerEntry.objects
            .filter(user=user, date__gte=month_start, date__lte=today)
            .order_by("-date", "-created_at")
        )

        foreign_currency = self._foreign_currency(user)

        # 카테고리별 합계
        category_totals = defaultdict(lambda: {
            "krw": Decimal("0.00"),
            "foreign": Decimal("0.00"),
        })

        # 생활비 전체 합계
        living_krw_total = Decimal("0.00")
        living_foreign_total = Decimal("0.00")

        for entry in entries:
            krw_amount = self._to_krw(entry)
            if krw_amount is None:
                continue

            foreign_amount = self._to_foreign(krw_amount, foreign_currency)

            category_totals[entry.category]["krw"] += krw_amount
            category_totals[entry.category]["foreign"] += foreign_amount

            if entry.category in LIVING_CATEGORIES:
                living_krw_total += krw_amount
                living_foreign_total += foreign_amount

        for cat_sum in category_totals.values():
            cat_sum["krw"] = cat_sum["krw"].quantize(Decimal("0.01"))
            cat_sum["foreign"] = cat_sum["foreign"].quantize(Decimal("0.01"))

        living_krw_total = living_krw_total.quantize(Decimal("0.01"))
        living_foreign_total = living_foreign_total.quantize(Decimal("0.01"))

        budget_krw = None
        budget_foreign = None
        diff_krw = None
        diff_foreign = None
        diff_sign = None

        try:
            budget = Budget.objects.filter(user=user).first()
            if budget and hasattr(budget, "living_budget"):
                living_budget = budget.living_budget # 예산안 연동
                budget_krw = Decimal(str(living_budget.total_amount)) # 한화 기준 예산
                budget_foreign = convert_from_krw(budget_krw, foreign_currency) # 교환국 기준 화폐로 변경

                # 예산 대비
                diff_krw = living_krw_total - budget_krw
                diff_foreign = living_foreign_total - budget_foreign

                # 예산안보다 더 쓰면 +, 덜 쓰면 -
                diff_sign = "+" if diff_krw > 0 else "-"
            else:
                budget_krw = Decimal("0.00")
                budget_foreign = Decimal("0.00")
                diff_krw = Decimal("0.00")
                diff_foreign = Decimal("0.00")
                diff_sign = "-"
        except Exception:
            budget_krw = Decimal("0.00")
            budget_foreign = Decimal("0.00")
            diff_krw = Decimal("0.00")
            diff_foreign = Decimal("0.00")
            diff_sign = "-"
        
        # 기본파견비용
        base_dispatch_payload = {
            "total": {"foreign_amount": Decimal("0.00"), "foreign_currency": foreign_currency, "krw_amount": Decimal("0.00"), "krw_currency": "KRW"},
            "airfare": None, "insurance": None, "visa": None, "tuition": None
        }

        if budget and hasattr(budget, "base_budget"):
            base_budget = budget.base_budget
            items = base_budget.items.all()

            total_krw = Decimal("0.00")
            total_foreign = Decimal("0.00")

            for item in items:
                krw_amount = item.exchange_amount.quantize(Decimal("0.01"))
                foreign_amount = convert_from_krw(krw_amount, foreign_currency)
                if foreign_amount is None:
                    foreign_amount = Decimal("0.00")

                total_krw += krw_amount
                total_foreign += foreign_amount
                
                payload_item = {
                    "foreign_amount": foreign_amount.quantize(Decimal("0.01")) if foreign_amount else Decimal("0.00"),
                    "foreign_currency": foreign_currency,
                    "krw_amount": krw_amount,
                    "krw_currency": "KRW",
                }

                if item.type == BaseBudgetItem.BaseItem.FLIGHT:
                    base_dispatch_payload["airfare"] = payload_item
                elif item.type == BaseBudgetItem.BaseItem.INSURANCE:
                    base_dispatch_payload["insurance"] = payload_item
                elif item.type == BaseBudgetItem.BaseItem.VISA:
                    base_dispatch_payload["visa"] = payload_item
                elif item.type == BaseBudgetItem.BaseItem.TUITION:
                    base_dispatch_payload["tuition"] = payload_item

            base_dispatch_payload["total"] = {
                "foreign_amount": total_foreign.quantize(Decimal("0.01")),
                "foreign_currency": foreign_currency,
                "krw_amount": total_krw.quantize(Decimal("0.01")),
                "krw_currency": "KRW",
            }

        # 카테고리 리스트
        label_map = self._category_label_map()
        existing_codes = [code for code, _ in LedgerEntry.Category.choices]

        categories_payload = []
        for code in existing_codes:
            # 용돈은 빼주기
            if code == "ALLOWANCE":
                continue

            summed = category_totals.get(code, {
                "krw": Decimal("0.00"),
                "foreign": Decimal("0.00"),
            })
            categories_payload.append(
                {
                    "code": code,
                    "label": label_map.get(code, code),
                    "foreign_amount": summed["foreign"],
                    "foreign_currency": foreign_currency,
                    "krw_amount": summed["krw"],
                    "krw_currency": "KRW",
                    "budget_diff": {   # 카테고리에서는 원화 보여주지 않음...(교환국 화폐 기준 보여주기)
                        "foreign_amount": None,
                        "foreign_currency": foreign_currency,
                    },
                }
            )

            # 최종 응답
            payload = {
                "month": today.strftime("%Y-%m"),
                "living_expense": {
                    "foreign_amount": living_foreign_total,
                    "foreign_currency": foreign_currency,
                    "krw_amount": living_krw_total,
                    "krw_currency": "KRW",
                },
                "living_expense_budget_diff": {
                    "foreign_amount": diff_foreign.quantize(Decimal("0.01")),
                    "foreign_currency": foreign_currency,
                    "krw_amount": diff_krw.quantize(Decimal("0.01")),
                    "krw_currency": "KRW",
                    "sign": diff_sign,  # +면 더 쓴 거, -면 덜 쓴 거. 예산안 대비.
                },
                "categories": categories_payload,
                "base_dispatch_cost": base_dispatch_payload,
            }

        serializer = MonthlyCategoryDashboardSerializer(payload)
        return ok("내 가계부 카테고리별 합산 조회 성공", serializer.data)

    def _to_krw(self, entry: LedgerEntry):
        if entry.currency_code == "KRW":
            return entry.amount
        return convert_to_krw(entry.amount, entry.currency_code)

    def _to_foreign(self, krw_amount: Decimal, foreign_currency: str):
        if foreign_currency == "KRW":
            return krw_amount
        converted = convert_from_krw(krw_amount, foreign_currency)
        if converted is None:
            return Decimal("0.00")
        return converted

    def _foreign_currency(self, user):
        exchange_profile = getattr(user, "exchange_profile", None)
        if not exchange_profile:
            return "KRW"

        country_name = getattr(exchange_profile, "exchange_country", None)
        if not country_name:
            return "KRW"

        name = country_name.strip()
        return COUNTRY_TO_CURRENCY.get(name, "KRW")

    def _category_label_map(self):
        return {code: label for code, label in LedgerEntry.Category.choices}


class LedgerEntryDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_entry(self, request, ledger_id):
        try:
            return LedgerEntry.objects.get(id=ledger_id, user=request.user)
        except LedgerEntry.DoesNotExist:
            return None

    def put(self, request, ledger_id):
        entry = self._get_entry(request, ledger_id)
        if entry is None:
            return bad("수정 실패", "없거나 권한 없음", status=404)

        old_date = entry.date

        serializer = LedgerEntryCreateSerializer(
            entry,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        if not serializer.is_valid():
            return bad("유효성 검사 실패", serializer.errors, status=400)

        updated = serializer.save()

        if updated.date != old_date:
            old_month = old_date.replace(day=1)
            new_month = updated.date.replace(day=1)

            try:
                old_ledger = Ledger.objects.get(user=request.user, month=old_month)
                old_ledger.ledger_entries.remove(updated)
            except Ledger.DoesNotExist:
                pass

            new_ledger, _ = Ledger.objects.get_or_create(
                user=request.user,
                month=new_month,
            )
            new_ledger.ledger_entries.add(updated)

        return ok(
            "가계부 항목이 수정되었습니다.",
            LedgerEntrySimpleSerializer(updated).data,
            status=200,
        )

    def delete(self, request, ledger_id):
        entry = self._get_entry(request, ledger_id)
        if entry is None:
            return bad("삭제 실패", "없거나 권한 없음", status=404)

        entry.delete()
        return Response({"message": "가계부 항목이 삭제되었습니다."}, status=204)


class ThisMonthSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = date.today()
        month_start = today.replace(day=1)
        entries = LedgerEntry.objects.filter(
            user=user,
            date__gte=month_start,
            date__lte=today,
        )

        result = self._calculate_summary(user, entries, today)
        serializer = ThisMonthSummarySerializer(result)
        return ok("이번달 수입/지출 합계 조회 성공", serializer.data)

    def _calculate_summary(self, user, entries, today=None):
        foreign_currency = self._foreign_currency(user)

        def _sum(entry_type):
            qs = entries.filter(entry_type=entry_type)
            total_foreign = Decimal("0.00")
            total_krw = Decimal("0.00")

            for entry in qs:
                if entry.amount_converted and entry.converted_currency_code == "KRW":
                    krw_amount = entry.amount_converted
                else:
                    krw_amount = (
                        entry.amount if entry.currency_code == "KRW"
                        else convert_to_krw(entry.amount, entry.currency_code)
                    )

                if krw_amount is None:
                    continue

                total_krw += krw_amount

                if foreign_currency == "KRW":
                    total_foreign += krw_amount
                else:
                    if entry.amount_converted and entry.converted_currency_code == foreign_currency:
                        total_foreign += entry.amount_converted
                    else:
                        foreign_amount = convert_from_krw(krw_amount, foreign_currency)
                        if foreign_amount:
                            total_foreign += foreign_amount

            total_foreign = total_foreign.quantize(Decimal("0.01"))
            total_krw = total_krw.quantize(Decimal("0.01"))
            return total_foreign, total_krw

        income_foreign, income_krw = _sum(LedgerEntry.EntryType.INCOME)
        expense_foreign, expense_krw = _sum(LedgerEntry.EntryType.EXPENSE)

        return {
            "month": today.strftime("%Y-%m") if today else "전체 기간",
            "foreign_currency": foreign_currency,
            "income_foreign": income_foreign,
            "income_krw": income_krw,
            "expense_foreign": expense_foreign,
            "expense_krw": expense_krw,
        }

    def _foreign_currency(self, user):
        exchange_profile = getattr(user, "exchange_profile", None)
        if not exchange_profile:
            return "KRW"

        country_name = getattr(exchange_profile, "exchange_country", None)
        if not country_name:
            return "KRW"

        name = country_name.strip()
        return COUNTRY_TO_CURRENCY.get(name, "KRW")


class TotalSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        entries = LedgerEntry.objects.filter(user=user)

        result = self._calculate_summary(user, entries)
        serializer = ThisMonthSummarySerializer(result)
        return ok("전체 수입/지출 합계 조회 성공", serializer.data)

    def _calculate_summary(self, user, entries, today=None):
        foreign_currency = self._foreign_currency(user)

        def _sum(entry_type):
            qs = entries.filter(entry_type=entry_type)
            total_foreign = Decimal("0.00")
            total_krw = Decimal("0.00")

            for entry in qs:
                if entry.amount_converted and entry.converted_currency_code == "KRW":
                    krw_amount = entry.amount_converted
                else:
                    krw_amount = (
                        entry.amount if entry.currency_code == "KRW"
                        else convert_to_krw(entry.amount, entry.currency_code)
                    )

                if krw_amount is None:
                    continue

                total_krw += krw_amount

                if foreign_currency == "KRW":
                    total_foreign += krw_amount
                else:
                    if entry.amount_converted and entry.converted_currency_code == foreign_currency:
                        total_foreign += entry.amount_converted
                    else:
                        foreign_amount = convert_from_krw(krw_amount, foreign_currency)
                        if foreign_amount:
                            total_foreign += foreign_amount

            total_foreign = total_foreign.quantize(Decimal("0.01"))
            total_krw = total_krw.quantize(Decimal("0.01"))
            return total_foreign, total_krw

        income_foreign, income_krw = _sum(LedgerEntry.EntryType.INCOME)
        expense_foreign, expense_krw = _sum(LedgerEntry.EntryType.EXPENSE)

        return {
            "month": today.strftime("%Y-%m") if today else "전체 기간",
            "foreign_currency": foreign_currency,
            "income_foreign": income_foreign,
            "income_krw": income_krw,
            "expense_foreign": expense_foreign,
            "expense_krw": expense_krw,
        }

    def _foreign_currency(self, user):
        exchange_profile = getattr(user, "exchange_profile", None)
        if not exchange_profile:
            return "KRW"

        country_name = getattr(exchange_profile, "exchange_country", None)
        if not country_name:
            return "KRW"

        name = country_name.strip()
        return COUNTRY_TO_CURRENCY.get(name, "KRW")
