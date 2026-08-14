from federal.models import SolidMapping,CityCode,StateCode


def getBranchList(searchtext):
    sol_mappings = SolidMapping.objects.filter(branch_location__icontains=searchtext)
    return sol_mappings
    
def getStateCode(stateName):
    try:
        return StateCode.objects.get(state_name=stateName)
    except StateCode.DoesNotExist:
        return " "
    
def getCityCode(cityName):
    try:
        return CityCode.objects.get(city_name=cityName)
    except CityCode.DoesNotExist:
        return " "