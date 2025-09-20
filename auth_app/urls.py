from django.urls import path
from .views import UserDetailView, LogoutView, CookieTokenObtainPairView, CookieTokenRefreshView

urlpatterns = [
    path('user/', UserDetailView.as_view(), name='user_detail'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/', CookieTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
]
