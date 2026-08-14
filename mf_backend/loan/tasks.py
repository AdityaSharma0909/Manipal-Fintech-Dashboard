from celery import shared_task

from loan.services.calculate_accrued_interest import CalculateAccruedInterest
from loan.services.calculate_penalty import CalculatePenalty
from loan.services.demand_generation import DemandGeneration


@shared_task(name='loan_payment_jobs')
def interest_accrued():
    CalculateAccruedInterest()
    CalculatePenalty()
    DemandGeneration()