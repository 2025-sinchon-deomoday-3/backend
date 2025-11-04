from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, date as date_type
from collections import defaultdict
from django.db.models import QuerySet

from .serializers import *
from .models import *


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
        qs = (
            LedgerEntry.objects
            .filter(user=request.user)
            .order_by("-date", "-created_at")
        )

        months = defaultdict(list)
        for e in qs:
            months[e.date.replace(day=1)].append(e)

        cat_order = self._category_order()
        cat_label = self._category_label_map()

        month_blocks = []
        for month_key in sorted(months.keys(), reverse=True):
            by_cat = defaultdict(list)
            for e in months[month_key]:
                by_cat[e.category].append(e)

            categories = []
            for code in cat_order:
                entries = by_cat.get(code, [])
                items = LedgerEntrySimpleSerializer(entries, many=True).data
                categories.append(
                    {
                        "code": code,
                        "label": cat_label.get(code, code),
                        "items": items,
                    }
                )

            month_blocks.append(
                {
                    "month": month_key.strftime("%Y-%m"),
                    "categories": categories,
                }
            )

        return ok("내 가계부 카테고리별 조회 성공", month_blocks)

    def _category_order(self):
        order = [
            "FOOD",
            "HOUSING",
            "TRANSPORT",
            "SHOPPING",
            "TRAVEL",
            "STUDY_MATERIALS",
            "ALLOWANCE",
            "ETC",
        ]
        existing = {code for code, _ in LedgerEntry.Category.choices}
        return [c for c in order if c in existing] + [
            c for c in existing if c not in order
        ]

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
