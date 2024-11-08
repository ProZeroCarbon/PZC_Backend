
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
    filter_backends = [DjangoFilterBackend]
    filterset_class = WasteFilter

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', 'all')
        if facility_id and facility_id.lower() != 'all':
            waste_data = Waste.objects.filter(user=user, facility__facility_id=facility_id)
        else:
            waste_data = Waste.objects.filter(user=user)
    
        filtered_waste_data = WasteFilter(request.GET, queryset=waste_data).qs
        waste_serializer = WasteSerializer(filtered_waste_data, many=True)
        
        # Calculate the overall waste total
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
class WasteEditView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, facility_id):
        try:
            # Lookup Waste by related Facility's facility_id and the authenticated user
            waste = Waste.objects.get(facility__facility_id=facility_id, user=request.user)
        except Waste.DoesNotExist:
            return Response({"error": "Waste data not found."}, status=status.HTTP_404_NOT_FOUND)

        # Update the waste data
        serializer = WasteCreateSerializer(waste, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Waste data updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#Deletewaste
class WasteDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, facility_id):
        try:
           waste = Waste.objects.get(facility__facility_id=facility_id, user=request.user)
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
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        if not year:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Monthly food waste query
            filters = {
                'user': user,
                'DatePicker__year': year,
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__facility_location__icontains'] = facility_location

            monthly_food_waste = (
                Waste.objects.filter(**filters)
                .values('DatePicker__month')
                .annotate(total_food_waste=Sum('food_waste'))
                .order_by('DatePicker__month')
            )

            # Prepare line chart data
            line_chart_data = []
            food_waste = defaultdict(float)

            for entry in monthly_food_waste:
                month_name = datetime(1900, entry['DatePicker__month'], 1).strftime('%b')
                food_waste[entry['DatePicker__month']] = entry['total_food_waste']

            for month in range(1, 13):
                month_name = datetime(1900, month, 1).strftime('%b')
                line_chart_data.append({
                    "month": month_name,
                    "food_waste": food_waste.get(month, 0)
                })

            # Facility-wise food waste query
            facility_filters = {'user': user}
            if facility_id and facility_id.lower() != 'all':
                facility_filters['facility__facility_id'] = facility_id
            facility_food_waste = (
                Waste.objects.filter(**facility_filters)
                .values('facility__facility_name')
                .annotate(total_food_waste=Sum('food_waste'))
                .order_by('-total_food_waste')
            )

            # Prepare donut chart data
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
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
#foodWaste Overview Card
class FoodWasteViewCard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        # Ensure year is provided and valid
        if not year:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Base query for all food waste data for the given user and year
            food_waste_data = Waste.objects.filter(user=user, DatePicker__year=year)

            # Filter by facility_id if provided and valid
            if facility_id and facility_id.lower() != 'all':
                if not Facility.objects.filter(facility_id=facility_id).exists():
                    return Response({'error': 'Invalid facility ID.'}, status=status.HTTP_400_BAD_REQUEST)
                food_waste_data = food_waste_data.filter(facility__facility_id=facility_id)

            # Filter by facility_location if provided
            if facility_location:
                food_waste_data = food_waste_data.filter(facility__facility_location__icontains=facility_location)

            # Aggregate food waste by facility
            facility_food_waste = (
                food_waste_data
                .values('facility__facility_name')
                .annotate(total_food_waste=Sum('food_waste'))
                .order_by('-total_food_waste')
            )

            # Prepare the response data for facility-wise food waste
            facility_food_waste_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "total_food_waste": entry['total_food_waste']
                }
                for entry in facility_food_waste
            ]

            # Calculate overall food waste
            overall_food_waste = food_waste_data.aggregate(total=Sum('food_waste'))['total'] or 0

            # Return the data as response
            response_data = {
                'overall_food_waste': overall_food_waste,
                'facility_food_waste': facility_food_waste_data,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Log the error for debugging purposes
            print(f"An error occurred: {e}")
            return Response({'error': 'An error occurred while processing your request.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



#Solid Waste overview
class SolidWasteOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        if not year:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Monthly food waste query
            filters = {
                'user': user,
                'DatePicker__year': year,
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__facility_location__icontains'] = facility_location

            monthly_solid_Waste = (
                Waste.objects.filter(**filters)
                .values('DatePicker__month')
                .annotate(total_solid_Waste=Sum('solid_Waste'))
                .order_by('DatePicker__month')
            )

            # Prepare line chart data
            line_chart_data = []
            solid_Waste = defaultdict(float)

            for entry in monthly_solid_Waste:
                month_name = datetime(1900, entry['DatePicker__month'], 1).strftime('%b')
                solid_Waste[entry['DatePicker__month']] = entry['total_solid_Waste']

            for month in range(1, 13):
                month_name = datetime(1900, month, 1).strftime('%b')
                line_chart_data.append({
                    "month": month_name,
                    "solid_Waste": solid_Waste.get(month, 0)
                })

            # Facility-wise food waste query
            facility_filters = {'user': user}
            if facility_id and facility_id.lower() != 'all':
                facility_filters['facility__facility_id'] = facility_id
            facility_solid_Waste = (
                Waste.objects.filter(**facility_filters)
                .values('facility__facility_name')
                .annotate(total_solid_Waste=Sum('solid_Waste'))
                .order_by('-total_solid_Waste')
            )

            # Prepare donut chart data
            total_solid_Waste = sum(entry['total_solid_Waste'] for entry in facility_solid_Waste)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_solid_Waste'] / total_solid_Waste * 100) if total_solid_Waste else 0,
                }
                for entry in facility_solid_Waste
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


#Solid Waste overview Card
class SolidWasteViewCard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        # Ensure year is provided and valid
        if not year:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Base query for all food waste data for the given user and year
            solid_Waste_data = Waste.objects.filter(user=user, DatePicker__year=year)

            # Filter by facility_id if provided and valid
            if facility_id and facility_id.lower() != 'all':
                if not Facility.objects.filter(facility_id=facility_id).exists():
                    return Response({'error': 'Invalid facility ID.'}, status=status.HTTP_400_BAD_REQUEST)
                solid_Waste_data = solid_Waste_data.filter(facility__facility_id=facility_id)

            # Filter by facility_location if provided
            if facility_location:
                solid_Waste_data = solid_Waste_data.filter(facility__facility_location__icontains=facility_location)

            # Aggregate food waste by facility
            facility_solid_Waste = (
                solid_Waste_data
                .values('facility__facility_name')
                .annotate(total_solid_Waste=Sum('solid_Waste'))
                .order_by('-total_solid_Waste')
            )

            # Prepare the response data for facility-wise food waste
            facility_solid_Waste_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "total_solid_Waste": entry['total_solid_Waste']
                }
                for entry in facility_solid_Waste
            ]

            # Calculate overall food waste
            overall_solid_Waste = solid_Waste_data.aggregate(total=Sum('solid_Waste'))['total'] or 0

            # Return the data as response
            response_data = {
                'overall_solid_Waste': overall_solid_Waste,
                'facility_solid_Waste': facility_solid_Waste_data,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Log the error for debugging purposes
            print(f"An error occurred: {e}")
            return Response({'error': 'An error occurred while processing your request.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



#e_waste overview view
class E_WasteOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        if not year:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Monthly food waste query
            filters = {
                'user': user,
                'DatePicker__year': year,
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__facility_location__icontains'] = facility_location

            monthly_E_Waste = (
                Waste.objects.filter(**filters)
                .values('DatePicker__month')
                .annotate(total_E_Waste=Sum('E_Waste'))
                .order_by('DatePicker__month')
            )

            # Prepare line chart data
            line_chart_data = []
            E_Waste = defaultdict(float)

            for entry in monthly_E_Waste:
                month_name = datetime(1900, entry['DatePicker__month'], 1).strftime('%b')
                E_Waste[entry['DatePicker__month']] = entry['total_E_Waste']

            for month in range(1, 13):
                month_name = datetime(1900, month, 1).strftime('%b')
                line_chart_data.append({
                    "month": month_name,
                    "E_Waste": E_Waste.get(month, 0)
                })

            # Facility-wise food waste query
            facility_filters = {'user': user}
            if facility_id and facility_id.lower() != 'all':
                facility_filters['facility__facility_id'] = facility_id
            facility_E_Waste = (
                Waste.objects.filter(**facility_filters)
                .values('facility__facility_name')
                .annotate(total_E_Waste=Sum('E_Waste'))
                .order_by('-total_E_Waste')
            )

            # Prepare donut chart data
            total_E_Waste = sum(entry['total_E_Waste'] for entry in facility_E_Waste)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_E_Waste'] / total_E_Waste * 100) if total_E_Waste else 0,
                }
                for entry in facility_E_Waste
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
       
#E-waste Overview Card
class E_WasteViewCard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        # Ensure year is provided and valid
        if not year:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Base query for all food waste data for the given user and year
            E_Waste_data = Waste.objects.filter(user=user, DatePicker__year=year)

            # Filter by facility_id if provided and valid
            if facility_id and facility_id.lower() != 'all':
                if not Facility.objects.filter(facility_id=facility_id).exists():
                    return Response({'error': 'Invalid facility ID.'}, status=status.HTTP_400_BAD_REQUEST)
                E_Waste_data = E_Waste_data.filter(facility__facility_id=facility_id)

            # Filter by facility_location if provided
            if facility_location:
                E_Waste_data = E_Waste_data.filter(facility__facility_location__icontains=facility_location)

            # Aggregate food waste by facility
            facility_E_Waste = (
                E_Waste_data
                .values('facility__facility_name')
                .annotate(total_E_Waste=Sum('E_Waste'))
                .order_by('-total_E_Waste')
            )

            # Prepare the response data for facility-wise food waste
            facility_E_Waste_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "total_E_Waste": entry['total_E_Waste']
                }
                for entry in facility_E_Waste
            ]

            # Calculate overall food waste
            overall_E_Waste = E_Waste_data.aggregate(total=Sum('E_Waste'))['total'] or 0

            # Return the data as response
            response_data = {
                'overall_E_Waste': overall_E_Waste,
                'facility_E_Waste': facility_E_Waste_data,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Log the error for debugging purposes
            print(f"An error occurred: {e}")
            return Response({'error': 'An error occurred while processing your request.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#biomedical_waste Overview
class Biomedical_WasteOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        if not year:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Monthly food waste query
            filters = {
                'user': user,
                'DatePicker__year': year,
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__facility_location__icontains'] = facility_location

            monthly_Biomedical_waste = (
                Waste.objects.filter(**filters)
                .values('DatePicker__month')
                .annotate(total_Biomedical_waste=Sum('Biomedical_waste'))
                .order_by('DatePicker__month')
            )

            # Prepare line chart data
            line_chart_data = []
            Biomedical_waste = defaultdict(float)

            for entry in monthly_Biomedical_waste:
                month_name = datetime(1900, entry['DatePicker__month'], 1).strftime('%b')
                Biomedical_waste[entry['DatePicker__month']] = entry['total_Biomedical_waste']

            for month in range(1, 13):
                month_name = datetime(1900, month, 1).strftime('%b')
                line_chart_data.append({
                    "month": month_name,
                    "Biomedical_waste": Biomedical_waste.get(month, 0)
                })

            # Facility-wise food waste query
            facility_filters = {'user': user}
            if facility_id and facility_id.lower() != 'all':
                facility_filters['facility__facility_id'] = facility_id
            facility_Biomedical_waste = (
                Waste.objects.filter(**facility_filters)
                .values('facility__facility_name')
                .annotate(total_Biomedical_waste=Sum('Biomedical_waste'))
                .order_by('-total_Biomedical_waste')
            )

            # Prepare donut chart data
            total_Biomedical_waste = sum(entry['total_Biomedical_waste'] for entry in facility_Biomedical_waste)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_Biomedical_waste'] / total_Biomedical_waste * 100) if total_Biomedical_waste else 0,
                }
                for entry in facility_Biomedical_waste
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


#Biomedical_overview_Card
class Biomedical_WasteViewCard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        # Ensure year is provided and valid
        if not year:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Base query for all food waste data for the given user and year
            Biomedical_waste = Waste.objects.filter(user=user, DatePicker__year=year)

            # Filter by facility_id if provided and valid
            if facility_id and facility_id.lower() != 'all':
                if not Facility.objects.filter(facility_id=facility_id).exists():
                    return Response({'error': 'Invalid facility ID.'}, status=status.HTTP_400_BAD_REQUEST)
                Biomedical_waste = Biomedical_waste.filter(facility__facility_id=facility_id)

            # Filter by facility_location if provided
            if facility_location:
                Biomedical_waste = Biomedical_waste.filter(facility__facility_location__icontains=facility_location)

            # Aggregate food waste by facility
            facility_Biomedical_waste = (
                Biomedical_waste
                .values('facility__facility_name')
                .annotate(total_Biomedical_waste=Sum('Biomedical_waste'))
                .order_by('-total_Biomedical_waste')
            )

            # Prepare the response data for facility-wise food waste
            facility_Biomedical_waste = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "total_Biomedical_waste": entry['total_Biomedical_waste']
                }
                for entry in facility_Biomedical_waste
            ]

            # Calculate overall food waste
            overall_Biomedical_waste = Biomedical_waste.aggregate(total=Sum('Biomedical_waste'))['total'] or 0

            # Return the data as response
            response_data = {
                'overall_Biomedical_waste': overall_Biomedical_waste,
                'facility_Biomedical_waste': facility_Biomedical_waste,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Log the error for debugging purposes
            print(f"An error occurred: {e}")
            return Response({'error': 'An error occurred while processing your request.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
        
#Liquid_discharge Overview 

class Liquid_DischargeOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        if not year:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Monthly food waste query
            filters = {
                'user': user,
                'DatePicker__year': year,
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__facility_location__icontains'] = facility_location

            monthly_liquid_discharge = (
                Waste.objects.filter(**filters)
                .values('DatePicker__month')
                .annotate(total_liquid_discharge=Sum('liquid_discharge'))
                .order_by('DatePicker__month')
            )

            # Prepare line chart data
            line_chart_data = []
            liquid_discharge = defaultdict(float)

            for entry in monthly_liquid_discharge:
                month_name = datetime(1900, entry['DatePicker__month'], 1).strftime('%b')
                liquid_discharge[entry['DatePicker__month']] = entry['total_liquid_discharge']

            for month in range(1, 13):
                month_name = datetime(1900, month, 1).strftime('%b')
                line_chart_data.append({
                    "month": month_name,
                    "liquid_discharge": liquid_discharge.get(month, 0)
                })

            # Facility-wise food waste query
            facility_filters = {'user': user}
            if facility_id and facility_id.lower() != 'all':
                facility_filters['facility__facility_id'] = facility_id
            facility_liquid_discharge = (
                Waste.objects.filter(**facility_filters)
                .values('facility__facility_name')
                .annotate(total_liquid_discharge=Sum('liquid_discharge'))
                .order_by('-total_liquid_discharge')
            )

            # Prepare donut chart data
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
            return Response(
                {'error': f'An error occurred while processing your request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )  
#LiquidOverview Card

class Liquid_DischargeViewCard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        # Ensure year is provided and valid
        if not year:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Base query for all food waste data for the given user and year
            liquid_discharge = Waste.objects.filter(user=user, DatePicker__year=year)

            # Filter by facility_id if provided and valid
            if facility_id and facility_id.lower() != 'all':
                if not Facility.objects.filter(facility_id=facility_id).exists():
                    return Response({'error': 'Invalid facility ID.'}, status=status.HTTP_400_BAD_REQUEST)
                liquid_discharge = liquid_discharge.filter(facility__facility_id=facility_id)

            # Filter by facility_location if provided
            if facility_location:
                liquid_discharge = liquid_discharge.filter(facility__facility_location__icontains=facility_location)

            # Aggregate food waste by facility
            facility_liquid_discharge = (
                liquid_discharge
                .values('facility__facility_name')
                .annotate(total_liquid_discharge=Sum('liquid_discharge'))
                .order_by('-total_liquid_discharge')
            )

            # Prepare the response data for facility-wise food waste
            facility_liquid_discharge = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "total_liquid_discharge": entry['total_liquid_discharge']
                }
                for entry in facility_liquid_discharge
            ]

            # Calculate overall food waste
            overall_liquid_discharge = liquid_discharge.aggregate(total=Sum('liquid_discharge'))['total'] or 0

            # Return the data as response
            response_data = {
                'overall_liquid_discharge': overall_liquid_discharge,
                'facility_liquid_discharge': facility_liquid_discharge,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Log the error for debugging purposes
            print(f"An error occurred: {e}")
            return Response({'error': 'An error occurred while processing your request.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
#OtherOverview
class OthersOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        if not year:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            filters = {
                'user': user,
                'DatePicker__year': year,
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__facility_location__icontains'] = facility_location

            monthly_other_waste = (
                Waste.objects.filter(**filters)
                .values('DatePicker__month')
                .annotate(total_other_waste=Sum('other_waste'))
                .order_by('DatePicker__month')
            )

            # Prepare line chart data
            line_chart_data = []
            other_waste = defaultdict(float)

            for entry in monthly_other_waste:
                month_name = datetime(1900, entry['DatePicker__month'], 1).strftime('%b')
                other_waste[entry['DatePicker__month']] = entry['total_other_waste']

            for month in range(1, 13):
                month_name = datetime(1900, month, 1).strftime('%b')
                line_chart_data.append({
                    "month": month_name,
                    "other_waste": other_waste.get(month, 0)
                })

            # Facility-wise food waste query
            facility_filters = {'user': user}
            if facility_id and facility_id.lower() != 'all':
                facility_filters['facility__facility_id'] = facility_id
            facility_other_waste = (
                Waste.objects.filter(**facility_filters)
                .values('facility__facility_name')
                .annotate(total_other_waste=Sum('other_waste'))
                .order_by('-total_other_waste')
            )

            # Prepare donut chart data
            total_other_waste = sum(entry['total_other_waste'] for entry in facility_other_waste)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_other_waste'] / total_other_waste * 100) if total_other_waste else 0,
                }
                for entry in facility_other_waste
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
#OtherviewCard
class OthersViewCard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        # Ensure year is provided and valid
        if not year:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Base query for all food waste data for the given user and year
            other_waste = Waste.objects.filter(user=user, DatePicker__year=year)

            # Filter by facility_id if provided and valid
            if facility_id and facility_id.lower() != 'all':
                if not Facility.objects.filter(facility_id=facility_id).exists():
                    return Response({'error': 'Invalid facility ID.'}, status=status.HTTP_400_BAD_REQUEST)
                other_waste = other_waste.filter(facility__facility_id=facility_id)

            # Filter by facility_location if provided
            if facility_location:
                other_waste = other_waste.filter(facility__facility_location__icontains=facility_location)

            # Aggregate food waste by facility
            facility_other_waste = (
                other_waste
                .values('facility__facility_name')
                .annotate(total_other_waste=Sum('other_waste'))
                .order_by('-total_other_waste')
            )

            # Prepare the response data for facility-wise food waste
            facility_other_waste = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "total_other_waste": entry['total_other_waste']
                }
                for entry in facility_other_waste
            ]

            # Calculate overall food waste
            overall_other_waste = other_waste.aggregate(total=Sum('other_waste'))['total'] or 0

            # Return the data as response
            response_data = {
                'overall_other_waste': overall_other_waste,
                'facility_other_waste': facility_other_waste,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Log the error for debugging purposes
            print(f"An error occurred: {e}")
            return Response({'error': 'An error occurred while processing your request.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
#Sent for RecycleOverview
class Waste_Sent_For_RecycleOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        if not year:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            filters = {
                'user': user,
                'DatePicker__year': year,
            }
            if facility_id and facility_id.lower() != 'all':
                filters['facility__facility_id'] = facility_id
            if facility_location:
                filters['facility__facility_location__icontains'] = facility_location

            monthly_Recycle_waste = (
                Waste.objects.filter(**filters)
                .values('DatePicker__month')
                .annotate(total_Recycle_waste=Sum('Recycle_waste'))
                .order_by('DatePicker__month')
            )

            # Prepare line chart data
            line_chart_data = []
            Recycle_waste = defaultdict(float)

            for entry in monthly_Recycle_waste:
                month_name = datetime(1900, entry['DatePicker__month'], 1).strftime('%b')
                Recycle_waste[entry['DatePicker__month']] = entry['total_Recycle_waste']

            for month in range(1, 13):
                month_name = datetime(1900, month, 1).strftime('%b')
                line_chart_data.append({
                    "month": month_name,
                    "Recycle_waste": Recycle_waste.get(month, 0)
                })

            # Facility-wise food waste query
            facility_filters = {'user': user}
            if facility_id and facility_id.lower() != 'all':
                facility_filters['facility__facility_id'] = facility_id
            facility_Recycle_waste = (
                Waste.objects.filter(**facility_filters)
                .values('facility__facility_name')
                .annotate(total_Recycle_waste=Sum('Recycle_waste'))
                .order_by('-total_Recycle_waste')
            )

            # Prepare donut chart data
            total_Recycle_waste = sum(entry['total_Recycle_waste'] for entry in facility_Recycle_waste)
            donut_chart_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "percentage": (entry['total_Recycle_waste'] / total_Recycle_waste * 100) if total_Recycle_waste else 0,
                }
                for entry in facility_Recycle_waste
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

        
#Sent_for_recycleOverviewcard
class Sent_For_RecycleViewCard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        # Ensure year is provided and valid
        if not year:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Base query for all food waste data for the given user and year
            Recycle_waste = Waste.objects.filter(user=user, DatePicker__year=year)

            # Filter by facility_id if provided and valid
            if facility_id and facility_id.lower() != 'all':
                if not Facility.objects.filter(facility_id=facility_id).exists():
                    return Response({'error': 'Invalid facility ID.'}, status=status.HTTP_400_BAD_REQUEST)
                Recycle_waste = Recycle_waste.filter(facility__facility_id=facility_id)

            # Filter by facility_location if provided
            if facility_location:
                Recycle_waste = Recycle_waste.filter(facility__facility_location__icontains=facility_location)

            # Aggregate food waste by facility
            facility_Recycle_waste = (
                Recycle_waste
                .values('facility__facility_name')
                .annotate(total_Recycle_waste=Sum('Recycle_waste'))
                .order_by('-total_Recycle_waste')
            )

            # Prepare the response data for facility-wise food waste
            facility_Recycle_waste = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "total_Recycle_waste": entry['total_Recycle_waste']
                }
                for entry in facility_Recycle_waste
            ]

            # Calculate overall food waste
            overall_Recycle_waste = Recycle_waste.aggregate(total=Sum('Recycle_waste'))['total'] or 0

            # Return the data as response
            response_data = {
                'overall_Recycle_waste': overall_Recycle_waste,
                'facility_Recycle_waste': facility_Recycle_waste,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Log the error for debugging purposes
            print(f"An error occurred: {e}")
            return Response({'error': 'An error occurred while processing your request.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Sent to Landfills Overview
class Waste_Sent_For_LandFillOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        year = request.GET.get('year', None)
        facility_location = request.GET.get('facility_location', None)
        
        
        if year is None:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if facility_id and facility_id.lower() != 'all':
                monthly_Landfill_waste = (
                    Waste.objects.filter(user=user, facility__id=facility_id, DatePicker__year=year,facility__facility_location__icontains=facility_location)
                    .values('DatePicker__month')
                    .annotate(total_Landfill_waste=Sum('Landfill_waste'))
                    .order_by('DatePicker__month')
                )
            else:
                monthly_Landfill_waste = (
                    Waste.objects.filter(user=user, DatePicker__year=year)
                    .values('DatePicker__month')
                    .annotate(total_Landfill_waste=Sum('Landfill_waste'))
                    .order_by('DatePicker__month')
                )

            line_chart_data = []

            for entry in monthly_Landfill_waste:
                month_name = datetime(1900, entry['DatePicker__month'], 1).strftime('%b')
                line_chart_data.append({
                    "month": month_name,
                    "Landfill_waste": entry['total_Landfill_waste']
                    
                })

            line_chart_data = []
            Landfill_waste = defaultdict(float)

            for entry in monthly_Landfill_waste:
                month_name = datetime(1900, entry['DatePicker__month'], 1).strftime('%b')
                Landfill_waste[entry['DatePicker__month']] = entry['total_Landfill_waste']

            for month in range(1, 13):
                month_name = datetime(1900, month, 1).strftime('%b')
                line_chart_data.append({
                    "month": month_name,
                    "Landfill_waste": Landfill_waste.get(month, 0)
                })
            
            if facility_id and facility_id.lower() != 'all':
                facility_Landfill_waste = (
                    Waste.objects.filter(user=user, facility__id=facility_id)
                    .values('facility__facility_name')
                    .annotate(total_Landfill_waste=Sum('Landfill_waste'))
                    .order_by('-total_Landfill_waste')
                )
            else:
                facility_Landfill_waste = (
                    Waste.objects.filter(user=user)
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
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        # Ensure year is provided and valid
        if not year:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Base query for all food waste data for the given user and year
            Landfill_waste = Waste.objects.filter(user=user, DatePicker__year=year)

            # Filter by facility_id if provided and valid
            if facility_id and facility_id.lower() != 'all':
                if not Facility.objects.filter(facility_id=facility_id).exists():
                    return Response({'error': 'Invalid facility ID.'}, status=status.HTTP_400_BAD_REQUEST)
                Landfill_waste = Landfill_waste.filter(facility__facility_id=facility_id)

            # Filter by facility_location if provided
            if facility_location:
                Landfill_waste = Landfill_waste.filter(facility__facility_location__icontains=facility_location)

            # Aggregate food waste by facility
            facility_Landfill_waste = (
                Landfill_waste
                .values('facility__facility_name')
                .annotate(total_Landfill_waste=Sum('Landfill_waste'))
                .order_by('-total_Landfill_waste')
            )

            # Prepare the response data for facility-wise food waste
            facility_Landfill_waste = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "total_Landfill_waste": entry['total_Landfill_waste']
                }
                for entry in facility_Landfill_waste
            ]

            # Calculate overall food waste
            overall_Landfill_waste = Landfill_waste.aggregate(total=Sum('Landfill_waste'))['total'] or 0

            # Return the data as response
            response_data = {
                'overall_Landfill_waste': overall_Landfill_waste,
                'facility_Landfill_waste': facility_Landfill_waste,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Log the error for debugging purposes
            print(f"An error occurred: {e}")
            return Response({'error': 'An error occurred while processing your request.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#WasteStackedOverviewGraph

# class StackedWasteOverviewView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user
#         facility_id = request.GET.get('facility_id', None)
#         year = request.GET.get('year', None)
        
#         if year is None:
#             return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             year = int(year)
#         except (TypeError, ValueError):
#             return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             waste_types = [
#                 'food_waste', 'solid_Waste', 'E_Waste', 'Biomedical_waste',
#                 'liquid_discharge', 'other_waste', 'Landfill_waste', 'Landfill_waste'
#             ]
#             monthly_data = {month: {waste_type: 0 for waste_type in waste_types} for month in range(1, 13)}

#             for waste_type in waste_types:
#                 if facility_id and facility_id.lower() != 'all':
#                     monthly_waste = (
#                         Waste.objects.filter(user=user, facility__id=facility_id, DatePicker__year=year)
#                         .values('DatePicker__month')
#                         .annotate(total=Coalesce(Sum(waste_type, output_field=FloatField()), Value(0, output_field=FloatField())))
#                         .order_by('DatePicker__month')
#                     )
#                 else:
#                     monthly_waste = (
#                         Waste.objects.filter(user=user, DatePicker__year=year)
#                         .values('DatePicker__month')
#                         .annotate(total=Coalesce(Sum(waste_type, output_field=FloatField()), Value(0, output_field=FloatField())))
#                         .order_by('DatePicker__month')
#                     )

#                 for entry in monthly_waste:
#                     month = entry['DatePicker__month']
#                     monthly_data[month][waste_type] = entry['total']

#             stacked_bar_data = []
#             for month in range(1, 13):
#                 month_name = datetime(1900, month, 1).strftime('%b')
#                 stacked_bar_data.append({
#                     "month": month_name,
#                     **monthly_data[month]
#                 })

#             response_data = {
#                 "stacked_bar_data": stacked_bar_data
#             }

#             return Response(response_data, status=status.HTTP_200_OK)

#         except Exception as e:
#             print(f"Error occurred: {e}") 
#             return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
class StackedWasteOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)
        
        if year is None:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            waste_types = [
                'food_waste', 'solid_Waste', 'E_Waste', 'Biomedical_waste',
                'liquid_discharge', 'other_waste', 'Recycle_waste', 'Landfill_waste'
            ]
            monthly_data = {month: {waste_type: 0 for waste_type in waste_types} for month in range(1, 13)}

            for waste_type in waste_types:
                queryset = Waste.objects.filter(user=user, DatePicker__year=year)
                
                if facility_id and facility_id.lower() != 'all':
                    queryset = queryset.filter(facility__facility_id=facility_id)

                if facility_location and facility_location.lower() != 'all':
                    queryset = queryset.filter(facility__facility_location__icontains=facility_location)

                monthly_waste = (
                    queryset
                    .values('DatePicker__month')
                    .annotate(total=Coalesce(Sum(waste_type, output_field=FloatField()), Value(0, output_field=FloatField())))
                    .order_by('DatePicker__month')
                )

                for entry in monthly_waste:
                    month = entry['DatePicker__month']
                    monthly_data[month][waste_type] = entry['total']

            stacked_bar_data = []
            for month in range(1, 13):
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

#Waste overview Donut Chart
# class WasteOverallDonutChartView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user
#         year = request.GET.get('year', None)
#         facility_id = request.GET.get('facility_id', None)
#         facility_location = request.GET.get('facility_location', None)
        
#         if not year:
#             return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
#         try:
#             year = int(year)
#         except (TypeError, ValueError):
#             return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             # Base queryset filtered by user and year
#             queryset = Waste.objects.filter(user=user, DatePicker__year=year)

#             # Apply facility_id filter if provided and not 'all'
#             if facility_id and facility_id.lower() != 'all':
#                 queryset = queryset.filter(facility__facility_id=facility_id)

#             # Apply facility_location filter if provided and not 'all'
#             if facility_location and facility_location.lower() != 'all':
#                 queryset = queryset.filter(facility__facility_location__icontains=facility_location)

#             # Aggregate waste totals for each waste type
#             waste_totals = queryset.aggregate(
#                 food_waste_total=Coalesce(Sum(Cast('food_waste', FloatField())), 0.0),
#                 solid_waste_total=Coalesce(Sum(Cast('solid_waste', FloatField())), 0.0),
#                 e_waste_total=Coalesce(Sum(Cast('E_Waste', FloatField())), 0.0),
#                 biomedical_waste_total=Coalesce(Sum(Cast('Biomedical_waste', FloatField())), 0.0),
#                 other_waste_total=Coalesce(Sum(Cast('other_waste', FloatField())), 0.0)
#             )

#             # Calculate overall waste total
#             overall_total = sum(waste_totals.values())

#             if overall_total == 0:
#                 return Response({'error': 'No waste data available for the selected year and facility.'}, status=status.HTTP_204_NO_CONTENT)

#             # Calculate percentages for each waste type
#             waste_percentages = {key: (value / overall_total) * 100 for key, value in waste_totals.items()}

#             # Format response data
#             response_data = {
#                 "year": year,
#                 "facility_id": facility_id,
#                 "facility_location": facility_location,
#                 "waste_percentages": waste_percentages
#             }

#             return Response(response_data, status=status.HTTP_200_OK)

#         except Exception as e:
#             import logging
#             logging.error(f"Error in WasteOverallDonutChartView: {e}")
#             return Response({'error': 'An internal error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class WasteOverallDonutChartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        year = request.GET.get('year', None)
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        
        if year is None:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            waste_types = [
                'food_waste', 'solid_Waste', 'E_Waste', 'Biomedical_waste', 'other_waste'
            ]

            # Base queryset filtered by user and year
            queryset = Waste.objects.filter(user=user, DatePicker__year=year)

           
            # Apply facility_id filter if provided and not 'all'
            if facility_id and facility_id.lower() != 'all':
                queryset = queryset.filter(facility__facility_id=facility_id)

            # Apply facility_location filter if provided and not 'all'
            if facility_location and facility_location.lower() != 'all':
                queryset = queryset.filter(facility__facility_location__icontains=facility_location)

            # Aggregate waste totals for each waste type
            waste_totals = queryset.aggregate(
                food_waste_total=Coalesce(Sum(Cast('food_waste', FloatField())), 0.0),
                solid_Waste_total=Coalesce(Sum(Cast('solid_Waste', FloatField())), 0.0),
                E_Waste_total=Coalesce(Sum(Cast('E_Waste', FloatField())), 0.0),
                Biomedical_waste_total=Coalesce(Sum(Cast('Biomedical_waste', FloatField())), 0.0),
                other_waste_total=Coalesce(Sum(Cast('other_waste', FloatField())), 0.0)
            )

            # Calculate overall waste total
            overall_total = sum(waste_totals.values())

            if overall_total == 0:
                return Response({'error': 'No waste data available for the selected year and facility.'}, status=status.HTTP_204_NO_CONTENT)

            # Calculate percentages for each waste type
            waste_percentages = {
                'food_waste': (waste_totals['food_waste_total'] / overall_total) * 100,
                'solid_Waste': (waste_totals['solid_Waste_total'] / overall_total) * 100,
                'E_Waste': (waste_totals['E_Waste_total'] / overall_total) * 100,
                'Biomedical_waste': (waste_totals['Biomedical_waste_total'] / overall_total) * 100,
                'other_waste': (waste_totals['other_waste_total'] / overall_total) * 100,
            }

            # Format response data
            response_data = {
                "year": year,
                "facility_id": facility_id,
                "facility_location": facility_location,
                "waste_percentages": waste_percentages
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error occurred: {e}")
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

 #SentToLandFillOverview
class SentToLandfillOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        year = request.GET.get('year', None)
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        
        
        if year is None:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            overall_total_fields = [
                'food_waste', 'solid_Waste', 'E_Waste', 'Biomedical_waste', 'other_waste'
            ]

            queryset = Waste.objects.filter(user=user, DatePicker__year=year)

            if facility_id and facility_id.lower() != 'all':
                queryset = queryset.filter(facility__facility_id=facility_id)

            Landfill_waste_total = queryset.aggregate(
                total=Coalesce(Sum(Cast('Landfill_waste', FloatField())), 0.0)
            )['total']

            overall_total = sum(
                queryset.aggregate(
                    **{f"{waste_type}_total": Coalesce(Sum(Cast(waste_type, FloatField())), 0.0)
                       for waste_type in overall_total_fields}
                ).values()
            )

            remaining_waste_total = overall_total - Landfill_waste_total

            if overall_total == 0:
                return Response({'error': 'No waste data available for the selected year and facility.'}, status=status.HTTP_204_NO_CONTENT)

            if facility_location and facility_location.lower() != 'all':
                queryset = queryset.filter(facility__facility_location__icontains=facility_location)
        
            landfill_percentage = (Landfill_waste_total / overall_total) * 100
            remaining_percentage = (remaining_waste_total / overall_total) * 100

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
        facility_location = request.GET.get('facility_location', None)
        
        
        if year is None:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            overall_total_fields = [
                'food_waste', 'solid_Waste', 'E_Waste', 'Biomedical_waste', 'other_waste'
            ]

            queryset = Waste.objects.filter(user=user, DatePicker__year=year)
            
            if facility_id and facility_id.lower() != 'all':
                queryset = queryset.filter(facility__facility_id=facility_id)
                
            if facility_location and facility_location.lower() != 'all':
                queryset = queryset.filter(facility__facility_location__icontains=facility_location)
            # Calculate total for 'sent_for_recycle'
            Recycle_waste_total = queryset.aggregate(
                total=Coalesce(Sum(Cast('Recycle_waste', FloatField())), 0.0)
            )['total']

            # Calculate total for other waste fields
            overall_total = sum(
                queryset.aggregate(
                    **{f"{waste_type}_total": Coalesce(Sum(Cast(waste_type, FloatField())), 0.0)
                       for waste_type in overall_total_fields}
                ).values()
            )

            # Calculate remaining waste by excluding 'sent_for_recycle'
            remaining_waste_total = overall_total - Recycle_waste_total
            
            # overall_total += sent_for_recycle_total

            if overall_total == 0:
                return Response({'error': 'No waste data available for the selected year and facility.'}, status=status.HTTP_204_NO_CONTENT)

            # Calculate percentages
            recycle_percentage = (Recycle_waste_total / overall_total) * 100
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
        facility_location = request.GET.get('facility_location', None)
        
        
        if year is None:
            return Response({'error':'Year Parameter is Required'},status=status.HTTP_400_BAD_REQUEST)
        
        try:
            year = int(year)
        except(TypeError,ValueError):
            return Response({'error':'Invalid Year Parameter'},status=status.HTTP_400_BAD_REQUEST)
        
        try:
            HVAC_data = Energy.objects.filter(user=user,DatePicker__year=year)
            
            if facility_id and facility_id.lower() != 'all':
                if not Facility.objects.filter(id=facility_id).exists():
                    return Response({'error': 'Invalid facility ID.'}, status=status.HTTP_400_BAD_REQUEST)
                HVAC_data = HVAC_data.filter(facility_id = facility_id)
                
            if facility_location:
                HVAC_data = HVAC_data.filter(facility__facility_location__icontains=facility_location)
            
            
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
        facility_location = request.GET.get('facility_location', None)
        
        
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
                    Energy.objects.filter(user=user, facility__id=facility_id, DatePicker__year=year,facility__facility_location__icontains=facility_location)
                    .values('DatePicker__month')
                    .annotate(total_hvac=Sum('hvac'))
                    .order_by('DatePicker__month')
                )
            else:
                monthly_hvac = (
                    Energy.objects.filter(user=user, DatePicker__year=year)
                    .values('DatePicker__month')
                    .annotate(total_hvac=Sum('hvac'))
                    .order_by('DatePicker__month')
                )

            line_chart_data = []
            hvac_data = defaultdict(float)

            for entry in monthly_hvac:
                month_name = datetime(1900, entry['DatePicker__month'], 1).strftime('%b')
                hvac_data[entry['DatePicker__month']] = entry['total_hvac']

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
  
#Production overviewCard

class ProductionOverViewCard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        if year is None:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            production_data = Energy.objects.filter(user=user, DatePicker__year=year)

            if facility_id and facility_id.lower() != 'all':
                if not Facility.objects.filter(id=facility_id).exists():
                    return Response({'error': 'Invalid facility ID.'}, status=status.HTTP_400_BAD_REQUEST)
                production_data = production_data.filter(facility__id=facility_id)

            if facility_location:
                production_data = production_data.filter(facility__facility_location__icontains=facility_location)

            facility_production = (
                production_data
                .values('facility__facility_name')
                .annotate(total_production=Sum('production'))
                .order_by('-total_production')
            )

            facility_production_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "total_production": entry['total_production']
                }
                for entry in facility_production
            ]

            overall_production = production_data.aggregate(total=Sum('production'))['total'] or 0

            response_data = {
                'overall_production': overall_production,
                'facility_production': facility_production_data,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"An error occurred: {e}")
            return Response({'error': 'An error occurred while processing your request.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#ProductionLine Charts and Donut charts
class ProductionOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
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
                monthly_production = (
                    Energy.objects.filter(user=user, facility__id=facility_id, DatePicker__year=year,facility__facility_location__icontains=facility_location)
                    .values('DatePicker__month')
                    .annotate(total_production=Sum('production'))
                    .order_by('DatePicker__month')
                )
            else:
                monthly_production = (
                    Energy.objects.filter(user=user, DatePicker__year=year,facility__facility_location__icontains=facility_location)
                    .values('DatePicker__month')
                    .annotate(total_production=Sum('production'))
                    .order_by('DatePicker__month')
                )

          
            line_chart_data = []
            production = defaultdict(float)

            for entry in monthly_production:
                month_name = datetime(1900, entry['DatePicker__month'], 1).strftime('%b')
                production[entry['DatePicker__month']] = entry['total_production']

            for month in range(1, 13):
                month_name = datetime(1900, month, 1).strftime('%b')
                line_chart_data.append({
                    "month": month_name,
                    "production": production.get(month, 0)
                })

            # Query for facility-wise food waste
            if facility_id and facility_id.lower() != 'all':
                facility_production = (
                    Energy.objects.filter(user=user, facility__id=facility_id)
                    .values('facility__facility_name')
                    .annotate(total_production=Sum('production'))
                    .order_by('-total_production')
                )
            else:
                facility_production = (
                    Energy.objects.filter(user=user)
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
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': 'An error occurred while processing your request.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#stp overviewcard
class StpOverViewCard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        if year is None:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            stp_data = Energy.objects.filter(user=user, DatePicker__year=year)

            if facility_id and facility_id.lower() != 'all':
                if not Facility.objects.filter(id=facility_id).exists():
                    return Response({'error': 'Invalid facility ID.'}, status=status.HTTP_400_BAD_REQUEST)
                stp_data = stp_data.filter(facility__id=facility_id)

            if facility_location:
                stp_data = stp_data.filter(facility__facility_location__icontains=facility_location)

            facility_stp = (
                stp_data
                .values('facility__facility_name')
                .annotate(total_stp=Sum('stp'))
                .order_by('-total_stp')
            )

            facility_stp_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "total_stp": entry['total_stp']
                }
                for entry in facility_stp
            ]

            overall_stp = stp_data.aggregate(total=Sum('stp'))['total'] or 0

            response_data = {
                'overall_stp': overall_stp,
                'facility_stp': facility_stp_data,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"An error occurred: {e}")
            return Response({'error': 'An error occurred while processing your request.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#STP Overview line charts and donut charts
class StpOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
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
                monthly_stp = (
                    Energy.objects.filter(user=user, facility__id=facility_id, DatePicker__year=year,facility__facility_location__icontains=facility_location)
                    .values('DatePicker__month')
                    .annotate(total_stp=Sum('stp'))
                    .order_by('DatePicker__month')
                )
            else:
                monthly_stp = (
                    Energy.objects.filter(user=user, DatePicker__year=year,facility__facility_location__icontains=facility_location)
                    .values('DatePicker__month')
                    .annotate(total_stp=Sum('stp'))
                    .order_by('DatePicker__month')
                )

          
            line_chart_data = []
            stp = defaultdict(float)

            for entry in monthly_stp:
                month_name = datetime(1900, entry['DatePicker__month'], 1).strftime('%b')
                stp[entry['DatePicker__month']] = entry['total_stp']

            for month in range(1, 13):
                month_name = datetime(1900, month, 1).strftime('%b')
                line_chart_data.append({
                    "month": month_name,
                    "stp": stp.get(month, 0)
                })

            # Query for facility-wise food waste
            if facility_id and facility_id.lower() != 'all':
                facility_stp = (
                    Energy.objects.filter(user=user, facility__id=facility_id)
                    .values('facility__facility_name')
                    .annotate(total_stp=Sum('stp'))
                    .order_by('-total_stp')
                )
            else:
                facility_stp = (
                    Energy.objects.filter(user=user)
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
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': 'An error occurred while processing your request.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Admin_block CardOverview
class Admin_BlockOverViewCard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
        year = request.GET.get('year', None)

        if year is None:
            return Response({'error': 'Year parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            admin_block_data = Energy.objects.filter(user=user, DatePicker__year=year)

            if facility_id and facility_id.lower() != 'all':
                if not Facility.objects.filter(id=facility_id).exists():
                    return Response({'error': 'Invalid facility ID.'}, status=status.HTTP_400_BAD_REQUEST)
                admin_block_data = admin_block_data.filter(facility__id=facility_id)

            if facility_location:
                admin_block_data = admin_block_data.filter(facility__facility_location__icontains=facility_location)

            facility_admin_block = (
                admin_block_data
                .values('facility__facility_name')
                .annotate(total_admin_block=Sum('admin_block'))
                .order_by('-total_admin_block')
            )

            facility_admin_block_data = [
                {
                    "facility_name": entry['facility__facility_name'],
                    "total_admin_block": entry['total_admin_block']
                }
                for entry in facility_admin_block
            ]

            overall_admin_block = admin_block_data.aggregate(total=Sum('admin_block'))['total'] or 0

            response_data = {
                'overall_admin_block': overall_admin_block,
                'facility_admin_block': facility_admin_block_data,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"An error occurred: {e}")
            return Response({'error': 'An error occurred while processing your request.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Admin_block Overview Linecharts and donut charts
class Admin_BlockOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        facility_id = request.GET.get('facility_id', None)
        facility_location = request.GET.get('facility_location', None)
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
                monthly_admin_block = (
                    Energy.objects.filter(user=user, facility__id=facility_id, DatePicker__year=year,facility__facility_location__icontains=facility_location)
                    .values('DatePicker__month')
                    .annotate(total_admin_block=Sum('admin_block'))
                    .order_by('DatePicker__month')
                )
            else:
                monthly_admin_block = (
                    Energy.objects.filter(user=user, DatePicker__year=year,facility__facility_location__icontains=facility_location)
                    .values('DatePicker__month')
                    .annotate(total_admin_block=Sum('admin_block'))
                    .order_by('DatePicker__month')
                )

          
            line_chart_data = []
            admin_block = defaultdict(float)

            for entry in monthly_admin_block:
                month_name = datetime(1900, entry['DatePicker__month'], 1).strftime('%b')
                admin_block[entry['DatePicker__month']] = entry['total_admin_block']

            for month in range(1, 13):
                month_name = datetime(1900, month, 1).strftime('%b')
                line_chart_data.append({
                    "month": month_name,
                    "admin_block": admin_block.get(month, 0)
                })

            # Query for facility-wise food waste
            if facility_id and facility_id.lower() != 'all':
                facility_admin_block = (
                    Energy.objects.filter(user=user, facility__id=facility_id)
                    .values('facility__facility_name')
                    .annotate(total_admin_block=Sum('admin_block'))
                    .order_by('-total_admin_block')
                )
            else:
                facility_admin_block = (
                    Energy.objects.filter(user=user)
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
                "line_chart_data": line_chart_data,
                "donut_chart_data": donut_chart_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': 'An error occurred while processing your request.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



'''Energy  Overview Cards ,Graphs and Individual line charts and donut charts Ends'''
