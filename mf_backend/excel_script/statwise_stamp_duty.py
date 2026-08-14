
from branch.models import Branch, StampDutyCharges



RADIAN_OFFICE_IN_INDIA=['Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chandigarh', 'Chhattisgarh', 'Dadra and Nagar Haveli', 'Daman and Diu', 'Delhi', 'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jammu and Kashmir', 'Jharkhand', 'Karnataka', 'Kerala', 'Ladakh', 'Lakshadweep', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Puducherry', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal']

branches = Branch.objects.filter(state='Uttar Pradesh')
for b in branches:
    s = StampDutyCharges.objects.create(branch=b, minimum_amount=0, stamp_duty_amount=0)
    print(s)

branches = Branch.objects.filter(state='Andhra Pradesh')
for b in branches:
    s = StampDutyCharges.objects.create(branch=b, minimum_amount=0, stamp_duty_amount=130)
    print(s)

branches = Branch.objects.filter(state='Karnataka')
for b in branches:
    s = StampDutyCharges.objects.create(branch=b, minimum_amount=100000, maximum_amount=1000000, stamp_duty_percent=0.15)
    print(s)
    s = StampDutyCharges.objects.create(branch=b, minimum_amount=1000000, stamp_duty_percent=0.25)
    print(s)


branches = Branch.objects.filter(state='Madhya Pradesh')
for b in branches:
    s = StampDutyCharges.objects.create(branch=b, minimum_amount=0, stamp_duty_percent=0.25)
    print(s)


branches = Branch.objects.filter(state='Tamil Nadu')
for b in branches:
    s = StampDutyCharges.objects.create(branch=b, minimum_amount=0, stamp_duty_amount=50)
    print(s)
