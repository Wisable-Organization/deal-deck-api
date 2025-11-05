"""
SQLAlchemy ORM models for the database
"""

from sqlalchemy import Column, String, Integer, Numeric, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

Base = declarative_base()


class Company(Base):
    __tablename__ = 'companies'

    id = Column(UUID(as_uuid=False), primary_key=True)
    name = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class CompanyMetric(Base):
    __tablename__ = 'company_metrics'

    id = Column(UUID(as_uuid=False), primary_key=True)
    company_id = Column(UUID(as_uuid=False), ForeignKey('companies.id'), nullable=False)
    type = Column(Text, nullable=False)
    value = Column(Numeric(15, 2), nullable=False)
    fiscal_year = Column(Integer)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    company = relationship("Company", backref="metrics")


class Deal(Base):
    __tablename__ = 'deals'

    id = Column(UUID(as_uuid=False), primary_key=True)
    company_id = Column(UUID(as_uuid=False), ForeignKey('companies.id'), nullable=False)
    stage = Column(Text, nullable=False)
    priority = Column(Text, default='medium', nullable=False)
    sde = Column(Numeric(15, 2))
    valuation_min = Column(Numeric(15, 2))
    valuation_max = Column(Numeric(15, 2))
    sde_multiple = Column(Numeric(5, 2))
    revenue_multiple = Column(Numeric(5, 2))
    commission = Column(Numeric(5, 2))
    description = Column(Text)
    notes = Column(Text)
    next_step_days = Column(Integer)
    touches = Column(Integer, default=0, nullable=False)
    age_in_stage = Column(Integer, default=0, nullable=False)
    health_score = Column(Integer, default=85, nullable=False)
    owner = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    company = relationship("Company", backref="deals")


class Contact(Base):
    __tablename__ = 'contacts'

    id = Column(UUID(as_uuid=False), primary_key=True)
    name = Column(Text, nullable=False)
    role = Column(Text, nullable=False)
    email = Column(Text)
    phone = Column(Text)
    entity_id = Column(UUID(as_uuid=False), nullable=False)
    entity_type = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class CompanyContact(Base):
    __tablename__ = 'companies_contacts'

    contact_id = Column(UUID(as_uuid=False), ForeignKey('contacts.id'), primary_key=True)
    company_id = Column(UUID(as_uuid=False), ForeignKey('companies.id'), primary_key=True)
    contact_role = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    contact = relationship("Contact", backref="company_contacts")
    company = relationship("Company", backref="company_contacts")


class BuyingParty(Base):
    __tablename__ = 'buying_parties'

    id = Column(UUID(as_uuid=False), primary_key=True)
    name = Column(Text, nullable=False)
    target_acquisition_min = Column(Integer)
    target_acquisition_max = Column(Integer)
    budget_min = Column(Numeric(15, 2))
    budget_max = Column(Numeric(15, 2))
    timeline = Column(Text)
    status = Column(Text, default='evaluating', nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class DealBuyerMatch(Base):
    __tablename__ = 'deal_buyer_matches'

    id = Column(UUID(as_uuid=False), primary_key=True)
    deal_id = Column(UUID(as_uuid=False), ForeignKey('deals.id'), nullable=False)
    buying_party_id = Column(UUID(as_uuid=False), ForeignKey('buying_parties.id'), nullable=False)
    target_acquisition = Column(Integer)
    budget = Column(Numeric(15, 2))
    status = Column(Text, default='interested', nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    deal = relationship("Deal", backref="buyer_matches")
    buying_party = relationship("BuyingParty", backref="deal_matches")


class Activity(Base):
    __tablename__ = 'activities'

    id = Column(UUID(as_uuid=False), primary_key=True)
    deal_id = Column(UUID(as_uuid=False), ForeignKey('deals.id'))
    buying_party_id = Column(UUID(as_uuid=False), ForeignKey('buying_parties.id'))
    type = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    description = Column(Text)
    status = Column(Text, default='pending', nullable=False)
    assigned_to = Column(Text)
    due_date = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    deal = relationship("Deal", backref="activities")
    buying_party = relationship("BuyingParty", backref="activities")


class Document(Base):
    __tablename__ = 'documents'

    id = Column(UUID(as_uuid=False), primary_key=True)
    deal_id = Column(UUID(as_uuid=False), ForeignKey('deals.id'))
    name = Column(Text, nullable=False)
    status = Column(Text, default='draft', nullable=False)
    doc_type = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    deal = relationship("Deal", backref="documents")

