"""
This module defines the database models for a Flask application. It includes the following models:

- Analysis: Represents the analysis with attributes id, quote, name, and client.
- Layer: Represents reinsurance layers with attributes id, analysis_id, deductible, and limit.

These models are designed to work with SQLAlchemy and are used to interact with the underlying database. Each model corresponds to a database table with its respective fields.
"""

# Cascading delete : https://www.geeksforgeeks.org/sqlalchemy-cascading-deletes/
from flaskapp.extensions import db
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Float, String
from sqlalchemy.orm import validates, relationship


class Analysis(db.Model):
    __tablename__ = 'analysis'
    id = Column(Integer, primary_key=True)
    quote = Column(Integer)
    name = Column(String(50))
    client = Column(String(50))

    def __repr__(self):
        return f'<Analysis {self.name}>'


class Layer(db.Model):
    __tablename__ = 'layer'
    id = Column(Integer, primary_key=True)
    analysis_id = Column(Integer, ForeignKey('analysis.id', ondelete='CASCADE'))
    deductible = Column(Integer)
    limit = Column(Integer)

    def __repr__(self):
        return f'{self.limit} XS {self.deductible}'


class LossFile(db.Model):
    __tablename__ = 'lossfile'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    losses = relationship('Loss', backref='lossfile', cascade='all, delete')

    def __repr__(self):
        return f'<LossFile {self.name}>'


class Loss(db.Model):
    __tablename__ = 'loss'
    id = Column(Integer, primary_key=True)
    lossfile_id = Column(Integer, ForeignKey('lossfile.id'))
    name = Column(String(50))
    year = Column(Integer)
    premium = Column(Integer)
    loss = Column(Integer)
    loss_ratio = Column(Float)

    def __repr__(self):
        return f'<Loss {self.name}'


class Restaurant(db.Model):
    __tablename__ = 'restaurant'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    street_address = Column(String(50))
    description = Column(String(250))

    def __str__(self):
        return self.name


class Review(db.Model):
    __tablename__ = 'review'
    id = Column(Integer, primary_key=True)
    restaurant = Column(Integer, ForeignKey('restaurant.id', ondelete="CASCADE"))
    user_name = Column(String(30))
    rating = Column(Integer)
    review_text = Column(String(500))
    review_date = Column(DateTime)

    @validates('rating')
    def validate_rating(self, key, value):
        assert value is None or (1 <= value <= 5)
        return value

    def __str__(self):
        return f"{self.user_name}: {self.review_date:%x}"
