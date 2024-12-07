from datetime import date, datetime
from django.shortcuts import render
from auth_registration.models import CustomUser,Summary,UploadReport
from .serializers import UserRegisterSerializer, UserLoginSerializer,SummarySerializer,UploadReportSerializer
from rest_framework.permissions import BasePermission
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .permissions import IsAdmin
from rest_framework import status
from users_pzc.models import Facility
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
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        try:
            if not request.user.is_superuser:
                return Response({"msg": "Permission denied. Only superusers can access this."}, status=status.HTTP_403_FORBIDDEN)
    
            organisation_name = request.query_params.get('organisation_name', None)
            query = CustomUser.objects.filter(is_staff=False, is_superuser=False)

            # Apply filter only if organisation_name is provided
            if organisation_name:
                query = query.filter(organisation_name__icontains=organisation_name)
            for user in query:
                user.plain_password = "Plain password is only available during user creation."

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
                            "plain_password": "-"
                        }
                    ]
                }, status=status.HTTP_200_OK)

            # Serialize the resulting queryset
            users_serializer = UserRegisterSerializer(query, many=True, context={'request': request})
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

class GetSummaries(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        organisation_name = request.query_params.get('organisation_name', None)
        facility_id = request.query_params.get('facility_id', None)
        category = request.query_params.get('category', None)
        year_param = request.query_params.get('year', None)
        summary_type = request.query_params.get('summary_type', None)  # Optional summary_type filter

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

        # Apply additional filters based on query params
        if organisation_name:
            queryset = queryset.filter(organisation__organisation_name__icontains=organisation_name)
        if facility_id:
            queryset = queryset.filter(facility=facility_id)  # Filter by specific facility_id
        if category:
            queryset = queryset.filter(category=category)
        if summary_type:
            queryset = queryset.filter(summary_type=summary_type)
        if year_param:
            # Filter by financial year based on the "YYYY-YYYY" format
            queryset = queryset.filter(financial_year__startswith=str(year_param))

        # Serialize the filtered queryset
        summaryserializer = SummarySerializer(queryset, many=True)
        summary_data = summaryserializer.data

        # Return the serialized data in the response
        return Response({
            'summary':summary_data
            }, status=status.HTTP_200_OK)

class ReportUpload(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def post(self, request):
        # Create a mutable copy of the request data
        data = request.data.copy()

        # Get the user_id from the request to associate the file with a specific user
        user_id = request.data.get('user_id')  # The admin specifies the target user

        if not user_id:
            return Response(
                {"error": "User ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Ensure the user exists
            user = CustomUser.objects.get(user_id=user_id)
            data['user'] = user.user_id  # Associate the user with the report
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if a file is included in the request
        if 'uploaded_file' not in request.FILES or not request.FILES['uploaded_file']:
            return Response(
                {"error": "File not uploaded. Please attach a file to upload."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Serialize the data
        serializer = UploadReportSerializer(data=data)
        
        if serializer.is_valid():
            # Save the report to the database
            serializer.save()
            return Response(
                {"success": "File uploaded successfully.", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DownloadReport(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user_id = request.query_params.get('user_id', None)
        
        # If user_id is provided, retrieve reports for that specific user
        if user_id:
            try:
                user = CustomUser.objects.get(user_id=user_id)
                reports = UploadReport.objects.filter(user=user)
            except CustomUser.DoesNotExist:
                return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            # If no user_id is provided, return all reports (Admin access only)
            reports = UploadReport.objects.all()

        # Serialize the reports
        Reportserializer = UploadReportSerializer(reports, many=True)
        uploaded_report=Reportserializer.data
        

        return Response({
            "Uploaded Reports":uploaded_report
        },
        status=status.HTTP_200_OK)
    
   
    
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
  