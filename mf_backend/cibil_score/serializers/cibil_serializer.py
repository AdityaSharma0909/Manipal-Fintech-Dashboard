from utils.envSetup import environment


class Address:
    def __init__(self, index, line_1, line_2, line_3, line_4,state_code, pin_code, addressCategory, residenceCode):
        self.index = index
        self.line1 = line_1
        self.line2 = line_2
        self.line3 = line_3
        self.line4 = line_4
        self.line5 = ""
        self.stateCode = state_code
        self.pinCode = pin_code
        self.addressCategory = addressCategory
        self.residenceCode = residenceCode

    def to_dict(self):
        return {
            "index": self.index,
            "line1": self.line1,
            "line2": self.line2,
            "line3": self.line3,
            "line4": self.line4,
            "line5": self.line5,
            "stateCode": str(self.stateCode),
            "pinCode": self.pinCode,
            "addressCategory": self.addressCategory,
            "residenceCode": self.residenceCode
        }

class TuefHeader:
    def __init__(self, application_no, statecode, loan_amount):
        valid_loan_amount_digits="000000000" # it should contain minimun 9 digits
        loan_amount_len=len(str(loan_amount))
        remaining_zeros=9-loan_amount_len
        loan_amount=valid_loan_amount_digits[:remaining_zeros]+str(loan_amount)
        self.headerType = "TUEF"
        self.version = "12"
        self.memberRefNo = application_no
        self.gststateCode = "29"
        if environment.APP_ENV=="PROD":
            self.enquiryMemberUserId="NB38619999_CIRC2CNPE"
            self.enquiryPassword="Bx8#Az4$Dr3#Bh"
        else:
            self.enquiryMemberUserId = "NB38619999_UATC2CNPE"
            self.enquiryPassword = "quilmxjTgmqmnrvtbucm@s7yuhwepr"
        self.enquiryPurpose = "05"
        self.enquiryAmount = str(loan_amount)
        self.scoreType = "08"
        self.outputFormat = "03"
        self.responsesize = 1
        self.ioMedia = "CC"
        self.authenticationMethod = "L"

    def to_dict(self):
        return {
            "headerType": self.headerType,
            "version": self.version,
            "memberRefNo": self.memberRefNo,
            "gstStateCode": self.gststateCode,
            "enquiryMemberUserId": self.enquiryMemberUserId,
            "enquiryPassword": self.enquiryPassword,
            "enquiryPurpose": self.enquiryPurpose,
            "enquiryAmount": self.enquiryAmount,
            "scoreType": self.scoreType,
            "outputFormat": self.outputFormat,
            "responseSize": self.responsesize,
            "ioMedia": self.ioMedia,
            "authenticationMethod": self.authenticationMethod
        }

class Name:
    def __init__(self, first_name, last_name, dob, gender):
        self.index = "N01"
        self.firstName = first_name
        self.middleName = ""
        self.lastName = last_name
        self.birthDate = str(dob)
        self.gender = gender

    def to_dict(self):
        return {
            "index": self.index,
            "firstName": self.firstName,
            "middleName": self.middleName,
            "lastName": self.lastName,
            "birthDate": self.birthDate,
            "gender": self.gender
        }

class ID:
    def __init__(self, pan_no, email):
        self.index_1 = "I01"
        self.idNumber_1 = pan_no
        self.idType_1 = "01"
        self.index_2 = "I02"
        self.idNumber_2 = email
        self.idType_2 = "51"

    def to_dict(self):
        return [
            {
                "index": self.index_1,
                "idNumber": self.idNumber_1,
                "idType": self.idType_1
            },
            # {
            #     "index": self.index_2,
            #     "idNumber": self.idNumber_2,
            #     "idType": self.idType_2
            # }
        ]

class Telephone:
    def __init__(self, phone):
        self.index = "T01"
        self.telephoneNumber = phone
        self.telephoneType = "01"

    def to_dict(self):
        return {
            "index": self.index,
            "telephoneNumber": self.telephoneNumber,
            "telephoneType": self.telephoneType
        }

# class EnquiryAccount:
#     def __init__(self, bank_account):
#         self.index = "I01"
#         self.accountNumber = bank_account
#
#     def to_dict(self):
#         return {
#             "index": self.index,
#             "accountNumber": self.accountNumber
#         }

class ConsumerInputSubject:
    def __init__(self, data, formatted_date, dob, gender):
        self.serviceCode = "CN1CAS0011"
        self.monitoringDate = formatted_date
        self.tuefHeader = TuefHeader(
            data.get('application_no'),
            statecode=data.get('state_code'),
            loan_amount=data.get('loan_amount')
        )
        self.names = [Name(data.get("first_name"), data.get("last_name"), dob, gender)]
        self.ids = ID(data.get("pan_no"), data.get('email'))
        self.telephones = [Telephone(data.get('phone'))]
        self.addresses = [Address(
            f"A{str(index + 1).zfill(2)}",
            address.get('line_1'),
            address.get('line_2',''),
            address.get('line_3',''),
            address.get('line_4',''),
            address.get('state_code'),
            address.get('pin_code'),
            address.get('residence_type'),
            address.get('address_category'),

        ) for index, address in enumerate(data.get('address',[]))]
        #self.enquiryAccounts = [EnquiryAccount(data.get("bank_account"))]

    def to_dict(self):
        #"enquiryAccounts": [account.to_dict() for account in self.enquiryAccounts]
        return {
            "serviceCode": self.serviceCode,
            "monitoringDate": self.monitoringDate,
            "consumerInputSubject": {
                "tuefHeader": self.tuefHeader.to_dict(),
                "names": [name.to_dict() for name in self.names],
                "ids": self.ids.to_dict(),
                "telephones": [telephone.to_dict() for telephone in self.telephones],
                "addresses": [address.to_dict() for address in self.addresses],
            }
        }


# # Example usage
# data = {
#     'application_no': '123456',
#     'pincode': '600054',
#     'loan_amount': '49500',
#     'first_name': 'John',
#     'last_name': 'Doe',
#     'pan_no': 'ABCDE1234F',
#     'email': 'john.doe@example.com',
#     'phone': '9893432110',
#     'address': {
#         'building_name': 'Building 1',
#         'line_1': 'Street 1',
#         'line_2': 'Area 1',
#         'state_code': '33',
#         'pin_code': '600054'
#     },
#     'bank_account': '1234567890'
# }
#
# formatted_date = '08102020'
# dob = '04071989'
# gender = 1
#
# consumer_input_subject = ConsumerInputSubject(data, formatted_date, dob, gender)
# result = consumer_input_subject.to_dict()
#
# print(result)
