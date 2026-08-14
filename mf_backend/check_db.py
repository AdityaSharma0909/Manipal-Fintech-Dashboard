import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'radian_backend.settings')
django.setup()

from onboarding_v2.models import LeadV2
from django.db.models import Count

print("=== STATUSES ===")
statuses = list(LeadV2.objects.values('status').annotate(c=Count('id')))
for s in statuses:
    print(s)

print("\n=== CITIES ===")
cities = list(LeadV2.objects.values('city').annotate(c=Count('id')))
for c in cities:
    print(c)
