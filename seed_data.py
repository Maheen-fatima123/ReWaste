"""
Seed script for ReWaste - populates the database with realistic sample data
for demo/showcase purposes.

Usage (run from the project root, with your virtualenv active):
    python seed_data.py

Safe to re-run: it clears existing Listings/Requests/Scores/Users first
so you don't end up with duplicates.
"""

import random
from datetime import datetime, timedelta

from app import app
from models.db import db
from models.models import User, Listing, Request, Score

# ── Sample businesses ─────────────────────────────────────────────────────
businesses = [
    {"business_name": "Zaitoon Textile Works", "email": "waste@zaitoontextile.pk", "sector": "textile", "city": "Karachi"},
    {"business_name": "Shaheen Cement Co", "email": "byproducts@shaheencement.pk", "sector": "manufacturing", "city": "Lahore"},
    {"business_name": "Al-Rehman Industries", "email": "scrap@alrehmanind.pk", "sector": "manufacturing", "city": "Lahore"},
    {"business_name": "Falak Textile Mills", "email": "sustainability@falaktextile.pk", "sector": "textile", "city": "Faisalabad"},
    {"business_name": "Sabza Valley Foods", "email": "ops@sabzavalley.pk", "sector": "food processing", "city": "Multan"},
    {"business_name": "Noorani Metal Works", "email": "sales@nooranimetal.pk", "sector": "metal", "city": "Karachi"},
    {"business_name": "Chenab Plastics Ltd", "email": "info@chenabplastics.pk", "sector": "plastic", "city": "Islamabad"},
    {"business_name": "Indus Paper Mills", "email": "contact@induspaper.pk", "sector": "paper", "city": "Rawalpindi"},
    {"business_name": "Barq Recyclers", "email": "hello@barqrecyclers.pk", "sector": "electronics", "city": "Karachi"},
    {"business_name": "Ujala Glass Co", "email": "info@ujalaglass.pk", "sector": "glass", "city": "Hyderabad"},
]

# ── Sample listings (linked to businesses by index) ───────────────────────
listings_data = [
    {"owner_idx": 0, "title": "Cotton Fabric Offcuts (Grade A)", "material_type": "Fabric", "quantity": 500, "unit": "kg", "price": 45000, "city": "Karachi",
     "description": "Clean cotton fabric offcuts from garment production, sorted by color. Ideal for quilting, rag production, or recycled yarn."},
    {"owner_idx": 1, "title": "Fly Ash (Bulk)", "material_type": "Other", "quantity": 20, "unit": "tonnes", "price": 60000, "city": "Lahore",
     "description": "Fly ash byproduct from cement kilns, suitable for brick manufacturing and concrete additives."},
    {"owner_idx": 3, "title": "Polyester Yarn Waste", "material_type": "Fabric", "quantity": 800, "unit": "kg", "price": 72000, "city": "Faisalabad",
     "description": "Mixed polyester yarn ends and cone waste, good for non-woven textile production."},
    {"owner_idx": 4, "title": "Fruit Peel & Pulp Waste", "material_type": "Other", "quantity": 2, "unit": "tonnes", "price": 15000, "city": "Multan",
     "description": "Daily fruit processing waste, suitable for composting or biogas generation."},
    {"owner_idx": 5, "title": "Steel Shavings & Scrap", "material_type": "Metal", "quantity": 1.2, "unit": "tonnes", "price": 180000, "city": "Karachi",
     "description": "Mixed mild steel shavings from CNC machining, clean and sorted."},
    {"owner_idx": 6, "title": "HDPE Plastic Regrind", "material_type": "Plastic", "quantity": 600, "unit": "kg", "price": 54000, "city": "Islamabad",
     "description": "Post-industrial HDPE regrind, consistent quality, suitable for injection molding."},
    {"owner_idx": 7, "title": "Cardboard & Kraft Paper Scrap", "material_type": "Paper", "quantity": 3, "unit": "tonnes", "price": 42000, "city": "Rawalpindi",
     "description": "Baled cardboard and kraft paper offcuts from packaging division."},
    {"owner_idx": 8, "title": "E-Waste Circuit Boards", "material_type": "Electronics", "quantity": 150, "unit": "kg", "price": 225000, "city": "Karachi",
     "description": "Sorted circuit boards from decommissioned electronics, good for metal recovery."},
    {"owner_idx": 9, "title": "Broken Glass Cullet", "material_type": "Glass", "quantity": 1, "unit": "tonnes", "price": 18000, "city": "Hyderabad",
     "description": "Sorted clear glass cullet, cleaned and ready for remelting."},
    {"owner_idx": 0, "title": "Denim Selvage Waste", "material_type": "Fabric", "quantity": 300, "unit": "kg", "price": 27000, "city": "Karachi",
     "description": "Denim selvage strips from cutting floor, popular for upcycled accessories."},
]

random.seed(42)

with app.app_context():
    # Clear existing data (order matters due to foreign keys)
    Request.query.delete()
    Score.query.delete()
    Listing.query.delete()
    User.query.delete()
    db.session.commit()

    # Create users
    users = []
    for b in businesses:
        u = User(business_name=b["business_name"], email=b["email"], sector=b["sector"], city=b["city"])
        u.set_password("Demo@1234")
        db.session.add(u)
        users.append(u)
    db.session.commit()

    # Create sustainability scores
    badge_levels = ["Bronze", "Silver", "Gold", "Platinum"]
    for u in users:
        score = Score(
            user_id=u.id,
            score_value=round(random.uniform(40, 98), 1),
            badge_level=random.choice(badge_levels),
        )
        db.session.add(score)
    db.session.commit()

    # Create listings
    listings = []
    for i, l in enumerate(listings_data):
        owner = users[l["owner_idx"]]
        listing = Listing(
            user_id=owner.id,
            title=l["title"],
            material_type=l["material_type"],
            quantity=l["quantity"],
            unit=l["unit"],
            price=l["price"],
            description=l["description"],
            city=l["city"],
            status="available",
            created_at=datetime.utcnow() - timedelta(days=random.randint(0, 20)),
        )
        db.session.add(listing)
        listings.append(listing)
    db.session.commit()

    # Create a few sample requests between businesses
    sample_requests = [
        {"listing_idx": 0, "buyer_idx": 3, "message": "Interested in the full 500kg lot. Can you share more photos of the color sorting?"},
        {"listing_idx": 4, "buyer_idx": 6, "message": "We'd like 500kg of the steel shavings for a trial batch. Is delivery to Islamabad possible?"},
        {"listing_idx": 6, "buyer_idx": 8, "message": "Can this cardboard batch be picked up this week?"},
    ]
    for r in sample_requests:
        listing = listings[r["listing_idx"]]
        buyer = users[r["buyer_idx"]]
        seller = users[listing.user_id - 1]
        req = Request(
            listing_id=listing.id,
            buyer_id=buyer.id,
            seller_id=seller.id,
            message=r["message"],
            status=random.choice(["pending", "accepted"]),
        )
        db.session.add(req)
    db.session.commit()

    print(f"Seeded {len(users)} businesses, {len(listings)} listings, {len(sample_requests)} requests.")
    print("Sample login -> email: waste@zaitoontextile.pk | password: Demo@1234")
