# myapp/models.py
from django.db import models
from django.utils import timezone 
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

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']  # Fields required when creating a superuser

    def __str__(self):
        return self.email


class Org_registration(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    organization_name = models.CharField(max_length=255)
    business_executive_name = models.CharField(max_length=255)
    location = models.CharField( max_length=255,null=True,blank=True)
    branch_id = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    
    def __str__(self):
        return f"Organization: {self.organization_name} for {self.user.email}"
    

class Facility(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    facility_name = models.CharField(max_length=255)
    facility_head = models.CharField(max_length=255)
    facility_location = models.CharField(max_length=255)
    facility_description = models.TextField()

    def __str__(self):
        return self.facility_name
    
class Waste(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    category = models.CharField(max_length=255)
    DatePicker = models.DateField(null=True,blank=True)
    food_waste = models.FloatField(default=0.0)
    solid_Waste = models.FloatField(default=0.0)
    E_Waste = models.FloatField(default=0.0)
    Biomedical_waste = models.FloatField(default=0.0)
    liquid_discharge = models.FloatField(default=0.0)
    other_waste = models.FloatField(default=0.0)
    Recycle_waste = models.FloatField(default=0.0)
    Landfill_waste = models.FloatField(default=0.0)
    overall_usage = models.FloatField(default=0.0, editable=False)

    def __str__(self):
        return f"Waste data for {self.user.email}"
    
    def save(self,*args, **kwargs):
        self.overall_usage = (self.food_waste + self.solid_Waste + self.E_Waste + self.Biomedical_waste + self.other_waste)
        super(Waste,self).save(*args, **kwargs)


class Energy(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    FUEL_USED_IN_OPERATIONS_CHOICES=[
        ('Types','Types'),
        ('Crude oil - Diesel','Crude oil - Diesel'),
        ('Crude oil - Petrol','Crude oil - Petrol'),
        ('Coal - Cooking coal','Coal - Cooking coal'),
        ('Coal - Coke Oven Coal','Coal - Coke Oven Coal'),
        ('Natural gas','Natural gas'),
        ('Biomass - wood','Biomass - wood'),
        ('Biomass - Other solid waste','Biomass - Other solid waste')
    ]
    hvac=models.FloatField(default=0.0)
    production = models.FloatField(default=0.0)
    stp_etp = models.FloatField(default=0.0)
    admin_block = models.FloatField(default=0.0)
    utilities = models.FloatField(default=0.0)
    others = models.FloatField(default=0.0)
    fuel_used_in_Operations = models.CharField(max_length=255,choices=FUEL_USED_IN_OPERATIONS_CHOICES,default='Types')
    fuel_consumption = models.FloatField(default=0.0)
    renewable_energy_solar = models.FloatField(default=0.0)
    renewable_energy_others = models.FloatField(default=0.0)
    overall_usage = models.FloatField(default=0.0, editable=False)
    
    def __str__(self):
        return f"Energy data for {self.user.email}"
    def save(self,*args, **kwargs):
        self.overall_usage = (self.hvac + self.production + self.stp_etp + self.admin_block + self.utilities + self.others)
        super(Energy,self).save(*args, **kwargs)

class Water(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    generated_water = models.FloatField(default=0.0)
    recycled_water = models.FloatField(default=0.0)
    softener_usage = models.FloatField(default=0.0)
    boiler_usage = models.FloatField(default=0.0)
    other_usage = models.FloatField(default=0.0)
    overall_usage = models.FloatField(default=0.0, editable=False)
    
    def __str__(self):
        return f"Water data for {self.user.email}"
    def save(self, *args, **kwargs):
        self.overall_usage = (self.generated_water + self.recycled_water + self.softener_usage + self.boiler_usage + self.other_usage)
        super(Water, self).save(*args, **kwargs)
    
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
    overall_Trees = models.FloatField(default=0.0, editable=False)

    
    def __str__(self):
        return f"biodiversity data for {self.user.email}"
    
    def save(self,*args, **kwargs):
        self.overall_Trees = (self.no_of_trees)
        super(Biodiversity,self).save(*args, **kwargs)
        
    
class Logistices(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    LOGISTICES_TYPE_CHOICES=[
        ('staff_logistices','Staff_Logistices'),
        ('cargo','Cargo')
    ]
    FUEL_TYPE_CHOICES=[
        ('diesel','Diesel'),
        ('petrol','Petrol'),
        ('LPG','LPG')
    ]
    logistices_types = models.CharField(max_length=255,choices=LOGISTICES_TYPE_CHOICES,default='staff_logistices')
    fuel_type = models.CharField(max_length=255,choices=FUEL_TYPE_CHOICES,default='diesel')
    no_of_trips = models.IntegerField()
    fuel_consumption = models.FloatField(default=0.0)
    no_of_vehicles = models.IntegerField()
    spends_on_fuel = models.FloatField(default=0.0)
    total_fuelconsumption = models.FloatField(default=0.0, editable=False)
    def __str__(self):
        return f" data for {self.user.email}"
    
    def save(self,*args, **kwargs):
        self.total_fuelconsumption = (self.fuel_consumption)
        super(Logistices,self).save(*args, **kwargs)
    