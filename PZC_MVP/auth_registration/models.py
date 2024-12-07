import base64
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
    
    encrypted_password = models.TextField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password'] 

    def __str__(self):
        return f"{self.email} ({self.role})"
    
    def save(self, *args, **kwargs):
        if not self.user_id:
            self.user_id = uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)
        
    def encrypt_password(self, plain_password):
        """
        Encrypt the plain password using Fernet symmetric encryption.
        """
        encryption_key = getattr(settings, 'ENCRYPTION_KEY', None)
        
        # Decode the key from base64 and ensure it's 32 bytes
        decoded_key = base64.urlsafe_b64decode(encryption_key.encode())  # Decode to bytes
        valid_key = decoded_key[:32]  # Ensure it is 32 bytes

        # Create Fernet cipher suite with valid 32-byte key
        cipher_suite = Fernet(base64.urlsafe_b64encode(valid_key))  # Re-encode the key to base64
        return cipher_suite.encrypt(plain_password.encode()).decode()

    def decrypt_password(self):
        """
        Decrypt the stored encrypted password.
        """
        if not self.encrypted_password:
            return None
        
        encryption_key = getattr(settings, 'ENCRYPTION_KEY', None)
        
        # Decode and ensure it's 32 bytes
        decoded_key = base64.urlsafe_b64decode(encryption_key.encode())
        valid_key = decoded_key[:32]

        # Create Fernet cipher suite with valid 32-byte key
        cipher_suite = Fernet(base64.urlsafe_b64encode(valid_key))  # Recreate Fernet instance
        return cipher_suite.decrypt(self.encrypted_password.encode()).decode()

class Summary(models.Model):
    user= models.ForeignKey('auth_registration.CustomUser',on_delete=models.CASCADE)
    SUMMARY_TYPE_CHOICES = [
        ('Summary', 'Summary'),
        ('Brief Summary', 'Brief Summary'),
        ('Long Summary','Long Summary'),
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
    organisation = models.ForeignKey('auth_registration.CustomUser',on_delete=models.CASCADE,related_name='organisation_summaries',limit_choices_to={'role': 'user'},  # Only users can have summaries
    )
    facility = models.ForeignKey('users_pzc.Facility',on_delete=models.CASCADE,related_name='facility_summaries',
    )
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    add_summary = models.TextField()

    def __str__(self):
        return f"{self.summary_type} - {self.financial_year} - {self.category}"

    def save(self, *args, **kwargs):
        if not self.summary_id:
            self.summary_id = uuid.uuid4().hex[:8].upper()
            
        # Use provided financial year or calculate based on DatePicker
        if not self.financial_year:
            if self.organisation.DatePicker:
                start_year = self.organisation.DatePicker.year
                if self.organisation.DatePicker.month < 4:  # Financial year starts in April
                    start_year -= 1
                self.financial_year = f"{start_year}-{start_year + 1}"
        if not self.summary_id:
            self.summary_id = uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)
        


class UploadReport(models.Model):
    user= models.ForeignKey('auth_registration.CustomUser',on_delete=models.CASCADE)
    report_id =  models.CharField(max_length=255, primary_key=True, editable=False)
    organisation_name = models.CharField(max_length=255, default='')
    financial_year = models.CharField(max_length=255, help_text="e.g., 2024-2025")
    uploaded_file = models.FileField(upload_to='Report_records/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.organisation_name} - {self.financial_year}"
    
    def save(self, *args, **kwargs):
        if not self.report_id:
            self.report_id = uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)
        
    
    
    
    
    
    
    
