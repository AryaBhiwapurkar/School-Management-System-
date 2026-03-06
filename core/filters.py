import django_filters
from .models import Student


class StudentFilter(django_filters.FilterSet):

    # direct field filter
    name = django_filters.CharFilter(lookup_expr="icontains")

    # foreign key filters
    section = django_filters.NumberFilter(field_name="section__id")
    school_class = django_filters.NumberFilter(field_name="section__school_class__id")

    class Meta:
        model = Student
        fields = ["name", "section", "school_class"]