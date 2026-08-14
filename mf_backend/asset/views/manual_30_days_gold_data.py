# import pytz
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from  dateutil import parser as parser
# import datetime
# from asset.models import GoldPriceData
# from utils.helper import get_gold_price


# class ManualUploadGoldData(APIView):

#     def post(self,request):
#         data=request.data
#         upload_data=[]
#         for date,price in data.items():
#             create_date=parser.parse(date)
#             timezone = pytz.timezone('Asia/Kolkata')

#             # Add timezone information to the datetime object
#             create_date = timezone.localize(create_date)
#             gold_price=price/10
#             lending_price=gold_price*0.75
#             upload_data.append(GoldPriceData(gold_price=gold_price, karat=22, lending_price=lending_price, created_at=create_date))

#         #GoldPriceData.objects.bulk_create(upload_data)
#         start_date = datetime.date.today() - datetime.timedelta(days=30)
#         end_date = datetime.datetime.now()
#         resp=list(GoldPriceData.objects.filter(
#             created_at__gte=start_date, created_at__lte=end_date
#         ).values())

#         return Response(resp, 200)