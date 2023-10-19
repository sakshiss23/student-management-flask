from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, logout_user, LoginManager, login_required

from werkzeug.security import generate_password_hash, check_password_hash

from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('APP_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/studentdb'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Models


class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))


class Department(db.Model):
    cid = db.Column(db.Integer, primary_key=True)
    branch = db.Column(db.String(100))


class Attendence(db.Model):
    aid = db.Column(db.Integer, primary_key=True)
    rollno = db.Column(db.String(100))
    attendance = db.Column(db.Integer())


class Marks(db.Model):
    aid = db.Column(db.Integer, primary_key=True)
    rollno = db.Column(db.String(100))
    marks = db.Column(db.Integer())


class Trig(db.Model):
    tid = db.Column(db.Integer, primary_key=True)
    rollno = db.Column(db.String(100))
    action = db.Column(db.String(100))
    timestamp = db.Column(db.String(100))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(1000))


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rollno = db.Column(db.String(50))
    sname = db.Column(db.String(50))
    sem = db.Column(db.Integer)
    gender = db.Column(db.String(50))
    branch = db.Column(db.String(50))
    email = db.Column(db.String(50))
    number = db.Column(db.String(12))
    address = db.Column(db.String(100))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    students = Student.query.all()
    return render_template('about.html', query=students)


@app.route('/studentdetails')
def studentdetails():
    students = Student.query.all()
    return render_template('studentdetails.html', query=students)


@app.route('/triggers')
def triggers():
    triggers = Trig.query.all()
    return render_template('triggers.html', query=triggers)


@app.route('/department', methods=['POST', 'GET'])
def department():
    if request.method == "POST":
        dept = request.form.get('dept')
        existing_department = Department.query.filter_by(branch=dept).first()
        if existing_department:
            flash("Department Already Exists", "warning")
            return redirect('/department')

        new_department = Department(branch=dept)
        db.session.add(new_department)
        db.session.commit()
        flash("Department Added", "success")

    return render_template('department.html')


@app.route('/addattendance', methods=['POST', 'GET'])
def addattendance():
    students = Student.query.all()
    if request.method == "POST":
        rollno = request.form.get('rollno')
        attend = request.form.get('attend')
        attendance = Attendence(rollno=rollno, attendance=attend)
        db.session.add(attendance)
        db.session.commit()
        flash("Attendance added", "warning")

    return render_template('attendance.html', query=students)


@app.route('/addmarks', methods=['POST', 'GET'])
def marks():
    students = Student.query.all()
    if request.method == "POST":
        rollno = request.form.get('rollno')
        marks_value = request.form.get('marks')
        mark = Marks(rollno=rollno, marks=marks_value)
        db.session.add(mark)
        db.session.commit()
        flash("Marks added", "warning")

    return render_template('marks.html', query=students)


@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == "POST":
        rollno = request.form.get('roll')
        bio = Student.query.filter_by(rollno=rollno).first()
        attend = Attendence.query.filter_by(rollno=rollno).first()
        mark = Marks.query.filter_by(rollno=rollno).first()
        return render_template('search.html', bio=bio, attend=attend, marks=mark)

    return render_template('search.html')


@app.route("/delete/<string:id>", methods=['POST', 'GET'])
@login_required
def delete(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash("Slot Deleted Successful", "danger")
    return redirect('/studentdetails')


@app.route("/edit/<string:id>", methods=['POST', 'GET'])
@login_required
def edit(id):
    departments = Department.query.all()
    student = Student.query.get_or_404(id)

    if request.method == "POST":
        student.rollno = request.form.get('rollno')
        student.sname = request.form.get('sname')
        student.sem = request.form.get('sem')
        student.gender = request.form.get('gender')
        student.branch = request.form.get('branch')
        student.email = request.form.get('email')
        student.number = request.form.get('num')
        student.address = request.form.get('address')

        db.session.commit()
        flash("Slot is Updated", "success")
        return redirect('/studentdetails')

    return render_template('edit.html', posts=student, dept=departments)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email Already Exist", "warning")
            return render_template('/signup.html')

        enc_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=enc_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Signup Successful. Please Login.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Login Success", "primary")
            return redirect(url_for('index'))

        flash("Invalid credentials", "danger")

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout Successful", "warning")
    return redirect(url_for('login'))


@app.route('/addstudent', methods=['POST', 'GET'])
@login_required
def addstudent():
    dept = db.engine.execute("SELECT * FROM `department`")
    if request.method == "POST":
        rollno = request.form.get('rollno')
        sname = request.form.get('sname')
        sem = request.form.get('sem')
        gender = request.form.get('gender')
        branch = request.form.get('branch')
        email = request.form.get('email')
        num = request.form.get('num')
        address = request.form.get('address')
        db.engine.execute(
            f"INSERT INTO `student` (`rollno`,`sname`,`sem`,`gender`,`branch`,`email`,`number`,`address`) VALUES ('{rollno}','{sname}','{sem}','{gender}','{branch}','{email}','{num}','{address}')")

        flash("Student Added", "info")

    return render_template('student.html', dept=dept)


@app.route('/test')
def test():
    try:
        Test.query.all()
        return 'My database is Connected'
    except:
        return 'My db is not Connected'


if __name__ == '__main__':
    app.run(debug=True)
