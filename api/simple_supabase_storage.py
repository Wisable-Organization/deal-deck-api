"""
Simple Supabase storage implementation using direct HTTP requests
Avoids dependency conflicts by not using the full Supabase client
"""

import os
import httpx
from typing import List, Optional
from .models import (
    Deal, Contact, BuyingParty, DealBuyerMatch, Activity, Document, Agreement,
    DealCreate, DealUpdate, NotesUpdate, ContactCreate, BuyingPartyCreate,
    BuyingPartyUpdate, ActivityCreate, ActivityUpdate, DocumentCreate, MatchCreate
)

class SimpleSupabaseStorage:
    """Simple Supabase storage using direct HTTP requests"""
    
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        self.client = httpx.AsyncClient()
    
    async def _request(self, method: str, endpoint: str, data=None):
        """Make HTTP request to Supabase"""
        url = f"{self.url}/rest/v1/{endpoint}"
        try:
            response = await self.client.request(method, url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Supabase request failed: {e}")
            raise
    
    # Deals
    async def get_deals(self) -> List[Deal]:
        data = await self._request("GET", "deals")
        deals = []
        for row in data:
            # Get company name from companies table
            company_data = await self._request("GET", f"companies?id=eq.{row.get('company_id')}")
            company_name = company_data[0].get("name") if company_data else "Unknown Company"
            
            # Get revenue from company_metrics
            revenue_data = await self._request(
                "GET", 
                f"company_metrics?company_id=eq.{row.get('company_id')}&type=eq.Revenue&order=fiscal_year.desc&limit=1"
            )
            revenue = revenue_data[0].get("value") if revenue_data else None
            
            # Convert database field names to our model field names
            deal_data = {
                "id": row.get("id"),
                "companyName": company_name,
                "revenue": str(revenue) if revenue else "",
                "sde": str(row.get("sde", "")) if row.get("sde") else None,
                "valuationMin": str(row.get("valuation_min", "")) if row.get("valuation_min") else None,
                "valuationMax": str(row.get("valuation_max", "")) if row.get("valuation_max") else None,
                "sdeMultiple": str(row.get("sde_multiple", "")) if row.get("sde_multiple") else None,
                "revenueMultiple": str(row.get("revenue_multiple", "")) if row.get("revenue_multiple") else None,
                "commission": str(row.get("commission", "")) if row.get("commission") else None,
                "stage": row.get("stage", ""),
                "priority": row.get("priority", "medium"),
                "description": row.get("description"),
                "notes": row.get("notes"),
                "nextStepDays": row.get("next_step_days"),
                "touches": row.get("touches", 0),
                "ageInStage": row.get("age_in_stage", 0),
                "healthScore": row.get("health_score", 85),
                "owner": row.get("owner", ""),
                "createdAt": row.get("created_at")
            }
            deals.append(Deal(**deal_data))
        return deals
    
    async def get_deal(self, deal_id: str) -> Optional[Deal]:
        data = await self._request("GET", f"deals?id=eq.{deal_id}")
        if data:
            row = data[0]
            
            # Get company name from companies table
            company_data = await self._request("GET", f"companies?id=eq.{row.get('company_id')}")
            company_name = company_data[0].get("name") if company_data else "Unknown Company"
            
            # Get revenue from company_metrics
            revenue_data = await self._request(
                "GET", 
                f"company_metrics?company_id=eq.{row.get('company_id')}&type=eq.Revenue&order=fiscal_year.desc&limit=1"
            )
            revenue = revenue_data[0].get("value") if revenue_data else None
            
            deal_data = {
                "id": row.get("id"),
                "companyName": company_name,
                "revenue": str(revenue) if revenue else "",
                "sde": str(row.get("sde", "")) if row.get("sde") else None,
                "valuationMin": str(row.get("valuation_min", "")) if row.get("valuation_min") else None,
                "valuationMax": str(row.get("valuation_max", "")) if row.get("valuation_max") else None,
                "sdeMultiple": str(row.get("sde_multiple", "")) if row.get("sde_multiple") else None,
                "revenueMultiple": str(row.get("revenue_multiple", "")) if row.get("revenue_multiple") else None,
                "commission": str(row.get("commission", "")) if row.get("commission") else None,
                "stage": row.get("stage", ""),
                "priority": row.get("priority", "medium"),
                "description": row.get("description"),
                "notes": row.get("notes"),
                "nextStepDays": row.get("next_step_days"),
                "touches": row.get("touches", 0),
                "ageInStage": row.get("age_in_stage", 0),
                "healthScore": row.get("health_score", 85),
                "owner": row.get("owner", ""),
                "createdAt": row.get("created_at")
            }
            return Deal(**deal_data)
        return None
    
    async def create_deal(self, deal: DealCreate) -> Deal:
        # Convert field names to database format
        deal_data = deal.model_dump()
        db_data = {
            "company_id": deal_data.get("companyId"),
            "sde": deal_data.get("sde"),
            "valuation_min": deal_data.get("valuationMin"),
            "valuation_max": deal_data.get("valuationMax"),
            "sde_multiple": deal_data.get("sdeMultiple"),
            "revenue_multiple": deal_data.get("revenueMultiple"),
            "commission": deal_data.get("commission"),
            "stage": deal_data.get("stage"),
            "priority": deal_data.get("priority"),
            "description": deal_data.get("description"),
            "notes": deal_data.get("notes"),
            "next_step_days": deal_data.get("nextStepDays"),
            "touches": deal_data.get("touches", 0),
            "age_in_stage": deal_data.get("ageInStage", 0),
            "health_score": deal_data.get("healthScore", 85),
            "owner": deal_data.get("owner")
        }
        data = await self._request("POST", "deals", db_data)
        # Convert back to our format
        row = data[0]
        return Deal(
            id=row.get("id"),
            companyName=row.get("company_name"),
            revenue=str(row.get("revenue", "")),
            sde=str(row.get("sde", "")) if row.get("sde") else None,
            valuationMin=str(row.get("valuation_min", "")) if row.get("valuation_min") else None,
            valuationMax=str(row.get("valuation_max", "")) if row.get("valuation_max") else None,
            sdeMultiple=str(row.get("sde_multiple", "")) if row.get("sde_multiple") else None,
            revenueMultiple=str(row.get("revenue_multiple", "")) if row.get("revenue_multiple") else None,
            commission=str(row.get("commission", "")) if row.get("commission") else None,
            stage=row.get("stage", ""),
            priority=row.get("priority", "medium"),
            description=row.get("description"),
            notes=row.get("notes"),
            nextStepDays=row.get("next_step_days"),
            touches=row.get("touches", 0),
            ageInStage=row.get("age_in_stage", 0),
            healthScore=row.get("health_score", 85),
            owner=row.get("owner", ""),
            createdAt=row.get("created_at")
        )
    
    async def update_deal(self, deal_id: str, updates: DealUpdate) -> Optional[Deal]:
        # Convert field names to database format
        update_data = updates.model_dump(exclude_unset=True)
        db_data = {}
        for key, value in update_data.items():
            if key == "companyId":
                db_data["company_id"] = value
            elif key == "valuationMin":
                db_data["valuation_min"] = value
            elif key == "valuationMax":
                db_data["valuation_max"] = value
            elif key == "sdeMultiple":
                db_data["sde_multiple"] = value
            elif key == "revenueMultiple":
                db_data["revenue_multiple"] = value
            elif key == "nextStepDays":
                db_data["next_step_days"] = value
            elif key == "ageInStage":
                db_data["age_in_stage"] = value
            elif key == "healthScore":
                db_data["health_score"] = value
            elif key == "stage":
                db_data["stage"] = value
            elif key == "priority":
                db_data["priority"] = value
            elif key == "owner":
                db_data["owner"] = value
            elif key == "description":
                db_data["description"] = value
            elif key == "notes":
                db_data["notes"] = value
            elif key == "touches":
                db_data["touches"] = value
            else:
                db_data[key] = value
        
        data = await self._request("PATCH", f"deals?id=eq.{deal_id}", db_data)
        if data:
            # Convert back to our format
            row = data[0]
            
            # Get company name from companies table
            company_data = await self._request("GET", f"companies?id=eq.{row.get('company_id')}")
            company_name = company_data[0].get("name") if company_data else "Unknown Company"
            
            # Get revenue from company_metrics
            revenue_data = await self._request(
                "GET", 
                f"company_metrics?company_id=eq.{row.get('company_id')}&type=eq.Revenue&order=fiscal_year.desc&limit=1"
            )
            revenue = revenue_data[0].get("value") if revenue_data else None
            
            deal_data = {
                "id": row.get("id"),
                "companyName": company_name,
                "revenue": str(revenue) if revenue else "",
                "sde": str(row.get("sde", "")) if row.get("sde") else None,
                "valuationMin": str(row.get("valuation_min", "")) if row.get("valuation_min") else None,
                "valuationMax": str(row.get("valuation_max", "")) if row.get("valuation_max") else None,
                "sdeMultiple": str(row.get("sde_multiple", "")) if row.get("sde_multiple") else None,
                "revenueMultiple": str(row.get("revenue_multiple", "")) if row.get("revenue_multiple") else None,
                "commission": str(row.get("commission", "")) if row.get("commission") else None,
                "stage": row.get("stage", ""),
                "priority": row.get("priority", "medium"),
                "description": row.get("description"),
                "notes": row.get("notes"),
                "nextStepDays": row.get("next_step_days"),
                "touches": row.get("touches", 0),
                "ageInStage": row.get("age_in_stage", 0),
                "healthScore": row.get("health_score", 85),
                "owner": row.get("owner", ""),
                "createdAt": row.get("created_at")
            }
            return Deal(**deal_data)
        return None
    
    async def delete_deal(self, deal_id: str) -> bool:
        try:
            await self._request("DELETE", f"deals?id=eq.{deal_id}")
            return True
        except:
            return False
    
    async def update_deal_notes(self, deal_id: str, notes: str) -> Optional[Deal]:
        data = await self._request("PATCH", f"deals?id=eq.{deal_id}", {"notes": notes})
        if data:
            row = data[0]
            deal_data = {
                "id": row.get("id"),
                "companyName": row.get("company_name"),
                "revenue": str(row.get("revenue", "")),
                "sde": str(row.get("sde", "")) if row.get("sde") else None,
                "valuationMin": str(row.get("valuation_min", "")) if row.get("valuation_min") else None,
                "valuationMax": str(row.get("valuation_max", "")) if row.get("valuation_max") else None,
                "sdeMultiple": str(row.get("sde_multiple", "")) if row.get("sde_multiple") else None,
                "revenueMultiple": str(row.get("revenue_multiple", "")) if row.get("revenue_multiple") else None,
                "commission": str(row.get("commission", "")) if row.get("commission") else None,
                "stage": row.get("stage", ""),
                "priority": row.get("priority", "medium"),
                "description": row.get("description"),
                "notes": row.get("notes"),
                "nextStepDays": row.get("next_step_days"),
                "touches": row.get("touches", 0),
                "ageInStage": row.get("age_in_stage", 0),
                "healthScore": row.get("health_score", 85),
                "owner": row.get("owner", ""),
                "createdAt": row.get("created_at")
            }
            return Deal(**deal_data)
        return None
    
    # Contacts
    async def get_contacts(self) -> List[Contact]:
        data = await self._request("GET", "contacts")
        contacts = []
        for row in data:
            contact_data = {
                "id": row.get("id"),
                "name": row.get("name"),
                "role": row.get("role"),
                "email": row.get("email"),
                "phone": row.get("phone"),
                "entityId": row.get("entity_id"),
                "entityType": row.get("entity_type")
            }
            contacts.append(Contact(**contact_data))
        return contacts
    
    async def get_contacts_by_entity(self, entity_id: str, entity_type: str) -> List[Contact]:
        if entity_type == "deal":
            # For deals, get the company_id first, then get contacts from companies_contacts
            deal_data = await self._request("GET", f"deals?id=eq.{entity_id}")
            if not deal_data:
                return []
            
            company_id = deal_data[0].get("company_id")
            if not company_id:
                return []
            
            # Get contacts through companies_contacts junction table
            data = await self._request(
                "GET", 
                f"companies_contacts?company_id=eq.{company_id}&select=contact_id,contact_role,is_primary,created_at,contacts(*)"
            )
            contacts = []
            for row in data:
                contact_data = row.get("contacts")
                if contact_data:
                    contact = Contact(
                        id=contact_data.get("id"),
                        name=contact_data.get("name"),
                        role=row.get("contact_role"),
                        email=contact_data.get("email"),
                        phone=contact_data.get("phone"),
                        entityId=entity_id,
                        entityType="deal"
                    )
                    contacts.append(contact)
            return contacts
        else:
            # For other entity types, use the original logic
            data = await self._request("GET", f"contacts?entity_id=eq.{entity_id}&entity_type=eq.{entity_type}")
            contacts = []
            for row in data:
                contact_data = {
                    "id": row.get("id"),
                    "name": row.get("name"),
                    "role": row.get("role"),
                    "email": row.get("email"),
                    "phone": row.get("phone"),
                    "entityId": row.get("entity_id"),
                    "entityType": row.get("entity_type")
                }
                contacts.append(Contact(**contact_data))
            return contacts
    
    async def create_contact(self, contact: ContactCreate) -> Contact:
        # Convert field names to database format
        contact_data = contact.model_dump()
        db_data = {
            "name": contact_data.get("name"),
            "role": contact_data.get("role"),
            "email": contact_data.get("email"),
            "phone": contact_data.get("phone"),
            "entity_id": contact_data.get("entityId"),
            "entity_type": contact_data.get("entityType")
        }
        data = await self._request("POST", "contacts", db_data)
        # Convert back to our format
        row = data[0]
        return Contact(
            id=row.get("id"),
            name=row.get("name"),
            role=row.get("role"),
            email=row.get("email"),
            phone=row.get("phone"),
            entityId=row.get("entity_id"),
            entityType=row.get("entity_type")
        )
    
    async def delete_contact(self, contact_id: str) -> bool:
        try:
            await self._request("DELETE", f"contacts?id=eq.{contact_id}")
            return True
        except:
            return False
    
    # Buying Parties
    async def get_buying_parties(self) -> List[BuyingParty]:
        data = await self._request("GET", "buying_parties")
        parties = []
        for row in data:
            party_data = {
                "id": row.get("id"),
                "name": row.get("name"),
                "targetAcquisitionMin": row.get("target_acquisition_min"),
                "targetAcquisitionMax": row.get("target_acquisition_max"),
                "budgetMin": str(row.get("budget_min", "")) if row.get("budget_min") else None,
                "budgetMax": str(row.get("budget_max", "")) if row.get("budget_max") else None,
                "timeline": row.get("timeline"),
                "status": row.get("status"),
                "notes": row.get("notes"),
                "createdAt": row.get("created_at")
            }
            parties.append(BuyingParty(**party_data))
        return parties
    
    async def get_buying_party(self, party_id: str) -> Optional[BuyingParty]:
        data = await self._request("GET", f"buying_parties?id=eq.{party_id}")
        if data:
            row = data[0]
            party_data = {
                "id": row.get("id"),
                "name": row.get("name"),
                "targetAcquisitionMin": row.get("target_acquisition_min"),
                "targetAcquisitionMax": row.get("target_acquisition_max"),
                "budgetMin": str(row.get("budget_min", "")) if row.get("budget_min") else None,
                "budgetMax": str(row.get("budget_max", "")) if row.get("budget_max") else None,
                "timeline": row.get("timeline"),
                "status": row.get("status"),
                "notes": row.get("notes"),
                "createdAt": row.get("created_at")
            }
            return BuyingParty(**party_data)
        return None
    
    async def create_buying_party(self, party: BuyingPartyCreate) -> BuyingParty:
        # Convert field names to database format
        party_data = party.model_dump()
        db_data = {
            "name": party_data.get("name"),
            "target_acquisition_min": party_data.get("targetAcquisitionMin"),
            "target_acquisition_max": party_data.get("targetAcquisitionMax"),
            "budget_min": party_data.get("budgetMin"),
            "budget_max": party_data.get("budgetMax"),
            "timeline": party_data.get("timeline"),
            "status": party_data.get("status"),
            "notes": party_data.get("notes")
        }
        data = await self._request("POST", "buying_parties", db_data)
        # Convert back to our format
        row = data[0]
        return BuyingParty(
            id=row.get("id"),
            name=row.get("name"),
            targetAcquisitionMin=row.get("target_acquisition_min"),
            targetAcquisitionMax=row.get("target_acquisition_max"),
            budgetMin=str(row.get("budget_min", "")) if row.get("budget_min") else None,
            budgetMax=str(row.get("budget_max", "")) if row.get("budget_max") else None,
            timeline=row.get("timeline"),
            status=row.get("status"),
            notes=row.get("notes"),
            createdAt=row.get("created_at")
        )
    
    async def update_buying_party(self, party_id: str, updates: BuyingPartyUpdate) -> Optional[BuyingParty]:
        # Convert field names to database format
        update_data = updates.model_dump(exclude_unset=True)
        db_data = {}
        for key, value in update_data.items():
            if key == "targetAcquisitionMin":
                db_data["target_acquisition_min"] = value
            elif key == "targetAcquisitionMax":
                db_data["target_acquisition_max"] = value
            elif key == "budgetMin":
                db_data["budget_min"] = value
            elif key == "budgetMax":
                db_data["budget_max"] = value
            else:
                db_data[key] = value
        
        data = await self._request("PATCH", f"buying_parties?id=eq.{party_id}", db_data)
        if data:
            row = data[0]
            party_data = {
                "id": row.get("id"),
                "name": row.get("name"),
                "targetAcquisitionMin": row.get("target_acquisition_min"),
                "targetAcquisitionMax": row.get("target_acquisition_max"),
                "budgetMin": str(row.get("budget_min", "")) if row.get("budget_min") else None,
                "budgetMax": str(row.get("budget_max", "")) if row.get("budget_max") else None,
                "timeline": row.get("timeline"),
                "status": row.get("status"),
                "notes": row.get("notes"),
                "createdAt": row.get("created_at")
            }
            return BuyingParty(**party_data)
        return None
    
    async def delete_buying_party(self, party_id: str) -> bool:
        try:
            await self._request("DELETE", f"buying_parties?id=eq.{party_id}")
            return True
        except:
            return False
    
    async def update_buying_party_notes(self, party_id: str, notes: str) -> Optional[BuyingParty]:
        data = await self._request("PATCH", f"buying_parties?id=eq.{party_id}", {"notes": notes})
        if data:
            row = data[0]
            party_data = {
                "id": row.get("id"),
                "name": row.get("name"),
                "targetAcquisitionMin": row.get("target_acquisition_min"),
                "targetAcquisitionMax": row.get("target_acquisition_max"),
                "budgetMin": str(row.get("budget_min", "")) if row.get("budget_min") else None,
                "budgetMax": str(row.get("budget_max", "")) if row.get("budget_max") else None,
                "timeline": row.get("timeline"),
                "status": row.get("status"),
                "notes": row.get("notes"),
                "createdAt": row.get("created_at")
            }
            return BuyingParty(**party_data)
        return None
    
    # Deal-Buyer Matches
    async def get_deal_buyer_matches(self, deal_id: str) -> List[DealBuyerMatch]:
        data = await self._request("GET", f"deal_buyer_matches?deal_id=eq.{deal_id}")
        matches = []
        for row in data:
            match_data = {
                "id": row.get("id"),
                "dealId": row.get("deal_id"),
                "buyingPartyId": row.get("buying_party_id"),
                "targetAcquisition": row.get("target_acquisition"),
                "budget": str(row.get("budget", "")) if row.get("budget") else None,
                "status": row.get("status"),
                "createdAt": row.get("created_at")
            }
            matches.append(DealBuyerMatch(**match_data))
        return matches
    
    async def get_buying_party_matches(self, party_id: str) -> List[DealBuyerMatch]:
        data = await self._request("GET", f"deal_buyer_matches?buying_party_id=eq.{party_id}")
        matches = []
        for row in data:
            match_data = {
                "id": row.get("id"),
                "dealId": row.get("deal_id"),
                "buyingPartyId": row.get("buying_party_id"),
                "targetAcquisition": row.get("target_acquisition"),
                "budget": str(row.get("budget", "")) if row.get("budget") else None,
                "status": row.get("status"),
                "createdAt": row.get("created_at")
            }
            matches.append(DealBuyerMatch(**match_data))
        return matches
    
    async def create_deal_buyer_match(self, match: MatchCreate) -> DealBuyerMatch:
        # Convert field names to database format
        match_data = match.model_dump()
        db_data = {
            "deal_id": match_data.get("dealId"),
            "buying_party_id": match_data.get("buyingPartyId"),
            "target_acquisition": match_data.get("targetAcquisition"),
            "budget": match_data.get("budget"),
            "status": match_data.get("status")
        }
        data = await self._request("POST", "deal_buyer_matches", db_data)
        # Convert back to our format
        row = data[0]
        return DealBuyerMatch(
            id=row.get("id"),
            dealId=row.get("deal_id"),
            buyingPartyId=row.get("buying_party_id"),
            targetAcquisition=row.get("target_acquisition"),
            budget=str(row.get("budget", "")) if row.get("budget") else None,
            status=row.get("status"),
            createdAt=row.get("created_at")
        )
    
    async def delete_deal_buyer_match(self, match_id: str) -> bool:
        try:
            await self._request("DELETE", f"deal_buyer_matches?id=eq.{match_id}")
            return True
        except:
            return False
    
    # Activities
    async def get_activities(self) -> List[Activity]:
        data = await self._request("GET", "activities")
        activities = []
        for row in data:
            activity_data = {
                "id": row.get("id"),
                "dealId": row.get("deal_id"),
                "buyingPartyId": row.get("buying_party_id"),
                "type": row.get("type"),
                "title": row.get("title"),
                "description": row.get("description"),
                "status": row.get("status"),
                "assignedTo": row.get("assigned_to"),
                "dueDate": row.get("due_date"),
                "completedAt": row.get("completed_at"),
                "createdAt": row.get("created_at")
            }
            activities.append(Activity(**activity_data))
        return activities
    
    async def get_activities_by_entity(self, entity_id: str) -> List[Activity]:
        data = await self._request("GET", f"activities?or=(deal_id.eq.{entity_id},buying_party_id.eq.{entity_id})")
        activities = []
        for row in data:
            activity_data = {
                "id": row.get("id"),
                "dealId": row.get("deal_id"),
                "buyingPartyId": row.get("buying_party_id"),
                "type": row.get("type"),
                "title": row.get("title"),
                "description": row.get("description"),
                "status": row.get("status"),
                "assignedTo": row.get("assigned_to"),
                "dueDate": row.get("due_date"),
                "completedAt": row.get("completed_at"),
                "createdAt": row.get("created_at")
            }
            activities.append(Activity(**activity_data))
        return activities
    
    async def create_activity(self, activity: ActivityCreate) -> Activity:
        # Convert field names to database format
        activity_data = activity.model_dump()
        db_data = {
            "deal_id": activity_data.get("dealId") or activity_data.get("entityId"),
            "buying_party_id": activity_data.get("buyingPartyId"),
            "type": activity_data.get("type"),
            "title": activity_data.get("title"),
            "description": activity_data.get("description"),
            "status": activity_data.get("status"),
            "assigned_to": activity_data.get("assignedTo"),
            "due_date": activity_data.get("dueDate")
        }
        data = await self._request("POST", "activities", db_data)
        # Convert back to our format
        row = data[0]
        return Activity(
            id=row.get("id"),
            dealId=row.get("deal_id"),
            buyingPartyId=row.get("buying_party_id"),
            type=row.get("type"),
            title=row.get("title"),
            description=row.get("description"),
            status=row.get("status"),
            assignedTo=row.get("assigned_to"),
            dueDate=row.get("due_date"),
            completedAt=row.get("completed_at"),
            createdAt=row.get("created_at")
        )
    
    async def update_activity(self, activity_id: str, updates: ActivityUpdate) -> Optional[Activity]:
        # Convert field names to database format
        update_data = updates.model_dump(exclude_unset=True)
        db_data = {}
        for key, value in update_data.items():
            if key == "dealId":
                db_data["deal_id"] = value
            elif key == "buyingPartyId":
                db_data["buying_party_id"] = value
            elif key == "assignedTo":
                db_data["assigned_to"] = value
            elif key == "dueDate":
                db_data["due_date"] = value
            elif key == "completedAt":
                db_data["completed_at"] = value
            else:
                db_data[key] = value
        
        data = await self._request("PATCH", f"activities?id=eq.{activity_id}", db_data)
        if data:
            row = data[0]
            activity_data = {
                "id": row.get("id"),
                "dealId": row.get("deal_id"),
                "buyingPartyId": row.get("buying_party_id"),
                "type": row.get("type"),
                "title": row.get("title"),
                "description": row.get("description"),
                "status": row.get("status"),
                "assignedTo": row.get("assigned_to"),
                "dueDate": row.get("due_date"),
                "completedAt": row.get("completed_at"),
                "createdAt": row.get("created_at")
            }
            return Activity(**activity_data)
        return None
    
    async def delete_activity(self, activity_id: str) -> bool:
        try:
            await self._request("DELETE", f"activities?id=eq.{activity_id}")
            return True
        except:
            return False
    
    # Documents
    async def get_documents(self) -> List[Document]:
        data = await self._request("GET", "documents")
        documents = []
        for row in data:
            doc_data = {
                "id": row.get("id"),
                "dealId": row.get("deal_id"),
                "buyingPartyId": row.get("buying_party_id"),
                "name": row.get("name"),
                "status": row.get("status"),
                "url": row.get("url"),
                "createdAt": row.get("created_at")
            }
            documents.append(Document(**doc_data))
        return documents
    
    async def get_documents_by_entity(self, entity_id: str) -> List[Document]:
        data = await self._request("GET", f"documents?or=(deal_id.eq.{entity_id},buying_party_id.eq.{entity_id})")
        documents = []
        for row in data:
            doc_data = {
                "id": row.get("id"),
                "dealId": row.get("deal_id"),
                "buyingPartyId": row.get("buying_party_id"),
                "name": row.get("name"),
                "status": row.get("status"),
                "url": row.get("url"),
                "createdAt": row.get("created_at")
            }
            documents.append(Document(**doc_data))
        return documents
    
    async def create_document(self, document: DocumentCreate) -> Document:
        # Convert field names to database format
        doc_data = document.model_dump()
        db_data = {
            "deal_id": doc_data.get("dealId"),
            "buying_party_id": doc_data.get("buyingPartyId"),
            "name": doc_data.get("name"),
            "status": doc_data.get("status"),
            "url": doc_data.get("url")
        }
        data = await self._request("POST", "documents", db_data)
        row = data[0]
        return Document(
            id=row.get("id"),
            dealId=row.get("deal_id"),
            buyingPartyId=row.get("buying_party_id"),
            name=row.get("name"),
            status=row.get("status"),
            url=row.get("url"),
            createdAt=row.get("created_at")
        )
    
    async def delete_document(self, document_id: str) -> bool:
        try:
            await self._request("DELETE", f"documents?id=eq.{document_id}")
            return True
        except:
            return False
    
    # Agreements
    async def get_agreements(self, deal_id: str) -> List[Agreement]:
        data = await self._request("GET", f"agreements?deal_id=eq.{deal_id}")
        agreements = []
        for row in data:
            agreement = Agreement(
                id=row.get("id"),
                dealId=row.get("deal_id"),
                buyingPartyId=row.get("buying_party_id"),
                type=row.get("type"),
                status=row.get("status"),
                provider=row.get("provider"),
                providerEnvelopeId=row.get("provider_envelope_id"),
                sentAt=row.get("sent_at"),
                viewedAt=row.get("viewed_at"),
                signedAt=row.get("signed_at"),
                expiresAt=row.get("expires_at"),
                amount=row.get("amount"),
                documentId=row.get("document_id"),
                notes=row.get("notes"),
                createdAt=row.get("created_at")
            )
            agreements.append(agreement)
        return agreements
    
    async def get_buyers_with_signed_nda(self, deal_id: str) -> List[BuyingParty]:
        """Get buying parties that have signed NDAs for this deal"""
        # Get agreements with type='nda' and status='signed' for this deal
        data = await self._request(
            "GET",
            f"agreements?deal_id=eq.{deal_id}&type=ilike.nda&status=ilike.signed&select=buying_party_id"
        )
        
        # Get unique buying party IDs
        party_ids = list(set([row.get("buying_party_id") for row in data if row.get("buying_party_id")]))
        
        # Fetch the buying parties
        parties = []
        for party_id in party_ids:
            party = await self.get_buying_party(party_id)
            if party:
                parties.append(party)
        
        return parties

# Create storage instance
storage = SimpleSupabaseStorage()
