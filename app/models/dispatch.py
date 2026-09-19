from app import db
from datetime import datetime, timezone

class Dispatch(db.Model):
    __tablename__ = 'dispatches'

    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False)
    test = db.relationship('Test', backref='dispatches')
    candidate_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    candidate = db.relationship('User', backref='dispatches_received')
    invited_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='invited')

    __table_args__ = (
        db.CheckConstraint(
            "status IN ('invited', 'started', 'expired_no_attempt', 'completed')",
            name="ck_dispatch_status",
        ),
    )

    def __repr__(self):
        return f'<Dispatch test={self.test_id} candidate={self.candidate_id} ({self.status})>'