from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Body
from datetime import datetime
import os
import traceback
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from marshmallow import ValidationError

# Import marshmallow schemas
from api.schemas import (
    DealResponseSchema, DealCreateSchema, DealUpdateSchema, NotesUpdateSchema,
    ContactResponseSchema, ContactCreateSchema,
    BuyingPartyResponseSchema, BuyingPartyCreateSchema, BuyingPartyUpdateSchema,
    DealBuyerMatchResponseSchema, MatchCreateSchema,
    ActivityResponseSchema, ActivityCreateSchema, ActivityUpdateSchema,
    DocumentResponseSchema, DocumentCreateSchema,
    BuyerRowSchema, PartyMatchRowSchema, MeetingSummarySchema
)

# Load environment variables
load_dotenv()

# Storage selection with lazy initialization
def get_storage():
    """Get storage instance with proper initialization"""
    # Try local PostgreSQL
    try:
        from api.storage import Storage
        storage = Storage()
        print("🗄️  Using local PostgreSQL storage")
        return storage
    except Exception as e:
        print(f"⚠️  Local PostgreSQL failed: {e}")
        traceback.print_exc()  # Print full traceback to stderr
        print("💾 Falling back to in-memory storage")   
        from api.memory_storage import MemoryStorage
        return MemoryStorage()

# Initialize storage
storage = get_storage()

router = APIRouter()


# Routes — Deals
@router.get("/deals")
async def list_deals():
    deals = await storage.get_deals()
    return [DealResponseSchema().dump(deal) for deal in deals]


@router.get("/deals/{deal_id}")
async def get_deal(deal_id: str):
    deal = await storage.get_deal(deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return DealResponseSchema().dump(deal)


@router.post("/deals", status_code=201)
async def create_deal(payload: Dict[str, Any] = Body(...)):
    try:
        validated = DealCreateSchema().load(payload)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.messages)
    deal = await storage.create_deal(validated)
    return DealResponseSchema().dump(deal)


@router.patch("/deals/{deal_id}")
async def update_deal(deal_id: str, payload: Dict[str, Any] = Body(...)):
    try:
        validated = DealUpdateSchema().load(payload)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.messages)
    deal = await storage.update_deal(deal_id, validated)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return DealResponseSchema().dump(deal)


@router.delete("/deals/{deal_id}", status_code=204)
async def delete_deal(deal_id: str):
    success = await storage.delete_deal(deal_id)
    if not success:
        raise HTTPException(status_code=404, detail="Deal not found")


@router.patch("/deals/{deal_id}/notes")
async def update_deal_notes(deal_id: str, payload: Dict[str, Any] = Body(...)):
    try:
        validated = NotesUpdateSchema().load(payload)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.messages)
    deal = await storage.update_deal_notes(deal_id, validated["notes"])
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return DealResponseSchema().dump(deal)


# Composite: buyers for a deal
@router.get("/deals/{deal_id}/buyers")
async def deal_buyers(deal_id: str):
    # Get matches for this deal
    matches = await storage.get_deal_buyer_matches(deal_id)
    rows = []
    
    for match in matches:
        # Get the buying party
        party = await storage.get_buying_party(match["buying_party_id"])
        if not party:
            continue
            
        # Get the first contact for this party
        contacts = await storage.get_contacts_by_entity(party["id"], "buying_party")
        contact = contacts[0] if contacts else None
        
        row = {
            "match": match,
            "party": party,
            "contact": contact
        }
        rows.append(BuyerRowSchema().dump(row))
    
    return rows


@router.get("/deals/{deal_id}/buyers-with-nda")
async def deal_buyers_with_signed_nda(deal_id: str):
    """Get buying parties that have signed NDAs for this deal"""
    parties = await storage.get_buyers_with_signed_nda(deal_id)
    return [BuyingPartyResponseSchema().dump(party) for party in parties]


# Contacts
@router.get("/contacts")
async def list_contacts(entity_id: Optional[str] = Query(None), entity_type: Optional[str] = Query(None)):
    if entity_id and entity_type:
        contacts = await storage.get_contacts_by_entity(entity_id, entity_type)
    else:
        contacts = await storage.get_contacts()
    return [ContactResponseSchema().dump(contact) for contact in contacts]


@router.post("/contacts", status_code=201)
async def create_contact(payload: Dict[str, Any] = Body(...)):
    try:
        validated = ContactCreateSchema().load(payload)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.messages)
    contact = await storage.create_contact(validated)
    return ContactResponseSchema().dump(contact)


@router.delete("/contacts/{contact_id}", status_code=204)
async def delete_contact(contact_id: str):
    success = await storage.delete_contact(contact_id)
    if not success:
        raise HTTPException(status_code=404, detail="Contact not found")


# Buying Parties
@router.get("/buying-parties")
async def list_buying_parties():
    parties = await storage.get_buying_parties()
    return [BuyingPartyResponseSchema().dump(party) for party in parties]


@router.get("/buying-parties/{party_id}")
async def get_buying_party(party_id: str):
    party = await storage.get_buying_party(party_id)
    if not party:
        raise HTTPException(status_code=404, detail="Buying party not found")
    return BuyingPartyResponseSchema().dump(party)


@router.post("/buying-parties", status_code=201)
async def create_buying_party(payload: Dict[str, Any] = Body(...)):
    try:
        validated = BuyingPartyCreateSchema().load(payload)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.messages)
    party = await storage.create_buying_party(validated)
    return BuyingPartyResponseSchema().dump(party)


@router.patch("/buying-parties/{party_id}")
async def update_buying_party(party_id: str, payload: Dict[str, Any] = Body(...)):
    try:
        validated = BuyingPartyUpdateSchema().load(payload)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.messages)
    party = await storage.update_buying_party(party_id, validated)
    if not party:
        raise HTTPException(status_code=404, detail="Buying party not found")
    return BuyingPartyResponseSchema().dump(party)


@router.delete("/buying-parties/{party_id}", status_code=204)
async def delete_buying_party(party_id: str):
    success = await storage.delete_buying_party(party_id)
    if not success:
        raise HTTPException(status_code=404, detail="Buying party not found")


@router.patch("/buying-parties/{party_id}/notes")
async def update_party_notes(party_id: str, payload: Dict[str, Any] = Body(...)):
    try:
        validated = NotesUpdateSchema().load(payload)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.messages)
    party = await storage.update_buying_party_notes(party_id, validated["notes"])
    if not party:
        raise HTTPException(status_code=404, detail="Buying party not found")
    return BuyingPartyResponseSchema().dump(party)


# Composite: deals for a buying party (matches)
@router.get("/buying-parties/{party_id}/matches")
async def party_matches(party_id: str):
    # Get matches for this buying party
    matches = await storage.get_buying_party_matches(party_id)
    rows = []
    
    for match in matches:
        # Get the deal
        deal = await storage.get_deal(match["deal_id"])
        if not deal:
            continue
        
        row = {
            "match": match,
            "deal": deal
        }
        rows.append(PartyMatchRowSchema().dump(row))
    
    return rows


# Activities
@router.get("/activities")
async def list_activities(entity_id: Optional[str] = Query(None)):
    if entity_id:
        activities = await storage.get_activities_by_entity(entity_id)
    else:
        activities = await storage.get_activities()
    return [ActivityResponseSchema().dump(activity) for activity in activities]


@router.post("/activities", status_code=201)
async def create_activity(payload: Dict[str, Any] = Body(...)):
    try:
        validated = ActivityCreateSchema().load(payload)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.messages)
    activity = await storage.create_activity(validated)
    return ActivityResponseSchema().dump(activity)


@router.patch("/activities/{activity_id}")
async def update_activity(activity_id: str, payload: Dict[str, Any] = Body(...)):
    try:
        validated = ActivityUpdateSchema().load(payload)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.messages)
    activity = await storage.update_activity(activity_id, validated)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return ActivityResponseSchema().dump(activity)


@router.delete("/activities/{activity_id}", status_code=204)
async def delete_activity(activity_id: str):
    success = await storage.delete_activity(activity_id)
    if not success:
        raise HTTPException(status_code=404, detail="Activity not found")


# Documents
@router.get("/documents")
async def list_documents(entity_id: Optional[str] = Query(None)):
    if entity_id:
        documents = await storage.get_documents_by_entity(entity_id)
    else:
        documents = await storage.get_documents()
    return [DocumentResponseSchema().dump(document) for document in documents]


@router.post("/documents", status_code=201)
async def create_document(payload: Dict[str, Any] = Body(...)):
    try:
        validated = DocumentCreateSchema().load(payload)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.messages)
    document = await storage.create_document(validated)
    return DocumentResponseSchema().dump(document)


@router.delete("/documents/{document_id}", status_code=204)
async def delete_document(document_id: str):
    success = await storage.delete_document(document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")


# Matches
@router.post("/deal-buyer-matches", status_code=201)
async def create_match(payload: Dict[str, Any] = Body(...)):
    try:
        validated = MatchCreateSchema().load(payload)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.messages)
    match = await storage.create_deal_buyer_match(validated)
    return DealBuyerMatchResponseSchema().dump(match)


@router.delete("/deal-buyer-matches/{match_id}", status_code=204)
async def delete_match(match_id: str):
    success = await storage.delete_deal_buyer_match(match_id)
    if not success:
        raise HTTPException(status_code=404, detail="Match not found")


# Meetings (latest summary) — stub for UI
@router.get("/meetings/latest-summary")
async def latest_summary(deal_id: str = Query(...)):
    # For now, return None; can be wired to external integrations later
    return None


