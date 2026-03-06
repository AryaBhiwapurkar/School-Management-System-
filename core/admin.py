from django.contrib import admin
from .models import Class, Section, Student, Teacher


# Register your models here.

admin.site.register(Class)
admin.site.register(Section)
admin.site.register(Student)
admin.site.register(Teacher)