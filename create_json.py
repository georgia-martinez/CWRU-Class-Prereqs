"""
Creates a JSON file with all CWRU courses. The JSON file stores the course code, name, number of credit hours, and the course description.
"""

import requests
import re
import json
import unicodedata

from bs4 import BeautifulSoup
from subject import *
from course import *
from req import *

CODE_REGEX = "[A-Z]{4}\s[0-9]{3}[A-Z]?"

def subject_dictionary():
    """
    Parses through the CWRU course bulletin and creates a dictionary with all the different subjects (e.g. ACCT, CSDS, MATH. Course bulletin link (as of August 2022): "https://bulletin.case.edu/course-descriptions/"

    @return: dictionary with all subjects
    """

    all_subjects = dict()

    # Get all subjects
    url = "https://bulletin.case.edu/course-descriptions/"

    result = requests.get(url)
    doc = BeautifulSoup(result.text, "html.parser")

    tags = doc.find_all("a", href=re.compile("/course-descriptions/[a-z]{4}/"), text=re.compile("\(?[A-Z]{4}\)\s[a-zA-Z]+"))

    for tag in tags:
        text = tag.string

        name = re.search(" [a-zA-z /]+", text).group(0)
        code = re.search("[A-Z]{4}", text).group(0)

        name = unicodedata.normalize("NFKD", name)
        code = unicodedata.normalize("NFKD", code)

        link = "https://bulletin.case.edu" + tag["href"]

        all_subjects[code] = Subject(code, name, link)

    return all_subjects

def encoder_course(course):
    """
    Returns a JSON encoded version of the given course

    @param course: course to be encoded
    @return: JSON encoded course
    """

    if not isinstance(course, Course):
        raise TypeError(f"Object {course} is not of type Course")

    return {
        "code": course.code, 
        "name": course.name,
        "credit hours": course.credit_hours,
        "description": course.description
        }

def get_subject_courses(subject):
    """
    Parses the course bulletin of the specified subject and returns a list of course objects

    @param subject: e.g. ENGR or USSY
    @return: list of course objects from the given subject
    """

    print(subject.code)

    url = subject.courses_link

    result = requests.get(url)
    doc = BeautifulSoup(result.text, "html.parser")

    tags = doc.find_all("div", class_="courseblock")

    courses = []

    for tag in tags:
        header = tag.find("p", class_="courseblocktitle").find("strong").get_text(strip=True)
        header = unicodedata.normalize("NFKD", header)

        # Get the course code
        code = header[0:header.find(".")]

        # Get the credit hours
        header = header.replace(code, "")

        credit_hours = re.search("[0-9].? ?-? ?[0-9]?[0-9]? Units?\.", header).group(0)
        credit_hours = credit_hours[0:credit_hours.find("U")].strip()

        header = header.replace("Unit.", "")
        header = header.replace("Units.", "") 

        # Get the course name
        name = header.replace(credit_hours, "")
        name = re.search("[A-Z][a-zA-Z0-9-\s':,?/&+\(\)\.]*\.?", name).group(0)
        
        last_idx = name.rfind(".")

        if last_idx != -1:
            name = name[0:last_idx]
        
        # Get the description
        description = tag.find("p", class_="courseblockdesc").text

        description = description.replace("EECS", "CSDS")
        description = description.replace("\n", " ")
        description = unicodedata.normalize("NFKD", description)

        course = Course(name, code, credit_hours, description)
        courses.append(course)

    return courses

def create_json_file():
    """
    Creates a JSON file with all the course data
    """

    all_subjects = subject_dictionary()
    all_courses = []

    with open("templates/course_data.json", "w") as json_file:
        for key in all_subjects:
            sub_courses = get_subject_courses(all_subjects[key])
            all_courses.extend(sub_courses)

        json_string = json.dumps(all_courses, default=encoder_course, indent=4)
        json_file.write(json_string)

if __name__ == "__main__":
    create_json_file()