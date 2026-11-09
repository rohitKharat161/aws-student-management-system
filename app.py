from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "sqlite:///students.db"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# Student Database Model
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    course = db.Column(db.String(100), nullable=False)


# Home Page
@app.route("/")
def home():
    students = Student.query.all()
    return render_template("index.html", students=students)


# Add Student
@app.route("/add", methods=["POST"])
def add_student():
    student = Student(
        name=request.form["name"],
        email=request.form["email"],
        course=request.form["course"]
    )

    db.session.add(student)
    db.session.commit()

    return redirect("/")


# Health Check
@app.route("/health")
def health():
    return {"status": "healthy"}, 200


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)