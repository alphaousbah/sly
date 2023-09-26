"""
This module defines the database models for a Flask application. It includes the following models:

- Analysis: Represents the analysis with attributes id, quote, name, and client.
- Layer: Represents reinsurance layers with attributes id, analysis_id, deductible, and limit.

These models are designed to work with SQLAlchemy and are used to interact with the underlying database.
Each model corresponds to a database table with its respective fields.
"""

# Cascading delete : https://www.geeksforgeeks.org/sqlalchemy-cascading-deletes/

from flaskapp.extensions import db


class Analysis(db.Model):
    __tablename__ = 'analysis'
    id = db.Column(db.Integer, primary_key=True)
    quote = db.Column(db.Integer)
    name = db.Column(db.String(50))
    client = db.Column(db.String(50))
    layers = db.relationship('Layer', backref='analysis', cascade='all, delete')
    histolossfiles = db.relationship('HistoLossFile', backref='analysis', cascade='all, delete')
    modeledlossfiles = db.relationship('ModeledLossFile', backref='analysis', cascade='all, delete')
    yearlosstables = db.relationship('YearLossTable', backref='analysis', cascade='all, delete')

    def __repr__(self):
        return f'<Analysis {self.name}>'


# Create a many-to-many db.relationship between layers and year loss tables
# The helper table must be created before the 2 linked objects
# https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/#many-to-many-db.relationships
yearlosstables = db.Table(
    'yearlosstables',
    db.Column('yearlosstable_id', db.Integer, db.ForeignKey('yearlosstable.id'), primary_key=True),
    db.Column('layer_id', db.Integer, db.ForeignKey('layer.id'), primary_key=True),
)


class Layer(db.Model):
    __tablename__ = 'layer'
    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analysis.id'))
    premium = db.Column(db.Integer)
    deductible = db.Column(db.Integer)
    limit = db.Column(db.Integer)
    yearlosstables = db.relationship(
        'YearLossTable',
        secondary=yearlosstables,
        lazy='subquery',
        backref=db.backref('layers', lazy=True)
    )

    def __repr__(self):
        return f'{self.limit} XS {self.deductible}'


class HistoLossFile(db.Model):
    __tablename__ = 'histolossfile'
    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analysis.id'))
    vintage = db.Column(db.Integer)
    name = db.Column(db.String(50), nullable=False)
    losses = db.relationship('HistoLoss', backref='file', cascade='all, delete')

    def __repr__(self):
        return f'<HistoLossFile {self.name}>'


class HistoLoss(db.Model):
    __tablename__ = 'histoloss'
    id = db.Column(db.Integer, primary_key=True)
    lossfile_id = db.Column(db.Integer, db.ForeignKey('histolossfile.id'))
    year = db.Column(db.Integer)
    premium = db.Column(db.Integer)
    loss = db.Column(db.Integer)
    loss_ratio = db.Column(db.Float)

    def __repr__(self):
        return f'<HistoLoss {self.year}: {self.premium}, {self.loss}, {self.loss_ratio}>'


class ModeledLossFile(db.Model):
    __tablename__ = 'modeledlossfile'
    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analysis.id'))
    name = db.Column(db.String(50), nullable=False)
    losses = db.relationship('ModeledLoss', backref='file', cascade='all, delete')

    def __repr__(self):
        return f'<ModeledLossFile {self.name}>'


class ModeledLoss(db.Model):
    __tablename__ = 'modeledloss'
    id = db.Column(db.Integer, primary_key=True)
    lossfile_id = db.Column(db.Integer, db.ForeignKey('modeledlossfile.id'))
    year = db.Column(db.Integer)
    amount = db.Column(db.Integer)

    def __repr__(self):
        return f'<ModeledLoss {self.year}: {self.amount}>'


class YearLossTable(db.Model):
    __tablename__ = 'yearlosstable'
    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analysis.id'))
    name = db.Column(db.String(50))
    view = db.Column(db.String(5))  # gross or net
    events = db.relationship('YearLoss', backref='table', cascade='all, delete')

    def __repr__(self):
        return f'<YearLossTable {self.name}>'


class YearLoss(db.Model):
    __tablename__ = 'yearloss'
    id = db.Column(db.Integer, primary_key=True)
    yearlosstable_id = db.Column(db.Integer, db.ForeignKey('yearlosstable.id'))
    year = db.Column(db.Integer)
    amount = db.Column(db.Float)

    def __repr__(self):
        return f'<YearLoss {self.year}: {self.amount}>'
