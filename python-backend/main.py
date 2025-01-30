import requests
import json
import datetime

def get_recent_terms():
    now = datetime.datetime.now()
    month = int(now.strftime("%m"))
    day = int(now.strftime("%d")) # in case we need it
    year = int(now.strftime("%y"))

    if month < 4 or month > 11: # Might need to change this depending on when new classes exactly release
        seasons = ["2", "8", "2", "8"] # 2 means Spring semester, 8 means Fall
        years = [year, year-1, year-1, year-2]
    else:
        seasons = ["8", "2", "8", "2"]
        years = [year, year, year-1, year-1]

    terms = []
    for i in range(len(seasons)):
        terms.append("1" + str(years[i]) + str(seasons[i])) # terms formula is “1” + [2 digit year] + [2 for Spring, 8 for Fall
    
    return terms

def get_mnemonics(term):
    url = "https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearchOptions?institution=UVA01&term=" + term
    response = requests.get(url)
    course_mnemonics = [subject["subject"] for subject in response.json()["subjects"]]
    return course_mnemonics

def get_courses():
    base_url = 'https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearch?institution=UVA01'
    course = ('CS','4991') #example coures for now to test
    response = requests.get(base_url + '&subject=' + course[0] + '&catalog_nbr=' + course[1])
    return response



# response = get_courses()
# print(response.json())

#print(get_recent_terms())

terms = get_recent_terms()
print(get_mnemonics(terms[0]))