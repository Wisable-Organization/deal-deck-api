"""
Marshmallow schemas for serialization/deserialization
"""

import marshmallow as ma
from marshmallow import fields, validate, ValidationError
from typing import Optional
from datetime import datetime
from api.models import (
    Base, Company, CompanyMetric, Deal, Contact, CompanyContact,
    BuyingParty, DealBuyerMatch, Activity, Document
)

def camelcase(s):
    parts = iter(s.split("_"))
    return next(parts) + "".join(i.title() for i in parts)


class BaseSchema(ma.Schema):
    """Base schema with model property"""
    
    class Meta:
        model = None  # To be set by subclasses
        load_instance = True
        sqla_session = None  # Session will be provided when needed
    
    def on_bind_field(self, field_name, field_obj):
        field_obj.data_key = camelcase(field_obj.data_key or field_name)


        
class UserResponseSchema(BaseSchema):
    """Schema for User API response"""
    id = fields.Str(required=True)
    email = fields.Str(required=True)


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
    owner_id = fields.Str(required=True)
    owner = fields.Str(required=True)  # Owner email for display
    created_at = fields.DateTime(required=True)


class DealCreateSchema(BaseSchema):
    """Schema for creating a Deal"""
    company_name = fields.Str(required=True)
    revenue = fields.Str(required=True)
    stage = fields.Str(required=True)
    priority = fields.Str(load_default="medium")
    owner_id = fields.Str(required=True)
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
    owner_id = fields.Str(allow_none=True)
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
    entity_id = fields.Str(allow_none=True)  # Optional, added by storage layer
    entity_type = fields.Str(allow_none=True)  # Optional, added by storage layer

class ContactCreateSchema(BaseSchema):
    """Schema for creating a Contact"""
    name = fields.Str(required=True)
    role = fields.Str(required=True)
    email = fields.Str(allow_none=True)
    phone = fields.Str(allow_none=True)

class PartyContactCreateSchema(BaseSchema):
    """Schema for creating a PartyContact (linking a Contact to a BuyingParty)"""
    buying_party_id = fields.Str(required=True)
    contact_id = fields.Str(required=True)
    role = fields.Str(allow_none=True)

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
    contacts = fields.List(fields.Nested(ContactResponseSchema), allow_none=True)


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
    stage = fields.Str(allow_none=True)
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

