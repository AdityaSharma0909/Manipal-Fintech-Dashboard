from asset.models import Asset
from application.models import Application
from datetime import datetime
from dateutil import tz

import traceback


def get_totals(app):
    try:
        assets = app.asset_application.all()
        assets_count = len(assets)
        total_wastage = 0
        total_gross_weight = 0
        total_asset_price = 0
        text = ''
        for i in assets:
            total_wastage += i.wastage
            total_gross_weight += i.gross_weight
            total_asset_price += i.asset_price
            text += f"{i.karat_value}/"
        return assets_count, total_wastage, total_gross_weight, total_asset_price, text
    except Exception as e:
        traceback.print_exc()


apps = Application.objects.all()
c = 0
total_assets_count = 0

diff_total_wastage = 0
count_diff_total_wastage = 0
diff_total_gross_weight = 0
count_diff_total_gross_weight = 0
diff_total_asset_price = 0
count_diff_total_asset_price = 0
diff_total_eligible_amount = 0
count_diff_total_eligible_amount = 0

eligibleErrorCount = 0
for app in apps:
    assets_count, tw, tgw, tap, text = get_totals(app)
    if app.total_wastage != tw:
        diff_total_wastage += app.total_wastage - tw
        count_diff_total_wastage += 1
        print(
            f"{app.application_number}: total_wastage Difference: ",
            (app.total_wastage - tw),
        )
    if app.total_gross_weight != tgw:
        diff_total_gross_weight += app.total_gross_weight - tgw
        count_diff_total_gross_weight += 1
        print(
            f"{app.application_number}: total_gross_weight Difference: ",
            (app.total_gross_weight - tgw),
        )
    if app.total_asset_price != tap:
        diff_total_asset_price += app.total_asset_price - tap
        count_diff_total_asset_price += 1
        print(
            f"{app.application_number}: total_asset_price Difference: ",
            (app.total_asset_price - tap),
        )

    if assets_count > 0:
        eligibleAmount = round(float(tap) * float(app.product.ltv_percentage) * 0.01, 2)
        if app.eligible_amount != eligibleAmount:

            local_zone = tz.tzlocal()
            if (app.eligible_amount - eligibleAmount) >= 1.0:
                diff_total_eligible_amount += app.eligible_amount - eligibleAmount
                count_diff_total_eligible_amount += 1
                eligibleErrorCount += 1
                diffTime: datetime = datetime.now(tz=local_zone) - app.created_at.astimezone(local_zone)
                print(
                    # app.created_at.astimezone(local_zone).strftime("%Y-%m-%d"),
                    text,
                    app.application_number,
                    diffTime.total_seconds() / (60 * 60 * 24),
                    f"{app.Originatedby.first_name} {app.Originatedby.last_name} / {(app.eligible_amount - eligibleAmount)}",
                )
            # print(
            #     f"{app.application_number}: eligible_amount Difference: ",
            #     (app.eligible_amount - eligibleAmount),
            # )

    # print(f"{app.application_id}: {assets_count} asset traversed")
    total_assets_count += assets_count
    c += 1

print("\n\n")
print(f"Total {c} application found")
print(f"Total {total_assets_count} assets found")
print(f"Total {eligibleErrorCount} eligible error found")

if count_diff_total_wastage > 0:
    avg_diff_total_wastage = diff_total_wastage / count_diff_total_wastage
    print("avg_diff_total_wastage: ", avg_diff_total_wastage)
if count_diff_total_gross_weight > 0:
    avg_diff_total_gross_weight = (
        diff_total_gross_weight / count_diff_total_gross_weight
    )
    print("avg_diff_total_gross_weight: ", avg_diff_total_gross_weight)
if count_diff_total_asset_price > 0:
    avg_diff_total_asset_price = diff_total_asset_price / count_diff_total_asset_price
    print("avg_diff_total_asset_price: ", avg_diff_total_asset_price)
if count_diff_total_eligible_amount > 0:
    avg_diff_total_eligible_amount = (
        diff_total_eligible_amount / count_diff_total_eligible_amount
    )
    print("avg_diff_total_eligible_amount: ", avg_diff_total_eligible_amount)

"""
python3 manage.py shell
exec(open('excel_script/asset_calculation_tester_script.py').read())
"""


"""
Output on 11 March 2024 07:59:32 PM :

Total 2232 application found
Total 3076 assets found
Total 125 eligible error found
avg_diff_total_eligible_amount:  22198.541279999983
"""