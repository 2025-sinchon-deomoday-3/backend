from django.db import migrations, models
from django.conf import settings
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ("summaries", "0002_detailprofile_summary_note_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="SummarySnapshot",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("snapshot_nickname", models.CharField(max_length=50, blank=True)),
                ("snapshot_gender", models.CharField(max_length=20, blank=True)),
                ("snapshot_exchange_country", models.CharField(max_length=50, blank=True)),
                ("snapshot_exchange_university", models.CharField(max_length=120, blank=True)),
                ("snapshot_exchange_type", models.CharField(max_length=20, blank=True)),
                ("snapshot_exchange_semester", models.CharField(max_length=40, blank=True)),
                ("snapshot_exchange_period", models.CharField(max_length=40, blank=True)),
                ("living_expense_foreign_amount", models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))),
                ("living_expense_foreign_currency", models.CharField(max_length=5, blank=True, help_text="교환국 통화 코드 (USD, JPY ...)")),
                ("living_expense_krw_amount", models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))),
                ("living_expense_krw_currency", models.CharField(max_length=3, default="KRW")),
                ("base_dispatch_foreign_amount", models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)),
                ("base_dispatch_krw_amount", models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "detail_profile",
                    models.ForeignKey(
                        to="summaries.detailprofile",
                        on_delete=models.SET_NULL,
                        null=True,
                        blank=True,
                        related_name="snapshots_detail_profile",
                    ),
                ),
                (
                    "exchange_profile",
                    models.ForeignKey(
                        to="accounts.exchangeprofile",
                        on_delete=models.SET_NULL,
                        null=True,
                        blank=True,
                        related_name="snapshots_exchange_profile",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        to=settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                        related_name="snapshots_user",
                    ),
                ),
            ],
            options={
                "db_table": "summaries_summarysnapshot",
            },
        ),
    ]
