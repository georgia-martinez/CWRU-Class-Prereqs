from bs4 import BeautifulSoup
import requests
import re
from subject import *
from course import *

all_subjects = dict()

def create_subject_map():
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

def course_reqs(course_input):

    input_code = re.search("[A-Z]{4}\s[0-9]{3}", course_input).group(0)
    subject = re.search("[A-Z]{4}", input_code).group(0)

    # Get all courses for a specific subject
    url = all_subjects[subject].courses_link

    result = requests.get(url)
    doc = BeautifulSoup(result.text, "html.parser")

    tags = doc.find_all("div", class_="courseblock")

    # Try and find the course code
    for tag in tags:
        course_header = tag.find("p", class_="courseblocktitle").find("strong").string

        code = re.search("[A-Z]{4}\s[0-9]{3}", course_header).group(0)
        code = code.replace("\xa0", " ")  # remove hard spaces

        if code == input_code:
            break

    if code is None:
        print("ERROR: Code not found")
        return

    # Get course name, credit hours, and description
    name = re.search("[A-Z][a-zA-Z\s\(\)\.]*\. ", course_header).group(0)
    name = name[0:name.rindex(".")]

    credit_hours = re.search("[0-9]{1} -? ?[0-9]?", course_header).group(0).replace(" ", "")

    description = tag.find("p", class_="courseblockdesc").text
    description = description.replace("\n", "")
    description = description.replace("\xa0", " ") # remove hard spaces

    course = Course(name, code, credit_hours, description)

    # Find the prerequisites
    prereqs_text = re.search("Prereq:[\sa-zA-Z0-9]*", description)
    prereqs = prereqs_text.group(0) if prereqs_text is not None else ""

    prereqs = prereqs.split(" and ")

    for req in prereqs:
        courses = re.findall("[A-Z]{4}\s[0-9]{3}", req)

        if courses:
            course.prereqs.append(courses)

    # Find the corequisites
    coreqs_text = re.search("Coreq:[\sa-zA-Z0-9]*", description)
    coreqs = coreqs_text.group(0) if coreqs_text is not None else "None"

    courses = re.findall("[A-Z]{4}\s[0-9]{3}", coreqs)

    if courses:
        course.coreqs.append(courses)

    return course

if __name__ == "__main__":
    create_subject_map()
    course = course_reqs("MATH 319")
    print(course.info())