
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
            'reporting_boundary', 'DatePicker', 'contact_no', 'alternative_contact_no','email', 'description',
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
            'password': {'write_only': True, 'required': True},
            'confirm_password': {'write_only': True, 'required': True},
        }

    def validate(self, data):
        current_user_id = self.instance.user_id if self.instance else None
        unique_fields = ['email', 'cin_number', 'contact_no', 'alternative_contact_no']

        for field in unique_fields:
            value = data.get(field)
            if value and CustomUser.objects.filter(**{field: value}).exclude(user_id=current_user_id).exists():
                raise serializers.ValidationError({field: f"A user with this {field} already exists."})

        return data

    def validate_email(self, value):
        current_user_id = self.instance.user_id if self.instance else None
        if CustomUser.objects.filter(email=value).exclude(user_id=current_user_id).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not any(char.isalpha() for char in value):
            raise serializers.ValidationError("Password must contain at least one letter.")
        if not any(char in "!@#$%^&*()-_+=" for char in value):
            raise serializers.ValidationError("Password must contain at least one special character (!@#$%^&*()-_+=).")
        return value

    def validate_confirm_password(self, value):
        password = self.initial_data.get('password')
        if value != password:
            raise serializers.ValidationError("Password and confirm password do not match.")
        return value
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        validated_data.pop('confirm_password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        user = CustomUser(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
    def to_representation(self, instance):
        request = self.context.get('request')
        representation = super().to_representation(instance)

        # Only include password for superusers
        if request and request.user and request.user.is_superuser:
            representation['password'] = instance.password  # Password is now managed by Django

        return representation
    # def to_representation(self, instance):
    #     request = self.context.get('request')
    #     representation = super().to_representation(instance)

    #     if request and request.user and request.user.is_superuser:
    #         representation['password'] = instance.decrypt_password()
    # def to_representation(self, instance):
    #     # Get the user context
    #     request = self.context.get('request')
    #     representation = super().to_representation(instance)

    #     # Include password only for admins (superuser)
    #     if request and request.user and request.user.is_superuser:
    #         # Assuming the 'password' field is set at user creation and is stored as hashed
    #         representation['password'] = 'your_original_password_logic'  # Replace with logic to fetch original password if needed

    #     return representation
    
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

    class Meta:
        model = Summary
        fields = [
            'summary_id', 'summary_type', 'financial_year', 'organisation', 
            'organisation_name', 'facility', 'facility_name', 'category', 
            'add_summary',
        ]
        read_only_fields = ['summary_id', 'financial_year']

    def validate(self, data):
        # Ensure organisation and facility belong to the same user
        organisation = data.get('organisation')
        facility = data.get('facility')

        if facility and organisation and facility.user != organisation:
            raise serializers.ValidationError("The selected facility does not belong to the given organisation.")
        if data.get('summary_type') == 'Long Summary' and 'category' in data:
            raise serializers.ValidationError("Category should not be provided for Long Summary.")
        return data

    def create(self, validated_data):
        # Automatically assign the user based on the request
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user  # Set the `user` field
        return super().create(validated_data)
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('organisation', None) 
        representation.pop('facility', None)
        return representation
    def to_representation(self, instance):
        # Remove the 'category' field from the response if the summary is a "Long Summary"
        representation = super().to_representation(instance)
        if instance.summary_type == 'Long Summary':
            representation.pop('category', None)
        return representation
