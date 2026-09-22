from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, SubmitField, IntegerField, TextAreaField, FormField, FieldList
from wtforms.validators import DataRequired, Length, NumberRange

class TestForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=255)])
    subject_name = StringField("Subject", validators=[DataRequired(), Length(max=120)])
    difficulty = SelectField('Difficulty', choices=[('basic', 'Basic'), ('advanced', 'Advanced')], validators=[DataRequired()])
    release_mode = SelectField('Release Mode', choices=[('immediate', 'Immediate'), ('manual', 'Manual'), ('scheduled', 'Scheduled')], validators=[DataRequired()])
    show_correct_answers = BooleanField("Show correct answers to candidates (Basic only)")
    time_limit_minutes = IntegerField(
        "Time Limit (minutes)",
        validators=[DataRequired(), NumberRange(min=1, message="Must be at least 1 minute.")],
    )

    validity_hours = IntegerField(
        "Validity Window (hours)",
        validators=[DataRequired(), NumberRange(min=1, message="Must be at least 1 hour.")],
    )
    submit = SubmitField('Save Test')


class OptionForm(FlaskForm):
    class Meta:
        csrf = False
    
    text = StringField('Option Text')
    is_correct = BooleanField('Correct Answer')



class QuestionForm(FlaskForm):
    type = SelectField(
        "Question Type",
        choices=[
            ("single", "Single Answer"),
            ("multi", "Multiple Answer"),
            ("truefalse", "True/False"),
            ("written", "Written Answer"),
        ],
        validators=[DataRequired()],
    )
    prompt = TextAreaField("Question Prompt", validators=[DataRequired()])
    points = IntegerField("Points", default=1, validators=[DataRequired(), NumberRange(min=1)])

    options = FieldList(FormField(OptionForm), min_entries=4, max_entries=8)

    submit = SubmitField("Save Question")