from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Association table for Boulder <-> Tag
boulder_tags = db.Table(
    'boulder_tags',
    db.Column('boulder_id', db.Integer, db.ForeignKey('boulder.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class Sector(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    blocks = db.relationship('Block', backref='sector', lazy=True)

class Block(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    image_path = db.Column(db.String(200))
    sector_id = db.Column(db.Integer, db.ForeignKey('sector.id'), nullable=False)
    boulders = db.relationship('Boulder', backref='block', lazy=True)

class Boulder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.String(10))
    description = db.Column(db.Text)
    image_path = db.Column(db.String(200))
    block_id = db.Column(db.Integer, db.ForeignKey('block.id'), nullable=False)
    tags = db.relationship('Tag', secondary=boulder_tags, lazy='subquery',
                          backref=db.backref('boulders', lazy=True))
    attempts = db.relationship('Attempt', backref='boulder', lazy=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    attempts = db.relationship('Attempt', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Attempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    boulder_id = db.Column(db.Integer, db.ForeignKey('boulder.id'), nullable=False)
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20))  # Tentativa, Cadena, Flash, or NULL
    rating = db.Column(db.Integer)  # 1-5 stars
    notes = db.Column(db.Text)

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
