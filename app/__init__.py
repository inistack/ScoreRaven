from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    

    login_manager.login_view = 'auth.login'
    
    with app.app_context():
        from app import models
    
    from app.celery_app import init_celery
    init_celery(app)
    from app import tasks
    from app.auth.routes import auth_bp
    from app.dashboard.routes import dashboard_bp
    from app.admin.routes import admin_bp
    from app.candidate.routes import candidate_bp
    from app.grading.routes import grading_bp
    from app.main.routes import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(candidate_bp)
    app.register_blueprint(grading_bp)
    app.register_blueprint(main_bp)

    @app.context_processor
    def inject_now_year():
        from datetime import datetime, timezone
        return {"now_year": datetime.now(timezone.utc).year}

    from app.cli import register_cli
    register_cli(app)


    return app


