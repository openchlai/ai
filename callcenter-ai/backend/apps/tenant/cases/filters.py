import django_filters
from .models import Case

class CaseFilter(django_filters.FilterSet):
    case_type = django_filters.CharFilter(field_name='case_type__code')
    status = django_filters.CharFilter(field_name='status__code')
    priority = django_filters.NumberFilter()
    is_confidential = django_filters.BooleanFilter()
    
    class Meta:
        model = Case
        fields = {
            'created_at': ['gte', 'lte'],
            'due_date': ['gte', 'lte'],
            'case_type__category': ['exact'],
            'assigned_to': ['exact'],
        }