from django.urls import path
from .views import *

app_name = 'rates'

urlpatterns = [
    path('convert/', ConvertView.as_view(), name='convert-currency'),
]