from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SubmitField, HiddenField
from wtforms.validators import InputRequired, Length

TIMES = [
    ("1-2", "1-2 часа в неделю"),
    ("3-5", "3-5 часов в неделю"),
    ("5-7", "5-7 часов в неделю"),
    ("7-10", "7-10 часов в неделю")
]


class RequestForm(FlaskForm):
    goal = RadioField('Какая цель занятий?', validators=[InputRequired()])
    time = RadioField('Сколько времени есть?', choices=TIMES, default=TIMES[0][0], validators=[InputRequired()])
    name = StringField('Вас зовут', [InputRequired(message="Введите что-нибудь")])
    phone = StringField('Ваш телефон', [InputRequired(message="Введите что-нибудь"),
                                        Length(min=7, message="Неправильный номер")])
    submit = SubmitField('Найдите мне преподавателя')


class BookingForm(FlaskForm):
    weekday = HiddenField('День недели', [InputRequired(message="Введите что-нибудь")])
    time = HiddenField('Время', [InputRequired(message="Введите что-нибудь")])
    teacher = HiddenField('Учитель', [InputRequired(message="Введите что-нибудь")])
    name = StringField('Вас зовут', [InputRequired(message="Введите что-нибудь")])
    phone = StringField('Ваш телефон', [InputRequired(message="Введите что-нибудь"),
                                        Length(min=7, message="Неправильный номер")])
    submit = SubmitField('Записаться на пробный урок')
