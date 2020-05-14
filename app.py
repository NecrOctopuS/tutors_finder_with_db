from flask import Flask, render_template, request
from data_tools import get_free_profile_hours, WEEKDAYS
from forms import RequestForm, BookingForm
from environs import Env
from flask_migrate import Migrate
from sqlalchemy import CheckConstraint
from flask_sqlalchemy import SQLAlchemy
import random
from sqlalchemy.orm.attributes import flag_modified

env = Env()
env.read_env()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = env.str("DATABASE_URL", "sqlite:///test.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = env.str('SECRET_KEY', 'my-super-secret-phrase-I-dont-tell-this-to-nobody')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

PROFILE_NUMBERS_PER_MAIN_PAGE = int(env.str('PROFILE_NUMBERS_PER_MAIN_PAGE', '6'))

teachers_goals_association = db.Table(
    "teachers_goals",
    db.Column("teacher_id", db.Integer, db.ForeignKey("teachers.id")),
    db.Column("goal_id", db.Integer, db.ForeignKey("goals.id")),
)


class Teacher(db.Model):
    __tablename__ = "teachers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    about = db.Column(db.Text)
    rating = db.Column(db.Float)
    picture = db.Column(db.String(200))
    price = db.Column(db.Integer)
    goals = db.relationship("Goal", secondary=teachers_goals_association, back_populates="teachers")
    free = db.Column(db.JSON)
    bookings = db.relationship("Booking", back_populates="teacher")


class Goal(db.Model):
    __tablename__ = "goals"
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(200))
    description = db.Column(db.String(200))
    teachers = db.relationship("Teacher", secondary=teachers_goals_association, back_populates="goals")
    icon = db.Column(db.String(30))


class Booking(db.Model):
    __tablename__ = "bookings"
    id = db.Column(db.Integer, primary_key=True)
    weekday = db.Column(db.String(3))
    time = db.Column(db.String(5), CheckConstraint("time LIKE '__:__'"))
    teacher = db.relationship("Teacher", back_populates="bookings")
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    name = db.Column(db.String(50))
    phone = db.Column(db.String(50))


class Request(db.Model):
    __tablename__ = "requests"
    id = db.Column(db.Integer, primary_key=True)
    goal = db.relationship("Goal")
    goal_id = db.Column(db.Integer, db.ForeignKey('goals.id'))
    time = db.Column(db.String(5))
    name = db.Column(db.String(50))
    phone = db.Column(db.String(50))


@app.route('/')
def render_main():
    profiles = random.sample(db.session.query(Teacher).all(), PROFILE_NUMBERS_PER_MAIN_PAGE)
    goals = db.session.query(Goal).all()
    return render_template('index.html', profiles=profiles, goals=goals)


@app.route('/goals/<goal_slug>/')
def render_goal(goal_slug):
    goal = db.session.query(Goal).filter(Goal.slug == goal_slug).one()
    profiles = db.session.query(Teacher).filter(Teacher.goals.any(id=goal.id)).order_by(Teacher.rating.desc()).all()
    return render_template('goal.html', goal=goal, profiles=profiles)


@app.route('/profiles/<int:profile_id>/')
def render_profile(profile_id):
    profile = db.session.query(Teacher).get_or_404(profile_id)
    goals = db.session.query(Goal).all()
    free_hours = get_free_profile_hours(profile.free)
    return render_template('profile.html', profile=profile, goals=goals, free_hours=free_hours, weekday=WEEKDAYS)


@app.route('/request/', methods=["GET", "POST"])
def render_request():
    form = RequestForm()
    goals = db.session.query(Goal).all()
    choices = [(str(goal.id), goal.description) for goal in goals]
    form.goal.choices = choices
    form.goal.data = choices[0][0]
    if request.method == "POST":
        if form.validate_on_submit():
            goal_id = form.goal.data
            goal = db.session.query(Goal).get_or_404(goal_id)
            time = form.time.data
            name = form.name.data
            phone = form.phone.data
            lesson_request = Request(goal=goal,
                                     goal_id=goal_id,
                                     time=time,
                                     name=name,
                                     phone=phone)
            db.session.add(lesson_request)
            db.session.commit()
            return render_template('request_done.html', goal=goal, time=time, name=name, phone=phone)
    return render_template('request.html', form=form)


@app.route('/booking/<int:profile_id>/<weekday>/<time>/', methods=["GET", "POST"])
def render_booking(profile_id, weekday, time):
    profile = db.session.query(Teacher).get_or_404(profile_id)
    form = BookingForm()
    form.weekday.default = weekday
    form.time.default = time
    form.teacher.default = profile_id
    if request.method == "POST":
        if form.validate_on_submit():
            name = form.name.data
            time = form.time.data
            weekday = form.weekday.data
            teacher_id = form.teacher.data
            phone = form.phone.data
            teacher = db.session.query(Teacher).get_or_404(profile_id)
            booking = Booking(weekday=weekday,
                              time=time,
                              teacher=teacher,
                              teacher_id=teacher_id,
                              name=name,
                              phone=phone)
            db.session.add(booking)
            schedule = teacher.free
            schedule[weekday][time] = False
            teacher.free = schedule
            flag_modified(teacher, "free")
            db.session.commit()
            return render_template('booking_done.html', weekday=WEEKDAYS[weekday], time=time, name=name, phone=phone)
    return render_template('booking.html', profile=profile, weekday=WEEKDAYS[weekday], time=time, form=form)


if __name__ == '__main__':
    app.run()
