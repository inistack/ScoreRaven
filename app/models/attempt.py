from datetime import datetime, timezone
from app import db


class Attempt(db.Model):
    __tablename__ = 'attempts'

    id = db.Column(db.Integer, primary_key=True)
    dispatch_id = db.Column(db.Integer, db.ForeignKey("dispatches.id"), nullable=False, unique=True)
    dispatch = db.relationship('Dispatch', backref=db.backref('attempt', uselist=False))
    started_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    submitted_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='in_progress')
    score = db.Column(db.Integer, nullable=True)
    claimed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    grader = db.relationship("User", backref="attempts_claimed")
    claimed_at = db.Column(db.DateTime, nullable=True)
    
    __table_args__ = (
        db.CheckConstraint(
            "status IN ('in_progress', 'submitted', 'pending_grading', 'graded', 'completed')",
            name="ck_attempt_status",
        ),
    )
    

    def __repr__(self):
        return f'<Attempt {self.id} dispatch={self.dispatch_id_id} ({self.status})>'
    

class AttemptQuestion(db.Model):
    __tablename__ = 'attempt_questions'

    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('attempts.id'), nullable=False)
    attempt = db.relationship('Attempt', backref='attempt_questions')
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    question = db.relationship('Question')
    display_order = db.Column(db.Integer, nullable=False)
    __table_args__ = (db.UniqueConstraint('attempt_id', 'question_id', name='uq_attempt_question'),)

    def __repr__(self):
        return f"<AttemptQuestion attempt={self.attempt_id} question={self.question_id} order={self.display_order}>"
    
