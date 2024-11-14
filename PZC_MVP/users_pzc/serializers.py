
from datetime import date
import re
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext as _
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
        fields = ['Organization_Name', 'Business_executive_Name', 'Location', 'Branch_ID', 'description']

    # Validation for 'organization_name'
    def validate_Organization_Name(self, value):
        request = self.context.get('request')
        
        if request and request.method in ['PUT', 'PATCH']:
            organization_id = request.parser_context['kwargs'].get('pk')
            if Org_registration.objects.exclude(pk=organization_id).filter(Organization_Name=value).exists():
                raise serializers.ValidationError("An organization with this name already exists.")
        else:
            if Org_registration.objects.filter(Organization_Name=value).exists():
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
    user_id = serializers.IntegerField(source='user.id', read_only=True)  # Include user_id

    class Meta:
        model = Facility
        fields = ['facility_id', 'user_id', 'facility_name', 'facility_head', 'facility_location', 'facility_description']
        
    def validate_facility_name(self, value):
        request = self.context.get('request')
        user = request.user  # Get the current user
        
        # For PUT requests, exclude the current instance if it exists
        if request and request.method in ['PUT', 'PATCH']:
            # Only exclude the current facility from the query if self.instance exists (indicating update)
            if self.instance:
                facility_id = self.instance.facility_id
                if Facility.objects.exclude(facility_id=facility_id).filter(facility_name=value, user=user).exists():
                    raise serializers.ValidationError("A facility with this name already exists for this user.")
            else:
                if Facility.objects.filter(facility_name=value, user=user).exists():
                    raise serializers.ValidationError("A facility with this name already exists for this user.")
        
        else:
            if Facility.objects.filter(facility_name=value, user=user).exists():
                raise serializers.ValidationError("A facility with this name already exists for this user.")
        
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data.pop('user', None)  # Ensure user is not explicitly passed
        facility = Facility.objects.create(user=user, **validated_data)
        return facility


class WasteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Waste
        fields = ['user_id','facility_id','category', 'DatePicker', 'food_waste', 'solid_Waste', 
                  'E_Waste', 'Biomedical_waste', 'liquid_discharge', 
                  'other_waste', 'Recycle_waste','Landfill_waste','waste_id']
class WasteCreateSerializer(serializers.ModelSerializer):
    facility_id = serializers.CharField(
        write_only=True, required=True,
        error_messages={
            'required': 'Facility ID is required.',
            'null': 'Facility ID cannot be null.'
        }
    )
    DatePicker = serializers.DateField(
        required=True,
        error_messages={
            'required': 'Date is required.',
            'invalid': 'Invalid date format. Please use YYYY-MM-DD.'
        }
    )
    category = serializers.CharField(
        required=True,
        error_messages={'required': 'Category is required.'}
    )

    # Dynamically generated waste fields
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        waste_fields = [
            'food_waste', 'solid_Waste', 'E_Waste', 'Biomedical_waste',
            'liquid_discharge', 'other_waste', 'Recycle_waste', 'Landfill_waste'
        ]
        
        for field in waste_fields:
            self.fields[field] = serializers.FloatField(
                required=True,
                min_value=0,
                error_messages={
                    'required': f'{field.replace("_", " ").title()} is required.',
                    'min_value': f'{field.replace("_", " ").title()} must be a positive number.'
                }
            )

    class Meta:
        model = Waste
        fields = [
            'facility_id', 'category', 'DatePicker', 'food_waste', 'solid_Waste',
            'E_Waste', 'Biomedical_waste', 'liquid_discharge', 'other_waste',
            'Recycle_waste', 'Landfill_waste', 'waste_id'
        ]
        extra_kwargs = {
            'facility': {'read_only': True},
            'waste_id': {'read_only': True}
        }

    def validate(self, data):
        facility_id = data.get('facility_id')
        date = data.get('DatePicker')
        
        if not facility_id:
            raise serializers.ValidationError({"facility_id": "Facility ID is required."})

        # Ensure the facility exists
        try:
            facility = Facility.objects.get(facility_id=facility_id)
            data['facility'] = facility  # Set facility object on validated data
        except Facility.DoesNotExist:
            raise serializers.ValidationError({"facility_id": "The selected facility does not exist."})

        # Extract the month and year from the provided date
        month = date.month
        year = date.year

        if self.instance is None:
            if Waste.objects.filter(
                facility=facility,
                DatePicker__year=year,
                DatePicker__month=month
            ).exists():
                raise serializers.ValidationError({
                    "non_field_errors": _("A Waste entry for this facility already exists for this month.")
                })
        else:
            existing_entry = Waste.objects.filter(
                facility=facility,
                DatePicker__year=year,
                DatePicker__month=month
            ).exclude(waste_id=self.instance.waste_id)  

            if existing_entry.exists():
                raise serializers.ValidationError({
                    "non_field_errors": _("A different Waste entry for this facility already exists for this month.")
                })

        # Validate waste fields
        waste_fields = [
            'food_waste', 'solid_Waste', 'E_Waste', 'Biomedical_waste',
            'liquid_discharge', 'other_waste', 'Recycle_waste', 'Landfill_waste'
        ]
        for field in waste_fields:
            value = data.get(field)
            if value is None or value < 0:
                raise serializers.ValidationError({
                    field: f"{field.replace('_', ' ').title()} must be a positive number and cannot be null."
                })

        return data

    def create(self, validated_data):
        # Set the user from context
        user = self.context['request'].user
        validated_data['user'] = user
        validated_data.pop('facility_id', None)
        return Waste.objects.create(**validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['facility_id'] = instance.facility.facility_id
        representation.pop('facility', None)
        return representation
class EnergySerializer(serializers.ModelSerializer):
    class Meta:
        model = Energy
        fields = [
            'user_id', 'facility_id', 'category', 'DatePicker', 'hvac', 'production', 'stp', 
            'admin_block', 'utilities', 'others', 'fuel_types','coking_coal','coke_oven_coal','natural_gas','diesel' ,'biomass_wood','biomass_other_solid',
            'renewable_solar', 'renewable_other', 'overall_usage', 'energy_id'
        ]

class EnergyCreateSerializer(serializers.ModelSerializer):
    facility_id = serializers.CharField(
        write_only=True, required=True,
        error_messages={
            'required': 'Facility ID is required.',
            'null': 'Facility ID cannot be null.'
        }
    )
    DatePicker = serializers.DateField(
        required=True,
        error_messages={
            'required': 'Date is required.',
            'invalid': 'Invalid date format. Please use YYYY-MM-DD.'
        }
    )
    category = serializers.CharField(
        required=True,
        error_messages={'required': 'Category is required.'}
    )
    fuel_types = serializers.CharField(
        required=True,
        error_messages={'required': 'Fuel types are required.'}
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Energy fields that should default to 0 if not provided
        optional_energy_fields = [
            'coking_coal', 'coke_oven_coal', 'natural_gas', 'diesel',
            'biomass_wood', 'biomass_other_solid'
        ]
        
        # Make these fields optional with a default value of 0
        for field in optional_energy_fields:
            self.fields[field] = serializers.FloatField(
                required=False,
                min_value=0,
                default=0,  # Default to 0 if not provided
                error_messages={
                    'min_value': f'{field.replace("_", " ").title()} must be a positive number.'
                }
            )

        # All other energy fields should be required
        energy_fields = [
            'hvac', 'production', 'stp', 'admin_block', 'utilities', 'others',
            'renewable_solar', 'renewable_other'
        ]

        for field in energy_fields:
            self.fields[field] = serializers.FloatField(
                required=True,
                min_value=0,
                error_messages={
                    'required': f'{field.replace("_", " ").title()} is required.',
                    'min_value': f'{field.replace("_", " ").title()} must be a positive number.'
                }
            )

    class Meta:
        model = Energy
        fields = [
            'facility_id', 'category', 'DatePicker', 'hvac', 'production', 'stp', 
            'admin_block', 'utilities', 'others', 'fuel_types', 'coking_coal', 'coke_oven_coal',
            'natural_gas', 'diesel', 'biomass_wood', 'biomass_other_solid', 'renewable_solar',
            'renewable_other', 'energy_id'
        ]
        extra_kwargs = {
            'facility': {'read_only': True},
            'energy_id': {'read_only': True}
        }

    def validate(self, data):
        facility_id = data.get('facility_id')
        date = data.get('DatePicker')

        # Ensure the facility exists
        if not facility_id:
            raise serializers.ValidationError({"facility_id": "Facility ID is required."})

        try:
            facility = Facility.objects.get(facility_id=facility_id)
            data['facility'] = facility  # Set facility object on validated data
        except Facility.DoesNotExist:
            raise serializers.ValidationError({"facility_id": "The selected facility does not exist."})

        # Extract the month and year from the provided date
        month = date.month
        year = date.year

        # Check if there is an existing entry for this facility and month
        if self.instance is None:  # New entry (POST)
            if Energy.objects.filter(
                facility=facility,
                DatePicker__year=year,
                DatePicker__month=month
            ).exists():
                raise serializers.ValidationError({
                    "non_field_errors": _("An Energy entry for this facility already exists for this month.")
                })
        else:  # Update (PUT)
            existing_entry = Energy.objects.filter(
                facility=facility,
                DatePicker__year=year,
                DatePicker__month=month
            ).exclude(energy_id=self.instance.energy_id)  # Exclude the current instance being updated

            if existing_entry.exists():
                raise serializers.ValidationError({
                    "non_field_errors": _("A different Energy entry for this facility already exists for this month.")
                })

        # Validate required fields (ensure they are numeric)
        energy_fields = [
            'hvac', 'production', 'stp', 'admin_block', 'utilities', 'others', 
            'renewable_solar', 'renewable_other'
        ]
        for field in energy_fields:
            value = data.get(field)
            if value is None or not self.is_numeric(value):  # Check if value is numeric
                raise serializers.ValidationError({
                    field: f"{field.replace('_', ' ').title()} must be a valid number and cannot be null."
                })

        # Ensure the optional fields default to 0 if missing or invalid
        optional_energy_fields = [
            'coking_coal', 'coke_oven_coal', 'natural_gas', 'diesel', 
            'biomass_wood', 'biomass_other_solid'
        ]
        for field in optional_energy_fields:
            if field not in data:
                data[field] = 0  # Set missing optional fields to 0
            elif not self.is_numeric(data[field]):  # Check if value is numeric
                data[field] = 0  # Set to 0 if not numeric

        return data

    def is_numeric(self, value):
        try:
            float(value)  # Try to cast to float
            return True
        except ValueError:
            return False

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        validated_data.pop('facility_id', None)
        return Energy.objects.create(**validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['facility_id'] = instance.facility.facility_id
        representation.pop('facility', None)
        return representation

class WaterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Water
        fields = ['DatePicker','category','Generated_Water', 'Recycled_Water', 'Softener_usage', 
                  'Boiler_usage', 'otherUsage', 'facility_id','water_id']

class WaterCreateSerializer(serializers.ModelSerializer):
    facility_id = serializers.CharField(
        write_only=True, required=True,
        error_messages={
            'required': 'Facility ID is required.',
            'null': 'Facility ID cannot be null.'
        }
    )
    DatePicker = serializers.DateField(
        required=True,
        error_messages={
            'required': 'Date is required.',
            'invalid': 'Invalid date format. Please use YYYY-MM-DD.'
        }
    )
    category = serializers.CharField(
        required=True,
        error_messages={'required': 'Category is required.'}
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        water_fields = [
            'Generated_Water', 'Recycled_Water', 'Softener_usage', 'Boiler_usage', 'otherUsage'
        ]
        
        for field in water_fields:
            self.fields[field] = serializers.FloatField(
                required=True,
                min_value=0,
                error_messages={
                    'required': f'{field.replace("_", " ").title()} is required.',
                    'min_value': f'{field.replace("_", " ").title()} must be a positive number.'
                }
            )

    class Meta:
        model = Water
        fields = [
            'facility_id', 'DatePicker', 'category', 'Generated_Water', 'Recycled_Water',
            'Softener_usage', 'Boiler_usage', 'otherUsage', 'water_id'
        ]
        extra_kwargs = {
            'facility': {'read_only': True},
            'water_id': {'read_only': True}
        }

    def validate(self, data):
        facility_id = data.get('facility_id')
        date = data.get('DatePicker')
        
        if not facility_id:
            raise serializers.ValidationError({"facility_id": "Facility ID is required."})

        try:
            facility = Facility.objects.get(facility_id=facility_id)
            data['facility'] = facility
        except Facility.DoesNotExist:
            raise serializers.ValidationError({"facility_id": "The selected facility does not exist."})

        month = date.month
        year = date.year

        if self.instance is None:
            if Water.objects.filter(
                facility=facility,
                DatePicker__year=year,
                DatePicker__month=month
            ).exists():
                raise serializers.ValidationError({
                    "non_field_errors": _("A Water entry for this facility already exists for this month.")
                })
        else:
            existing_entry = Water.objects.filter(
                facility=facility,
                DatePicker__year=year,
                DatePicker__month=month
            ).exclude(water_id=self.instance.water_id)

            if existing_entry.exists():
                raise serializers.ValidationError({
                    "non_field_errors": _("A different Water entry for this facility already exists for this month.")
                })

        # Ensure that Generated_Water is greater than or equal to Recycled_Water
        generated_water = data.get('Generated_Water')
        recycled_water = data.get('Recycled_Water')

        if generated_water is not None and recycled_water is not None:
            if recycled_water > generated_water:
                raise serializers.ValidationError({
                    "Recycled_Water": "Recycled Water must be less than or equal to Generated Water."
                })

        # Validate positive values for all water fields
        water_fields = [
            'Generated_Water', 'Recycled_Water', 'Softener_usage', 'Boiler_usage', 'otherUsage'
        ]
        for field in water_fields:
            value = data.get(field)
            if value is None or value < 0:
                raise serializers.ValidationError({
                    field: f"{field.replace('_', ' ').title()} must be a positive number and cannot be null."
                })

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        validated_data.pop('facility_id', None)

        water = Water.objects.create(**validated_data)
        return water


class BiodiversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Biodiversity
        fields = ['facility_id','DatePicker','category','no_trees', 'species', 'age', 'height', 'width','totalArea','new_trees_planted','head_count', 'biodiversity_id']


class BiodiversityCreateSerializer(serializers.ModelSerializer):
    facility_id = serializers.CharField(
        write_only=True, required=True,
        error_messages={
            'required': 'Facility ID is required.',
            'null': 'Facility ID cannot be null.'
        }
    )
    DatePicker = serializers.DateField(
        required=True,
        error_messages={
            'required': 'Date is required.',
            'invalid': 'Invalid date format. Please use YYYY-MM-DD.'
        }
    )
    category = serializers.CharField(
        required=True,
        error_messages={'required': 'Category is required.'}
    )
    species = serializers.CharField(
        required=True,
        error_messages={'required': 'Species is required.'}
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        biodiversity_fields = [
            'no_trees', 'age', 'height', 'width', 'totalArea', 'new_trees_planted', 'head_count'
        ]
        
        for field in biodiversity_fields:
            self.fields[field] = serializers.FloatField(
                required=True,
                min_value=0,
                error_messages={
                    'required': f'{field.replace("_", " ").title()} is required.',
                    'min_value': f'{field.replace("_", " ").title()} must be a positive number.'
                }
            )
    
    class Meta:
        model = Biodiversity
        fields = [
            'facility_id','DatePicker', 'category', 'no_trees', 'species', 'age', 'height', 'width',
            'totalArea', 'new_trees_planted', 'head_count', 'biodiversity_id'
        ]
        extra_kwargs = {
            'facility': {'read_only': True},
            'biodiversity_id': {'read_only': True}
        }

    def validate(self, data):
        facility_id = data.get('facility_id')
        date = data.get('DatePicker')
        try:
            facility = Facility.objects.get(facility_id=facility_id)
            data['facility'] = facility
        except Facility.DoesNotExist:
            raise serializers.ValidationError({"facility_id": "The selected facility does not exist."})

        month = date.month
        year = date.year

        # Ensure there’s no existing Biodiversity entry for the same month and year
        if self.instance is None:
            if Biodiversity.objects.filter(
                facility=facility,
                DatePicker__year=year,
                DatePicker__month=month
            ).exists():
                raise serializers.ValidationError({
                    "non_field_errors": _("A Biodiversity entry for this facility already exists for this month.")
                })
        else:
            # Exclude the current instance in the check when updating
            existing_entry = Biodiversity.objects.filter(
                facility=facility,
                DatePicker__year=year,
                DatePicker__month=month
            ).exclude(biodiversity_id=self.instance.biodiversity_id)

            if existing_entry.exists():
                raise serializers.ValidationError({
                    "non_field_errors": _("A different Biodiversity entry for this facility already exists for this month.")
                })
        
        return data
    
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        validated_data.pop('facility_id', None)

        biodiversity = Biodiversity.objects.create(**validated_data)
        return biodiversity


class LogisticesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logistices
        fields = ['DatePicker','category','logistices_types','Typeof_fuel','km_travelled','No_Trips','fuel_consumption','No_Vehicles','Spends_on_fuel','facility','logistices_id']
    
    def validate(self, data):
        if data['No_Trips'] < 0 or data['fuel_consumption'] < 0 or data['No_Vehicles'] < 0:
            raise serializers.ValidationError("Trips, fuel consumption, and vehicles must be positive numbers.")
        return data
    
    def create(self, validated_data):
        user = self.context['request'].user
        if 'user' in validated_data:
            validated_data.pop('user')
        logistices = Logistices.objects.create(user=user, **validated_data)
        return logistices
    
    
    



