import pandas as pd
import re
from django.db import transaction
from branch.models import Branch


excel_file = './excel_script/lat_long_sheet.xlsx'
df = pd.read_excel(excel_file)

# Function to convert DMS to DD
def dms_to_dd(dms_str):
    dms_pattern = re.match(r"(\d+)[°](\d+)'(\d+\.\d+)\"([NSEW])", dms_str)
    degrees = float(dms_pattern.group(1))
    minutes = float(dms_pattern.group(2))
    seconds = float(dms_pattern.group(3))
    direction = dms_pattern.group(4)

    dd = degrees + minutes / 60 + seconds / 3600
    if direction in ['S', 'W']:
        dd = -dd
    
    return dd

# Variables to track branches
updated_count = 0
not_updated_count = 0

for index, row in df.iterrows():
    branch_name = row['Branch']
    location = row['Location']

    try:
        lat_dms, long_dms = location.split(' ', 1)
        lat_dd = dms_to_dd(lat_dms)
        long_dd = dms_to_dd(long_dms)

        with transaction.atomic():
            branch = Branch.objects.get(branch_name=branch_name)
            branch.latitude = str(lat_dd)
            branch.longitude = str(long_dd)
            branch.save()
            print(f"Updated branch: {branch_name} with Latitude: {lat_dd}, Longitude: {long_dd}")
            updated_count += 1
    except Branch.DoesNotExist:
        print(f"Branch not found: {branch_name}")
        not_updated_count += 1
    except ValueError as e:
        print(f"Error processing location for branch {branch_name}: {e}")
        not_updated_count += 1

# Print the total number of updated and not updated branches
print(f"Total branches updated: {updated_count}")
print(f"Total branches not updated: {not_updated_count}")


# exec(open('excel_script/convert_dms_to_dd.py').read())