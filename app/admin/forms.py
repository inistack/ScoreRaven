from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange

class TestForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=255)])
    subject_id = SelectField('Subject', coerce=int, validators=[DataRequired()])
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

