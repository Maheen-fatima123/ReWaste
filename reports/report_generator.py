"""
report_generator.py — hasaan's module (Module 5: Monthly Reports)

Builds a one-page PDF summary of a business's activity for a given month:
how many exchanges they completed, how much they diverted, and a simple
breakdown by material type. Uses pandas to organise the numbers and
matplotlib to draw and save the actual PDF page.

Note on dates: the `requests` table only stores `created_at` (when a buy
request was first sent), there's no separate "completed on" timestamp in
the schema. So "this month's activity" below means: requests that were
created in that month and are currently marked completed. Good enough for
a first version — worth adding a `completed_at` column later if the team
wants exact completion dates.
"""
import os
from datetime import datetime
from calendar import month_name

import matplotlib
matplotlib.use('Agg')  # no display on the server, just save straight to file
import matplotlib.pyplot as plt
import pandas as pd

from models.models import Request, Listing, User

REPORTS_FOLDER_NAME = os.path.join('static', 'reports')


def _month_bounds(year, month):
    """Returns (start, end) datetimes covering exactly one calendar month."""
    start = datetime(year, month, 1)
    if month == 12:
        end = datetime(year + 1, 1, 1)
    else:
        end = datetime(year, month + 1, 1)
    return start, end


def _collect_month_data(user_id, year, month):
    """Pulls this business's completed exchanges for the given month into a DataFrame."""
    start, end = _month_bounds(year, month)

    completed = (
        Request.query
        .filter(Request.seller_id == user_id)
        .filter(Request.status == 'completed')
        .filter(Request.created_at >= start, Request.created_at < end)
        .all()
    )

    rows = []
    for r in completed:
        listing = Listing.query.get(r.listing_id)
        if listing is None:
            continue
        rows.append({
            'date': r.created_at,
            'material_type': listing.material_type,
            'quantity': listing.quantity,
            'unit': listing.unit,
            'price': listing.price,
        })

    return pd.DataFrame(rows, columns=['date', 'material_type', 'quantity', 'unit', 'price'])


def generate_monthly_report(user_id, year=None, month=None, reports_folder=None):
    """
    Builds the PDF report for one business for one month and saves it to disk.
    Calling this again for the same month just overwrites the same file, so
    it's safe to regenerate on demand.

    Returns the full filepath of the saved PDF.
    """
    now = datetime.utcnow()
    year = year or now.year
    month = month or now.month

    user = User.query.get(user_id)
    df = _collect_month_data(user_id, year, month)

    folder = reports_folder or REPORTS_FOLDER_NAME
    os.makedirs(folder, exist_ok=True)
    filename = f"report_{user_id}_{year}_{month:02d}.pdf"
    filepath = os.path.join(folder, filename)

    total_exchanges = len(df)
    total_quantity = round(df['quantity'].sum(), 2) if not df.empty else 0
    top_material = df['material_type'].value_counts().idxmax() if not df.empty else 'N/A'

    fig = plt.figure(figsize=(8.27, 11.69))  # A4 portrait
    fig.suptitle("ReWaste Monthly Report", fontsize=18, fontweight='bold', y=0.97)

    fig.text(0.1, 0.92, f"{user.business_name if user else 'Business'}", fontsize=13, fontweight='bold')
    fig.text(0.1, 0.895, f"{month_name[month]} {year}", fontsize=11, color='#555555')

    summary_lines = [
        f"Completed exchanges this month:  {total_exchanges}",
        f"Total quantity diverted:  {total_quantity}  (summed across each listing's own unit)",
        f"Most active material category:  {top_material}",
    ]
    fig.text(0.1, 0.84, "\n".join(summary_lines), fontsize=11, va='top', linespacing=1.8)

    ax = fig.add_axes([0.12, 0.35, 0.76, 0.38])
    if not df.empty:
        by_material = df.groupby('material_type')['quantity'].sum().sort_values(ascending=False)
        ax.bar(by_material.index, by_material.values, color='#2d6a4f')
        ax.set_ylabel('Quantity diverted')
        ax.set_title('Quantity diverted by material type', fontsize=11)
        plt.setp(ax.get_xticklabels(), rotation=30, ha='right')
    else:
        ax.axis('off')
        ax.text(0.5, 0.5, "No completed exchanges this month.",
                ha='center', va='center', fontsize=11, color='#888888')

    fig.text(0.1, 0.06, f"Generated on {now.strftime('%d %b %Y')} by ReWaste", fontsize=8, color='#999999')

    fig.savefig(filepath, format='pdf')
    plt.close(fig)

    return filepath
