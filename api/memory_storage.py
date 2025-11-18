"""
In-memory storage fallback for when Supabase is not available
"""

from typing import List, Optional, Dict, Any
from uuid import uuid4
from datetime import datetime

# Import password hashing function
try:
    from api.auth import get_password_hash
except ImportError:
    # Fallback if auth module not available
    def get_password_hash(password: str) -> str:
        # Simple fallback - in production this should use proper hashing
        return f"hashed_{password}"

class MemoryStorage:
    """In-memory storage implementation"""
    
    def __init__(self):
        self.deals = {}
        self.contacts = {}
        self.buying_parties = {}
        self.matches = {}
        self.activities = {}
        self.documents = {}
        self.users = {}
        self._seed_data()
    
    def _seed_data(self):
        """Seed with sample data"""
        # Seed users first (if not already seeded)
        if not self.users:
            self._seed_users()
        
        # Only seed other data if deals don't exist
        if self.deals:
            return
            
        # Create sample deal
        deal_id = str(uuid4())
        self.deals[deal_id] = {
            "id": deal_id,
            "company_name": "TechFlow Industries",
            "revenue": "2800000",
            "sde": "950000",
            "valuation_min": "8500000",
            "valuation_max": "12000000",
            "sde_multiple": "10.5",
            "revenue_multiple": "3.8",
            "commission": "3.5",
            "stage": "valuation",
            "priority": "high",
            "description": "B2B payment processing with AI fraud detection",
            "notes": "Strong team, recurring revenue model",
            "next_step_days": 3,
            "touches": 12,
            "age_in_stage": 14,
            "health_score": 55,
            "owner": "Jennifer Walsh",
            "created_at": datetime.utcnow(),
        }
        
        # Create sample contact
        contact_id = str(uuid4())
        self.contacts[contact_id] = {
            "id": contact_id,
            "name": "John Mitchell",
            "role": "Owner",
            "email": "john@techflow.com",
            "phone": "555-0101",
            "entity_id": deal_id,
            "entity_type": "deal",
        }
        
        # Create sample buying party
        party_id = str(uuid4())
        self.buying_parties[party_id] = {
            "id": party_id,
            "name": "TechCorp Industries",
            "target_acquisition_min": 60,
            "target_acquisition_max": 80,
            "budget_min": "5000000",
            "budget_max": "15000000",
            "timeline": "Q2 2024",
            "status": "evaluating",
            "notes": "Strategic buyer",
            "created_at": datetime.utcnow(),
        }
        
        # Create sample match
        match_id = str(uuid4())
        self.matches[match_id] = {
            "id": match_id,
            "deal_id": deal_id,
            "buying_party_id": party_id,
            "target_acquisition": 70,
            "budget": "8000000",
            "status": "interested",
            "created_at": datetime.utcnow(),
        }
        
        # Create sample activity
        activity_id = str(uuid4())
        self.activities[activity_id] = {
            "id": activity_id,
            "deal_id": deal_id,
            "buying_party_id": None,
            "type": "task",
            "title": "Follow-up on financial questions",
            "description": "Send email to CFO requesting clarification on Q4 numbers",
            "status": "completed",
            "assigned_to": "Jennifer Walsh",
            "due_date": None,
            "completed_at": None,
            "created_at": datetime.utcnow(),
        }
        
        # Create sample document
        doc_id = str(uuid4())
        self.documents[doc_id] = {
            "id": doc_id,
            "deal_id": deal_id,
            "buying_party_id": None,
            "name": "Financial Statements 2023",
            "status": "signed",
            "doc_type": None,
            "created_at": datetime.utcnow(),
        }
    
    def _seed_users(self):
        """Seed sample users for testing"""
        now = datetime.utcnow()
        
        # User 1: Admin user
        user1_id = str(uuid4())
        self.users[user1_id] = {
            "id": user1_id,
            "email": "admin@dealdeck.com",
            "encrypted_password": get_password_hash("admin123"),
            "recovery_token": None,
            "recovery_sent_at": None,
            "email_confirmed_at": now,
            "created_at": now,
            "updated_at": now
        }
        
        # User 2: Regular user
        user2_id = str(uuid4())
        self.users[user2_id] = {
            "id": user2_id,
            "email": "jennifer.walsh@dealdeck.com",
            "encrypted_password": get_password_hash("password123"),
            "recovery_token": None,
            "recovery_sent_at": None,
            "email_confirmed_at": now,
            "created_at": now,
            "updated_at": now
        }
        
        # User 3: Test user
        user3_id = str(uuid4())
        self.users[user3_id] = {
            "id": user3_id,
            "email": "test@dealdeck.com",
            "encrypted_password": get_password_hash("test123"),
            "recovery_token": None,
            "recovery_sent_at": None,
            "email_confirmed_at": None,  # Not confirmed yet
            "created_at": now,
            "updated_at": now
        }
    
    # Deals
    async def get_deals(self) -> List[Dict[str, Any]]:
        return list(self.deals.values())
    
    async def get_deal(self, deal_id: str) -> Optional[Dict[str, Any]]:
        return self.deals.get(deal_id)
    
    async def create_deal(self, deal: Dict[str, Any]) -> Dict[str, Any]:
        deal_id = str(uuid4())
        new_deal = {"id": deal_id, "created_at": datetime.utcnow(), **deal}
        self.deals[deal_id] = new_deal
        return new_deal
    
    async def update_deal(self, deal_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if deal_id not in self.deals:
            return None
        deal = self.deals[deal_id].copy()
        for k, v in updates.items():
            if v is not None:
                deal[k] = v
        self.deals[deal_id] = deal
        return deal
    
    async def delete_deal(self, deal_id: str) -> bool:
        if deal_id in self.deals:
            del self.deals[deal_id]
            return True
        return False
    
    async def update_deal_notes(self, deal_id: str, notes: str) -> Optional[Dict[str, Any]]:
        if deal_id not in self.deals:
            return None
        deal = self.deals[deal_id].copy()
        deal["notes"] = notes
        self.deals[deal_id] = deal
        return deal
    
    # Contacts
    async def get_contacts(self) -> List[Dict[str, Any]]:
        return list(self.contacts.values())
    
    async def get_contacts_by_entity(self, entity_id: str, entity_type: str) -> List[Dict[str, Any]]:
        return [c for c in self.contacts.values() if c["entity_id"] == entity_id and c["entity_type"] == entity_type]
    
    async def create_contact(self, contact: Dict[str, Any]) -> Dict[str, Any]:
        contact_id = str(uuid4())
        new_contact = {"id": contact_id, **contact}
        self.contacts[contact_id] = new_contact
        return new_contact
    
    async def delete_contact(self, contact_id: str) -> bool:
        if contact_id in self.contacts:
            del self.contacts[contact_id]
            return True
        return False
    
    # Buying Parties
    async def get_buying_parties(self) -> List[Dict[str, Any]]:
        parties = list(self.buying_parties.values())
        # Add contacts to each party
        for party in parties:
            party_contacts = [
                {k: v for k, v in c.items() if k not in ["entity_id", "entity_type"]}
                for c in self.contacts.values()
                if c.get("entity_id") == party["id"] and c.get("entity_type") == "buying_party"
            ]
            party["contacts"] = party_contacts
        return parties
    
    async def get_buying_party(self, party_id: str) -> Optional[Dict[str, Any]]:
        return self.buying_parties.get(party_id)
    
    async def create_buying_party(self, party: Dict[str, Any]) -> Dict[str, Any]:
        party_id = str(uuid4())
        new_party = {"id": party_id, "created_at": datetime.utcnow(), **party}
        self.buying_parties[party_id] = new_party
        return new_party
    
    async def update_buying_party(self, party_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if party_id not in self.buying_parties:
            return None
        party = self.buying_parties[party_id].copy()
        for k, v in updates.items():
            if v is not None:
                party[k] = v
        self.buying_parties[party_id] = party
        return party
    
    async def delete_buying_party(self, party_id: str) -> bool:
        if party_id in self.buying_parties:
            del self.buying_parties[party_id]
            return True
        return False
    
    async def update_buying_party_notes(self, party_id: str, notes: str) -> Optional[Dict[str, Any]]:
        if party_id not in self.buying_parties:
            return None
        party = self.buying_parties[party_id].copy()
        party["notes"] = notes
        self.buying_parties[party_id] = party
        return party
    
    # Deal-Buyer Matches
    async def get_deal_buyer_matches(self, deal_id: str) -> List[Dict[str, Any]]:
        return [m for m in self.matches.values() if m["deal_id"] == deal_id]
    
    async def get_buying_party_matches(self, party_id: str) -> List[Dict[str, Any]]:
        return [m for m in self.matches.values() if m["buying_party_id"] == party_id]
    
    async def create_deal_buyer_match(self, match: Dict[str, Any]) -> Dict[str, Any]:
        match_id = str(uuid4())
        new_match = {"id": match_id, "created_at": datetime.utcnow(), **match}
        self.matches[match_id] = new_match
        return new_match
    
    async def delete_deal_buyer_match(self, match_id: str) -> bool:
        if match_id in self.matches:
            del self.matches[match_id]
            return True
        return False
    
    # Activities
    async def get_activities(self) -> List[Dict[str, Any]]:
        return list(self.activities.values())
    
    async def get_activities_by_entity(self, entity_id: str) -> List[Dict[str, Any]]:
        return [a for a in self.activities.values() if a.get("deal_id") == entity_id or a.get("buying_party_id") == entity_id]
    
    async def create_activity(self, activity: Dict[str, Any]) -> Dict[str, Any]:
        activity_id = str(uuid4())
        new_activity = {"id": activity_id, "created_at": datetime.utcnow(), **activity}
        self.activities[activity_id] = new_activity
        return new_activity
    
    async def update_activity(self, activity_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if activity_id not in self.activities:
            return None
        activity = self.activities[activity_id].copy()
        for k, v in updates.items():
            if v is not None:
                activity[k] = v
        self.activities[activity_id] = activity
        return activity
    
    async def delete_activity(self, activity_id: str) -> bool:
        if activity_id in self.activities:
            del self.activities[activity_id]
            return True
        return False
    
    # Documents
    async def get_documents(self) -> List[Dict[str, Any]]:
        return list(self.documents.values())
    
    async def get_documents_by_entity(self, entity_id: str) -> List[Dict[str, Any]]:
        # Documents are only linked to deals, not buying parties
        return [d for d in self.documents.values() if d.get("deal_id") == entity_id]
    
    async def create_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        doc_id = str(uuid4())
        new_doc = {"id": doc_id, "created_at": datetime.utcnow(), **document}
        self.documents[doc_id] = new_doc
        return new_doc
    
    async def delete_document(self, document_id: str) -> bool:
        if document_id in self.documents:
            del self.documents[document_id]
            return True
        return False
    
    # Agreements (not supported in memory storage)
    async def get_buyers_with_signed_nda(self, deal_id: str) -> List[Dict[str, Any]]:
        """Get buying parties that have signed NDAs - not supported in memory storage"""
        return []

    # User authentication methods
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        for user in self.users.values():
            if user.get("email") == email:
                return user
        return None

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        return self.users.get(user_id)

    async def get_user_by_recovery_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Get user by recovery token"""
        for user in self.users.values():
            if user.get("recovery_token") == token:
                return user
        return None

    async def create_user(self, email: str, hashed_password: str) -> Dict[str, Any]:
        """Create a new user"""
        user_id = str(uuid4())
        now = datetime.utcnow()
        user = {
            "id": user_id,
            "email": email,
            "encrypted_password": hashed_password,
            "recovery_token": None,
            "recovery_sent_at": None,
            "email_confirmed_at": None,
            "created_at": now,
            "updated_at": now
        }
        self.users[user_id] = user
        return user

    async def update_user_password(self, user_id: str, hashed_password: str) -> bool:
        """Update user password"""
        if user_id not in self.users:
            return False
        user = self.users[user_id].copy()
        user["encrypted_password"] = hashed_password
        user["recovery_token"] = None
        user["recovery_sent_at"] = None
        user["updated_at"] = datetime.utcnow()
        self.users[user_id] = user
        return True

    async def set_recovery_token(self, user_id: str, token: str) -> bool:
        """Set recovery token for password reset"""
        if user_id not in self.users:
            return False
        user = self.users[user_id].copy()
        user["recovery_token"] = token
        user["recovery_sent_at"] = datetime.utcnow()
        user["updated_at"] = datetime.utcnow()
        self.users[user_id] = user
        return True

# Create storage instance
storage = MemoryStorage()
