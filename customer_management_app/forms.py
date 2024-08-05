# forms.py
from django import forms # type: ignore
from .models import Customer, Loan , Payment

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'id_number', 'phone', 'email', 'location']  # Include 'location' field in the form
    def clean_id_number(self):
        id_number = self.cleaned_data['id_number']
        if len(id_number) != 8:
            raise forms.ValidationError("ID number must be exactly 8 characters long.")
        return id_number
    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if len(phone) > 10:
            raise forms.ValidationError("Phone number must be 10 characters or fewer.")
        return phone

    def __init__(self, *args, **kwargs):
        self.agent = kwargs.pop('agent', None)  # Retrieve agent from kwargs
        super(CustomerForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(CustomerForm, self).save(commit=False)
        if self.agent:
            instance.agent = self.agent
        if commit:
            instance.save()
        return instance

class LoanForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ['customer', 'amount', 'date_borrowed', 'due_date', 'status']
        widgets = {
            'date_borrowed': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(LoanForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['status'].disabled = False  # Enable editing status for existing loans
        else:
            self.fields['status'].initial = 'pending'
            self.fields['status'].disabled = True  # Disable status field for new loans

    def clean_customer(self):
        customer = self.cleaned_data['customer']
        if self.instance.pk is None:  # Only check for new loans
            if customer.has_active_loan():
                raise forms.ValidationError(f"{customer.name} already has an active loan.")
        return customer

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['loan', 'amount_paid']

    def clean_amount_paid(self):
        amount_paid = self.cleaned_data['amount_paid']
        loan = self.cleaned_data.get('loan')

        if loan and amount_paid > loan.balance:
            raise forms.ValidationError("Amount paid cannot be more than the remaining balance.")
        return amount_paid

class UploadExcelForm(forms.Form):
    file = forms.FileField()


    



 #balance = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    #def save(self, *args, **kwargs):
      #  if not self.pk:  # Only calculate interest_rate if creating a new loan
       #     self.interest_rate = Decimal('22.5')  # Set interest rate as 22.5%
       # self.balance = self.amount + self.calculate_interest() - self.total_amount_paid
        #super(Loan, self).save(*args, **kwargs)         