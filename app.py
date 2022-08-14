from flask import Flask, render_template, request
from main import new_course_graph

app = Flask(__name__)

@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        course = request.form.get("course")

        new_course_graph(course)

        print(course)

        return render_template("index.html")
    else:
        return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)