"""
Pydantic models for DealDash API
Shared models to avoid circular imports
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


# Core data models
class Deal(BaseModel):
    id: str
    companyName: str
    revenue: str
    sde: Optional[str] = None
    valuationMin: Optional[str] = None
    valuationMax: Optional[str] = None
    sdeMultiple: Optional[str] = None
    revenueMultiple: Optional[str] = None
    commission: Optional[str] = None
    stage: str
    priority: str
    description: Optional[str] = None
    notes: Optional[str] = None
    nextStepDays: Optional[int] = None
    touches: int = 0
    ageInStage: int = 0
    healthScore: int = 85
    owner: str
    createdAt: datetime


class Contact(BaseModel):
    id: str
    name: str
    role: str
    email: Optional[str] = None
    phone: Optional[str] = None
    entityId: str
    entityType: str


class BuyingParty(BaseModel):
    id: str
    name: str
    targetAcquisitionMin: Optional[int] = None
    targetAcquisitionMax: Optional[int] = None
    budgetMin: Optional[str] = None
    budgetMax: Optional[str] = None
    timeline: Optional[str] = None
    status: str
    notes: Optional[str] = None
    createdAt: datetime


class DealBuyerMatch(BaseModel):
    id: str
    dealId: str
    buyingPartyId: str
    targetAcquisition: Optional[int] = None
    budget: Optional[str] = None
    status: str
    createdAt: datetime


class Activity(BaseModel):
    id: str
    dealId: Optional[str] = None
    buyingPartyId: Optional[str] = None
    type: str
    title: str
    description: Optional[str] = None
    status: str
    assignedTo: Optional[str] = None
    dueDate: Optional[datetime] = None
    completedAt: Optional[datetime] = None
    createdAt: datetime


class Document(BaseModel):
    id: str
    dealId: Optional[str] = None
    buyingPartyId: Optional[str] = None
    name: str
    status: str
    url: Optional[str] = None
    docType: Optional[str] = None
    createdAt: datetime


class Agreement(BaseModel):
    id: str
    dealId: str
    buyingPartyId: str
    type: str
    status: str
    provider: Optional[str] = None
    providerEnvelopeId: Optional[str] = None
    sentAt: Optional[datetime] = None
    viewedAt: Optional[datetime] = None
    signedAt: Optional[datetime] = None
    expiresAt: Optional[datetime] = None
    amount: Optional[str] = None
    documentId: Optional[str] = None
    notes: Optional[str] = None
    createdAt: datetime


# Insert/Update payloads
class DealCreate(BaseModel):
    companyName: str
    revenue: str
    stage: str
    priority: str = "medium"
    owner: str
    sde: Optional[str] = None
    valuationMin: Optional[str] = None
    valuationMax: Optional[str] = None
    sdeMultiple: Optional[str] = None
    revenueMultiple: Optional[str] = None
    commission: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    nextStepDays: Optional[int] = None
    touches: Optional[int] = 0
    ageInStage: Optional[int] = 0
    healthScore: Optional[int] = 85


class DealUpdate(BaseModel):
    companyName: Optional[str] = None
    revenue: Optional[str] = None
    stage: Optional[str] = None
    priority: Optional[str] = None
    owner: Optional[str] = None
    sde: Optional[str] = None
    valuationMin: Optional[str] = None
    valuationMax: Optional[str] = None
    sdeMultiple: Optional[str] = None
    revenueMultiple: Optional[str] = None
    commission: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    nextStepDays: Optional[int] = None
    touches: Optional[int] = None
    ageInStage: Optional[int] = None
    healthScore: Optional[int] = None


class NotesUpdate(BaseModel):
    notes: str = Field(min_length=0)


class ContactCreate(BaseModel):
    name: str
    role: str
    email: Optional[str] = None
    phone: Optional[str] = None
    entityId: str
    entityType: str


class BuyingPartyCreate(BaseModel):
    name: str
    targetAcquisitionMin: Optional[int] = None
    targetAcquisitionMax: Optional[int] = None
    budgetMin: Optional[str] = None
    budgetMax: Optional[str] = None
    timeline: Optional[str] = None
    status: str = "evaluating"
    notes: Optional[str] = None


class BuyingPartyUpdate(BaseModel):
    name: Optional[str] = None
    targetAcquisitionMin: Optional[int] = None
    targetAcquisitionMax: Optional[int] = None
    budgetMin: Optional[str] = None
    budgetMax: Optional[str] = None
    timeline: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class ActivityCreate(BaseModel):
    dealId: Optional[str] = None
    buyingPartyId: Optional[str] = None
    type: str
    title: str
    description: Optional[str] = None
    status: str = "pending"
    assignedTo: Optional[str] = None
    dueDate: Optional[datetime] = None


class ActivityUpdate(BaseModel):
    type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    assignedTo: Optional[str] = None
    dueDate: Optional[datetime] = None
    completedAt: Optional[datetime] = None


class DocumentCreate(BaseModel):
    dealId: Optional[str] = None
    buyingPartyId: Optional[str] = None
    name: str
    status: str = "draft"
    url: Optional[str] = None


class MatchCreate(BaseModel):
    dealId: str
    buyingPartyId: str
    targetAcquisition: Optional[int] = None
    budget: Optional[str] = None
    status: str = "interested"


# Composite models
class BuyerRow(BaseModel):
    match: DealBuyerMatch
    party: BuyingParty
    contact: Optional[Contact] = None


class MeetingSummary(BaseModel):
    summary: str
    createdAt: datetime
    source: Optional[str] = None
