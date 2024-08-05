from django.urls import path # type: ignore
from django.contrib import admin # type: ignore
from customer_management_app import admin # type: ignore
from . import views
from . import views
#from django_plotly_dash.views import serve_dash # type: ignore
urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.agent_dashboard, name='agent_dashboard'),
    path('customers/', views.customer_list, name='customer_list'),
    path('loans/', views.loan_list, name='loan_list'),
    path('add_customer/', views.add_customer, name='add_customer'),
    path('add_loan/', views.add_loan, name='add_loan'),
    path('loans/<int:loan_id>/', views.loan_detail, name='loan_detail'),
    path('export/customers/csv/', views.export_customers_csv, name='export_customers_csv'),
    path('export/customers/pdf/', views.export_customers_pdf, name='export_customers_pdf'),
    path('loans/export/csv/', views.export_loans_csv, name='export_loans_csv'),
    path('loans/export/pdf/', views.export_loans_pdf, name='export_loans_pdf'),
    path('payment/add/<int:loan_id>/', views.add_payment, name='add_payment'),  # URL for adding payments
    path('accounts/logout/', views.custom_logout, name='logout'),
    path('login/', views.login_view, name='login_view'),
    path('customer_payment_history/<int:customer_id>/', views.customer_payment_history, name='customer_payment_history'),
    #path('upload/', views.upload_excel, name='upload_excel'),  # Updated URL pattern
    path('send_due_reminders/', views.send_due_reminders, name='send_due_reminders'),
    #path('django_plotly_dash/<str:app_name>/', serve_dash, name='serve_dash'),
    
]

