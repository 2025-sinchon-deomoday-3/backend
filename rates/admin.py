from django.contrib import admin
from .models import * 

# Register your models here.
@admin.register(ExchangeRates)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display  = ("id","base_currency", "target_currency", "rate")
    search_fields = ("target_currency")
    ordering      = ("id")

