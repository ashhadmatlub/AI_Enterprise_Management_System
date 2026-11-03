from django.contrib import admin
from .models import (
    Employee,
    EmployeeRequest,
    EmployeeTask,
    JobPosition,
    TrainingEnrollment,
    TrainingProgram,
)

admin.site.register(Employee)
admin.site.register(EmployeeRequest)
admin.site.register(EmployeeTask)
admin.site.register(JobPosition)
admin.site.register(TrainingProgram)
admin.site.register(TrainingEnrollment)
