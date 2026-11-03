# from django.urls import path
# from . import views

# app_name = "hr"

# urlpatterns = [
#     path("", views.home, name="home"),
#     path("positions/", views.position_list, name="positions"),
# ]


from django.urls import path
from . import views

app_name = "hr"

urlpatterns = [
    
    # HR Dashboard Overview
    
    path("", views.home, name="home"),

    
    # 1. Employee Management (CRUD)
    
    path("employees/", views.employee_list, name="employee_list"),
    path("employees/add/", views.employee_create, name="employee_create"),
    path("employees/<int:pk>/", views.employee_detail, name="employee_detail"),
    path("employees/<int:pk>/edit/", views.employee_update, name="employee_update"),
    path("employees/<int:pk>/delete/", views.employee_delete, name="employee_delete"),

    
    # 2. Employee Requests
    
    path("requests/", views.request_list, name="request_list"),
    path("requests/add/", views.request_create, name="request_create"),
    path("requests/<int:pk>/status/", views.request_update_status, name="request_update_status"),

    
    # 3. Employee Task Tracking
    
    path("tasks/", views.task_list, name="task_list"),
    path("tasks/add/", views.task_create, name="task_create"),
    path("tasks/<int:pk>/status/", views.task_update_status, name="task_update_status"),

    
    # 4. Job Positions Management (CRUD)
    
    path("positions/", views.position_list, name="positions"),
    path("positions/add/", views.position_create, name="position_create"),
    path("positions/<int:pk>/edit/", views.position_update, name="position_update"),
    path("positions/<int:pk>/delete/", views.position_delete, name="position_delete"),

    
    # 5. Training & Development
    
    path("training/", views.training_list, name="training_list"),
    path("training/add/", views.training_create, name="training_create"),
    path("training/enroll/", views.training_enroll, name="training_enroll"),
]