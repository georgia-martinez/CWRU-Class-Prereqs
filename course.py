class Course:
    def __init__(self, name, code, credit_hours, description):
        self.code = code
        self.name = name
        self.credit_hours = credit_hours
        self.description = description
        self.prereqs = []
        self.coreqs = []
        self.visited = False

    def to_string(self):
        info = f"{self.code}: {self.name} ({self.credit_hours} units)\n{self.description}\n"

        if self.prereqs:
            info += "Prereqs: " + self.reqs_to_string(self.prereqs) + "\n"

        if self.coreqs:
            info += "Coreqs: " + self.reqs_to_string(self.prereqs)

        return info

    def reqs_to_string(self, req_list):
        req_string = ""

        for req in req_list:
            req_string += "[" + ", ".join(req.courses_string()) + "] "

        return req_string

