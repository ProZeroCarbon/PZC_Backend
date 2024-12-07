
from datetime import date
import re
import uuid
from venv import logger
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext as _
from auth_registration.models import CustomUser,Summary
from users_pzc.models import Waste,Water,Energy,Biodiversity,Logistices,Facility
import logging

#Registration Serializers starts
class UserRegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = [
            'user_id', 'organisation_name', 'business_executive', 'cin_number',
            'year_of_corporation', 'website_url', 'corporate_address', 'registered_office_address',
            'reporting_boundary', 'DatePicker', 'contact_no', 'alternative_contact_no', 'email', 'description',
            'password', 'confirm_password'
        ]
        extra_kwargs = {
            'organisation_name': {'required': True},
            'business_executive': {'required': True},
            'cin_number': {'required': True},
            'year_of_corporation': {'required': True},
            'website_url': {'required': True},
            'corporate_address': {'required': True},
            'registered_office_address': {'required': True},
            'reporting_boundary': {'required': True},
            'DatePicker': {'required': True},
            'contact_no': {'required': True},
            'alternative_contact_no': {'required': True},
            'email': {'required': True},
            'description': {'required': True},
            'password': {'write_only': True},
            'confirm_password': {'write_only': True},
        }

    def validate(self, data):
        # Ensure the password and confirm_password match
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Password and confirm password do not match."})

        # Validate unique fields
        unique_fields = ['email', 'cin_number', 'contact_no', 'alternative_contact_no']
        for field in unique_fields:
            value = data.get(field)
            if value and CustomUser.objects.filter(**{field: value}).exists():
                raise serializers.ValidationError({field: f"A user with this {field} already exists."})

        return data

    def validate_password(self, value):
        # Password strength validation
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not any(char.isalpha() for char in value):
            raise serializers.ValidationError("Password must contain at least one letter.")
        if not any(char in "!@#$%^&*()-_+=" for char in value):
            raise serializers.ValidationError("Password must contain at least one special character (!@#$%^&*()-_+=).")
        return value

    def create(self, validated_data):
        # Store the plain password temporarily
        plain_password = validated_data.pop('password')
        validated_data.pop('confirm_password', None)

        # Create the user
        user = CustomUser(**validated_data)
        user.set_password(plain_password)  # Hash the password before saving
        user.encrypted_password = user.encrypt_password(plain_password)
        user.save()

        # Attach the plain password temporarily for the response (do not save in the DB)
        # user.plain_password = plain_password  # This is for temporary use in the response

        return user
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')

        # Show plain_password only to superusers
        if request and request.user.is_superuser:
            representation['plain_password'] = instance.decrypt_password()
        else:
            representation.pop('plain_password', None)

        return representation
#Registration Serializers Ends

#LOgin Serializers Starts
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8, max_length=128)

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("Email field cannot be empty.")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise serializers.ValidationError("Invalid email format.")
        return value

    def validate_password(self, value):
        if not value:
            raise serializers.ValidationError("Password field cannot be empty.")
        return value

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if user is None:
                raise serializers.ValidationError("Unable to log in with provided credentials.", code='authorization')
        else:
            raise serializers.ValidationError("Must include 'email' and 'password'.", code='authorization')

        data['user'] = user
        return data
    
#LOgin Serializers Ends
class SummarySerializer(serializers.ModelSerializer):
    organisation_name = serializers.CharField(source="organisation.organisation_name", read_only=True)
    facility_name = serializers.CharField(source="facility.facility_name", read_only=True)
    # category = serializers.CharField(required=False)

    class Meta:
        model = Summary
        fields = [
            'summary_id', 'summary_type', 'financial_year', 'organisation',
            'organisation_name', 'facility', 'facility_name', 'category',
            'add_summary',
        ]
        read_only_fields = ['summary_id']

    def validate(self, data):
        organisation = data.get('organisation')
        facility = data.get('facility')
        category = data.get('category')
        financial_year = data.get('financial_year')

        if data.get('summary_type') == 'Long Summary' and category is not None:
            raise serializers.ValidationError("Category should not be provided for Long Summary.")
        
        # Validate facility ownership
        if facility and organisation and facility.user != organisation:
            raise serializers.ValidationError("The selected facility does not belong to the given organisation.")

        # Check for duplicate summary
        if Summary.objects.filter(
            organisation=organisation,
            facility=facility,
            category=category,
            financial_year=financial_year,
        ).exists():
            raise serializers.ValidationError(
                "A summary already exists for the given organisation, facility, category, and financial year."
            )

        # Validate financial year against the Waste model's DatePicker
        if category and financial_year:
            category_datepicker = self.get_category_datepicker(category, facility)
            if not category_datepicker:
                raise serializers.ValidationError(
                    {"category": "No valid DatePicker found for the selected category and facility."}
                )

            # Calculate expected financial year
            start_year = category_datepicker.year
            if category_datepicker.month < 4:  # Financial year starts in April
                start_year -= 1

            expected_financial_year = f"{start_year}-{start_year + 1}"
            
            if financial_year.isdigit() and len(financial_year) == 4:
                if str(start_year) == financial_year:
                    financial_year = expected_financial_year
                else:
                    raise serializers.ValidationError(
                        {"financial_year": f"The financial year '{financial_year}' does not match the expected financial year '{expected_financial_year}' derived from the DatePicker."}
                    )

        return data


    def get_category_datepicker(self, category, facility):
        try:
            if category == 'Waste':
                return self.get_waste_datepicker(facility)
            elif category == 'Water':
                return self.get_water_datepicker(facility)
            elif category == 'Energy':
                return self.get_energy_datepicker(facility)
            elif category == 'Biodiversity':
                return self.get_biodiversity_datepicker(facility)
            elif category == 'Logistics':
                return self.get_logistics_datepicker(facility)
            else:
                raise serializers.ValidationError(
                    {"category": f"Invalid category '{category}' selected."}
                )
        except serializers.ValidationError as e:
            # Re-raise the validation error to be handled by the calling code
            raise e
        except Exception as e:
            # Catch other unforeseen errors and raise a general error message
            raise serializers.ValidationError(
                {"category": f"An error occurred while fetching DatePicker: {str(e)}"}
            )
    def get_waste_datepicker(self, facility):
        try:
            waste = Waste.objects.filter(facility=facility).first()
            if waste and waste.DatePicker:
                return waste.DatePicker
            else:
                raise serializers.ValidationError(
                    {"category": "No valid DatePicker found for the Waste category and facility."}
                
                )
        except Exception as e:
            raise serializers.ValidationError(
                {"category": f"Error fetching Waste DatePicker: {str(e)}"}
            )
    def get_water_datepicker(self, facility):
        try:
            water = Water.objects.filter(facility=facility).first()
            if water and water.DatePicker:
                return water.DatePicker
            else:
                raise serializers.ValidationError(
                    {"category": "No valid DatePicker found for the Water category and facility."}
                )
        except Exception as e:
            raise serializers.ValidationError(
                {"category": f"Error fetching Water DatePicker: {str(e)}"}
            )
    def get_energy_datepicker(self, facility):
        try:
            energy = Energy.objects.filter(facility=facility).first()
            if energy and energy.DatePicker:
                return energy.DatePicker
            else:
                raise serializers.ValidationError(
                    {"category": "No valid DatePicker found for the Energy category and facility."}
                )
        except Exception as e:
            raise serializers.ValidationError(
                {"category": f"Error fetching Energy DatePicker: {str(e)}"}
            )
    def get_biodiversity_datepicker(self, facility):
        try:
            biodiversity = Biodiversity.objects.filter(facility=facility).first()
            if biodiversity and biodiversity.DatePicker:
                return biodiversity.DatePicker
            else:
                raise serializers.ValidationError(
                    {"category": "No valid DatePicker found for the Biodiversity category and facility."}
                )
        except Exception as e:
            raise serializers.ValidationError(
                {"category": f"Error fetching Biodiversity DatePicker: {str(e)}"}
            )
    def get_logistics_datepicker(self, facility):
        try:
            logistics = Logistices.objects.filter(facility=facility).first()
            if logistics and logistics.DatePicker:
                return logistics.DatePicker
            else:
                raise serializers.ValidationError(
                    {"category": "No valid DatePicker found for the Logistics category and facility."}
                )
        except Exception as e:
            raise serializers.ValidationError(
                {"category": f"Error fetching Logistics DatePicker: {str(e)}"}
            )       
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user  # Assign the logged-in user
        if validated_data.get('summary_type') == 'Long Summary':
            validated_data['category'] = None  # Clear category for Long Summary
        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('organisation', None)  # Exclude internal fields
        representation.pop('facility', None)
        return representation


