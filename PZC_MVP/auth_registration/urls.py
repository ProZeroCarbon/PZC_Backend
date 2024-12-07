# auth_registration/urls.py
from django.urls import path
from .views import Registercreate,RegisterView,RegisterUpdate,RegisterDelete, LoginView,LogoutView,AdminDashboardView,Add_Summary,GetSummaries,SuperuserListView,ReportUpload,DownloadReport
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # JWT-Token Refresh Start
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # JWT-Token Refresh End

    # APIs for Registration and Login
    path('login/', LoginView.as_view(), name='login'),
    path('add_clients/', Registercreate.as_view(), name='add_clients'),
    path('view_clients/',RegisterView.as_view(),name="view_clients"),
    path('update_clients/<str:user_id>/',RegisterUpdate.as_view(),name="update_clients"),
    path('delete_clients/<str:user_id>/',RegisterDelete.as_view(),name="delete_clients"),
    
    
    path("admin_dashboard/",AdminDashboardView.as_view(),name="admin_dash"),
    path("add_summary/",Add_Summary.as_view(),name="add_summary"),
    path("view_summary/",GetSummaries.as_view(),name="view_summary"),
    
    
    path('upload_report/',ReportUpload.as_view(),name="upload_report"),
    path('download_report/',DownloadReport.as_view(),name="download_report"),
    
    path('superusers/',SuperuserListView.as_view(),name='superuser'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
