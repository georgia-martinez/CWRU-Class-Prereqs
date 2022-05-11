class Course:
    def __init__(self, name, code, credit_hours, description):
        self.code = code
        self.name = name
        self.credit_hours = credit_hours
        self.description = description
        self.prereqs = []
        self.coreqs = []

    def info(self):
        print(f"{self.code}\n{self.name}\n{self.credit_hours}\n{self.description}\n{self.prereqs}\n{self.coreqs}")
