# auth_registration/urls.py
from django.urls import path
from .views import RegisterView, LoginView, LogoutView,AdminDashboardView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # JWT-Token Refresh Start
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # JWT-Token Refresh End

    # APIs for Registration and Login
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path("admin_dashboard/",AdminDashboardView.as_view(),name="admin_dash"),
    path('superusers/',AdminDashboardView.as_view(),name='superuser'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
