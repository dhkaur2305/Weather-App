from django.urls import path
from .import views

urlpatterns = [
    path('', views.home, name = 'home'),
    path('delete/<int:record_id>/', views.delete_weather, name = 'delete_weather'),
    path('update/<int:record_id>/', views.update_weather, name = 'update_weather'),
    path('export-json/', views.export_json, name = 'export_json'),
]
