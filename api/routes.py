from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime
import os
from dotenv import load_dotenv

# Import all models from api.models to avoid type mismatches
from .models import (
    Deal, Contact, BuyingParty, DealBuyerMatch, Activity, Document,
    DealCreate, DealUpdate, ContactCreate, BuyingPartyCreate, BuyingPartyUpdate,
    ActivityCreate, ActivityUpdate, DocumentCreate, MatchCreate
)

# Load environment variables
load_dotenv()

# Storage selection with lazy initialization
def get_storage():
    """Get storage instance with proper initialization"""
    if os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_SERVICE_ROLE_KEY"):
        try:
            from .simple_supabase_storage import SimpleSupabaseStorage
            storage = SimpleSupabaseStorage()
            print("🔗 Using Supabase storage")
            return storage
        except Exception as e:
            print(f"⚠️  Supabase failed: {e}")
            print("💾 Falling back to in-memory storage")
            from .memory_storage import MemoryStorage
            return MemoryStorage()
    else:
        from .memory_storage import MemoryStorage
        print("💾 Using in-memory storage (no Supabase credentials)")
        return MemoryStorage()

# Initialize storage
storage = get_storage()

router = APIRouter()


# NotesUpdate model for PATCH endpoint
class NotesUpdate(BaseModel):
    notes: str = Field(min_length=0)


# Routes — Deals
@router.get("/deals", response_model=List[Deal])
async def list_deals():
    return await storage.get_deals()


@router.get("/deals/{deal_id}", response_model=Deal)
async def get_deal(deal_id: str):
    deal = await storage.get_deal(deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal


@router.post("/deals", response_model=Deal, status_code=201)
async def create_deal(payload: DealCreate):
    return await storage.create_deal(payload)


@router.patch("/deals/{deal_id}", response_model=Deal)
async def update_deal(deal_id: str, payload: DealUpdate):
    deal = await storage.update_deal(deal_id, payload)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal


@router.delete("/deals/{deal_id}", status_code=204)
async def delete_deal(deal_id: str):
    success = await storage.delete_deal(deal_id)
    if not success:
        raise HTTPException(status_code=404, detail="Deal not found")


@router.patch("/deals/{deal_id}/notes", response_model=Deal)
async def update_deal_notes(deal_id: str, payload: NotesUpdate):
    deal = await storage.update_deal_notes(deal_id, payload.notes)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal


# Composite: buyers for a deal
class BuyerRow(BaseModel):
    match: DealBuyerMatch
    party: BuyingParty
    contact: Optional[Contact] = None


@router.get("/deals/{deal_id}/buyers", response_model=List[BuyerRow])
async def deal_buyers(deal_id: str):
    # Get matches for this deal
    matches = await storage.get_deal_buyer_matches(deal_id)
    rows: List[BuyerRow] = []
    
    for match in matches:
        # Get the buying party
        party = await storage.get_buying_party(match.buyingPartyId)
        if not party:
            continue
            
        # Get the first contact for this party
        contacts = await storage.get_contacts_by_entity(party.id, "buying_party")
        contact = contacts[0] if contacts else None
        
        rows.append(BuyerRow(match=match, party=party, contact=contact))
    
    return rows


@router.get("/deals/{deal_id}/buyers-with-nda", response_model=List[BuyingParty])
async def deal_buyers_with_signed_nda(deal_id: str):
    """Get buying parties that have signed NDAs for this deal"""
    return await storage.get_buyers_with_signed_nda(deal_id)


# Contacts
@router.get("/contacts", response_model=List[Contact])
async def list_contacts(entityId: Optional[str] = Query(None), entityType: Optional[str] = Query(None)):
    if entityId and entityType:
        return await storage.get_contacts_by_entity(entityId, entityType)
    return await storage.get_contacts()


@router.post("/contacts", response_model=Contact, status_code=201)
async def create_contact(payload: ContactCreate):
    return await storage.create_contact(payload)


@router.delete("/contacts/{contact_id}", status_code=204)
async def delete_contact(contact_id: str):
    success = await storage.delete_contact(contact_id)
    if not success:
        raise HTTPException(status_code=404, detail="Contact not found")


# Buying Parties
@router.get("/buying-parties", response_model=List[BuyingParty])
async def list_buying_parties():
    return await storage.get_buying_parties()


@router.get("/buying-parties/{party_id}", response_model=BuyingParty)
async def get_buying_party(party_id: str):
    party = await storage.get_buying_party(party_id)
    if not party:
        raise HTTPException(status_code=404, detail="Buying party not found")
    return party


@router.post("/buying-parties", response_model=BuyingParty, status_code=201)
async def create_buying_party(payload: BuyingPartyCreate):
    return await storage.create_buying_party(payload)


@router.patch("/buying-parties/{party_id}", response_model=BuyingParty)
async def update_buying_party(party_id: str, payload: BuyingPartyUpdate):
    party = await storage.update_buying_party(party_id, payload)
    if not party:
        raise HTTPException(status_code=404, detail="Buying party not found")
    return party


@router.delete("/buying-parties/{party_id}", status_code=204)
async def delete_buying_party(party_id: str):
    success = await storage.delete_buying_party(party_id)
    if not success:
        raise HTTPException(status_code=404, detail="Buying party not found")


@router.patch("/buying-parties/{party_id}/notes", response_model=BuyingParty)
async def update_party_notes(party_id: str, payload: NotesUpdate):
    party = await storage.update_buying_party_notes(party_id, payload.notes)
    if not party:
        raise HTTPException(status_code=404, detail="Buying party not found")
    return party


# Composite: deals for a buying party (matches)
class PartyMatchRow(BaseModel):
    match: DealBuyerMatch
    deal: Deal


@router.get("/buying-parties/{party_id}/matches", response_model=List[PartyMatchRow])
async def party_matches(party_id: str):
    # Get matches for this buying party
    matches = await storage.get_buying_party_matches(party_id)
    rows: List[PartyMatchRow] = []
    
    for match in matches:
        # Get the deal
        deal = await storage.get_deal(match.dealId)
        if not deal:
            continue
        
        rows.append(PartyMatchRow(match=match, deal=deal))
    
    return rows


# Activities
@router.get("/activities", response_model=List[Activity])
async def list_activities(entityId: Optional[str] = Query(None)):
    if entityId:
        return await storage.get_activities_by_entity(entityId)
    return await storage.get_activities()


@router.post("/activities", response_model=Activity, status_code=201)
async def create_activity(payload: ActivityCreate):
    return await storage.create_activity(payload)


@router.patch("/activities/{activity_id}", response_model=Activity)
async def update_activity(activity_id: str, payload: ActivityUpdate):
    activity = await storage.update_activity(activity_id, payload)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity


@router.delete("/activities/{activity_id}", status_code=204)
async def delete_activity(activity_id: str):
    success = await storage.delete_activity(activity_id)
    if not success:
        raise HTTPException(status_code=404, detail="Activity not found")


# Documents
@router.get("/documents", response_model=List[Document])
async def list_documents(entityId: Optional[str] = Query(None)):
    if entityId:
        return await storage.get_documents_by_entity(entityId)
    return await storage.get_documents()


@router.post("/documents", response_model=Document, status_code=201)
async def create_document(payload: DocumentCreate):
    return await storage.create_document(payload)


@router.delete("/documents/{document_id}", status_code=204)
async def delete_document(document_id: str):
    success = await storage.delete_document(document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")


# Matches
@router.post("/deal-buyer-matches", response_model=DealBuyerMatch, status_code=201)
async def create_match(payload: MatchCreate):
    return await storage.create_deal_buyer_match(payload)


@router.delete("/deal-buyer-matches/{match_id}", status_code=204)
async def delete_match(match_id: str):
    success = await storage.delete_deal_buyer_match(match_id)
    if not success:
        raise HTTPException(status_code=404, detail="Match not found")


# Meetings (latest summary) — stub for UI
class MeetingSummary(BaseModel):
    summary: str
    createdAt: datetime
    source: Optional[str] = None


@router.get("/meetings/latest-summary", response_model=Optional[MeetingSummary])
def latest_summary(dealId: str = Query(...)):
    # For now, return None; can be wired to external integrations later
    return None


