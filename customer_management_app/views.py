from datetime import date, timedelta  # type: ignore
from decimal import Decimal  # type: ignore
import csv  # type: ignore
import pandas as pd  # type: ignore

from django.db import transaction  # type: ignore
from django.db.models import Sum, F  # type: ignore
from django.shortcuts import render, get_object_or_404, redirect  # type: ignore
from django.http import HttpResponse  # type: ignore
from django.template.loader import get_template  # type: ignore
from django.core.mail import send_mail  # type: ignore
from django.contrib import messages  # type: ignore
from django.contrib.auth import authenticate, login, logout  # type: ignore
from django.contrib.auth.decorators import login_required, user_passes_test  # type: ignore
from django.contrib.auth.mixins import UserPassesTestMixin  # type: ignore
from django.views.generic import UpdateView  # type: ignore
from django.urls import reverse_lazy  # type: ignore
from django.core.exceptions import ObjectDoesNotExist  # type: ignore
from django.utils.dateparse import parse_date  # type: ignore
from django.utils import timezone  # type: ignore

from xhtml2pdf import pisa  # type: ignore

from .models import Agent, Customer, Loan, Payment  # type: ignore
from .forms import LoanForm, PaymentForm, CustomerForm, UploadExcelForm  # type: ignore

def home(request):
    return render(request, 'login.html')

@login_required
def agent_dashboard(request):
    agent = request.user.agent_profile
    agent_id = agent.id
    # Total loans disbursed (count and sum of amounts)
    loans_disbursed = Loan.objects.filter(customer__agent=agent, status='disbursed')
    total_loans_disbursed_count = loans_disbursed.count()
    total_loans_disbursed_amount = loans_disbursed.aggregate(Sum('amount'))['amount__sum'] or 0

    # Total loans repaid (count and sum of total amounts to be paid)
    loans_repaid = Loan.objects.filter(customer__agent=agent, status='repaid')
    total_loans_repaid_count = loans_repaid.count()
    total_loans_repaid_amount = sum(loan.total_to_be_paid for loan in loans_repaid)

    # Pending loans
    pending_loans_count = Loan.objects.filter(customer__agent=agent, status='approved').count()

    approved_loans = Loan.objects.filter(customer__agent=agent, status='approved')
    approved_loans_count = approved_loans.count()
    approved_loans_amount = approved_loans.aggregate(Sum('amount'))['amount__sum'] or 0

    # Upcoming loans due soon
    today = timezone.now().date()
    upcoming_loans = Loan.objects.filter(customer__agent=agent, due_date__gte=today, status='disbursed')
    upcoming_loans_due_soon = upcoming_loans.filter(due_date__lte=today + timedelta(days=2))

    # Overdue loans
    overdue_loans = Loan.objects.filter(customer__agent=agent, due_date__lt=today, status='disbursed')
    
    context = {
        'total_loans_disbursed_count': total_loans_disbursed_count,
        'total_loans_disbursed_amount': total_loans_disbursed_amount,
        'total_loans_repaid_count': total_loans_repaid_count,
        'total_loans_repaid_amount': total_loans_repaid_amount,
        'approved_loans_count': approved_loans_count,
        'approved_loans_amount': approved_loans_amount,
        'pending_loans_count': pending_loans_count,
        'upcoming_loans_due_soon': upcoming_loans_due_soon,
        'overdue_loans': overdue_loans,
    }
    return render(request, 'agent_dashboard.html', context)

@login_required
def customer_list(request):
    agent = request.user.agent_profile
    customers = Customer.objects.filter(agent=agent)

    active_customers = []
    inactive_customers = []

    for customer in customers:
        loans = customer.loan_set.all()
        if loans.filter(status__in=['approved', 'disbursed']).exists():
            active_customers.append(customer)
        else:
            inactive_customers.append(customer)

    overdue_loans = Loan.objects.filter(customer__agent=agent, due_date__lt=date.today()).exclude(status='repaid')

    context = {
        'active_customers': active_customers,
        'inactive_customers': inactive_customers,
        'overdue_loans': overdue_loans,
    }

    return render(request, 'customer_list.html', context)


def loan_list(request):
    agent = request.user.agent_profile
    customers = Customer.objects.filter(agent=agent)
    loans = Loan.objects.filter(customer__in=customers)
    today = date.today()

    # Filter loans based on status
    disbursed_loans = loans.filter(status='disbursed')
    repaid_loans = loans.filter(status='repaid')
    pending_loans = loans.filter(status='pending')
    overdue_loans = disbursed_loans.filter(due_date__lt=today)

    # Calculate totals for each status
    def calculate_totals(loan_queryset):
        total_amount = loan_queryset.aggregate(total_amount=Sum('amount'))['total_amount'] or Decimal('0.00')
        total_balance = sum(loan.balance for loan in loan_queryset)
        total_overdue_interest = sum(loan.overdue_interest for loan in loan_queryset)
        total_interest = sum(loan.calculate_interest for loan in loan_queryset)
        return total_amount, total_balance, total_overdue_interest, total_interest

    disbursed_totals = calculate_totals(disbursed_loans)
    repaid_totals = calculate_totals(repaid_loans)
    pending_totals = calculate_totals(pending_loans)
    overdue_totals = calculate_totals(overdue_loans)

    grand_total_amount = sum(t[0] for t in [disbursed_totals, repaid_totals, pending_totals, overdue_totals])
    grand_total_balance = sum(t[1] for t in [disbursed_totals, repaid_totals, pending_totals, overdue_totals])
    grand_total_overdue_interest = sum(t[2] for t in [disbursed_totals, repaid_totals, pending_totals, overdue_totals])
    grand_total_interest = sum(t[3] for t in [disbursed_totals, repaid_totals, pending_totals, overdue_totals])

    return render(request, 'loan_list.html', {
        'disbursed_loans': disbursed_loans,
        'repaid_loans': repaid_loans,
        'pending_loans': pending_loans,
        'overdue_loans': overdue_loans,
        'today': today,
        'disbursed_totals': disbursed_totals,
        'repaid_totals': repaid_totals,
        'pending_totals': pending_totals,
        'overdue_totals': overdue_totals,
        'grand_total_amount': grand_total_amount,
        'grand_total_balance': grand_total_balance,
        'grand_total_overdue_interest': grand_total_overdue_interest,
        'grand_total_interest': grand_total_interest,
    })

 
@login_required
def add_loan(request):
    if request.method == 'POST':
        form = LoanForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.status = 'pending'
            loan.save()
            return redirect('loan_list')
    else:
        form = LoanForm()
    return render(request, 'add_loan.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)
def edit_loan(request, pk):
    loan = get_object_or_404(Loan, pk=pk)
    if request.method == 'POST':
        form = LoanForm(request.POST, instance=loan)
        if form.is_valid():
            form.save()
            return redirect('loan_list')
    else:
        form = LoanForm(instance=loan)
    return render(request, 'add_loan.html', {'form': form, 'loan': loan})

class LoanUpdateView(UserPassesTestMixin, UpdateView):
    model = Loan
    form_class = LoanForm
    template_name = 'add_loan.html'
    success_url = reverse_lazy('loan_list')

    def test_func(self):
        return self.request.user.is_superuser

@login_required
def loan_detail(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id)
    return render(request, 'loan_detail.html', {'loan': loan})

@login_required
def export_loans_csv(request):
    agent = request.user.agent_profile
    loans = Loan.objects.filter(customer__agent=agent)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="loans.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Customer', 'Amount', 'Date Borrowed', 'Due Date', 'Status', 'Interest Rate'])

    for loan in loans:
        writer.writerow([loan.customer.name, loan.amount, loan.date_borrowed, loan.due_date, loan.status, loan.interest_rate])

    return response

@login_required
def export_loans_pdf(request):
    agent = request.user.agent_profile
    loans = Loan.objects.filter(customer__agent=agent)

    template_path = 'loan_list_pdf.html'
    context = {'loans': loans}
    
    template = get_template(template_path)
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="loans.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

@login_required
@transaction.atomic
def add_payment(request, loan_id=None):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.date_paid = date.today()
            try:
                if payment.loan.customer.agent != request.user.agent_profile:
                    raise PermissionError("You are not authorized to add payment for this loan.")
                payment.save()
                messages.success(request, 'Payment added successfully.')
                return redirect('loan_list')
            except PermissionError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, 'An error occurred while processing the payment.')
    else:
        form = PaymentForm()

    if loan_id:
        loan = get_object_or_404(Loan, pk=loan_id)
        if loan.customer.agent != request.user.agent_profile:
            messages.error(request, 'You are not authorized to add payment for this loan.')
            return redirect('loan_list')
        form.fields['loan'].queryset = Loan.objects.filter(pk=loan_id)
    elif 'customer' in request.GET:
        try:
            customer_id = int(request.GET.get('customer'))
            form.fields['loan'].queryset = Loan.objects.filter(customer_id=customer_id, status__in=['approved', 'disbursed']).order_by('date_borrowed')
        except (ValueError, TypeError):
            form.fields['loan'].queryset = Loan.objects.none()
    else:
        form.fields['loan'].queryset = Loan.objects.none()

    return render(request, 'add_payment.html', {'form': form})

@login_required
def export_customers_csv(request):
    agent = request.user.agent_profile
    customers = Customer.objects.filter(agent=agent)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="customers.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Name', 'ID Number', 'Phone', 'Email', 'Date Borrowed', 'Due Date', 'Amount', 'Interest Rate'])

    for customer in customers:
        loans = Loan.objects.filter(customer=customer)
        for loan in loans:
            writer.writerow([customer.name, customer.id_number, customer.phone, customer.email, loan.date_borrowed, loan.due_date, loan.amount, loan.interest_rate])
    
    return response

@login_required
def export_customers_pdf(request):
    agent = request.user.agent_profile
    customers = Customer.objects.filter(agent=agent)

    template_path = 'customer_list_pdf.html'
    context = {'customers': customers}

    template = get_template(template_path)
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="customers.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('PDF creation error', status=400)
    
    return response

def custom_logout(request):
    logout(request)
    return redirect('home')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('admin:index')
            else:
                return redirect('agent_dashboard')
        else:
            return render(request, 'login.html', {'error_message': 'Invalid username or password'})
    else:
        return render(request, 'login.html')

@login_required
def add_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.agent = request.user.agent_profile
            customer.save()
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, 'add_customer.html', {'form': form})

@login_required
def customer_payment_history(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    loans = customer.loan_set.all()
    payments = Payment.objects.filter(loan__customer=customer)

    return render(request, 'customer_payment_history.html', {
        'customer': customer,
        'loans': loans,
        'payments': payments
    })

@login_required
def send_due_reminders(request):
    today = date.today()
    due_loans = Loan.objects.filter(due_date=today)

    for loan in due_loans:
        subject = "Repayment of Loan"
        message = (f"Dear {loan.customer.name},\n\n"
                   f"This is a reminder that your loan of amount {loan.amount} is due today. "
                   f"Your total balance is {loan.balance}. Please make the payment at your earliest convenience "
                   f"to avoid any penalties.\n\n"
                   f"Thank you,\nYour Loan Management Team")
        recipient_list = [loan.customer.email]

        send_mail(subject, message, 'chegep122@gmail.com', recipient_list)

    messages.success(request, "Due reminders have been sent to all customers with loans due today.")
    return redirect('loan_list')

