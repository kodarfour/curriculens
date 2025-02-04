import requests
from datetime import datetime

import psycopg
from psycopg.types.json import Jsonb

POSSIBLE_ATTRIBUTES = [
    "ASUD-CSW", "ASUD-HP", "ASUD-LS", "ASUD-AIP", "ASUD-CMP", "ASUD-SES", "ASUD-SS",
    "ASUW-WL", "ASUQ-QCD", "ASUR-R21C1", "ASUR-R21C2",
    "NW", "SW", "HS", "HNS", "FL",
    "NCLC-NOCOST", "NCLC-LOWCOST",
    "CSAS", "CSSS", "SSAS", "AST", "ASA", "CSA", "CST", "SSA", "SST", "TA",
    "CORE-CRITTHINK", "CORE-ORALCOMM", "CORE-QUANTITAT", "CORE-RESEARCH",
    "CORE-SCIENTIFIC", "CORE-WRITTEN"
]

def get_recent_terms():
    now = datetime.now()
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

def process_time(time):
    if not time:
        return None
    try:
        return datetime.strptime(time, "%H.%M.%S.%f").strftime("%H:%M:%S")
    except ValueError as e:
        print(f"Time conversion error: {e} for input {time}")
        return None

def get_mnemonics(term):
    url = "https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearchOptions?institution=UVA01&term=" + term
    response = requests.get(url)
    course_mnemonics = [subject["subject"] for subject in response.json()["subjects"]]
    return course_mnemonics

def get_courses(term, subject, page): # specific term, subject, and page
    base_url = "https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearch?institution=UVA01"
    response = requests.get(base_url + '&term=' + term + '&subject=' + subject + '&page=' + page)
    if response.status_code != 200:
        print(f"Failed to fetch courses for {subject} {term}, page {page}")
        return {"pageCount": 0, "classes": []}  # Prevent NoneType errors

    try:
        data = response.json()
        return data
    except Exception as e:
        print(f"JSON parsing error: {e}")
        return {"pageCount": 0, "classes": []}

def get_attributes(crse_attr_value):
    active_attributes = crse_attr_value.split(",") if crse_attr_value else []
    attributes_jsonb = {attr: (attr in active_attributes) for attr in POSSIBLE_ATTRIBUTES}

    return attributes_jsonb

def get_course_data(r, semester, existing_courses):
    course_type = r["component"]

    parent_course_id = None
    if course_type in {"LAB", "DIS"}:
        key = (r["subject"], r["catalog_nbr"], semester)
        possible_lectures = existing_courses.get(key, [])
        print(possible_lectures)
        if possible_lectures:
            parent_course_id = possible_lectures

    course_data = {
        "department": r["subject_descr"],
        "subject": r["subject"],
        "course_number": r["catalog_nbr"],
        "credits": int(r["units"][-1]), # gets the highest credit count if there is a range
        "instruction_mode": r["instruction_mode_descr"],
        "location": r["meetings"][0]["facility_descr"] if r.get("meetings") else None,
        "days": r["meetings"][0]["days"] if r.get("meetings") else None,
        "start_time": process_time(r["meetings"][0]["start_time"]) if r.get("meetings") else None,
        "end_time": process_time(r["meetings"][0]["end_time"]) if r.get("meetings") else None,
        "section": r["class_section"],
        "professors": [instructor["name"] for instructor in r["instructors"]],
        "semester": semester,
        "attributes": Jsonb(get_attributes(r.get("crse_attr_value"))),
        "type": course_type,
        "parent_course_id": parent_course_id
    }
    return course_data



# Config for local PostgreSQL database
DB_CONFIG = {
    "dbname": "curriculens",
    "user": "myuser",
    "password": "mypassword",
    "host": "host.docker.internal",
    "port": 5432,
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
    professors TEXT[],
    semester VARCHAR(50),
    attributes JSONB,
    type VARCHAR(50),
    parent_course_id INTEGER[],
    UNIQUE (subject, course_number, section, semester)
);
"""

# Base query for insert
INSERT_SQL = """
INSERT INTO courses (
    department, subject, course_number, credits, instruction_mode,
    location, days, start_time, end_time, section, professors,
    semester, attributes, type, parent_course_id
) VALUES (
    %(department)s, %(subject)s, %(course_number)s, %(credits)s, %(instruction_mode)s,
    %(location)s, %(days)s, %(start_time)s, %(end_time)s, %(section)s, %(professors)s,
    %(semester)s, %(attributes)s, %(type)s, %(parent_course_id)s
)RETURNING id;
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
                    existing_courses = {}
                    r = get_courses(term, subject, str(1))
                    page_count = r["pageCount"]
                    for course in r["classes"]:
                        if int(course["catalog_nbr"]) >= 5000:
                            page_count = -1
                            break
                        course_data = get_course_data(course, semester, existing_courses)
                        cursor.execute(INSERT_SQL, course_data)
                        inserted_id = cursor.fetchone()[0] 

                        if course["component"] == "LEC":
                            key = (course["subject"], course["catalog_nbr"], semester)
                            existing_courses.setdefault(key, []).append(inserted_id)

                        print(subject, course["catalog_nbr"], course["class_section"], semester, "inserted successfully into the 'courses' table!")
                    conn.commit()

                    if page_count < 2:
                        continue
                    for page in range(2, page_count+1):
                        r = get_courses(term, subject, str(page))
                        for course in r["classes"]:
                            if int(course["catalog_nbr"]) >= 5000:
                                page_count = -1
                                break
                            course_data = get_course_data(course, semester, existing_courses)
                            cursor.execute(INSERT_SQL, course_data)
                            inserted_id = cursor.fetchone()[0] 

                            if course["component"] == "LEC":
                                key = (course["subject"], course["catalog_nbr"], semester)
                                existing_courses.setdefault(key, []).append(inserted_id)

                            print(subject, course["catalog_nbr"], course["class_section"], semester, "inserted successfully into the 'courses' table!")
                        conn.commit()
                        if page_count < 0:
                            break



            
except Exception as e:
    print(f"An error occurred: {e}")