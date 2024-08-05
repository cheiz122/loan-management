from django.db import models # type: ignore
from django.contrib.auth.models import User # type: ignore
from django.utils import timezone # type: ignore
from datetime import timedelta
from django.contrib.auth.models import AbstractUser # type: ignore
from django.contrib.auth.models import User # type: ignore
from decimal import Decimal

from decimal import Decimal
from decimal import Decimal


class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agent_profile')
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name

class Customer(models.Model):
    name = models.CharField(max_length=255)
    id_number = models.CharField(max_length=8, unique=True)
    phone = models.CharField(max_length=10)
    email = models.EmailField()
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    def loan_count(self):
        return self.loan_set.count()

    def has_active_loan(self):
        return self.loan_set.filter(status__in=['pending', 'approved', 'disbursed']).exists()

class Loan(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('disbursed', 'Disbursed'),
        ('repaid', 'Repaid'),
        ('defaulted', 'Defaulted'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_borrowed = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=22.5)

    @property
    def balance(self):
        return self.total_to_be_paid - self.total_payments_made

    @property
    def total_payments_made(self):
        payments = Payment.objects.filter(loan=self)
        total_paid = sum(payment.amount_paid for payment in payments)
        return total_paid

    @property
    def overdue_interest(self):
        if self.due_date < timezone.now().date() and self.status not in ['repaid', 'defaulted']:
            overdue_days = (timezone.now().date() - self.due_date).days
            return self.amount * Decimal('0.05') * Decimal(overdue_days)
        return Decimal('0')

    @property
    def calculate_interest(self):
        return self.amount * (self.interest_rate / 100)

    @property
    def total_to_be_paid(self):
        return self.amount + self.calculate_interest + self.overdue_interest

    def update_status(self):
        if self.balance <= 0 and self.status != 'repaid':
            self.status = 'repaid'
            self.save()

    def __str__(self):
        return f"Loan for {self.customer.name} - {self.amount}"

class Payment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    date_paid = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.loan.update_status()

    def __str__(self):
        return f"Payment of {self.amount_paid} for {self.loan.customer.name}"
