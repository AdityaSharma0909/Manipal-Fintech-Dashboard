from asset.models import Asset
from application.models import Application

import traceback

def get_totals(app):
    try:
        assets = app.asset_application.all()
        assets_count = len(assets)
        total_wastage = 0
        total_gross_weight = 0
        total_asset_price = 0
        for i in assets:
            total_wastage += i.wastage
            total_gross_weight += i.gross_weight
            total_asset_price += i.asset_price
        return assets_count, total_wastage, total_gross_weight, total_asset_price
    except Exception as e:
        traceback.print_exc()


apps = Application.objects.all()
c = 0
total_assets_count = 0
for app in apps:
    assets_count, tw, tgw, tap = get_totals(app)
    app.total_wastage = tw
    app.total_gross_weight = tgw
    app.total_asset_price = tap
    app.save()
    print(f"{app.application_id}: {assets_count} asset traversed")
    total_assets_count += assets_count
    c += 1

print(f"Total {c} application updated")
print(f"Total {total_assets_count} assets found")



"""
python3 manage.py shell
exec(open('excel_script/asset_calculation_of_application.py').read())
"""



"""
Output on 11 March 2024 07:59:32 PM :

Total 2232 application updated
Total 3076 assets found

"""