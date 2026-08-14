import requests
import argparse
import os

def upload_branches(file_path, base_url, token, truncate=False, bank_name=None, lender_code=None):
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return

    url = f"{base_url.rstrip('/')}/onboarding_v2/admin/import-branches/"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    files = {
        'file': (os.path.basename(file_path), open(file_path, 'rb'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' if file_path.endswith('.xlsx') else 'text/csv')
    }
    
    data = {
        'truncate': str(truncate).lower(),
    }
    if bank_name:
        data['bank_name'] = bank_name
    if lender_code:
        data['lender_code'] = lender_code

    print(f"Uploading {file_path} to {url}...")
    try:
        response = requests.post(url, headers=headers, files=files, data=data)
        if response.status_code == 200:
            print("Successfully uploaded!")
            print("Server Response:", response.json())
        else:
            print(f"Failed to upload. Status Code: {response.status_code}")
            print("Error details:", response.text)
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bulk upload bank branches via API")
    parser.add_argument("file", help="Path to CSV/XLSX file")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL of the server (default: http://localhost:8000)")
    parser.add_argument("--token", required=True, help="JWT/Auth Token for admin user")
    parser.add_argument("--truncate", action="store_true", help="Clear existing branches before import")
    parser.add_argument("--bank", help="Default bank name")
    parser.add_argument("--lender", help="Lender code")

    args = parser.parse_args()
    upload_branches(args.file, args.url, args.token, truncate=args.truncate, bank_name=args.bank, lender_code=args.lender)
