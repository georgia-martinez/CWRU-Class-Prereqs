class Course:
    def __init__(self, name, code, credit_hours, description):
        self.code = code
        self.name = name
        self.credit_hours = credit_hours
        self.description = description
        self.prereqs = []
        self.coreqs = []
        self.visited = False

    def info(self):
        print(self.code)
        print(self.name)
        print(self.credit_hours)
        print(self.description)
        print(self.reqs_to_string(self.prereqs))
        print(self.reqs_to_string(self.coreqs))

    def reqs_to_string(self, req_type):
        final_string = ""

        for req in req_type:
            req_string = "["

            for course in req.courses:
                req_string += course.code + " "

            req_string = req_string[:-1] + "]"
            final_string += req_string

        return final_string

