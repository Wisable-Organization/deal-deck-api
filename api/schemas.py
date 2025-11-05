"""
Marshmallow schemas for serialization/deserialization
"""

import marshmallow as ma
from marshmallow import fields, validate, ValidationError
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from typing import Optional
from datetime import datetime
from .models import (
    Base, Company, CompanyMetric, Deal, Contact, CompanyContact,
    BuyingParty, DealBuyerMatch, Activity, Document
)

def camelcase(s):
    parts = iter(s.split("_"))
    return next(parts) + "".join(i.title() for i in parts)


class BaseSchema(SQLAlchemySchema):
    """Base schema with model property"""
    
    class Meta:
        model = None  # To be set by subclasses
        load_instance = True
        sqla_session = None  # Session will be provided when needed
    
    def on_bind_field(self, field_name, field_obj):
        field_obj.data_key = camelcase(field_obj.data_key or field_name)


class CompanySchema(BaseSchema):
    """Schema for Company model"""
    
    class Meta:
        model = Company
        
    id = auto_field()
    name = auto_field()
    created_at = auto_field()


class CompanyMetricSchema(BaseSchema):
    """Schema for CompanyMetric model"""
    
    class Meta:
        model = CompanyMetric
        
    id = auto_field()
    company_id = auto_field()
    type = auto_field()
    value = auto_field()
    fiscal_year = auto_field()
    created_at = auto_field()


class DealSchema(BaseSchema):
    """Schema for Deal model"""
    
    class Meta:
        model = Deal
        
    id = auto_field()
    company_id = auto_field()
    stage = auto_field()
    priority = auto_field()
    sde = auto_field()
    valuation_min = auto_field()
    valuation_max = auto_field()
    sde_multiple = auto_field()
    revenue_multiple = auto_field()
    commission = auto_field()
    description = auto_field()
    notes = auto_field()
    next_step_days = auto_field()
    touches = auto_field()
    age_in_stage = auto_field()
    health_score = auto_field()
    owner = auto_field()
    created_at = auto_field()


class ContactSchema(BaseSchema):
    """Schema for Contact model"""
    
    class Meta:
        model = Contact
        
    id = auto_field()
    name = auto_field()
    role = auto_field()
    email = auto_field()
    phone = auto_field()
    entity_id = auto_field()
    entity_type = auto_field()
    created_at = auto_field()


class CompanyContactSchema(BaseSchema):
    """Schema for CompanyContact model"""
    
    class Meta:
        model = CompanyContact
        
    contact_id = auto_field()
    company_id = auto_field()
    contact_role = auto_field()
    created_at = auto_field()


class BuyingPartySchema(BaseSchema):
    """Schema for BuyingParty model"""
    
    class Meta:
        model = BuyingParty
        
    id = auto_field()
    name = auto_field()
    target_acquisition_min = auto_field()
    target_acquisition_max = auto_field()
    budget_min = auto_field()
    budget_max = auto_field()
    timeline = auto_field()
    status = auto_field()
    notes = auto_field()
    created_at = auto_field()


class DealBuyerMatchSchema(BaseSchema):
    """Schema for DealBuyerMatch model"""
    
    class Meta:
        model = DealBuyerMatch
        
    id = auto_field()
    deal_id = auto_field()
    buying_party_id = auto_field()
    target_acquisition = auto_field()
    budget = auto_field()
    status = auto_field()
    created_at = auto_field()


class ActivitySchema(BaseSchema):
    """Schema for Activity model"""
    
    class Meta:
        model = Activity
        
    id = auto_field()
    deal_id = auto_field()
    buying_party_id = auto_field()
    type = auto_field()
    title = auto_field()
    description = auto_field()
    status = auto_field()
    assigned_to = auto_field()
    due_date = auto_field()
    completed_at = auto_field()
    created_at = auto_field()


class DocumentSchema(BaseSchema):
    """Schema for Document model"""
    
    class Meta:
        model = Document
        
    id = auto_field()
    deal_id = auto_field()
    name = auto_field()
    status = auto_field()
    doc_type = auto_field()
    created_at = auto_field()


# Request/Response schemas for API (with computed fields)
class DealResponseSchema(BaseSchema):
    """Schema for Deal API response (includes company_name and revenue)"""
    id = fields.Str(required=True)
    company_name = fields.Str(required=True)
    revenue = fields.Str(required=True)
    sde = fields.Str(allow_none=True)
    valuation_min = fields.Str(allow_none=True)
    valuation_max = fields.Str(allow_none=True)
    sde_multiple = fields.Str(allow_none=True)
    revenue_multiple = fields.Str(allow_none=True)
    commission = fields.Str(allow_none=True)
    stage = fields.Str(required=True)
    priority = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    notes = fields.Str(allow_none=True)
    next_step_days = fields.Int(allow_none=True)
    touches = fields.Int(required=True)
    age_in_stage = fields.Int(required=True)
    health_score = fields.Int(required=True)
    owner = fields.Str(required=True)
    created_at = fields.DateTime(required=True)


class DealCreateSchema(BaseSchema):
    """Schema for creating a Deal"""
    company_name = fields.Str(required=True)
    revenue = fields.Str(required=True)
    stage = fields.Str(required=True)
    priority = fields.Str(load_default="medium")
    owner = fields.Str(required=True)
    sde = fields.Str(allow_none=True)
    valuation_min = fields.Str(allow_none=True)
    valuation_max = fields.Str(allow_none=True)
    sde_multiple = fields.Str(allow_none=True)
    revenue_multiple = fields.Str(allow_none=True)
    commission = fields.Str(allow_none=True)
    description = fields.Str(allow_none=True)
    notes = fields.Str(allow_none=True)
    next_step_days = fields.Int(allow_none=True)
    touches = fields.Int(load_default=0)
    age_in_stage = fields.Int(load_default=0)
    health_score = fields.Int(load_default=85)


class DealUpdateSchema(BaseSchema):
    """Schema for updating a Deal"""
    company_name = fields.Str(allow_none=True)
    revenue = fields.Str(allow_none=True)
    stage = fields.Str(allow_none=True)
    priority = fields.Str(allow_none=True)
    owner = fields.Str(allow_none=True)
    sde = fields.Str(allow_none=True)
    valuation_min = fields.Str(allow_none=True)
    valuation_max = fields.Str(allow_none=True)
    sde_multiple = fields.Str(allow_none=True)
    revenue_multiple = fields.Str(allow_none=True)
    commission = fields.Str(allow_none=True)
    description = fields.Str(allow_none=True)
    notes = fields.Str(allow_none=True)
    next_step_days = fields.Int(allow_none=True)
    touches = fields.Int(allow_none=True)
    age_in_stage = fields.Int(allow_none=True)
    health_score = fields.Int(allow_none=True)


class NotesUpdateSchema(BaseSchema):
    """Schema for updating notes"""
    notes = fields.Str(required=True, validate=validate.Length(min=0))


class ContactResponseSchema(BaseSchema):
    """Schema for Contact API response"""
    id = fields.Str(required=True)
    name = fields.Str(required=True)
    role = fields.Str(required=True)
    email = fields.Str(allow_none=True)
    phone = fields.Str(allow_none=True)
    entity_id = fields.Str(required=True)
    entity_type = fields.Str(required=True)


class ContactCreateSchema(BaseSchema):
    """Schema for creating a Contact"""
    name = fields.Str(required=True)
    role = fields.Str(required=True)
    email = fields.Str(allow_none=True)
    phone = fields.Str(allow_none=True)
    entity_id = fields.Str(required=True)
    entity_type = fields.Str(required=True)


class BuyingPartyResponseSchema(BaseSchema):
    """Schema for BuyingParty API response"""
    id = fields.Str(required=True)
    name = fields.Str(required=True)
    target_acquisition_min = fields.Int(allow_none=True)
    target_acquisition_max = fields.Int(allow_none=True)
    budget_min = fields.Str(allow_none=True)
    budget_max = fields.Str(allow_none=True)
    timeline = fields.Str(allow_none=True)
    status = fields.Str(required=True)
    notes = fields.Str(allow_none=True)
    created_at = fields.DateTime(required=True)


class BuyingPartyCreateSchema(BaseSchema):
    """Schema for creating a BuyingParty"""
    name = fields.Str(required=True)
    target_acquisition_min = fields.Int(allow_none=True)
    target_acquisition_max = fields.Int(allow_none=True)
    budget_min = fields.Str(allow_none=True)
    budget_max = fields.Str(allow_none=True)
    timeline = fields.Str(allow_none=True)
    status = fields.Str(load_default="evaluating")
    notes = fields.Str(allow_none=True)


class BuyingPartyUpdateSchema(BaseSchema):
    """Schema for updating a BuyingParty"""
    name = fields.Str(allow_none=True)
    target_acquisition_min = fields.Int(allow_none=True)
    target_acquisition_max = fields.Int(allow_none=True)
    budget_min = fields.Str(allow_none=True)
    budget_max = fields.Str(allow_none=True)
    timeline = fields.Str(allow_none=True)
    status = fields.Str(allow_none=True)
    notes = fields.Str(allow_none=True)


class DealBuyerMatchResponseSchema(BaseSchema):
    """Schema for DealBuyerMatch API response"""
    id = fields.Str(required=True)
    deal_id = fields.Str(required=True)
    buying_party_id = fields.Str(required=True)
    target_acquisition = fields.Int(allow_none=True)
    budget = fields.Str(allow_none=True)
    status = fields.Str(required=True)
    created_at = fields.DateTime(required=True)


class MatchCreateSchema(BaseSchema):
    """Schema for creating a DealBuyerMatch"""
    deal_id = fields.Str(required=True)
    buying_party_id = fields.Str(required=True)
    target_acquisition = fields.Int(allow_none=True)
    budget = fields.Str(allow_none=True)
    status = fields.Str(load_default="interested")


class ActivityResponseSchema(BaseSchema):
    """Schema for Activity API response"""
    id = fields.Str(required=True)
    deal_id = fields.Str(allow_none=True)
    buying_party_id = fields.Str(allow_none=True)
    type = fields.Str(required=True)
    title = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    status = fields.Str(required=True)
    assigned_to = fields.Str(allow_none=True)
    due_date = fields.DateTime(allow_none=True)
    completed_at = fields.DateTime(allow_none=True)
    created_at = fields.DateTime(required=True)


class ActivityCreateSchema(BaseSchema):
    """Schema for creating an Activity"""
    deal_id = fields.Str(allow_none=True)
    buying_party_id = fields.Str(allow_none=True)
    type = fields.Str(required=True)
    title = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    status = fields.Str(load_default="pending")
    assigned_to = fields.Str(allow_none=True)
    due_date = fields.DateTime(allow_none=True)


class ActivityUpdateSchema(BaseSchema):
    """Schema for updating an Activity"""
    type = fields.Str(allow_none=True)
    title = fields.Str(allow_none=True)
    description = fields.Str(allow_none=True)
    status = fields.Str(allow_none=True)
    assigned_to = fields.Str(allow_none=True)
    due_date = fields.DateTime(allow_none=True)
    completed_at = fields.DateTime(allow_none=True)


class DocumentResponseSchema(BaseSchema):
    """Schema for Document API response"""
    id = fields.Str(required=True)
    deal_id = fields.Str(allow_none=True)
    name = fields.Str(required=True)
    status = fields.Str(required=True)
    doc_type = fields.Str(allow_none=True)
    created_at = fields.DateTime(required=True)


class DocumentCreateSchema(BaseSchema):
    """Schema for creating a Document"""
    deal_id = fields.Str(allow_none=True)
    name = fields.Str(required=True)
    status = fields.Str(load_default="draft")
    doc_type = fields.Str(allow_none=True)


class BuyerRowSchema(BaseSchema):
    """Schema for composite BuyerRow response"""
    match = fields.Nested(DealBuyerMatchResponseSchema, required=True)
    party = fields.Nested(BuyingPartyResponseSchema, required=True)
    contact = fields.Nested(ContactResponseSchema, allow_none=True)


class PartyMatchRowSchema(BaseSchema):
    """Schema for composite PartyMatchRow response"""
    match = fields.Nested(DealBuyerMatchResponseSchema, required=True)
    deal = fields.Nested(DealResponseSchema, required=True)


class MeetingSummarySchema(BaseSchema):
    """Schema for MeetingSummary response"""
    summary = fields.Str(required=True)
    created_at = fields.DateTime(required=True)
    source = fields.Str(allow_none=True)

