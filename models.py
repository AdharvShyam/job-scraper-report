from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    searches = db.relationship('SearchHistory', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'


class SearchHistory(db.Model):
    __tablename__ = 'search_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    keyword = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    results_count = db.Column(db.Integer, default=0)
    searched_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Search {self.keyword} in {self.location}>'