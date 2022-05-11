from bs4 import BeautifulSoup
import requests
import re
from subject import *

url = "https://bulletin.case.edu/course-descriptions/"

result = requests.get(url)
doc = BeautifulSoup(result.text, "html.parser")

tags = doc.find_all("a", href=re.compile("/course-descriptions/[a-z]{4}/"), text=re.compile("\(?[A-Z]{4}\)\s[a-zA-Z]+"))

all_subjects = dict()

for tag in tags:
    text = tag.string

    name = re.search(" [a-zA-z /]+", text).group(0)
    code = re.search("[A-Z]{4}", text).group(0)

    all_subjects[code] = Subject(name, code, tag["href"])