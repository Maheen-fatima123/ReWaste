from models.db import db
from datetime import datetime


class User(db.Model):
    """A registered business on LoopBack."""
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    business_name = db.Column(db.String(120), nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    sector        = db.Column(db.String(80))          # e.g. manufacturing, retail
    city          = db.Column(db.String(80))
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    listings  = db.relationship('Listing',  backref='owner',  lazy=True)
    score     = db.relationship('Score',    backref='user',   uselist=False)


class Listing(db.Model):
    """A waste material posted for exchange."""
    __tablename__ = 'listings'

    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title         = db.Column(db.String(120), nullable=False)
    material_type = db.Column(db.String(80), nullable=False)   # plastic, metal, paper …
    quantity      = db.Column(db.Float, nullable=False)
    unit          = db.Column(db.String(20), nullable=False)   # kg, tonnes, pieces
    price         = db.Column(db.Float, nullable=False)
    description   = db.Column(db.Text)
    photo         = db.Column(db.String(200))                  # filename in /static/uploads
    city          = db.Column(db.String(80))
    status        = db.Column(db.String(20), default='available')  # available | sold
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    requests = db.relationship('Request', backref='listing', lazy=True)


class Request(db.Model):
    """A buyer's request on a listing."""
    __tablename__ = 'requests'

    id         = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listings.id'),  nullable=False)
    buyer_id   = db.Column(db.Integer, db.ForeignKey('users.id'),     nullable=False)
    seller_id  = db.Column(db.Integer, db.ForeignKey('users.id'),     nullable=False)
    message    = db.Column(db.Text)
    status     = db.Column(db.String(20), default='pending')   # pending | accepted | completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    buyer  = db.relationship('User', foreign_keys=[buyer_id])
    seller = db.relationship('User', foreign_keys=[seller_id])


class Score(db.Model):
    """Sustainability score for each business."""
    __tablename__ = 'scores'

    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    score_value  = db.Column(db.Float, default=0.0)
    badge_level  = db.Column(db.String(20), default='Bronze')  # Bronze Silver Gold Platinum
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
