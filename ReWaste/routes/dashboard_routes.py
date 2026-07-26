"""
dashboard_routes.py — hasaan's module
Module 4: Sustainability Score and Dashboard
Module 5: Monthly Reports (generation is triggered from the dashboard page)
"""
from datetime import datetime
from calendar import month_abbr
from functools import wraps

from flask import Blueprint, render_template, redirect, url_for, session, flash, send_file, current_app

from models.db import db
from models.models import User, Listing, Request, Score
from reports.report_generator import generate_monthly_report

dashboard_bp = Blueprint('dashboard', __name__)

# ── Score formula settings ──────────────────────────────────────────────────
# score = (listings posted * 5) + (completed exchanges * 20) + (kg-equivalent diverted * 0.5)
POINTS_PER_LISTING = 5
POINTS_PER_COMPLETED_EXCHANGE = 20
POINTS_PER_KG_DIVERTED = 0.5

# badge thresholds — lowest first
BADGE_TIERS = [
    ('Bronze',   0),
    ('Silver',   75),
    ('Gold',     200),
    ('Platinum', 400),
]

# rough unit-to-kg conversion so a 5-tonne listing doesn't score the same as a
# 5 kg listing. Units we can't meaningfully convert (pieces, litres, meters)
# are just counted at face value — an approximation, not an exact weight.
UNIT_TO_KG = {'kg': 1, 'tonnes': 1000}


def login_required(f):
    """Same simple pattern used in listing_routes.py and request_routes.py."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('please log in first.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def _diverted_amount(quantity, unit):
    return quantity * UNIT_TO_KG.get(unit, 1)


def get_badge(score_value):
    """Returns (current_badge, next_badge_or_None, points_needed_for_next)."""
    current = BADGE_TIERS[0][0]
    for name, threshold in BADGE_TIERS:
        if score_value >= threshold:
            current = name

    names = [t[0] for t in BADGE_TIERS]
    idx = names.index(current)
    if idx + 1 < len(BADGE_TIERS):
        next_name, next_threshold = BADGE_TIERS[idx + 1]
        return current, next_name, round(next_threshold - score_value, 1)
    return current, None, 0


def calculate_score(user_id):
    """Computes the sustainability score for one business and saves it to the scores table."""
    listings_count = Listing.query.filter_by(user_id=user_id).count()
    completed = Request.query.filter_by(seller_id=user_id, status='completed').all()
    completed_count = len(completed)

    total_diverted = 0.0
    for r in completed:
        listing = Listing.query.get(r.listing_id)
        if listing:
            total_diverted += _diverted_amount(listing.quantity, listing.unit)

    score_value = round(
        listings_count * POINTS_PER_LISTING +
        completed_count * POINTS_PER_COMPLETED_EXCHANGE +
        total_diverted * POINTS_PER_KG_DIVERTED,
        1
    )
    badge, next_badge, points_to_next = get_badge(score_value)

    # update or create this business's row in the scores table
    score_row = Score.query.filter_by(user_id=user_id).first()
    if score_row is None:
        score_row = Score(user_id=user_id)
        db.session.add(score_row)
    score_row.score_value = score_value
    score_row.badge_level = badge
    score_row.last_updated = datetime.utcnow()
    db.session.commit()

    return {
        'score_value': score_value,
        'badge': badge,
        'next_badge': next_badge,
        'points_to_next': points_to_next,
        'listings_count': listings_count,
        'completed_count': completed_count,
        'total_diverted': round(total_diverted, 1),
    }


def _last_n_months(n=6):
    """List of (year, month) tuples for the last n months, oldest first."""
    now = datetime.utcnow()
    months = []
    y, m = now.year, now.month
    for _ in range(n):
        months.append((y, m))
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    return list(reversed(months))


def _monthly_activity(user_id):
    """Builds the data behind the two progress charts on the dashboard."""
    months = _last_n_months(6)
    completed = Request.query.filter_by(seller_id=user_id, status='completed').all()

    labels = [f"{month_abbr[m]} {y}" for (y, m) in months]
    exchange_counts = [0] * len(months)
    diverted_totals = [0.0] * len(months)

    for r in completed:
        for i, (y, m) in enumerate(months):
            if r.created_at.year == y and r.created_at.month == m:
                exchange_counts[i] += 1
                listing = Listing.query.get(r.listing_id)
                if listing:
                    diverted_totals[i] += _diverted_amount(listing.quantity, listing.unit)
                break

    diverted_totals = [round(x, 1) for x in diverted_totals]
    return labels, exchange_counts, diverted_totals


def _platform_average():
    """Average score across every business that has one — the industry benchmark."""
    all_scores = [s.score_value for s in Score.query.all()]
    if not all_scores:
        return 0
    return round(sum(all_scores) / len(all_scores), 1)


@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    stats = calculate_score(user_id)
    labels, exchange_counts, diverted_totals = _monthly_activity(user_id)
    platform_avg = _platform_average()

    # precompute benchmark bar widths here so the template stays simple
    scale = max(stats['score_value'], platform_avg, 1)
    you_pct = round(min(stats['score_value'] / scale * 100, 100), 1)
    avg_pct = round(min(platform_avg / scale * 100, 100), 1)

    return render_template(
        'dashboard.html',
        stats=stats,
        badge_tiers=BADGE_TIERS,
        chart_labels=labels,
        chart_exchanges=exchange_counts,
        chart_diverted=diverted_totals,
        platform_avg=platform_avg,
        you_pct=you_pct,
        avg_pct=avg_pct,
    )


@dashboard_bp.route('/dashboard/report')
@login_required
def download_report():
    """Generates (or regenerates) this month's PDF report and sends it for download."""
    user_id = session['user_id']
    reports_folder = current_app.config.get('REPORTS_FOLDER')
    filepath = generate_monthly_report(user_id, reports_folder=reports_folder)
    return send_file(filepath, as_attachment=True)
