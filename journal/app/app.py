from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sqlalchemy as sa
import os

app = Flask(__name__)
application = app

app.config.from_pyfile('config.py')

ip = os.getenv('ip')
PGUSER = str(os.getenv('PGUSER'))
PGPASSWORD = str(os.getenv('PGPASSWORD'))
DATABASE = str(os.getenv('DATABASE'))

POSTGRES_URI = f'postgresql://{PGUSER}:{PGPASSWORD}@{ip}/{DATABASE}'

app.config['SQLALCHEMY_DATABASE_URI'] = POSTGRES_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(app, metadata=metadata)
migrate = Migrate(app, db)

# from models import Student, PlanOfStudy, Gradebook

class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    lastname = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    admission_year = db.Column(db.Integer, nullable=False)
    education_form = db.Column(db.String(100), nullable=False)
    group = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '<Student %r>' % self.lastname
    
    # __table_args__ = {'extend_existing': True}
    
class PlanOfStudy(db.Model):
    __tablename__ = 'planofstudy'

    id = db.Column(db.Integer, primary_key=True)
    speciality = db.Column(db.String(100), nullable=False)
    discipline = db.Column(db.String(100), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    hours = db.Column(db.Integer, nullable=False)
    exam_or_test = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return self.discipline

class Gradebook(db.Model):
    __tablename__ = 'gradebook'

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    discipline_id = db.Column(db.Integer, db.ForeignKey("planofstudy.id"), nullable=False)
    mark = db.Column(db.Integer, nullable=False)

    student = db.relationship('Student')
    planofstudy = db.relationship('PlanOfStudy')   

@app.route('/')
def index():
    # fill_db()
    return render_template('index.html' )

@app.route('/schetchik', methods=['GET', 'POST'])
def schetchik():
    if request.method == 'POST':
        form_of_educ = request.form['select_form']
        student_count = Student.query.filter_by(education_form=form_of_educ).count()
        return render_template('schetchik.html', title='Счетчик', student_count=student_count, form_of_educ=form_of_educ)
    return render_template('schetchik.html', title='Счетчик', student_count=None)

@app.route('/disciplineinfo', methods=['GET', 'POST'])
def disciplineinfo():
    if request.method == 'POST':
        selected_discipline = request.form.get('discipline_name') or request.args.get('selected_discipline')
        print(request.args)
        try:
            hours = PlanOfStudy.query.filter_by(discipline=selected_discipline).first().hours
            otchet = PlanOfStudy.query.filter_by(discipline=selected_discipline).first().exam_or_test
        except:
            flash("Такой дисциплины несуществует", "danger")
            return render_template('disciplineinfo.html', title='Инфорация о дисциплине', hours=None)
        
        return render_template('disciplineinfo.html', title='Инфорация о дисциплине', hours=hours, otchet=otchet, selected_discipline=selected_discipline)
    
    return render_template('disciplineinfo.html', title='Инфорация о дисциплине', hours=None)

@app.route('/studentslist')
def studentslist():
    students_arr = Student.query.all()
    return render_template('studentslist.html', title='Список студентов', students=students_arr)

@app.route('/educationplanslist')
def educationplanslist():
    educationplans_arr = PlanOfStudy.query.all()
    return render_template('educationplanslist.html', title='Список учебных планов', educationplans = educationplans_arr)

@app.route('/createstudent', methods=['GET', 'POST'])
def createstudent():
    if request.method == 'POST':
        name = request.form.get('name')
        lastname = request.form.get('lastname')
        surname = request.form.get('surname')
        admission_year = request.form.get('admission_year')
        education_form = request.form.get('education_form')
        group = request.form.get('group')
        try:
            student = Student(name=name, lastname=lastname, surname=surname, admission_year=admission_year, education_form=education_form, group=group)
            db.session.add(student)
            db.session.commit()
            flash("Пользователь успешно добавлен", "success")
            return redirect(url_for("studentslist"))
        except:
            flash("Произошла ошибка", "danger")
            return render_template('createstudent.html', title='Добавление студента')

    return render_template('createstudent.html', title='Добавление студента')

@app.route('/editstudent/<int:id>', methods=['GET', 'POST'])
def editstudent(id):
    student = Student.query.get_or_404(id)
    if request.method == 'POST':
        student.name = request.form.get('name')
        student.lastname = request.form.get('lastname')
        student.surname = request.form.get('surname')
        student.admission_year = request.form.get('admission_year')
        student.education_form = request.form.get('education_form')
        student.group = request.form.get('group')
        try:
            db.session.commit()
            flash("Пользователь успешно отредактирован", "success")
            return redirect(url_for("studentslist"))
        except:
            flash("Произошла ошибка", "danger")
            return render_template('editstudent/<int:id>.html', title='Редактирование студента')

    return render_template('editstudent.html', title='Редактирование студента', student=student)

@app.route('/createeducationplan', methods=['GET', 'POST'])
def createeducationplan():
    if request.method == 'POST':
        speciality = request.form.get('speciality')
        discipline = request.form.get('discipline')
        semester = request.form.get('semester')
        hours = request.form.get('hours')
        exam_or_test = request.form.get('exam_or_test')
        try:
            plan = PlanOfStudy(speciality=speciality, discipline=discipline, semester=semester, hours=hours, exam_or_test=exam_or_test)
            db.session.add(plan)
            db.session.commit()
            flash("Учебный план успешно добавлен", "success")
            return redirect(url_for("educationplanslist"))
        except:
            flash("Произошла ошибка", "danger")
            return render_template('createeducationplan.html', title='Добавление учебного плана')
    
    return render_template('createeducationplan.html', title='Добавление учебного плана')

@app.route('/editeducationplan/<int:id>', methods=['GET', 'POST'])
def editeducationplan(id):
    educationplan = PlanOfStudy.query.get_or_404(id)
    if request.method == 'POST':
        educationplan.speciality = request.form.get('speciality')
        educationplan.discipline = request.form.get('discipline')
        educationplan.semester = request.form.get('semester')
        educationplan.hours = request.form.get('hours')
        educationplan.exam_or_test = request.form.get('exam_or_test')
        try:
            db.session.commit()
            flash("Учебный план успешно отредактирован", "success")
            return redirect(url_for("educationplanslist"))
        except:
            flash("Произошла ошибка", "danger")
            return render_template('editeducationplan/<int:id>.html', title='Редактирование учебного плана')
    
    return render_template('editeducationplan.html', title='Редактирование учебного плана', educationplan=educationplan)

@app.route('/gradelist')
def gradelist():
    students_arr = Student.query.all()
    educationplans_arr = PlanOfStudy.query.all()
    grade_arr = Gradebook.query.all()
    
    return render_template('gradelist.html', title='Успеваемость', grades=grade_arr, students=students_arr, educationplans = educationplans_arr)

@app.route('/createmark', methods=['GET', 'POST'])
def createmark():
    if request.method == 'POST':
        student_id = request.form['select_student']
        discipline_id = request.form['select_discipline']
        year = request.form.get('year')
        mark = request.form.get('mark')
        try:
            grade = Gradebook(student_id=student_id, discipline_id=discipline_id, year=year, mark=mark)
            db.session.add(grade)
            db.session.commit()
            flash("Оценка успешно добавлена", "success")
            return redirect(url_for("gradelist"))
        except:
            flash("Произошла ошибка", "danger")
            return render_template('createmark.html', title='Добавление оценки')
    
    students_arr = Student.query.all()
    educationplans_arr = PlanOfStudy.query.all()
    return render_template('createmark.html', title='Добавление оценки', students=students_arr, educationplans = educationplans_arr)

@app.route('/editmark/<int:id>', methods=['GET', 'POST'])
def editmark(id):
    grade = Gradebook.query.get_or_404(id)
    if request.method == 'POST':
        grade.student_id = request.form['select_student']
        grade.discipline_id = request.form['select_discipline']
        grade.year = request.form.get('year')
        grade.mark = request.form.get('mark')
        try:
            db.session.commit()
            flash("Оценка успешно отредактирован", "success")
            return redirect(url_for("gradelist"))
        except:
            flash("Произошла ошибка", "danger")
            return render_template('editmark/<int:id>.html', title='Редактирование оценки')
    
    students_arr = Student.query.all()
    educationplans_arr = PlanOfStudy.query.all()

    return render_template('editmark.html', title='Редактирование оценки', grade=grade, students=students_arr, educationplans = educationplans_arr)

if __name__ == '__main__':
    app.run(host='0.0.0.0')