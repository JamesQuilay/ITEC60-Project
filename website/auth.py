from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash
from . import db  
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and not user.is_admin and user.check_password(password):
            login_user(user)
            flash('Login successful!', category='success')
            return redirect(url_for('views.home'))
        elif user and user.is_admin:
            flash('Login failed. Please check your email and password.', category='error')
        else:
            flash('Login failed. Please check your email and password.', category='error')

    return render_template('login.html', user=current_user)

@auth.route('/adminLogin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')  # Adjust the property name here
        password = request.form.get('password')

        admin_user = User.query.filter_by(email=email, is_admin=True).first()

        if admin_user and admin_user.check_password(password):
            login_user(admin_user)
            flash('Admin login successful!', category='success')
            return redirect(url_for('views.admin_panel'))
        else:
            flash('Admin login failed. Please check your email and password.', category='error')

    return render_template('admin_login.html', user=current_user)

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(
                password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    flash('Logged out.', category='success')
    logout_user()
    return redirect(url_for('auth.login'))

