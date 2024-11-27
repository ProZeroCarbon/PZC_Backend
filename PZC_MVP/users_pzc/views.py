import traceback
import pandas as pd
from datetime import datetime
from collections import defaultdict
from django.db.models import Sum, Value, FloatField,Min, Max,F
from django.db.models.functions import Coalesce, Cast, ExtractMonth
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegisterSerializer, UserLoginSerializer,WasteSerializer,WasteCreateSerializer,EnergyCreateSerializer,EnergySerializer,WaterCreateSerializer,WaterSerializer,BiodiversityCreateSerializer,BiodiversitySerializer,FacilitySerializer,LogisticsSerializer,OrganizationSerializer,FileUploadSerializer
from .models import CustomUser,Waste,Energy,Water,Biodiversity,Facility,Logistics,Org_registration
from django.db.models import Q
from django.db.models import Field
import logging

logger = logging.getLogger(__name__)

#Register View
class RegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"msg": "User registered successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#LoginView
class LoginView(APIView):
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(email=email, password=password)  # Use authenticate here
            if user is None:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

            refresh = RefreshToken.for_user(user)
            response = Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
            response.set_cookie('access_token', str(refresh.access_token), httponly=True)
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#Dashboard View
class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_data = {
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'password':request.user.password
        }
        return Response(user_data, status=status.HTTP_200_OK)



'''Organization Crud Operations Starts'''

# OrganizationCreate
class OrganizationCreate(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = OrganizationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Organization Registration added successfully"}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# OrganizationView
class OrganizationView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        org_reg_data = Org_registration.objects.filter(user=user)
        organization_serializer = OrganizationSerializer(org_reg_data, many=True)
        user_data = {
            'email': user.email,
            'org_reg_data': organization_serializer.data
        }
        return Response(user_data, status=status.HTTP_200_OK)
'''Oragnization Crud Operations Ends'''

'''Facility Crud Operations starts'''
#FacilityCreate
class FacilityCreateView(APIView):
    permission_classes = [IsAuthenticated] 

    def post(self, request):
        serializer = FacilitySerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Facility added successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class FacilityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', 'all')
        location = request.GET.get('location')
        action = request.GET.get('action')

        # Start by filtering facilities by the user
        facility_data = Facility.objects.filter(user=user)

        # Apply optional filters based on query parameters
        if facility_id.lower() != 'all':
            facility_data = facility_data.filter(facility_id=facility_id)
        
        if location:
            facility_data = facility_data.filter(location__icontains=location)

        if action:
            facility_data = facility_data.filter(action__icontains=action)

        # Serialize and prepare the response
        facility_serializer = FacilitySerializer(facility_data, many=True)
        
        user_data = {
            'email': user.email,
            'facility_data': facility_serializer.data,
        }
        
        return Response(user_data, status=status.HTTP_200_OK)

class FacilityEditView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, facility_id):
        try:
            facility = Facility.objects.get(facility_id=facility_id, user=request.user)
        except Facility.DoesNotExist:
            return Response({"error": "Facility not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = FacilitySerializer(facility, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Facility updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#FacilityDelete
class FacilityDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, facility_id):
        if not isinstance(facility_id, str) or len(facility_id) != 8:
            return Response({"error": "Invalid facility ID provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Try to get the facility using facility_id
            facility = Facility.objects.get(facility_id=facility_id, user=request.user)
            facility.delete()
            return Response({"message": "Facility deleted successfully."}, status=status.HTTP_200_OK)
        except Facility.DoesNotExist:
            return Response({"error": "Facility not found."}, status=status.HTTP_404_NOT_FOUND)
      
'''Facility Crud Operations Ends'''


'''Waste CRUD Operations Starts'''
#Watste Create Form
# class WasteCreateView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         serializer = WasteCreateSerializer(data=request.data, context={'request': request})
#         if serializer.is_valid():
#             serializer.save()
#             return Response({"message": "Waste data added successfully."}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WasteCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Check if data is a list (for multiple entries) or a single object
        is_bulk = isinstance(request.data, list)
        if is_bulk:
            serializer = WasteCreateSerializer(data=request.data, many=True, context={'request': request})
        else:
            serializer = WasteCreateSerializer(data=request.data, context={'request': request})

        # Validate and save the serializer
        if serializer.is_valid():
            serializer.save()
            message = "Waste data added successfully." if not is_bulk else "All Waste entries added successfully."
            return Response({"message": message}, status=status.HTTP_201_CREATED)

        # Return validation errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WasteView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', 'all')
        year = request.GET.get('year')
        
        try:
            if year:
                year = int(year)
            else:
                latest_date = Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                
                if latest_date:
                    year = latest_date.year if latest_date.month >= 4 else latest_date.year - 1
                else:
                    current_date = datetime.now()
                    year = current_date.year - 1 if current_date.month < 4 else current_date.year
            
            start_date = datetime(year, 4, 1)
            end_date = datetime(year + 1, 3, 31)
        except ValueError:
            return Response(
                {"error": "Invalid fiscal year format. Please provide a valid year, e.g., 2023."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        waste_data = Waste.objects.filter(user=user, DatePicker__range=(start_date, end_date))

        if facility_id.lower() != 'all':
            waste_data = waste_data.filter(facility__facility_id=facility_id)
            print(f"Filtered Waste Data Count by Facility: {waste_data.count()}")
        else:
            print("Facility ID is 'all'; skipping facility filtering.")
        
        if not waste_data.exists():
            empty_fields = {
                "facility_id":facility_id,
                "food_waste":0,
                "solid_Waste":0,
                "E_Waste":0,
                "Biomedical_waste":0,
                "liquid_discharge":0,
                "other_waste":0,
                "Recycle_waste":0,
                "Landfill_waste":0
            }
            return Response(
                {
                    "message": "No data available for the selected facility and fiscal year.",
                    "email": user.email,
                    "year": year,
                    "waste_data": [empty_fields],
                    "overall_waste_usage_total": 0
                },
                status=status.HTTP_200_OK
            )
        
        waste_serializer = WasteSerializer(waste_data, many=True)
        overall_total = sum(
            (waste.food_waste or 0) + (waste.solid_Waste or 0) + (waste.E_Waste or 0) + 
            (waste.Biomedical_waste or 0) + (waste.other_waste or 0)
            for waste in waste_data
        )
        
        user_data = {
            "email": user.email,
            "year": year, 
            "waste_data": waste_serializer.data,
            "overall_waste_usage_total": overall_total
        }
        
        return Response(user_data, status=status.HTTP_200_OK)

class WasteEditView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, waste_id):
        try:
            waste = Waste.objects.get(waste_id=waste_id, user=request.user)
        except Waste.DoesNotExist:
            return Response({"error": "Waste data not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = WasteCreateSerializer(waste, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Waste data updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#Deletewaste
class WasteDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, waste_id):
        try:
           waste = Waste.objects.get(waste_id=waste_id, user=request.user)
        except Waste.DoesNotExist:
            return Response({"error": "Waste data not found."}, status=status.HTTP_404_NOT_FOUND)

        waste.delete()
        return Response({"message": "Waste data deleted successfully."}, status=status.HTTP_200_OK)

'''Waste CRUD Operations Ends'''

'''Energy CRUD Operations Starts'''
#EnergyCreate
class EnergyCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        is_bulk = isinstance(request.data, list)
        if is_bulk:
            serializer = EnergyCreateSerializer(data=request.data, many=True, context={'request': request})
        else:
            serializer = EnergyCreateSerializer(data=request.data,context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response({"messages":"Energy data added Succesfully"},status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EnergyView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', 'all')
        year = request.GET.get('year')
        
        try:
            if year:
                year = int(year)
            else:
                current_date = datetime.now()
                year = current_date.year - 1 if current_date.month < 4 else current_date.year

            start_date = datetime(year, 4, 1)
            end_date = datetime(year + 1, 3, 31)
        except ValueError:
            return Response(
                {"error": "Invalid fiscal year format. Please provide a valid year, e.g., 2023."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        energy_data = Energy.objects.filter(user=user, DatePicker__range=(start_date, end_date))
        if not energy_data.exists() and not request.GET.get('year'):
            latest_year = year
            while not energy_data.exists() and latest_year > 2000:  # Arbitrary cutoff year
                latest_year -= 1
                start_date = datetime(latest_year, 4, 1)
                end_date = datetime(latest_year + 1, 3, 31)
                energy_data = Energy.objects.filter(user=user, DatePicker__range=(start_date, end_date))
            year = latest_year 
        
        if facility_id.lower() != 'all':
            energy_data = energy_data.filter(facility__facility_id=facility_id)
            print(f"Filtered Energy Data Count by Facility: {energy_data.count()}")
        else:
            print("Facility ID is 'all'; skipping facility filtering.")
        
        if not energy_data.exists():
            return Response(
                {
                    "message": "No data available for the selected facility and fiscal year.",
                    "email": user.email,
                    "year": year,
                    "energy_data": [],
                    "overall_energy_usage_total": 0
                },
                status=status.HTTP_200_OK
            )
        
        # Use the correct serializer (EnergySerializer)
        energy_serializer = EnergySerializer(energy_data, many=True)
        
        # Calculate overall total
        overall_total = sum(
            energy.hvac + energy.production + energy.stp + energy.admin_block + energy.utilities + energy.others
            for energy in energy_data
        )
        
        user_data = {
            "email": user.email,
            "energy_data": energy_serializer.data,
            "overall_energy_usage_total": overall_total
        }
        
        return Response(user_data, status=status.HTTP_200_OK)

class EnergyView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', 'all')
        year = request.GET.get('year')
        
        try:
            if year:
                year = int(year)
            else:
                latest_date = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                
                if latest_date:
                    year = latest_date.year if latest_date.month >= 4 else latest_date.year - 1
                else:
                    current_date = datetime.now()
                    year = current_date.year - 1 if current_date.month < 4 else current_date.year
            
            start_date = datetime(year, 4, 1)
            end_date = datetime(year + 1, 3, 31)
        except ValueError:
            return Response(
                {"error": "Invalid fiscal year format. Please provide a valid year, e.g., 2023."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        energy_data = Energy.objects.filter(user=user, DatePicker__range=(start_date, end_date))

        if facility_id.lower() != 'all':
            energy_data = energy_data.filter(facility__facility_id=facility_id)
            print(f"Filtered energy Data Count by Facility: {energy_data.count()}")
        else:
            print("Facility ID is 'all'; skipping facility filtering.")
        
        if not energy_data.exists():
            empty_fields = {
                "facility_id":"N/A",
                "hvac":0,
                "production":0,
                "stp":0,
                "admin_block":0,
                "utilities":0,
                "others":0,
                "coking_coal":0,
                "coke_oven_coal":0,
                "natural_gas":0,
                "diesel":0,"biomass_wood": 0,
                "biomass_other_solid": 0,
                "renewable_solar": 0,
                "renewable_other": 0,
            }
            return Response(
                {
                    "message": "No data available for the selected facility and fiscal year.",
                    "email": user.email,
                    "year": year,
                    "energy_data": [empty_fields],
                    "overall_energy_usage_total": 0
                },
                status=status.HTTP_200_OK
            )
        
        energy_serializer = EnergySerializer(energy_data, many=True)
        overall_total = sum(
           ( energy.hvac or 0) + (energy.production or 0) + (energy.stp or 0) + (energy.admin_block or 0) + (energy.utilities or 0) + (energy.others or 0)
            for energy in energy_data
        )
        
        
        user_data = {
            "email": user.email,
            "year": year, 
            "energy_data": energy_serializer.data,
            "overall_energy_usage_total": overall_total
        }
        
        return Response(user_data, status=status.HTTP_200_OK)
#EnergyEdit
class EnergyEditView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, energy_id):
        try:
            energy = Energy.objects.get(energy_id=energy_id, user=request.user)
        except Energy.DoesNotExist:
            return Response({"error": "Energy data not found."}, status=status.HTTP_404_NOT_FOUND)
        

        serializer = EnergyCreateSerializer(energy, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Energy data updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#EnergyDelete
class EnergyDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, energy_id):
        try:
            energy = Energy.objects.get(energy_id=energy_id, user=request.user)
        except Energy.DoesNotExist:
            return Response({"error": "Energy data not found."}, status=status.HTTP_404_NOT_FOUND)

        energy.delete()
        return Response({"message": "Energy data deleted successfully."}, status=status.HTTP_200_OK)
'''Energy CRUD Operations Ends'''

'''Water CRUD Operations Starts'''
#waterCreate
class WaterCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        is_bulk = isinstance(request.data, list)
        if is_bulk:
            serializer = WaterCreateSerializer(data=request.data, many=True, context={'request': request})
        else:
            serializer = WaterCreateSerializer(data=request.data,context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response({"messages":"Water data added succesfully"},status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

#WaterView

class WaterView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', 'all')
        year = request.GET.get('year')
        
        try:
            if year:
                year = int(year)
            else:
                latest_date = Water.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                
                if latest_date:
                    year = latest_date.year if latest_date.month >= 4 else latest_date.year - 1
                else:
                    current_date = datetime.now()
                    year = current_date.year - 1 if current_date.month < 4 else current_date.year
            
            start_date = datetime(year, 4, 1)
            end_date = datetime(year + 1, 3, 31)
        except ValueError:
            return Response(
                {"error": "Invalid fiscal year format. Please provide a valid year, e.g., 2023."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        water_data = Water.objects.filter(user=user, DatePicker__range=(start_date, end_date))

        if facility_id.lower() != 'all':
            water_data = water_data.filter(facility__facility_id=facility_id)
            print(f"Filtered water Data Count by Facility: {water_data.count()}")
        else:
            print("Facility ID is 'all'; skipping facility filtering.")
        
        if not water_data.exists():
            empty_fields = {
                "facility_id":"N/A",
                "Generated_Water": 0,
                "Recycled_Water": 0,
                "Softener_usage": 0,
                "Boiler_usage": 0,
                "otherUsage": 0
            }
            return Response(
                {
                    "message": "No data available for the selected facility and fiscal year.",
                    "email": user.email,
                    "year": year,
                    "water_data": [empty_fields],
                    "overall_water_usage_total": 0
                },
                status=status.HTTP_200_OK
            )
        
        water_serializer = WaterSerializer(water_data, many=True)
        overall_total = sum(water.overall_usage for water in water_data)
        
        
        user_data = {
            "email": user.email,
            "year": year, 
            "water_data": water_serializer.data,
            "overall_water_usage_total": overall_total
        }
        
        return Response(user_data, status=status.HTTP_200_OK)

#WaterEdit
class WaterEditView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, water_id):
        try:
            water = Water.objects.get(water_id=water_id,user=request.user)
        except Water.DoesNotExist:
            return Response({"error": "Water data not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = WaterCreateSerializer(water, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Water data updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#WaterDelete
class WaterDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, water_id):
        try:
            water = Water.objects.get(water_id=water_id, user=request.user)
        except Water.DoesNotExist:
            return Response({"error": "Water data not found."}, status=status.HTTP_404_NOT_FOUND)

        water.delete()
        return Response({"message": "Water data deleted successfully."}, status=status.HTTP_200_OK)


'''Water CRUD Operations Ends'''

'''Biodiversity CRUD Operations Starts'''

#biodiversity Create
class BiodiversityCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        is_bulk = isinstance(request.data, list)
        if is_bulk:
            serializer = BiodiversityCreateSerializer(data=request.data, many=True, context={'request': request})
        else:
            serializer = BiodiversityCreateSerializer(data=request.data,context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response({'messages':'Biodiversity data added Succesfully'},status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
#biodiversity View
class BiodiversityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', 'all')
        year = request.GET.get('year')

        try:
            if year:
                year = int(year)
            else:
                latest_date = Biodiversity.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']

                if latest_date:
                    year = latest_date.year if latest_date.month >= 4 else latest_date.year - 1
                else:
                    current_date = datetime.now()
                    year = current_date.year - 1 if current_date.month < 4 else current_date.year

            start_date = datetime(year, 4, 1)
            end_date = datetime(year + 1, 3, 31)
        except ValueError:
            return Response(
                {"error": "Invalid fiscal year format. Please provide a valid year, e.g., 2023."},
                status=status.HTTP_400_BAD_REQUEST
            )

        biodiversity_data = Biodiversity.objects.filter(user=user, DatePicker__range=(start_date, end_date))

        if facility_id.lower() != 'all':
            biodiversity_data = biodiversity_data.filter(facility__facility_id=facility_id)
            print(f"Filtered biodiversity Data Count by Facility: {biodiversity_data.count()}")
        else:
            print("Facility ID is 'all'; skipping facility filtering.")

        if not biodiversity_data.exists():
            empty_fields = {
                "facility_id":"N/A",
                "no_trees": 0,
                "no_plants": 0,
                "water_bodies": 0,
                "wildlife_species": 0,
                "green_cover_area": 0
            }

            return Response(
                {
                    "message": "No data available for the selected facility and fiscal year.",
                    "email": user.email,
                    "year": year,
                    "biodiversity_data": [empty_fields],
                    "overall_biodiversity_usage_total": 0
                },
                status=status.HTTP_200_OK
            )

        biodiversity_serializer = BiodiversitySerializer(biodiversity_data, many=True)
        serialized_data = biodiversity_serializer.data
        for data, biodiversity in zip(serialized_data, biodiversity_data):
            data['facility_id'] = biodiversity.facility.facility_id
            
        overall_total = sum(biodiversity.no_trees for biodiversity in biodiversity_data)

        user_data = {
            "email": user.email,
            "year": year, 
            "biodiversity_data": biodiversity_serializer.data,
            "overall_biodiversity_usage_total": overall_total
        }

        return Response(user_data, status=status.HTTP_200_OK)

#BiodiversityEdit
class BiodiversityEditView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, biodiversity_id):
        try:
            biodiversity = Biodiversity.objects.get(biodiversity_id=biodiversity_id, user=request.user)
        except Biodiversity.DoesNotExist:
            return Response({"error": "Biodiversity data not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = BiodiversityCreateSerializer(biodiversity, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Biodiversity data updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#BiodiversityDelete
class BiodiversityDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, biodiversity_id):
        try:
            biodiversity = Biodiversity.objects.get(biodiversity_id=biodiversity_id, user=request.user)
        except Biodiversity.DoesNotExist:
            return Response({"error": "Biodiversity data not found."}, status=status.HTTP_404_NOT_FOUND)

        biodiversity.delete()
        return Response({"message": "Biodiversity data deleted successfully."}, status=status.HTTP_200_OK)

'''Biodiversity CRUD Operations Ends'''


'''Logistics CRUD Operations Starts'''
#Logistics Create Form
class LogisticsCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        is_bulk = isinstance(request.data, list)
        if is_bulk:
            serializer = LogisticsSerializer(data=request.data, many=True, context={'request': request})
        else:
            serializer = LogisticsSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"message": "Logistics data added successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#View Logistics
class LogisticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', 'all')
        year = request.GET.get('year')

        try:
            if year:
                year = int(year)
            else:
                latest_date = Logistics.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']

                if latest_date:
                    year = latest_date.year if latest_date.month >= 4 else latest_date.year - 1
                else:
                    current_date = datetime.now()
                    year = current_date.year - 1 if current_date.month < 4 else current_date.year

            start_date = datetime(year, 4, 1)
            end_date = datetime(year + 1, 3, 31)
        except ValueError:
            return Response(
                {"error": "Invalid fiscal year format. Please provide a valid year, e.g., 2023."},
                status=status.HTTP_400_BAD_REQUEST
            )

        logistics_data = Logistics.objects.filter(user=user, DatePicker__range=(start_date, end_date))

        if facility_id.lower() != 'all':
            logistics_data = logistics_data.filter(facility__facility_id=facility_id)
            print(f"Filtered logistics Data Count by Facility: {logistics_data.count()}")
        else:
            print("Facility ID is 'all'; skipping facility filtering.")

        if not logistics_data.exists():
            empty_fields = {
                "facility_id":"N/A",
                "logistics_types": "N/A",
                "Typeof_fuel": "N/A",
                "km_travelled": 0,
                "No_Trips": 0,
                "fuel_consumption": 0,
                "No_Vehicles":0,
                "Spends_on_fuel":0
            }

            return Response(
                {
                    "message": "No data available for the selected facility and fiscal year.",
                    "email": user.email,
                    "year": year,
                    "logistics_data": [empty_fields],
                    "overall_logistics_usage_total": 0
                },
                status=status.HTTP_200_OK
            )

        logistics_serializer = LogisticsSerializer(logistics_data, many=True)
        
        serialized_data = logistics_serializer.data
        for data, logistics in zip(serialized_data, logistics_data):
            data['facility_id'] = logistics.facility.facility_id
            
        overall_fuelconsumption = sum(logistics_fuel.fuel_consumption for logistics_fuel in logistics_data)

        user_data = {
            "email": user.email,
            "year": year, 
            "facility_id": facility_id,
            "logistics_data": logistics_serializer.data,
            "overall_logistics_usage_total": overall_fuelconsumption
        }

        return Response(user_data, status=status.HTTP_200_OK)

#Edit Logistics
class LogisticsEditView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, logistics_id):
        try:
            # Retrieve the instance to update
            logistics = Logistics.objects.get(logistics_id=logistics_id, user=request.user)
        except Logistics.DoesNotExist:
            return Response({"error": "Logistics entry not found."}, status=status.HTTP_404_NOT_FOUND)

        # Initialize the serializer with the instance and request data
        serializer = LogisticsSerializer(logistics, data=request.data, context={'request': request})

        # Validate and save
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Logistics data updated successfully."}, status=status.HTTP_200_OK)
        else:
            # Return detailed validation errors
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


#Delete Logistics
class LogisticsDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, logistics_id):
        try:
            logistics = Logistics.objects.get(logistics_id=logistics_id, user=request.user)
        except Logistics.DoesNotExist:
            return Response({"error": "Logistics data not found."}, status=status.HTTP_404_NOT_FOUND)

        logistics.delete()
        return Response({"message": "Logistics data deleted successfully."}, status=status.HTTP_200_OK)

'''Logistics CRUD Operations Ends'''


#Logout View
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        access_token = request.COOKIES.get('access_token')
        refresh_token = request.COOKIES.get('refresh_token')

        if not access_token or not refresh_token:
            return Response(
                {"error": "No active session or tokens found to logout."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
           
            token = RefreshToken(refresh_token)
            token.blacklist() 
        except Exception as e:
            return Response(
                {"error": "Error logging out. Invalid or expired tokens."},
                status=status.HTTP_400_BAD_REQUEST
            )

        response = Response({"message": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')

        return response
    
    
'''OverViwe of allTotal_Usages '''
class OverallUsageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', 'all').lower()
        year = request.GET.get('year')

        try:
            if year:
                year = int(year)
            else:
                latest_date = Logistics.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                
                if latest_date:
                    year = latest_date.year if latest_date.month >= 4 else latest_date.year - 1
                else:
                    current_date = datetime.now()
                    year = current_date.year - 1 if current_date.month < 4 else current_date.year
            
            start_date = datetime(year, 4, 1)
            end_date = datetime(year + 1, 3, 31)
        except ValueError:
            return Response(
                {"error": "Invalid fiscal year format. Please provide a valid year, e.g., 2023."},
                status=status.HTTP_400_BAD_REQUEST
            )

        overall_data = {
            "waste_usage": 0,
            "energy_usage": 0,
            "water_usage": 0,
            "biodiversity_usage": 0,
            "logistics_usage": 0,
        }

        # Filters based on user and date range
        filters = {'user': user, 'DatePicker__range': (start_date, end_date)}
        if facility_id != 'all':
            filters['facility__facility_id'] = facility_id

        # Fetch data for each category and aggregate usage
        waste_data = Waste.objects.filter(**filters)
        overall_data["waste_usage"] = waste_data.aggregate(
            total=Sum('food_waste') + Sum('solid_Waste') + Sum('E_Waste') +
                  Sum('Biomedical_waste') + Sum('other_waste')
        )['total'] or 0

        energy_data = Energy.objects.filter(**filters)
        overall_data["energy_usage"] = energy_data.aggregate(
            total=Sum('hvac') + Sum('production') + Sum('stp') +
                  Sum('admin_block') + Sum('utilities') + Sum('others')
        )['total'] or 0

        water_data = Water.objects.filter(**filters)
        overall_data["water_usage"] = water_data.aggregate(total=Sum('overall_usage'))['total'] or 0

        biodiversity_data = Biodiversity.objects.filter(**filters)
        overall_data["biodiversity_usage"] = biodiversity_data.aggregate(total=Sum('overall_Trees'))['total'] or 0

        logistics_data = Logistics.objects.filter(**filters)
        overall_data["logistics_usage"] = logistics_data.aggregate(total=Sum('total_fuelconsumption'))['total'] or 0

        # If no data is found for the selected filters (year/facility), fetch the latest available data
        if not waste_data.exists() and facility_id == 'all':
            # Fetch the most recent data available from any year, including future years
            waste_data = Waste.objects.filter(user=user).order_by('-DatePicker').first()
            energy_data = Energy.objects.filter(user=user).order_by('-DatePicker').first()
            water_data = Water.objects.filter(user=user).order_by('-DatePicker').first()
            biodiversity_data = Biodiversity.objects.filter(user=user).order_by('-DatePicker').first()
            logistics_data = Logistics.objects.filter(user=user).order_by('-DatePicker').first()

            # Handle None cases and return zero values when no data is found
            if not waste_data:
                waste_data = []
            else:
                waste_data = [waste_data]  # Wrap in a list if data is found

            if not energy_data:
                energy_data = []
            else:
                energy_data = [energy_data]

            if not water_data:
                water_data = []
            else:
                water_data = [water_data]

            if not biodiversity_data:
                biodiversity_data = []
            else:
                biodiversity_data = [biodiversity_data]

            if not logistics_data:
                logistics_data = []
            else:
                logistics_data = [logistics_data]

        # Serialize the data
        waste_serializer = WasteSerializer(waste_data, many=True)
        energy_serializer = EnergySerializer(energy_data, many=True)
        water_serializer = WaterSerializer(water_data, many=True)
        biodiversity_serializer = BiodiversitySerializer(biodiversity_data, many=True)
        logistics_serializer = LogisticsSerializer(logistics_data, many=True)

        # Format the response data
        response_data = {
            "email": user.email,
            "year": year,
            "facility_id": facility_id if facility_id != 'all' else "All facilities",
            "overall_data": overall_data,
            # "details": {
            #     "waste_data": waste_serializer.data if waste_data else [],
            #     "energy_data": energy_serializer.data if energy_data else [],
            #     "water_data": water_serializer.data if water_data else [],
            #     "biodiversity_data": biodiversity_serializer.data if biodiversity_data else [],
            #     "logistics_data": logistics_serializer.data if logistics_data else []
            # }
        }

        return Response(response_data, status=status.HTTP_200_OK)

'''OverViwe of allTotal_Usages'''
    
'''Waste Overviewgraphs and Individual Line charts and donut charts Starts'''
class WasteViewCard_Over(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', 'all')
        facility_location = request.GET.get('facility_location')
        year = request.GET.get('year')

        try:
            if facility_id != 'all' and not Facility.objects.filter(facility_id=facility_id, user=user).exists():
                return Response({'error': 'Invalid facility ID or not associated with the logged-in user.'}, status=status.HTTP_400_BAD_REQUEST)

            if year:
                try:
                    year = int(year)
                    if year < 1900 or year > datetime.now().year + 10:  # Allow future years up to 10 years ahead
                        return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)
                except ValueError:
                    return Response({'error': 'Year must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)

            # Determine the range of dates to query
            if year:
                start_date = datetime(year, 4, 1)
                end_date = datetime(year + 1, 3, 31)
            else:
                # Get the latest year with available data
                latest_entry = Waste.objects.filter(user=user).order_by('-DatePicker').first()
                if latest_entry:
                    latest_year = latest_entry.DatePicker.year
                    year = latest_year if latest_entry.DatePicker.month >= 4 else latest_year - 1
                else:
                    today = datetime.now()
                    year = today.year - 1 if today.month < 4 else today.year

                start_date = datetime(year, 4, 1)
                end_date = datetime(year + 1, 3, 31)

            # Query waste data
            waste_data = Waste.objects.filter(user=user, DatePicker__range=(start_date, end_date))

            # Apply specific facility filter if provided
            if facility_id != 'all':
                waste_data = waste_data.filter(facility__facility_id=facility_id)

            # Apply facility location filter if provided
            if facility_location:
                waste_data = waste_data.filter(facility__location__icontains=facility_location)

            # If no data is found, create a structure with zeros
            waste_fields = [
                'food_waste', 'solid_Waste', 'E_Waste', 'Biomedical_waste',
                'liquid_discharge', 'other_waste', 'Recycle_waste', 'Landfill_waste'
            ]

            response_data = {
                'year': year,
                'overall_waste_totals': {},
                'facility_waste_data': {}
            }

            if not waste_data.exists():
                # Populate zero values when no data exists
                for field in waste_fields:
                    response_data['overall_waste_totals'][f"overall_{field}"] = 0
                    response_data['facility_waste_data'][field] = []
            else:
                for field in waste_fields:
                    # Facility-specific totals
                    facility_waste_data = (
                        waste_data
                        .values('facility__facility_name')
                        .annotate(total=Sum(field))
                        .order_by('-total')
                    )

                    response_data['facility_waste_data'][field] = [
                        {
                            "facility_name": entry['facility__facility_name'],
                            f"total_{field}": entry['total']
                        }
                        for entry in facility_waste_data
                    ]

                    # Overall totals
                    overall_total = waste_data.aggregate(total=Sum(field))['total'] or 0
                    response_data['overall_waste_totals'][f"overall_{field}"] = overall_total

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            print(error_message)
            return Response({'error': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#FoodWaste
class FoodWasteOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            if not year:
                year = self.get_latest_available_year(user)

            try:
                year = int(year)
            except ValueError:
                return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

            start_date, end_date = self.get_fiscal_year_range(year)

            filters = {
                'user': user,
                'DatePicker__range': (start_date.date(), end_date.date())
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__location__icontains'] = facility_location

            waste_data = Waste.objects.filter(**filters)
            if not waste_data.exists():
                return self.get_empty_response(year)

            monthly_food_waste = (
                waste_data
                .values('DatePicker__month')
                .annotate(total_food_waste=Sum('food_waste'))
            )

            food_waste = {month: 0 for month in range(1, 13)}
            for entry in monthly_food_waste:
                food_waste[entry['DatePicker__month']] = entry['total_food_waste']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            line_chart_data = [
                {
                    "month": datetime(1900, month, 1).strftime('%b'),
                    "food_waste": food_waste[month]
                }
                for month in month_order
            ]

            # Prepare facility data for donut chart
            facility_food_waste = (
                waste_data
                .values('facility__facility_name')
                .annotate(total_food_waste=Sum('food_waste'))
                .order_by('-total_food_waste')
            )

            total_food_waste = sum(entry['total_food_waste'] for entry in facility_food_waste)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_food_waste'] / total_food_waste * 100) if total_food_waste else 0,
                }
                for entry in facility_food_waste
            ]

            response_data = {
                "year": year,
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            print(f"Error: {str(e)}")
            print("Traceback:", traceback.format_exc())
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_latest_available_year(self, user):
        latest_waste = Waste.objects.filter(user=user).order_by('-DatePicker').first()
        if latest_waste:
            return latest_waste.DatePicker.year
        return datetime.now().year  # Default to current year if no data is available

    def get_fiscal_year_range(self, year):
        start_date = datetime(year, 4, 1)
        end_date = datetime(year + 1, 3, 31)
        return start_date, end_date

    def get_empty_response(self, year):
        month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
        line_chart_data = [{"month": datetime(1900, month, 1).strftime('%b'), "food_waste": 0} for month in month_order]
        donut_chart_data = [{"facility_name": "No Facility", "percentage": 0}]
        return Response({
            "year": year,
            "line_chart_data": line_chart_data,
            "donut_chart_data": donut_chart_data
        }, status=status.HTTP_200_OK)

#SolidWaste
class SolidWasteOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            if not year:
                year = self.get_latest_available_year(user)

            try:
                year = int(year)
            except ValueError:
                return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

            start_date, end_date = self.get_fiscal_year_range(year)

            filters = {
                'user': user,
                'DatePicker__range': (start_date.date(), end_date.date())
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__location__icontains'] = facility_location

            waste_data = Waste.objects.filter(**filters)
            if not waste_data.exists():
                return self.get_empty_response(year)

            monthly_solid_Waste = (
                waste_data
                .values('DatePicker__month')
                .annotate(total_solid_Waste=Sum('solid_Waste'))
            )

            solid_Waste = {month: 0 for month in range(1, 13)}
            for entry in monthly_solid_Waste:
                solid_Waste[entry['DatePicker__month']] = entry['total_solid_Waste']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            line_chart_data = [
                {
                    "month": datetime(1900, month, 1).strftime('%b'),
                    "solid_Waste": solid_Waste[month]
                }
                for month in month_order
            ]

            # Prepare facility data for donut chart
            facility_solid_Waste = (
                waste_data
                .values('facility__facility_name')
                .annotate(total_solid_Waste=Sum('solid_Waste'))
                .order_by('-total_solid_Waste')
            )

            total_solid_Waste = sum(entry['total_solid_Waste'] for entry in facility_solid_Waste)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_solid_Waste'] / total_solid_Waste * 100) if total_solid_Waste else 0,
                }
                for entry in facility_solid_Waste
            ]

            response_data = {
                "year": year,
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            print(f"Error: {str(e)}")
            print("Traceback:", traceback.format_exc())
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_latest_available_year(self, user):
        latest_waste = Waste.objects.filter(user=user).order_by('-DatePicker').first()
        if latest_waste:
            return latest_waste.DatePicker.year
        return datetime.now().year  # Default to current year if no data is available

    def get_fiscal_year_range(self, year):
        start_date = datetime(year, 4, 1)
        end_date = datetime(year + 1, 3, 31)
        return start_date, end_date

    def get_empty_response(self, year):
        month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
        line_chart_data = [{"month": datetime(1900, month, 1).strftime('%b'), "food_waste": 0} for month in month_order]
        donut_chart_data = [{"facility_name": "No Facility", "percentage": 0}]
        return Response({
            "year": year,
            "line_chart_data": line_chart_data,
            "donut_chart_data": donut_chart_data
        }, status=status.HTTP_200_OK)

#e_waste overview view
class E_WasteOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            if not year:
                year = self.get_latest_available_year(user)

            try:
                year = int(year)
            except ValueError:
                return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

            start_date, end_date = self.get_fiscal_year_range(year)

            filters = {
                'user': user,
                'DatePicker__range': (start_date.date(), end_date.date())
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__location__icontains'] = facility_location

            waste_data = Waste.objects.filter(**filters)
            if not waste_data.exists():
                return self.get_empty_response(year)

            monthly_E_Waste = (
                waste_data
                .values('DatePicker__month')
                .annotate(total_E_Waste=Sum('E_Waste'))
            )

            E_Waste = {month: 0 for month in range(1, 13)}
            for entry in monthly_E_Waste:
                E_Waste[entry['DatePicker__month']] = entry['total_E_Waste']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            line_chart_data = [
                {
                    "month": datetime(1900, month, 1).strftime('%b'),
                    "E_Waste": E_Waste[month]
                }
                for month in month_order
            ]

            # Prepare facility data for donut chart
            facility_E_Waste = (
                waste_data
                .values('facility__facility_name')
                .annotate(total_E_Waste=Sum('E_Waste'))
                .order_by('-total_E_Waste')
            )

            total_E_Waste = sum(entry['total_E_Waste'] for entry in facility_E_Waste)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_E_Waste'] / total_E_Waste * 100) if total_E_Waste else 0,
                }
                for entry in facility_E_Waste
            ]

            response_data = {
                "year": year,
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            print(f"Error: {str(e)}")
            print("Traceback:", traceback.format_exc())
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_latest_available_year(self, user):
        latest_waste = Waste.objects.filter(user=user).order_by('-DatePicker').first()
        if latest_waste:
            return latest_waste.DatePicker.year
        return datetime.now().year 

    def get_fiscal_year_range(self, year):
        start_date = datetime(year, 4, 1)
        end_date = datetime(year + 1, 3, 31)
        return start_date, end_date

    def get_empty_response(self, year):
        month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
        line_chart_data = [{"month": datetime(1900, month, 1).strftime('%b'), "food_waste": 0} for month in month_order]
        donut_chart_data = [{"facility_name": "No Facility", "percentage": 0}]
        return Response({
            "year": year,
            "line_chart_data": line_chart_data,
            "donut_chart_data": donut_chart_data
        }, status=status.HTTP_200_OK)

#biomedical_waste Overview
class Biomedical_WasteOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            if not year:
                year = self.get_latest_available_year(user)

            try:
                year = int(year)
            except ValueError:
                return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

            start_date, end_date = self.get_fiscal_year_range(year)

            filters = {
                'user': user,
                'DatePicker__range': (start_date.date(), end_date.date())
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__location__icontains'] = facility_location

            waste_data = Waste.objects.filter(**filters)
            if not waste_data.exists():
                return self.get_empty_response(year)

            monthly_Biomedical_waste = (
                waste_data
                .values('DatePicker__month')
                .annotate(total_Biomedical_waste=Sum('Biomedical_waste'))
            )

            Biomedical_waste = {month: 0 for month in range(1, 13)}
            for entry in monthly_Biomedical_waste:
                Biomedical_waste[entry['DatePicker__month']] = entry['total_Biomedical_waste']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            line_chart_data = [
                {
                    "month": datetime(1900, month, 1).strftime('%b'),
                    "Biomedical_waste": Biomedical_waste[month]
                }
                for month in month_order
            ]

            # Prepare facility data for donut chart
            facility_Biomedical_waste = (
                waste_data
                .values('facility__facility_name')
                .annotate(total_Biomedical_waste=Sum('Biomedical_waste'))
                .order_by('-total_Biomedical_waste')
            )

            total_Biomedical_waste = sum(entry['total_Biomedical_waste'] for entry in facility_Biomedical_waste)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_Biomedical_waste'] / total_Biomedical_waste * 100) if total_Biomedical_waste else 0,
                }
                for entry in facility_Biomedical_waste
            ]

            response_data = {
                "year": year,
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            print(f"Error: {str(e)}")
            print("Traceback:", traceback.format_exc())
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_latest_available_year(self, user):
        latest_waste = Waste.objects.filter(user=user).order_by('-DatePicker').first()
        if latest_waste:
            return latest_waste.DatePicker.year
        return datetime.now().year 

    def get_fiscal_year_range(self, year):
        start_date = datetime(year, 4, 1)
        end_date = datetime(year + 1, 3, 31)
        return start_date, end_date

    def get_empty_response(self, year):
        month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
        line_chart_data = [{"month": datetime(1900, month, 1).strftime('%b'), "food_waste": 0} for month in month_order]
        donut_chart_data = [{"facility_name": "No Facility", "percentage": 0}]
        return Response({
            "year": year,
            "line_chart_data": line_chart_data,
            "donut_chart_data": donut_chart_data
        }, status=status.HTTP_200_OK)

#Liquid_DischargeOverviewView
class Liquid_DischargeOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            if not year:
                year = self.get_latest_available_year(user)

            try:
                year = int(year)
            except ValueError:
                return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

            start_date, end_date = self.get_fiscal_year_range(year)

            filters = {
                'user': user,
                'DatePicker__range': (start_date.date(), end_date.date())
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__location__icontains'] = facility_location

            waste_data = Waste.objects.filter(**filters)
            if not waste_data.exists():
                return self.get_empty_response(year)

            monthly_liquid_discharge = (
                waste_data
                .values('DatePicker__month')
                .annotate(total_liquid_discharge=Sum('liquid_discharge'))
            )

            liquid_discharge = {month: 0 for month in range(1, 13)}
            for entry in monthly_liquid_discharge:
                liquid_discharge[entry['DatePicker__month']] = entry['total_liquid_discharge']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            line_chart_data = [
                {
                    "month": datetime(1900, month, 1).strftime('%b'),
                    "liquid_discharge": liquid_discharge[month]
                }
                for month in month_order
            ]

            # Prepare facility data for donut chart
            facility_liquid_discharge = (
                waste_data
                .values('facility__facility_name')
                .annotate(total_liquid_discharge=Sum('liquid_discharge'))
                .order_by('-total_liquid_discharge')
            )

            total_liquid_discharge = sum(entry['total_liquid_discharge'] for entry in facility_liquid_discharge)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_liquid_discharge'] / total_liquid_discharge * 100) if total_liquid_discharge else 0,
                }
                for entry in facility_liquid_discharge
            ]

            response_data = {
                "year": year,
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            print(f"Error: {str(e)}")
            print("Traceback:", traceback.format_exc())
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_latest_available_year(self, user):
        latest_waste = Waste.objects.filter(user=user).order_by('-DatePicker').first()
        if latest_waste:
            return latest_waste.DatePicker.year
        return datetime.now().year 

    def get_fiscal_year_range(self, year):
        start_date = datetime(year, 4, 1)
        end_date = datetime(year + 1, 3, 31)
        return start_date, end_date

    def get_empty_response(self, year):
        month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
        line_chart_data = [{"month": datetime(1900, month, 1).strftime('%b'), "food_waste": 0} for month in month_order]
        donut_chart_data = [{"facility_name": "No Facility", "percentage": 0}]
        return Response({
            "year": year,
            "line_chart_data": line_chart_data,
            "donut_chart_data": donut_chart_data
        }, status=status.HTTP_200_OK)

#OtherOverview
class OthersOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            if not year:
                year = self.get_latest_available_year(user)

            try:
                year = int(year)
            except ValueError:
                return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

            start_date, end_date = self.get_fiscal_year_range(year)

            filters = {
                'user': user,
                'DatePicker__range': (start_date.date(), end_date.date())
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__location__icontains'] = facility_location

            waste_data = Waste.objects.filter(**filters)
            if not waste_data.exists():
                return self.get_empty_response(year)

            monthly_other_waste = (
                waste_data
                .values('DatePicker__month')
                .annotate(total_other_waste=Sum('other_waste'))
            )

            other_waste = {month: 0 for month in range(1, 13)}
            for entry in monthly_other_waste:
                other_waste[entry['DatePicker__month']] = entry['total_other_waste']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            line_chart_data = [
                {
                    "month": datetime(1900, month, 1).strftime('%b'),
                    "other_waste": other_waste[month]
                }
                for month in month_order
            ]

            # Prepare facility data for donut chart
            facility_other_waste = (
                waste_data
                .values('facility__facility_name')
                .annotate(total_other_waste=Sum('other_waste'))
                .order_by('-total_other_waste')
            )

            total_other_waste = sum(entry['total_other_waste'] for entry in facility_other_waste)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_other_waste'] / total_other_waste * 100) if total_other_waste else 0,
                }
                for entry in facility_other_waste
            ]

            response_data = {
                "year": year,
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            print(f"Error: {str(e)}")
            print("Traceback:", traceback.format_exc())
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_latest_available_year(self, user):
        latest_waste = Waste.objects.filter(user=user).order_by('-DatePicker').first()
        if latest_waste:
            return latest_waste.DatePicker.year
        return datetime.now().year 

    def get_fiscal_year_range(self, year):
        start_date = datetime(year, 4, 1)
        end_date = datetime(year + 1, 3, 31)
        return start_date, end_date

    def get_empty_response(self, year):
        month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
        line_chart_data = [{"month": datetime(1900, month, 1).strftime('%b'), "food_waste": 0} for month in month_order]
        donut_chart_data = [{"facility_name": "No Facility", "percentage": 0}]
        return Response({
            "year": year,
            "line_chart_data": line_chart_data,
            "donut_chart_data": donut_chart_data
        }, status=status.HTTP_200_OK)

#Sent for RecycleOverview
class Waste_Sent_For_RecycleOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            if not year:
                year = self.get_latest_available_year(user)

            try:
                year = int(year)
            except ValueError:
                return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

            start_date, end_date = self.get_fiscal_year_range(year)

            filters = {
                'user': user,
                'DatePicker__range': (start_date.date(), end_date.date())
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__location__icontains'] = facility_location

            waste_data = Waste.objects.filter(**filters)
            if not waste_data.exists():
                return self.get_empty_response(year)

            monthly_Recycle_waste = (
                waste_data
                .values('DatePicker__month')
                .annotate(total_Recycle_waste=Sum('Recycle_waste'))
            )

            Recycle_waste = {month: 0 for month in range(1, 13)}
            for entry in monthly_Recycle_waste:
                Recycle_waste[entry['DatePicker__month']] = entry['total_Recycle_waste']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            line_chart_data = [
                {
                    "month": datetime(1900, month, 1).strftime('%b'),
                    "Recycle_waste": Recycle_waste[month]
                }
                for month in month_order
            ]

            # Prepare facility data for donut chart
            facility_Recycle_waste = (
                waste_data
                .values('facility__facility_name')
                .annotate(total_Recycle_waste=Sum('Recycle_waste'))
                .order_by('-total_Recycle_waste')
            )

            total_Recycle_waste = sum(entry['total_Recycle_waste'] for entry in facility_Recycle_waste)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_Recycle_waste'] / total_Recycle_waste * 100) if total_Recycle_waste else 0,
                }
                for entry in facility_Recycle_waste
            ]

            response_data = {
                "year": year,
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            print(f"Error: {str(e)}")
            print("Traceback:", traceback.format_exc())
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_latest_available_year(self, user):
        latest_waste = Waste.objects.filter(user=user).order_by('-DatePicker').first()
        if latest_waste:
            return latest_waste.DatePicker.year
        return datetime.now().year 

    def get_fiscal_year_range(self, year):
        start_date = datetime(year, 4, 1)
        end_date = datetime(year + 1, 3, 31)
        return start_date, end_date

    def get_empty_response(self, year):
        month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
        line_chart_data = [{"month": datetime(1900, month, 1).strftime('%b'), "food_waste": 0} for month in month_order]
        donut_chart_data = [{"facility_name": "No Facility", "percentage": 0}]
        return Response({
            "year": year,
            "line_chart_data": line_chart_data,
            "donut_chart_data": donut_chart_data
        }, status=status.HTTP_200_OK)

#Sent For LandFill Overview
class Waste_Sent_For_LandFillOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            if not year:
                year = self.get_latest_available_year(user)

            try:
                year = int(year)
            except ValueError:
                return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

            start_date, end_date = self.get_fiscal_year_range(year)

            filters = {
                'user': user,
                'DatePicker__range': (start_date.date(), end_date.date())
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__location__icontains'] = facility_location

            waste_data = Waste.objects.filter(**filters)
            if not waste_data.exists():
                return self.get_empty_response(year)

            monthly_Landfill_waste = (
                waste_data
                .values('DatePicker__month')
                .annotate(total_Landfill_waste=Sum('Landfill_waste'))
            )

            Landfill_waste = {month: 0 for month in range(1, 13)}
            for entry in monthly_Landfill_waste:
                Landfill_waste[entry['DatePicker__month']] = entry['total_Landfill_waste']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            line_chart_data = [
                {
                    "month": datetime(1900, month, 1).strftime('%b'),
                    "Landfill_waste": Landfill_waste[month]
                }
                for month in month_order
            ]

            # Prepare facility data for donut chart
            facility_Landfill_waste = (
                waste_data
                .values('facility__facility_name')
                .annotate(total_Landfill_waste=Sum('Landfill_waste'))
                .order_by('-total_Landfill_waste')
            )

            total_Landfill_waste = sum(entry['total_Landfill_waste'] for entry in facility_Landfill_waste)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_Landfill_waste'] / total_Landfill_waste * 100) if total_Landfill_waste else 0,
                }
                for entry in facility_Landfill_waste
            ]

            response_data = {
                "year": year,
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            print(f"Error: {str(e)}")
            print("Traceback:", traceback.format_exc())
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_latest_available_year(self, user):
        latest_waste = Waste.objects.filter(user=user).order_by('-DatePicker').first()
        if latest_waste:
            return latest_waste.DatePicker.year
        return datetime.now().year 

    def get_fiscal_year_range(self, year):
        start_date = datetime(year, 4, 1)
        end_date = datetime(year + 1, 3, 31)
        return start_date, end_date

    def get_empty_response(self, year):
        month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
        line_chart_data = [{"month": datetime(1900, month, 1).strftime('%b'), "food_waste": 0} for month in month_order]
        donut_chart_data = [{"facility_name": "No Facility", "percentage": 0}]
        return Response({
            "year": year,
            "line_chart_data": line_chart_data,
            "donut_chart_data": donut_chart_data
        }, status=status.HTTP_200_OK)

#Stacked Graphs Overview
class StackedWasteOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            filters = {'user': user}

            # Determine the latest available year if no year is specified
            if not year:
                latest_waste = Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))
                if latest_waste['latest_date']:
                    latest_date = latest_waste['latest_date']
                    year = latest_date.year
                else:
                    year = datetime.now().year  # Default to the current year if no data exists

            year = int(year)  # Ensure year is an integer
            today = datetime.now()

            # Determine fiscal year range
            if today.month >= 4:
                start_date = datetime(year, 4, 1)
                end_date = datetime(year + 1, 3, 31)
            else:
                start_date = datetime(year - 1, 4, 1)
                end_date = datetime(year, 3, 31)
            filters['DatePicker__range'] = (start_date, end_date)

            # Facility filters if specified
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location and facility_location.lower() != 'all':
                filters['facility__facility_location__icontains'] = facility_location

            waste_types = [
                'food_waste', 'solid_Waste', 'E_Waste', 'Biomedical_waste',
                'liquid_discharge', 'Recycle_waste', 'Landfill_waste', 'other_waste'
            ]

            # Initialize monthly data dictionary
            monthly_data = {month: {waste_type: 0 for waste_type in waste_types} for month in range(1, 13)}

            # Fetch and aggregate monthly data
            for waste_type in waste_types:
                queryset = Waste.objects.filter(**filters)

                # Aggregate monthly data with explicit output_field for each waste type
                monthly_waste = (
                    queryset
                    .values('DatePicker__month')
                    .annotate(total=Coalesce(Sum(waste_type, output_field=FloatField()), Value(0, output_field=FloatField())))
                    .order_by('DatePicker__month')
                )

                for entry in monthly_waste:
                    month = entry['DatePicker__month']
                    monthly_data[month][waste_type] = entry['total']

            # Prepare response data in fiscal month order (April to March)
            stacked_bar_data = []
            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            for month in month_order:
                month_name = datetime(1900, month, 1).strftime('%b')
                stacked_bar_data.append({
                    "month": month_name,
                    **monthly_data[month]
                })

            response_data = {
                "facility_id": facility_id,
                "year": year,
                "facility_location": facility_location,
                "stacked_bar_data": stacked_bar_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error occurred: {e}") 
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#WasteOverview Donut chart
class WasteOverallDonutChartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        year = request.GET.get('year', None)  # Get the 'year' query parameter
        facility_id = request.GET.get('facility_id', 'all')
        facility_location = request.GET.get('facility_location', None)

        try:
            # Initialize filters with the user-specific data
            filters = {'user': user}

            # Get today's date for fiscal year calculation
            today = datetime.now()

            # Determine the latest available year based on the data in the database
            if not year:
                latest_waste = Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))
                if latest_waste['latest_date']:
                    latest_date = latest_waste['latest_date']
                    year = latest_date.year  # Use the year from the latest available date
                else:
                    year = today.year  # Default to current year if no data exists
            else:
                try:
                    year = int(year)  # Ensure the 'year' is an integer
                except ValueError:
                    return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

            # Fiscal year calculation based on the month
            if today.month >= 4:  # If today is after March, use the current year for the fiscal year
                start_date = datetime(year, 4, 1)
                end_date = datetime(year + 1, 3, 31)
            else:  # If before April, use the previous year for the fiscal year
                start_date = datetime(year - 1, 4, 1)
                end_date = datetime(year, 3, 31)

            # Apply the fiscal year range filter
            filters['DatePicker__range'] = (start_date, end_date)

            # Facility ID filtering
            if facility_id and facility_id.lower() != 'all':
                try:
                    Facility.objects.get(facility_id=facility_id)  # Check if the facility exists
                    filters['facility__facility_id'] = facility_id
                except Facility.DoesNotExist:
                    return Response({'error': f'Facility with ID {facility_id} does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

            # Facility location filtering
            if facility_location and facility_location.lower() != 'all':
                if not Facility.objects.filter(facility_location__icontains=facility_location).exists():
                    return Response({'error': f'No facility found with location {facility_location}.'}, status=status.HTTP_400_BAD_REQUEST)
                filters['facility__facility_location__icontains'] = facility_location

            # Query the Waste model with the filters applied
            queryset = Waste.objects.filter(**filters)

            if not queryset.exists():  # If no data is found, return zero values for all waste types
                waste_totals = {
                    'food_waste_total': 0.0,
                    'solid_Waste_total': 0.0,
                    'E_Waste_total': 0.0,
                    'Biomedical_waste_total': 0.0,
                    'other_waste_total': 0.0
                }
            else:
                # Aggregate waste totals for each waste type if data is found
                waste_totals = queryset.aggregate(
                    food_waste_total=Coalesce(Sum(Cast('food_waste', FloatField())), 0.0),
                    solid_Waste_total=Coalesce(Sum(Cast('solid_Waste', FloatField())), 0.0),
                    E_Waste_total=Coalesce(Sum(Cast('E_Waste', FloatField())), 0.0),
                    Biomedical_waste_total=Coalesce(Sum(Cast('Biomedical_waste', FloatField())), 0.0),
                    other_waste_total=Coalesce(Sum(Cast('other_waste', FloatField())), 0.0)
                )

            # Calculate the overall total waste
            overall_total = sum(waste_totals.values())

            # Calculate percentages for each waste type
            waste_percentages = {}
            for waste_type, total in waste_totals.items():
                waste_percentages[waste_type] = (total / overall_total) * 100 if overall_total else 0

            # Format the response data
            response_data = {
                "year": year,
                "facility_id": facility_id,
                "facility_location": facility_location,
                "waste_percentages": waste_percentages
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Log the error for debugging purposes
            print(f"Error occurred: {e}")
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#SenT to Landfill Overview Piechart
class SentToLandfillOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # Get parameters from the request
        year = request.GET.get('year', None)
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        
        # Default to the current year if 'year' is not provided
        if not year:
            # Get the latest available year based on the waste data in the database
            latest_waste = Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))
            if latest_waste['latest_date']:
                latest_date = latest_waste['latest_date']
                year = latest_date.year  # Use the year from the latest available date
            else:
                year = timezone.now().year  # Default to current year if no data exists
        else:
            try:
                year = int(year)  # Ensure the 'year' parameter is a valid integer
            except ValueError:
                return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Initialize the filters with the user and year
        filters = {'user': user, 'DatePicker__year': year}
        
        try:
            # Define the list of waste fields to calculate the overall total
            overall_total_fields = [
                'food_waste', 'solid_Waste', 'E_Waste', 'Biomedical_waste', 'other_waste'
            ]

            # Start with the base queryset filtered by user and year
            queryset = Waste.objects.filter(**filters)

            # Apply facility_id filter if provided (and not 'all')
            if facility_id and facility_id.lower() != 'all':
                queryset = queryset.filter(facility__facility_id=facility_id)
            
            # Apply facility_location filter if provided (and not 'all')
            if facility_location and facility_location.lower() != 'all':
                queryset = queryset.filter(facility__facility_location__icontains=facility_location)

            # Calculate the total 'Landfill_waste'
            Landfill_waste_total = queryset.aggregate(
                total=Coalesce(Sum(Cast('Landfill_waste', FloatField())), 0.0)
            )['total']

            # Calculate the overall total waste (sum of food_waste, solid_Waste, etc.)
            overall_total = sum(
                queryset.aggregate(
                    **{f"{waste_type}_total": Coalesce(Sum(Cast(waste_type, FloatField())), 0.0)
                       for waste_type in overall_total_fields}
                ).values()
            )

            # Calculate the remaining waste (excluding Landfill waste)
            remaining_waste_total = overall_total - Landfill_waste_total

            # Calculate the landfill and remaining waste percentages
            landfill_percentage = (Landfill_waste_total / overall_total) * 100 if overall_total else 0
            remaining_percentage = (remaining_waste_total / overall_total) * 100 if overall_total else 0

            # Prepare the response data
            response_data = {
                "landfill_percentage": landfill_percentage,
                "remaining_percentage": remaining_percentage
            }

            return Response(
                {
                    "year":year,
                    "sentToLandFill":response_data
                },
                status=status.HTTP_200_OK
                )

        except Exception as e:
            print(f"Error occurred: {e}")
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Sent to Recycle Overview Piechart
class SentToRecycledOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # Get parameters from the request
        year = request.GET.get('year', None)
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        
        # Default to the current year if 'year' is not provided
        if not year:
            # Get the latest available year based on the waste data in the database
            latest_waste = Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))
            if latest_waste['latest_date']:
                latest_date = latest_waste['latest_date']
                year = latest_date.year  # Use the year from the latest available date
            else:
                year = timezone.now().year  # Default to current year if no data exists
        else:
            try:
                year = int(year)  # Ensure the 'year' parameter is a valid integer
            except ValueError:
                return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Initialize the filters with the user and year
        filters = {'user': user, 'DatePicker__year': year}
        
        try:
            # Define the list of waste fields to calculate the overall total
            overall_total_fields = [
                'food_waste', 'solid_Waste', 'E_Waste', 'Biomedical_waste', 'other_waste'
            ]

            # Start with the base queryset filtered by user and year
            queryset = Waste.objects.filter(**filters)

            # Apply facility_id filter if provided (and not 'all')
            if facility_id and facility_id.lower() != 'all':
                queryset = queryset.filter(facility__facility_id=facility_id)
            
            # Apply facility_location filter if provided (and not 'all')
            if facility_location and facility_location.lower() != 'all':
                queryset = queryset.filter(facility__facility_location__icontains=facility_location)

            # Calculate the total 'Landfill_waste'
            Recycle_waste_total = queryset.aggregate(
                total=Coalesce(Sum(Cast('Recycle_waste', FloatField())), 0.0)
            )['total']

            # Calculate the overall total waste (sum of food_waste, solid_Waste, etc.)
            overall_total = sum(
                queryset.aggregate(
                    **{f"{waste_type}_total": Coalesce(Sum(Cast(waste_type, FloatField())), 0.0)
                       for waste_type in overall_total_fields}
                ).values()
            )

            # Calculate the remaining waste (excluding Recycle waste)
            remaining_waste_total = overall_total - Recycle_waste_total

            # Calculate the Recycle and remaining waste percentages
            Recycle_percentage = (Recycle_waste_total / overall_total) * 100 if overall_total else 0
            remaining_percentage = (remaining_waste_total / overall_total) * 100 if overall_total else 0

            # Prepare the response data
            response_data = {
                "Recycle_percentage": Recycle_percentage,
                "remaining_percentage": remaining_percentage
            }

            return Response(
                {
                    "year":year,
                    "SentToRecycle":response_data
                },
                status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error occurred: {e}")
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

'''Waste Overviewgraphs and Individual Line charts and donut charts Ends'''


'''Energy  Overview Cards ,Graphs and Individual line charts and donut charts Starts'''
#Energy Overview Cards
class EnergyViewCard_Over(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', 'all')
        facility_location = request.GET.get('facility_location')
        year = request.GET.get('year')

        try:
            # Validate facility_id
            if facility_id != 'all' and not Facility.objects.filter(facility_id=facility_id, user=user).exists():
                return Response({'error': 'Invalid facility ID or not associated with the logged-in user.'}, status=status.HTTP_400_BAD_REQUEST)

            # Validate year
            if year:
                try:
                    year = int(year)
                    if year < 1900 or year > datetime.now().year + 10:  # Allow future years up to 10 years ahead
                        return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)
                except ValueError:
                    return Response({'error': 'Year must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)

            # Determine start_date and end_date for the fiscal year
            if year:
                start_date = datetime(year, 4, 1)
                end_date = datetime(year + 1, 3, 31)
            else:
                latest_entry = Energy.objects.filter(user=user).order_by('-DatePicker').first()
                if latest_entry:
                    latest_year = latest_entry.DatePicker.year
                    year = latest_year if latest_entry.DatePicker.month >= 4 else latest_year - 1
                else:
                    today = datetime.now()
                    year = today.year - 1 if today.month < 4 else today.year

                start_date = datetime(year, 4, 1)
                end_date = datetime(year + 1, 3, 31)

            # Query energy data
            energy_data = Energy.objects.filter(user=user, DatePicker__range=(start_date, end_date))

            if facility_id != 'all':
                energy_data = energy_data.filter(facility__facility_id=facility_id)

            if facility_location:
                energy_data = energy_data.filter(facility__location__icontains=facility_location)

            energy_fields = [
                'hvac', 'production', 'stp', 'admin_block',
                'utilities', 'others', 'renewable_solar', 'renewable_other', 'coking_coal', 
                'coke_oven_coal', 'natural_gas', 'diesel', 'biomass_wood', 'biomass_other_solid'
            ]

            fuel_usage_fields = [
                'coke_oven_coal', 'coking_coal', 'natural_gas', 'diesel', 'biomass_wood', 'biomass_other_solid'
            ]

            renewable_energy_fields = ['renewable_solar', 'renewable_other']

            response_data = {
                'year': year,
                'overall_energy_totals': {}
            }

            if not energy_data.exists():
                # Populate zero values when no data exists
                response_data['overall_energy_totals']['overall_fuel_used_in_operations'] = 0
                response_data['overall_energy_totals']['overall_renewable_energy'] = 0
                for field in energy_fields:
                    response_data['overall_energy_totals'][f"overall_{field}"] = 0
            else:
                # Initialize counters for renewable energy and fuel usage totals
                fuel_used_in_operations_total = 0
                renewable_energy_total = 0

                for field in energy_fields:
                    # Aggregate total for each field
                    overall_total = energy_data.aggregate(total=Sum(field))['total'] or 0

                    # Add renewable energy (sum of renewable_solar and renewable_other)
                    if field in renewable_energy_fields:
                        renewable_energy_total += overall_total

                    # Add to fuel usage totals (sum of coke_oven_coal, coking_coal, natural_gas, diesel, biomass_wood, biomass_other_solid)
                    if field in fuel_usage_fields:
                        fuel_used_in_operations_total += overall_total

                    # Include other fields in the response if they have non-zero values
                    if overall_total > 0 and field not in renewable_energy_fields + fuel_usage_fields:
                        response_data['overall_energy_totals'][f"overall_{field}"] = overall_total

                # Set the calculated totals for renewable energy and fuel used in operations
                response_data['overall_energy_totals']['overall_fuel_used_in_operations'] = fuel_used_in_operations_total
                response_data['overall_energy_totals']['overall_renewable_energy'] = renewable_energy_total

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            print(error_message)
            return Response({'error': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#HVAC Line Charts and Donut Chart 
class HVACOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            if not year:
                year = self.get_latest_available_year(user)

            try:
                year = int(year)
            except ValueError:
                return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

            start_date, end_date = self.get_fiscal_year_range(year)

            filters = {
                'user': user,
                'DatePicker__range': (start_date.date(), end_date.date())
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__location__icontains'] = facility_location

            energy_data = Energy.objects.filter(**filters)
            if not energy_data.exists():
                return self.get_empty_response(year)

            monthly_hvac = (
                energy_data
                .values('DatePicker__month')
                .annotate(total_hvac=Sum('hvac'))
            )

            hvac = {month: 0 for month in range(1, 13)}
            for entry in monthly_hvac:
                hvac[entry['DatePicker__month']] = entry['total_hvac']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            line_chart_data = [
                {
                    "month": datetime(1900, month, 1).strftime('%b'),
                    "hvac": hvac[month]
                }
                for month in month_order
            ]

            # Prepare facility data for donut chart
            facility_hvac = (
                energy_data
                .values('facility__facility_name')
                .annotate(total_hvac=Sum('hvac'))
                .order_by('-total_hvac')
            )

            total_hvac = sum(entry['total_hvac'] for entry in facility_hvac)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_hvac'] / total_hvac * 100) if total_hvac else 0,
                }
                for entry in facility_hvac
            ]

            response_data = {
                "year": year,
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            print(f"Error: {str(e)}")
            print("Traceback:", traceback.format_exc())
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_latest_available_year(self, user):
        latest_energy = Energy.objects.filter(user=user).order_by('-DatePicker').first()
        if latest_energy:
            return latest_energy.DatePicker.year
        return datetime.now().year  # Default to current year if no data is available

    def get_fiscal_year_range(self, year):
        start_date = datetime(year, 4, 1)
        end_date = datetime(year + 1, 3, 31)
        return start_date, end_date

    def get_empty_response(self, year):
        month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
        line_chart_data = [{"month": datetime(1900, month, 1).strftime('%b'), "hvac": 0} for month in month_order]
        donut_chart_data = [{"facility_name": "No Facility", "percentage": 0}]
        return Response({
            "year": year,
            "line_chart_data": line_chart_data,
            "donut_chart_data": donut_chart_data
        }, status=status.HTTP_200_OK)

#ProductionLine Charts and Donut charts
class ProductionOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            if not year:
                year = self.get_latest_available_year(user)

            try:
                year = int(year)
            except ValueError:
                return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

            start_date, end_date = self.get_fiscal_year_range(year)

            filters = {
                'user': user,
                'DatePicker__range': (start_date.date(), end_date.date())
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__location__icontains'] = facility_location

            energy_data = Energy.objects.filter(**filters)
            if not energy_data.exists():
                return self.get_empty_response(year)

            monthly_production = (
                energy_data
                .values('DatePicker__month')
                .annotate(total_production=Sum('production'))
            )

            production = {month: 0 for month in range(1, 13)}
            for entry in monthly_production:
                production[entry['DatePicker__month']] = entry['total_production']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            line_chart_data = [
                {
                    "month": datetime(1900, month, 1).strftime('%b'),
                    "production": production[month]
                }
                for month in month_order
            ]

            # Prepare facility data for donut chart
            facility_production = (
                energy_data
                .values('facility__facility_name')
                .annotate(total_production=Sum('production'))
                .order_by('-total_production')
            )

            total_production = sum(entry['total_production'] for entry in facility_production)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_production'] / total_production * 100) if total_production else 0,
                }
                for entry in facility_production
            ]

            response_data = {
                "year": year,
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            print(f"Error: {str(e)}")
            print("Traceback:", traceback.format_exc())
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_latest_available_year(self, user):
        latest_energy = Energy.objects.filter(user=user).order_by('-DatePicker').first()
        if latest_energy:
            return latest_energy.DatePicker.year
        return datetime.now().year  # Default to current year if no data is available

    def get_fiscal_year_range(self, year):
        start_date = datetime(year, 4, 1)
        end_date = datetime(year + 1, 3, 31)
        return start_date, end_date

    def get_empty_response(self, year):
        month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
        line_chart_data = [{"month": datetime(1900, month, 1).strftime('%b'), "production": 0} for month in month_order]
        donut_chart_data = [{"facility_name": "No Facility", "percentage": 0}]
        return Response({
            "year": year,
            "line_chart_data": line_chart_data,
            "donut_chart_data": donut_chart_data
        }, status=status.HTTP_200_OK)

#STP Overview line charts and donut charts
class StpOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            if not year:
                year = self.get_latest_available_year(user)

            try:
                year = int(year)
            except ValueError:
                return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

            start_date, end_date = self.get_fiscal_year_range(year)

            filters = {
                'user': user,
                'DatePicker__range': (start_date.date(), end_date.date())
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__location__icontains'] = facility_location

            energy_data = Energy.objects.filter(**filters)
            if not energy_data.exists():
                return self.get_empty_response(year)

            monthly_stp = (
                energy_data
                .values('DatePicker__month')
                .annotate(total_stp=Sum('stp'))
            )

            stp = {month: 0 for month in range(1, 13)}
            for entry in monthly_stp:
                stp[entry['DatePicker__month']] = entry['total_stp']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            line_chart_data = [
                {
                    "month": datetime(1900, month, 1).strftime('%b'),
                    "stp": stp[month]
                }
                for month in month_order
            ]

            # Prepare facility data for donut chart
            facility_stp = (
                energy_data
                .values('facility__facility_name')
                .annotate(total_stp=Sum('stp'))
                .order_by('-total_stp')
            )

            total_stp = sum(entry['total_stp'] for entry in facility_stp)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_stp'] / total_stp * 100) if total_stp else 0,
                }
                for entry in facility_stp
            ]

            response_data = {
                "year": year,
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            print(f"Error: {str(e)}")
            print("Traceback:", traceback.format_exc())
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_latest_available_year(self, user):
        latest_energy = Energy.objects.filter(user=user).order_by('-DatePicker').first()
        if latest_energy:
            return latest_energy.DatePicker.year
        return datetime.now().year  # Default to current year if no data is available

    def get_fiscal_year_range(self, year):
        start_date = datetime(year, 4, 1)
        end_date = datetime(year + 1, 3, 31)
        return start_date, end_date

    def get_empty_response(self, year):
        month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
        line_chart_data = [{"month": datetime(1900, month, 1).strftime('%b'), "stp": 0} for month in month_order]
        donut_chart_data = [{"facility_name": "No Facility", "percentage": 0}]
        return Response({
            "year": year,
            "line_chart_data": line_chart_data,
            "donut_chart_data": donut_chart_data
        }, status=status.HTTP_200_OK)

#Admin_block Overview Linecharts and donut charts
class Admin_BlockOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            if not year:
                year = self.get_latest_available_year(user)

            try:
                year = int(year)
            except ValueError:
                return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

            start_date, end_date = self.get_fiscal_year_range(year)

            filters = {
                'user': user,
                'DatePicker__range': (start_date.date(), end_date.date())
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__location__icontains'] = facility_location

            energy_data = Energy.objects.filter(**filters)
            if not energy_data.exists():
                return self.get_empty_response(year)

            monthly_admin_block = (
                energy_data
                .values('DatePicker__month')
                .annotate(total_admin_block=Sum('admin_block'))
            )

            admin_block = {month: 0 for month in range(1, 13)}
            for entry in monthly_admin_block:
                admin_block[entry['DatePicker__month']] = entry['total_admin_block']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            line_chart_data = [
                {
                    "month": datetime(1900, month, 1).strftime('%b'),
                    "admin_block": admin_block[month]
                }
                for month in month_order
            ]

            # Prepare facility data for donut chart
            facility_admin_block = (
                energy_data
                .values('facility__facility_name')
                .annotate(total_admin_block=Sum('admin_block'))
                .order_by('-total_admin_block')
            )

            total_admin_block = sum(entry['total_admin_block'] for entry in facility_admin_block)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_admin_block'] / total_admin_block * 100) if total_admin_block else 0,
                }
                for entry in facility_admin_block
            ]

            response_data = {
                "year": year,
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            print(f"Error: {str(e)}")
            print("Traceback:", traceback.format_exc())
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_latest_available_year(self, user):
        latest_energy = Energy.objects.filter(user=user).order_by('-DatePicker').first()
        if latest_energy:
            return latest_energy.DatePicker.year
        return datetime.now().year  # Default to current year if no data is available

    def get_fiscal_year_range(self, year):
        start_date = datetime(year, 4, 1)
        end_date = datetime(year + 1, 3, 31)
        return start_date, end_date

    def get_empty_response(self, year):
        month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
        line_chart_data = [{"month": datetime(1900, month, 1).strftime('%b'), "admin_block": 0} for month in month_order]
        donut_chart_data = [{"facility_name": "No Facility", "percentage": 0}]
        return Response({
            "year": year,
            "line_chart_data": line_chart_data,
            "donut_chart_data": donut_chart_data
        }, status=status.HTTP_200_OK)

#Utilities_OverView Linecharts and Donut Charts
class Utilities_OverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            if not year:
                year = self.get_latest_available_year(user)

            try:
                year = int(year)
            except ValueError:
                return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

            start_date, end_date = self.get_fiscal_year_range(year)

            filters = {
                'user': user,
                'DatePicker__range': (start_date.date(), end_date.date())
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__location__icontains'] = facility_location

            energy_data = Energy.objects.filter(**filters)
            if not energy_data.exists():
                return self.get_empty_response(year)

            monthly_utilities = (
                energy_data
                .values('DatePicker__month')
                .annotate(total_utilities=Sum('utilities'))
            )

            utilities = {month: 0 for month in range(1, 13)}
            for entry in monthly_utilities:
                utilities[entry['DatePicker__month']] = entry['total_utilities']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            line_chart_data = [
                {
                    "month": datetime(1900, month, 1).strftime('%b'),
                    "utilities": utilities[month]
                }
                for month in month_order
            ]

            # Prepare facility data for donut chart
            facility_utilities = (
                energy_data
                .values('facility__facility_name')
                .annotate(total_utilities=Sum('utilities'))
                .order_by('-total_utilities')
            )

            total_utilities = sum(entry['total_utilities'] for entry in facility_utilities)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_utilities'] / total_utilities * 100) if total_utilities else 0,
                }
                for entry in facility_utilities
            ]

            response_data = {
                "year": year,
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            print(f"Error: {str(e)}")
            print("Traceback:", traceback.format_exc())
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_latest_available_year(self, user):
        latest_energy = Energy.objects.filter(user=user).order_by('-DatePicker').first()
        if latest_energy:
            return latest_energy.DatePicker.year
        return datetime.now().year  # Default to current year if no data is available

    def get_fiscal_year_range(self, year):
        start_date = datetime(year, 4, 1)
        end_date = datetime(year + 1, 3, 31)
        return start_date, end_date

    def get_empty_response(self, year):
        month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
        line_chart_data = [{"month": datetime(1900, month, 1).strftime('%b'), "utilities": 0} for month in month_order]
        donut_chart_data = [{"facility_name": "No Facility", "percentage": 0}]
        return Response({
            "year": year,
            "line_chart_data": line_chart_data,
            "donut_chart_data": donut_chart_data
        }, status=status.HTTP_200_OK)


# Others Overview Linecharts andDonut charts
class Others_OverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            if not year:
                year = self.get_latest_available_year(user)

            try:
                year = int(year)
            except ValueError:
                return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

            start_date, end_date = self.get_fiscal_year_range(year)

            filters = {
                'user': user,
                'DatePicker__range': (start_date.date(), end_date.date())
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__location__icontains'] = facility_location

            energy_data = Energy.objects.filter(**filters)
            if not energy_data.exists():
                return self.get_empty_response(year)

            monthly_others = (
                energy_data
                .values('DatePicker__month')
                .annotate(total_others=Sum('others'))
            )

            others = {month: 0 for month in range(1, 13)}
            for entry in monthly_others:
                others[entry['DatePicker__month']] = entry['total_others']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            line_chart_data = [
                {
                    "month": datetime(1900, month, 1).strftime('%b'),
                    "others": others[month]
                }
                for month in month_order
            ]

            # Prepare facility data for donut chart
            facility_others = (
                energy_data
                .values('facility__facility_name')
                .annotate(total_others=Sum('others'))
                .order_by('-total_others')
            )

            total_others = sum(entry['total_others'] for entry in facility_others)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_others'] / total_others * 100) if total_others else 0,
                }
                for entry in facility_others
            ]

            response_data = {
                "year": year,
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            print(f"Error: {str(e)}")
            print("Traceback:", traceback.format_exc())
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_latest_available_year(self, user):
        latest_energy = Energy.objects.filter(user=user).order_by('-DatePicker').first()
        if latest_energy:
            return latest_energy.DatePicker.year
        return datetime.now().year  # Default to current year if no data is available

    def get_fiscal_year_range(self, year):
        start_date = datetime(year, 4, 1)
        end_date = datetime(year + 1, 3, 31)
        return start_date, end_date

    def get_empty_response(self, year):
        month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
        line_chart_data = [{"month": datetime(1900, month, 1).strftime('%b'), "others": 0} for month in month_order]
        donut_chart_data = [{"facility_name": "No Facility", "percentage": 0}]
        return Response({
            "year": year,
            "line_chart_data": line_chart_data,
            "donut_chart_data": donut_chart_data
        }, status=status.HTTP_200_OK)


#Renewable_EnergyOverview Line Charts And Donut Charts
class Renewable_EnergyOverView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            filters = {'user': user}
            
            # If year is not provided, get the latest available year based on the Energy model
            if not year:
                latest_energy = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))
                if latest_energy['latest_date']:
                    latest_date = latest_energy['latest_date']
                    year = latest_date.year 
                else:
                    year = datetime.now().year
            else:
                try:
                    year = int(year)
                except ValueError:
                    return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

           
            if datetime.now().month >= 4: 
                start_date = datetime(year, 4, 1)
                end_date = datetime(year + 1, 3, 31)
            else:  # Last fiscal year
                start_date = datetime(year - 1, 4, 1)
                end_date = datetime(year, 3, 31)
            
            filters['DatePicker__range'] = (start_date, end_date)


            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__facility_location__icontains'] = facility_location

            monthly_renewable_energy = (
                Energy.objects.filter(**filters)
                .values('DatePicker__month')
                .annotate(total_renewable_energy=Sum('renewable_solar') + Sum('renewable_other'))
                .order_by('DatePicker__month')
            )

            line_chart_data = []
            renewable_energy = defaultdict(float)
            
            for entry in monthly_renewable_energy:
                renewable_energy[entry['DatePicker__month']] = entry['total_renewable_energy']

    
            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            today = datetime.now()

            for month in month_order:
                month_name = datetime(1900, month, 1).strftime('%b')
    
                if (year == today.year and month <= today.month) or (year < today.year):
                    line_chart_data.append({
                        "month": month_name,
                        "renewable_energy": renewable_energy.get(month, 0)
                    })
                else:
                    line_chart_data.append({
                        "month": month_name,
                        "renewable_energy": 0
                    })

            facility_filters = {
                'user': user,
                'DatePicker__range': (start_date, end_date)
            }
            if facility_id and facility_id.lower() != 'all':
                facility_filters['facility__facility_id'] = facility_id
            facility_renewable_energy = (
                Energy.objects.filter(**facility_filters)
                .values('facility__facility_name')
                .annotate(total_renewable_energy=Sum('renewable_solar') + Sum('renewable_other'))
                .order_by('-total_renewable_energy')
            )

            # Prepare donut chart data
            total_renewable_energy = sum(entry['total_renewable_energy'] for entry in facility_renewable_energy)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_renewable_energy'] / total_renewable_energy * 100) if total_renewable_energy else 0,
                }
                for entry in facility_renewable_energy
            ]

            response_data = {
                "year":year,
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

#Fuel Used in Opeartions Line Chart and donut chart
class Fuel_Used_OperationsOverView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            filters = {'user': user}
            
            # If year is not provided, get the latest available year based on the Energy model
            if not year:
                latest_energy = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))
                if latest_energy['latest_date']:
                    latest_date = latest_energy['latest_date']
                    year = latest_date.year  # Use the year from the latest available date
                else:
                    year = datetime.now().year  # Default to the current year if no data exists
            else:
                try:
                    year = int(year)
                except ValueError:
                    return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

            # Define fiscal year range
            if datetime.now().month >= 4:  # Current fiscal year starts in April
                start_date = datetime(year, 4, 1)
                end_date = datetime(year + 1, 3, 31)
            else:  # Last fiscal year
                start_date = datetime(year - 1, 4, 1)
                end_date = datetime(year, 3, 31)
            
            filters['DatePicker__range'] = (start_date, end_date)

            # Apply facility filters if provided
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__facility_location__icontains'] = facility_location

            # Query monthly fuel used in operations data
            monthly_fuel_used_in_operations = (
                Energy.objects.filter(**filters)
                .values('DatePicker__month')
                .annotate(total_fuel_used_in_operations=Sum('coking_coal') + Sum('coke_oven_coal') + Sum('natural_gas') + Sum('diesel') + Sum('biomass_wood') + Sum('biomass_other_solid'))
                .order_by('DatePicker__month')
            )

            # Prepare line chart data with zero defaults
            line_chart_data = []
            fuel_used_in_operations = defaultdict(float)

            # Map retrieved data to months
            for entry in monthly_fuel_used_in_operations:
                fuel_used_in_operations[entry['DatePicker__month']] = entry['total_fuel_used_in_operations']

            # Define the month order (April to March)
            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            today = datetime.now()

            # for month in month_order:
            #     month_name = datetime(1900, month, 1).strftime('%b')
            #     # Include data up to the current month, set future months to zero
            #     if (year == today.year and month <= today.month) or (year < today.year):
            #         line_chart_data.append({
            #             "month": month_name,
            #             "fuel_used_in_operations": fuel_used_in_operations.get(month, 0)
            #         })
            #     else:
            #         line_chart_data.append({
            #             "month": month_name,
            #             "fuel_used_in_operations": 0
            #         })
            # Loop through each month from April to March
            for month in month_order:
                month_name = datetime(1900, month, 1).strftime('%b')

                if year == today.year and month > today.month:
                    fuel_used_in_operations[month] = 0  # No data yet for future months of the current year
                else:
                    
                    line_chart_data.append({
                    "month": month_name,
                    "fuel_used_in_operations": fuel_used_in_operations.get(month, 0)
                })


            # Facility-wise fuel used in operations query for donut chart data
            facility_filters = {
                'user': user,
                'DatePicker__range': (start_date, end_date)
            }
            if facility_id and facility_id.lower() != 'all':
                facility_filters['facility__facility_id'] = facility_id
            facility_fuel_used_in_operations = (
                Energy.objects.filter(**facility_filters)
                .values('facility__facility_name')
                .annotate(total_fuel_used_in_operations=Sum('coking_coal') + Sum('coke_oven_coal') + Sum('natural_gas') + Sum('diesel') + Sum('biomass_wood') + Sum('biomass_other_solid'))
                .order_by('-total_fuel_used_in_operations')
            )

            # Prepare donut chart data
            total_fuel_used_in_operations = sum(entry['total_fuel_used_in_operations'] for entry in facility_fuel_used_in_operations)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_fuel_used_in_operations'] / total_fuel_used_in_operations * 100) if total_fuel_used_in_operations else 0,
                }
                for entry in facility_fuel_used_in_operations
            ]

            response_data = {
                "year":year,
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

#StackedEnergyOverview 
class StackedEnergyOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            filters = {'user': user}

            if year:
                try:
                    year = int(year)
                except ValueError:
                    return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                latest_energy = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))
                if latest_energy['latest_date']:
                    year = latest_energy['latest_date'].year 
                else:
                    year = datetime.now().year

            today = datetime.now()
            if today.month >= 4: 
                start_date = datetime(year, 4, 1)
                end_date = datetime(year + 1, 3, 31)
            else: 
                start_date = datetime(year - 1, 4, 1)
                end_date = datetime(year, 3, 31)

            filters['DatePicker__range'] = (start_date, end_date)

          
            if facility_id and facility_id.lower() != 'all':
                try:
                    Facility.objects.get(facility_id=facility_id)
                    filters['facility__facility_id'] = facility_id
                except Facility.DoesNotExist:
                    return Response({'error': f'Facility with ID {facility_id} does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

           
            if facility_location and facility_location.lower() != 'all':
                if not Facility.objects.filter(facility_location__icontains=facility_location).exists():
                    return Response({'error': f'No facility found with location {facility_location}.'}, status=status.HTTP_400_BAD_REQUEST)
                filters['facility__facility_location__icontains'] = facility_location

            energy_types = [
                'hvac', 'production', 'stp', 'admin_block', 'utilities', 
                'others', 'renewable_energy'
            ]


            monthly_data = {month: {energy_type: 0 for energy_type in energy_types} for month in range(1, 13)}

            for energy_type in energy_types:
                queryset = Energy.objects.filter(**filters)

                if energy_type == 'renewable_energy':
                    monthly_energy = (
                        queryset
                        .values('DatePicker__month')
                        .annotate(
                            total=Coalesce(
                                Sum('renewable_solar') + Sum('renewable_other'),
                                Value(0, output_field=FloatField())
                            )
                        )
                        .order_by('DatePicker__month')
                    )
                else:
                    monthly_energy = (
                        queryset
                        .values('DatePicker__month')
                        .annotate(total=Coalesce(Sum(energy_type, output_field=FloatField()), Value(0, output_field=FloatField())))
                        .order_by('DatePicker__month')
                    )

                for entry in monthly_energy:
                    month = entry['DatePicker__month']
                    monthly_data[month][energy_type] = entry['total']

            
            stacked_bar_data = []
            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            for month in month_order:
                month_name = datetime(1900, month, 1).strftime('%b')
                stacked_bar_data.append({
                    "month": month_name,
                    **monthly_data[month] 
                })

            response_data = {
                "facility_id": facility_id,
                "year": year,
                "facility_location": facility_location,
                "stacked_bar_data": stacked_bar_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error occurred: {e}") 
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#EnergyAnalyticsView With Pie Chart And Donut CHart
class EnergyAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        year = request.GET.get('year', None)
        facility_id = request.GET.get('facility_id', 'all')
        facility_location = request.GET.get('facility_location', None)

        try:
            filters = {'user': user}

            today = datetime.now()
            
            if year:
                try:
                    year = int(year)
                except ValueError:
                    return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                latest_energy = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))
                if latest_energy['latest_date']:
                    year = latest_energy['latest_date'].year
                else:
                    year = today.year 
           
            if today.month >= 4:
                start_date = datetime(year, 4, 1)
                end_date = datetime(year + 1, 3, 31)
            else:
                start_date = datetime(year - 1, 4, 1)
                end_date = datetime(year, 3, 31)

            filters['DatePicker__range'] = (start_date, end_date)

            if facility_id.lower() != 'all':
                try:
                    Facility.objects.get(facility_id=facility_id)
                    filters['facility__facility_id'] = facility_id
                except Facility.DoesNotExist:
                    return Response({'error': f'Facility with ID {facility_id} does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

            if facility_location and facility_location.lower() != 'all':
                if not Facility.objects.filter(facility_location__icontains=facility_location).exists():
                    return Response({'error': f'No facility found with location {facility_location}.'}, status=status.HTTP_400_BAD_REQUEST)
                filters['facility__facility_location__icontains'] = facility_location

            energy_aggregate = Energy.objects.filter(**filters).aggregate(
                total_hvac=Coalesce(Sum('hvac', output_field=FloatField()), 0.0),
                total_production=Coalesce(Sum('production', output_field=FloatField()), 0.0),
                total_stp=Coalesce(Sum('stp', output_field=FloatField()), 0.0),
                total_admin_block=Coalesce(Sum('admin_block', output_field=FloatField()), 0.0),
                total_utilities=Coalesce(Sum('utilities', output_field=FloatField()), 0.0),
                total_others=Coalesce(Sum('others', output_field=FloatField()), 0.0),
                total_renewable_solar=Coalesce(Sum('renewable_solar', output_field=FloatField()), 0.0),
                total_renewable_other=Coalesce(Sum('renewable_other', output_field=FloatField()), 0.0)
            )

            if not energy_aggregate:
                energy_aggregate = {key: 0.0 for key in energy_aggregate}

            total_renewable_energy = energy_aggregate['total_renewable_solar'] + energy_aggregate['total_renewable_other']
            total_non_renewable_energy = (
                energy_aggregate['total_hvac'] +
                energy_aggregate['total_production'] +
                energy_aggregate['total_stp'] +
                energy_aggregate['total_admin_block'] +
                energy_aggregate['total_utilities'] +
                energy_aggregate['total_others']
            )
            total_energy = total_non_renewable_energy + total_renewable_energy

            renewable_energy_percentage = (total_renewable_energy / total_energy * 100) if total_energy > 0 else 0
            remaining_energy_percentage = (total_non_renewable_energy / total_energy * 100) if total_energy > 0 else 0
            pie_chart_data = [
                {"label": "Renewable Energy", "value": renewable_energy_percentage},
                {"label": "Remaining Energy", "value": remaining_energy_percentage}
            ]

            energy_percentages = {}
            overall_total = total_non_renewable_energy
            for key, total in {
                "hvac_total": energy_aggregate['total_hvac'],
                "production_total": energy_aggregate['total_production'],
                "stp_total": energy_aggregate['total_stp'],
                "admin_block_total": energy_aggregate['total_admin_block'],
                "utilities_total": energy_aggregate['total_utilities'],
                "others_total": energy_aggregate['total_others']
            }.items():
                energy_percentages[key] = (total / overall_total * 100) if overall_total else 0

            # Final response data combining pie and donut chart information
            response_data = {
                "facility_id": facility_id,
                "year": year,
                "facility_location": facility_location,
                "pie_chart_data": pie_chart_data,
                "energy_percentages": energy_percentages
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error occurred: {e}")
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

'''Energy  Overview Cards ,Graphs and Individual line charts and donut charts Ends'''

'''Water Overview Cards ,Graphs and Individual Line Charts and donut Charts Starts'''
#Water Card OverView
class WaterViewCard_Over(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', 'all')
        facility_location = request.GET.get('facility_location')
        year = request.GET.get('year')

        try:
            # Validate facility ID
            if facility_id != 'all' and not Facility.objects.filter(facility_id=facility_id, user=user).exists():
                return Response({'error': 'Invalid facility ID or not associated with the logged-in user.'}, status=status.HTTP_400_BAD_REQUEST)

            # Validate year parameter
            if year:
                try:
                    year = int(year)
                    if year < 1900 or year > datetime.now().year + 10:  # Allow future years up to 10 years ahead
                        return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)
                except ValueError:
                    return Response({'error': 'Year must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)

            # Determine fiscal year range
            if year:
                start_date = datetime(year, 4, 1)
                end_date = datetime(year + 1, 3, 31)
            else:
                latest_entry = Water.objects.filter(user=user).order_by('-DatePicker').first()
                if latest_entry:
                    latest_year = latest_entry.DatePicker.year
                    year = latest_year if latest_entry.DatePicker.month >= 4 else latest_year - 1
                else:
                    today = datetime.now()
                    year = today.year - 1 if today.month < 4 else today.year

                start_date = datetime(year, 4, 1)
                end_date = datetime(year + 1, 3, 31)

            # Query water data
            water_data = Water.objects.filter(user=user, DatePicker__range=(start_date, end_date))

            if facility_id != 'all':
                water_data = water_data.filter(facility__facility_id=facility_id)

            if facility_location:
                water_data = water_data.filter(facility__location__icontains=facility_location)

            # Water fields for aggregation
            water_fields = [
                'Generated_Water', 'Recycled_Water', 'Softener_usage', 'Boiler_usage', 'otherUsage'
            ]

            # Calculate overall totals
            overall_totals = {
                f"overall_{field}": water_data.aggregate(total=Sum(field))['total'] or 0 for field in water_fields
            }

            response_data = {
                'year': year,
                'overall_water_totals': overall_totals
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            print(error_message)
            return Response({'error': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#GeneratedWater Overview Line Charts and Donut Chart
class Generated_WaterOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            if not year:
                year = self.get_latest_available_year(user)

            try:
                year = int(year)
            except ValueError:
                return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

            start_date, end_date = self.get_fiscal_year_range(year)

            filters = {
                'user': user,
                'DatePicker__range': (start_date.date(), end_date.date())
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__location__icontains'] = facility_location

            water_data = Water.objects.filter(**filters)
            if not water_data.exists():
                return self.get_empty_response(year)

            monthly_Generated_Water = (
                water_data
                .values('DatePicker__month')
                .annotate(total_Generated_Water=Sum('Generated_Water'))
            )

            Generated_Water = {month: 0 for month in range(1, 13)}
            for entry in monthly_Generated_Water:
                Generated_Water[entry['DatePicker__month']] = entry['total_Generated_Water']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            line_chart_data = [
                {
                    "month": datetime(1900, month, 1).strftime('%b'),
                    "Generated_Water": Generated_Water[month]
                }
                for month in month_order
            ]

            # Prepare facility data for donut chart
            facility_Generated_Water = (
                water_data
                .values('facility__facility_name')
                .annotate(total_Generated_Water=Sum('Generated_Water'))
                .order_by('-total_Generated_Water')
            )

            total_Generated_Water = sum(entry['total_Generated_Water'] for entry in facility_Generated_Water)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_Generated_Water'] / total_Generated_Water * 100) if total_Generated_Water else 0,
                }
                for entry in facility_Generated_Water
            ]

            response_data = {
                "year": year,
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            print(f"Error: {str(e)}")
            print("Traceback:", traceback.format_exc())
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_latest_available_year(self, user):
        latest_water = Water.objects.filter(user=user).order_by('-DatePicker').first()
        if latest_water:
            return latest_water.DatePicker.year
        return datetime.now().year  # Default to current year if no data is available

    def get_fiscal_year_range(self, year):
        start_date = datetime(year, 4, 1)
        end_date = datetime(year + 1, 3, 31)
        return start_date, end_date

    def get_empty_response(self, year):
        month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
        line_chart_data = [{"month": datetime(1900, month, 1).strftime('%b'), "Generated_Water": 0} for month in month_order]
        donut_chart_data = [{"facility_name": "No Facility", "percentage": 0}]
        return Response({
            "year": year,
            "line_chart_data": line_chart_data,
            "donut_chart_data": donut_chart_data
        }, status=status.HTTP_200_OK)


#Recycle Water Overview line charts and Donut chart
class Recycle_WaterOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            if not year:
                year = self.get_latest_available_year(user)

            try:
                year = int(year)
            except ValueError:
                return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

            start_date, end_date = self.get_fiscal_year_range(year)

            filters = {
                'user': user,
                'DatePicker__range': (start_date.date(), end_date.date())
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__location__icontains'] = facility_location

            water_data = Water.objects.filter(**filters)
            if not water_data.exists():
                return self.get_empty_response(year)

            monthly_Recycled_Water = (
                water_data
                .values('DatePicker__month')
                .annotate(total_Recycled_Water=Sum('Recycled_Water'))
            )

            Recycled_Water = {month: 0 for month in range(1, 13)}
            for entry in monthly_Recycled_Water:
                Recycled_Water[entry['DatePicker__month']] = entry['total_Recycled_Water']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            line_chart_data = [
                {
                    "month": datetime(1900, month, 1).strftime('%b'),
                    "Recycled_Water": Recycled_Water[month]
                }
                for month in month_order
            ]

            # Prepare facility data for donut chart
            facility_Recycled_Water = (
                water_data
                .values('facility__facility_name')
                .annotate(total_Recycled_Water=Sum('Recycled_Water'))
                .order_by('-total_Recycled_Water')
            )

            total_Recycled_Water = sum(entry['total_Recycled_Water'] for entry in facility_Recycled_Water)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_Recycled_Water'] / total_Recycled_Water * 100) if total_Recycled_Water else 0,
                }
                for entry in facility_Recycled_Water
            ]

            response_data = {
                "year": year,
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            print(f"Error: {str(e)}")
            print("Traceback:", traceback.format_exc())
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_latest_available_year(self, user):
        latest_water = Water.objects.filter(user=user).order_by('-DatePicker').first()
        if latest_water:
            return latest_water.DatePicker.year
        return datetime.now().year  # Default to current year if no data is available

    def get_fiscal_year_range(self, year):
        start_date = datetime(year, 4, 1)
        end_date = datetime(year + 1, 3, 31)
        return start_date, end_date

    def get_empty_response(self, year):
        month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
        line_chart_data = [{"month": datetime(1900, month, 1).strftime('%b'), "Recycled_Water": 0} for month in month_order]
        donut_chart_data = [{"facility_name": "No Facility", "percentage": 0}]
        return Response({
            "year": year,
            "line_chart_data": line_chart_data,
            "donut_chart_data": donut_chart_data
        }, status=status.HTTP_200_OK)

#SoftenSoftener_usage overview line chart and donut chart
class Softener_usageOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            if not year:
                year = self.get_latest_available_year(user)

            try:
                year = int(year)
            except ValueError:
                return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

            start_date, end_date = self.get_fiscal_year_range(year)

            filters = {
                'user': user,
                'DatePicker__range': (start_date.date(), end_date.date())
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__location__icontains'] = facility_location

            water_data = Water.objects.filter(**filters)
            if not water_data.exists():
                return self.get_empty_response(year)

            monthly_Softener_usage = (
                water_data
                .values('DatePicker__month')
                .annotate(total_Softener_usage=Sum('Softener_usage'))
            )

            Softener_usage = {month: 0 for month in range(1, 13)}
            for entry in monthly_Softener_usage:
                Softener_usage[entry['DatePicker__month']] = entry['total_Softener_usage']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            line_chart_data = [
                {
                    "month": datetime(1900, month, 1).strftime('%b'),
                    "Softener_usage": Softener_usage[month]
                }
                for month in month_order
            ]

            # Prepare facility data for donut chart
            facility_Softener_usage = (
                water_data
                .values('facility__facility_name')
                .annotate(total_Softener_usage=Sum('Softener_usage'))
                .order_by('-total_Softener_usage')
            )

            total_Softener_usage = sum(entry['total_Softener_usage'] for entry in facility_Softener_usage)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_Softener_usage'] / total_Softener_usage * 100) if total_Softener_usage else 0,
                }
                for entry in facility_Softener_usage
            ]

            response_data = {
                "year": year,
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            print(f"Error: {str(e)}")
            print("Traceback:", traceback.format_exc())
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_latest_available_year(self, user):
        latest_water = Water.objects.filter(user=user).order_by('-DatePicker').first()
        if latest_water:
            return latest_water.DatePicker.year
        return datetime.now().year  # Default to current year if no data is available

    def get_fiscal_year_range(self, year):
        start_date = datetime(year, 4, 1)
        end_date = datetime(year + 1, 3, 31)
        return start_date, end_date

    def get_empty_response(self, year):
        month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
        line_chart_data = [{"month": datetime(1900, month, 1).strftime('%b'), "Softener_usage": 0} for month in month_order]
        donut_chart_data = [{"facility_name": "No Facility", "percentage": 0}]
        return Response({
            "year": year,
            "line_chart_data": line_chart_data,
            "donut_chart_data": donut_chart_data
        }, status=status.HTTP_200_OK)

#Boiler_usage Overview line chart and Donut Chart
class Boiler_usageOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            if not year:
                year = self.get_latest_available_year(user)

            try:
                year = int(year)
            except ValueError:
                return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

            start_date, end_date = self.get_fiscal_year_range(year)

            filters = {
                'user': user,
                'DatePicker__range': (start_date.date(), end_date.date())
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__location__icontains'] = facility_location

            water_data = Water.objects.filter(**filters)
            if not water_data.exists():
                return self.get_empty_response(year)

            monthly_Boiler_usage = (
                water_data
                .values('DatePicker__month')
                .annotate(total_Boiler_usage=Sum('Boiler_usage'))
            )

            Boiler_usage = {month: 0 for month in range(1, 13)}
            for entry in monthly_Boiler_usage:
                Boiler_usage[entry['DatePicker__month']] = entry['total_Boiler_usage']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            line_chart_data = [
                {
                    "month": datetime(1900, month, 1).strftime('%b'),
                    "Boiler_usage": Boiler_usage[month]
                }
                for month in month_order
            ]

            # Prepare facility data for donut chart
            facility_Boiler_usage = (
                water_data
                .values('facility__facility_name')
                .annotate(total_Boiler_usage=Sum('Boiler_usage'))
                .order_by('-total_Boiler_usage')
            )

            total_Boiler_usage = sum(entry['total_Boiler_usage'] for entry in facility_Boiler_usage)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_Boiler_usage'] / total_Boiler_usage * 100) if total_Boiler_usage else 0,
                }
                for entry in facility_Boiler_usage
            ]

            response_data = {
                "year": year,
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            print(f"Error: {str(e)}")
            print("Traceback:", traceback.format_exc())
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_latest_available_year(self, user):
        latest_water = Water.objects.filter(user=user).order_by('-DatePicker').first()
        if latest_water:
            return latest_water.DatePicker.year
        return datetime.now().year  # Default to current year if no data is available

    def get_fiscal_year_range(self, year):
        start_date = datetime(year, 4, 1)
        end_date = datetime(year + 1, 3, 31)
        return start_date, end_date

    def get_empty_response(self, year):
        month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
        line_chart_data = [{"month": datetime(1900, month, 1).strftime('%b'), "Boiler_usage": 0} for month in month_order]
        donut_chart_data = [{"facility_name": "No Facility", "percentage": 0}]
        return Response({
            "year": year,
            "line_chart_data": line_chart_data,
            "donut_chart_data": donut_chart_data
        }, status=status.HTTP_200_OK)

#otherUsage overview line chart and Donut chart
class otherUsage_OverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            if not year:
                year = self.get_latest_available_year(user)

            try:
                year = int(year)
            except ValueError:
                return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

            start_date, end_date = self.get_fiscal_year_range(year)

            filters = {
                'user': user,
                'DatePicker__range': (start_date.date(), end_date.date())
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__location__icontains'] = facility_location

            water_data = Water.objects.filter(**filters)
            if not water_data.exists():
                return self.get_empty_response(year)

            monthly_otherUsage = (
                water_data
                .values('DatePicker__month')
                .annotate(total_otherUsage=Sum('otherUsage'))
            )

            otherUsage = {month: 0 for month in range(1, 13)}
            for entry in monthly_otherUsage:
                otherUsage[entry['DatePicker__month']] = entry['total_otherUsage']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            line_chart_data = [
                {
                    "month": datetime(1900, month, 1).strftime('%b'),
                    "otherUsage": otherUsage[month]
                }
                for month in month_order
            ]

            # Prepare facility data for donut chart
            facility_otherUsage = (
                water_data
                .values('facility__facility_name')
                .annotate(total_otherUsage=Sum('otherUsage'))
                .order_by('-total_otherUsage')
            )

            total_otherUsage = sum(entry['total_otherUsage'] for entry in facility_otherUsage)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_otherUsage'] / total_otherUsage * 100) if total_otherUsage else 0,
                }
                for entry in facility_otherUsage
            ]

            response_data = {
                "year": year,
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            print(f"Error: {str(e)}")
            print("Traceback:", traceback.format_exc())
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_latest_available_year(self, user):
        latest_water = Water.objects.filter(user=user).order_by('-DatePicker').first()
        if latest_water:
            return latest_water.DatePicker.year
        return datetime.now().year  # Default to current year if no data is available

    def get_fiscal_year_range(self, year):
        start_date = datetime(year, 4, 1)
        end_date = datetime(year + 1, 3, 31)
        return start_date, end_date

    def get_empty_response(self, year):
        month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
        line_chart_data = [{"month": datetime(1900, month, 1).strftime('%b'), "otherUsage": 0} for month in month_order]
        donut_chart_data = [{"facility_name": "No Facility", "percentage": 0}]
        return Response({
            "year": year,
            "line_chart_data": line_chart_data,
            "donut_chart_data": donut_chart_data
        }, status=status.HTTP_200_OK)

#Stacked Graph Overview 
class StackedWaterOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            filters = {'user': user}

            if year:
                try:
                    year = int(year)
                except ValueError:
                    return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                latest_water = Water.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))
                if latest_water['latest_date']:
                    year = latest_water['latest_date'].year 
                else:
                    year = datetime.now().year

            today = datetime.now()
            if today.month >= 4: 
                start_date = datetime(year, 4, 1)
                end_date = datetime(year + 1, 3, 31)
            else: 
                start_date = datetime(year - 1, 4, 1)
                end_date = datetime(year, 3, 31)

            filters['DatePicker__range'] = (start_date, end_date)

          
            if facility_id and facility_id.lower() != 'all':
                try:
                    Facility.objects.get(facility_id=facility_id)
                    filters['facility__facility_id'] = facility_id
                except Facility.DoesNotExist:
                    return Response({'error': f'Facility with ID {facility_id} does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

           
            if facility_location and facility_location.lower() != 'all':
                if not Facility.objects.filter(facility_location__icontains=facility_location).exists():
                    return Response({'error': f'No facility found with location {facility_location}.'}, status=status.HTTP_400_BAD_REQUEST)
                filters['facility__facility_location__icontains'] = facility_location

            water_types = [
            'Generated_Water', 'Recycled_Water', 'Softener_usage', 'Boiler_usage', 'otherUsage'
            ]


            monthly_data = {month: {water_type: 0 for water_type in water_types} for month in range(1, 13)}

            for water_type in water_types:
                queryset = Water.objects.filter(**filters)

                if water_type == 'renewable_water':
                    monthly_water = (
                        queryset
                        .values('DatePicker__month')
                        .annotate(
                            total=Coalesce(
                                Sum('renewable_solar') + Sum('renewable_other'),
                                Value(0, output_field=FloatField())
                            )
                        )
                        .order_by('DatePicker__month')
                    )
                else:
                    monthly_water = (
                        queryset
                        .values('DatePicker__month')
                        .annotate(total=Coalesce(Sum(water_type, output_field=FloatField()), Value(0, output_field=FloatField())))
                        .order_by('DatePicker__month')
                    )

                for entry in monthly_water:
                    month = entry['DatePicker__month']
                    monthly_data[month][water_type] = entry['total']

            
            stacked_bar_data = []
            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            for month in month_order:
                month_name = datetime(1900, month, 1).strftime('%b')
                stacked_bar_data.append({
                    "month": month_name,
                    **monthly_data[month] 
                })

            response_data = {
                "facility_id": facility_id,
                "year": year,
                "facility_location": facility_location,
                "stacked_bar_data": stacked_bar_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error occurred: {e}") 
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#Water Anaytics Donut Chart And Line Graph
class WaterAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        year = request.GET.get('year', None)
        facility_id = request.GET.get('facility_id', 'all')
        facility_location = request.GET.get('facility_location', None)

        try:
            filters = {'user': user}
            today = datetime.now()

            # Year calculation
            if year:
                try:
                    year = int(year)
                except ValueError:
                    return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                latest_water = Water.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))
                year = latest_water['latest_date'].year if latest_water['latest_date'] else today.year

            # Fiscal year range
            start_date, end_date = (
                (datetime(year, 4, 1), datetime(year + 1, 3, 31))
                if today.month >= 4
                else (datetime(year - 1, 4, 1), datetime(year, 3, 31))
            )
            filters['DatePicker__range'] = (start_date, end_date)

            # Facility ID filtering
            if facility_id.lower() != 'all':
                if not Facility.objects.filter(facility_id=facility_id).exists():
                    return Response({'error': f'Facility with ID {facility_id} does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
                filters['facility__facility_id'] = facility_id

            # Facility location filtering
            if facility_location and facility_location.lower() != 'all':
                if not Facility.objects.filter(facility_location__icontains=facility_location).exists():
                    return Response({'error': f'No facility found with location {facility_location}.'}, status=status.HTTP_400_BAD_REQUEST)
                filters['facility__facility_location__icontains'] = facility_location

            # Query Water data
            queryset = Water.objects.filter(**filters)
            if not queryset.exists():
                return Response({
                    "year": year,
                    "facility_id": facility_id,
                    "facility_location": facility_location,
                    "donut_chart_data": {
                        "Softener_Usage": 0,
                        "Boiler_Usage": 0,
                        "Other_Usage": 0
                    },
                    "pie_chart_data": [
                        {"label": "Recycled Water", "value": 0},
                        {"label": "Remaining Water", "value": 0}
                    ]
                }, status=status.HTTP_200_OK)

            # Aggregations
            water_totals = queryset.aggregate(
                Softener_usage_total=Coalesce(Sum(Cast('Softener_usage', FloatField())), 0.0),
                Boiler_usage_total=Coalesce(Sum(Cast('Boiler_usage', FloatField())), 0.0),
                otherUsage_total=Coalesce(Sum(Cast('otherUsage', FloatField())), 0.0),
                Generated_Water_total=Coalesce(Sum(Cast('Generated_Water', FloatField())), 0.0),
                Recycled_Water_total=Coalesce(Sum(Cast('Recycled_Water', FloatField())), 0.0)
            )

            # Normalize donut chart percentages
            total_usage = (
                water_totals['Softener_usage_total'] +
                water_totals['Boiler_usage_total'] +
                water_totals['otherUsage_total']
            )
            water_percentages = {
                "Softener_Usage": (water_totals['Softener_usage_total'] / total_usage * 100) if total_usage else 0,
                "Boiler_Usage": (water_totals['Boiler_usage_total'] / total_usage * 100) if total_usage else 0,
                "Other_Usage": (water_totals['otherUsage_total'] / total_usage * 100) if total_usage else 0
            }

            # Pie chart data
            generated_recycled_total = (
                water_totals['Generated_Water_total'] +
                water_totals['Recycled_Water_total']
            )
            recycled_water = water_totals['Recycled_Water_total']
            remaining_water = generated_recycled_total - recycled_water
            pie_chart_data = [
                {"label": "Recycled Water", "value": (recycled_water / generated_recycled_total * 100) if generated_recycled_total else 0},
                {"label": "Remaining Water", "value": (remaining_water / generated_recycled_total * 100) if generated_recycled_total else 0}
            ]

            return Response({
                "year": year,
                "facility_id": facility_id,
                "facility_location": facility_location,
                "donut_chart_data": water_percentages,
                "pie_chart_data": pie_chart_data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logging.error(f"Error in WaterAnalyticsView: {e}")
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

'''Water Overview Cards ,Graphs and Individual Line Charts and donut Charts Ends'''

'''Biodiversity Overview Cards Starts'''
class BiodiversityMetricsGraphsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', 'all')

        try:
            # Filters for user and facility
            filters = {'user': user}
            if facility_id != 'all':
                filters['facility__facility_id'] = facility_id

            # Query all data for the user and facility
            all_years_data = Biodiversity.objects.filter(**filters)

            if not all_years_data.exists():
                return Response(
                    {
                        "facility_id": facility_id,
                        "year": None,
                        "current_year_metrics": {
                            "total_trees": 0,
                            "carbon_offset": 0,
                            "green_belt_density": 0,
                            "trees_per_capita": 0,
                            "new_trees_planted": 0,
                            "biomass": 0,
                            "co2_sequestration_rate": 0,
                        },
                        "yearly_metrics": [],
                        "chart_data": {
                            "Offset_year": [],
                            "Green_Belt_Density": [],
                            "Trees_Per_Capita": [],
                        },
                    },
                    status=status.HTTP_200_OK,
                )

            # Get the latest date if no year is specified
            latest_date = all_years_data.aggregate(latest_date=Max('DatePicker'))['latest_date']
            if not latest_date:
                return Response({'error': 'No data available in the database.'}, status=status.HTTP_404_NOT_FOUND)

            latest_year = latest_date.year
            year = request.GET.get('year', latest_year)

            try:
                year = int(year)
            except ValueError:
                return Response({'error': 'Invalid year provided.'}, status=status.HTTP_400_BAD_REQUEST)

            # Define fiscal year ranges for filtering
            start_date = datetime(year, 4, 1)
            end_date = datetime(year + 1, 3, 31)

            # Filter data for the current year
            current_year_data = all_years_data.filter(DatePicker__range=(start_date, end_date))

            # Aggregate yearly metrics
            yearly_data = {}
            for entry in all_years_data.values('DatePicker', 'width', 'height', 'no_trees', 'totalArea', 'head_count'):
                entry_year = entry['DatePicker'].year
                if entry_year not in yearly_data:
                    yearly_data[entry_year] = {'no_trees': 0, 'width': 0, 'height': 0, 'totalArea': 0, 'head_count': 0}
                yearly_data[entry_year]['no_trees'] += entry['no_trees'] or 0
                yearly_data[entry_year]['width'] += entry['width'] or 0
                yearly_data[entry_year]['height'] += entry['height'] or 0
                yearly_data[entry_year]['totalArea'] += entry['totalArea'] or 0
                yearly_data[entry_year]['head_count'] += entry['head_count'] or 0

            # Compute metrics for each year
            results = []
            for entry_year, data in yearly_data.items():
                total_trees = data['no_trees']
                carbon_offset = 0.00006 * (data['width'] ** 2) * data['height'] * total_trees
                green_belt_density = (total_trees / data['totalArea']) * 10000 if data['totalArea'] > 0 else 0
                trees_per_capita = total_trees / data['head_count'] if data['head_count'] > 0 else 0
                results.append({
                    'year': entry_year,
                    'carbon_offset': carbon_offset,
                    'green_belt_density': green_belt_density,
                    'trees_per_capita': trees_per_capita,
                })

            # Sort results by year
            results.sort(key=lambda x: x['year'])

            # Prepare chart data in the requested structure
            offset_year_data = []
            green_belt_density_data = []
            trees_per_capita_data = []

            for entry in results:
                offset_year_data.append({
                    'year': entry['year'],
                    'carbon_offset': entry['carbon_offset'],
                })

                green_belt_density_data.append({
                    'year': entry['year'],
                    'green_belt_density': entry['green_belt_density'],
                })

                trees_per_capita_data.append({
                    'year': entry['year'],
                    'trees_per_capita': entry['trees_per_capita'],
                })

            # Prepare metrics for the current year
            total_trees = green_belt_density = trees_per_capita = new_trees_planted = biomass = 0
            carbon_offset = co2_sequestration_rate = 0

            if current_year_data.exists():
                total_trees, green_belt_density, trees_per_capita, new_trees_planted = self.calculate_metrics(current_year_data)
                carbon_offset = self.calculate_co2(current_year_data)
                biomass = self.calculate_biomass(current_year_data)
                co2_sequestration_rate = self.calculate_co2_sequestration_rate(all_years_data, current_year_data)
            
            offset_year_data = [{"year": r['year'], "carbon_offset": r['carbon_offset']} for r in results]
            green_belt_density_data = [{"year": r['year'], "green_belt_density": r['green_belt_density']} for r in results]
            trees_per_capita_data = [{"year": r['year'], "trees_per_capita": r['trees_per_capita']} for r in results]
            # Response structure
            response_data = {
                "facility_id": facility_id,
                "year": year,
                "current_year_metrics": {
                    "total_trees": total_trees,
                    "carbon_offset": carbon_offset,
                    "green_belt_density": green_belt_density,
                    "trees_per_capita": trees_per_capita,
                    "new_trees_planted": new_trees_planted,
                    "biomass": biomass,
                    "co2_sequestration_rate": co2_sequestration_rate,
                },
                 "Offset_year": offset_year_data,
                "Green_Belt_Density": green_belt_density_data,
                "Trees_Per_Capita": trees_per_capita_data,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def calculate_co2(self, data):
        return sum(
            0.00006 *
            (entry['width'] or 0) ** 2 *
            (entry['height'] or 0) *
            (entry['no_trees'] or 0)
            for entry in data.values('width', 'height', 'no_trees')
        )

    def calculate_biomass(self, data):
        return sum(
            0.0998 *
            (entry['width'] or 0) ** 2 *
            (entry['height'] or 0)
            for entry in data.values('width', 'height')
        )

    def calculate_metrics(self, data):
        aggregated = data.aggregate(
            total_trees=Sum('no_trees'),
            total_area=Sum('totalArea'),
            head_count=Sum('head_count'),
            new_trees_planted=Sum('new_trees_planted')
        )
        total_trees = aggregated.get('total_trees', 0)
        total_area = aggregated.get('total_area', 0)
        head_count = aggregated.get('head_count', 0)
        new_trees_planted = aggregated.get('new_trees_planted', 0)

        green_belt_density = (total_trees / total_area) * 10000 if total_area > 0 else 0
        trees_per_capita = total_trees / head_count if head_count > 0 else 0

        return total_trees, green_belt_density, trees_per_capita, new_trees_planted

    def calculate_co2_sequestration_rate(self, all_years_data, current_year_data):
        # Get the current year from the current year's data
        current_year = current_year_data.first().DatePicker.year

        # Fetch data for the previous year
        prev_year_data = all_years_data.filter(DatePicker__year=current_year - 1)

        # Calculate CO2 sequestration rate
        current_year_co2 = self.calculate_co2(current_year_data)
        prev_year_co2 = self.calculate_co2(prev_year_data) if prev_year_data.exists() else 0

        # Return the difference, or current_year_co2 if there's no previous year data
        return current_year_co2 - prev_year_co2

'''Biodiversity Overview Cards Ends'''

'''LOgistics overview Graphs starts'''
class LogisticsOverviewAndGraphs(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', 'all')
        year = request.GET.get('year')

        try:
            # Determine the fiscal year if no year is specified
            if not year:
                latest_date = Logistics.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                year = latest_date.year if latest_date else datetime.now().year
            else:
                year = int(year)

            # Define fiscal year ranges
            start_date = datetime(year, 4, 1)
            end_date = datetime(year + 1, 3, 31)

            # Filters
            filters = {'user': user, 'DatePicker__range': (start_date, end_date)}
            if facility_id != 'all':
                filters['facility__facility_id'] = facility_id

            # Query data for the current year
            current_year_data = Logistics.objects.filter(**filters)

            # If no data exists, set all fields to 0
            if not current_year_data.exists():
                return Response({
                    "year": year,
                    "facility_id": facility_id,
                    "logistics_totals": {
                        "total_vehicles": 0,
                        "total_trips": 0,
                        "total_km_travelled": 0.0,
                        "total_fuel_consumed": 0.0
                    },
                    "line_chart_data": [
                        {"month": datetime(1900, month, 1).strftime('%b'), "Co2": 0.0}
                        for month in range(1, 13)
                    ],
                    "donut_chart_data": [{"facility_name": "No Facility", "percentage": 0}],
                    "logistics_fuel_comparison": {
                        "cargo": [
                            {"month": datetime(1900, month, 1).strftime('%b'), "cargo": 0.0}
                            for month in range(1, 13)
                        ],
                        "staff": [
                            {"month": datetime(1900, month, 1).strftime('%b'), "staff": 0.0}
                            for month in range(1, 13)
                        ]
                    }
                }, status=200)

            # Aggregating totals for the overview
            total_vehicles = current_year_data.aggregate(
                total_vehicles=Coalesce(Sum('No_Vehicles'), Value(0))
            )['total_vehicles']

            total_trips = current_year_data.aggregate(
                total_trips=Coalesce(Sum('No_Trips'), Value(0))
            )['total_trips']

            total_km_travelled = current_year_data.aggregate(
                total_km_travelled=Coalesce(Sum('km_travelled'), Value(0.0))
            )['total_km_travelled']

            total_fuel_consumed = current_year_data.aggregate(
                total_fuel_consumed=Coalesce(Sum('fuel_consumption'), Value(0.0))
            )['total_fuel_consumed']

            # Monthly Fuel Consumption
            monthly_data = current_year_data.annotate(month=ExtractMonth('DatePicker')).values('month').annotate(
                total_fuel=Coalesce(Sum('fuel_consumption', output_field=FloatField()), Value(0.0, output_field=FloatField()))
            )
            monthly_fuel = {d['month']: d['total_fuel'] for d in monthly_data}

            # Facility-wise Fuel Consumption
            facility_data = current_year_data.values('facility__facility_name').annotate(
                total_fuel=Coalesce(Sum('fuel_consumption', output_field=FloatField()), Value(0.0, output_field=FloatField()))
            )

            # Calculate percentages for the donut chart
            total_fuel = sum(d['total_fuel'] for d in facility_data) or 1  # Avoid division by zero
            donut_chart_data = [
                {"facility_name": d['facility__facility_name'], "percentage": round((d['total_fuel'] / total_fuel) * 100, 2)}
                for d in facility_data
            ]
            if not donut_chart_data:
                donut_chart_data = [{"facility_name": "No Facility", "percentage": 0}]

            # Logistics Types Fuel Consumption
            type_month_data = current_year_data.annotate(month=ExtractMonth('DatePicker')).values(
                'month', 'logistics_types'
            ).annotate(
                total_fuel=Coalesce(Sum('fuel_consumption', output_field=FloatField()), Value(0.0, output_field=FloatField()))
            )

            # Define the month order from April to March
            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]

            # Fill missing months with zeros for graphs
            all_months = range(1, 13)
            monthly_fuel = {month: monthly_fuel.get(month, 0.0) for month in all_months}
            cargo_data = {month: 0.0 for month in all_months}  # Initialize to 0 for each month
            staff_data = {month: 0.0 for month in all_months}  # Initialize to 0 for each month

            # Process logistics types data and update cargo and staff data
            for data in type_month_data:
                month = data['month']
                logistics_type = data['logistics_types']  # Ensure this matches the correct field names
                fuel_consumed = data['total_fuel']

                if logistics_type == 'Cargo':  # Ensure 'cargo' matches the correct string in the data
                    cargo_data[month] = fuel_consumed
                elif logistics_type == 'Staff':  # Ensure 'staff_logistics' matches the correct string in the data
                    staff_data[month] = fuel_consumed

            # Prepare the data for the line chart
            bar_chart_data = [
                {"month": datetime(1900, month, 1).strftime('%b'), "Fuel_Consumption": monthly_fuel[month]}
                for month in month_order
            ]

            # Prepare the data for comparing logistics types
            cargo_data_with_names = [
                {"month": datetime(1900, month, 1).strftime('%b'), "cargo": cargo_data[month]}
                for month in month_order
            ]
            staff_data_with_names = [
                {"month": datetime(1900, month, 1).strftime('%b'), "staff": staff_data[month]}
                for month in month_order
            ]

            # Structure the final response
            data = {
                "year": year,
                "facility_id": facility_id,
                "logistics_totals": {
                    "total_vehicles": total_vehicles,
                    "total_trips": total_trips,
                    "total_km_travelled": total_km_travelled,
                    "total_fuel_consumed": total_fuel_consumed
                },
                "bar_chart_data": bar_chart_data,  # Line Chart
                "donut_chart_data": donut_chart_data,  # Donut Chart
                "logistics_fuel_comparison": {  # Bar Graph (Fuel Consumption by Logistics Type)
                    "cargo": cargo_data_with_names,
                    "staff": staff_data_with_names
                }
            }

            return Response(data, status=200)

        except ValueError:
            return Response({"error": "Invalid year format."}, status=400)

        except Exception as e:
            return Response({"error": str(e)}, status=500)

'''LOgistics overview Graphs ends'''
'''Emissions Calculations starts'''
class EmissionCalculations(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        year = request.GET.get('year', None)
        facility_id = request.GET.get('facility_id', 'all')
        facility_location = request.GET.get('facility_location', None)

        try:
            filters = {'user': user}
            today = datetime.now()

            # Year calculation
            if year:
                try:
                    year = int(year)
                except ValueError:
                    return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                latest_energy_date = Energy.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_water_date = Water.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_waste_date = Waste.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_logistics_date = Logistics.objects.filter(user=user).aggregate(latest_date=Max('DatePicker'))['latest_date']
                latest_date = max(filter(None, [latest_energy_date, latest_water_date, latest_waste_date, latest_logistics_date]))
                year = latest_date.year if latest_date else today.year
                
            # Fiscal year range
            start_date, end_date = (
                (datetime(year, 4, 1), datetime(year + 1, 3, 31))
                if today.month >= 4
                else (datetime(year - 1, 4, 1), datetime(year, 3, 31))
            )
            filters['DatePicker__range'] = (start_date, end_date)

            # Facility ID filtering
            if facility_id.lower() != 'all':
                if not Facility.objects.filter(facility_id=facility_id).exists():
                    return Response({'error': f'Facility with ID {facility_id} does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
                filters['facility__facility_id'] = facility_id

            # Facility location filtering
            if facility_location and facility_location.lower() != 'all':
                if not Facility.objects.filter(facility_location__icontains=facility_location).exists():
                    return Response({'error': f'No facility found with location {facility_location}.'}, status=status.HTTP_400_BAD_REQUEST)
                filters['facility__facility_location__icontains'] = facility_location

            # Fetch energy and water data
            energy_data = Energy.objects.filter(**filters)
            water_data = Water.objects.filter(**filters)
            waste_data = Waste.objects.filter(**filters)
            logistics_data = Logistics.objects.filter(**filters)

            # Energy Emission factors
            electricity_factor = 0.82
            fuel_factors = {
                'coking_coal': 2.66,
                'coke_oven_coal': 3.1,
                'natural_gas': 2.7,
                'diesel': 2.91 * 1000,  # Diesel in liters, convert to kg
                'biomass_wood': 1.75,
                'biomass_other_solid': 1.16
            }
            petrol_factor = 2.29 * 1000
            diesel_factor = 2.91 * 1000

            # Monthly totals (ordered by fiscal year: April - March)
            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            monthly_total_emissions = {}

            for month in month_order:  # Loop over fiscal months
                # Filter data for the specific month
                monthly_energy = energy_data.filter(DatePicker__month=month)
                monthly_water = water_data.filter(DatePicker__month=month)
                monthly_waste = waste_data.filter(DatePicker__month=month)
                monthly_logistics = logistics_data.filter(DatePicker__month=month)

                # Calculate electricity emissions
                hvac_sum = monthly_energy.aggregate(total=Coalesce(Sum('hvac'), 0.0))['total']
                production_sum = monthly_energy.aggregate(total=Coalesce(Sum('production'), 0.0))['total']
                stp_sum = monthly_energy.aggregate(total=Coalesce(Sum('stp'), 0.0))['total']
                admin_block_sum = monthly_energy.aggregate(total=Coalesce(Sum('admin_block'), 0.0))['total']
                utilities_sum = monthly_energy.aggregate(total=Coalesce(Sum('utilities'), 0.0))['total']
                others_sum = monthly_energy.aggregate(total=Coalesce(Sum('others'), 0.0))['total']

                electricity_emissions = (
                    hvac_sum + production_sum + stp_sum + admin_block_sum + utilities_sum + others_sum
                ) * electricity_factor

                # Calculate fuel emissions
                fuel_emissions = sum([
                    monthly_energy.aggregate(total=Coalesce(Sum('coking_coal'), 0.0))['total'] * fuel_factors['coking_coal'],
                    monthly_energy.aggregate(total=Coalesce(Sum('coke_oven_coal'), 0.0))['total'] * fuel_factors['coke_oven_coal'],
                    monthly_energy.aggregate(total=Coalesce(Sum('natural_gas'), 0.0))['total'] * fuel_factors['natural_gas'],
                    monthly_energy.aggregate(total=Coalesce(Sum('diesel'), 0.0))['total'] * fuel_factors['diesel'],
                    monthly_energy.aggregate(total=Coalesce(Sum('biomass_wood'), 0.0))['total'] * fuel_factors['biomass_wood'],
                    monthly_energy.aggregate(total=Coalesce(Sum('biomass_other_solid'), 0.0))['total'] * fuel_factors['biomass_other_solid']
                ])
                total_energy_emissions = electricity_emissions + fuel_emissions

                # Calculate water usage Emissions
                total_water = monthly_water.aggregate(
                    total=Coalesce(Sum('Generated_Water'), 0.0)
                    + Coalesce(Sum('Recycled_Water'), 0.0)
                    + Coalesce(Sum('Softener_usage'), 0.0)
                    + Coalesce(Sum('Boiler_usage'), 0.0)
                    + Coalesce(Sum('otherUsage'), 0.0)
                )['total']
                
                total_water_emissions = total_water*0.46
                
                # Calculate waste emissions
                total_waste_emissions = sum([
                    monthly_waste.aggregate(total=Coalesce(Sum('Landfill_waste'), 0.0))['total'] * 300,
                    monthly_waste.aggregate(total=Coalesce(Sum('Recycle_waste'), 0.0))['total'] * 10
                ])
                 # Calculate Logistics emissions
                total_logistics_emissions = sum([
                    monthly_logistics.filter(Typeof_fuel='diesel').aggregate(
                        total=Coalesce(Sum('fuel_consumption'), 0.0))['total'] * diesel_factor,
                    monthly_logistics.filter(Typeof_fuel='petrol').aggregate(
                        total=Coalesce(Sum('fuel_consumption'), 0.0))['total'] * petrol_factor
                ])
                # Total emissions (energy + water)
                total_emissions = total_energy_emissions + total_water_emissions + total_waste_emissions + total_logistics_emissions
                # total_emissions = total_logistics_emissions
            
                
                # Store monthly emissions data
                monthly_total_emissions[month] = total_emissions

            # Prepare the response data for line chart
            line_chart_data = []
            for month in month_order:
                month_name = datetime(1900, month, 1).strftime('%b')  # Get month name
                line_chart_data.append({
                    "month": month_name,
                    "total_emissions": monthly_total_emissions.get(month, 0)
                })

            response_data = {
                'year': year,
                'line_chart_data': line_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            print(error_message)
            return Response({'error': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
'''Emissions Calculations starts'''

'''YearFilter Starts'''
class YearFacilityDataAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            facility_id = request.query_params.get('facility_id', 'all')  # Default to 'all'

            # Validate facility
            if facility_id != 'all' and not Facility.objects.filter(facility_id=facility_id, user=user).exists():
                return Response(
                    {'error': 'Invalid facility ID or not associated with the logged-in user.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Map categories to models (but we will only be interested in the years)
            model_serializer_map = {
                'waste': Waste,
                'energy': Energy,
                'water': Water,
                'biodiversity': Biodiversity,
                'logistics': Logistics,
            }

            # Fetch years from all categories (models)
            years_set = set()
            for model in model_serializer_map.values():
                queryset = model.objects.filter(user=user)
                if facility_id != 'all':
                    queryset = queryset.filter(facility__facility_id=facility_id)
                
                years_set.update(queryset.values_list('DatePicker__year', flat=True))

            # If no years found, return a friendly message
            if not years_set:
                return Response(
                    {'facility_id': facility_id, 'available_years': [{"year": "0"}]},
                    status=status.HTTP_200_OK
                )
            # Convert set to list and sort the years
            years_list = sorted(list(years_set), reverse=True)

            # Construct the response in the desired format
            response_data = [{"year": str(year)} for year in years_list]

            return Response({
                "facility_id": facility_id,
                "available_years": response_data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            print(error_message)  # For debugging purposes, consider using a logger in production
            return Response({'error': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
'''YearFilter Ends'''

'''ExcelSheets Upload Starts'''
class WasteExcelUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data['file']
            try:
                # Load Excel file
                data = pd.read_excel(file)

                # Map Excel columns to database fields
                column_mapping = {
                    'Facility': 'facility_id',  # Use facility_id for facility mapping
                    'Date': 'DatePicker',
                    'Category': 'category',
                    'Solid_Waste': 'solid_Waste',
                    'Food_Waste': 'food_waste',
                    'E_Waste': 'E_Waste',
                    'Liquid_Discharge': 'liquid_discharge',
                    'Biomedical_Waste': 'Biomedical_waste',
                    'Other_Waste': 'other_waste',
                    'Sent_for_Recycling': 'Recycle_waste',
                    'Sent_to_Landfill': 'Landfill_waste',
                    'Total': 'overall_usage'
                }

                # Ensure required columns are present
                required_columns = list(column_mapping.keys())
                if not all(col in data.columns for col in required_columns):
                    return Response(
                        {"error": f"Missing required columns. Required: {', '.join(required_columns)}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Rename columns for easier processing
                data.rename(columns=column_mapping, inplace=True)

                # Process each row in the Excel file
                user = request.user
                results = []

                for _, row in data.iterrows():
                    facility_id = row['facility_id']
                    date = pd.to_datetime(row['DatePicker'])
                    category = row['category']

                    row_result = {
                        "facility_id": facility_id,
                        "category": category,
                        "DatePicker": date.strftime('%Y-%m-%d'),
                        "food_waste": row['food_waste'],
                        "solid_Waste": row['solid_Waste'],
                        "E_Waste": row['E_Waste'],
                        "Biomedical_waste": row['Biomedical_waste'],
                        "liquid_discharge": row['liquid_discharge'],
                        "other_waste": row['other_waste'],
                        "Recycle_waste": row['Recycle_waste'],
                        "Landfill_waste": row['Landfill_waste'],
                        "overall_usage": row['overall_usage'],
                        "status": "Success"  # Default status
                    }

                    # Validate facility
                    try:
                        facility = Facility.objects.get(facility_id=facility_id, user=user)
                    except Facility.DoesNotExist:
                        row_result["status"] = f"Failed: Facility '{facility_id}' does not exist"
                        results.append(row_result)
                        continue

                    # Check for existing Waste entry
                    month = date.month
                    year = date.year
                    existing_entry = Waste.objects.filter(
                        facility=facility,
                        DatePicker__year=year,
                        DatePicker__month=month
                    )

                    if existing_entry.exists():
                        # Skip silently for duplicate data
                        continue

                    # Create Waste entry
                    Waste.objects.create(
                        user=user,
                        facility=facility,
                        category=category,
                        DatePicker=date,
                        food_waste=row['food_waste'],
                        solid_Waste=row['solid_Waste'],
                        E_Waste=row['E_Waste'],
                        Biomedical_waste=row['Biomedical_waste'],
                        liquid_discharge=row['liquid_discharge'],
                        other_waste=row['other_waste'],
                        Recycle_waste=row['Recycle_waste'],
                        Landfill_waste=row['Landfill_waste'],
                        overall_usage=row['overall_usage']
                    )

                    # Add successful row
                    results.append(row_result)

                # Return results directly as an array
                return Response(results, status=status.HTTP_200_OK)

            except Exception as e:
                return Response(
                    {"error": f"An error occurred while processing the file: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

'''Excel Sheets Upload Ends'''