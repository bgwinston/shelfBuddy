from .views import create_reading_plan, reading_plan_detail, log_progress, weekly_report, check_falling_behind,reading_dashboard
from django.urls import path


urlpatterns = [
path('reading/create/', create_reading_plan, name='create_reading_plan'),
path('reading/<int:plan_id>/', reading_plan_detail, name='reading_plan_detail'),
path('reading/<int:plan_id>/log/', log_progress, name='log_progress'),
path('reading/weekly-report/', weekly_report, name='weekly_report'),
path('reading/behind/', check_falling_behind, name='check_falling_behind'),
path('reading/dashboard', reading_dashboard, name='reading_dashboard'),
]