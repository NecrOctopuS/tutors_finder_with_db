from flask import Flask, render_template
from data_tools import get_profile_from_json_by_id, get_profile_goals, get_free_profile_hours, \
    WEEKDAYS, write_lesson_to_json, get_goals_for_request_form, read_json, write_request_to_json, \
    ICONS
from forms import RequestForm, BookingForm
from environs import Env
from flask_migrate import Migrate
from sqlalchemy import CheckConstraint
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
env = Env()
env.read_env()

app.secret_key = env.str('SECRET_KEY', 'my-super-secret-phrase-I-dont-tell-this-to-nobody')

GOALS_JSON_PATH = env.str('GOALS_JSON_PATH', 'goals.json')
TEACHERS_JSON_PATH = env.str('TEACHERS_JSON_PATH', 'teachers.json')
REQUESTS_JSON_PATH = env.str('REQUESTS_JSON_PATH', 'request.json')
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
    return render_template('index.html', profiles=profiles, goals=goals, icons=ICONS)


@app.route('/goals/<goal_slug>/')
def render_goal(goal_slug):
    goal = db.session.query(Goal).filter(Goal.slug == goal_slug).one()
    profiles = db.session.query(Teacher).filter(Teacher.goals.any(id=goal.id)).order_by(Teacher.rating.desc()).all()
    icon = ICONS[goal.slug]
    return render_template('goal.html', goal=goal, profiles=profiles, icon=icon)


@app.route('/profiles/<int:profile_id>/')
def render_profile(profile_id):
    profile = db.session.query(Teacher).get_or_404(profile_id)
    goals = db.session.query(Goal).all()
    free_hours = get_free_profile_hours(profile.free)
    return render_template('profile.html', profile=profile, goals=goals, free_hours=free_hours, weekday=WEEKDAYS)


@app.route('/request/')
def render_request():
    form = RequestForm()
    goals = get_goals_for_request_form(GOALS_JSON_PATH)
    form.goal.choices = goals
    form.goal.default = goals[0][0]
    form.process()
    return render_template('request.html', form=form)


@app.route('/request_done/', methods=["POST"])
def render_request_done():
    goals = get_goals_for_request_form(GOALS_JSON_PATH)
    form = RequestForm()
    form.goal.choices = goals
    if form.validate():
        goals = read_json(GOALS_JSON_PATH)
        goal = form.goal.data
        time = form.time.data
        name = form.name.data
        phone = form.phone.data
        write_request_to_json(goal, time, name, phone, REQUESTS_JSON_PATH)
        return render_template('request_done.html', goal=goals[goal], time=time, name=name, phone=phone)
    return 'Данные не получены '


@app.route('/booking/<int:profile_id>/<weekday>/<time>/')
def render_booking(profile_id, weekday, time):
    profile = get_profile_from_json_by_id(profile_id, TEACHERS_JSON_PATH)
    form = BookingForm()
    form.weekday.default = weekday
    form.time.default = time
    form.teacher.default = profile_id
    return render_template('booking.html', profile=profile, weekday=WEEKDAYS[weekday], form=form)


@app.route('/booking_done/', methods=["POST"])
def render_booking_done():
    form = BookingForm()
    if form.validate():
        name = form.name.data
        time = form.time.data
        weekday = form.weekday.data
        teacher_id = form.teacher.data
        phone = form.phone.data
        write_lesson_to_json(teacher_id, weekday, time, TEACHERS_JSON_PATH)
        return render_template('booking_done.html', name=name, time=time, weekday=WEEKDAYS[weekday], phone=phone)
    return 'Данные не получены '


if __name__ == '__main__':
    app.run()
