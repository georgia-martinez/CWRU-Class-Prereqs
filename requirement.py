from enum import Enum, auto

class Category(Enum):
    PREREQ = auto()
    COREQ = auto()

class Requirement:
    def __init__(self, category):
        self.category = category
        self.courses = []