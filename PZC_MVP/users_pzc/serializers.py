
import re
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import CustomUser,Waste,Energy,Water,Biodiversity,Facility,Logistices,Org_registration

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
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

    def create(self, validated_data):
        user = CustomUser(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


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


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Org_registration
        fields = ['organization_name', 'business_executive_name', 'location', 'branch_id', 'description']

    # Validation for 'organization_name'
    def validate_organization_name(self, value):
        request = self.context.get('request')
        
        if request and request.method in ['PUT', 'PATCH']:
            organization_id = request.parser_context['kwargs'].get('pk')
            if Org_registration.objects.exclude(pk=organization_id).filter(organization_name=value).exists():
                raise serializers.ValidationError("An organization with this name already exists.")
        else:
            if Org_registration.objects.filter(organization_name=value).exists():
                raise serializers.ValidationError("An organization with this name already exists.")
        
        if len(value) < 3:
            raise serializers.ValidationError("Organization name must be at least 3 characters long.")
        
        if not re.match("^[A-Za-z\s]*$", value):
            raise serializers.ValidationError("Organization name must contain only letters and spaces.")
        
        return value

    def validate_business_executive_name(self, value):
        if not re.match("^[A-Za-z\s]*$", value):
            raise serializers.ValidationError("Business Executive name must contain only letters and spaces.")
        return value
    
    def validate_location(self, value):
        if value and not re.match("^[A-Za-z0-9\s,]*$", value):
            raise serializers.ValidationError("Location can only contain letters, numbers, commas, and spaces.")
        return value
    
    def validate_branch_id(self, value):
        if not re.match("^[A-Za-z0-9]*$", value):
            raise serializers.ValidationError("Branch ID must be alphanumeric.")
        if len(value) < 5 or len(value) > 10:
            raise serializers.ValidationError("Branch ID must be between 5 and 10 characters long.")
        return value

    def validate_description(self, value):
        if value is None or value.strip() == '':
            raise serializers.ValidationError("Description cannot be empty.")
        if len(value) < 10:
            raise serializers.ValidationError("Description must be at least 10 characters long.")
        if value.lower() in ['na', 'none', 'not applicable']:
            raise serializers.ValidationError("Please provide a valid description.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        organization = Org_registration.objects.create(user=user, **validated_data)
        return organization
class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = ['facility_name', 'facility_head', 'location', 'description']
        
    def validate_facility_name(self, value):
        request = self.context.get('request')
        if request and request.method == 'PUT':
            facility_id = request.parser_context['kwargs'].get('pk')
            if Facility.objects.exclude(pk=facility_id).filter(facility_name=value).exists():
                raise serializers.ValidationError("A facility with this name already exists.")
        else:
            if Facility.objects.filter(facility_name=value).exists():
                raise serializers.ValidationError("A facility with this name already exists.")
        
        return value
    
    def create(self, validated_data):
        user = self.context['request'].user
        if 'user' in validated_data:
            validated_data.pop('user')
        facility = Facility.objects.create(user=user, **validated_data)
        return facility
    
class WasteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Waste
        fields = ['food_waste', 'solid_waste', 'e_waste', 'biomedical_waste', 
                  'liquid_discharge', 'others', 'sent_for_recycle', 
                  'send_to_landfill', 'facility','created_at']


class WasteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Waste
        fields = ['food_waste', 'solid_waste', 'e_waste', 'biomedical_waste', 
                  'liquid_discharge', 'others', 'sent_for_recycle', 
                  'send_to_landfill','facility','created_at']
    
    def validate(self, data):
        if data['food_waste'] < 0 or data['solid_waste'] < 0 or data['e_waste'] < 0 or data['biomedical_waste'] < 0:
            raise serializers.ValidationError("Waste quantities must be positive.")
        if not Facility.objects.filter(id=data['facility'].id).exists():
            raise serializers.ValidationError("The selected facility does not exist.")
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        if 'user' in validated_data:
            validated_data.pop('user')
        waste = Waste.objects.create(user=user, **validated_data)
        return waste



class EnergySerializer(serializers.ModelSerializer):
    class Meta:
        model = Energy
        fields = ['hvac', 'production', 'stp_etp', 'admin_block', 
                  'utilities', 'others', 'fuel_used_in_Operations','fuel_consumption','renewable_energy_solar', 
                  'renewable_energy_others', 'facility','created_at']


class EnergyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Energy
        fields = ['hvac', 'production', 'stp_etp', 'admin_block', 
                  'utilities', 'others', 'fuel_used_in_Operations','fuel_consumption', 'renewable_energy_solar', 
                  'renewable_energy_others', 'facility','created_at']
    
    def validate(self, data):
        if data['hvac'] < 0 or data['production'] < 0 or data['stp_etp'] < 0:
            raise serializers.ValidationError("Energy usage values must be positive.")
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        if 'user' in validated_data:
            validated_data.pop('user')
        energy = Energy.objects.create(user=user, **validated_data)
        return energy

class WaterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Water
        fields = ['generated_water', 'recycled_water', 'softener_usage', 
                  'boiler_usage', 'other_usage','facility','created_at']


class WaterCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Water
        fields = ['generated_water', 'recycled_water', 'softener_usage', 
                  'boiler_usage', 'other_usage', 'facility','created_at']

    def validate(self, data):
        if data['generated_water'] < 0 or data['recycled_water'] < 0:
            raise serializers.ValidationError("Water usage values must be positive.")
        # if data.get('recycled_water', 0) >= data.get('generated_water', 0):
        #     raise serializers.ValidationError("Recycled water must be less than generated water.")
        if not Facility.objects.filter(id=data['facility'].id).exists():
            raise serializers.ValidationError("The selected facility does not exist.")
        return data
    
    def create(self, validated_data):
        user = self.context['request'].user
        if 'user' in validated_data:
            validated_data.pop('user')
        water = Water.objects.create(user=user, **validated_data)
        return water



class BiodiversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Biodiversity
        fields = ['no_of_trees', 'Specie_name', 'age', 'height', 'width','total_area','new_trees_planted','head_count', 'facility','created_at']


class BiodiversityCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Biodiversity
        fields = ['no_of_trees', 'Specie_name', 'age', 'height', 'width','total_area','new_trees_planted','head_count', 'facility','created_at']

    def validate_no_of_trees(self, value):
        if value <= 0:
            raise serializers.ValidationError("Number of trees must be a positive integer.")
        return value
    
    def create(self, validated_data):
        user = self.context['request'].user
        if 'user' in validated_data:
            validated_data.pop('user')
        biodiversity = Biodiversity.objects.create(user=user, **validated_data)
        return biodiversity



class LogisticesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logistices
        fields = ['logistices_types','fuel_type','no_of_trips','fuel_consumption','no_of_vehicles','spends_on_fuel','facility','created_at']
    
    def validate(self, data):
        if data['no_of_trips'] < 0 or data['fuel_consumption'] < 0 or data['no_of_vehicles'] < 0:
            raise serializers.ValidationError("Trips, fuel consumption, and vehicles must be positive numbers.")
        return data
    
    def create(self, validated_data):
        user = self.context['request'].user
        if 'user' in validated_data:
            validated_data.pop('user')
        logistices = Logistices.objects.create(user=user, **validated_data)
        return logistices
    
    
    



