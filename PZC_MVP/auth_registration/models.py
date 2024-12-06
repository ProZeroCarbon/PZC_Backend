
import uuid
from django.db import models
from django.utils.timezone import now
from django.conf import settings

from cryptography.fernet import Fernet
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


# Create your models here.
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
    USER_ROLES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )
    
    user_id = models.CharField(max_length=255,primary_key=True, editable=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=USER_ROLES, default='user')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # New fields as per the requirement
    organisation_name = models.CharField(max_length=255)
    business_executive = models.CharField(max_length=255)
    cin_number = models.CharField(max_length=20)
    year_of_corporation = models.IntegerField(null=True, blank=True, default=2024)
    website_url = models.URLField()
    corporate_address = models.TextField()
    registered_office_address = models.TextField()
    reporting_boundary = models.CharField(max_length=255)
    DatePicker = models.DateField(null=True, blank=True)
    contact_no = models.CharField(max_length=15)
    alternative_contact_no = models.CharField(max_length=15, blank=True, null=True)
    description = models.TextField()
    

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password'] 

    def __str__(self):
        return f"{self.email} ({self.role})"
    
    def save(self, *args, **kwargs):
        if not self.user_id:
            self.user_id = uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)
    # def encrypt_password(self, password):
    #     cipher = Fernet(settings.ENCRYPTION_KEY.encode())
    #     return cipher.encrypt(password.encode()).decode()

    # def decrypt_password(self):
    #     if self.plaintext_password_encrypted:
    #         cipher = Fernet(settings.ENCRYPTION_KEY.encode())
    #         return cipher.decrypt(self.plaintext_password_encrypted.encode()).decode()

class Summary(models.Model):
    user= models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    SUMMARY_TYPE_CHOICES = [
        ('Summary', 'Summary'),
        ('Brief Summary', 'Brief Summary'),
        ('Long Summary','Load Summary'),
    ]

    CATEGORY_CHOICES = [
        ('Water', 'Water'),
        ('Energy', 'Energy'),
        ('Waste', 'Waste'),
        ('Biodiversity', 'Biodiversity'),
        ('Logistics', 'Logistics'),
    ]

    summary_id = models.CharField(max_length=255, primary_key=True, editable=False)
    summary_type = models.CharField(max_length=50, choices=SUMMARY_TYPE_CHOICES)
    financial_year = models.CharField(max_length=9)
    organisation = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='organisation_summaries',limit_choices_to={'role': 'user'},  # Only users can have summaries
    )
    facility = models.ForeignKey('users_pzc.Facility',on_delete=models.CASCADE,related_name='facility_summaries',
    )
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, null=True, blank=True)
    add_summary = models.TextField()

    def __str__(self):
        return f"{self.summary_type} - {self.financial_year} - {self.category}"

    def save(self, *args, **kwargs):
        if not self.summary_id:
            self.summary_id = uuid.uuid4().hex[:8].upper()
            
        if not self.financial_year:
            if self.organisation.DatePicker:
                start_year = self.organisation.DatePicker.year
                if self.organisation.DatePicker.month < 4: 
                    start_year -= 1
                self.financial_year = f"{start_year}-{start_year + 1}"
        if not self.summary_id:
            self.summary_id = uuid.uuid4().hex[:8].upper()
        if self.summary_type == 'Long Summary':
            self.category = None
        super().save(*args, **kwargs)
    