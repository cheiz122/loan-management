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
    # Render the login page
    return render(request, 'login.html')

@login_required
def agent_dashboard(request):
    # Fetch agent-related data for the dashboard
    agent = request.user.agent_profile
    agent_id = agent.id
    
    # Fetch total loans disbursed (count and amount)
    loans_disbursed = Loan.objects.filter(customer__agent=agent, status='disbursed')
    total_loans_disbursed_count = loans_disbursed.count()
    total_loans_disbursed_amount = loans_disbursed.aggregate(Sum('amount'))['amount__sum'] or 0

    # Fetch total loans repaid (count and total amount)
    loans_repaid = Loan.objects.filter(customer__agent=agent, status='repaid')
    total_loans_repaid_count = loans_repaid.count()
    total_loans_repaid_amount = sum(loan.total_to_be_paid for loan in loans_repaid)

    # Fetch pending loans
    pending_loans_count = Loan.objects.filter(customer__agent=agent, status='approved').count()

    # Fetch approved loans (count and amount)
    approved_loans = Loan.objects.filter(customer__agent=agent, status='approved')
    approved_loans_count = approved_loans.count()
    approved_loans_amount = approved_loans.aggregate(Sum('amount'))['amount__sum'] or 0

    # Fetch upcoming loans due soon
    today = timezone.now().date()
    upcoming_loans = Loan.objects.filter(customer__agent=agent, due_date__gte=today, status='disbursed')
    upcoming_loans_due_soon = upcoming_loans.filter(due_date__lte=today + timedelta(days=2))

    # Fetch overdue loans
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
    # Render the agent dashboard with the fetched data
    return render(request, 'agent_dashboard.html', context)

@login_required
def customer_list(request):
    # Fetch all customers for the logged-in agent
    agent = request.user.agent_profile
    customers = Customer.objects.filter(agent=agent)

    active_customers = []
    inactive_customers = []

    # Sort customers into active and inactive based on their loan status
    for customer in customers:
        loans = customer.loan_set.all()
        if loans.filter(status__in=['approved', 'disbursed']).exists():
            active_customers.append(customer)
        else:
            inactive_customers.append(customer)

    # Fetch overdue loans for the agent
    overdue_loans = Loan.objects.filter(customer__agent=agent, due_date__lt=date.today()).exclude(status='repaid')

    context = {
        'active_customers': active_customers,
        'inactive_customers': inactive_customers,
        'overdue_loans': overdue_loans,
    }

    # Render the customer list with active/inactive customers and overdue loans
    return render(request, 'customer_list.html', context)


def loan_list(request):
    # Fetch all loans related to the logged-in agent's customers
    agent = request.user.agent_profile
    customers = Customer.objects.filter(agent=agent)
    loans = Loan.objects.filter(customer__in=customers)
    today = date.today()

    # Filter loans by their status
    disbursed_loans = loans.filter(status='disbursed')
    repaid_loans = loans.filter(status='repaid')
    pending_loans = loans.filter(status='pending')
    overdue_loans = disbursed_loans.filter(due_date__lt=today)

    # Calculate totals for the loans based on their status
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

    # Calculate grand totals across all statuses
    grand_total_amount = sum(t[0] for t in [disbursed_totals, repaid_totals, pending_totals, overdue_totals])
    grand_total_balance = sum(t[1] for t in [disbursed_totals, repaid_totals, pending_totals, overdue_totals])
    grand_total_overdue_interest = sum(t[2] for t in [disbursed_totals, repaid_totals, pending_totals, overdue_totals])
    grand_total_interest = sum(t[3] for t in [disbursed_totals, repaid_totals, pending_totals, overdue_totals])

    # Render the loan list page with totals for different loan statuses
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
    # Handle adding a new loan
    if request.method == 'POST':
        form = LoanForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.status = 'pending'  # Mark loan as pending initially
            loan.save()
            return redirect('loan_list')  # Redirect to the loan list after saving
    else:
        form = LoanForm()  # Display the form if it's a GET request
    return render(request, 'add_loan.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)
def edit_loan(request, pk):
    # Handle editing an existing loan (only superusers can edit)
    loan = get_object_or_404(Loan, pk=pk)
    if request.method == 'POST':
        form = LoanForm(request.POST, instance=loan)
        if form.is_valid():
            form.save()
            return redirect('loan_list')  # Redirect after saving
    else:
        form = LoanForm(instance=loan)
    return render(request, 'add_loan.html', {'form': form, 'loan': loan})
    messages.success(request, "Due reminders have been sent to all customers with loans due today.")
    return redirect('loan_list')

@login_required
def import_customers_excel(request):
    if request.method == 'POST' and request.FILES['excel_file']:
        form = UploadExcelForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['excel_file']
            # Read the Excel file into a Pandas DataFrame
            df = pd.read_excel(file)
            # Process each row in the DataFrame to create Customer objects
            for _, row in df.iterrows():
                customer = Customer(
                    name=row['Name'],
                    id_number=row['ID Number'],
                    phone=row['Phone'],
                    email=row['Email'],
                    agent=request.user.agent_profile,
                )
                customer.save()
            messages.success(request, "Customers have been successfully imported.")
            return redirect('customer_list')
        else:
            messages.error(request, "There was an error with the uploaded file.")
    else:
        form = UploadExcelForm()

    return render(request, 'import_customers_excel.html', {'form': form})

@login_required
def import_loans_excel(request):
    if request.method == 'POST' and request.FILES['excel_file']:
        form = UploadExcelForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['excel_file']
            # Read the Excel file into a Pandas DataFrame
            df = pd.read_excel(file)
            # Process each row in the DataFrame to create Loan objects
            for _, row in df.iterrows():
                customer = Customer.objects.get(id=row['Customer ID'])
                loan = Loan(
                    customer=customer,
                    amount=row['Amount'],
                    date_borrowed=row['Date Borrowed'],
                    due_date=row['Due Date'],
                    interest_rate=row['Interest Rate'],
                    status=row['Status'],
                )
                loan.save()
            messages.success(request, "Loans have been successfully imported.")
            return redirect('loan_list')
        else:
            messages.error(request, "There was an error with the uploaded file.")
    else:
        form = UploadExcelForm()

    return render(request, 'import_loans_excel.html', {'form': form})

@login_required
def add_agent(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')

        user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name, email=email)
        agent = Agent(user=user)
        agent.save()
        messages.success(request, 'Agent added successfully!')
        return redirect('agent_dashboard')
    else:
        return render(request, 'add_agent.html')

@login_required
def agent_profile(request):
    agent = request.user.agent_profile
    return render(request, 'agent_profile.html', {'agent': agent})

@login_required
def update_agent_profile(request):
    agent = request.user.agent_profile
    if request.method == 'POST':
        form = AgentProfileForm(request.POST, instance=agent)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('agent_profile')
    else:
        form = AgentProfileForm(instance=agent)

    return render(request, 'update_agent_profile.html', {'form': form, 'agent': agent})

@login_required
def delete_customer(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Customer deleted successfully.')
        return redirect('customer_list')

    return render(request, 'confirm_delete_customer.html', {'customer': customer})

@login_required
def delete_loan(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    if request.method == 'POST':
        loan.delete()
        messages.success(request, 'Loan deleted successfully.')
        return redirect('loan_list')

    return render(request, 'confirm_delete_loan.html', {'loan': loan})
  @login_required
def due_reminder(request):
    today = timezone.now().date()
    customers_with_due_loans = Loan.objects.filter(due_date=today, status='Active')
    
    for loan in customers_with_due_loans:
        customer = loan.customer
        send_due_reminder_email(customer.email, loan)
    
    messages.success(request, "Due reminders have been sent to all customers with loans due today.")
    return redirect('loan_list')

@login_required
def import_customers_excel(request):
    if request.method == 'POST' and request.FILES['excel_file']:
        form = UploadExcelForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['excel_file']
            # Read the Excel file into a Pandas DataFrame
            df = pd.read_excel(file)
            # Process each row in the DataFrame to create Customer objects
            for _, row in df.iterrows():
                customer = Customer(
                    name=row['Name'],
                    id_number=row['ID Number'],
                    phone=row['Phone'],
                    email=row['Email'],
                    agent=request.user.agent_profile,
                )
                customer.save()
            messages.success(request, "Customers have been successfully imported.")
            return redirect('customer_list')
        else:
            messages.error(request, "There was an error with the uploaded file.")
    else:
        form = UploadExcelForm()

    return render(request, 'import_customers_excel.html', {'form': form})

@login_required
def import_loans_excel(request):
    if request.method == 'POST' and request.FILES['excel_file']:
        form = UploadExcelForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['excel_file']
            # Read the Excel file into a Pandas DataFrame
            df = pd.read_excel(file)
            # Process each row in the DataFrame to create Loan objects
            for _, row in df.iterrows():
                customer = Customer.objects.get(id=row['Customer ID'])
                loan = Loan(
                    customer=customer,
                    amount=row['Amount'],
                    date_borrowed=row['Date Borrowed'],
                    due_date=row['Due Date'],
                    interest_rate=row['Interest Rate'],
                    status=row['Status'],
                )
                loan.save()
            messages.success(request, "Loans have been successfully imported.")
            return redirect('loan_list')
        else:
            messages.error(request, "There was an error with the uploaded file.")
    else:
        form = UploadExcelForm()

    return render(request, 'import_loans_excel.html', {'form': form})

@login_required
def add_agent(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')

        user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name, email=email)
        agent = Agent(user=user)
        agent.save()
        messages.success(request, 'Agent added successfully!')
        return redirect('agent_dashboard')
    else:
        return render(request, 'add_agent.html')

@login_required
def agent_profile(request):
    agent = request.user.agent_profile
    return render(request, 'agent_profile.html', {'agent': agent})

@login_required
def update_agent_profile(request):
    agent = request.user.agent_profile
    if request.method == 'POST':
        form = AgentProfileForm(request.POST, instance=agent)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('agent_profile')
    else:
        form = AgentProfileForm(instance=agent)

    return render(request, 'update_agent_profile.html', {'form': form, 'agent': agent})

@login_required
def delete_customer(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Customer deleted successfully.')
        return redirect('customer_list')

    return render(request, 'confirm_delete_customer.html', {'customer': customer})

@login_required
def delete_loan(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    if request.method == 'POST':
        loan.delete()
        messages.success(request, 'Loan deleted successfully.')
        return redirect('loan_list')

    return render(request, 'confirm_delete_loan.html', {'loan': loan})
