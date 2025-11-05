from django.urls import path
from .views import *

app_name = 'accounts'

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path("token/refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"),

    # 회원가입 시 본교, 파견국가, 파견학교 검색
    path("universities/", UniversitySearchView.as_view(), name="university_list"),
    path("countries/", CountryListView.as_view(), name="country_list"),
    path("exchange-universities/", ExchangeUniversitySearchView.as_view(), name="exchange_university_list"),

    # 프로필
    path("profile/", MyProfileView.as_view(), name="my-profile"),
]