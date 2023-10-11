"""
Commands for testing:
rm .\migrations\; flask db init; flask db migrate; flask db upgrade; python
from app import app; app.app_context().push(); from flaskapp.extensions import *; from flaskapp.models import *
analysis1 = Analysis(); analysis2 = Analysis(); layer1 = Layer(analysis_id=1); layer2 = Layer(analysis_id=1) ; layer3 = Layer(analysis_id=1) ; layer4 = Layer(analysis_id=2); layer5 = Layer(analysis_id=2) ; layer6 = Layer(analysis_id=2) ; session = db.session; session.add_all([layer1, layer2, layer3, layer4, layer5, layer6]) ; modelfile1 = ModelFile(analysis_id=1); modelfile2 = ModelFile(analysis_id=1) ; modelfile3 = ModelFile(analysis_id=2) ; modelfile4 = ModelFile(analysis_id=2) ; session.add_all([modelfile1, modelfile2, modelfile3, modelfile4]); selectedpricingrelationship1 = SelectedPricingRelationship(layer_id=1, modelfile_id=1) ; selectedpricingrelationship2 = SelectedPricingRelationship(layer_id=1, modelfile_id=2) ; selectedpricingrelationship3 = SelectedPricingRelationship(layer_id=2, modelfile_id=1) ; selectedpricingrelationship4 = SelectedPricingRelationship(layer_id=2, modelfile_id=2) ; result1 = Result(analysis_id=1) ; result2 = Result(analysis_id=1) ; result3 = Result(analysis_id=2) ; result4 = Result(analysis_id=2) ; session.add_all([result1, result2, result3, result4]) ; pricingrelationship1 = PricingRelationship(result_id=1, layer_id=1, modelfile_id=1) ; pricingrelationship2 = PricingRelationship(result_id=1, layer_id=1, modelfile_id=2) ; pricingrelationship3 = PricingRelationship(result_id=1, layer_id=2, modelfile_id=1) ; pricingrelationship4 = PricingRelationship(result_id=1, layer_id=2, modelfile_id=2) ; session.add_all([pricingrelationship1, pricingrelationship2, pricingrelationship3, pricingrelationship4]) ; session.commit()

This module defines a set of SQLAlchemy database models representing an insurance analysis system.

The models include:
- Analysis: Represents a reinsurance analysis.
- Layer: Represents a layer within an analysis.
- HistoLossFile: Represents historical loss data files associated with an analysis.
- HistoLoss: Represents individual historical loss records.
- PremiumFile: Represents premium data files (not used for SL pricing).
- Premium: Represents individual premium records (not used for SL pricing).
- RiskProfileFile: Represents risk profile data files (not used for SL pricing).
- RiskProfile: Represents individual risk profiles (not used for SL pricing).
- ModelFile: Represents a loss model associated with an analysis.
- ModelYearLoss: Represents individual year loss records.
- SelectedPricingRelationship: Represents selected pricing relationships between layers and model files.
- Result: Represents analysis results.
- PricingRelationship: Represents pricing relationships between layers and model files in results.
- ResultYearLoss: Represents individual year loss records in analysis results.

These models are designed to work with SQLAlchemy and are used to interact with the underlying database.

Relationships between the models:
- 1-to-many relationship between Analysis and Layer: done
- 1-to-many relationship between Analysis and HistoLossFile: done
- 1-to-many relationship between Analysis and PremiumFile: done
- 1-to-many relationship between Analysis and RiskProfileFile: done
- 1-to-many relationship between Analysis and ModelFile: done
- 1-to-many relationship between Analysis and Result: done

- 1-to-many relationship between HistoLossFile and HistoLoss: done
- 1-to-many relationship between PremiumFile and Premium: done
- 1-to-many relationship between RiskProfileFile and RiskProfile: done
- 1-to-many relationship between ModelFile and ModelYearLoss: done
- 1-to-many relationship between Result and PricingRelationship: done
- 1-to-many relationship between PricingRelationship and ResultYearLoss: done

- many-to-many relationship between Layer and ModelFile in the association object SelectedPricingRelationship: done
- many-to-many relationship between Layer and ModelFile in the association object PricingRelationship: done

Resources:
- Reference: https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#many-to-many
- https://stackoverflow.com/questions/30406808/flask-sqlalchemy-difference-between-association-model-and-association-table-fo
- https://copyprogramming.com/howto/sqlalchemy-relationship-on-many-to-many-association-table
- https://stackoverflow.com/questions/68322485/conflicts-with-relationship-between-tables
- https://docs.sqlalchemy.org/en/14/orm/backref.html
- Cascading delete: https://www.geeksforgeeks.org/sqlalchemy-cascading-deletes/

"""

from flaskapp.extensions import db
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref


class Analysis(db.Model):
    __tablename__ = 'analysis'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    quote = Column(Integer)
    client = Column(String(50))

    # Define the 1-to-many relationship between Analysis and Layer, HistoLossFile, PremiumFile, RiskProfileFile, ModelFile, Result
    layers = relationship('Layer', back_populates='analysis', cascade='all, delete-orphan')
    histolossfiles = relationship('HistoLossFile', back_populates='analysis', cascade='all, delete-orphan')
    premiumfiles = relationship('PremiumFile', back_populates='analysis', cascade='all, delete-orphan')
    riskprofilefiles = relationship('RiskProfileFile', back_populates='analysis', cascade='all, delete-orphan')
    modelfiles = relationship('ModelFile', back_populates='analysis', cascade='all, delete-orphan')
    results = relationship('Result', back_populates='analysis', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<{self.__tablename__.capitalize()} {self.id} {self.name}>'


class Layer(db.Model):
    __tablename__ = 'layer'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))

    # Define the specific columns
    premium = Column(Integer)
    deductible = Column(Integer)
    limit = Column(Integer)

    # Define the 1-to-many relationship between Analysis and Layer
    analysis_id = Column(Integer, ForeignKey(Analysis.id))
    analysis = relationship('Analysis', back_populates='layers')

    # Define the many-to-many relationship between Layer and ModelFile in the association object PricingRelationship
    selectedmodelfiles = relationship(
        'ModelFile',
        secondary='selectedpricingrelationship',
        back_populates='selectedlayers',
    )

    # Define the many-to-many relationship between Layer and ModelFile in the association object PricingRelationship
    modelfiles = relationship(
        'ModelFile',
        secondary='pricingrelationship',
        back_populates='layers',
    )

    def __repr__(self):
        return f'<{self.__tablename__.capitalize()} {self.id} {self.name}>'


class HistoLossFile(db.Model):
    __tablename__ = 'histolossfile'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))

    # Define the specific columns
    vintage = Column(Integer)

    # Define the 1-to-many relationship between Analysis and HistoLossFile
    analysis_id = Column(Integer, ForeignKey(Analysis.id))
    analysis = relationship('Analysis', back_populates='histolossfiles')

    # 1-to-many relationship between HistoLossFile and HistoLoss
    losses = relationship('HistoLoss', back_populates='lossfile', cascade='all, delete')

    def __repr__(self):
        return f'<{self.__tablename__.capitalize()} {self.id} {self.name}>'


class HistoLoss(db.Model):
    __tablename__ = 'histoloss'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))

    # Define the specific columns
    year = Column(Integer)
    premium = Column(Integer)
    loss = Column(Integer)
    loss_ratio = Column(Float)

    # 1-to-many relationship between HistoLossFile and HistoLoss
    lossfile_id = Column(Integer, ForeignKey(HistoLossFile.id))
    lossfile = relationship('HistoLossFile', back_populates='losses')

    def __repr__(self):
        return f'<{self.__tablename__.capitalize()} {self.id} {self.name}>'


class PremiumFile(db.Model):  # This model is not necessary for SL pricing
    __tablename__ = 'premiumfile'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))

    # 1-to-many relationship between Analysis and PremiumFile
    analysis_id = Column(Integer, ForeignKey(Analysis.id))
    analysis = relationship('Analysis', back_populates='premiumfiles')

    # 1-to-many relationship between PremiumFile and Premium
    premiums = relationship('Premium', back_populates='premiumfile')

    def __repr__(self):
        return f'<{self.__tablename__.capitalize()} {self.id} {self.name}>'


class Premium(db.Model):  # This model is not necessary for SL pricing
    __tablename__ = 'premium'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))

    # Define the specific columns
    year = Column(Integer)
    amount = Column(Integer)

    # 1-to-many relationship between PremiumFile and Premium
    premiumfile_id = Column(Integer, ForeignKey(PremiumFile.id))
    premiumfile = relationship('PremiumFile', back_populates='premiums')

    def __repr__(self):
        return f'<{self.__tablename__.capitalize()} {self.id} {self.name}>'


class RiskProfileFile(db.Model):  # This model is not necessary for SL pricing
    __tablename__ = 'riskprofilefile'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))

    # Define the 1-to-many relationship between Analysis and RiskProfile
    analysis_id = Column(Integer, ForeignKey(Analysis.id))
    analysis = relationship('Analysis', back_populates='riskprofilefiles')

    # 1-to-many relationship between RiskProfileFile and RiskProfile
    riskprofiles = relationship('RiskProfile', back_populates='riskprofilefile')

    def __repr__(self):
        return f'<{self.__tablename__.capitalize()} {self.id} {self.name}>'


class RiskProfile(db.Model):  # This model is not necessary for SL pricing
    __tablename__ = 'riskprofile'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))

    # 1-to-many relationship between RiskProfileFile and RiskProfile
    riskprofilefile_id = Column(Integer, ForeignKey(RiskProfileFile.id))
    riskprofilefile = relationship('RiskProfileFile', back_populates='riskprofiles')

    def __repr__(self):
        return f'<{self.__tablename__.capitalize()} {self.id} {self.name}>'


class ModelFile(db.Model):
    __tablename__ = 'modelfile'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))

    # Define the 1-to-many relationship between Analysis and ModelFile
    analysis_id = Column(Integer, ForeignKey(Analysis.id))
    analysis = relationship('Analysis', back_populates='modelfiles')

    # Define the many-to-many relationship between Layer and ModelFile in the association object PricingRelationship
    selectedlayers = relationship(
        'Layer',
        secondary='selectedpricingrelationship',
        back_populates='selectedmodelfiles',
    )

    # Define the many-to-many relationship between Layer and ModelFile in the association object PricingRelationship
    layers = relationship(
        'Layer',
        secondary='pricingrelationship',
        back_populates='modelfiles',
    )

    # Define the 1-to-many relationship between ModelFile and ModelYearLoss
    modelyearlosses = relationship('ModelYearLoss', back_populates='modelfile', cascade='all, delete')

    def __repr__(self):
        return f'<{self.__tablename__.capitalize()} {self.id} {self.name}>'


class ModelYearLoss(db.Model):
    __tablename__ = 'modelyearloss'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))

    # Define the specific columns
    year = Column(Integer)
    amount = Column(Integer)

    # Define the 1-to-many relationship between ModelFile and ModelYearLoss
    modelfile_id = Column(Integer, ForeignKey(ModelFile.id))
    modelfile = relationship('ModelFile', back_populates='modelyearlosses')

    def __repr__(self):
        return f'<{self.__tablename__.capitalize()} {self.id} {self.name}>'


class SelectedPricingRelationship(db.Model):
    __tablename__ = 'selectedpricingrelationship'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))

    # Define the many-to-many relationship between Layer and ModelFile in the association object SelectedPricingRelationship
    layer_id = Column(Integer, ForeignKey(Layer.id))
    layer = relationship(
        'Layer',
        backref=backref('selectedpricingrelationships', passive_deletes='all, delete-orphan'),
    )

    modelfile_id = Column(Integer, ForeignKey(ModelFile.id))
    modelfile = relationship(
        'ModelFile',
        backref=backref('selectedpricingrelationships', passive_deletes='all, delete-orphan'),
    )

    def __repr__(self):
        return f'<{self.__tablename__.capitalize()} {self.id} {self.name}>'


class Result(db.Model):
    __tablename__ = 'result'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))

    # Define the 1-to-many relationship between Analysis and Result
    analysis_id = Column(Integer, ForeignKey(Analysis.id))
    analysis = relationship('Analysis', back_populates='results')

    # Define the 1-to-many relationship between Result and PricingRelationship
    pricingrelationships = relationship('PricingRelationship', back_populates='result', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<{self.__tablename__.capitalize()} {self.id} {self.name}>'


class PricingRelationship(db.Model):
    __tablename__ = 'pricingrelationship'
    id = Column(Integer, primary_key=True)

    # Define the 1-to-many relationship between Result and PricingRelationship
    result_id = Column(Integer, ForeignKey(Result.id))
    result = relationship('Result', back_populates='pricingrelationships')

    # Define the many-to-many relationship between Layer and ModelFile in the association object PricingRelationship
    layer_id = Column(Integer, ForeignKey(Layer.id))
    layer = relationship(
        'Layer',
        backref=backref('pricingrelationships', passive_deletes='all, delete-orphan'),
    )

    modelfile_id = Column(Integer, ForeignKey(ModelFile.id))
    modelfile = relationship(
        'ModelFile',
        backref=backref('pricingrelationships', passive_deletes='all, delete-orphan'),
    )

    # Define the 1-to-many relationship between PricingRelationship and ResultYearLoss
    resultyearlosses = relationship('ResultYearLoss', back_populates='pricingrelationship')

    def __repr__(self):
        return f'<{self.__tablename__.capitalize()} {self.id} {self.name}>'


class ResultYearLoss(db.Model):
    __tablename__ = 'resultyearloss'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))

    # Define the specific columns
    year = Column(Integer)
    gross_amount = Column(Integer)
    net_amount = Column(Integer)

    # Define the 1-to-many relationship between PricingRelationship and ResultYearLoss
    pricingrelationship_id = Column(Integer, ForeignKey(PricingRelationship.id))
    pricingrelationship = relationship('PricingRelationship', back_populates='resultyearlosses')

    def __repr__(self):
        return f'<{self.__tablename__.capitalize()} {self.id} {self.name}>'
