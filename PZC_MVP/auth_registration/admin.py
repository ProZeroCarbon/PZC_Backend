from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'role', 'organisation_name', 'business_executive', 'contact_no', 'password_display']
    search_fields = ['email', 'organisation_name']
    ordering = ['email']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),  # 'password' is shown as a field, but hidden by default
        ('Personal info', {
            'fields': (
                'organisation_name', 'business_executive', 'cin_number', 'year_of_corporation', 
                'website_url', 'corporate_address', 'registered_office_address', 'reporting_boundary', 
                'DatePicker', 'contact_no', 'alternative_contact_no', 'description'
            )
        }),
        ('Permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'organisation_name', 'business_executive', 
                       'cin_number', 'year_of_corporation', 'website_url', 'corporate_address', 'registered_office_address', 
                       'reporting_boundary', 'DatePicker', 'contact_no', 'alternative_contact_no', 'description')
        }),
    )

    def save_model(self, request, obj, form, change):
        obj.set_password(form.cleaned_data['password1'])  # Set password during user creation
        obj.save()

    def password_display(self, obj):
        # Only display the password for admin users
        if self.has_change_permission(obj):
            return format_html('<span style="color: red;">{}</span>', obj.password)  # Return password as plain text
        return "********"  # Mask password for non-admin users

    password_display.short_description = 'Password'  # Display name for the password field in the admin panel

# Register the CustomUser model with the custom admin interface
admin.site.register(CustomUser, CustomUserAdmin)
