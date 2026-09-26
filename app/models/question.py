from app import db

class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False)
    test = db.relationship("Test", backref=db.backref("questions", cascade="all, delete-orphan"))

    type = db.Column(db.String(20), nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    points = db.Column(db.Integer, nullable=False, default=1)

    __table_args__ = (
        db.CheckConstraint(
            "type IN ('single', 'multi', 'truefalse', 'written')", name="ck_question_type"
        ),
    )

    def __repr__(self):
        return f'<Question {self.id} ({self.type}) for Test {self.test_id}>'
    

class Option(db.Model):
    __tablename__ = 'options'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    question = db.relationship("Question", backref=db.backref("options", cascade="all, delete-orphan"))
    text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False, default=False)

    display_order = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Option {self.id} for Question {self.question_id}>'

