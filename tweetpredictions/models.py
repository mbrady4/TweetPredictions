"""SQLAlchemy models for Twitoff."""
from flask_sqlalchemy import SQLAlchemy

DB = SQLAlchemy()


class User(DB.Model):
    """Twitter users that we pull and analyze Tweets for."""
    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(16))
    newest_tweet_id = DB.Column(DB.BigInteger)

    def __repr__(self):
        return '<User {}>'.format(self.name)


class Tweet(DB.Model):
    """Tweets."""
    id = DB.Column(DB.BigInteger, primary_key=True)
    text = DB.Column(DB.Unicode(500))
    embedding = DB.Column(DB.PickleType, nullable=False)
    user_id = DB.Column(DB.BigInteger, DB.ForeignKey('user.id'))
    user = DB.relationship('User', backref=DB.backref('text', lazy=True))

    def __repr__(self):
        return '<Tweet {}>'.format(self.text)


class Predictions(DB.Model):
    """Predictions Made"""
    id = DB.Column(DB.Integer, primary_key=True)
    text = DB.Column(DB.Unicode(500))
    user_1_name = DB.Column(DB.String(16))
    user_1_prob = DB.Column(DB.Integer)
    user_2_name = DB.Column(DB.String(16))
    user_2_prob = DB.Column(DB.Integer)