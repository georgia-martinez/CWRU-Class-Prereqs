import re
import argparse
import json

from subject import *
from course import *
from requirement import *
from course_graph import CourseGraph

all_courses = dict()

def get_course(code):
    """
    Given a course code, returns the corresponding Course object

    @param code: (e.g. CSDS 132)
    @return: Course object 
    """

    # Check if course is already in the course dictionary
    if code in all_courses:
        return all_courses[code]

    # Otherwise create a new course object
    with open("course_data.json", "r") as json_file:
        data = json.load(json_file)

        for i in range(len(data)):
            course = data[i]

            if course["code"] == code:
                break
    
    # Check if the course was found
    if i == len(data) - 1 and code != data[-1]["code"]:
        raise Exception(f"{code} does not exist")

    new_course = Course(course["name"], course["code"], course["credit hours"], course["description"])

    all_courses[code] = new_course

    set_requirements(new_course)

    return new_course

def set_requirements(course):
    """
    Recursively sets the requirements for the given course and all of its prereqs

    @param course: course to start with
    """

    desc = course.description

    req_regex = "[\sa-zA-Z0-9\(\)/]*"

    prereqs_text = re.search("Prereq:" + req_regex, desc)
    prereqs = prereqs_text.group(0) if prereqs_text is not None else ""

    prereqs = prereqs.split(" and ")

    all_prereqs = []

    for req in prereqs:
        courses = re.findall("[A-Z]{4}\s[0-9]{3}[A-Z]?", req)

        if courses:
            all_prereqs.append(courses)

    for group in all_prereqs:
        req = Requirement(Category.PREREQ)

        for prereq in group:
            prereq_course = get_course(prereq)

            if prereq_course not in req.courses:
                req.courses.append(prereq_course)

        course.prereqs.append(req)

def add_node_click_code():
    """
    Adds code to the PyVis generated html file to make the nodes return info when clicked
    """

    html_file = "course_prereqs.html"
    start_line = 0

    LINE_BEFORE = "network = new vis.Network(container, data, options);"

    # Find the correct spot to insert the new code
    with open(html_file, "r") as f:
        data = f.readlines()

        for i in range(len(data)):
            line = data[i]

            if LINE_BEFORE in line:
                start_line = i + 2 # Line to insert the new code
                break

    # Insert the new lines of code
    with open(html_file, "w") as f:
        code_to_insert = """

        network.on("click", function (params) {
            console.log(params.nodes[0]);
        });
        """

        data.insert(start_line, code_to_insert)
        f.writelines(data)

def new_course_graph(input_course):
    """
    Main method that does like everything
    """

    root_course = get_course(input_course)
    print(root_course.to_string())

    course_graph = CourseGraph(all_courses)
    course_graph.create_graph(root_course)

    add_node_click_code()

# Setting up the parser
parser = argparse.ArgumentParser(description="CWRU Prereq Visualizer")
parser.add_argument("-c", "--course", type=str, default="PHYS 122", metavar="", help="Name of a course (e.g. PHYS 122)")
args = parser.parse_args()

if __name__ == "__main__":
    new_course_graph(args.course)