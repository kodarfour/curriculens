from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json


driver = webdriver.Chrome()

url = "https://thecourseforum.com/department/49/"
driver.get(url)

wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.CLASS_NAME, "course-list")))


last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height


courses = driver.find_elements(By.CLASS_NAME, "rating-card")
course_data = []

for course in courses:
    try:
        course_code = course.find_element(By.ID, "title").text
        
        rating = course.find_element(By.ID, "rating").text
        if rating == "—":
            rating = None
        
        gpa = course.find_element(By.ID, "gpa").text
        if gpa == "—":
            gpa = None

        print(f"Course: {course_code}, Rating: {rating}, GPA: {gpa}")
    except Exception as e:
        print(f"Error extracting data: {e}")


driver.quit()
