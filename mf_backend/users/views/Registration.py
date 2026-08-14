from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from ..serializers import UserResponseSerializer, UserUpdateSerializer
from utils.responseHandler import HttpResponse
import traceback
from utils.constants import ROLES, ROLE_MANAGEMENT_SCOPE, API_IMMUTABLE_ROLES
from branch.models import Branch,BranchUserMapping
from django.contrib.auth import get_user_model
import requests
from dateutil import parser as parser

from ..service.userService import UserService

User =get_user_model()
import utils.helper as helper
class RegistrationView(APIView):
    def post(self, request):
        try:
            data = request.data
            service = UserService()
            if not data:
                return HttpResponse.BadRequest({"error": "Empty Data"})

            actor_role = service.normalize_role(getattr(request.user, 'role', None))
            requested_role = service.normalize_role(data.get('role'))

            if actor_role == ROLES.VERTICAL_ADMIN.value and requested_role == ROLES.VERTICAL_ADMIN.value:
                return HttpResponse.Forbidden({"msg": "VERTICAL_ADMIN cannot create role VERTICAL_ADMIN"})

            try:
                user=get_user_model().objects.get(phone=data['phone'])
                return HttpResponse.BadRequest({'error':f'{user.role} is already registered with the given phone number {data["phone"]}'})
            except ObjectDoesNotExist:
                pass

            role = requested_role
            if actor_role not in ROLE_MANAGEMENT_SCOPE:
                return HttpResponse.Forbidden({"msg": f"{actor_role} is not authorized to create users"})
            if role in API_IMMUTABLE_ROLES:
                return HttpResponse.Forbidden({"msg": service.get_immutable_role_message(actor_role, role)})
            if role not in ROLE_MANAGEMENT_SCOPE.get(actor_role, ()): 
                return HttpResponse.Forbidden({"msg": f"{actor_role} cannot create role {role}"})

            if request.user.role==ROLES.CPC.value:
                print("i am cpc")
                role=data['role']
                if role==ROLES.CHIEF_BUSINESS_OPERATOR.value or role==ROLES.BUSINESS_HEAD.value or role==ROLES.CLUSTER_MANAGER.value or role==ROLES.REGIONAL_HEAD.value:
                    user=UserService().register_user(data)
                    return HttpResponse.Success({"message": "User created successfully"})
                if data["role"]==ROLES.BRANCH_MANAGER.value or role==ROLES.BRANCH_OPERATION_MANAGER.value:
                    user = User.objects.create_user(
                        username=data["username"],
                        first_name=data["first_name"],
                        last_name=data["last_name"],
                        phone=data["phone"],
                        email=data["email"],
                        aadhar_no=data["aadhar_no"],
                        designation=data["designation"],
                        pan_no=data["pan_no"],
                        date_of_joining=data["doj"],
                        employee_id=data["employee_id"],
                        role=ROLES.BRANCH_MANAGER.value,
                        is_active=data.get('is_active', True),
                        employee_profile_photo=data.get('employee_profile_photo',None)
                    )
                    password=helper.generate_password()

                    user.set_password(password)
                    user.save()
                    name=data["first_name"]+" "+data["last_name"]
                    helper.sendEmailUser(email=data["email"],username=data["username"],password=password,name=name)
                    # FCMService([user]).generateNotification(
                    #             title="Loan Officer",
                    #             message=f"Your username : {user.username}  , phone : {user.phone} , first name : {user.first_name} , last name : {user.last_name}, password : {password}"
                    #         )
                    return HttpResponse.Success({"message": "User created successfully"})
            
                
                elif data["role"]==ROLES.LOAN_OFFICER.value:
                    data=request.data
                    if data["branch_id"]:

                        branch=Branch.objects.get(branch_id=str(data["branch_id"]))
                        user = User.objects.create_user(
                        username=data["username"],
                        first_name=data["first_name"],
                        last_name=data["last_name"],
                        email=data["email"],
                        phone=data["phone"],
                        aadhar_no=data["aadhar_no"],
                        designation=data["designation"],
                        pan_no=data["pan_no"],
                        date_of_joining=data["doj"],
                        employee_id=data["employee_id"],
                        role=ROLES.LOAN_OFFICER.value,
                        is_active=data.get('is_active', True),
                        employee_profile_photo=data.get('employee_profile_photo', None)
                    )
                        password=helper.generate_password()
                        user.set_password(password)
                        user.save()
                        name=data["first_name"]+" "+data["last_name"]
                        helper.sendEmailUser(email=data["email"],username=data["username"],password=password,name=name)
                       

                            
                           
                        BranchUserMapping.objects.create(
                        branch=branch,
                        user= user,
                        source_id=500,
                        ).save()   
                        # FCMService([user]).generateNotification(
                        #             title="Loan Officer",
                        #             message=f"Your username : {user.username}  , phone : {user.phone} , first name : {user.first_name} , last name : {user.last_name}, password : {password}"
                        #         )
                        return HttpResponse.Success({"password": password})
                            
                            
                            # return HttpResponse.Success({"message": ser.data})
                            
                    else:
                         return HttpResponse.BadRequest({"error": "Cannot add user without branch"})
                        
                            

                else:
                    return HttpResponse.BadRequest({"error": f"role - {role} is invalid"})
                    
                    
            elif request.user.role==ROLES.BRANCH_MANAGER.value:
                if data["role"]==ROLES.LOAN_OFFICER.value:
                    if data["branch_id"]:
                        branch=Branch.objects.get(branch_id=str(data["branch_id"]))
                        
                        user = User.objects.create_user(
                            username=data["username"],
                            first_name=data["first_name"],
                            last_name=data["last_name"],
                            phone=data["phone"],
                            email=data["email"],
                            aadhar_no=data["aadhar_no"],
                            designation=data["designation"],
                            pan_no=data["pan_no"],
                            date_of_joining=data["doj"],
                            employee_id=data["employee_id"],
                            role=ROLES.LOAN_OFFICER.value,
                            is_active=data.get('is_active', True),
                            employee_profile_photo=data.get('employee_profile_photo', None)
                        )
                        password=helper.generate_password()
                        print(password)
                        user.set_password(password)
                        user.save()

                        helper.sendEmailUser(email=data["email"],username=data["username"],password=password,name=data.get('first_name',"")+" "+data.get('last_name', ""))
                        BranchUserMapping.objects.create(
                        branch=branch,
                        user= user,
                        source_id=500,
                        ).save()   

                        # FCMService([user]).generateNotification(
                        #             title="Loan Officer",
                        #             message=f"Your username : {user.username}  , phone : {user.phone} , first name : {user.first_name} , last name : {user.last_name}, password : {password}"
                        #         )
                        return HttpResponse.Success({"password": password})
                    else:
                        return HttpResponse.BadRequest({"error": "Cannot add user without branch"})
                            
                            
                            # return HttpResponse.Success({"message": ser.data})
                            

                        
                            
                        # return HttpResponse.BadRequest({"error": ser.errors})

                        

                            # print("Branch id is not there")
                            # user = User.objects.create_user(
                            # username=data["username"],
                            # # password=data["password"],
                            # first_name=data["first_name"],
                            # last_name=data["last_name"],
                            # phone=data["phone"],
                            # email=data["email"],
                            # aadhar_no=data["aadhar_no"],
                            # designation=data["designation"],
                            # pan_no=data["pan_no"],
                            # date_of_joining=data["doj"],
                            # employee_id=data["employee_id"],
                            # role=ROLES.LOAN_OFFICER.value,
                            # is_active=True
                            # )#.save()
                            # password=helper.generate_password()
                            # user.set_password(user.set_password(password))
                            # user.save()
                            # helper.sendEmailUser(email=data["email"],username=data["username"],password=password,name=name)
                    
                    return HttpResponse.Success({"message": "User created successfully"})
                else:
                    return HttpResponse.BadRequest({"error": " is allowed "})
            else:
                return HttpResponse.BadRequest({"error": "Only Branch Manager is allowed "})       
            
            
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
    
    def patch(self, request):
        try:
            user = User.objects.get(
                user_id=request.GET.get("user_id", "")
            )
            data = request.data
            service = UserService()
            if not data:
                return HttpResponse.BadRequest({"error": "Empty Data"})
            
            # retrieve the user to be updated
            if "date_of_joining" in data:
                data['date_of_joining']=parser.parse(data.pop('date_of_joining')).replace(tzinfo=None).date()
            print(data)
            if "role" in data:
                if request.user.role in ROLE_MANAGEMENT_SCOPE:
                    if data["role"] in API_IMMUTABLE_ROLES:
                        return HttpResponse.Forbidden({"msg": service.get_immutable_role_message(request.user.role, data['role'])})
                    if data["role"] != user.role and data["role"] not in ROLE_MANAGEMENT_SCOPE.get(request.user.role, ()):
                        return HttpResponse.BadRequest({"error": f"role - {data['role']} is invalid for {request.user.role}"})
                if request.user.role == ROLES.BRANCH_MANAGER.value:
                    if data["role"] != ROLES.LOAN_OFFICER.value:
                        return HttpResponse.BadRequest({"error": "Only Loan Officer is allowed"})

            if "password" in data:
                if data["password"] == data["confirm_password"]:
                    if len(data["password"]) >= 8:
                        user.set_password(data["password"])
                    else:
                        return HttpResponse.BadRequest({"error": "Password must be at least 8 characters"})
                else:
                    return HttpResponse.BadRequest({"error": "Password and confirm password does not match"})
            print(data)
            user_update = UserUpdateSerializer(instance=user, data=data, partial=True)
            if user_update.is_valid():
                user_update.save()
                print(user_update.data)
            else:
                return HttpResponse.BadRequest(user_update.errors)
            # if "first_name" in data:
            #     user.first_name = data["first_name"]
            # if "last_name" in data:
            #     user.last_name = data["last_name"]
            # if "email" in data:
            #     user.email = data["email"]
            # if "designation" in data:
            #     user.designation = data["designation"]
            # if "aadhar_no" in data:
            #     user.aadhar_no = data["aadhar_no"]

            # if "pan_no" in data:
            #     user.pan_no = data["pan_no"]
            # if "employee_id" in data:
            #     user.employee_id = data["employee_id"]
            # if "phone" in data:
            #     #if user.phone == data["phone"]:
            #     #    return HttpResponse.BadRequest({"error": "Phone number is same"})
            #     user.phone = data["phone"]
            #
            # user.status=data.get('status')
            # # save the updated user
            # user.save()

            return HttpResponse.Success({"message": "User updated successfully"})

        except User.DoesNotExist:
            return HttpResponse.NotFound({"error": "User not found"})
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))

    

class BranchManager(APIView):
    def get(self, request):
        try:
            # if request.user.role==ROLES.CPC.value:
            branch_managers=User.objects.filter(role=ROLES.BRANCH_MANAGER.value)
            return HttpResponse.Success({"branch_managers": UserResponseSerializer(branch_managers, many=True).data})
                
            # else:
            #     return HttpResponse.BadRequest({"error": "Only Branch Manager is allowed "})
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))


class UserByRole(APIView):
    def get(self, request):
        try:
            role = request.GET.get('role')
            if role == 'bm':
                r = ROLES.BRANCH_MANAGER.value
            elif role == 'cm':
                r = ROLES.CLUSTER_MANAGER.value
            elif role == 'abm':
                r = ROLES.ASSISTANT_BRANCH_MANAGER.value
            elif role == 'rh':
                r = ROLES.REGIONAL_HEAD.value
            else:
                return HttpResponse.BadRequest("Wrong role given")

            branch_managers=User.objects.filter(role=r)
            return HttpResponse.Success({"users": UserResponseSerializer(branch_managers, many=True).data})
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))



class TestView(APIView):
    def get(self, request):
        try:
           
            url = "https://ibjarates.com/"

            payload = {}
            headers = {}

            response = requests.request("GET", url, headers=headers, data=payload)

            print(response.text)

            return HttpResponse.Success(response.text)
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
        


class AllUsers(APIView):
    def get(self, request):
        try:
            
            branch_managers=User.objects.filter(role=ROLES.BRANCH_MANAGER.value)
            loan_managers=User.objects.filter(role=ROLES.LOAN_OFFICER.value)
            return HttpResponse.Success({"branch_managers": UserResponseSerializer(branch_managers, many=True).data,"loan_managers": UserResponseSerializer(loan_managers, many=True).data})
            
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))

class UserAll(APIView):
    def get(self, request):
        try:
            user = User.objects.get(
                user_id=request.GET.get("user_id", "")
            )
            return HttpResponse.Success({"user": UserResponseSerializer(user).data})
        
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
