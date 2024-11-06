
from datetime import datetime
from collections import defaultdict
from django.db.models import Sum, Value, FloatField
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
from users_pzc.filters import WasteFilter,EnergyFilter,WaterFilter,BiodiversityFilter,LogisticesFilter,FacilityFilter

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
    
#FacilityView or get
class FacilityView(APIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = FacilityFilter

    def get(self, request):
        user = request.user
        facility_data = Facility.objects.filter(user=user)
        filtered_facility_data = FacilityFilter(request.GET,queryset=facility_data).qs
        facility_serializer = FacilitySerializer(filtered_facility_data, many=True)
        user_data = {
            'email': user.email,
            'facility_data': facility_serializer.data
        }
        return Response(user_data, status=status.HTTP_200_OK)

        
#FAcility Update
class FacilityEditView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            facility = Facility.objects.get(pk=pk, user=request.user)
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

    def delete(self, request, pk):
        # Check if pk is a positive integer
        if not isinstance(pk, int) or pk <= 0:
            return Response({"error": "Invalid ID provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Try to get the facility belonging to the user
            facility = Facility.objects.get(pk=pk, user=request.user)
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
    filter_backends = [DjangoFilterBackend]
    filterset_class = WasteFilter
    
    def get(self,request):
        user =request.user
        waste_data = Waste.objects.filter(user=user)
        filtered_waste_data = WasteFilter(request.GET, queryset=waste_data).qs
        waste_serializer = WasteSerializer(filtered_waste_data, many=True)
        overall_total = sum(
            waste.food_waste + waste.solid_Waste + waste.E_Waste + waste.Biomedical_waste + waste.other_waste
            for waste in filtered_waste_data
        )
        response_data = {
            'email': user.email,
            'waste_data': waste_serializer.data,
            'overall_waste_total': overall_total
        }
        return Response(response_data, status=status.HTTP_200_OK)
#EditWaste
class WasteEditView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            waste = Waste.objects.get(pk=pk, user=request.user)
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

    def delete(self, request, pk):
        try:
            waste = Waste.objects.get(pk=pk, user=request.user)
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


#Energyview
class EnergyView(APIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = EnergyFilter
    
    def get(self, request):
        user = request.user
        energy_data = Energy.objects.filter(user=user)
        filtered_energy_data =EnergyFilter(request.GET,queryset=energy_data).qs
        energy_serializer = EnergySerializer(filtered_energy_data,many=True)
        overall_total = 0.0
        for energy in energy_data:
            overall_total +=(energy.hvac + energy.production + energy.stp_etp + energy.admin_block + energy.utilities + energy.others)
        
        user_data={
            'email' : user.email,
            'energy_data' : energy_serializer.data,
            'over_all_Energy_total' : overall_total
            
        }
        return Response(user_data,status=status.HTTP_200_OK)
    
#EnergyEdit
class EnergyEditView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            energy = Energy.objects.get(pk=pk, user=request.user)
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

    def delete(self, request, pk):
        try:
            energy = Energy.objects.get(pk=pk, user=request.user)
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
        return Response(serializer.error,status=status.HTTP_400_BAD_REQUEST)

#WaterView 
class WaterView(APIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = WaterFilter
    
    def get(self,request):
        user = request.user
        water_data = Water.objects.filter(user=user)
        filtered_water_data = WaterFilter(request.GET,queryset=water_data).qs
        water_serializer = WaterSerializer(filtered_water_data,many=True)
        overall_total = sum(water.overall_usage for water in water_data)
        # overall_total = 0.0
        # for water in water_data:
        #     overall_total +=(water.generated_water + water.recycled_water + water.softener_usage + water.boiler_usage + water.other_usage)
        user_data={
           ' email' : user.email,
            'water_data' : water_serializer.data,
            'overall_water_usage_total': overall_total
        }
        return Response(user_data,status=status.HTTP_200_OK)

#WaterEdit
class WaterEditView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            water = Water.objects.get(pk=pk, user=request.user)
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

    def delete(self, request, pk):
        try:
            water = Water.objects.get(pk=pk, user=request.user)
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
    filter_backends = [DjangoFilterBackend]
    filterset_class = BiodiversityFilter
    def get(self,request):
        user = request.user
        biodiversity_data = Biodiversity.objects.filter(user=user)
        filtered_biodiversity_data = BiodiversityFilter(request.GET,queryset=biodiversity_data).qs
        biodiversity_serializer = BiodiversitySerializer(filtered_biodiversity_data,many=True)
        overall_total = sum(biodiversity.no_of_trees for biodiversity in biodiversity_data) 
        user_data={
            'email' : user.email,
            'biodiversity_data':biodiversity_serializer.data,
            'biodiversity_total':overall_total
        }
        return Response(user_data,status=status.HTTP_200_OK)

#BiodiversityEdit
class BiodiversityEditView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            biodiversity = Biodiversity.objects.get(pk=pk, user=request.user)
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

    def delete(self, request, pk):
        try:
            biodiversity = Biodiversity.objects.get(pk=pk, user=request.user)
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
    
    
'''Waste Overviewgraphs and Individual Line charts and donut charts Starts'''

#FoodWaste Overview
class FoodWasteOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        year = request.GET.get('year', None)
        
        if year is None:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Query to get monthly food waste
            if facility_id and facility_id.lower() != 'all':
                monthly_food_waste = (
                    Waste.objects.filter(user=user, facility__id=facility_id, date__year=year)
                    .values('date__month')
                    .annotate(total_food_waste=Sum('food_waste'))
                    .order_by('date__month')
                )
            else:
                monthly_food_waste = (
                    Waste.objects.filter(user=user, date__year=year)
                    .values('date__month')
                    .annotate(total_food_waste=Sum('food_waste'))
                    .order_by('date__month')
                )

          
            line_chart_data = []
            food_waste = defaultdict(float)

            for entry in monthly_food_waste:
                month_name = datetime(1900, entry['date__month'], 1).strftime('%b')
                food_waste[entry['date__month']] = entry['total_food_waste']

            for month in range(1, 13):
                month_name = datetime(1900, month, 1).strftime('%b')
                line_chart_data.append({
                    "month": month_name,
                    "food_waste": food_waste.get(month, 0)
                })

            # Query for facility-wise food waste
            if facility_id and facility_id.lower() != 'all':
                facility_food_waste = (
                    Waste.objects.filter(user=user, facility__id=facility_id)
                    .values('facility__facility_name')
                    .annotate(total_food_waste=Sum('food_waste'))
                    .order_by('-total_food_waste')
                )
            else:
                facility_food_waste = (
                    Waste.objects.filter(user=user)
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
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': 'An error occurred while processing your request.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#foodWaste Overview Card
class FoodWasteViewCard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        year = request.GET.get('year', None)
        
        if year is None:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Filter waste data based on user, facility, and year
            food_waste_data = Waste.objects.filter(user=user, data__year=year)
            
            if facility_id and facility_id.lower() != 'all':
                food_waste_data = food_waste_data.filter(facility__id=facility_id)

            # Calculate the total food waste for each facility for the specified year
            facility_food_waste = (
                food_waste_data
                .values('facility__facility_name')
                .annotate(total_food_waste=Sum('food_waste'))
                .order_by('-total_food_waste')
            )

            facility_food_waste_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "total_food_waste": entry['total_food_waste']
                }
                for entry in facility_food_waste
            ]

            # Overall food waste for the year across all facilities (if applicable)
            overall_food_waste = food_waste_data.aggregate(total=Sum('food_waste'))['total'] or 0

            response_data = {
                'overall_food_waste': overall_food_waste,
                'facility_food_waste': facility_food_waste_data,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': 'An error occurred while processing your request.'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)



#Solid Waste overview
class SolidWasteOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        year = request.GET.get('year', None)
        
        if year is None:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Query to get monthly solid waste
            if facility_id and facility_id.lower() != 'all':
                monthly_solid_waste = (
                    Waste.objects.filter(user=user, facility__id=facility_id, DatePicker__year=year)
                    .values('DatePicker__month')
                    .annotate(total_solid_waste=Sum('solid_waste'))
                    .order_by('DatePicker__month')
                )
            else:
                monthly_solid_waste = (
                    Waste.objects.filter(user=user, data__year=year)
                    .values('DatePicker__month')
                    .annotate(total_solid_waste=Sum('solid_waste'))
                    .order_by('DatePicker__month')
                )

            line_chart_data = []
            solid_waste = defaultdict(float)

            for entry in monthly_solid_waste:
                month_name = datetime(1900, entry['DatePicker__month'], 1).strftime('%b')
                solid_waste[entry['DatePicker__month']] = entry['total_solid_waste']

            for month in range(1, 13):
                month_name = datetime(1900, month, 1).strftime('%b')
                line_chart_data.append({
                    "month": month_name,
                    "solid_waste": solid_waste.get(month, 0)
                })
                
            # Query for facility-wise solid waste
            if facility_id and facility_id.lower() != 'all':
                facility_solid_waste = (
                    Waste.objects.filter(user=user, facility__id=facility_id)
                    .values('facility__facility_name')
                    .annotate(total_solid_waste=Sum('solid_waste'))
                    .order_by('-total_solid_waste')
                )
            else:
                facility_solid_waste = (
                    Waste.objects.filter(user=user)
                    .values('facility__facility_name')
                    .annotate(total_solid_waste=Sum('solid_waste'))
                    .order_by('-total_solid_waste')
                )

            total_solid_waste = sum(entry['total_solid_waste'] for entry in facility_solid_waste)
            
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_solid_waste'] / total_solid_waste * 100) if total_solid_waste else 0,
                }
                for entry in facility_solid_waste
            ]

            response_data = {
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': 'An error occurred while processing your request.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Solid Waste overview Card
class SolidWasteViewCard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        year = request.GET.get('year', None)
        
        if year is None:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Filter waste data based on user, facility, and year
            solid_waste_data = Waste.objects.filter(user=user, DatePicker__year=year)
            
            if facility_id and facility_id.lower() != 'all':
                solid_waste_data = solid_waste_data.filter(facility__id=facility_id)

            # Calculate the total food waste for each facility for the specified year
            facility_solid_waste = (
                solid_waste_data
                .values('facility__facility_name')
                .annotate(total_solid_waste=Sum('solid_waste'))
                .order_by('-total_solid_waste')
            )

            facility_solid_waste_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "total_solid_waste": entry['total_solid_waste']
                }
                for entry in facility_solid_waste
            ]

            # Overall food waste for the year across all facilities (if applicable)
            overall_solid_waste = solid_waste_data.aggregate(total=Sum('solid_waste'))['total'] or 0

            response_data = {
                'overall_solid_waste': overall_solid_waste,
                'facility_solid_waste': facility_solid_waste_data,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': 'An error occurred while processing your request.'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#e_waste overview view
class E_WasteOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        year = request.GET.get('year', None)
        
        if year is None:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Query to get monthly e-waste
            if facility_id and facility_id.lower() != 'all':
                monthly_e_waste = (
                    Waste.objects.filter(user=user, facility__id=facility_id, created_at__year=year)
                    .values('created_at__month')
                    .annotate(total_e_waste=Sum('e_waste'))
                    .order_by('created_at__month')
                )
            else:
                monthly_e_waste = (
                    Waste.objects.filter(user=user, created_at__year=year)
                    .values('created_at__month')
                    .annotate(total_e_waste=Sum('e_waste'))
                    .order_by('created_at__month')
                )
                
            line_chart_data = []
            e_waste = defaultdict(float)

            for entry in monthly_e_waste:
                month_name = datetime(1900, entry['created_at__month'], 1).strftime('%b')
                e_waste[entry['created_at__month']] = entry['total_e_waste']

            for month in range(1, 13):
                month_name = datetime(1900, month, 1).strftime('%b')
                line_chart_data.append({
                    "month": month_name,
                    "e_waste": e_waste.get(month, 0)
                })
            # Query for facility-wise e-waste
            if facility_id and facility_id.lower() != 'all':
                facility_e_waste = (
                    Waste.objects.filter(user=user, facility__id=facility_id)
                    .values('facility__facility_name')
                    .annotate(total_e_waste=Sum('e_waste'))
                    .order_by('-total_e_waste')
                )
            else:
                facility_e_waste = (
                    Waste.objects.filter(user=user)
                    .values('facility__facility_name')
                    .annotate(total_e_waste=Sum('e_waste'))
                    .order_by('-total_e_waste')
                )

            total_e_waste = sum(entry['total_e_waste'] for entry in facility_e_waste)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_e_waste'] / total_e_waste * 100) if total_e_waste else 0,
                }
                for entry in facility_e_waste
            ]

            response_data = {
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': 'An error occurred while processing your request.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#E-waste Overview Card
class E_WasteViewCard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        year = request.GET.get('year', None)
        
        if year is None:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Filter waste data based on user, facility, and year
            e_waste_data = Waste.objects.filter(user=user, created_at__year=year)
            
            if facility_id and facility_id.lower() != 'all':
                e_waste_data = e_waste_data.filter(facility__id=facility_id)

            # Calculate the total food waste for each facility for the specified year
            facility_e_waste = (
                e_waste_data
                .values('facility__facility_name')
                .annotate(total_e_waste=Sum('e_waste'))
                .order_by('-total_e_waste')
            )

            facility_e_waste_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "total_e_waste": entry['total_e_waste']
                }
                for entry in facility_e_waste
            ]

            # Overall food waste for the year across all facilities (if applicable)
            overall_e_waste = e_waste_data.aggregate(total=Sum('e_waste'))['total'] or 0

            response_data = {
                'overall_e_waste': overall_e_waste,
                'facility_e_waste': facility_e_waste_data,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': 'An error occurred while processing your request.'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#biomedical_waste Overview

class Biomedical_WasteOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        year = request.GET.get('year', None)
        
        if year is None:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if facility_id and facility_id.lower() != 'all':
                monthly_biomedical_waste = (
                    Waste.objects.filter(user=user, facility__id=facility_id, created_at__year=year)
                    .values('created_at__month')
                    .annotate(total_biomedical_waste=Sum('biomedical_waste'))
                    .order_by('created_at__month')
                )
            else:
                monthly_biomedical_waste = (
                    Waste.objects.filter(user=user, created_at__year=year)
                    .values('created_at__month')
                    .annotate(total_biomedical_waste=Sum('biomedical_waste'))
                    .order_by('created_at__month')
                )

            
            line_chart_data = []
            biomedical_waste = defaultdict(float)

            for entry in monthly_biomedical_waste:
                month_name = datetime(1900, entry['created_at__month'], 1).strftime('%b')
                biomedical_waste[entry['created_at__month']] = entry['total_biomedical_waste']

            for month in range(1, 13):
                month_name = datetime(1900, month, 1).strftime('%b')
                line_chart_data.append({
                    "month": month_name,
                    "biomedical_waste": biomedical_waste.get(month, 0)
                })
                
                
            if facility_id and facility_id.lower() != 'all':
                facility_biomedical_waste = (
                    Waste.objects.filter(user=user, facility__id=facility_id)
                    .values('facility__facility_name')
                    .annotate(total_biomedical_waste=Sum('biomedical_waste'))
                    .order_by('-total_biomedical_waste')
                )
            else:
                facility_biomedical_waste = (
                    Waste.objects.filter(user=user)
                    .values('facility__facility_name')
                    .annotate(total_biomedical_waste=Sum('biomedical_waste'))
                    .order_by('-total_biomedical_waste')
                )

            total_biomedical_waste = sum(entry['total_biomedical_waste'] for entry in facility_biomedical_waste)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_biomedical_waste'] / total_biomedical_waste * 100) if total_biomedical_waste else 0,
                }
                for entry in facility_biomedical_waste
            ]

            response_data = {
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': 'An error occurred while processing your request.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#Biomedical_overview_Card
class Biomedical_WasteViewCard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        year = request.GET.get('year', None)
        
        if year is None:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
           
            biomedical_waste_data = Waste.objects.filter(user=user, created_at__year=year)
            
            if facility_id and facility_id.lower() != 'all':
                biomedical_waste_data = biomedical_waste_data.filter(facility__id=facility_id)

            facility_biomedical_waste = (
                biomedical_waste_data
                .values('facility__facility_name')
                .annotate(total_biomedical_waste=Sum('biomedical_waste'))
                .order_by('-total_biomedical_waste')
            )

            facility_biomedical_waste_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "total_biomedical_waste": entry['total_biomedical_waste']
                }
                for entry in facility_biomedical_waste
            ]

            overall_biomedical_waste = biomedical_waste_data.aggregate(total=Sum('biomedical_waste'))['total'] or 0

            response_data = {
                'overall_biomedical_waste': overall_biomedical_waste,
                'facility_biomedical_waste': facility_biomedical_waste_data,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': 'An error occurred while processing your request.'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
#Liquid_discharge Overview 

class Liquid_DischargeOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        year = request.GET.get('year', None)
        
        if year is None:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if facility_id and facility_id.lower() != 'all':
                monthly_liquid_discharge = (
                    Waste.objects.filter(user=user, facility__id=facility_id, created_at__year=year)
                    .values('created_at__month')
                    .annotate(total_liquid_discharge=Sum('liquid_discharge'))
                    .order_by('created_at__month')
                )
            else:
                monthly_liquid_discharge = (
                    Waste.objects.filter(user=user, created_at__year=year)
                    .values('created_at__month')
                    .annotate(total_liquid_discharge=Sum('liquid_discharge'))
                    .order_by('created_at__month')
                )
                
            line_chart_data = []
            liquid_discharge = defaultdict(float)

            for entry in monthly_liquid_discharge:
                month_name = datetime(1900, entry['created_at__month'], 1).strftime('%b')
                liquid_discharge[entry['created_at__month']] = entry['total_liquid_discharge']

            for month in range(1, 13):
                month_name = datetime(1900, month, 1).strftime('%b')
                line_chart_data.append({
                    "month": month_name,
                    "liquid_discharge": liquid_discharge.get(month, 0)
                })
            
            if facility_id and facility_id.lower() != 'all':
                facility_liquid_discharge = (
                    Waste.objects.filter(user=user, facility__id=facility_id)
                    .values('facility__facility_name')
                    .annotate(total_liquid_discharge=Sum('liquid_discharge'))
                    .order_by('-total_liquid_discharge')
                )
            else:
                facility_liquid_discharge = (
                    Waste.objects.filter(user=user)
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
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': 'An error occurred while processing your request.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
#LiquidOverview Card

class Liquid_DischargeViewCard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        year = request.GET.get('year', None)
        
        if year is None:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
           
            liquid_discharge_data = Waste.objects.filter(user=user, created_at__year=year)
            
            if facility_id and facility_id.lower() != 'all':
                liquid_discharge_data = liquid_discharge_data.filter(facility__id=facility_id)

            facility_liquid_discharge = (
                liquid_discharge_data
                .values('facility__facility_name')
                .annotate(total_liquid_discharge=Sum('liquid_discharge'))
                .order_by('-total_liquid_discharge')
            )

            facility_liquid_discharge_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "total_liquid_discharge": entry['total_liquid_discharge']
                }
                for entry in facility_liquid_discharge
            ]

            overall_liquid_discharge = liquid_discharge_data.aggregate(total=Sum('liquid_discharge'))['total'] or 0

            response_data = {
                'overall_liquid_discharge': overall_liquid_discharge,
                'facility_liquid_discharge': facility_liquid_discharge_data,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': 'An error occurred while processing your request.'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#OtherOverview
class OthersOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        year = request.GET.get('year', None)
        
        if year is None:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if facility_id and facility_id.lower() != 'all':
                monthly_others = (
                    Waste.objects.filter(user=user, facility__id=facility_id, date__year=year)
                    .values('date__month')
                    .annotate(total_others=Sum('others'))
                    .order_by('date__month')
                )
            else:
                monthly_others = (
                    Waste.objects.filter(user=user, date__year=year)
                    .values('date__month')
                    .annotate(total_others=Sum('others'))
                    .order_by('date__month')
                )

            line_chart_data = []
            others = defaultdict(float)

            for entry in monthly_others:
                month_name = datetime(1900, entry['date__month'], 1).strftime('%b')
                others[entry['date__month']] = entry['total_others']

            for month in range(1, 13):
                month_name = datetime(1900, month, 1).strftime('%b')
                line_chart_data.append({
                    "month": month_name,
                    "others": others.get(month, 0)
                })

            if facility_id and facility_id.lower() != 'all':
                facility_others = (
                    Waste.objects.filter(user=user, facility__id=facility_id)
                    .values('facility__facility_name')
                    .annotate(total_others=Sum('others'))
                    .order_by('-total_others')
                )
            else:
                facility_others = (
                    Waste.objects.filter(user=user)
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
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': 'An error occurred while processing your request.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#OtherviewCard
class OthersViewCard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        year = request.GET.get('year', None)
        
        if year is None:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
           
            others_data = Waste.objects.filter(user=user, created_at__year=year)
            
            if facility_id and facility_id.lower() != 'all':
                others_data = others_data.filter(facility__id=facility_id)

            facility_others = (
                others_data
                .values('facility__facility_name')
                .annotate(total_others=Sum('others'))
                .order_by('-total_others')
            )

            facility_others_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "total_others": entry['total_others']
                }
                for entry in facility_others
            ]

            overall_others = others_data.aggregate(total=Sum('others'))['total'] or 0

            response_data = {
                'overall_others': overall_others,
                'facility_others': facility_others_data,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': 'An error occurred while processing your request.'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#Sent for RecycleOverview

class Waste_Sent_For_RecycleOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        year = request.GET.get('year', None)
        
        if year is None:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if facility_id and facility_id.lower() != 'all':
                monthly_sent_for_recycle = (
                    Waste.objects.filter(user=user, facility__id=facility_id, created_at__year=year)
                    .values('created_at__month')
                    .annotate(total_sent_for_recycle=Sum('sent_for_recycle'))
                    .order_by('created_at__month')
                )
            else:
                monthly_sent_for_recycle = (
                    Waste.objects.filter(user=user, created_at__year=year)
                    .values('created_at__month')
                    .annotate(total_sent_for_recycle=Sum('sent_for_recycle'))
                    .order_by('created_at__month')
                )

            line_chart_data = []
            sent_for_recycle = defaultdict(float)

            for entry in monthly_sent_for_recycle:
                month_name = datetime(1900, entry['created_at__month'], 1).strftime('%b')
                sent_for_recycle[entry['created_at__month']] = entry['total_sent_for_recycle']

            for month in range(1, 13):
                month_name = datetime(1900, month, 1).strftime('%b')
                line_chart_data.append({
                    "month": month_name,
                    "sent_for_recycle": sent_for_recycle.get(month, 0)
                })
            
            if facility_id and facility_id.lower() != 'all':
                facility_sent_for_recycle = (
                    Waste.objects.filter(user=user, facility__id=facility_id)
                    .values('facility__facility_name')
                    .annotate(total_sent_for_recycle=Sum('sent_for_recycle'))
                    .order_by('-total_sent_for_recycle')
                )
            else:
                facility_sent_for_recycle = (
                    Waste.objects.filter(user=user)
                    .values('facility__facility_name')
                    .annotate(total_sent_for_recycle=Sum('sent_for_recycle'))
                    .order_by('-total_sent_for_recycle')
                )

            total_sent_for_recycle = sum(entry['total_sent_for_recycle'] for entry in facility_sent_for_recycle)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_sent_for_recycle'] / total_sent_for_recycle * 100) if total_sent_for_recycle else 0,
                }
                for entry in facility_sent_for_recycle
            ]

            response_data = {
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': 'An error occurred while processing your request.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#Sent_for_recycleOverviewcard

class Sent_For_RecycleViewCard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        year = request.GET.get('year', None)
        
        if year is None:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
           
            sent_for_recycle_data = Waste.objects.filter(user=user, created_at__year=year)
            
            if facility_id and facility_id.lower() != 'all':
                sent_for_recycle_data = sent_for_recycle_data.filter(facility__id=facility_id)

            facility_sent_for_recycle = (
                sent_for_recycle_data
                .values('facility__facility_name')
                .annotate(total_sent_for_recycle=Sum('sent_for_recycle'))
                .order_by('-total_sent_for_recycle')
            )

            facility_sent_for_recycle_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "total_sent_for_recycle": entry['total_sent_for_recycle']
                }
                for entry in facility_sent_for_recycle
            ]

            overall_sent_for_recycle = sent_for_recycle_data.aggregate(total=Sum('sent_for_recycle'))['total'] or 0

            response_data = {
                'overall_sent_for_recycle': overall_sent_for_recycle,
                'facility_sent_for_recycle': facility_sent_for_recycle_data,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': 'An error occurred while processing your request.'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

#Sent to Landfills Overview
class Waste_Sent_For_LandFillOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        year = request.GET.get('year', None)
        
        if year is None:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if facility_id and facility_id.lower() != 'all':
                monthly_send_to_landfill = (
                    Waste.objects.filter(user=user, facility__id=facility_id, created_at__year=year)
                    .values('created_at__month')
                    .annotate(total_send_to_landfill=Sum('send_to_landfill'))
                    .order_by('created_at__month')
                )
            else:
                monthly_send_to_landfill = (
                    Waste.objects.filter(user=user, created_at__year=year)
                    .values('created_at__month')
                    .annotate(total_send_to_landfill=Sum('send_to_landfill'))
                    .order_by('created_at__month')
                )

            line_chart_data = []

            for entry in monthly_send_to_landfill:
                month_name = datetime(1900, entry['created_at__month'], 1).strftime('%b')
                line_chart_data.append({
                    "month": month_name,
                    "send_to_landfill": entry['total_send_to_landfill']
                    
                })

            line_chart_data = []
            send_to_landfill = defaultdict(float)

            for entry in monthly_send_to_landfill:
                month_name = datetime(1900, entry['created_at__month'], 1).strftime('%b')
                send_to_landfill[entry['created_at__month']] = entry['total_send_to_landfill']

            for month in range(1, 13):
                month_name = datetime(1900, month, 1).strftime('%b')
                line_chart_data.append({
                    "month": month_name,
                    "send_to_landfill": send_to_landfill.get(month, 0)
                })
            
            if facility_id and facility_id.lower() != 'all':
                facility_send_to_landfill = (
                    Waste.objects.filter(user=user, facility__id=facility_id)
                    .values('facility__facility_name')
                    .annotate(total_send_to_landfill=Sum('send_to_landfill'))
                    .order_by('-total_send_to_landfill')
                )
            else:
                facility_send_to_landfill = (
                    Waste.objects.filter(user=user)
                    .values('facility__facility_name')
                    .annotate(total_send_to_landfill=Sum('send_to_landfill'))
                    .order_by('-total_send_to_landfill')
                )

            total_send_to_landfill = sum(entry['total_send_to_landfill'] for entry in facility_send_to_landfill)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_send_to_landfill'] / total_send_to_landfill * 100) if total_send_to_landfill else 0,
                }
                for entry in facility_send_to_landfill
            ]

            response_data = {
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error occurred: {e}")
            return Response({'error': 'An error occurred while processing your request.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    
#Sent_for_LandfillCard
class Sent_For_LandFillViewCard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        year = request.GET.get('year', None)
        
        if year is None:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
           
            send_to_landfill_data = Waste.objects.filter(user=user, created_at__year=year)
            
            if facility_id and facility_id.lower() != 'all':
                send_to_landfill_data = send_to_landfill_data.filter(facility__id=facility_id)

            facility_send_to_landfill = (
                send_to_landfill_data
                .values('facility__facility_name')
                .annotate(total_send_to_landfill=Sum('send_to_landfill'))
                .order_by('-total_send_to_landfill')
            )

            facility_send_to_landfill_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "total_send_to_landfill": entry['total_send_to_landfill']
                }
                for entry in facility_send_to_landfill
            ]

            overall_send_to_landfill = send_to_landfill_data.aggregate(total=Sum('send_to_landfill'))['total'] or 0

            response_data = {
                'overall_send_to_landfill': overall_send_to_landfill,
                'facility_send_to_landfill': facility_send_to_landfill_data,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error occurred: {e}")
            return Response({'error': 'An error occurred while processing your request.'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
#WasteStackedOverview

class StackedWasteOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        year = request.GET.get('year', None)
        
        if year is None:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            waste_types = [
                'food_waste', 'solid_waste', 'e_waste', 'biomedical_waste',
                'liquid_discharge', 'others', 'sent_for_recycle', 'send_to_landfill'
            ]
            monthly_data = {month: {waste_type: 0 for waste_type in waste_types} for month in range(1, 13)}

            for waste_type in waste_types:
                if facility_id and facility_id.lower() != 'all':
                    monthly_waste = (
                        Waste.objects.filter(user=user, facility__id=facility_id, created_at__year=year)
                        .values('created_at__month')
                        .annotate(total=Coalesce(Sum(waste_type, output_field=FloatField()), Value(0, output_field=FloatField())))
                        .order_by('created_at__month')
                    )
                else:
                    monthly_waste = (
                        Waste.objects.filter(user=user, created_at__year=year)
                        .values('created_at__month')
                        .annotate(total=Coalesce(Sum(waste_type, output_field=FloatField()), Value(0, output_field=FloatField())))
                        .order_by('created_at__month')
                    )

                for entry in monthly_waste:
                    month = entry['created_at__month']
                    monthly_data[month][waste_type] = entry['total']

            stacked_bar_data = []
            for month in range(1, 13):
                month_name = datetime(1900, month, 1).strftime('%b')
                stacked_bar_data.append({
                    "month": month_name,
                    **monthly_data[month]
                })

            response_data = {
                "stacked_bar_data": stacked_bar_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error occurred: {e}") 
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
  
#Waste overview Donut Chart
class WasteOverallDonutChartView(APIView):
    
#Sent to LandfillOverview
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        year = request.GET.get('year', None)
        facility_id = request.GET.get('facility_id', None)
        
        if year is None:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            waste_types = [
                'food_waste', 'solid_waste', 'e_waste', 'biomedical_waste', 'others'
            ]

            queryset = Waste.objects.filter(user=user, created_at__year=year)

            if facility_id and facility_id.lower() != 'all':
                queryset = queryset.filter(facility__id=facility_id)

            waste_totals = queryset.aggregate(
                food_waste_total=Coalesce(Sum(Cast('food_waste', FloatField())), 0.0),
                solid_waste_total=Coalesce(Sum(Cast('solid_waste', FloatField())), 0.0),
                e_waste_total=Coalesce(Sum(Cast('e_waste', FloatField())), 0.0),
                biomedical_waste_total=Coalesce(Sum(Cast('biomedical_waste', FloatField())), 0.0),
                others_total=Coalesce(Sum(Cast('others', FloatField())), 0.0)
            )

            overall_total = sum(waste_totals.values())

            if overall_total == 0:
                return Response({'error': 'No waste data available for the selected year and facility.'}, status=status.HTTP_204_NO_CONTENT)

            # Calculate percentages
            waste_percentages = {
                'food_waste': (waste_totals['food_waste_total'] / overall_total) * 100,
                'solid_waste': (waste_totals['solid_waste_total'] / overall_total) * 100,
                'e_waste': (waste_totals['e_waste_total'] / overall_total) * 100,
                'biomedical_waste': (waste_totals['biomedical_waste_total'] / overall_total) * 100,
                'others': (waste_totals['others_total'] / overall_total) * 100,
            }

            # Format response data
            response_data = {
                "year": year,
                "facility_id": facility_id,
                "waste_percentages": waste_percentages
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error occurred: {e}")
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
 #       
class SentToLandfillOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        year = request.GET.get('year', None)
        facility_id = request.GET.get('facility_id', None)
        
        if year is None:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            overall_total_fields = [
                'food_waste', 'solid_waste', 'e_waste', 'biomedical_waste', 'others'
            ]

            queryset = Waste.objects.filter(user=user, created_at__year=year)

            if facility_id and facility_id.lower() != 'all':
                queryset = queryset.filter(facility__id=facility_id)

            sent_to_landfill_total = queryset.aggregate(
                total=Coalesce(Sum(Cast('send_to_landfill', FloatField())), 0.0)
            )['total']

            overall_total = sum(
                queryset.aggregate(
                    **{f"{waste_type}_total": Coalesce(Sum(Cast(waste_type, FloatField())), 0.0)
                       for waste_type in overall_total_fields}
                ).values()
            )

            remaining_waste_total = overall_total - sent_to_landfill_total

            if overall_total == 0:
                return Response({'error': 'No waste data available for the selected year and facility.'}, status=status.HTTP_204_NO_CONTENT)

            # Calculate percentages
            landfill_percentage = (sent_to_landfill_total / overall_total) * 100
            remaining_percentage = (remaining_waste_total / overall_total) * 100

            # Format response data
            response_data = {
                "year": year,
                "facility_id": facility_id,
                "landfill_percentage": landfill_percentage,
                "remaining_percentage": remaining_percentage
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error occurred: {e}")
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#Sent to Recycle
class SentToRecycledOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        year = request.GET.get('year', None)
        facility_id = request.GET.get('facility_id', None)
        
        if year is None:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            overall_total_fields = [
                'food_waste', 'solid_waste', 'e_waste', 'biomedical_waste', 'others'
            ]

            queryset = Waste.objects.filter(user=user, created_at__year=year)
            
            if facility_id and facility_id.lower() != 'all':
                queryset = queryset.filter(facility__id=facility_id)

            # Calculate total for 'sent_for_recycle'
            sent_for_recycle_total = queryset.aggregate(
                total=Coalesce(Sum(Cast('sent_for_recycle', FloatField())), 0.0)
            )['total']

            # Calculate total for other waste fields
            overall_total = sum(
                queryset.aggregate(
                    **{f"{waste_type}_total": Coalesce(Sum(Cast(waste_type, FloatField())), 0.0)
                       for waste_type in overall_total_fields}
                ).values()
            )

            # Calculate remaining waste by excluding 'sent_for_recycle'
            remaining_waste_total = overall_total - sent_for_recycle_total
            
            # overall_total += sent_for_recycle_total

            if overall_total == 0:
                return Response({'error': 'No waste data available for the selected year and facility.'}, status=status.HTTP_204_NO_CONTENT)

            # Calculate percentages
            recycle_percentage = (sent_for_recycle_total / overall_total) * 100
            remaining_percentage = (remaining_waste_total / overall_total) * 100

            # Format response data
            response_data = {
                "year": year,
                "facility_id": facility_id,
                "recycle_percentage": recycle_percentage,
                "remaining_percentage": remaining_percentage
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error occurred: {e}")
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
'''Waste Overviewgraphs and Individual Line charts and donut charts Ends'''


'''Energy  Overview Cards ,Graphs and Individual line charts and donut charts Starts'''
#HVAC CardOverView
class HVAC_CardOverview(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        user = request.user
        year = request.GET.get('year',None)
        facility_id = request.GET.get('facility_id',None)
        
        if year is None:
            return Response({'error':'Year Parameter is Required'},status=status.HTTP_400_BAD_REQUEST)
        
        try:
            year = int(year)
        except(TypeError,ValueError):
            return Response({'error':'Invalid Year Parameter'},status=status.HTTP_400_BAD_REQUEST)
        
        try:
            HVAC_data = Energy.objects.filter(user=user,created_at__year=year)
            
            if facility_id and facility_id.lower() != 'all':
                HVAC_data = HVAC_data.filter(facility_id = facility_id)
            
            facility_HVAC = (
                HVAC_data
                .values('facility__facility_name')
                .annotate(total_hvac=Sum('hvac'))
                .order_by('-total_hvac')
            )
            facility_HVAC_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "total_hvac": entry['total_hvac']
                }
                for entry in facility_HVAC
            ]
            overall_hvac = HVAC_data.aggregate(total=Sum('hvac'))['total'] or 0

            response_data = {
                'overall_hvac': overall_hvac,
                'facility_hvac': facility_HVAC_data,
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': 'An error occurred while processing your request.'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#HVAC Line Charts and Donut Chart
class HVACOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        year = request.GET.get('year', None)
        
        if year is None:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Query to get monthly HVAC data
            if facility_id and facility_id.lower() != 'all':
                monthly_hvac = (
                    Energy.objects.filter(user=user, facility__id=facility_id, created_at__year=year)
                    .values('created_at__month')
                    .annotate(total_hvac=Sum('hvac'))
                    .order_by('created_at__month')
                )
            else:
                monthly_hvac = (
                    Energy.objects.filter(user=user, created_at__year=year)
                    .values('created_at__month')
                    .annotate(total_hvac=Sum('hvac'))
                    .order_by('created_at__month')
                )

            line_chart_data = []
            hvac_data = defaultdict(float)

            for entry in monthly_hvac:
                month_name = datetime(1900, entry['created_at__month'], 1).strftime('%b')
                hvac_data[entry['created_at__month']] = entry['total_hvac']

            for month in range(1, 13):
                month_name = datetime(1900, month, 1).strftime('%b')
                line_chart_data.append({
                    "month": month_name,
                    "hvac": hvac_data.get(month, 0)
                })

            # Query for facility-wise HVAC data
            if facility_id and facility_id.lower() != 'all':
                facility_hvac = (
                    Energy.objects.filter(user=user, facility__id=facility_id)
                    .values('facility__facility_name')
                    .annotate(total_hvac=Sum('hvac'))
                    .order_by('-total_hvac')
                )
            else:
                facility_hvac = (
                    Energy.objects.filter(user=user)
                    .values('facility__facility_name')
                    .annotate(total_hvac=Sum('hvac'))
                    .order_by('-total_hvac')
                )

            total_hvac = sum(entry['total_hvac'] for entry in facility_hvac) or 0
            
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_hvac'] / total_hvac * 100) if total_hvac else 0,
                }
                for entry in facility_hvac
            ]

            response_data = {
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': 'An error occurred while processing your request.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    
  
  

'''Energy  Overview Cards ,Graphs and Individual line charts and donut charts Ends'''
