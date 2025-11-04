from django.urls import path
from .views import *

app_name = 'summaries'

urlpatterns = [
    path("detail-profile/", DetailProfileView.as_view(), name="detail-profile"),
]