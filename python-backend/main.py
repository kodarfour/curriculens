import requests
import datetime

import psycopg
from psycopg.types.json import Jsonb

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
        terms.append("1" + str(years[i]) + str(seasons[i])) # terms formula is “1” + [2 digit year] + [2 for Spring, 8 for Fall]
    
    return terms

def term_to_semester_translator(term):
    sem = ""
    if term[-1] == "8":
        sem = "Fall"
    else:
        sem = "Spring"
    return sem + " 20" + term[1:3]

def get_mnemonics(term):
    url = "https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearchOptions?institution=UVA01&term=" + term
    response = requests.get(url)
    course_mnemonics = [subject["subject"] for subject in response.json()["subjects"]]
    return course_mnemonics

def get_courses(term, subject, page): # specific term, subject, and page
    base_url = "https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearch?institution=UVA01"
    response = requests.get(base_url + '&term=' + term + '&subject=' + subject + '&page=' + page)
    return response.json()

def get_course_data(r, semester):
    course_data = {
        "department": r["subject_descr"],
        "subject": r["subject"],
        "course_number": r["catalog_nbr"],
        "credits": int(r["units"]),
        "instruction_mode": r["instruction_mode_descr"],
        "location": r["meetings"][0]["facility_descr"],
        "days": r["meetings"][0]["days"],
        "start_time": r["meetings"][0]["start_time"],
        "end_time": r["meetings"][0]["end_time"],
        "section": r["class_section"],
        "professors": [instructor["name"] for instructor in r["instructors"]],
        "semester": semester,
        "attributes": r["crse_attr_value"],
        "type": "Lecture",
    }
    return course_data



# Config for local PostgreSQL database
DB_CONFIG = {
    "dbname": "curriculens",
    "user": "myuser",
    "password": "mypassword",
    "host": "localhost",
    "port": 4564,
}

# Base query to create the table
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS courses (
    id SERIAL PRIMARY KEY,
    department VARCHAR(100),
    subject VARCHAR(100),
    course_number INTEGER,
    credits INTEGER,
    instruction_mode VARCHAR(50),
    location VARCHAR(100),
    days VARCHAR(50),
    start_time TIME,
    end_time TIME,
    section VARCHAR(50),
    professor TEXT[],
    semester VARCHAR(50),
    attributes VARCHAR(50),
    type VARCHAR(50),
    UNIQUE (subject, course_number, section, semester)
);
"""

# Base query for insert
INSERT_SQL = """
INSERT INTO courses (
    department, subject, course_number, credits, instruction_mode,
    location, days, start_time, end_time, section, professor,
    semester, attributes, type
) VALUES (
    %(department)s, %(subject)s, %(course_number)s, %(credits)s, %(instruction_mode)s,
    %(location)s, %(days)s, %(start_time)s, %(end_time)s, %(section)s, %(professor)s,
    %(semester)s, %(attributes)s, %(type)s
);
"""


recent_terms = get_recent_terms()
course_mmnemonics = ["CS"] #get_mnemonics()

try:
    # Connect to the PostgreSQL database using psycopg 3
    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute(CREATE_TABLE_SQL)

            for term in recent_terms:
                semester = term_to_semester_translator(term)
                for subject in course_mmnemonics:
                    r = get_courses(term, subject, 1)
                    page_count = r["pageCount"]
                    for course in r["classes"]:
                        course_data = get_course_data(course, semester)
                        cursor.execute(INSERT_SQL, course_data)
                        print(semester, subject, "page 1 data inserted successfully into the 'courses' table!")

                    if page_count == 1:
                        continue
                    for page in range(2, page_count+1):
                        response = get_courses(term, subject, page)
                        for course in r["classes"]:
                            course_data = get_course_data(course, semester)
                            cursor.execute(INSERT_SQL, course_data)
                            print(semester, subject, "page", page, "data inserted successfully into the 'courses' table!")



            
except Exception as e:
    print(f"An error occurred: {e}")