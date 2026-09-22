from app import db
from app.models import Subject

def get_or_create_subject(name):
    name = name.strip()
    subject = Subject.query.filter(db.func.lower(Subject.name) == name.lower()).first()
    if subject:
        return subject
    
    subject = Subject(name=name)
    db.session.add(subject)
    db.session.flush()
    return subject


