import pandas as pd
from account.models import Account
from django.db import transaction


excel_file = pd.ExcelFile("./excel_script/upload_address/sheet.xlsx")
sheet1 = "Sheet1"


def upload_address_to_excel():
    # Read the sheet into a DataFrame
    df_employee = pd.read_excel(excel_file, sheet1)
    
    # Extract all customer IDs from the DataFrame
    all_customer_ids = df_employee["Customer ID"]
    
    # Create an empty list to store addresses
    addresses = []
    
    for emp_id in all_customer_ids:
        print(emp_id)
        with transaction.atomic():
            try:
                # Fetch the account with the given customer ID
                account = Account.objects.filter(customer_id=emp_id).first()
                
                if account:
                    # Fetch the user's permanent address
                    permanent_address = account.user_addresse.filter(
                        address_type='PERMANENT_ADDRESS'
                    ).first()
                    
                    if permanent_address:
                        # Format the address details into a single string
                        formatted_address = ", ".join(
                            filter(
                                None,  # Filter out None or empty values
                                [
                                    permanent_address.building_name,
                                    permanent_address.street_name,
                                    permanent_address.city,
                                    permanent_address.state,
                                    permanent_address.pincode,
                                    permanent_address.country,
                                ],
                            )
                        )
                    else:
                        formatted_address = "No Permanent Address"
                else:
                    formatted_address = ""
                
            except Exception as e:
                formatted_address = f"Error: {str(e)}"
            
            # Append the formatted address to the list
            addresses.append(formatted_address)
    
    # Add the addresses as a new column in the DataFrame
    df_employee["Address"] = addresses
    
    # Save the updated DataFrame back to a new Excel file
    output_file = "./excel_script/upload_address/Application_data_with_addresses.xlsx"
    df_employee.to_excel(output_file, index=False)
    print(f"Updated Excel file saved at: {output_file}")

upload_address_to_excel()

"""
python3 manage.py shell
exec(open('excel_script/upload_address/update_address.py').read())
"""