from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    transactions = db.relationship('Transaction', backref='user', lazy=True)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10))  # receita ou despesa
    description = db.Column(db.String(100))
    amount = db.Column(db.Float)
    date = db.Column(db.String(10))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
