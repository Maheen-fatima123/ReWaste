"""
auth_routes.py  — Haadiya's module.
Stub included so the app imports cleanly during development.
Haadiya will replace this with the full implementation.
"""
from flask import Blueprint, render_template, redirect, url_for, session

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login')
def login():
    return render_template('login.html')


@auth_bp.route('/signup')
def signup():
    return render_template('signup.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
