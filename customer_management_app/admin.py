
from django.contrib import admin # type: ignore
from .models import Agent, Customer, Loan, Payment

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone')
    search_fields = ('name', 'phone')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'id_number', 'phone', 'email', 'agent')
    search_fields = ('name', 'id_number', 'phone', 'email')
    list_filter = ('agent',)

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('customer', 'amount', 'date_borrowed', 'due_date', 'status', 'balance', 'interest_rate')
    list_filter = ('status', 'due_date')
    search_fields = ('customer__name', 'amount')

    def save_model(self, request, obj, form, change):
        if obj.status == 'disbursed' and obj.balance == 0:
            obj.status = 'repaid'
        super().save_model(request, obj, form, change)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('loan', 'get_amount_paid', 'date_paid', 'get_loan_status')

    def get_amount_paid(self, obj):
        return obj.amount_paid

    get_amount_paid.short_description = 'Amount Paid'

    def get_loan_status(self, obj):
        return obj.loan.status

    get_loan_status.short_description = 'Loan Status'

    search_fields = ('loan__customer__name', 'loan__customer__id_number')
