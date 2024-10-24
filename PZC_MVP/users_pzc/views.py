
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegisterSerializer, UserLoginSerializer,WasteSerializer,WasteCreateSerializer,EnergyCreateSerializer,EnergySerializer,WaterCreateSerializer,WaterSerializer,UploadDataSerializer,BiodiversityCreateSerializer,BiodiversitySerializer,FacilitySerializer,UploadDataSerializer
from .models import CustomUser,Waste,Energy,Water,UploadData,Biodiversity,Facility

#Register View
class RegisterView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"msg": "User registered successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#LoginView
class LoginView(APIView):
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

# class LoginView(APIView):
#     def post(self, request):
#         serializer = UserLoginSerializer(data=request.data)
#         if serializer.is_valid():
#             email = serializer.validated_data['email']
#             password = serializer.validated_data['password']
#             try:
#                 user = CustomUser.objects.get(email=email)
#             except CustomUser.DoesNotExist:
#                 return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

#             if user.check_password(password):
#                 refresh = RefreshToken.for_user(user)
#                 response = Response({
#                     'refresh': str(refresh),
#                     'access': str(refresh.access_token),
#                 }, status=status.HTTP_200_OK)
#                 response.set_cookie('access_token', str(refresh.access_token), httponly=True)
#                 return response
#             return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#Dashboard View
class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # user = request.user
        # waste_data = Waste.objects.filter(user=user)
        # waste_serializer = WasteSerializer(waste_data,many=True)
        user_data = {
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            # 'waste_data' : waste_serializer.data
        }
        return Response(user_data, status=status.HTTP_200_OK)

#Logout View
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = Response({"message": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response




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
    
#viewWaste
class WasteView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        waste_data = Waste.objects.filter(user=user)
        waste_serializer = WasteSerializer(waste_data,many=True)
        user_data = {
            'email':user.email,
            'waste_data' : waste_serializer.data
        }
        return Response(user_data, status=status.HTTP_200_OK)


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
    def get(self, request):
        user = request.user
        energy_data = Energy.objects.filter(user=user)
        energy_serializer = EnergySerializer(energy_data,many=True)
        user_data={
            'email' : user.email,
            'energy_data' : energy_serializer.data
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
    
    def get(self,request):
        user = request.user
        water_data = Water.objects.filter(user=user)
        water_serializer = WaterSerializer(water_data,many=True)
        user_data={
           ' email' : user.email,
            'water_data' : water_serializer.data
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
    def get(self,request):
        user = request.user
        biodiversity_data = Biodiversity.objects.filter(user=user)
        biodiversity_serializer = BiodiversitySerializer(biodiversity_data,many=True)
        user_data={
            'email' : user.email,
            'biodiversity_data':biodiversity_serializer.data
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


class FacilityCreateView(APIView):
    permission_classes = [IsAuthenticated] 

    def post(self, request):
        serializer = FacilitySerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)  # Associate the facility with the logged-in user
            return Response({"message": "Facility added successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UploadDataCreateView(APIView):
    permission_classes = [IsAuthenticated]  

    def post(self, request):
        upload_serializer = UploadDataSerializer(data=request.data, context={'request': request})
        if upload_serializer.is_valid():
            upload_data = upload_serializer.save()  # Save already associates user through serializer

            category = request.data.get('category')
            category_data = request.data.get('category_data')

            # Handling specific category data
            if category == 'Waste':
                waste_serializer = WasteCreateSerializer(data=category_data, context={'request': request})
                if waste_serializer.is_valid():
                    waste_serializer.save()  # User is handled in serializer
                    return Response({"message": "Waste data added successfully."}, status=status.HTTP_201_CREATED)
                return Response(waste_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            elif category == 'Energy':
                energy_serializer = EnergyCreateSerializer(data=category_data, context={'request': request})
                if energy_serializer.is_valid():
                    energy_serializer.save()
                    return Response({"message": "Energy data added successfully."}, status=status.HTTP_201_CREATED)
                return Response(energy_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            elif category == 'Water':
                water_serializer = WaterCreateSerializer(data=category_data, context={'request': request})
                if water_serializer.is_valid():
                    water_serializer.save()
                    return Response({"message": "Water data added successfully."}, status=status.HTTP_201_CREATED)
                return Response(water_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            elif category == 'Biodiversity':
                biodiversity_serializer = BiodiversityCreateSerializer(data=category_data, context={'request': request})
                if biodiversity_serializer.is_valid():
                    biodiversity_serializer.save()
                    return Response({"message": "Biodiversity data added successfully."}, status=status.HTTP_201_CREATED)
                return Response(biodiversity_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response({"error": "Invalid category."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(upload_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
