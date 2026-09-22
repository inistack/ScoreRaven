from datetime import datetime, timezone
from app import db

class Test(db.Model):
    __tablename__ = 'tests'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    subject = db.relationship('Subject', backref="tests")

    difficulty = db.Column(db.String(20), nullable=False)
    time_limit_seconds = db.Column(db.Integer, nullable=False)
    validity_hours = db.Column(db.Integer, nullable=False)
    release_mode = db.Column(db.String(20), nullable=False, default="manual")

    show_correct_answers = db.Column(db.Boolean, nullable=False, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    creator = db.relationship('User', backref="tests_created")

    published_at = db.Column(db.DateTime, nullable=True)
    is_locked = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.CheckConstraint("difficulty IN ('basic', 'advanced')", name="ck_test_difficulty"),
        db.CheckConstraint(
            "release_mode IN ('immediate', 'manual', 'scheduled')", name="ck_test_release_mode"
        ),
    )

    def __repr__(self):
        return f'<Test {self.title} ({self.difficulty})>'