from django_filters import rest_framework as filters
from django.core.exceptions import ValidationError
from users_pzc.models import Waste, Energy, Water, Biodiversity, Logistices, Facility


class FacilityFilter(filters.FilterSet):
    search = filters.CharFilter(field_name='facility_name', lookup_expr='icontains')

    class Meta:
        model = Facility
        fields = ['facility_name']


class FacilityDateFilterBase(filters.FilterSet):
    facility_id = filters.NumberFilter(field_name="facility__id")
    start_year = filters.NumberFilter(field_name="DatePicker", lookup_expr="year__gte")
    end_year = filters.NumberFilter(field_name="DatePicker", lookup_expr="year__lte")

    class Meta:
        fields = ['facility_id', 'start_year', 'end_year']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Validate start_year and end_year
        start_year = self.data.get('start_year')
        end_year = self.data.get('end_year')
        if start_year and end_year:
            try:
                start_year = int(start_year)
                end_year = int(end_year)
                if start_year > end_year:
                    raise ValidationError("Start year must be less than or equal to end year.")
            except ValueError:
                raise ValidationError("Start year and end year must be valid numbers.")

    def filter_queryset(self, queryset):
        # Ensure facility_id exists if provided
        facility_id = self.data.get('facility_id')
        if facility_id and not Facility.objects.filter(id=facility_id).exists():
            raise ValidationError("Facility with the specified ID does not exist.")
        
        return super().filter_queryset(queryset)


class WasteFilter(FacilityDateFilterBase):
    class Meta(FacilityDateFilterBase.Meta):
        model = Waste


class EnergyFilter(FacilityDateFilterBase):
    class Meta(FacilityDateFilterBase.Meta):
        model = Energy


class WaterFilter(FacilityDateFilterBase):
    class Meta(FacilityDateFilterBase.Meta):
        model = Water


class BiodiversityFilter(FacilityDateFilterBase):
    class Meta(FacilityDateFilterBase.Meta):
        model = Biodiversity


class LogisticesFilter(FacilityDateFilterBase):
    class Meta(FacilityDateFilterBase.Meta):
        model = Logistices
