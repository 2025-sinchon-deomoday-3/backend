from django.urls import path
from .views import *

app_name = 'budgets'

urlpatterns = [
    path('fill/', BudgetView.as_view(), name='budget-view'),
    # path('base-budget/', BaseBudgetView.as_view(), name='base-budget-view'),
    # path('living-budget/',LivingBudgetView.as_view(), name= 'living-budget-view')
]