from flaskapp.extensions import db
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import validates


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
    analysis_id = Column(Integer, ForeignKey('analysis.id'))
    deductible = Column(Integer)
    limit = Column(Integer)

    def __str__(self):
        return f'{self.limit} XS {self.deductible}'


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
