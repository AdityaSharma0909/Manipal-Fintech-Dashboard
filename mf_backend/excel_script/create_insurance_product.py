from account.serializers import InsuranceSerializer
from utils.constants import LENDING_TYPE
from django.db import transaction

def Script():
    insurance_products = [
        {
            "product_name": "MU_6_1A",
            "company_name": "Radian Insurance",
            "company": "b6e03bad-dbe3-494c-b474-b9be297e85aa",
            "validity": 12,
            "coverage": "1 Adult",
            "insurance_policy_type": LENDING_TYPE.MSME_UNSECURED.value,
            "tenure": 6,
            "rate": 3.47
        },
        {
            "product_name": "MU_6_2A",
            "company_name": "Radian Insurance",
            "company": "b6e03bad-dbe3-494c-b474-b9be297e85aa",
            "validity": 12,
            "coverage": "2 Adult",
            "insurance_policy_type": LENDING_TYPE.MSME_UNSECURED.value,
            "tenure": 6,
            "rate": 6.60
        },
        {
            "product_name": "MU_12_1A",
            "company_name": "Radian Insurance",
            "company": "b6e03bad-dbe3-494c-b474-b9be297e85aa",
            "validity": 12,
            "coverage": "1 Adult",
            "insurance_policy_type": LENDING_TYPE.MSME_UNSECURED.value,
            "tenure": 12,
            "rate": 6.95
        },
        {
            "product_name": "MU_12_2A",
            "company_name": "Radian Insurance",
            "company": "b6e03bad-dbe3-494c-b474-b9be297e85aa",
            "validity": 12,
            "coverage": "2 Adult",
            "insurance_policy_type": LENDING_TYPE.MSME_UNSECURED.value,
            "tenure": 12,
            "rate": 13.20
        },
        {
            "product_name": "MU_18_1A",
            "company_name": "Radian Insurance",
            "company": "b6e03bad-dbe3-494c-b474-b9be297e85aa",
            "validity": 12,
            "coverage": "1 Adult",
            "insurance_policy_type": LENDING_TYPE.MSME_UNSECURED.value,
            "tenure": 18,
            "rate": 10.42
        },
        {
            "product_name": "MU_18_2A",
            "company_name": "Radian Insurance",
            "company": "b6e03bad-dbe3-494c-b474-b9be297e85aa",
            "validity": 12,
            "coverage": "2 Adult",
            "insurance_policy_type": LENDING_TYPE.MSME_UNSECURED.value,
            "tenure": 18,
            "rate": 19.80
        },
        {
            "product_name": "MU_24_1A",
            "company_name": "Radian Insurance",
            "company": "b6e03bad-dbe3-494c-b474-b9be297e85aa",
            "validity": 12,
            "coverage": "1 Adult",
            "insurance_policy_type": LENDING_TYPE.MSME_UNSECURED.value,
            "tenure": 24,
            "rate": 13.89
        },
        {
            "product_name": "MU_24_2A",
            "company_name": "Radian Insurance",
            "company": "b6e03bad-dbe3-494c-b474-b9be297e85aa",
            "validity": 12,
            "coverage": "2 Adult",
            "insurance_policy_type": LENDING_TYPE.MSME_UNSECURED.value,
            "tenure": 24,
            "rate": 26.40
        }
    ]

    with transaction.atomic():
        ser = InsuranceSerializer(data=insurance_products, many=True)
        if ser.is_valid():
            ser.save()
        else:
            print("Validation errors:", ser.errors)
    print(f"Total products added: {len(insurance_products)}")

Script()

# exec(open('excel_script/create_insurance_product.py').read())
    