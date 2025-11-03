from django.contrib import admin
from .models import * 

# Register your models here.
@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display  = ["id","base_currency", "target_currency", "rate"]
    search_fields = ["target_currency"]
    ordering      = ["id"]

