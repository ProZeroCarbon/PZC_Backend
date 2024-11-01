from django_filters import rest_framework as filters
from users_pzc.models import Waste,Energy,Water,Biodiversity,Logistices,Facility


class FacilityFilter(filters.FilterSet):
    search = filters.CharFilter(field_name='facility_name',lookup_expr='icontains')
    
    class Meta:
        model = Facility
        fields = ['facility_name']

class FacilityDateFilterBase(filters.FilterSet):
    facility_id =filters.NumberFilter(field_name="facility__id")
    start_year = filters.NumberFilter(field_name="created_at",lookup_expr="year__gte")
    end_year = filters.NumberFilter(field_name="created_at",lookup_expr="year__lte")
    
    class Meta:
        fields=['facility_id','start_year','end_year']

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


