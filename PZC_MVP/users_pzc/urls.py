

from django.urls import   path
from .views import RegisterView, LoginView, DashboardView, LogoutView,WasteCreateView,WasteView,WasteEditView,WasteDeleteView,EnergyCreateView,EnergyView,EnergyEditView,EnergyDeleteView,WaterView,WaterCreateView,WaterEditView,WaterDeleteView,BiodiversityCreateView,BiodiversityView,BiodiversityEditView,BiodiversityDeleteView,FacilityCreateView,FacilityView,FacilityEditView,FacilityDeleteView,LogisticesCreateView,LogisticesView,LogisticesEditView,LogisticesDeleteView,OrganizationCreate,OrganizationView,FoodWasteOverviewView,FoodWasteViewCard,SolidWasteOverviewView,SolidWasteViewCard,E_WasteOverviewView,E_WasteViewCard,Biomedical_WasteOverviewView,Biomedical_WasteViewCard,Liquid_DischargeOverviewView,Liquid_DischargeViewCard,OthersOverviewView,OthersViewCard,Waste_Sent_For_RecycleOverviewView,Sent_For_RecycleViewCard,Waste_Sent_For_LandFillOverviewView,Sent_For_LandFillViewCard,StackedWasteOverviewView,WasteOverallDonutChartView,SentToLandfillOverviewView,SentToRecycledOverviewView,HVAC_CardOverview,HVACOverviewView,ProductionOverViewCard,ProductionOverviewView,StpOverViewCard,StpOverviewView,Admin_BlockOverViewCard,Admin_BlockOverviewView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
urlpatterns = [
   
   #JWT-Token Refresh Starts
   path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
   path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
   #JWT-Token Refresh Ends
   
   #Apis for Registration and Login  starts
   path('register/', RegisterView.as_view(), name='register'),
   path('login/', LoginView.as_view(), name='login'),
   path('dashboard/', DashboardView.as_view(), name='dashboard'),
   path('logout/', LogoutView.as_view(), name='logout'),
   #Apis for Registration and Login Ends
    
   #Apis For Organization_Registration Starts
   path('Organization_Create/',OrganizationCreate.as_view(),name='Organization_Create'),
   path('Organization_view/',OrganizationView.as_view(),name='Organization_view'),
   #Apis For Organization_Registration Ends
    
   #Apis for Facility Crud Operations Starts
   path('add_facility/',FacilityCreateView.as_view(),name='add_facility'),
   path('view_facility/',FacilityView.as_view(),name='view_facility'),
   path('update_facility/<int:pk>/update/',FacilityEditView.as_view(),name='update_facility'),
   path('delete_facility/<int:pk>/',FacilityDeleteView.as_view(),name='delete_facility'),
   #Apis for Facility Crud Operations Ends
     
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
   path('biodiversity/<int:pk>/delete/', BiodiversityDeleteView.as_view(), name='biodiversity_delete'),
   #Apis for Biodiversity Crud Operations Ends
    
   #Apis for Logistices Crud Operations starts
   path('add_logistices/',LogisticesCreateView.as_view(),name='add_logistices'),
   path('view_logistices/',LogisticesView.as_view(),name='add_logistices'),
   path('update_logistices/<int:pk>/update',LogisticesEditView.as_view(),name='add_logistices'),
   path('delete_logistices/<int:pk>/',LogisticesDeleteView.as_view(),name='add_logistices'),
   #Apis for Logistices Crud Operations Ends
   
   
   
   #Apis for Waste overviewgraphs starts
   path('FoodWasteOverviewView/',FoodWasteOverviewView.as_view(),name="FoodWasteOverview"),
   path('FoodWasteViewCard/',FoodWasteViewCard.as_view(),name="FoodWasteViewCard"),
   
   path('SolidWasteOverviewView/',SolidWasteOverviewView.as_view(),name="SolidWasteOverviewView"),
   path('SolidWasteViewCard/',SolidWasteViewCard.as_view(),name="SolidWasteViewCard"),
   
   path('E_WasteOverviewView/',E_WasteOverviewView.as_view(),name="E_WasteOverviewView"),
   path('E_WasteViewCard/',E_WasteViewCard.as_view(),name="E_WasteViewCard"),
   
   path('Biomedical_WasteOverviewView/',Biomedical_WasteOverviewView.as_view(),name="Biomedical_WasteOverviewView"),
   path('Biomedical_WasteViewCard/',Biomedical_WasteViewCard.as_view(),name="Biomedical_WasteViewCard"),
   
   
   path('Liquid_DischargeOverviewView/',Liquid_DischargeOverviewView.as_view(),name="Liquid_DischargeOverviewView"),
   path('Liquid_DischargeViewCard/',Liquid_DischargeViewCard.as_view(),name='Liquid_DischargeViewCard'),
   
   path('OthersOverviewView/',OthersOverviewView.as_view(),name='OthersOverviewView'),
   path('OthersViewCard/',OthersViewCard.as_view(),name='OthersViewCard'),
   
   path('Waste_Sent_For_RecycleOverviewView/',Waste_Sent_For_RecycleOverviewView.as_view(),name='Waste_Sent_For_RecycleOverviewView'),
   path('Sent_For_RecycleViewCard/',Sent_For_RecycleViewCard.as_view(),name='Sent_For_RecycleViewCard'),
   
   path('Waste_Sent_For_LandFillOverviewView/',Waste_Sent_For_LandFillOverviewView.as_view(),name='Waste_Sent_For_LandFillOverviewView'),
   path('Sent_For_LandFillViewCard/',Sent_For_LandFillViewCard.as_view(),name='Sent_For_LandFillViewCard'),
   
   #Apis For Stacked Graph,donuts Graphs Overview
   path('StackedWasteOverviewView/',StackedWasteOverviewView.as_view(),name='StackedWasteOverviewView'),
   path('WasteOverallDonutChartView/',WasteOverallDonutChartView.as_view(),name='WasteOverallDonutChartView'),
   path('Sent_To_Landfill_OverviewView/',SentToLandfillOverviewView.as_view(),name='Sent_To_Landfill_OverviewView'),
   path('SentToRecycledOverviewView/',SentToRecycledOverviewView.as_view(),name='SentToRecycledOverviewView'),
   #Apis for Waste overviewgraphs Ends
   

   #Apis For Energy overview
   path('HVAC_CardOverview/',HVAC_CardOverview.as_view(),name='HVAC_CardOverview'),
   path('HVACOverviewView/',HVACOverviewView.as_view(),name='HVACOverviewView'),
   
   path('ProductionOverViewCard/',ProductionOverViewCard.as_view(),name='ProductionOverViewCard'),
   path('ProductionOverviewView/',ProductionOverviewView.as_view(),name='ProductionOverviewView'),
   
   path('StpOverViewCard/',StpOverViewCard.as_view(),name='StpOverViewCard'),
   path('StpOverviewView/',StpOverviewView.as_view(),name='StpOverviewView'),
   
   path('Admin_BlockOverViewCard/',Admin_BlockOverViewCard.as_view(),name='Admin_BlockOverViewCard'),
   path('Admin_BlockOverviewView/',Admin_BlockOverviewView.as_view(),name='Admin_BlockOverviewView'),
   
   
   
   
    
    
]
