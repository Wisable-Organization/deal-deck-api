"""
SQLAlchemy ORM models for the database
"""

from sqlalchemy import Column, String, Integer, Numeric, Text, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

Base = declarative_base()


class MatchStage(str, enum.Enum):
    """Enum for deal-buyer match stages"""
    NEW = "new"
    NDA_SENT = "nda_sent"
    NDA_SIGNED = "nda_signed"
    CIM_SENT = "cim_sent"
    CIM_VIEWED = "cim_viewed"
    INTRO_CALL = "intro_call"
    DILIGENCE = "diligence"
    IOI = "ioi"
    LOI = "loi"
    UNDER_CONTRACT = "under_contract"
    WON = "won"
    LOST = "lost"


class Company(Base):
    __tablename__ = 'companies'

    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class CompanyMetric(Base):
    __tablename__ = 'company_metrics'

    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(UUID(as_uuid=False), ForeignKey('companies.id'), nullable=False)
    type = Column(Text, nullable=False)
    value = Column(Numeric(15, 2), nullable=False)
    fiscal_year = Column(Integer)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    company = relationship("Company", backref="metrics")


class Deal(Base):
    __tablename__ = 'deals'

    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
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
    owner_id = Column(UUID(as_uuid=False), ForeignKey('auth.users.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    company = relationship("Company", backref="deals")
    owner = relationship("User", backref="deals")


class Contact(Base):
    __tablename__ = 'contacts'

    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(Text, nullable=False)
    role = Column(Text, nullable=False)
    email = Column(Text)
    phone = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationship to BuyingParty through party_contacts
    buying_parties = relationship(
        "BuyingParty", 
        secondary="party_contacts", 
        back_populates="contacts",
        overlaps="party_contacts"
    )


class CompanyContact(Base):
    __tablename__ = 'companies_contacts'

    contact_id = Column(UUID(as_uuid=False), ForeignKey('contacts.id'), primary_key=True)
    company_id = Column(UUID(as_uuid=False), ForeignKey('companies.id'), primary_key=True)
    contact_role = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    contact = relationship("Contact", backref="company_contacts")
    company = relationship("Company", backref="company_contacts")


class PartyContact(Base):
    __tablename__ = 'party_contacts'

    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    buying_party_id = Column(UUID(as_uuid=False), ForeignKey('buying_parties.id', ondelete='CASCADE'), nullable=False)
    contact_id = Column(UUID(as_uuid=False), ForeignKey('contacts.id'), nullable=False)
    role = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    contact = relationship("Contact", overlaps="buying_parties,contacts")
    buying_party = relationship("BuyingParty", back_populates="party_contacts", overlaps="buying_parties,contacts")


class BuyingParty(Base):
    __tablename__ = 'buying_parties'

    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(Text, nullable=False)
    target_acquisition_min = Column(Integer)
    target_acquisition_max = Column(Integer)
    budget_min = Column(Numeric(15, 2))
    budget_max = Column(Numeric(15, 2))
    timeline = Column(Text)
    status = Column(Text, default='evaluating', nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    contacts = relationship(
        "Contact", 
        secondary="party_contacts", 
        back_populates="buying_parties",
        overlaps="party_contacts"
    )
    
    party_contacts = relationship(
        "PartyContact",
        back_populates="buying_party",
        overlaps="contacts,buying_parties"
    )
    
    # Relationship to documents through document_shares
    documents = relationship(
        "Document",
        secondary="document_shares",
        back_populates="buying_parties",
        overlaps="document_shares"
    )
    
    # Explicit relationship to DocumentShare (replaces backref from DocumentShare)
    document_shares = relationship(
        "DocumentShare",
        back_populates="buying_party",
        overlaps="buying_parties,documents"
    )


class DealBuyerMatch(Base):
    __tablename__ = 'deal_buyer_matches'

    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    deal_id = Column(UUID(as_uuid=False), ForeignKey('deals.id'), nullable=False)
    buying_party_id = Column(UUID(as_uuid=False), ForeignKey('buying_parties.id', ondelete='CASCADE'), nullable=False)
    target_acquisition = Column(Integer)
    budget = Column(Numeric(15, 2))
    status = Column(Text, default='interested', nullable=False)
    stage = Column(Text, default='new', nullable=False)  # Use MatchStage enum values as constants
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    deal = relationship("Deal", backref="buyer_matches")
    buying_party = relationship("BuyingParty", backref="deal_matches")


class Activity(Base):
    __tablename__ = 'activities'

    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    deal_id = Column(UUID(as_uuid=False), ForeignKey('deals.id'))
    buying_party_id = Column(UUID(as_uuid=False), ForeignKey('buying_parties.id', ondelete='CASCADE'))
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

    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    deal_id = Column(UUID(as_uuid=False), ForeignKey('deals.id'))
    name = Column(Text, nullable=False)
    status = Column(Text, default='draft', nullable=False)
    doc_type = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    deal = relationship("Deal", backref="documents")
    
    # Relationship to BuyingParty through document_shares
    buying_parties = relationship(
        "BuyingParty",
        secondary="document_shares",
        back_populates="documents",
        overlaps="document_shares"
    )
    
    # Explicit relationship to DocumentShare (replaces backref from DocumentShare)
    document_shares = relationship(
        "DocumentShare",
        back_populates="document",
        overlaps="buying_parties,documents"
    )


class DocumentShare(Base):
    __tablename__ = 'document_shares'

    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(UUID(as_uuid=False), ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    entity_id = Column(UUID(as_uuid=False), ForeignKey('buying_parties.id', ondelete='CASCADE'), name='buying_party_id', nullable=False)
    shared_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime(timezone=True))
    can_download = Column(Boolean, default=True, nullable=False)
    notes = Column(Text)

    document = relationship("Document", back_populates="document_shares", overlaps="buying_parties,documents")
    buying_party = relationship("BuyingParty", back_populates="document_shares", overlaps="buying_parties,documents")


class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'auth'}

    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), nullable=False)
    encrypted_password = Column(String(255), nullable=False)
    recovery_token = Column(String(255))
    recovery_sent_at = Column(DateTime(timezone=True))
    email_confirmed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

