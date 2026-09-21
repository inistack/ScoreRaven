from flask import Blueprint, render_template, redirect, url_for, flash
from app import db
from flask_login import login_user, logout_user, login_required
from app.models import User
from app.auth.forms import RegistrationForm, SetPasswordForm, LoginForm
from app.auth.token import generate_token, verify_token
from app.emails.auth_emails import send_verification_email

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("An account with that email already exists.", "error")
            return redirect(url_for('auth.register'))
        user = User(name=form.name.data, email=form.email.data, role='candidate')
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        token = generate_token(user.email, salt='email-verify')
        send_verification_email(user.email, token)

        flash("Account created. Check your email to verify before you can be invited to tests.", "info")
        return redirect(url_for('auth.login'))
    
    return render_template("auth/register.html", form=form)
        

@auth_bp.route('/verify/<token>')
def verify_email(token):
    email = verify_token(token, salt='email-verify', max_age_seconds=86400)
    if email is None:
        flash("This verification link is invalid or has expired.", "error")
        return redirect(url_for('auth.login'))
    
    user = User.query.filter_by(email=email).first()

    if user is None:
        flash("This verification link is invalid or has expired.", "error")
        return redirect(url_for('auth.login'))
    
    if user.is_verified:
        flash("Your email is already verified. You can log in.", "info")
        return redirect(url_for('auth.login'))
    
    user.is_verified = True
    db.session.commit()

    flash("Email verified. You're now eligible to be invited to tests.", "success")
    return redirect(url_for('auth.login'))


@auth_bp.route('/set-password/<token>', methods=['GET', 'POST'])
def set_password(token):
    email = verify_token(token, salt="set-password", max_age_seconds=86400)

    if email is None:
        flash("This link is invalid or has expired.", "error")
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(email=email).first()

    if user is None:
        flash("This link is invalid or has expired.", "error")
        return redirect(url_for("auth.login"))

    if user.has_password_set:
        flash("You've already set a password. Log in instead.", "info")
        return redirect(url_for("auth.login"))
    
    form = SetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Password set. You can now log in.", "success")
        return redirect(url_for("auth.login"))
    
    return render_template("auth/set_password.html", form=form, token=token)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter_by(email=form.email.data).first()
        if user is None or not user.has_password_set:
             flash("Invalid email or password.", "error")
             return redirect(url_for('auth.login'))
        
        if not user.check_password(form.password.data):
             flash("Invalid email or password.", "error")
             return redirect(url_for('auth.login'))
        
        login_user(user)
        return redirect(url_for('dashboard.index'))
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('auth.login'))