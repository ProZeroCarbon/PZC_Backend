from datetime import date, datetime
from django.shortcuts import render
from auth_registration.models import CustomUser,Summary
from .serializers import UserRegisterSerializer, UserLoginSerializer,SummarySerializer
from rest_framework.permissions import BasePermission
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .permissions import IsAdmin
from rest_framework import status
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404


'''Clients Registration Starts'''

#Registration Create

class Registercreate(APIView):
    permission_classes = [IsAuthenticated,IsAdmin]
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"msg": "User registered successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#Register View
class RegisterView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        try:
            # Get the organisation_name query parameter (if provided)
            organisation_name = request.query_params.get('organisation_name', None)

            # Base queryset: exclude staff and superusers
            query = CustomUser.objects.filter(is_staff=False, is_superuser=False)

            # Apply filter only if organisation_name is provided
            if organisation_name:
                query = query.filter(organisation_name__icontains=organisation_name)

            # If no data exists, return a default structure with "-" values
            if not query.exists():
                return Response({
                    "clients": [
                        {
                            "user_id": "-",
                            "organisation_name": "-",
                            "business_executive": "-",
                            "cin_number": "-",
                            "year_of_corporation": "-",
                            "website_url": "-",
                            "corporate_address": "-",
                            "registered_office_address": "-",
                            "reporting_boundary": "-",
                            "DatePicker": "-",
                            "contact_no": "-",
                            "alternative_contact_no": "-",
                            "email": "-",
                            "description": "-",
                        }
                    ]
                }, status=status.HTTP_200_OK)

            # Serialize the resulting queryset
            users_serializer = UserRegisterSerializer(query, many=True)
            client_data = users_serializer.data

            return Response({
                "clients": client_data,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"msg": "An error occurred", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#register Update
class RegisterUpdate(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, user_id):
        try:
            # Retrieve the user by ID
            user = get_object_or_404(CustomUser, user_id=user_id, is_staff=False, is_superuser=False)
            serializer = UserRegisterSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Client data Updated successfully."}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"msg": "An error occurred", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#RegisterDelete     
class RegisterDelete(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def delete(self, request, user_id):
        try:
            # Retrieve the user by ID
            user = get_object_or_404(CustomUser, user_id=user_id, is_staff=False, is_superuser=False)
            user.delete()
            return Response({"message": "Client data deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"msg": "An error occurred", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
'''Clients Registration ends'''

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
            # response.set_cookie('access_token', str(refresh.access_token), httponly=True)
            # return response

        # Return errors if serializer is invalid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminDashboardView(APIView):
    permission_classes = [IsAuthenticated,IsAdminUser]

    def get_fiscal_year_dates(self, year):
        fiscal_year_start = date(year, 4, 1)
        fiscal_year_end = date(year + 1, 3, 31)
        return fiscal_year_start, fiscal_year_end

    def get(self, request):
        # Restrict access to superusers only
        if not request.user.is_superuser:
            return Response({"error": "Access denied. Admins only."}, status=403)

        # Get the year parameter from the query
        year_param = request.query_params.get('year')
        try:
            if year_param:
                year = int(year_param)
                if year < 1900 or year > datetime.now().year + 10:  # Allow future years up to 10 years ahead
                    return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # If no year is provided, retrieve all data from the database
                year = None
        except ValueError:
            return Response({'error': 'Year must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)

        if year:
            # Query data for the selected fiscal year, excluding superusers
            fiscal_year_start, fiscal_year_end = self.get_fiscal_year_dates(year)
            queryset = CustomUser.objects.filter(
                is_superuser=False, DatePicker__range=[fiscal_year_start, fiscal_year_end]
            )
        else:
            # Retrieve all available data, excluding superusers
            queryset = CustomUser.objects.filter(is_superuser=False)

        # Calculate metrics
        total_users = queryset.count()
        active_users = queryset.filter(is_active=True).count()
        inactive_users = total_users - active_users

        # Response data
        admin_data = {
            "selected_year": year if year else "All years",
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": inactive_users,
        }

        # if year:
        #     admin_data.update({
        #         "fiscal_year_start": fiscal_year_start.strftime("%Y-%m-%d"),
        #         "fiscal_year_end": fiscal_year_end.strftime("%Y-%m-%d"),
        #     })

        return Response({"admin_dashboard": admin_data}, status=200)

class Add_Summary(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        # Pass context for access to request.user
        serializer = SummarySerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            summary = serializer.save()  # Save the summary object
            return Response(
                {
                    "msg": "Summary added successfully.",
                    "data": SummarySerializer(summary).data,  # Return serialized data
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class GetSummaries(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user
#         organisation_id = request.query_params.get('organisation', None)
#         category = request.query_params.get('category', None)

#         # Base queryset filtered for the authenticated user
#         queryset = Summary.objects.filter(user=user)

#         # Apply additional filters
#         if organisation_id:
#             queryset = queryset.filter(organisation__user_id=organisation_id)
#         if category:
#             queryset = queryset.filter(category=category)

#         # Serialize the data
#         serializer = SummarySerializer(queryset, many=True)
        
#         return Response(serializer.data, status=status.HTTP_200_OK)
class GetSummaries(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        organisation_name = request.query_params.get('organisation_name', None)
        facility_id = request.query_params.get('facility_id', None)
        category = request.query_params.get('category', None)
        year_param = request.query_params.get('year', None)

        # Validate year parameter
        try:
            if year_param:
                year = int(year_param)
                if year < 1900 or year > datetime.now().year + 10:  # Allow future years up to 10 years ahead
                    return Response({'error': 'Invalid year parameter.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # If no year is provided, retrieve all data from the database
                year = None
        except ValueError:
            return Response({'error': 'Year must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)

        # Base queryset filtered for the authenticated user
        queryset = Summary.objects.filter(user=user)

        # Apply additional filters
        if organisation_name:
            queryset = queryset.filter(organisation__organisation_name__icontains=organisation_name)
        if facility_id:
            queryset = queryset.filter(facility__id=facility_id)  # Use facility_id instead of facility_name
        if category:
            queryset = queryset.filter(category=category)
        if year:
            # Filter by financial year if year is provided (Assuming financial_year is in "YYYY-YYYY" format)
            queryset = queryset.filter(financial_year__startswith=str(year))

        # Serialize the data
        serializer = SummarySerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
class SuperuserListView(APIView):
    permission_classes = [IsAdmin,IsAuthenticated]  # Only admin users can access this view

    def get(self, request):
        superusers = CustomUser.objects.filter(is_superuser=True).values('email','is_staff')
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
  