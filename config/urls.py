from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("hr/", include("hr.urls")),
    path("recruitment/", include("recruitment.urls")),
    path("finance/", include("finance.urls")),
]
