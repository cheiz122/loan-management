from django.urls import path # type: ignore
from .views_api import AgentListCreate, CustomerListCreate, LoanListCreate, PaymentListCreate, LoanDetail, CustomerDetail

urlpatterns = [
    path('agents/', AgentListCreate.as_view(), name='agent-list-create'),
    path('customers/', CustomerListCreate.as_view(), name='customer-list-create'),
    path('loans/', LoanListCreate.as_view(), name='loan-list-create'),
    path('payments/', PaymentListCreate.as_view(), name='payment-list-create'),
    path('loans/<int:pk>/', LoanDetail.as_view(), name='loan-detail'),
    path('customers/<int:pk>/', CustomerDetail.as_view(), name='customer-detail'),
]
