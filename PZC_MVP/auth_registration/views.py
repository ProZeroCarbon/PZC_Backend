from django.shortcuts import render

from auth_registration.models import CustomUser
from .serializers import UserRegisterSerializer, UserLoginSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import BasePermission
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404

# Create your views here.
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
            user = serializer.validated_data.get('user')
            if user is None:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)

            # Role-based dashboard redirection
            if user.is_superuser:  # Check if the user is a superuser (admin)
                dashboard_data = {"message": "Welcome to Admin Dashboard"}
            else:  # Default user role
                dashboard_data = {"message": "Welcome to User Dashboard"}

            return Response({
                'role': 'admin' if user.is_superuser else 'user',
                'dashboard_data': dashboard_data,
                'refresh': str(refresh),
                'access': str(refresh.access_token)
                
            }, status=status.HTTP_200_OK)

        # Return errors if serializer is invalid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class IsSuperUser(BasePermission):
    """
    Custom permission to only allow superusers (admin users).
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser

class AdminDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'admin':
            return Response({"error": "Access denied. Admins only."}, status=status.HTTP_403_FORBIDDEN)

        # Replace with real admin data
        admin_data = {
            "total_users": 120,
            "active_users": 100,
            "system_logs": ["Log1", "Log2", "Log3"],
        }

        return Response({"admin_dashboard": admin_data}, status=status.HTTP_200_OK)

class SuperuserListView(APIView):
    permission_classes = [IsSuperUser]  # Only admin users can access this view

    def get(self, request):
        superusers = CustomUser.objects.filter(is_superuser=True).values('email', 'first_name', 'last_name', 'is_staff')
        return Response({"superusers": list(superusers)})
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
  