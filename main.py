import requests
import re
import random
import argparse
import json

from bs4 import BeautifulSoup
from pyvis.network import Network

from subject import *
from course import *
from requirement import *

all_subjects = dict()
all_courses = dict()

CODE_REGEX = "[A-Z]{4}\s[0-9]{3}[A-Z]?"

EDGE_COLORS = {
  "turquoise": "8cc9cf",
  "blue": "739cc0",
  "purple": "958ccf",
  "pink": "c78ccf",
  "red": "cf8c8c",
  "green": "8ccfa5"
}

used_edge_colors = EDGE_COLORS.copy()

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
    desc = course.description

    req_regex = "[\sa-zA-Z0-9\(\)/]*"

    prereqs_text = re.search("Prereq:" + req_regex, desc)
    prereqs = prereqs_text.group(0) if prereqs_text is not None else ""

    prereqs = prereqs.split(" and ")

    all_prereqs = []

    for req in prereqs:
        courses = re.findall(CODE_REGEX, req)

        if courses:
            all_prereqs.append(courses)

    for group in all_prereqs:
        req = Requirement(Category.PREREQ)

        for prereq in group:
            prereq_course = get_course(prereq)

            if prereq_course not in req.courses:
                req.courses.append(prereq_course)

        course.prereqs.append(req)

def random_color():

    if len(used_edge_colors) == 0:
        raise Exception("Out of unique edge colors")

    key = random.choice(list(used_edge_colors))
    color = used_edge_colors[key]

    del used_edge_colors[key]

    return color

def display_graph(root):
    net = Network("500px", "500px", directed=True)

    for key in all_courses:
        curr = all_courses[key]
        net.add_node(key, title=curr.name, color="#FFFFFF")
        curr.visited = False

    stack = [root]

    while stack:
        curr = stack[-1]
        stack.pop()

        if not curr.visited:
            curr.visited = True

        for req in curr.prereqs:

            if len(req.courses) == 1:
                edge_color = "#cccccc"
            else:
                edge_color = random_color()

            for prereq in req.courses:

                new_edge = {'from': prereq.code, 'to': curr.code, 'arrows': 'to'}

                if new_edge not in net.edges:
                    net.add_edge(prereq.code, curr.code, color=edge_color)

                if not all_courses[prereq.code].visited:
                    stack.append(all_courses[prereq.code])

    net.save_graph("course_prereqs.html")

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

def main(course_str):
    root_course = get_course(course_str)
    print(root_course.to_string())

    display_graph(root_course)

    add_node_click_code()

# Setting up the parser
parser = argparse.ArgumentParser(description="CWRU Prereq Visualizer")
parser.add_argument("-c", "--course", type=str, default="PHYS 122", metavar="", help="Name of a course (e.g. PHYS 122)")
args = parser.parse_args()

if __name__ == "__main__":
    main(args.course)