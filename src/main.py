from bs4 import BeautifulSoup
import requests
import re
import networkx as nx
import matplotlib.pyplot as plt

from subject import *
from course import *
from node import *

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

def find_course_reqs(course_input):

    code_regex = "[A-Z]{4}\s[0-9]{3}[A-Z]?"
    input_code = re.search(code_regex, course_input).group(0)
    subject = re.search("[A-Z]{4}", input_code).group(0)

    # Get all courses for a specific subject
    url = all_subjects[subject].courses_link

    result = requests.get(url)
    doc = BeautifulSoup(result.text, "html.parser")

    tags = doc.find_all("div", class_="courseblock")

    # Try and find the course code
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

    course = Course(name, code, credit_hours, description)

    # Find the prerequisites
    req_regex = "[\sa-zA-Z0-9\(\)/]*"

    prereqs_text = re.search("Prereq:" + req_regex, description)
    prereqs = prereqs_text.group(0) if prereqs_text is not None else ""

    prereqs = prereqs.split(" and ")

    for req in prereqs:
        courses = re.findall(code_regex, req)

        if courses:
            course.prereqs.append(courses)

    # Find the corequisites
    coreqs_text = re.search("Coreq:" + req_regex, description)
    coreqs = coreqs_text.group(0) if coreqs_text is not None else "None"

    courses = re.findall(code_regex, coreqs)

    if courses:
        course.coreqs.append(courses)

    # Update course dictionary
    if course.code not in all_courses:
        all_courses[course.code] = course

        # Call function on all prereqs and coreqs
        for group in course.prereqs:
            for prereq in group:
                find_course_reqs(prereq)

        for group in course.coreqs:
            for coreq in group:
                find_course_reqs(coreq)

def create_graph(root):
    graph = nx.DiGraph()

    print(root.code)

    nodes = dict()

    for key in all_courses:
        nodes[key] = Node(all_courses[key])
        graph.add_node(all_courses[key].code)

    stack = [nodes[root.code]]

    while stack:
        curr_node = stack[-1]
        stack.pop()

        if not curr_node.visited:
            curr_node.visited = True

        for group in curr_node.course.prereqs:
            for prereq in group:
                graph.add_edge(all_courses[prereq].code, curr_node.course.code)

                if not nodes[prereq].visited:
                    stack.append(nodes[prereq])

    pos = nx.spring_layout(graph)
    nx.draw_networkx_nodes(graph, pos, node_size=500)
    nx.draw_networkx_edges(graph, pos, edgelist=graph.edges(), edge_color="black")
    nx.draw_networkx_labels(graph, pos)

    plt.show()

if __name__ == "__main__":
    create_subject_map()

    test_code = "CSDS 338"

    find_course_reqs(test_code)
    course = all_courses[test_code]

    create_graph(course)