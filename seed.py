from api import create_app, db
from api.models import User, Course, Enrollment, Assignment, Grade
from faker import Faker
import random
from datetime import datetime, timedelta, timezone

fake = Faker()


def seed_data():
    app = create_app()
    with app.app_context():
        db.session.query(Grade).delete()
        db.session.query(Assignment).delete()
        db.session.query(Enrollment).delete()
        db.session.query(Course).delete()
        db.session.query(User).delete()

        instructors = []
        for _ in range(5):
            instructor = User(
                name=fake.name()[:50],
                email=fake.unique.email(),
                phone=fake.phone_number()[:20],
                role="instructor",
            )
            instructor.set_password("password123")
            instructors.append(instructor)
            db.session.add(instructor)

        students = []
        for _ in range(20):
            student = User(
                name=fake.name()[:50],
                email=fake.unique.email(),
                phone=fake.phone_number()[:20],
                role="student",
            )
            student.set_password("password123")
            students.append(student)
            db.session.add(student)

        db.session.commit()

        courses = []
        for i in range(10):
            course = Course(
                name=f"Course {i + 1}",
                description=fake.text(max_nb_chars=200)[:200],
                instructor_id=random.choice(instructors).id,
            )
            courses.append(course)
            db.session.add(course)

        db.session.commit()

        for student in students:
            enrolled_courses = random.sample(courses, k=random.randint(1, 5))
            for course in enrolled_courses:
                enrollment = Enrollment(
                    student_id=student.id, course_id=course.id
                )
                db.session.add(enrollment)

        db.session.commit()

        assignments = []
        for course in courses:
            for _ in range(random.randint(2, 5)):
                assignment = Assignment(
                    title=fake.sentence(nb_words=5)[:100],
                    description=fake.text(max_nb_chars=150)[:150],
                    due_date=datetime.now(timezone.utc) + timedelta(days=random.randint(1, 30)),
                    course_id=course.id,
                )
                assignments.append(assignment)
                db.session.add(assignment)

        db.session.commit()

        for assignment in assignments:
            enrolled_students = Enrollment.query.filter_by(course_id=assignment.course_id).all()
            for enrollment in enrolled_students:
                grade = Grade(
                    assignment_id=assignment.id,
                    student_id=enrollment.student_id,
                    grade=random.uniform(50.0, 100.0),
                )
                db.session.add(grade)

        db.session.commit()
        print("Seeding complete!")


if __name__ == "__main__":
    seed_data()