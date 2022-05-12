from bs4 import BeautifulSoup
import requests
import re
from pyvis.network import Network

from subject import *
from course import *
from requirement import *

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

all_courses = dict()
code_regex = "[A-Z]{4}\s[0-9]{3}[A-Z]?"

def new_course(course_input):

    input_code = re.search(code_regex, course_input).group(0)

    # Check if course is already in the courses dictionary
    if input_code in all_courses:
        return all_courses[input_code]

    # Get all courses for a specific subject
    subject = re.search("[A-Z]{4}", input_code).group(0)

    url = all_subjects[subject].courses_link

    result = requests.get(url)
    doc = BeautifulSoup(result.text, "html.parser")

    tags = doc.find_all("div", class_="courseblock")

    # Try and find the course code on the site
    for tag in tags:
        course_header = tag.find("p", class_="courseblocktitle").find("strong").string

        code = re.search(code_regex, course_header).group(0)
        code = code.replace("\xa0", " ")  # remove hard spaces

        if code == input_code:
            break

    if code != input_code:
        print(f"ERROR: {input_code} not found")
        return

    # Get course name, credit hours, and description
    name = re.search("[A-Z][a-zA-Z\s\(\)\.]*\. ", course_header).group(0)
    name = name[0:name.rindex(".")]

    credit_hours = re.search("[0-9]{1} -? ?[0-9]?", course_header).group(0).replace(" ", "")

    description = tag.find("p", class_="courseblockdesc").text

    description = description.replace("EECS", "CSDS")
    description = description.replace("\n", "")
    description = description.replace("\xa0", " ") # remove hard spaces

    # Add course to courses dictionary
    course = Course(name, code, credit_hours, description)
    all_courses[code] = course

    # Set the prereqs
    set_reqs(course)

    return course

def set_reqs(course):
    desc = course.description

    req_regex = "[\sa-zA-Z0-9\(\)/]*"

    prereqs_text = re.search("Prereq:" + req_regex, desc)
    prereqs = prereqs_text.group(0) if prereqs_text is not None else ""

    prereqs = prereqs.split(" and ")

    all_prereqs = []

    for req in prereqs:
        courses = re.findall(code_regex, req)

        if courses:
            all_prereqs.append(courses)

    for group in all_prereqs:
        req = Requirement(Category.PREREQ)

        for prereq in group:
            prereq_course = new_course(prereq)

            if prereq_course not in req.courses:
                req.courses.append(prereq_course)

        course.prereqs.append(req)

def display_graph(root):
    net = Network("500px", "500px", directed=True)

    for key in all_courses:
        curr = all_courses[key]
        net.add_node(key, title=curr.name)
        curr.visited = False

    stack = [root]

    while stack:
        curr = stack[-1]
        stack.pop()

        if not curr.visited:
            curr.visited = True

        for req in curr.prereqs:
            for prereq in req.courses:

                new_edge = {'from': prereq.code, 'to': curr.code, 'arrows': 'to'}

                if new_edge not in net.edges:
                    net.add_edge(prereq.code, curr.code)

                if not all_courses[prereq.code].visited:
                    stack.append(all_courses[prereq.code])

    net.show("course_prereqs.html")

def main(string):
    create_subject_map()

    course = new_course(string)
    course.info()

    display_graph(course)

if __name__ == "__main__":
    main("MATH 319")