from enum import Enum, auto

class Category(Enum):
    PREREQ = auto()
    COREQ = auto()

class Requirement:
    def __init__(self, category):
        self.category = category
        self.courses = []

    def courses_string(self):
        return [x.code for x in self.courses]