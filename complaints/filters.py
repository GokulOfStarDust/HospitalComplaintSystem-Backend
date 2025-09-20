import django_filters
from .models import Complaint

class ComplaintFilter(django_filters.FilterSet):
    ward = django_filters.CharFilter(field_name='room__ward', lookup_expr='icontains')
    block = django_filters.CharFilter(field_name='room__Block', lookup_expr='icontains')
    assigned_department = django_filters.CharFilter(field_name='assigned_department__department_name', lookup_expr='iexact')

    class Meta:
        model = Complaint
        fields = ['status', 'priority', 'issue_type', 'assigned_department', 'ward', 'block']
