"""
auth_routes.py — haadiya's module
handles sign up, login, logout, and profile editing
"""
from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from models.db import db
from models.models import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    # this page lets a new business create an account
    if request.method == 'POST':
        business_name = request.form.get('business_name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        sector = request.form.get('sector', '').strip()
        city = request.form.get('city', '').strip()

        # basic checks before we touch the database
        if not business_name or not email or not password:
            flash('business name, email, and password are required.', 'error')
            return redirect(url_for('auth.signup'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('this email is already registered, try logging in.', 'error')
            return redirect(url_for('auth.signup'))

        new_user = User(
            business_name=business_name,
            email=email,
            sector=sector,
            city=city,
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash('account created, please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('signup.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # this page lets an existing business log in
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()

        if user is None or not user.check_password(password):
            flash('wrong email or password.', 'error')
            return redirect(url_for('auth.login'))

        # save who is logged in inside the session
        session['user_id'] = user.id
        session['business_name'] = user.business_name
        session['is_admin'] = user.is_admin

        flash('logged in successfully.', 'success')
        return redirect(url_for('listing.browse'))

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    # clears everything saved in the session, this logs the user out
    session.clear()
    flash('logged out.', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    # this page shows and lets a user edit their own profile
    if 'user_id' not in session:
        flash('please log in first.', 'warning')
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        user.business_name = request.form.get('business_name', user.business_name).strip()
        user.sector = request.form.get('sector', user.sector)
        user.city = request.form.get('city', user.city)

        db.session.commit()
        session['business_name'] = user.business_name

        flash('profile updated.', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('profile.html', user=user)
