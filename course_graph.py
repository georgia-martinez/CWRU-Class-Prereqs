import random
from pyvis.network import Network

class CourseGraph():

    def __init__(self, course_dict):
        self.course_dict = course_dict
        self.edge_colors = {}

    def random_color(self):
        """
        @return: random edge color that hasn't been picked yet
        """

        if len(self.edge_colors) == 0:
            raise Exception("Out of unique edge colors")

        key = random.choice(list(self.edge_colors))
        color = self.edge_colors[key]

        del self.edge_colors[key]

        return color

    def create_graph(self, root):
        """
        Creates an HTML file with a new course graph for the given course

        @param root: course to create a graph for
        """

        net = Network("500px", "500px", directed=True)

        edge_colors = {
            "turquoise": "8cc9cf",
            "blue": "739cc0",
            "purple": "958ccf",
            "pink": "c78ccf",
            "red": "cf8c8c",
            "green": "8ccfa5"
        }

        for key in self.course_dict:
            curr = self.course_dict[key]
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
                    edge_color = self.random_color()

                for prereq in req.courses:

                    new_edge = {'from': prereq.code, 'to': curr.code, 'arrows': 'to'}

                    if new_edge not in net.edges:
                        net.add_edge(prereq.code, curr.code, color=edge_color)

                    if not self.course_dict[prereq.code].visited:
                        stack.append(self.course_dict[prereq.code])

        net.save_graph("course_prereqs.html")