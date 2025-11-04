from django.urls import path
from .views import *

app_name = 'ledgers'

urlpatterns = [
    path('fill/', LedgerEntryCreateView.as_view(), name='ledgerCreate'),
    path("date/", MyLedgerAllDateView.as_view(), name="ledger_by_date"),
    path("category/", MyLedgerAllCategoryView.as_view(), name="ledger_by_category"),
    path("fill/<int:ledger_id>/", LedgerEntryDetailView.as_view(), name="ledger_detail"),
    path("fill/<int:ledger_id>", LedgerEntryDetailView.as_view()), # 슬래시 없는 url도 가능하도록
]