from .views import create_reading_plan, reading_plan_detail, log_progress, weekly_report, check_falling_behind,reading_dashboard, create_goal_view, delete_goal,about_shelfbuddy, edit_reading_plan, reading_plan_detail, apply_suggested_target
from django.urls import path


urlpatterns = [
path('reading/create/', create_reading_plan, name='create_reading_plan'),
path('reading/<int:plan_id>/', reading_plan_detail, name='reading_plan_detail'),
path('reading/<int:plan_id>/log/', log_progress, name='log_progress'),
path('reading/weekly-report/', weekly_report, name='weekly_report'),
path('reading/behind/', check_falling_behind, name='check_falling_behind'),
path('reading/dashboard', reading_dashboard, name='reading_dashboard'),
path('goals/create/', create_goal_view, name='create_goal'),
path('goal/<int:goal_id>/delete/', delete_goal, name='delete_goal'),
path('about/', about_shelfbuddy, name='about_shelfbuddy'),
path('reading-plan/<int:plan_id>/edit/',edit_reading_plan, name='edit_reading_plan'),
path('plan/<int:plan_id>/',reading_plan_detail, name='reading_plan_detail'),
]