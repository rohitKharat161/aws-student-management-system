
from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "student-app-local-key")

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "sqlite:///students.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    course = db.Column(db.String(100), nullable=False)


@app.route("/")
def home():
    students = Student.query.all()
    total_courses = db.session.query(
        Student.course
    ).distinct().count()

    return render_template(
        "index.html",
        students=students,
        total_courses=total_courses
    )
@app.route("/add", methods=["POST"])
def add_student():
    student = Student(
        name=request.form["name"].strip(),
        email=request.form["email"].strip().lower(),
        course=request.form["course"].strip()
    )

    db.session.add(student)

    try:
        db.session.commit()
        flash("Student added successfully!", "success")
    except IntegrityError:
        db.session.rollback()
        flash("Email already exists. Use another email.", "error")

    return redirect(url_for("home"))


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_student(id):
    student = db.get_or_404(Student, id)

    if request.method == "POST":
        student.name = request.form["name"].strip()
        student.email = request.form["email"].strip().lower()
        student.course = request.form["course"].strip()

        try:
            db.session.commit()
            flash("Student updated successfully!", "success")
            return redirect(url_for("home"))
        except IntegrityError:
            db.session.rollback()
            flash("Email already belongs to another student.", "error")

    return render_template("edit.html", student=student)


@app.route("/delete/<int:id>", methods=["POST"])
def delete_student(id):
    student = db.get_or_404(Student, id)

    db.session.delete(student)
    db.session.commit()

    flash("Student deleted successfully!", "success")
    return redirect(url_for("home"))


@app.route("/health")
def health():
    return {"status": "healthy"}, 200


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

