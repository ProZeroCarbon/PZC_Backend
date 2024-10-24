
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import CustomUser,Waste,Energy,Water,UploadData,Biodiversity,Facility,UploadData

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
        return value

    def create(self, validated_data):
        user = CustomUser(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if user is None:
                raise serializers.ValidationError(_("Unable to log in with provided credentials."), code='authorization')
        else:
            raise serializers.ValidationError(_("Must include 'email' and 'password'."), code='authorization')

        data['user'] = user
        return data


class WasteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Waste
        fields = ['food_waste','solid_waste','e_waste','biomedical_waste','liquid_discharge','others','sent_for_recycle','send_to_landfill','created_at']


class WasteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Waste
        fields = ['food_waste', 'solid_waste', 'e_waste', 'biomedical_waste','others']

    def create(self, validated_data):
        user = self.context['request'].user
        waste = Waste.objects.create(user=user, **validated_data)
        return waste

class EnergySerializer(serializers.ModelSerializer):
    class Meta:
        model = Energy
        fields = ['hvac','production','stp_etp','admin_block','utilities','others','renewable_energy_solar','renewable_energy_others']

class EnergyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Energy
        fields = ['hvac','production','stp_etp','admin_block','utilities','others','renewable_energy_solar','renewable_energy_others']
        
    def create(self,validated_data):
        user = self.context['request'].user
        energy = Energy.objects.create(user=user,**validated_data)
        return energy
    
class WaterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Water
        fields = ['generated_water','recycled_water','softener_usage','boiler_usage','other_usage']

class WaterCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Water
        fields = ['generated_water','recycled_water','softener_usage','boiler_usage','other_usage']
        
    def create(self,validate_data):
        user = self.context['request'].user
        water = Water.objects.create(user=user,**validate_data)
        return water
    
class BiodiversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Biodiversity
        fields = ['no_of_trees','Specie_name','age','height','width']
        
class BiodiversityCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Biodiversity
        fields = ['no_of_trees','Specie_name','age','height','width']
    
    def create(self,validate_data):
        user = self.context['request'].user
        biodiversity = Biodiversity.objects.create(user=user,**validate_data)
        return biodiversity
    
class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = ['facility_name', 'facility_head', 'location', 'description']
        
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data.pop('user', None)
        facility = Facility.objects.create(user=user, **validated_data)
        return facility

class UploadDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadData
        fields = ['facility', 'date', 'category']
    
    def create(self, validated_data):
        user = self.context['request'].user
        upload_data = UploadData.objects.create(user=user, **validated_data)  # User associated
        return upload_data

    def validate(self, data):
        user = self.context['request'].user
        facility = data.get('facility')
        if facility and facility.user != user:
            raise serializers.ValidationError("You do not have permission to upload data for this facility.")
        return data
