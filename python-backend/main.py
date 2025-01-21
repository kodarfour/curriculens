#PYTHON 3.12.2
import requests
import json

def get_courses():
    base_url = 'https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearch?institution=UVA01'
    course = ('CS','4991') #example coures for now to test
    response = requests.get(base_url + '&subject=' + course[0] + '&catalog_nbr=' + course[1])
    return response

response = get_courses()
print(response.json())
