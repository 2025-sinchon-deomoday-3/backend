from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

app_name = 'accounts'

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path("token/refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # 로그인(토큰 발급)
]