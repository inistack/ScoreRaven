from app import db
from datetime import datetime, timezone

class Answer(db.Model):
    __tablename__ = 'answers'

    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('attempts.id'), nullable=False)
    attempt = db.relationship('Attempt', backref='answers')

    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    question = db.relationship('Question')

    selected_options_ids = db.Column(db.JSON, nullable=True)
    written_text = db.Column(db.Text, nullable=True)

    is_correct = db.Column(db.Boolean, nullable=True)
    points_awarded = db.Column(db.Integer, nullable=True)

    graded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    grader = db.relationship('User', backref='answers_graded')
    graded_at = db.Column(db.DateTime, nullable=True)

    __table_args__ = (db.UniqueConstraint('attempt_id', 'question_id', name='uq_attempt_answer'),)

    def __repr__(self):
        return f"<Answer attempt={self.attempt_id} question={self.question_id}>"
    

class GradeHistory(db.Model):
    __tablename__ = "grade_history"

    id = db.Column(db.Integer, primary_key=True)

    answer_id = db.Column(db.Integer, db.ForeignKey("answers.id"), nullable=False)
    answer = db.relationship("Answer", backref="grade_history")

    previous_is_correct = db.Column(db.Boolean, nullable=True)
    previous_points = db.Column(db.Integer, nullable=True)
    new_is_correct = db.Column(db.Boolean, nullable=True)
    new_points = db.Column(db.Integer, nullable=True)

    changed_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    grader = db.relationship("User", backref="grade_history_entries")

    changed_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))