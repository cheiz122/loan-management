# customer_management_app/dash_apps/loan_dashboard.py
from django_plotly_dash import DjangoDash  # type: ignore
import dash_core_components as dcc  # type: ignore
import dash_html_components as html  # type: ignore
from dash.dependencies import Input, Output  # type: ignore
from django.utils import timezone  # type: ignore
from .models import Loan  # type: ignore
from django.db.models import Sum  # type: ignore
import plotly.graph_objs as go

app = DjangoDash('LoanDashboard')

app.layout = html.Div([
    dcc.Graph(id='loans-disbursed'),
    dcc.Graph(id='loans-repaid'),
    dcc.Interval(
        id='interval-component',
        interval=60 * 1000,  # in milliseconds
        n_intervals=0
    )
])

@app.callback(
    [Output('loans-disbursed', 'figure'),
     Output('loans-repaid', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_graphs(n):
    today = timezone.now().date()
    loans_disbursed = Loan.objects.filter(status='disbursed')
    loans_repaid = Loan.objects.filter(status='repaid')

    # Total loans disbursed
    total_disbursed_amount = loans_disbursed.aggregate(Sum('amount'))['amount__sum'] or 0
    total_disbursed_count = loans_disbursed.count()

    # Total loans repaid
    total_repaid_amount = sum(loan.total_to_be_paid() for loan in loans_repaid)
    total_repaid_count = loans_repaid.count()

    disbursed_figure = {
        'data': [go.Bar(x=['Total Disbursed'], y=[total_disbursed_amount])],
        'layout': go.Layout(title='Total Loans Disbursed')
    }

    repaid_figure = {
        'data': [go.Bar(x=['Total Repaid'], y=[total_repaid_amount])],
        'layout': go.Layout(title='Total Loans Repaid')
    }

    return disbursed_figure, repaid_figure
