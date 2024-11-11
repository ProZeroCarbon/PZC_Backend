from django_filters import rest_framework as filters
from django.core.exceptions import ValidationError
from users_pzc.models import Waste, Energy, Water, Biodiversity, Logistices, Facility

# class FacilityFilter(filters.FilterSet):
#     search = filters.CharFilter(field_name='facility_name', lookup_expr='icontains')
#     facility_id = filters.CharFilter(field_name="facility_id")
#     facility_location = filters.CharFilter(field_name="facility_location", lookup_expr='icontains')

#     class Meta:
#         model = Facility
#         fields = ['facility_name', 'facility_id', 'facility_location']
    
#     def filter_queryset(self, queryset):
#         facility_id = self.data.get('facility_id')
#         if facility_id and facility_id.lower() == 'all':
#             return queryset
#         return super().filter_queryset(queryset)

# class FacilityDateFilterBase(filters.FilterSet):
#     facility_id = filters.CharFilter(field_name="facility__facility_id")
#     facility_location = filters.CharFilter(field_name="facility__facility_location", lookup_expr='icontains')
#     start_year = filters.NumberFilter(field_name="DatePicker", lookup_expr="year__gte")
#     end_year = filters.NumberFilter(field_name="DatePicker", lookup_expr="year__lte")

#     class Meta:
#         model = Facility
#         fields = ['facility_id', 'facility_location', 'start_year', 'end_year']

#     def clean_years(self):
#         start_year = self.data.get('start_year')
#         end_year = self.data.get('end_year')
#         if start_year and end_year:
#             try:
#                 start_year, end_year = int(start_year), int(end_year)
#                 if start_year > end_year:
#                     raise ValidationError("Start year must be less than or equal to end year.")
#             except ValueError:
#                 raise ValidationError("Start year and end year must be valid numbers.")

#     def filter_queryset(self, queryset):
#         self.clean_years()

#         facility_id = self.data.get('facility_id')
#         if facility_id and facility_id.lower() != 'all':
#             if not Facility.objects.filter(facility_id=facility_id).exists():
#                 raise ValidationError("Facility with the specified ID does not exist.")

#         return super().filter_queryset(queryset)


# class WasteFilter(FacilityDateFilterBase):
#     class Meta(FacilityDateFilterBase.Meta):
#         model = Waste
        
#     def filter_queryset(self, queryset):
#         facility_id = self.data.get('facility_id', 'all')
#         if facility_id.lower() != 'all':
#             queryset = queryset.filter(facility__facility_id=facility_id)
        
#         return super().filter_queryset(queryset)
# class EnergyFilter(FacilityDateFilterBase):
#     class Meta(FacilityDateFilterBase.Meta):
#         model = Energy
#     def filter_queryset(self, queryset):
#         # Adjusting filter for facility_id if not 'all'
#         facility_id = self.data.get('facility_id', 'all')
#         if facility_id.lower() != 'all':
#             queryset = queryset.filter(facility__facility_id=facility_id)
        
#         return super().filter_queryset(queryset)


# class WaterFilter(FacilityDateFilterBase):
#     class Meta(FacilityDateFilterBase.Meta):
#         model = Water
#     def filter_queryset(self, queryset):
#         facility_id = self.data.get('facility_id', 'all')
#         if facility_id.lower() != 'all':
#             queryset = queryset.filter(facility__facility_id=facility_id)
        
#         return super().filter_queryset(queryset)

# class BiodiversityFilter(FacilityDateFilterBase):
#     class Meta(FacilityDateFilterBase.Meta):
#         model = Biodiversity


# class LogisticesFilter(FacilityDateFilterBase):
#     class Meta(FacilityDateFilterBase.Meta):
#         model = Logistices



class FacilityFilter(filters.FilterSet):
    search = filters.CharFilter(field_name='facility_name', lookup_expr='icontains')
    facility_id = filters.CharFilter(field_name="facility_id")
    facility_location = filters.CharFilter(field_name="facility_location", lookup_expr='icontains')

    class Meta:
        model = Facility
        fields = ['facility_name', 'facility_id', 'facility_location']
class FacilityDateFilterBase(filters.FilterSet):
    facility_id = filters.CharFilter(field_name="facility__facility_id")
    facility_location = filters.CharFilter(field_name="facility__facility_location", lookup_expr='icontains')
    start_year = filters.NumberFilter(field_name="DatePicker", lookup_expr="year__gte")
    end_year = filters.NumberFilter(field_name="DatePicker", lookup_expr="year__lte")

    class Meta:
        model = Facility
        fields = ['facility_id', 'facility_location', 'start_year', 'end_year']

    def clean_years(self):
        start_year = self.data.get('start_year')
        end_year = self.data.get('end_year')
        if start_year and end_year:
            try:
                start_year, end_year = int(start_year), int(end_year)
                if start_year > end_year:
                    raise ValidationError("Start year must be less than or equal to end year.")
            except ValueError:
                raise ValidationError("Start year and end year must be valid numbers.")

    def filter_queryset(self, queryset):
        self.clean_years()

        facility_id = self.data.get('facility_id')
        if facility_id and facility_id.lower() != 'all':
            if not Facility.objects.filter(facility_id=facility_id).exists():
                raise ValidationError("Facility with the specified ID does not exist.")

        return super().filter_queryset(queryset)
# class WasteFilter(FacilityDateFilterBase):
#     class Meta(FacilityDateFilterBase.Meta):
#         model = Waste

#     def filter_queryset(self, queryset):
#         # Apply fiscal year filtering based on DatePicker
#         start_year = self.data.get('start_year')
#         end_year = self.data.get('end_year')

#         if start_year and end_year:
#             queryset = queryset.filter(DatePicker__year__gte=start_year, DatePicker__year__lte=end_year)

#         # Apply the facility_id filter if it's not 'all'
#         facility_id = self.data.get('facility_id', 'all')
#         if facility_id.lower() != 'all':
#             queryset = queryset.filter(facility__facility_id=facility_id)

#         return super().filter_queryset(queryset)

class WasteFilter(FacilityDateFilterBase):
    class Meta(FacilityDateFilterBase.Meta):
        model = Waste

class WasteFilter(FacilityDateFilterBase):
    class Meta(FacilityDateFilterBase.Meta):
        model = Waste
        
    def filter_queryset(self, queryset):
        # Check for 'facility_id' and handle accordingly
        facility_id = self.data.get('facility_id', 'all')
        
        if facility_id.lower() != 'all':
            # Filter by facility if facility_id is not 'all'
            queryset = queryset.filter(facility__facility_id=facility_id)

        # Apply fiscal year filter using 'DatePicker'
        start_year = self.data.get('start_year')
        end_year = self.data.get('end_year')

        if start_year and end_year:
            queryset = queryset.filter(DatePicker__year__gte=start_year, DatePicker__year__lte=end_year)

        return super().filter_queryset(queryset)



    
class EnergyFilter(FacilityDateFilterBase):
    class Meta(FacilityDateFilterBase.Meta):
        model = Energy
    def filter_queryset(self, queryset):
        # Adjusting filter for facility_id if not 'all'
        facility_id = self.data.get('facility_id', 'all')
        if facility_id.lower() != 'all':
            queryset = queryset.filter(facility__facility_id=facility_id)
        
        return super().filter_queryset(queryset)


class WaterFilter(FacilityDateFilterBase):
    class Meta(FacilityDateFilterBase.Meta):
        model = Water
    def filter_queryset(self, queryset):
        facility_id = self.data.get('facility_id', 'all')
        if facility_id.lower() != 'all':
            queryset = queryset.filter(facility__facility_id=facility_id)
        
        return super().filter_queryset(queryset)
    
class BiodiversityFilter(FacilityDateFilterBase):
    class Meta(FacilityDateFilterBase.Meta):
        model = Biodiversity


class LogisticesFilter(FacilityDateFilterBase):
    class Meta(FacilityDateFilterBase.Meta):
        model = Logistices


