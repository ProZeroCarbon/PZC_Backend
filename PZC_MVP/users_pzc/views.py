
from datetime import datetime
from collections import defaultdict
from django.db.models import Sum, Value, FloatField,Min, Max

from django.db.models.functions import Coalesce, Cast
from django.utils import timezone
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegisterSerializer, UserLoginSerializer,WasteSerializer,WasteCreateSerializer,EnergyCreateSerializer,EnergySerializer,WaterCreateSerializer,WaterSerializer,BiodiversityCreateSerializer,BiodiversitySerializer,FacilitySerializer,LogisticesSerializer,OrganizationSerializer
from .models import CustomUser,Waste,Energy,Water,Biodiversity,Facility,Logistices,Org_registration
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from users_pzc.filters import LogisticesFilter

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
class WasteCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = WasteCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Waste data added successfully."}, status=status.HTTP_201_CREATED)
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
            return Response(
                {
                    "message": "No data available for the selected facility and fiscal year.",
                    "email": user.email,
                    "year": year,
                    "waste_data": [],
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
        serializer = WaterCreateSerializer(data=request.data,context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response({"messages":"Water data added succesfully"},status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

#WaterView
# class WaterView(APIView):
#     permission_classes = [IsAuthenticated]
    
#     def get(self, request):
#         user = request.user
#         facility_id = request.GET.get('facility_id', 'all')
#         year = request.GET.get('year')
#         try:
#             if year:
#                 year = int(year)
#             else:
#                 current_date = datetime.now()
#                 year = current_date.year - 1 if current_date.month < 4 else current_date.year

#             start_date = datetime(year, 4, 1)
#             end_date = datetime(year + 1, 3, 31)
#         except ValueError:
#             return Response(
#                 {"error": "Invalid fiscal year format. Please provide a valid year, e.g., 2023."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         water_data = Water.objects.filter(user=user, DatePicker__range=(start_date, end_date))
#         if facility_id.lower() != 'all':
#             water_data = water_data.filter(facility__facility_id=facility_id)
#             print(f"Filtered Water Data Count by Facility: {water_data.count()}")
#         else:
#             print("Facility ID is 'all'; skipping facility filtering.")
        
#         if not water_data.exists():
#             return Response(
#                 {
#                     "message": "No data available for the selected facility and fiscal year.",
#                     "email": user.email,
#                     "year": year,
#                     "water_data": [],
#                     "overall_water_usage_total": 0
#                 },
#                 status=status.HTTP_200_OK
#             )
        
#         water_serializer = WaterSerializer(water_data, many=True)
#         overall_total = sum(water.overall_usage for water in water_data)
        
#         user_data = {
#             "email": user.email,
#             "water_data": water_serializer.data,
#             "overall_water_usage_total": overall_total
#         }
        
#         return Response(user_data, status=status.HTTP_200_OK)


# class WaterView(APIView):
#     permission_classes = [IsAuthenticated]
    
#     def get(self, request):
#         user = request.user
#         facility_id = request.GET.get('facility_id', 'all')
#         year = request.GET.get('year')
        
#         try:
#             if year:
#                 year = int(year)
#             else:
#                 current_date = datetime.now()
#                 year = current_date.year - 1 if current_date.month < 4 else current_date.year

#             start_date = datetime(year, 4, 1)
#             end_date = datetime(year + 1, 3, 31)
#         except ValueError:
#             return Response(
#                 {"error": "Invalid fiscal year format. Please provide a valid year, e.g., 2023."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
        
#         water_data = Water.objects.filter(user=user, DatePicker__range=(start_date, end_date))
#         if not water_data.exists() and not request.GET.get('year'):
#             latest_year = year
#             while not water_data.exists() and latest_year > 2000:
#                 latest_year -= 1
#                 start_date = datetime(latest_year, 4, 1)
#                 end_date = datetime(latest_year + 1, 3, 31)
#                 water_data = Water.objects.filter(user=user, DatePicker__range=(start_date, end_date))
#             year = latest_year
        
#         if facility_id.lower() != 'all':
#             water_data = water_data.filter(facility__facility_id=facility_id)
#             print(f"Filtered water Data Count by Facility: {water_data.count()}")
#         else:
#             print("Facility ID is 'all'; skipping facility filtering.")
        
#         if not water_data.exists():
#             return Response(
#                 {
#                     "message": "No data available for the selected facility and fiscal year.",
#                     "email": user.email,
#                     "year": year,
#                     "water_data": [],
#                     "overall_water_usage_total": 0
#                 },
#                 status=status.HTTP_200_OK
#             )
        
#         # Use the correct serializer (waterSerializer)
#         water_serializer = WaterSerializer(water_data, many=True)
        
#         # Calculate overall total
#         overall_total = sum(water.overall_usage for water in water_data)
        
#         user_data = {
#             "year":year,
#             "email": user.email,
#             "energy_data": water_serializer.data,
#             "overall_energy_usage_total": overall_total
#         }
        
#         return Response(user_data, status=status.HTTP_200_OK)


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
        
        water_data = Water.objects.filter(user=user, DatePicker__range=(start_date, end_date))

        if facility_id.lower() != 'all':
            water_data = water_data.filter(facility__facility_id=facility_id)
            print(f"Filtered water Data Count by Facility: {water_data.count()}")
        else:
            print("Facility ID is 'all'; skipping facility filtering.")
        
        if not water_data.exists():
            return Response(
                {
                    "message": "No data available for the selected facility and fiscal year.",
                    "email": user.email,
                    "year": year,
                    "water_data": [],
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
            print(f"Filtered Biodiversity Data Count by Facility: {biodiversity_data.count()}")
        else:
            print("Facility ID is 'all'; skipping facility filtering.")
        
        if not biodiversity_data.exists():
            return Response(
                {
                    "message": "No data available for the selected facility and fiscal year.",
                    "email": user.email,
                    "year": year,
                    "biodiversity_data": [],
                    "overall_biodiversity_usage_total": 0
                },
                status=status.HTTP_200_OK
            )
        
        biodiversity_serializer = BiodiversitySerializer(biodiversity_data, many=True)
        overall_total = sum(biodiversity.no_trees for biodiversity in biodiversity_data) 
        
        user_data = {
            "email": user.email,
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


'''Logistices CRUD Operations Starts'''
#Logistices Create Form
class LogisticesCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogisticesSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"message": "Logistices data added successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#View Logistices
class LogisticesView(APIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = LogisticesFilter    
    def get(self, request):
        user = request.user
        logistices_data = Logistices.objects.filter(user=user)
        filtered_logistices_data = LogisticesFilter(request.GET,queryset=logistices_data).qs
        logistices_serializer = LogisticesSerializer(filtered_logistices_data, many=True)
        overall_fuelconsumption = sum(logistices_fuel.fuel_consumption for logistices_fuel in logistices_data)
        user_data = {
            'email': user.email,
            'logistices_data': logistices_serializer.data,
            'Fuel_consumption_total':overall_fuelconsumption
        }
        return Response(user_data, status=status.HTTP_200_OK)

#Edit Logistices
class LogisticesEditView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            logistices = Logistices.objects.get(pk=pk, user=request.user)
        except Logistices.DoesNotExist:
            return Response({"error": "Logistices data not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = LogisticesSerializer(logistices, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Logistices data updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#Delete Logistices
class LogisticesDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            logistices = Logistices.objects.get(pk=pk, user=request.user)
        except Logistices.DoesNotExist:
            return Response({"error": "Logistices data not found."}, status=status.HTTP_404_NOT_FOUND)

        logistices.delete()
        return Response({"message": "Logistices data deleted successfully."}, status=status.HTTP_200_OK)

'''Logistices CRUD Operations Ends'''




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

        overall_data = {
            "waste_usage": 0,
            "energy_usage": 0,
            "water_usage": 0,
            "biodiversity_usage": 0,
            "logistics_usage": 0,
        }

        filters = {'user': user, 'DatePicker__range': (start_date, end_date)}
        if facility_id.lower() != 'all':
            filters['facility__facility_id'] = facility_id

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

        # Water usage
        water_data = Water.objects.filter(**filters)
        overall_data["water_usage"] = water_data.aggregate(total=Sum('overall_usage'))['total'] or 0

        # Biodiversity usage
        biodiversity_data = Biodiversity.objects.filter(**filters)
        overall_data["biodiversity_usage"] = biodiversity_data.aggregate(total=Sum('overall_Trees'))['total'] or 0

        # Logistics usage
        logistics_data = Logistices.objects.filter(**filters)
        overall_data["logistics_usage"] = logistics_data.aggregate(total=Sum('total_fuelconsumption'))['total'] or 0

        # Serialize data for each model
        waste_serializer = WasteSerializer(waste_data, many=True)
        energy_serializer = EnergySerializer(energy_data, many=True)
        water_serializer = WaterSerializer(water_data, many=True)
        biodiversity_serializer = BiodiversitySerializer(biodiversity_data, many=True)
        logistics_serializer = LogisticesSerializer(logistics_data, many=True)

        # Format response data
        response_data = {
            "email": user.email,
            "year": year,
            "facility_id": facility_id,
            "overall_data": overall_data,
            "details": {
                "waste_data": waste_serializer.data,
                "energy_data": energy_serializer.data,
                "water_data": water_serializer.data,
                "biodiversity_data": biodiversity_serializer.data,
                "logistics_data": logistics_serializer.data
            }
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
                "year":year,
                "landfill_percentage": landfill_percentage,
                "remaining_percentage": remaining_percentage
            }

            return Response(response_data, status=status.HTTP_200_OK)

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
                "year":year,
                "Recycle_percentage": Recycle_percentage,
                "remaining_percentage": remaining_percentage
            }

            return Response(response_data, status=status.HTTP_200_OK)

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
            if facility_id != 'all' and not Facility.objects.filter(facility_id=facility_id, user=user).exists():
                return Response({'error': 'Invalid facility ID or not associated with the logged-in user.'}, status=status.HTTP_400_BAD_REQUEST)

            if year:
                try:
                    year = int(year)
                    if year < 1900 or year > datetime.now().year + 10:  # Allow future years up to 10 years ahead
                        return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)
                except ValueError:
                    return Response({'error': 'Year must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)
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

            response_data = {
                'year': year,
                'overall_energy_totals': {},
                'facility_energy_data': {}
            }

            if not energy_data.exists():
                # Populate zero values when no data exists
                for field in energy_fields:
                    response_data['overall_energy_totals'][f"overall_{field}"] = 0
                    response_data['facility_energy_data'][field] = []
            else:
                for field in energy_fields:
                    # Facility-specific totals
                    facility_energy_data = (
                        energy_data
                        .values('facility__facility_name')
                        .annotate(total=Sum(field))
                        .order_by('-total')
                    )

                    response_data['facility_energy_data'][field] = [
                        {
                            "facility_name": entry['facility__facility_name'],
                            f"total_{field}": entry['total']
                        }
                        for entry in facility_energy_data
                    ]

                    # Overall totals
                    overall_total = energy_data.aggregate(total=Sum(field))['total'] or 0
                    response_data['overall_energy_totals'][f"overall_{field}"] = overall_total

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
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        try:
            if facility_id != 'all':
                if not Facility.objects.filter(facility_id=facility_id).exists():
                    return Response({'error': 'Invalid facility ID.'}, status=status.HTTP_400_BAD_REQUEST)

            if year:
                try:
                    year = int(year)  # Convert year to integer
                    if year < 1900 or year > datetime.now().year + 1: 
                        return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)
                except ValueError:
                    return Response({'error': 'Year must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)

            filters = {'user': user}
            water_data = Water.objects.filter(**filters)

            if year:
                start_date = datetime(year, 4, 1) 
                end_date = datetime(year + 1, 3, 31) 
                filters['DatePicker__range'] = (start_date, end_date)
                water_data = water_data.filter(**filters)
            else:
                today = datetime.now()
                if today.month >= 4:  # Current fiscal year
                    start_date = datetime(today.year, 4, 1)
                    end_date = datetime(today.year + 1, 3, 31)
                else:  # Last fiscal year (if before April)
                    start_date = datetime(today.year - 1, 4, 1)
                    end_date = datetime(today.year, 3, 31)
                filters['DatePicker__range'] = (start_date, end_date)
                water_data = water_data.filter(**filters)

            # Filter by facility_id if provided and valid
            if facility_id != 'all':
                water_data = water_data.filter(facility__facility_id=facility_id)

            # Filter by facility_location if provided
            if facility_location:
                water_data = water_data.filter(facility__facility_location__icontains=facility_location)

            water_fields = [
            'Generated_Water', 'Recycled_Water', 'Softener_usage', 'Boiler_usage', 'otherUsage'
            ]

            # Initialize response data
            response_data = {'overall_water_totals': {}, 'facility_water_data': {}}

            for field in water_fields:
                facility_water_data = (
                    water_data
                    .values('facility__facility_name')
                    .annotate(total=Sum(field))
                    .order_by('-total')
                )

                # Prepare facility-wise data for each water type
                response_data['facility_water_data'][field] = [
                    {
                        "facility_name": entry['facility__facility_name'],
                        f"total_{field}": entry['total']
                    }
                    for entry in facility_water_data
                ]

                overall_total = water_data.aggregate(total=Sum(field))['total'] or 0
                response_data['overall_water_totals'][f"overall_{field}"] = overall_total

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"An error occurred: {e}")
            return Response({'error': 'An error occurred while processing your request.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#GeneratedWater Overview Line Charts and Donut Chart
class Generated_WaterOverviewView(APIView):
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
                year = datetime.now().year
            
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

            monthly_Generated_Water = (
                Water.objects.filter(**filters)
                .values('DatePicker__month')
                .annotate(total_Generated_Water=Sum('Generated_Water'))
                .order_by('DatePicker__month')
            )

            line_chart_data = []
            Generated_Water = defaultdict(float)

            for entry in monthly_Generated_Water:
                Generated_Water[entry['DatePicker__month']] = entry['total_Generated_Water']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            today = datetime.now()

            for month in month_order:
                month_name = datetime(1900, month, 1).strftime('%b')
                if (year == today.year and month <= today.month) or (year < today.year):
                    line_chart_data.append({
                        "month": month_name,
                        "Generated_Water": Generated_Water.get(month, 0)
                    })
                else:
                    line_chart_data.append({
                        "month": month_name,
                        "Generated_Water": 0
                    })

            facility_filters = {
                'user': user,
                'DatePicker__range': (start_date, end_date)
            }
            if facility_id and facility_id.lower() != 'all':
                facility_filters['facility__facility_id'] = facility_id
            facility_Generated_Water = (
                Water.objects.filter(**facility_filters)
                .values('facility__facility_name')
                .annotate(total_Generated_Water=Sum('Generated_Water'))
                .order_by('-total_Generated_Water')
            )

            # Prepare donut chart data
            total_Generated_Water = sum(entry['total_Generated_Water'] for entry in facility_Generated_Water)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_Generated_Water'] / total_Generated_Water * 100) if total_Generated_Water else 0,
                }
                for entry in facility_Generated_Water
            ]

            response_data = {
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
#Recycle Water Overview line charts and Donut chart
class Recycle_WaterOverviewView(APIView):
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
                year = datetime.now().year
            
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

            monthly_Recycled_Water = (
                Water.objects.filter(**filters)
                .values('DatePicker__month')
                .annotate(total_Recycled_Water=Sum('Recycled_Water'))
                .order_by('DatePicker__month')
            )

            line_chart_data = []
            Recycled_Water = defaultdict(float)

            for entry in monthly_Recycled_Water:
                Recycled_Water[entry['DatePicker__month']] = entry['total_Recycled_Water']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            today = datetime.now()

            for month in month_order:
                month_name = datetime(1900, month, 1).strftime('%b')
                if (year == today.year and month <= today.month) or (year < today.year):
                    line_chart_data.append({
                        "month": month_name,
                        "Recycled_Water": Recycled_Water.get(month, 0)
                    })
                else:
                    line_chart_data.append({
                        "month": month_name,
                        "Recycled_Water": 0
                    })

            facility_filters = {
                'user': user,
                'DatePicker__range': (start_date, end_date)
            }
            if facility_id and facility_id.lower() != 'all':
                facility_filters['facility__facility_id'] = facility_id
            facility_Recycled_Water = (
                Water.objects.filter(**facility_filters)
                .values('facility__facility_name')
                .annotate(total_Recycled_Water=Sum('Recycled_Water'))
                .order_by('-total_Recycled_Water')
            )

            # Prepare donut chart data
            total_Recycled_Water = sum(entry['total_Recycled_Water'] for entry in facility_Recycled_Water)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_Recycled_Water'] / total_Recycled_Water * 100) if total_Recycled_Water else 0,
                }
                for entry in facility_Recycled_Water
            ]

            response_data = {
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

#SoftenSoftener_usage overview line chart and donut chart
class Softener_usageOverviewView(APIView):
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
                year = datetime.now().year
            
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

            monthly_Softener_usage = (
                Water.objects.filter(**filters)
                .values('DatePicker__month')
                .annotate(total_Softener_usage=Sum('Softener_usage'))
                .order_by('DatePicker__month')
            )

            line_chart_data = []
            Softener_usage = defaultdict(float)

            for entry in monthly_Softener_usage:
                Softener_usage[entry['DatePicker__month']] = entry['total_Softener_usage']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            today = datetime.now()

            for month in month_order:
                month_name = datetime(1900, month, 1).strftime('%b')
                if (year == today.year and month <= today.month) or (year < today.year):
                    line_chart_data.append({
                        "month": month_name,
                        "Softener_usage": Softener_usage.get(month, 0)
                    })
                else:
                    line_chart_data.append({
                        "month": month_name,
                        "Softener_usage": 0
                    })

            facility_filters = {
                'user': user,
                'DatePicker__range': (start_date, end_date)
            }
            if facility_id and facility_id.lower() != 'all':
                facility_filters['facility__facility_id'] = facility_id
            facility_Softener_usage = (
                Water.objects.filter(**facility_filters)
                .values('facility__facility_name')
                .annotate(total_Softener_usage=Sum('Softener_usage'))
                .order_by('-total_Softener_usage')
            )

            # Prepare donut chart data
            total_Softener_usage = sum(entry['total_Softener_usage'] for entry in facility_Softener_usage)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_Softener_usage'] / total_Softener_usage * 100) if total_Softener_usage else 0,
                }
                for entry in facility_Softener_usage
            ]

            response_data = {
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

#Boiler_usage Overview line chart and Donut Chart
class Boiler_usageOverviewView(APIView):
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
                year = datetime.now().year
            
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

            monthly_Boiler_usage = (
                Water.objects.filter(**filters)
                .values('DatePicker__month')
                .annotate(total_Boiler_usage=Sum('Boiler_usage'))
                .order_by('DatePicker__month')
            )

            line_chart_data = []
            Boiler_usage = defaultdict(float)

            for entry in monthly_Boiler_usage:
                Boiler_usage[entry['DatePicker__month']] = entry['total_Boiler_usage']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            today = datetime.now()

            for month in month_order:
                month_name = datetime(1900, month, 1).strftime('%b')
                if (year == today.year and month <= today.month) or (year < today.year):
                    line_chart_data.append({
                        "month": month_name,
                        "Boiler_usage": Boiler_usage.get(month, 0)
                    })
                else:
                    line_chart_data.append({
                        "month": month_name,
                        "Boiler_usage": 0
                    })

            facility_filters = {
                'user': user,
                'DatePicker__range': (start_date, end_date)
            }
            if facility_id and facility_id.lower() != 'all':
                facility_filters['facility__facility_id'] = facility_id
            facility_Boiler_usage = (
                Water.objects.filter(**facility_filters)
                .values('facility__facility_name')
                .annotate(total_Boiler_usage=Sum('Boiler_usage'))
                .order_by('-total_Boiler_usage')
            )

            # Prepare donut chart data
            total_Boiler_usage = sum(entry['total_Boiler_usage'] for entry in facility_Boiler_usage)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_Boiler_usage'] / total_Boiler_usage * 100) if total_Boiler_usage else 0,
                }
                for entry in facility_Boiler_usage
            ]

            response_data = {
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

#otherUsage overview line chart and Donut chart
class otherUsage_OverviewView(APIView):
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
                year = datetime.now().year
            
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

            monthly_otherUsage = (
                Water.objects.filter(**filters)
                .values('DatePicker__month')
                .annotate(total_otherUsage=Sum('otherUsage'))
                .order_by('DatePicker__month')
            )

            line_chart_data = []
            otherUsage = defaultdict(float)

            for entry in monthly_otherUsage:
                otherUsage[entry['DatePicker__month']] = entry['total_otherUsage']

            month_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            today = datetime.now()

            for month in month_order:
                month_name = datetime(1900, month, 1).strftime('%b')
                if (year == today.year and month <= today.month) or (year < today.year):
                    line_chart_data.append({
                        "month": month_name,
                        "otherUsage": otherUsage.get(month, 0)
                    })
                else:
                    line_chart_data.append({
                        "month": month_name,
                        "otherUsage": 0
                    })

            facility_filters = {
                'user': user,
                'DatePicker__range': (start_date, end_date)
            }
            if facility_id and facility_id.lower() != 'all':
                facility_filters['facility__facility_id'] = facility_id
            facility_otherUsage = (
                Water.objects.filter(**facility_filters)
                .values('facility__facility_name')
                .annotate(total_otherUsage=Sum('otherUsage'))
                .order_by('-total_otherUsage')
            )

            # Prepare donut chart data
            total_otherUsage = sum(entry['total_otherUsage'] for entry in facility_otherUsage)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_otherUsage'] / total_otherUsage * 100) if total_otherUsage else 0,
                }
                for entry in facility_otherUsage
            ]

            response_data = {
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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

            year = int(year) if year else datetime.now().year
            today = datetime.now()
            if today.month >= 4:
                start_date = datetime(year, 4, 1)
                end_date = datetime(year + 1, 3, 31)
            else:
                start_date = datetime(year - 1, 4, 1)
                end_date = datetime(year, 3, 31)
            filters['DatePicker__range'] = (start_date, end_date)

            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location and facility_location.lower() != 'all':
                filters['facility__facility_location__icontains'] = facility_location

            water_types = [
            'Generated_Water', 'Recycled_Water', 'Softener_usage', 'Boiler_usage', 'otherUsage'
            ]

            monthly_data = {month: {water_type: 0 for water_type in water_types} for month in range(1, 13)}
 
            for water_type in water_types:
                queryset = Water.objects.filter(**filters)

                # Aggregate monthly data with explicit output_field for each water type
                monthly_water = (
                    queryset
                    .values('DatePicker__month')
                    .annotate(total=Coalesce(Sum(water_type, output_field=FloatField()), Value(0, output_field=FloatField())))
                    .order_by('DatePicker__month')
                )

                for entry in monthly_water:
                    month = entry['DatePicker__month']
                    monthly_data[month][water_type] = entry['total']

                # # Specific debug for December to check if values are captured
                # december_data = queryset.filter(DatePicker__month=12).aggregate(
                #     total=Coalesce(Sum(water_type, output_field=FloatField()), Value(0, output_field=FloatField()))
                # )
                # print(f"December total for {water_type}: {december_data['total']}")

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
#Water Analytics Donut chart and pie chart Overview
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
            if year:
                try:
                    year = int(year)
                except ValueError:
                    return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)
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

            # Query water data and aggregate fields
            queryset = Water.objects.filter(**filters)
            water_totals = queryset.aggregate(
                Softener_usage_total=Coalesce(Sum(Cast('Softener_usage', FloatField())), 0.0),
                Boiler_usage_total=Coalesce(Sum(Cast('Boiler_usage', FloatField())), 0.0),
                otherUsage_total=Coalesce(Sum(Cast('otherUsage', FloatField())), 0.0),
                Generated_Water_total=Coalesce(Sum(Cast('Generated_Water', FloatField())), 0.0),
                Recycled_Water_total=Coalesce(Sum(Cast('Recycled_Water', FloatField())), 0.0)
            )

            generated_recycled_total = water_totals['Generated_Water_total'] + water_totals['Recycled_Water_total']

            water_percentages = {}
            for water_type, total in {
                "Softener Usage": water_totals['Softener_usage_total'],
                "Boiler Usage": water_totals['Boiler_usage_total'],
                "Other Usage": water_totals['otherUsage_total']
            }.items():
                water_percentages[water_type] = (total / generated_recycled_total * 100) if generated_recycled_total else 0

            recycled_water = water_totals['Recycled_Water_total']
            remaining_water = generated_recycled_total - recycled_water
            recycled_water_percentage = (recycled_water / generated_recycled_total * 100) if generated_recycled_total else 0
            remaining_water_percentage = (remaining_water / generated_recycled_total * 100) if generated_recycled_total else 0

            response_data = {
                "year": year,
                "facility_id": facility_id,
                "facility_location": facility_location,
                "donut_chart_data": water_percentages,
                "pie_chart_data": [
                    {"label": "Recycled Water", "value": recycled_water_percentage},
                    {"label": "Remaining Water", "value": remaining_water_percentage}
                ]
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error occurred: {e}")
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
  
      
'''Water Overview Cards ,Graphs and Individual Line Charts and donut Charts Ends'''
# class BiodiversityMetricsView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user
#         facility_id = request.GET.get('facility_id', 'all')
#         year = request.GET.get('year')
        
#         try:
#             # Validate and parse year
#             if year:
#                 try:
#                     year = int(year)
#                     if year < 1900 or year > datetime.now().year + 1:
#                         return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)
#                 except ValueError:
#                     return Response({'error': 'Year must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)

#             # Financial year date range
#             today = datetime.now()
#             if year:
#                 start_date = datetime(year, 4, 1)
#                 end_date = datetime(year + 1, 3, 31)
#             else:
#                 if today.month >= 4:
#                     start_date = datetime(today.year, 4, 1)
#                     end_date = datetime(today.year + 1, 3, 31)
#                 else:
#                     start_date = datetime(today.year - 1, 4, 1)
#                     end_date = datetime(today.year, 3, 31)

#             # Filter data based on user, facility, and date range
#             filters = {'user': user, 'DatePicker__range': (start_date, end_date)}
#             if facility_id != 'all':
#                 filters['facility__facility_id'] = facility_id

#             biodiversity_data = Biodiversity.objects.filter(**filters)

#             if not biodiversity_data.exists():
#                 return Response({
#                     "message": "No biodiversity data available for the selected facility and fiscal year."
#                 }, status=status.HTTP_200_OK)

#             # Calculating metrics
#             total_trees = biodiversity_data.aggregate(total_trees=Sum('no_trees'))['total_trees'] or 0
#             total_new_trees = biodiversity_data.aggregate(total_new_trees=Sum('new_trees_planted'))['total_new_trees'] or 0
#             total_area = biodiversity_data.aggregate(total_area=Sum('totalArea'))['total_area'] or 0
#             head_count = biodiversity_data.aggregate(head_count=Sum('head_count'))['head_count'] or 0

#             # Metric calculations
#             green_belt_density = (total_trees / total_area) * 10000 if total_area else 0
#             trees_per_capita = total_trees / head_count if head_count else 0

#             # Carbon Offset and CO2 sequestration
#             carbon_offset = sum(0.00006 * entry.width * entry.width * entry.height * entry.no_trees for entry in biodiversity_data)
#             biomass = sum(0.0998 * entry.width * entry.width * entry.height for entry in biodiversity_data)
#             co2_sequestration_rate = carbon_offset # Assuming offset per year

#             # Response data
#             response_data = {
#                 "facility_id": facility_id,
#                 "year": year or today.year,
#                 "metrics": {
#                     "total_trees": total_trees,
#                     "carbon_offset": carbon_offset,
#                     "green_belt_density": green_belt_density,
#                     "trees_per_capita": trees_per_capita,
#                     "total_new_trees": total_new_trees,
#                     "biomass": biomass,
#                     "co2_sequestration_rate": co2_sequestration_rate
#                 }
#             }

#             return Response(response_data, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# # class BiodiversityMetricsView(APIView):
# #     permission_classes = [IsAuthenticated]

# #     def get(self, request):
# #         user = request.user
# #         facility_id = request.GET.get('facility_id', 'all')
# #         year = request.GET.get('year')
        
# #         try:
# #             # Validate and parse year
# #             if year:
# #                 try:
# #                     year = int(year)
# #                     if year < 1900 or year > datetime.now().year + 1:
# #                         return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)
# #                 except ValueError:
# #                     return Response({'error': 'Year must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)

# #             # Financial year date range
# #             today = datetime.now()
# #             if year:
# #                 start_date = datetime(year, 4, 1)
# #                 end_date = datetime(year + 1, 3, 31)
# #             else:
# #                 if today.month >= 4:
# #                     start_date = datetime(today.year, 4, 1)
# #                     end_date = datetime(today.year + 1, 3, 31)
# #                 else:
# #                     start_date = datetime(today.year - 1, 4, 1)
# #                     end_date = datetime(today.year, 3, 31)

# #             # Filter data based on user, facility, and date range
# #             filters = {'user': user, 'DatePicker__range': (start_date, end_date)}
# #             if facility_id != 'all':
# #                 filters['facility__facility_id'] = facility_id

# #             biodiversity_data = Biodiversity.objects.filter(**filters)

# #             if not biodiversity_data.exists():
# #                 return Response({
# #                     "message": "No biodiversity data available for the selected facility and fiscal year."
# #                 }, status=status.HTTP_200_OK)

# #             # Calculate total metrics
# #             total_trees = biodiversity_data.aggregate(total_trees=Sum('no_trees'))['total_trees'] or 0
# #             total_new_trees = biodiversity_data.aggregate(total_new_trees=Sum('new_trees_planted'))['total_new_trees'] or 0
# #             total_area = biodiversity_data.aggregate(total_area=Sum('totalArea'))['total_area'] or 0
# #             head_count = biodiversity_data.aggregate(head_count=Sum('head_count'))['head_count'] or 0

# #             # Metric calculations
# #             green_belt_density = (total_trees / total_area) * 10000 if total_area else 0
# #             trees_per_capita = total_trees / head_count if head_count else 0

# #             # Calculate year-wise CO2 sequestration and biomass
# #             year_wise_data = {}
# #             current_year = start_date.year

# #             while current_year <= end_date.year:
# #                 year_start = datetime(current_year, 4, 1)
# #                 year_end = datetime(current_year + 1, 3, 31)

# #                 # Filter for the current fiscal year
# #                 yearly_data = biodiversity_data.filter(DatePicker__range=(year_start, year_end))

# #                 # Calculate CO2 sequestration and biomass for the current fiscal year
# #                 carbon_offset = sum(0.00006 * entry.width * entry.width * entry.height * entry.no_trees for entry in yearly_data)
# #                 biomass = sum(0.0998 * entry.width * entry.width * entry.height for entry in yearly_data)

# #                 year_wise_data[current_year] = {
# #                     "carbon_offset": carbon_offset,
# #                     "biomass": biomass,
# #                     "co2_sequestration_rate": carbon_offset  # Assuming offset per year
# #                 }

# #                 current_year += 1

# #             # Response data
# #             response_data = {
# #                 "facility_id": facility_id,
# #                 "year": year or today.year,
# #                 "metrics": {
# #                     "total_trees": total_trees,
# #                     "green_belt_density": green_belt_density,
# #                     "trees_per_capita": trees_per_capita,
# #                     "total_new_trees": total_new_trees
# #                 },
# #                 "year_wise_data": year_wise_data
# #             }

# #             return Response(response_data, status=status.HTTP_200_OK)

# #         except Exception as e:
# #             error_message = f"An error occurred: {str(e)}"
# #             print(error_message)
# #             return Response({'error': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# class BiodiversityMetricsView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user
#         facility_id = request.GET.get('facility_id', 'all')
#         year = request.GET.get('year')
        
#         try:
#             # Validate and parse the year
#             if year:
#                 try:
#                     year = int(year)
#                     if year < 1900 or year > datetime.now().year + 1:
#                         return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)
#                 except ValueError:
#                     return Response({'error': 'Year must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)

#             # Set fiscal year date range
#             today = datetime.now()
#             if year:
#                 start_date = datetime(year, 4, 1)
#                 end_date = datetime(year + 1, 3, 31)
#             else:
#                 if today.month >= 4:
#                     start_date = datetime(today.year, 4, 1)
#                     end_date = datetime(today.year + 1, 3, 31)
#                 else:
#                     start_date = datetime(today.year - 1, 4, 1)
#                     end_date = datetime(today.year, 3, 31)

#             # Filter biodiversity data based on user, facility, and date range
#             filters = {'user': user, 'DatePicker__range': (start_date, end_date)}
#             if facility_id != 'all':
#                 filters['facility__facility_id'] = facility_id

#             biodiversity_data = Biodiversity.objects.filter(**filters)

#             if not biodiversity_data.exists():
#                 return Response({
#                     "message": "No biodiversity data available for the selected facility and fiscal year."
#                 }, status=status.HTTP_200_OK)

#             # Calculate metrics
#             total_trees = biodiversity_data.aggregate(total_trees=Sum('no_trees'))['total_trees'] or 0
#             total_new_trees = biodiversity_data.aggregate(total_new_trees=Sum('new_trees_planted'))['total_new_trees'] or 0
#             total_area = biodiversity_data.aggregate(total_area=Sum('totalArea'))['total_area'] or 0
#             head_count = biodiversity_data.aggregate(head_count=Sum('head_count'))['head_count'] or 0

#             # Metric calculations
#             green_belt_density = (total_trees / total_area) * 10000 if total_area else 0
#             trees_per_capita = total_trees / head_count if head_count else 0

#             # Find initial and final years for the CO2 sequestration calculation
#             initial_year = biodiversity_data.aggregate(Min('DatePicker'))['DatePicker__min'].year
#             final_year = biodiversity_data.aggregate(Max('DatePicker'))['DatePicker__max'].year

#             # Calculate carbon offset and CO2 sequestration rate
#             carbon_offset = sum(0.00006 * entry.width * entry.width * entry.height * entry.no_trees for entry in biodiversity_data)
#             biomass = sum(0.0998 * entry.width * entry.width * entry.height for entry in biodiversity_data)

#             # Calculate cumulative CO2 sequestration rate across years
#             co2_sequestration_rate = 0
#             for entry in biodiversity_data:
#                 entry_year = entry.DatePicker.year
#                 year_difference = entry_year - initial_year + 1  # Avoid division by zero
#                 co2_sequestration_rate += (0.00006 * entry.width * entry.width * entry.height * entry.no_trees) / year_difference

#             # Prepare response data
#             response_data = {
#                 "facility_id": facility_id,
#                 "year": year or today.year,
#                 "metrics": {
#                     "total_trees": total_trees,
#                     "carbon_offset": carbon_offset,
#                     "green_belt_density": green_belt_density,
#                     "trees_per_capita": trees_per_capita,
#                     "total_new_trees": total_new_trees,
#                     "biomass": biomass,
#                     "co2_sequestration_rate": co2_sequestration_rate
#                 }
#             }

#             return Response(response_data, status=status.HTTP_200_OK)

#         except Exception as e:
#             error_message = f"An error occurred while processing biodiversity metrics: {str(e)}"
#             return Response({'error': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BiodiversityMetricsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', 'all')
        year = request.GET.get('year')
        
        try:
            # Validate and parse the year
            if year:
                try:
                    year = int(year)
                    if year < 1900 or year > datetime.now().year + 1:
                        return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)
                except ValueError:
                    return Response({'error': 'Year must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)

            # Set fiscal year date range
            today = datetime.now()
            if year:
                start_date = datetime(year, 4, 1)
                end_date = datetime(year + 1, 3, 31)
            else:
                if today.month >= 4:
                    start_date = datetime(today.year, 4, 1)
                    end_date = datetime(today.year + 1, 3, 31)
                else:
                    start_date = datetime(today.year - 1, 4, 1)
                    end_date = datetime(today.year, 3, 31)

            # Filter biodiversity data based on user, facility, and date range
            filters = {'user': user, 'DatePicker__range': (start_date, end_date)}
            if facility_id != 'all':
                filters['facility__facility_id'] = facility_id

            biodiversity_data = Biodiversity.objects.filter(**filters)

            if not biodiversity_data.exists():
                return Response({
                    "message": "No biodiversity data available for the selected facility and fiscal year."
                }, status=status.HTTP_200_OK)

            # Calculate metrics
            total_trees = biodiversity_data.aggregate(total_trees=Sum('no_trees'))['total_trees'] or 0
            total_new_trees = biodiversity_data.aggregate(total_new_trees=Sum('new_trees_planted'))['total_new_trees'] or 0
            total_area = biodiversity_data.aggregate(total_area=Sum('totalArea'))['total_area'] or 0
            head_count = biodiversity_data.aggregate(head_count=Sum('head_count'))['head_count'] or 0

            # Metric calculations
            green_belt_density = (total_trees / total_area) * 10000 if total_area else 0
            trees_per_capita = total_trees / head_count if head_count else 0

            # Find the final year for the CO2 sequestration calculation
            final_year = biodiversity_data.aggregate(Max('DatePicker'))['DatePicker__max'].year
            previous_year = final_year - 1

            # Filter data for each year and calculate CO2 sequestration
            co2_final_year = biodiversity_data.filter(DatePicker__year=final_year).aggregate(
                co2=Sum(0.00006 * 'width' * 'width' * 'height' * 'no_trees')
            )['co2'] or 0

            co2_previous_year = biodiversity_data.filter(DatePicker__year=previous_year).aggregate(
                co2=Sum(0.00006 * 'width' * 'width' * 'height' * 'no_trees')
            )['co2'] or 0

            # Calculate the CO2 sequestration rate difference
            co2_sequestration_rate = co2_final_year - co2_previous_year

            # Prepare response data
            response_data = {
                "facility_id": facility_id,
                "year": year or today.year,
                "metrics": {
                    "total_trees": total_trees,
                    "carbon_offset": co2_final_year,
                    "green_belt_density": green_belt_density,
                    "trees_per_capita": trees_per_capita,
                    "total_new_trees": total_new_trees,
                    "biomass": sum(0.0998 * entry.width * entry.width * entry.height for entry in biodiversity_data),
                    "co2_sequestration_rate": co2_sequestration_rate
                }
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            error_message = f"An error occurred while processing biodiversity metrics: {str(e)}"
            return Response({'error': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)