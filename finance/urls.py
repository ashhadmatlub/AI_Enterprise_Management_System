from django.urls import path
from . import views

app_name = "finance"

urlpatterns = [
    path("", views.finance_home, name="home"),
    path("add/<str:stream_type>/", views.add_entry, name="add_entry"),
    path("edit/<str:stream_type>/<int:item_id>/", views.edit_entry, name="edit_entry"),
    path("delete/<str:stream_type>/<int:item_id>/", views.delete_entry, name="delete_entry"),
]
