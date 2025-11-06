from django.contrib import admin
from .models import * 
# Register your models here.

# Register your models here.
@admin.register(Budget)
class BugetAdmin(admin.ModelAdmin):
    list_display  = ["id","user", "created_at", "updated_at"]
    search_fields = ["user"]
    ordering      = ["id"]


@admin.register(BaseBudget)
class BaseBudgetAdmin(admin.ModelAdmin):
    list_display = ["id", "total_amount_krw", "created_at", "updated_at"]
    search_fields = ["user"]
    ordering = ["id"]


@admin.register(BaseBudgetItem)
class BaseBudgetItemAdmin(admin.ModelAdmin):
    list_display = ["id", "type", "amount", "currency", "created_at", "updated_at"]
    ordering = ["id"]

@admin.register(LivingBudget)
class LivingBudgetAdmin(admin.ModelAdmin):
    list_display = ["id", "total_amount","created_at", "updated_at"]
    ordering = ["id"]


@admin.register(LivingBudgetItem)
class LivingBudgetItemAdmin(admin.ModelAdmin):
    list_display = ["id", "type", "amount", "created_at", "updated_at"]
    ordering = ["id"]
    

