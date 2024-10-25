# myapp/models.py

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class Facility(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    facility_name = models.CharField(max_length=255)
    facility_head = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.facility_name
    
class Waste(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    food_waste = models.FloatField(default=0.0)
    solid_waste = models.FloatField(default=0.0)
    e_waste = models.FloatField(default=0.0)
    biomedical_waste = models.FloatField(default=0.0)
    liquid_discharge = models.FloatField(default=0.0)
    others = models.FloatField(default=0.0)
    sent_for_recycle = models.FloatField(default=0.0)
    send_to_landfill = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Waste data for {self.user.email}"


class Energy(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    hvac=models.FloatField(default=0.0)
    production = models.FloatField(default=0.0)
    stp_etp = models.FloatField(default=0.0)
    admin_block = models.FloatField(default=0.0)
    utilities = models.FloatField(default=0.0)
    others = models.FloatField(default=0.0)
    # fuel_used_in Operations = models.CharField(max_length=255)
    fuel_consumption = models.FloatField(default=0.0)
    renewable_energy_solar = models.FloatField(default=0.0)
    renewable_energy_others = models.FloatField(default=0.0)
    def __str__(self):
        return f"Energy data for {self.user.email}"

class Water(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    generated_water = models.FloatField(default=0.0)
    recycled_water = models.FloatField(default=0.0)
    softener_usage = models.FloatField(default=0.0)
    boiler_usage = models.FloatField(default=0.0)
    other_usage = models.FloatField(default=0.0)
    
    def __str__(self):
        return f"Water data for {self.user.email}"
    
class Biodiversity(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    no_of_trees=models.IntegerField(default=0)
    Specie_name = models.CharField(max_length=255)
    age = models.IntegerField(default=0)
    height = models.FloatField(default=0.0)
    width = models.FloatField(default=0.0)
    total_area = models.FloatField(default=0.0)
    new_trees_planted = models.FloatField(default=0.0)
    head_count = models.FloatField(default=0.0)
    def __str__(self):
        return f"biodiversity data for {self.user.email}"
    
class Logistices(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    LOGISTICES_TYPE_CHOICES=[
        ('type','Type'),
        ('staff_logistices','Staff_Logistices'),
        ('cargo','Cargo')
    ]
    FUEL_TYPE=[
        ('type','Type'),
        ('diesel','Disesel'),
        ('petrol','Petrol'),
        ('LPG','CNG')
    ]
    logistices_types = models.CharField(max_length=255,choices=LOGISTICES_TYPE_CHOICES,default='type')
    fuel_type = models.CharField(max_length=255,choices=FUEL_TYPE,default='type')
    no_of_trips = models.IntegerField()
    fuel_consumption = models.FloatField(max_length=255)
    no_of_vehicles = models.IntegerField()
    spends_on_fuel = models.FloatField(max_length=255)
    def __str__(self):
        return f" data for {self.user.email}"