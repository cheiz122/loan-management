from django.core.management.base import BaseCommand # type: ignore
from django.utils import timezone # type: ignore
from myapp.models import Loan # type: ignore

class Command(BaseCommand):
    help = 'Update status of overdue loans'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        overdue_loans = Loan.objects.filter(due_date__lt=today, status='disbursed')
        updated_count = 0

        for loan in overdue_loans:
            loan.status = 'overdue'
            loan.save()
            updated_count += 1

        self.stdout.write(f'Successfully updated {updated_count} overdue loans.')
