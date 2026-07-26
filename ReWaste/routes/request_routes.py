"""
request_routes.py — haadiya's module
handles the request to buy and contact system
uses the Request model that already exists in models/models.py
"""
from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from models.db import db
from models.models import Request, Listing

request_bp = Blueprint('request', __name__)


def login_required(f):
    # same simple pattern maheen used in listing_routes.py
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('please log in first.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@request_bp.route('/listings/<int:listing_id>/request', methods=['POST'])
@login_required
def send_request(listing_id):
    # this runs when a buyer clicks the request to buy button on a listing
    listing = Listing.query.get_or_404(listing_id)
    buyer_id = session['user_id']

    # a business cannot send a request on its own listing
    if listing.user_id == buyer_id:
        flash('you cannot request your own listing.', 'error')
        return redirect(url_for('listing.view_listing', listing_id=listing_id))

    message_text = request.form.get('message', '').strip()

    new_request = Request(
        listing_id=listing.id,
        buyer_id=buyer_id,
        seller_id=listing.user_id,
        message=message_text,
        status='pending',
    )

    db.session.add(new_request)
    db.session.commit()

    flash('request sent to the seller.', 'success')
    return redirect(url_for('listing.view_listing', listing_id=listing_id))


@request_bp.route('/requests/sent')
@login_required
def sent_requests():
    # shows every request this business has sent to other sellers
    buyer_id = session['user_id']
    requests_list = (
        Request.query
        .filter_by(buyer_id=buyer_id)
        .order_by(Request.created_at.desc())
        .all()
    )
    return render_template('my_requests.html', requests_list=requests_list, view_type='sent')


@request_bp.route('/requests/received')
@login_required
def received_requests():
    # shows every request other businesses have sent to this seller
    seller_id = session['user_id']
    requests_list = (
        Request.query
        .filter_by(seller_id=seller_id)
        .order_by(Request.created_at.desc())
        .all()
    )
    return render_template('my_requests.html', requests_list=requests_list, view_type='received')


@request_bp.route('/requests/<int:request_id>/accept', methods=['POST'])
@login_required
def accept_request(request_id):
    # only the seller who owns the listing can accept a request
    exchange_request = Request.query.get_or_404(request_id)

    if exchange_request.seller_id != session['user_id']:
        flash('you cannot change this request.', 'error')
        return redirect(url_for('request.received_requests'))

    exchange_request.status = 'accepted'
    db.session.commit()

    flash('request accepted.', 'success')
    return redirect(url_for('request.received_requests'))


@request_bp.route('/requests/<int:request_id>/complete', methods=['POST'])
@login_required
def complete_request(request_id):
    # marks the exchange as completed
    # this status is what hasaan's sustainability score module will count
    exchange_request = Request.query.get_or_404(request_id)

    if exchange_request.seller_id != session['user_id']:
        flash('you cannot change this request.', 'error')
        return redirect(url_for('request.received_requests'))

    exchange_request.status = 'completed'
    db.session.commit()

    flash('exchange marked as completed.', 'success')
    return redirect(url_for('request.received_requests'))
