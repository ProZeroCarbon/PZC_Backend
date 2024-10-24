# myapp/urls.py

from django.urls import path
from .views import RegisterView, LoginView, DashboardView, LogoutView,WasteCreateView,WasteView,WasteEditView,WasteDeleteView,EnergyCreateView,EnergyView,EnergyEditView,EnergyDeleteView,WaterView,WaterCreateView,WaterEditView,WaterDeleteView,BiodiversityCreateView,BiodiversityView,BiodiversityEditView,BiodiversityDeleteView,FacilityCreateView,UploadDataCreateView

urlpatterns = [
   #Apis for Registration and Login  starts
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    #Apis for Registration and Login Ends
     
   #Apis for Waste Crud Operations starts
    
    path('add_waste/', WasteCreateView.as_view(), name='add_waste'),
    path('view_waste/',WasteView.as_view(),name='view_waste'),
    path('waste_update/<int:pk>/update/', WasteEditView.as_view(), name='waste_update'),
    path('waste_delete/<int:pk>/delete/', WasteDeleteView.as_view(), name='waste_delete'),
    
   #Apis for Waste Crud Operations Ends
    
    #Apis for Energy Crud Operations starts
    path('add_energy/',EnergyCreateView.as_view(),name='add_energy'),
    path('view_energy/',EnergyView.as_view(),name="view_energy"),
    path('energy_update/<int:pk>/update/', EnergyEditView.as_view(), name='energy_update'),
    path('energy_delete/<int:pk>/delete/', EnergyDeleteView.as_view(), name='energy_delete'),
    
   #Apis for Energy Crud Operations Ends
    
   #Apis for Water Crud Operations starts
    
    path('add_water/',WaterCreateView.as_view(),name='add_water'),
    path('view_water/',WaterView.as_view(),name='View_water'),
    path('water_update/<int:pk>/', WaterEditView.as_view(), name='water_update'),
    path('water_delete/<int:pk>/delete/', WaterDeleteView.as_view(), name='water_delete'),
    
   #Apis for Water Crud Operations Ends
     
   #Apis for Biodiversity Crud Operations starts
    
    path('add_biodiversity/',BiodiversityCreateView.as_view(),name='add_biodiversity'),
    path('view_biodiversity/',BiodiversityView.as_view(),name='view_biodiversity'),
    path('biodiversity_update/<int:pk>/update/', BiodiversityEditView.as_view(), name='biodiversity_update'),
    path('biodiversity/delete<int:pk>/delete/', BiodiversityDeleteView.as_view(), name='biodiversity_delete'),
    
   #Apis for Biodiversity Crud Operations Ends
    
    path('add_facility/',FacilityCreateView.as_view(),name='add_facility'),
    path('add_upload_data/',UploadDataCreateView.as_view(),name='add_upload_data')
]
