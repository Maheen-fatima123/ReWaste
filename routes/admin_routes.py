"""
admin_routes.py — haadiya's module
a basic panel only an admin account can open
"""
from flask import Blueprint, render_template, redirect, url_for, flash, session
from models.db import db
from models.models import User, Listing, Request

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('is_admin'):
            flash('admin access only.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/admin')
@admin_required
def admin_dashboard():
    # shows overall platform numbers on one simple page
    total_users = User.query.count()
    total_listings = Listing.query.count()
    total_completed = Request.query.filter_by(status='completed').count()

    return render_template(
        'admin_dashboard.html',
        total_users=total_users,
        total_listings=total_listings,
        total_completed=total_completed,
    )


@admin_bp.route('/admin/businesses')
@admin_required
def admin_businesses():
    # shows every registered business
    all_users = User.query.all()
    return render_template('admin_businesses.html', all_users=all_users)


@admin_bp.route('/admin/listings')
@admin_required
def admin_listings():
    # shows every listing so the admin can spot bad or fake ones
    all_listings = Listing.query.all()
    return render_template('admin_listings.html', all_listings=all_listings)


@admin_bp.route('/admin/listings/<int:listing_id>/remove', methods=['POST'])
@admin_required
def admin_remove_listing(listing_id):
    # deletes one listing from the database
    listing = Listing.query.get_or_404(listing_id)
    db.session.delete(listing)
    db.session.commit()
    flash('listing removed.', 'success')
    return redirect(url_for('admin.admin_listings'))
