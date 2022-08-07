"""
Creates a JSON file with all CWRU courses from every subject
"""

import requests
import re
import json

from bs4 import BeautifulSoup
from subject import *
from course import *
from requirement import *

CODE_REGEX = "[A-Z]{4}\s[0-9]{3}[A-Z]?"

def create_subject_map():
    """

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

        all_subjects[code] = Subject(code, name, "https://bulletin.case.edu" + tag["href"])

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
    
    """

    print(subject.code)

    url = subject.courses_link

    result = requests.get(url)
    doc = BeautifulSoup(result.text, "html.parser")

    tags = doc.find_all("div", class_="courseblock")

    courses = []

    for tag in tags:
        course_header = tag.find("p", class_="courseblocktitle").find("strong").string

        course_header.replace("\xa0", " ") # remove hard spaces

        course_header.replace("Unit.", "")
        course_header.replace("Units.", "")

        code = course_header[0:course_header.find(".")]

        # code = re.search("[A-Z]{4}\s[0-9]{3}[0-9]?[A-Z]?", course_header).group(0)
        credit_hours = re.search("[0-9]{1} -? ?.?[0-9]?", course_header).group(0).replace(" ", "")

        name = course_header.replace(code, "") # can't find code if hard spaces are removed before
        name = name.replace(credit_hours, "")

        name = re.search("[A-Z][a-zA-Z0-9-\s':,?/&+\(\)\.]*\.?", name).group(0)
        
        last_idx = name.rfind(".")

        if last_idx != -1:
            name = name[0:last_idx]
        
        name = re.sub(" *[0-9] ", "", name)

        description = tag.find("p", class_="courseblockdesc").text

        description = description.replace("EECS", "CSDS")
        description = description.replace("\n", "")
        description = description.replace("\xa0", " ") # remove hard spaces

        course = Course(name, code, credit_hours, description)
        courses.append(course)

    return courses

def create_json_file():
    all_subjects = create_subject_map()

    with open("course_data.json", "w") as json_file:
        for key in all_subjects:
            sub_courses = get_subject_courses(all_subjects[key])

            for course in sub_courses:
                json_string = json.dumps(course, default=encoder_course, indent=4)
                json_file.write(json_string)

if __name__ == "__main__":
    create_json_file()