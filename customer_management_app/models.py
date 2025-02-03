from django.db import models # type: ignore
from django.contrib.auth.models import User # type: ignore
from django.utils import timezone # type: ignore
from datetime import timedelta
from django.contrib.auth.models import AbstractUser # type: ignore
from django.contrib.auth.models import User # type: ignore
from decimal import Decimal

# Agent model for representing an agent, which has a one-to-one relationship with the User model
class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agent_profile')  # Relating each agent to a single user
    name = models.CharField(max_length=255)  # The name of the agent
    phone = models.CharField(max_length=20, blank=True, null=True)  # Phone number of the agent (optional)

    def __str__(self):
        return self.name  # Return the name of the agent for string representation

# Customer model to store customer-related details
class Customer(models.Model):
    name = models.CharField(max_length=255)  # Customer's full name
    id_number = models.CharField(max_length=8, unique=True)  # Unique ID for the customer
    phone = models.CharField(max_length=10)  # Customer's phone number
    email = models.EmailField()  # Customer's email address
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)  # The agent assigned to the customer
    active = models.BooleanField(default=True)  # Status indicating whether the customer is active
    location = models.CharField(max_length=100)  # Customer's location

    def __str__(self):
        return self.name  # Return the customer's name for string representation

    # Method to get the count of loans taken by the customer
    def loan_count(self):
        return self.loan_set.count()

    # Method to check if the customer has an active loan
    def has_active_loan(self):
        return self.loan_set.filter(status__in=['pending', 'approved', 'disbursed']).exists()

# Loan model to store loan details for customers
class Loan(models.Model):
    # Loan status choices
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('disbursed', 'Disbursed'),
        ('repaid', 'Repaid'),
        ('defaulted', 'Defaulted'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)  # The customer who took the loan
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Amount of the loan
    date_borrowed = models.DateField()  # Date when the loan was borrowed
    due_date = models.DateField()  # Due date for loan repayment
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')  # Current status of the loan
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=22.5)  # Interest rate for the loan

    @property
    def balance(self):
        # Calculate the current balance left on the loan
        return self.total_to_be_paid - self.total_payments_made

    @property
    def total_payments_made(self):
        # Calculate the total payments made for the loan
        payments = Payment.objects.filter(loan=self)
        total_paid = sum(payment.amount_paid for payment in payments)
        return total_paid

    @property
    def overdue_interest(self):
        # Calculate the overdue interest if the loan is not paid by the due date
        if self.due_date < timezone.now().date() and self.status not in ['repaid', 'defaulted']:
            overdue_days = (timezone.now().date() - self.due_date).days
            return self.amount * Decimal('0.05') * Decimal(overdue_days)
        return Decimal('0')

    @property
    def calculate_interest(self):
        # Calculate the interest to be applied on the loan
        return self.amount * (self.interest_rate / 100)

    @property
    def total_to_be_paid(self):
        # Calculate the total amount to be paid, including the original amount, interest, and overdue interest
        return self.amount + self.calculate_interest + self.overdue_interest

    def update_status(self):
        # Update the loan status to 'repaid' if the balance is paid off
        if self.balance <= 0 and self.status != 'repaid':
            self.status = 'repaid'
            self.save()

    def __str__(self):
        return f"Loan for {self.customer.name} - {self.amount}"  # Return a string representation of the loan

# Payment model to store loan payments
class Payment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)  # The loan associated with the payment
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)  # The amount paid for the loan
    date_paid = models.DateField(auto_now_add=True)  # Date when the payment was made

    # Override the save method to update the loan status after each payment
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Call the parent class's save method
        self.loan.update_status()  # Update the loan status after saving the payment

    def __str__(self):
        return f"Payment of {self.amount_paid} for {self.loan.customer.name}"  # Return a string representation of the payment
