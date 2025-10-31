"""
In-memory storage fallback for when Supabase is not available
"""

from typing import List, Optional
from uuid import uuid4
from datetime import datetime
from .models import (
    Deal, Contact, BuyingParty, DealBuyerMatch, Activity, Document,
    DealCreate, DealUpdate, NotesUpdate, ContactCreate, BuyingPartyCreate,
    BuyingPartyUpdate, ActivityCreate, ActivityUpdate, DocumentCreate, MatchCreate
)

class MemoryStorage:
    """In-memory storage implementation"""
    
    def __init__(self):
        self.deals = {}
        self.contacts = {}
        self.buying_parties = {}
        self.matches = {}
        self.activities = {}
        self.documents = {}
        self._seed_data()
    
    def _seed_data(self):
        """Seed with sample data"""
        if self.deals:
            return
            
        # Create sample deal
        deal_id = str(uuid4())
        self.deals[deal_id] = Deal(
            id=deal_id,
            companyName="TechFlow Industries",
            revenue="2800000",
            sde="950000",
            valuationMin="8500000",
            valuationMax="12000000",
            sdeMultiple="10.5",
            revenueMultiple="3.8",
            commission="3.5",
            stage="valuation",
            priority="high",
            description="B2B payment processing with AI fraud detection",
            notes="Strong team, recurring revenue model",
            nextStepDays=3,
            touches=12,
            ageInStage=14,
            healthScore=55,
            owner="Jennifer Walsh",
            createdAt=datetime.utcnow(),
        )
        
        # Create sample contact
        contact_id = str(uuid4())
        self.contacts[contact_id] = Contact(
            id=contact_id,
            name="John Mitchell",
            role="Owner",
            email="john@techflow.com",
            phone="555-0101",
            entityId=deal_id,
            entityType="deal",
        )
        
        # Create sample buying party
        party_id = str(uuid4())
        self.buying_parties[party_id] = BuyingParty(
            id=party_id,
            name="TechCorp Industries",
            targetAcquisitionMin=60,
            targetAcquisitionMax=80,
            budgetMin="5000000",
            budgetMax="15000000",
            timeline="Q2 2024",
            status="evaluating",
            notes="Strategic buyer",
            createdAt=datetime.utcnow(),
        )
        
        # Create sample match
        match_id = str(uuid4())
        self.matches[match_id] = DealBuyerMatch(
            id=match_id,
            dealId=deal_id,
            buyingPartyId=party_id,
            targetAcquisition=70,
            budget="8000000",
            status="interested",
            createdAt=datetime.utcnow(),
        )
        
        # Create sample activity
        activity_id = str(uuid4())
        self.activities[activity_id] = Activity(
            id=activity_id,
            dealId=deal_id,
            type="task",
            title="Follow-up on financial questions",
            description="Send email to CFO requesting clarification on Q4 numbers",
            status="completed",
            assignedTo="Jennifer Walsh",
            createdAt=datetime.utcnow(),
        )
        
        # Create sample document
        doc_id = str(uuid4())
        self.documents[doc_id] = Document(
            id=doc_id,
            dealId=deal_id,
            name="Financial Statements 2023",
            status="signed",
            url=None,
            createdAt=datetime.utcnow(),
        )
    
    # Deals
    async def get_deals(self) -> List[Deal]:
        return list(self.deals.values())
    
    async def get_deal(self, deal_id: str) -> Optional[Deal]:
        return self.deals.get(deal_id)
    
    async def create_deal(self, deal: DealCreate) -> Deal:
        deal_id = str(uuid4())
        new_deal = Deal(id=deal_id, createdAt=datetime.utcnow(), **deal.model_dump())
        self.deals[deal_id] = new_deal
        return new_deal
    
    async def update_deal(self, deal_id: str, updates: DealUpdate) -> Optional[Deal]:
        if deal_id not in self.deals:
            return None
        deal = self.deals[deal_id]
        data = deal.model_dump()
        for k, v in updates.model_dump(exclude_unset=True).items():
            data[k] = v
        updated = Deal(**data)
        self.deals[deal_id] = updated
        return updated
    
    async def delete_deal(self, deal_id: str) -> bool:
        if deal_id in self.deals:
            del self.deals[deal_id]
            return True
        return False
    
    async def update_deal_notes(self, deal_id: str, notes: str) -> Optional[Deal]:
        if deal_id not in self.deals:
            return None
        deal = self.deals[deal_id]
        updated = deal.model_copy(update={"notes": notes})
        self.deals[deal_id] = updated
        return updated
    
    # Contacts
    async def get_contacts(self) -> List[Contact]:
        return list(self.contacts.values())
    
    async def get_contacts_by_entity(self, entity_id: str, entity_type: str) -> List[Contact]:
        return [c for c in self.contacts.values() if c.entityId == entity_id and c.entityType == entity_type]
    
    async def create_contact(self, contact: ContactCreate) -> Contact:
        contact_id = str(uuid4())
        new_contact = Contact(id=contact_id, **contact.model_dump())
        self.contacts[contact_id] = new_contact
        return new_contact
    
    async def delete_contact(self, contact_id: str) -> bool:
        if contact_id in self.contacts:
            del self.contacts[contact_id]
            return True
        return False
    
    # Buying Parties
    async def get_buying_parties(self) -> List[BuyingParty]:
        return list(self.buying_parties.values())
    
    async def get_buying_party(self, party_id: str) -> Optional[BuyingParty]:
        return self.buying_parties.get(party_id)
    
    async def create_buying_party(self, party: BuyingPartyCreate) -> BuyingParty:
        party_id = str(uuid4())
        new_party = BuyingParty(id=party_id, createdAt=datetime.utcnow(), **party.model_dump())
        self.buying_parties[party_id] = new_party
        return new_party
    
    async def update_buying_party(self, party_id: str, updates: BuyingPartyUpdate) -> Optional[BuyingParty]:
        if party_id not in self.buying_parties:
            return None
        party = self.buying_parties[party_id]
        data = party.model_dump()
        for k, v in updates.model_dump(exclude_unset=True).items():
            data[k] = v
        updated = BuyingParty(**data)
        self.buying_parties[party_id] = updated
        return updated
    
    async def delete_buying_party(self, party_id: str) -> bool:
        if party_id in self.buying_parties:
            del self.buying_parties[party_id]
            return True
        return False
    
    async def update_buying_party_notes(self, party_id: str, notes: str) -> Optional[BuyingParty]:
        if party_id not in self.buying_parties:
            return None
        party = self.buying_parties[party_id]
        updated = party.model_copy(update={"notes": notes})
        self.buying_parties[party_id] = updated
        return updated
    
    # Deal-Buyer Matches
    async def get_deal_buyer_matches(self, deal_id: str) -> List[DealBuyerMatch]:
        return [m for m in self.matches.values() if m.dealId == deal_id]
    
    async def get_buying_party_matches(self, party_id: str) -> List[DealBuyerMatch]:
        return [m for m in self.matches.values() if m.buyingPartyId == party_id]
    
    async def create_deal_buyer_match(self, match: MatchCreate) -> DealBuyerMatch:
        match_id = str(uuid4())
        new_match = DealBuyerMatch(id=match_id, createdAt=datetime.utcnow(), **match.model_dump())
        self.matches[match_id] = new_match
        return new_match
    
    async def delete_deal_buyer_match(self, match_id: str) -> bool:
        if match_id in self.matches:
            del self.matches[match_id]
            return True
        return False
    
    # Activities
    async def get_activities(self) -> List[Activity]:
        return list(self.activities.values())
    
    async def get_activities_by_entity(self, entity_id: str) -> List[Activity]:
        return [a for a in self.activities.values() if a.dealId == entity_id or a.buyingPartyId == entity_id]
    
    async def create_activity(self, activity: ActivityCreate) -> Activity:
        activity_id = str(uuid4())
        new_activity = Activity(id=activity_id, createdAt=datetime.utcnow(), **activity.model_dump())
        self.activities[activity_id] = new_activity
        return new_activity
    
    async def update_activity(self, activity_id: str, updates: ActivityUpdate) -> Optional[Activity]:
        if activity_id not in self.activities:
            return None
        activity = self.activities[activity_id]
        data = activity.model_dump()
        for k, v in updates.model_dump(exclude_unset=True).items():
            data[k] = v
        updated = Activity(**data)
        self.activities[activity_id] = updated
        return updated
    
    async def delete_activity(self, activity_id: str) -> bool:
        if activity_id in self.activities:
            del self.activities[activity_id]
            return True
        return False
    
    # Documents
    async def get_documents(self) -> List[Document]:
        return list(self.documents.values())
    
    async def get_documents_by_entity(self, entity_id: str) -> List[Document]:
        return [d for d in self.documents.values() if d.dealId == entity_id or d.buyingPartyId == entity_id]
    
    async def create_document(self, document: DocumentCreate) -> Document:
        doc_id = str(uuid4())
        new_doc = Document(id=doc_id, createdAt=datetime.utcnow(), **document.model_dump())
        self.documents[doc_id] = new_doc
        return new_doc
    
    async def delete_document(self, document_id: str) -> bool:
        if document_id in self.documents:
            del self.documents[document_id]
            return True
        return False
    
    # Agreements (not supported in memory storage)
    async def get_buyers_with_signed_nda(self, deal_id: str) -> List[BuyingParty]:
        """Get buying parties that have signed NDAs - not supported in memory storage"""
        return []

# Create storage instance
storage = MemoryStorage()
