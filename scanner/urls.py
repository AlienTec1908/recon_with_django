from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('operations/', views.operations, name='operations'),
    path('api/scan/start', views.api_start_scan, name='api_start_scan'),
    path('api/scan/save_finding', views.api_save_finding, name='api_save_finding'),
    path('api/scan/update_progress', views.api_update_progress, name='api_update_progress'),
    path('api/scan/end', views.api_end_scan, name='api_end_scan'),
    path('api/scan/state/<uuid:session_id>/', views.api_get_scan_state, name='api_get_scan_state'),
    path('api/scan/logs/<uuid:session_id>/', views.api_get_scan_logs, name='api_get_scan_logs'),
    path('api/operations/<uuid:session_id>/', views.api_get_operations, name='api_get_operations'),
]
