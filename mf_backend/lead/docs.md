Here’s the full set of “copy-paste” commands pointing to http://91.203.132.113 so you can run the entire flow on your server. Replace placeholders (IDs, presigned URLs, file paths) as you go.

Get an auth token via user login (using your credentials)
curl --location "http://91.203.132.113/user/login/" \
  --header "Content-Type: application/json" \
  --data-raw '{
    "username": "00011",
    "password": "Getafix@123"
  }'
# Save the token from the response as TOKEN (update below)
Create a lead (use a fresh phone to avoid uniqueness errors)
TOKEN="<access_token_from_login>"
curl -s -X POST "http://91.203.132.113/api/v2/onboarding/leads/" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "contact_number": "9000011111",
    "customer_name": "Test User",
    "product_category": "LOAN",
    "product_subcategory": "BALANCE_TRANSFER",
    "amount": "150000",
    "pincode": "560001",
    "source": "SELF"
  }'
# Save lead id (lead_uuid) from response
Create one application for the lead
LEAD_ID="<lead_uuid>"
APP_RESP=$(curl -s -X POST "http://91.203.132.113/api/v2/onboarding/applications/" \
  -H "Authorization: Bearer 24rbKCauxv3WVHsqj2O7z0v67tGCHT" -H "Content-Type: application/json" \
  -d '{"lead": "'"${LEAD_ID}"'","lending_partner": null,"loan_type": null}')
echo "$APP_RESP"
APP_ID=$(echo "$APP_RESP" | python -c "import sys,json; d=json.load(sys.stdin); print(d['data']['application']['application_id'])")
echo "APP_ID=$APP_ID"
# If you already have an application, set it directly:
APP_ID="APP-F5D8C7AA1DC1"
Stage PAN
curl -s -X POST "http://91.203.132.113/api/v2/onboarding/applications/${APP_ID}/stage/" \
  -H "Authorization: Bearer 24rbKCauxv3WVHsqj2O7z0v67tGCHT" -H "Content-Type: application/json" \
  -d '{"stage":"PAN","is_complete":true,
       "payload":{"contact_number":"9000011111","pan_number":"ABCDE1234F",
                  "name_on_pan":"TEST USER","dob_as_per_pan":"1990-01-01"}}'
Stage BASIC
curl -s -X POST "http://91.203.132.113/api/v2/onboarding/applications/${APP_ID}/stage/" \
  -H "Authorization: Bearer 24rbKCauxv3WVHsqj2O7z0v67tGCHT" -H "Content-Type: application/json" \
  -d '{"stage":"BASIC","is_complete":true,
       "payload":{"full_name_as_pan":"TEST USER","dob":"1990-01-01","dob_as_per_pan":"1990-01-01",
                  "phone_number":"9000011111","gender":"MALE","aadhar_number":"123412341234"}}'
Stage ADDRESS
curl -s -X POST "http://91.203.132.113/api/v2/onboarding/applications/${APP_ID}/stage/" \
  -H "Authorization: Bearer 24rbKCauxv3WVHsqj2O7z0v67tGCHT" -H "Content-Type: application/json" \
  -d '{"stage":"ADDRESS","is_complete":true,
       "payload":{"permanent":{"address_line1":"123 Main St","pincode":"560001",
                               "state":"KA","district":"BLR","city":"BLR"},
                  "current_same_as_permanent":true}}'
Presign and upload documents (example for PAN; repeat for other docs)
PAN_PRESIGN=$(curl -s -X POST "http://91.203.132.113/api/v2/onboarding/applications/${APP_ID}/documents/presign/" \
  -H "Authorization: Bearer 24rbKCauxv3WVHsqj2O7z0v67tGCHT" -H "Content-Type: application/json" \
  -d '{"document_type":"PAN","filename":"pan.jpg","content_type":"image/jpeg"}')
PUT_URL=$(echo "$PAN_PRESIGN" | python -c "import sys,json; d=json.load(sys.stdin); print(d['data']['put_url'])")
GET_URL_PAN=$(echo "$PAN_PRESIGN" | python -c "import sys,json; d=json.load(sys.stdin); print(d['data']['get_url'])")

curl -X PUT "$PUT_URL" --upload-file /path/to/pan.jpg
Repeat for AADHAAR_FRONT, AADHAAR_BACK, VOTER_ID, DRIVING_LICENSE, PASSPORT, OTHER (bureau PDF), etc., and save their GET URLs.

Stage DOCUMENTS (use the GET URLs you captured)
curl -s -X POST "http://91.203.132.113/api/v2/onboarding/applications/${APP_ID}/stage/" \
  -H "Authorization: Bearer 24rbKCauxv3WVHsqj2O7z0v67tGCHT" -H "Content-Type: application/json" \
  -d '{
    "stage":"DOCUMENTS","is_complete":true,
    "payload":[
      {"document_type":"PAN","status":"UPLOADED","file_url":"<pan_get_url>"},
      {"document_type":"AADHAAR_FRONT","status":"UPLOADED","file_url":"<aadhaar_front_get_url>"},
      {"document_type":"AADHAAR_BACK","status":"UPLOADED","file_url":"<aadhaar_back_get_url>"},
      {"document_type":"VOTER_ID","status":"UPLOADED","file_url":"<voter_get_url>"},
      {"document_type":"DRIVING_LICENSE","status":"UPLOADED","file_url":"<dl_get_url>"},
      {"document_type":"PASSPORT","status":"UPLOADED","file_url":"<passport_get_url>"},
      {"document_type":"OTHER","status":"UPLOADED","file_url":"<bureau_pdf_get_url>","sub_type":"bureau_report"}
    ]
  }'
Stage PERSONAL
curl -s -X POST "http://91.203.132.113/api/v2/onboarding/applications/${APP_ID}/stage/" \
  -H "Authorization: Bearer 24rbKCauxv3WVHsqj2O7z0v67tGCHT" -H "Content-Type: application/json" \
  -d '{"stage":"PERSONAL","is_complete":true,
       "payload":{"full_name":"TEST USER","dob":"1990-01-01","dob_as_per_pan":"1990-01-01",
                  "gender":"MALE","mobile_number":"9000011111","marital_status":"UNMARRIED",
                  "profession":"SALARY","category":"GENERAL","religion":"HINDU"}}'
Stage ADDRESS_SECONDARY (+POA)
curl -s -X POST "http://91.203.132.113/api/v2/onboarding/applications/${APP_ID}/stage/" \
  -H "Authorization: Bearer 24rbKCauxv3WVHsqj2O7z0v67tGCHT" -H "Content-Type: application/json" \
  -d '{"stage":"ADDRESS_SECONDARY","is_complete":true,
       "payload":{"permanent":{"address_line1":"123 Main St","pincode":"560001","state":"KA","district":"BLR","city":"BLR"},
                  "current_same_as_permanent":true,
                  "poa":[{"document_type":"AADHAAR_FRONT","status":"UPLOADED","file_url":"<poa_get_url>"}]}}'
Stage GOLD (include totals and packet/appraiser info)
curl -s -X POST "http://91.203.132.113/api/v2/onboarding/applications/${APP_ID}/stage/" \
  -H "Authorization: Bearer 24rbKCauxv3WVHsqj2O7z0v67tGCHT" -H "Content-Type: application/json" \
  -d '{"stage":"GOLD","is_complete":true,
       "payload":{"packet_id":"PKT123","barcode_id":"BAR123","appraiser_id":"APP123","appraiser_name":"John Doe",
                  "items":[{"type_of_jewellery":"RING","number_of_articles":1,"purity":"22K",
                            "gross_weight":"10.0","net_weight":"9.5","net_adjusted_weight":"9.3",
                            "gross_value":"60000","net_adjusted_value":"58000"}],
                  "gross_weight_total":"10.0","gross_value_total":"60000",
                  "net_adjusted_weight_total":"9.3","net_adjusted_value_total":"58000"}}'
Stage LOAN
curl -s -X POST "http://91.203.132.113/api/v2/onboarding/applications/${APP_ID}/stage/" \
  -H "Authorization: Bearer 24rbKCauxv3WVHsqj2O7z0v67tGCHT" -H "Content-Type: application/json" \
  -d '{"stage":"LOAN","is_complete":true,
       "payload":{"eligible_amount":"100000","requested_amount":"90000","interest_rate":"10.5",
                  "tenure_years":6,"type_of_emi":"FIXED","interest_type":"FIXED",
                  "repayment_frequency":"BULLET","category":"SECURED",
                  "disbursement_type":"SINGLE","purpose":"BUSINESS","loan_subcategory":"BALANCE_TRANSFER"}}'
Stage BANK
curl -s -X POST "http://91.203.132.113/api/v2/onboarding/applications/${APP_ID}/stage/" \
  -H "Authorization: Bearer 24rbKCauxv3WVHsqj2O7z0v67tGCHT" -H "Content-Type: application/json" \
  -d '{"stage":"BANK","is_complete":true,
       "payload":{"bank_name":"Axis Bank","account_number":"1234567890",
                  "customer_name_as_per_bank":"TEST USER","ifsc_code":"UTIB0000123","branch_name":"Main"}}'
Stage ADDITIONAL
curl -s -X POST "http://localhost:8001/api/v2/onboarding/applications/${APP_ID}/stage/" \
  -H "Authorization: Bearer 24rbKCauxv3WVHsqj2O7z0v67tGCHT" -H "Content-Type: application/json" \
  -d '{"stage":"ADDITIONAL","is_complete":true,
       "payload":{"is_employee":false,"nominee_relation":"SPOUSE",
                  "nominee_full_name":"Spouse Name","nominee_contact_number":"9000000001"}}'
Submit (queues SAAS pre-screen + bureau)
curl -s -X POST "http://91.203.132.113/api/v2/onboarding/applications/${APP_ID}/submit/" \
  -H "Authorization: Bearer 24rbKCauxv3WVHsqj2O7z0v67tGCHT"
SAAS webhook to us (for reference)
# SAAS posts to:
# http://91.203.132.113/api/v2/onboarding/webhooks/saastech/pre-screen/
# Header: X-Saas-Token: <webhook_token>
# Body example:
# {
#   "application_id": "<APP_ID>",
#   "status": "eligible",
#   "request_id": "SAAST-REQ-001",
#   "remarks": "Eligible",
#   "meta": {"source": "saas_tech", "timestamp": "2025-01-01T12:00:00Z"}
# }
Notes:

AgreementId is forced to 2605 when posting to SAAS.
Document→SAAS mapping is automatic; missing docs are omitted.
Use a new phone number for each lead to avoid uniqueness errors.
Keep consentIpAddress a non-null string and phoneNumber numeric for bureau payload.
If token requests still fail, ensure the OAuth Application’s client_secret is a simple plaintext value (“password”) and the user exists/active.
