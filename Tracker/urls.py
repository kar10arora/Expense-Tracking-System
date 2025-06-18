from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_register_view, name='login'),
    path('register/', views.login_register_view, name='register'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('add-expense/', views.add_expense_view, name='add_expense'),
    path('reports/', views.reports_view, name='reports'),
    path('approve-expenses/', views.approve_expenses_view, name='approve_expenses'),  # Only for custom_admin and finance
    path('my-submissions/', views.my_submissions_view, name='my_submissions'),
    path('delete-expense/<int:id>/', views.delete_expense, name='delete_expense'),
    path('edit-expense/<int:id>/', views.edit_expense, name='edit_expense'),
    
    # API endpoints for chart data
    path('api/test/', views.test_api, name='test_api'),
    path('api/chart-data/', views.chart_data_api, name='chart_data_api'),
    path('api/reports-chart-data/', views.reports_chart_data_api, name='reports_chart_data_api'),
]