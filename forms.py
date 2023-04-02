from wtforms import StringField, IntegerField, SubmitField, BooleanField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired


class NewTestForm(FlaskForm):
    name = StringField('Testo pavadinimas', [DataRequired()])
    num_questions = IntegerField('Klausimų skaičius', [DataRequired()])
    submit = SubmitField('Submit')


class NewQuestionForm(FlaskForm):
    question = StringField('Klausimas', [DataRequired()])
    num_answers = IntegerField('Atsakymų skaičius', [DataRequired()])


class Answers(FlaskForm):
    answer = StringField('Atsakymas', [DataRequired()])
    checkbox = BooleanField()