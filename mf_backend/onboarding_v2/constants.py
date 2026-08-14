from django.db import models


class ProductCategory(models.TextChoices):
    LOAN = "LOAN", "Loan"
    INSURANCE = "INSURANCE", "Insurance"


class ProductSubCategory(models.TextChoices):
    GOLD_LOAN = "GOLD_LOAN", "Gold Loan"
    HOME_LOAN = "HOME_LOAN", "Home Loan"
    PERSONAL_LOAN = "PERSONAL_LOAN", "Personal Loan"
    BUSINESS_LOAN = "BUSINESS_LOAN", "Business Loan"
    LOAN_AGAINST_PROPERTY = "LOAN_AGAINST_PROPERTY", "Loan Against Property"
    MOTOR_LOAN = "MOTOR_LOAN", "Motor Loan"
    WORKING_CAPITAL = "WORKING_CAPITAL", "Working Capital"
    OVERDRAFT_DOD = "OVERDRAFT_DOD", "Overdraft(DOD)"
    HEALTH_INSURANCE = "HEALTH_INSURANCE", "Health Insurance"
    MOTOR_INSURANCE = "MOTOR_INSURANCE", "Motor Insurance"
    CREDIT_CARDS = "CREDIT_CARDS", "Credit Cards"


class LoanSubCategory(models.TextChoices):
    FRESH = "FRESH", "Fresh"


class LeadSource(models.TextChoices):
    SELF = "SELF", "Self"
    BANK_REFERRED = "BANK_REFERRED", "Bank Reffered"
    CENTRAL = "CENTRAL", "Central"
    TELE = "TELE", "Tele"
    AGENT = "AGENT", "Agent"
    WEBSITE = "WEBSITE", "Website"
    DIGITAL_MARKETING = "DIGITAL_MARKETING", "Digital Marketing"
    BTL = "BTL", "BTL"
    CSR = "CSR", "CSR"
    WALK_IN = "WALK_IN", "Walk-in"
    REPEAT = "REPEAT", "Repeat"
    DATABASE = "DATABASE", "Database"


class LeadType(models.TextChoices):
    FRESH = "FRESH", "Fresh"
    BALANCE_TRANSFER = "BALANCE_TRANSFER", "Balance Transfer"
    CO_LENDING = "CO_LENDING", "Co-Lending"
    SELF_LENDING = "SELF_LENDING", "Self Lending"
    BANK_LEAD = "BANK_LEAD", "Bank Lead"


class LeadStatus(models.TextChoices):
    UNVERIFIED = "UNVERIFIED", "Unverified"
    ACTIVE = "ACTIVE", "Active"
    AUTO_CLOSED = "AUTO_CLOSED", "Auto-closed"
    APPLICATION_CREATED = "APPLICATION_CREATED", "Application created"
    NOT_ELIGIBLE = "NOT_ELIGIBLE", "Not eligible"


class ApplicationStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    SENT_FOR_PRE_SCREENING = "SENT_FOR_PRE_SCREENING", "SentForPreScreening"
    IN_PROGRESS = "IN_PROGRESS", "InProgress"
    READY_FOR_LOAN = "READY_FOR_LOAN", "ReadyForLoan"
    APPROVED = "APPROVED", "Approved"
    AGREEMENT_SIGNED = "AGREEMENT_SIGNED", "AgreementSigned"
    DISBURSEMENT_READY = "DISBURSEMENT_READY", "DisbursementReady"
    DISBURSED = "DISBURSED", "Disbursed"
    MATURED = "MATURED", "Matured"
    DROPPED = "DROPPED", "Dropped"
    DISBURSEMENT_CANCELLED = "DISBURSEMENT_CANCELLED", "DisbursementCancelled"
    DROP_REQUESTED = "DROP_REQUESTED", "DropRequested"
    ALLOCATION_PENDING = "ALLOCATION_PENDING", "AllocationPending"
    COMMERCIAL_PROCESSING = "COMMERCIAL_PROCESSING", "CommercialProcessing"
    DEVIATION_REQUESTED = "DEVIATION_REQUESTED", "DeviationRequested"
    CORRECTION = "CORRECTION", "Correction"
    CORRECTION_RAISED_BY_UNDERWRITING = "CORRECTION_RAISED_BY_UNDERWRITING", "Correction raised by underwriting"
    REJECTED = "REJECTED", "Rejected"
    ELIGIBLE = "ELIGIBLE", "Eligible"
    NOT_ELIGIBLE = "NOT_ELIGIBLE", "NotEligible"
    PASSED = "PASSED", "Passed"
    SUBMITTED = "SUBMITTED", "Submitted"
    FAILED_TO_SUBMIT = "FAILED_TO_SUBMIT", "FailedToSubmit"
    FAILED_TO_SUBMIT_PRESCREEN = "FAILED_TO_SUBMIT_PRESCREEN", "FailedToSubmitPrescreen"
    FAILED_TO_SUBMIT_CREATE_LOAN = "FAILED_TO_SUBMIT_CREATE_LOAN", "FailedToSubmitCreateLoan"
    NEW_LEAD = "NEW_LEAD", "NewLead"
    UNVERIFIED = "UNVERIFIED", "Unverified"
    PUNCHING_PENDING = "PUNCHING_PENDING", "Punching Pending"
    LOAN_STATUS_UPDATED = "LOAN_STATUS_UPDATED", "Loan Status Updated"
    SUBMITTED_TO_UNDERWRITING = "SUBMITTED_TO_UNDERWRITING", "Application Submitted to Underwriting"
    FAILED_TO_SUBMIT_TO_UNDERWRITING = "FAILED_TO_SUBMIT_TO_UNDERWRITING", "Failed to submit to underwriting"
    REJECTED_BY_UNDERWRITING = "REJECTED_BY_UNDERWRITING", "Rejected by Underwriting"
    APPROVED_BY_ACCOUNTS = "APPROVED_BY_ACCOUNTS", "Approved by Accounts"
    REJECTED_BY_ACCOUNTS = "REJECTED_BY_ACCOUNTS", "Rejected by accounts"
    BT_FUND_DISBURSED = "BT_FUND_DISBURSED", "BT Fund Disbursed"
    ESIGN_INITIATED = "ESIGN_INITIATED", "E-sign Initiated"
    ESIGN_COMPLETED = "ESIGN_COMPLETED", "E-sign Completed"
    RH_APPROVAL_PENDING = "RH_APPROVAL_PENDING", "RH Approval Pending"
    APPROVED_BY_RH = "APPROVED_BY_RH", "Approved by RH"
    REJECTED_BY_RH = "REJECTED_BY_RH", "Rejected by RH"
    CORRECTION_RAISED_BY_RH = "CORRECTION_RAISED_BY_RH", "Correction raised by RH"
    AMOUNT_PAID_TO_EXISTING_LENDER = "AMOUNT_PAID_TO_EXISTING_LENDER", "Amount paid to Existing Lender"
    AMOUNT_NOT_PAID_TO_EXISTING_LENDER = "AMOUNT_NOT_PAID_TO_EXISTING_LENDER", "Amount not paid to Existing Lender"
    AMOUNT_PAID_TO_EXISTING_LENDER_ON_HOLD = "AMOUNT_PAID_TO_EXISTING_LENDER_ON_HOLD", "Amount paid to Existing Lender-On Hold"
    GOLD_RECEIVED_FROM_EXISTING_LENDER = "GOLD_RECEIVED_FROM_EXISTING_LENDER", "Gold received from Existing lender"
    GOLD_NOT_RECEIVED_FROM_EXISTING_LENDER = "GOLD_NOT_RECEIVED_FROM_EXISTING_LENDER", "Gold not received from Existing lender"
    GOLD_RECEIVED_FROM_EXISTING_LENDER_ON_HOLD = "GOLD_RECEIVED_FROM_EXISTING_LENDER_ON_HOLD", "Gold received from Existing lender - On Hold"
    GOLD_SUBMITTED_TO_PARTNER_BANK = "GOLD_SUBMITTED_TO_PARTNER_BANK", "Gold Submitted to Partner Bank"
    GOLD_NOT_SUBMITTED_TO_PARTNER_BANK = "GOLD_NOT_SUBMITTED_TO_PARTNER_BANK", "Gold not Submitted to Partner bank"
    GOLD_SUBMITTED_TO_PARTNER_BANK_ON_HOLD = "GOLD_SUBMITTED_TO_PARTNER_BANK_ON_HOLD", "Gold Submitted to Partner bank - On Hold"
    NEW_LOAN_TAKEN_BY_SELF = "NEW_LOAN_TAKEN_BY_SELF", "New loan taken by Self"
    LOAN_TRANSFERRED = "LOAN_TRANSFERRED", "Loan Transferred"
    AMOUNT_NOT_PAID_TO_EXISTING_LENDER_BT_RETURN_COMPLETED = "AMOUNT_NOT_PAID_TO_EXISTING_LENDER_BT_RETURN_COMPLETED", "Amount Not Paid to Existing Lender and BT Return Completed"
    GOLD_NOT_RECEIVED_FROM_EXISTING_LENDER_BT_RETURN_COMPLETED = "GOLD_NOT_RECEIVED_FROM_EXISTING_LENDER_BT_RETURN_COMPLETED", "Gold Not Received From Existing Lender and BT Return Completed"
    GOLD_NOT_SUBMITTED_TO_PARTNER_BANK_BT_RETURN_COMPLETED = "GOLD_NOT_SUBMITTED_TO_PARTNER_BANK_BT_RETURN_COMPLETED", "Gold Not Submitted to Partner Bank and BT Return Completed"
    LOAN_TRANSFERRED_BT_RETURN_COMPLETED = "LOAN_TRANSFERRED_BT_RETURN_COMPLETED", "Loan Transferred and BT Return Completed"
    LOAN_STATUS_UPDATED_BT_RETURN_COMPLETED = "LOAN_STATUS_UPDATED_BT_RETURN_COMPLETED", "Loan status updated and BT Return Completed"


class ApplicationStage(models.TextChoices):
    SELF_DECLARATION = "SELF_DECLARATION", "Self Declaration"
    PAN = "PAN", "Pan"
    BASIC = "BASIC", "Basic"
    ADDRESS = "ADDRESS", "Address"
    DOCUMENTS = "DOCUMENTS", "Documents"
    PERSONAL = "PERSONAL", "Personal"
    ADDRESS_SECONDARY = "ADDRESS_SECONDARY", "AddressSecondary"
    GOLD = "GOLD", "Gold"
    PLEDGE_CARD = "PLEDGE_CARD", "Pledge Card"
    LOAN = "LOAN", "Loan"
    BANK = "BANK", "Bank"
    ADDITIONAL = "ADDITIONAL", "Additional"
    CHARGES = "CHARGES", "Charges and Details"
    CUSTOMER_VISIT = "CUSTOMER_VISIT", "Customer Visit"
    SELFIE = "SELFIE", "Selfie"
    WAIVER = "WAIVER", "Waiver"
    ELIGIBILITY = "ELIGIBILITY", "Eligibility"
    AMOUNT_TRANSFERRED = "AMOUNT_TRANSFERRED", "Amount Transferred"
    GOLD_RECEIVED = "GOLD_RECEIVED", "Gold Received"
    GOLD_SUBMITTED = "GOLD_SUBMITTED", "Gold Submitted"
    CHOOSE_CUSTOMER = "CHOOSE_CUSTOMER", "Choose Customer"
    FUND_REFUND = "FUND_REFUND", "Fund Refund"
    SUBMITTED = "SUBMITTED", "Submitted"
    COMPLETE = "COMPLETE", "Complete"
    LOAN_RANGE_SELECTION = "LOAN_RANGE_SELECTION", "Loan Range Selection"
    PRODUCT_SELECTION = "PRODUCT_SELECTION", "Product Selection"
    LENDING_PARTNER_BANK = "LENDING_PARTNER_BANK", "Lending Partner Bank"


SELF_LENDING_STAGES = [
    (ApplicationStage.LENDING_PARTNER_BANK, 5),
    (ApplicationStage.PAN, 10),
    (ApplicationStage.ELIGIBILITY, 15),
    (ApplicationStage.PRODUCT_SELECTION, 20),
    (ApplicationStage.SELF_DECLARATION, 25),
    (ApplicationStage.DOCUMENTS, 35),
    (ApplicationStage.PERSONAL, 45),
    (ApplicationStage.ADDRESS, 55),
    (ApplicationStage.GOLD, 70),
    (ApplicationStage.LOAN, 80),
    (ApplicationStage.ADDITIONAL, 90),
    (ApplicationStage.CHARGES, 100),
]


FRESH_LOAN_STAGES = [
    (ApplicationStage.BASIC, 0),
    (ApplicationStage.ADDRESS, 50),
]

FRESH_GOLD_LOAN_STAGES = [
    (ApplicationStage.BASIC, 0),
    (ApplicationStage.ADDRESS, 50),
    (ApplicationStage.LOAN, 50),
]

CO_LENDING_STAGES = [
    (ApplicationStage.LENDING_PARTNER_BANK, 0),
    (ApplicationStage.LOAN_RANGE_SELECTION, 25),
    (ApplicationStage.PRODUCT_SELECTION, 50),
    (ApplicationStage.BASIC, 75),
    (ApplicationStage.ADDRESS, 100),
]

BT_LOAN_STAGES = [
    (ApplicationStage.DOCUMENTS, 0),
    (ApplicationStage.BASIC, 10),
    (ApplicationStage.ADDRESS, 20),
    (ApplicationStage.PLEDGE_CARD, 30),
    (ApplicationStage.LOAN, 40),
    (ApplicationStage.BANK, 50),
    (ApplicationStage.CUSTOMER_VISIT, 60),
    (ApplicationStage.ADDITIONAL, 70),
    (ApplicationStage.WAIVER, 80),
    (ApplicationStage.AMOUNT_TRANSFERRED, 90),
    (ApplicationStage.GOLD_RECEIVED, 95),
    (ApplicationStage.GOLD_SUBMITTED, 98),
    (ApplicationStage.CHOOSE_CUSTOMER, 99),
]


class DocumentType(models.TextChoices):
    PAN = "PAN", "PAN"
    AADHAAR = "AADHAAR", "Aadhaar"
    LIVE_PHOTO = "LIVE_PHOTO", "Live Photo"
    VOTER_ID = "VOTER_ID", "Voter ID"
    DRIVING_LICENSE = "DRIVING_LICENSE", "Driving License"
    PASSPORT = "PASSPORT", "Passport"
    MANREGA_CARD = "MANREGA_CARD", "Manrega Card"
    OTHER = "OTHER", "Other"
    CATTLE = "CATTLE", "Cattle"
    FRESH_LOAN = "FRESH_LOAN", "Fresh Loan"
    PLEDGE_CARD = "PLEDGE_CARD", "Pledge Card"
    CUSTOMER_VISIT = "CUSTOMER_VISIT", "Customer Visit"
    SELFIE = "SELFIE", "Selfie"


class DocumentStatus(models.TextChoices):
    VERIFIED = "VERIFIED", "Verified"
    PENDING_UPLOAD = "PENDING_UPLOAD", "PendingUpload"
    UPLOADED = "UPLOADED", "Uploaded"


class AddressType(models.TextChoices):
    PERMANENT = "PERMANENT", "Permanent"
    CURRENT = "CURRENT", "Current"
    MAILING = "MAILING", "Mailing"


class PrimaryBorrowerType(models.TextChoices):
    INDIVIDUAL = "INDIVIDUAL", "Individual"
    CORPORATE = "CORPORATE", "Corporate"


class NriStatus(models.TextChoices):
    YES = "Y", "Yes"
    NO = "N", "No"


class BureauDecision(models.TextChoices):
    APPROVED = "APPROVED", "Approved"
    DECLINED = "DECLINED", "Declined"
    PENDING = "PENDING", "Pending"


class Profession(models.TextChoices):
    AGRICULTURE = "AGRICULTURE", "Agriculture"
    ANCILLARY_SERVICES = "ANCILLARY_SERVICES", "Ancillary Services"
    ANIMAL_HUSBANDRY = "ANIMAL_HUSBANDRY", "Animal Husbandry"
    BUSINESS = "BUSINESS", "Business"
    BUISNESS = "BUISNESS", "Buisness"
    FIN_INSTN_INTERMEDIARY = "FIN_INSTN_INTERMEDIARY", "Fin Instn/Intermediary"
    HANDICRAFT = "HANDICRAFT", "Handicraft"
    HOME_MAKER = "HOME_MAKER", "Home Maker"
    HOUSEWIFE = "HOUSEWIFE", "Housewife"
    INDIVIDUALS = "INDIVIDUALS", "Individuals"
    LABOUR = "LABOUR", "Labour"
    MFG = "MFG", "Mfg"
    MANUFACTURING = "MANUFACTURING", "Manufacturing"
    NPO = "NPO", "NPO"
    OTHERS = "OTHERS", "Others"
    OTHER = "OTHER", "Other"
    POLITICIAN = "POLITICIAN", "Politician"
    PROF = "PROF", "Prof"
    PROFESSIONAL = "PROFESSIONAL", "Professional"
    REAL_ESTATE = "REAL_ESTATE", "Real estate"
    RURAL_ARTISANS = "RURAL_ARTISANS", "Rural Artisans"
    RETIRED = "RETIRED", "Retired"
    SALARIED = "SALARIED", "Salaried"
    SELF_EMPLOYED = "SELF_EMPLOYED", "Self Employed"
    SERVICES = "SERVICES", "Services"
    STUDENT = "STUDENT", "Student"
    SERVICE = "SERVICE", "Service"
    TRADE = "TRADE", "Trade"
    TRADING = "TRADING", "Trading"
    UNEMPLOYED = "UNEMPLOYED", "Unemployed"


class Occupation(models.TextChoices):
    ACTIVITIES_ALLIED_TO_AGRICULTURE = "ACTIVITIES_ALLIED_TO_AGRICULTURE", "Activities Allied To Agriculture"
    AGRI_CROPS_FRUITS_VEGETABLES = "AGRI_CROPS_FRUITS_VEGETABLES", "Agri Crops/Fruits/Vegetables"
    POULTRY_FISHERIES_LIVESTOCK = "POULTRY_FISHERIES_LIVESTOCK", "Poultry / Fisheries / Livestock"
    ATTENDANT = "ATTENDANT", "Attendant"
    CARETAKER = "CARETAKER", "Caretaker"
    CARPENTER_PLUMBER_ELECTRICIAN = "CARPENTER_PLUMBER_ELECTRICIAN", "Carpenter/Plumber/Electrician"
    CLERK = "CLERK", "Clerk"
    COOK = "COOK", "Cook"
    DRIVER = "DRIVER", "Driver"
    MAID = "MAID", "Maid"
    MASON = "MASON", "Mason"
    TAILOR = "TAILOR", "Tailor"
    WAITER = "WAITER", "Waiter"
    WATCHMAN = "WATCHMAN", "Watchman"
    WORKER_LABOUR_OPERATOR = "WORKER_LABOUR_OPERATOR", "Worker/Labour/Operator"
    COMMISSIONAGENT_ARTHIY = "COMMISSIONAGENT_ARTHIY", "CommissionAgent/Arthiy"
    COMMODITY_BROKER = "COMMODITY_BROKER", "Commodity Broker"
    FINTECH_STARTUPS = "FINTECH_STARTUPS", "Fintech Startups"
    INSURANCE = "INSURANCE", "Insurance"
    MONEYCHANGER_FFMC = "MONEYCHANGER_FFMC", "MoneyChanger/FFMC"
    STOCK_BROKERS = "STOCK_BROKERS", "Stock Brokers"
    HOUSEWIFE = "HOUSEWIFE", "Housewife"
    MINOR = "MINOR", "Minor"
    RETIRED = "RETIRED", "Retired"
    STUDENT = "STUDENT", "Student"
    UNEMPLOYED = "UNEMPLOYED", "Unemployed"
    AIRLINES_INDUSTRY_ALLIED_ACTIVITIES = "AIRLINES_INDUSTRY_ALLIED_ACTIVITIES", "Airlines Industry/Allied activities"
    ALCOHOL_BEVRG = "ALCOHOL_BEVRG", "Alcohol Bevrg."
    ARMS_AND_AMMUNITION_EXPLOSIVES = "ARMS_AND_AMMUNITION_EXPLOSIVES", "Arms & Ammunition/ Explosives"
    VEHICLE_VEHICLE_SERVICING_ETC = "VEHICLE_VEHICLE_SERVICING_ETC", "Vehicle/Vehicle Servicing etc."
    CEMENT_AND_CEMENT_PRODUCTS = "CEMENT_AND_CEMENT_PRODUCTS", "Cement & Cement Products"
    CHEMICALS_AND_CHEMICAL_PRODUCTS = "CHEMICALS_AND_CHEMICAL_PRODUCTS", "Chemicals & Chemical Products"
    COSMETIC_OTH_BEAUTY_PRODUCT_ART_JEWELLERY = "COSMETIC_OTH_BEAUTY_PRODUCT_ART_JEWELLERY", "Cosmetic/Oth Beauty Product/Art jewellery"
    DAIRYING_AND_MILK_TRADING = "DAIRYING_AND_MILK_TRADING", "Dairying & Milk Trading"
    DRUGS_PHARMACEUTICALS_BIOTECHNOLOGY = "DRUGS_PHARMACEUTICALS_BIOTECHNOLOGY", "Drugs/Pharmaceuticals/Biotechnology"
    ELECTRIC_ELECTRONIC_MACHINERY_GOODS = "ELECTRIC_ELECTRONIC_MACHINERY_GOODS", "Electric/Electronic Machinery/Goods"
    ENERGY_GENERATION_AND_DISTRIBUTION = "ENERGY_GENERATION_AND_DISTRIBUTION", "Energy Generation & Distribution"
    FERTILIZERS_PESTICIDES = "FERTILIZERS_PESTICIDES", "Fertilizers/Pesticides"
    FIREWORKS_FIRECRACKERS = "FIREWORKS_FIRECRACKERS", "Fireworks / Firecrackers"
    FOOD_MANUFACTURING_PROCESSING = "FOOD_MANUFACTURING_PROCESSING", "Food Manufacturing/Processing"
    FURNITURE_HOME_DECOR = "FURNITURE_HOME_DECOR", "Furniture/Home Decor"
    GEMS_AND_JEWELLERY_BULLION = "GEMS_AND_JEWELLERY_BULLION", "Gems & Jewellery/Bullion"
    GENERAL_UTILITY_PRODUCTS = "GENERAL_UTILITY_PRODUCTS", "General Utility Products"
    GLASS_AND_GLASS_WARE = "GLASS_AND_GLASS_WARE", "Glass & Glass Ware"
    HANDLOOM_TEXTILE_AND_KHADI = "HANDLOOM_TEXTILE_AND_KHADI", "Handloom Textile and Khadi"
    HARDWARE_FITTINGS_PAINTS = "HARDWARE_FITTINGS_PAINTS", "Hardware/Fittings / Paints"
    HEAVY_MACHINERY_GENERAL_ENGG_GOODS = "HEAVY_MACHINERY_GENERAL_ENGG_GOODS", "Heavy Machinery/General Engg. Goods"
    LEATHER_AND_LEATHER_PRODUCTS = "LEATHER_AND_LEATHER_PRODUCTS", "Leather & Leather Products"
    MARBLE_GRANITE_ETC = "MARBLE_GRANITE_ETC", "Marble / Granite etc"
    MEAT_PRODUCTS_AND_MEAT_PROCESSORS = "MEAT_PRODUCTS_AND_MEAT_PROCESSORS", "Meat Products & Meat Processors"
    MEDIA_AND_FILM_PRODUCTION_HOUSES = "MEDIA_AND_FILM_PRODUCTION_HOUSES", "Media and Film Production Houses"
    MEDICAL_EQUIPMENTS_ALLIED_PRODUCTS = "MEDICAL_EQUIPMENTS_ALLIED_PRODUCTS", "Medical Equipments/Allied products"
    METAL_AND_METAL_PRODUCTS = "METAL_AND_METAL_PRODUCTS", "Metal & Metal Products"
    NON_ALCOHOLIC_BEVRG = "NON_ALCOHOLIC_BEVRG", "Non-Alcoholic Bevrg."
    OIL_GAS_NATURAL_ARTIFICIAL_FUELS = "OIL_GAS_NATURAL_ARTIFICIAL_FUELS", "Oil/Gas/Natural/Artificial Fuels"
    PAPER_AND_PAPER_PRODUCTS = "PAPER_AND_PAPER_PRODUCTS", "Paper And Paper Products"
    PRECIOUS_METAL_STONE_ALLIED_PRODUCT = "PRECIOUS_METAL_STONE_ALLIED_PRODUCT", "Precious Metal/Stone/Allied Product"
    PRINTING_PUBLISHING_STATIONARY = "PRINTING_PUBLISHING_STATIONARY", "Printing/Publishing/ Stationary"
    RUBBER_PLASTIC_AND_THEIR_PRODUCTS = "RUBBER_PLASTIC_AND_THEIR_PRODUCTS", "Rubber,Plastic & Their Products"
    SHIPPING_MARITIME_ALLIED_GOODS = "SHIPPING_MARITIME_ALLIED_GOODS", "Shipping/Maritime/Allied Goods"
    SPORTS_GOODS_GAMES_TOYS = "SPORTS_GOODS_GAMES_TOYS", "Sports Goods / Games / Toys"
    TEA_COFFEE = "TEA_COFFEE", "Tea/Coffee"
    TELECOM_AND_TELECOMMUNICATION = "TELECOM_AND_TELECOMMUNICATION", "Telecom and Telecommunication"
    TEXTILES_CLOTHING_FIBRES_FOOTWEAR = "TEXTILES_CLOTHING_FIBRES_FOOTWEAR", "Textiles/Clothing/Fibres/Footwear"
    TIMBER_AND_ALLIED_ACTIVITIES = "TIMBER_AND_ALLIED_ACTIVITIES", "Timber & allied activities"
    TOBACCO_ALLIED_PRODUCTS = "TOBACCO_ALLIED_PRODUCTS", "Tobacco/Allied Products"
    TRANSPORT_EQUIPMENTS_AND_SPARE_PARTS = "TRANSPORT_EQUIPMENTS_AND_SPARE_PARTS", "Transport Equipments and Spare Parts"
    ASSOCIATIONS_APMC_MANDI_KHADI_HANDLOOM = "ASSOCIATIONS_APMC_MANDI_KHADI_HANDLOOM", "Associations(APMC/Mandi/Khadi/Handloom)"
    PUBLIC_REPRESENTATIVE_MP_MLA = "PUBLIC_REPRESENTATIVE_MP_MLA", "Public Representative/MP/MLA"
    ACTOR_MUSICIAN_DANCERS_AUTHOR_ARTIST = "ACTOR_MUSICIAN_DANCERS_AUTHOR_ARTIST", "Actor/Musician/Dancers/Author/Artist"
    ADVOCATES_NOTARYATTORNEY_JUDGE = "ADVOCATES_NOTARYATTORNEY_JUDGE", "Advocates/NotaryAttorney/Judge"
    ARCHITECTS_INTERIOR_DESIGNER = "ARCHITECTS_INTERIOR_DESIGNER", "Architects/ Interior Designer"
    CHARTERED_ACCOUNTANTS = "CHARTERED_ACCOUNTANTS", "Chartered Accountants"
    DOCTORS_MEDICAL_PROFESSIONALS = "DOCTORS_MEDICAL_PROFESSIONALS", "Doctors / Medical Professionals"
    ENGINEERS = "ENGINEERS", "Engineers"
    MEDIA_PERSON = "MEDIA_PERSON", "Media Person"
    NURSES = "NURSES", "Nurses"
    PHARMACIST = "PHARMACIST", "Pharmacist"
    PHOTOGRAPHER = "PHOTOGRAPHER", "Photographer"
    PROFESSORS_LECTURER = "PROFESSORS_LECTURER", "Professors / Lecturer"
    SPORTS_PERSON = "SPORTS_PERSON", "Sports person"
    ACTIVITIES_ALLIED_TO_REAL_ESTATE = "ACTIVITIES_ALLIED_TO_REAL_ESTATE", "Activities Allied To Real Estate"
    REAL_ESTATE_BROKER_AGENT = "REAL_ESTATE_BROKER_AGENT", "Real Estate Broker/Agent"
    CONSTRUCTION_DEVELOPMENT = "CONSTRUCTION_DEVELOPMENT", "Construction/Development"
    DEFENCE_ALLIED_SERVICES = "DEFENCE_ALLIED_SERVICES", "Defence/Allied Services"
    DIPLOMAT = "DIPLOMAT", "Diplomat"
    EMPLOYEES_OF_EMBASSY_CONSULATE = "EMPLOYEES_OF_EMBASSY_CONSULATE", "Employees of Embassy/Consulate"
    SALARIED_EMPLOYEE_PRIVATE_SECTOR = "SALARIED_EMPLOYEE_PRIVATE_SECTOR", "Salaried employee - Private sector"
    PSU_EMPLOYEE = "PSU_EMPLOYEE", "PSU Employee"
    SALARIED_EMPLOYEE_GOVERNMENT_SECTOR = "SALARIED_EMPLOYEE_GOVERNMENT_SECTOR", "Salaried employee- Government sector"
    AIRLINESINDUSTRY_AND_ALLIEDACTIVITIES = "AIRLINESINDUSTRY_AND_ALLIEDACTIVITIES", "AirlinesIndustry&alliedactivities"
    AUCTION_HOUSE = "AUCTION_HOUSE", "Auction House"
    COACHING_CLASSES = "COACHING_CLASSES", "Coaching Classes"
    CONSULTANTS = "CONSULTANTS", "Consultants"
    CONTRACTOR_CONSTRUCTION = "CONTRACTOR_CONSTRUCTION", "Contractor_Construction"
    COSMETIC_BEAUTY_SERV_ARTIFICIALJEWEL = "COSMETIC_BEAUTY_SERV_ARTIFICIALJEWEL", "Cosmetic/beauty_serv/ArtificialJewel"
    CREDIT_BUREAU_RATING_AGENCIES = "CREDIT_BUREAU_RATING_AGENCIES", "Credit Bureau / Rating Agencies"
    CYBER_CAFES_VIDEO_GAME_PARLOURS = "CYBER_CAFES_VIDEO_GAME_PARLOURS", "Cyber Cafes /Video Game Parlours"
    DIAGNOSTIC_CENTERS_PATHOLOGY_LABS = "DIAGNOSTIC_CENTERS_PATHOLOGY_LABS", "Diagnostic Centers/Pathology Labs"
    EDUCATIONAL_INSTITUTIONS = "EDUCATIONAL_INSTITUTIONS", "Educational Institutions"
    ENGINEERING_FIRMS_AND_CONCERNS = "ENGINEERING_FIRMS_AND_CONCERNS", "Engineering Firms & Concerns"
    EVENT_MGMT_PLANNER_ORGANISER = "EVENT_MGMT_PLANNER_ORGANISER", "Event Mgmt/Planner/Organiser"
    FASHION_DESIGNER = "FASHION_DESIGNER", "Fashion designer"
    GAMBLING_CASINO_BETTINGACTIVITIES = "GAMBLING_CASINO_BETTINGACTIVITIES", "Gambling/Casino/Bettingactivities"
    HOSPITALS_NURSING_HOMES = "HOSPITALS_NURSING_HOMES", "Hospitals/Nursing Homes"
    HOTELS_BARS_EATERIES_LODGE_ETC = "HOTELS_BARS_EATERIES_LODGE_ETC", "Hotels/Bars/Eateries/Lodge etc."
    IT_ITES_BPO_KPO_BACK_OFFICE_OPS = "IT_ITES_BPO_KPO_BACK_OFFICE_OPS", "IT/ITES/BPO/KPO/Back Office Ops"
    LAW_FIRMS = "LAW_FIRMS", "Law Firms"
    LEASING_RENTAL_SERVICES = "LEASING_RENTAL_SERVICES", "Leasing (Rental) Services"
    LEISURE_PLACES_THEATRE_MUSEUM = "LEISURE_PLACES_THEATRE_MUSEUM", "Leisure Places/Theatre/Museum"
    LOGISTICS_TRANSPORT_AND_SUPPORT = "LOGISTICS_TRANSPORT_AND_SUPPORT", "Logistics/Transport & Support"
    MKTG_ADVERTISING_MEDIA_CONSULTANT = "MKTG_ADVERTISING_MEDIA_CONSULTANT", "Mktg./Advertising/Media Consultant"
    MINING_QUARRYING_EXTRACTION = "MINING_QUARRYING_EXTRACTION", "Mining / Quarrying / Extraction"
    MONEY_LENDER_CHIT_FUNDS = "MONEY_LENDER_CHIT_FUNDS", "Money Lender / Chit funds"
    MUNICIPALCORPORATIONS_LOCALBODIES = "MUNICIPALCORPORATIONS_LOCALBODIES", "Municipalcorporations/LocalBodies"
    PHOTOSTUDIO_PHOTOGRAPHICACTIVITIES = "PHOTOSTUDIO_PHOTOGRAPHICACTIVITIES", "PhotoStudio/Photographicactivities"
    PRINTING_PUBLISHING_STATIONERY = "PRINTING_PUBLISHING_STATIONERY", "Printing/Publishing/ Stationery"
    PRODUCT_PACKAGING_ACTIVITY_BOTTLING = "PRODUCT_PACKAGING_ACTIVITY_BOTTLING", "Product Packaging Activity/Bottling"
    RECRUITMENTAGENCY_HOUSEKEEPING = "RECRUITMENTAGENCY_HOUSEKEEPING", "RecruitmentAgency/Housekeeping"
    REPAIRS_AND_MAINTENANCE_SERVICE = "REPAIRS_AND_MAINTENANCE_SERVICE", "Repairs & Maintenance Service"
    SHIPPING_MARITIME_AND_ALLIED_ACTIVITIES = "SHIPPING_MARITIME_AND_ALLIED_ACTIVITIES", "Shipping/Maritime &Allied activities"
    SOCIETIES_HOUSING_SOCIETY = "SOCIETIES_HOUSING_SOCIETY", "Societies - Housing society"
    STOCK_COMMODITYEXCH_FIN_INTERMEDIARY = "STOCK_COMMODITYEXCH_FIN_INTERMEDIARY", "Stock/CommodityExch/Fin Intermediary"
    TOURISM_TOURS_AND_TRAVELS = "TOURISM_TOURS_AND_TRAVELS", "Tourism / Tours and Travels"
    WAREHOUSING_STORAGE = "WAREHOUSING_STORAGE", "Warehousing / Storage"
    ART_AND_ANTIQUE_DEALERS = "ART_AND_ANTIQUE_DEALERS", "Art And Antique Dealers"
    COSMETIC_BEAUTY_PROD_ARTIFICIALJEWEL = "COSMETIC_BEAUTY_PROD_ARTIFICIALJEWEL", "Cosmetic/Beauty Prod/ArtificialJewel"
    DRUGS_PHARMA_GOODS_BIOTECHNOLOGY = "DRUGS_PHARMA_GOODS_BIOTECHNOLOGY", "Drugs/Pharma Goods/Biotechnology"
    ELECTRICAL_ELECTRONICMACHINERY_AND_GOODS = "ELECTRICAL_ELECTRONICMACHINERY_AND_GOODS", "Electrical/ElectronicMachinery&Goods"
    FISH_AND_AQUA_TRADERS_AND_PROCESSORS = "FISH_AND_AQUA_TRADERS_AND_PROCESSORS", "Fish & Aqua Traders And Processors"
    FOOD_GRAINS_AND_GROCERIES = "FOOD_GRAINS_AND_GROCERIES", "Food Grains & Groceries"
    FOOD_MFG_AND_PROCESSING = "FOOD_MFG_AND_PROCESSING", "Food Mfg And Processing"
    HEAVY_MACHINERY_ENGG_GOODS = "HEAVY_MACHINERY_ENGG_GOODS", "Heavy Machinery/Engg. Goods"
    MEDICAL_EQUIPMENT_ALLIED_PRODUCT = "MEDICAL_EQUIPMENT_ALLIED_PRODUCT", "Medical Equipment/Allied Product"
    PETROL_PUMP = "PETROL_PUMP", "Petrol Pump"
    PRECIOUS_METAL_STONE_ETC = "PRECIOUS_METAL_STONE_ETC", "Precious Metal, Stone, etc."
    SCRAP_DEALER = "SCRAP_DEALER", "Scrap Dealer"
    TEXTILES_AND_CLOTHING_FIBRES_AND_FOOTWEAR = "TEXTILES_AND_CLOTHING_FIBRES_AND_FOOTWEAR", "Textiles&Clothing,Fibres&Footwear"
    VIRTUAL_CURRENCY_CRYPTO_CURRENCY = "VIRTUAL_CURRENCY_CRYPTO_CURRENCY", "Virtual Currency / Crypto Currency"
    WILDLIFE_HUNTING_TRAPPING_GOODS = "WILDLIFE_HUNTING_TRAPPING_GOODS", "Wildlife/Hunting/Trapping Goods"


class IncomeSource(models.TextChoices):
    SALARY = "SALARY", "Salary"
    BUSINESS = "BUSINESS", "Business"
    RETIRED = "RETIRED", "Retired"
    SELF_EMPLOYED = "SELF_EMPLOYED", "Self employed"
    PROFESSIONAL_INCOME = "PROFESSIONAL_INCOME", "Professional Income"


class LoanPurpose(models.TextChoices):
    MEDICAL_TREATMENT = "MEDICAL_TREATMENT", "Medical Treatment"
    AGRICULTURE_NEEDS = "AGRICULTURE_NEEDS", "Agriculture Needs"
    BUSINESS_NEEDS = "BUSINESS_NEEDS", "Business Needs"
    EDUCATION = "EDUCATION", "Education"
    TOUR_TRAVEL = "TOUR_TRAVEL", "Tour &Travel"
    VEHICLE_PURCHASE = "VEHICLE_PURCHASE", "Vehicle Purchase"
    BUYING_OR_RENOVATING_HOME = "BUYING_OR_RENOVATING_HOME", "Buying or Renovating Home"
    BIDDING_TENDERING = "BIDDING_TENDERING", "Bidding/Tendering"
    PERSONAL_NEEDS = "PERSONAL_NEEDS", "Personal Needs"
    OTHER = "OTHER", "Other"


class ProofOfAddress(models.TextChoices):
    AADHAAR = "AADHAAR", "Aadhaar"
    VOTER_ID = "VOTER_ID", "Voter ID"
    DRIVING_LICENSE = "DRIVING_LICENSE", "Driving License"
    NREGA = "NREGA", "NREGA"
    PASSPORT = "PASSPORT", "Passport"


class Gender(models.TextChoices):
    MALE = "MALE", "Male"
    FEMALE = "FEMALE", "Female"
    OTHER = "OTHER", "Other"


class EmiType(models.TextChoices):
    FIXED = "FIXED", "Fixed"


class InterestType(models.TextChoices):
    FIXED = "FIXED", "Fixed"


class RepaymentFrequency(models.TextChoices):
    BULLET = "BULLET", "Bullet"
    QUARTERLY = "QUARTERLY", "Quarterly"
    MONTHLY = "MONTHLY", "Monthly"


class CategoryType(models.TextChoices):
    SECURED = "SECURED", "Secured"


class DisbursementType(models.TextChoices):
    SINGLE = "SINGLE", "Single"


class LendingPartner(models.TextChoices):
    AXIS_BANK = "AXIS_BANK", "Axis Bank"
    CSB_BANK = "CSB_BANK", "CSB Bank"
    DBS = "DBS", "DBS"
    DCB_BANK = "DCB_BANK", "DCB Bank"
    HDFC_BANK = "HDFC_BANK", "HDFC Bank"
    ICICI_BANK = "ICICI_BANK", "ICICI Bank"
    KOTAK_MAHINDRA_BANK = "KOTAK_MAHINDRA_BANK", "Kotak Mahindra Bank"
    RBL_BANK = "RBL_BANK", "RBL Bank"
    BAJAJ_FINSERV = "BAJAJ_FINSERV", "Bajaj Finserv"
    
    # Label-based keys for frontend compatibility
    AXIS_BANK_STR = "Axis Bank", "Axis Bank"
    CSB_BANK_STR = "CSB Bank", "CSB Bank"
    DCB_BANK_STR = "DCB Bank", "DCB Bank"
    HDFC_BANK_STR = "HDFC Bank", "HDFC Bank"
    ICICI_BANK_STR = "ICICI Bank", "ICICI Bank"
    KOTAK_MAHINDRA_BANK_STR = "Kotak Mahindra Bank", "Kotak Mahindra Bank"
    RBL_BANK_STR = "RBL Bank", "RBL Bank"
    BAJAJ_FINSERV_STR = "Bajaj Finserv", "Bajaj Finserv"

    DBS_BANK = "DBS_BANK", "DBS Bank"
    KOTAK_BANK = "KOTAK_BANK", "Kotak Bank"
    KARNATAKA_BANK = "KARNATAKA_BANK", "Karnataka Bank"
    OTHER = "OTHER", "Other"


TENURE_MONTHS = [6, 9, 12]


class Purity(models.TextChoices):
    K22 = "22K", "22K"


class Religion(models.TextChoices):
    BUDDHIST = "BUDDHIST", "Buddhist"
    CHRISTIAN = "CHRISTIAN", "Christian"
    HINDU = "HINDU", "Hindu"
    JAIN = "JAIN", "Jain"
    MUSLIM = "MUSLIM", "Muslim"
    OTHERS = "OTHERS", "Others"
    PARSI = "PARSI", "Parsi"
    ZOROASTRIAN = "ZOROASTRIAN", "Zoroastrian"
    SIKH = "SIKH", "Sikh"


class Category(models.TextChoices):
    GENERAL = "GENERAL", "General"
    OBC = "OBC", "OBC"
    SC = "SC", "Schedule Caste"
    ST = "ST", "Schedule Tribe"
    OTHER = "OTHER", "Other"


class ResidenceType(models.TextChoices):
    PG = "PG", "PG"
    OWNED = "OWNED", "Owned"
    RENTED = "RENTED", "Rented"
    PARENTAL = "PARENTAL", "Parental"
    OTHERS = "OTHERS", "Others"


class Qualification(models.TextChoices):
    METRIC = "METRIC", "Metric"
    MATRIC = "MATRIC", "Matric"
    INTERMEDIATE = "INTERMEDIATE", "Intermediate"
    GRADUATE = "GRADUATE", "Graduate"
    ILLITERATE = "ILLITERATE", "Illiterate"
    PRIMARY = "PRIMARY", "Primary"
    POST_GRADUATE = "POST_GRADUATE", "Post Graduate"


class LivingWith(models.TextChoices):
    FAMILY = "FAMILY", "Family"
    ALONE = "ALONE", "Alone"
    FRIENDS = "FRIENDS", "Friends"
    OTHERS = "OTHERS", "Others"


class MaritalStatus(models.TextChoices):
    MARRIED = "MARRIED", "Married"
    UNMARRIED = "UNMARRIED", "Unmarried"
    WIDOWED = "WIDOWED", "Widowed"
    DIVORCED = "DIVORCED", "Divorced"


class Relation(models.TextChoices):
    SELF = "SELF", "Self"
    FATHER = "FATHER", "Father"
    MOTHER = "MOTHER", "Mother"
    SPOUSE = "SPOUSE", "Spouse"
    BROTHER = "BROTHER", "Brother"
    SISTER = "SISTER", "Sister"
    SON = "SON", "Son"
    DAUGHTER = "DAUGHTER", "Daughter"
    FATHER_IN_LAW = "FATHER_IN_LAW", "Father-in-law"
    MOTHER_IN_LAW = "MOTHER_IN_LAW", "Mother-in-law"
    FRIEND = "FRIEND", "Friend"
    COLLEAGUE = "COLLEAGUE", "Colleague"
    OTHER = "OTHER", "Other"


class RentalIncome(models.TextChoices):
    ABOVE_75K = ">75K", ">75K"
    BETWEEN_50K_75K = "50-70k", "50-70k"
    BETWEEN_25K_50K = "25-50K", "25-50K"
    BELOW_25K = "<25K", "<25K"


class AnnualIncomeFamilyRange(models.TextChoices):
    ABOVE_20L = ">20L", ">20L"
    BETWEEN_15L_20L = "15-20L", "15-20L"
    BETWEEN_10L_15L = "10-15L", "10-15L"
    BELOW_10L = "<10L", "<10L"


class HouseOwnership(models.TextChoices):
    SELF_OWNED = "SELF_OWNED", "Self Owned"
    RENTED = "RENTED", "Rented"
    NATIVE_OWNED = "NATIVE_OWNED", "Native Owned"


class JewelleryType(models.TextChoices):
    ANKLET = "ANKLET", "Anklet"
    BANGLE = "BANGLE", "Bangle"
    BRACELET = "BRACELET", "Bracelet"
    CHAIN = "CHAIN", "Chain"
    EAR_RING = "EAR_RING", "Ear Ring"
    MANG_TIKKA = "MANG_TIKKA", "Mang Tikka"
    NECKLACE = "NECKLACE", "Necklace"
    NOSE_RING = "NOSE_RING", "Nose Ring"
    PENDANT = "PENDANT", "Pendant"
    RING = "RING", "Ring"
    WAIST_CHAIN = "WAIST_CHAIN", "Waist Chain"


class PaymentMode(models.TextChoices):
    NEFT = "NEFT", "NEFT"
    IMPS = "IMPS", "IMPS"
    RTGS = "RTGS", "RTGS"
    UPI = "UPI", "UPI"
    CASH = "CASH", "Cash"
    CHEQUE = "CHEQUE", "Cheque"


class FundTransferredBy(models.TextChoices):
    SELF = "SELF", "Self"
    THIRD_PARTY = "THIRD_PARTY", "Third Party"


class TransactionStatus(models.TextChoices):
    UNVERIFIED = "UNVERIFIED", "Unverified"
    VERIFIED = "VERIFIED", "Verified"
    REJECTED = "REJECTED", "Rejected"
