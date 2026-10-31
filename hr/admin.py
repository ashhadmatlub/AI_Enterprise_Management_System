from django.contrib import admin

from django.contrib import admin
from .models import Employee, EmployeeRequest, EmployeeTask

admin.site.register(Employee)
admin.site.register(EmployeeRequest)
admin.site.register(EmployeeTask)
