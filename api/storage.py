"""
Local PostgreSQL storage implementation using SQLAlchemy
Connects directly to the local PostgreSQL database
"""

import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import create_engine, select, func, or_
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy.pool import NullPool
from api.models import (
    Base, Company, CompanyMetric, Deal, Contact,
    BuyingParty, DealBuyerMatch,
    Activity, Document, CompanyContact, User
)


class Storage:
    """Local PostgreSQL storage using SQLAlchemy"""

    def __init__(self):
        # Get connection string from environment or use default local connection
        use_supabase = os.getenv("USE_SUPABASE", "false") == "true"
        print(f"USE_SUPABASE: {os.getenv('USE_SUPABASE', 'not caught')}")
        print(f"DATABASE_URL: {os.getenv('DATABASE_URL', 'not caught')}")
        db_url = os.getenv("DATABASE_URL") if not use_supabase else os.getenv("SUPABASE_DATABASE_URL")
        self.engine = create_engine(db_url, poolclass=NullPool)
        self.Session = sessionmaker(bind=self.engine)
        print(f"🗄️  Connected to {"Supabase" if use_supabase else "local PostgreSQL"}: deal-deck")
    def _get_company_id(self, company_name: str):
        """Get or create a company and return its ID"""
        with self.Session() as session:
            # Check if company exists
            company = session.scalar(
                select(Company).where(Company.name == company_name).limit(1)
            )
            
            if company:
                return company.id
            
            # Create company
            company = Company(
                name=company_name,
                created_at=datetime.utcnow()
            )
            session.add(company)
            session.commit()
            session.refresh(company)
            return company.id

    def _deal_instance_to_dict(self, deal_instance: Deal, company_name: str = None, revenue: float = None) -> Dict[str, Any]:
        """Convert  Deal object to dict"""
        return {
            "id": str(deal_instance.id),
            "company_name": company_name or "Unknown Company",
            "revenue": str(revenue) if revenue else "",
            "sde": str(deal_instance.sde) if deal_instance.sde else None,
            "valuation_min": str(deal_instance.valuation_min) if deal_instance.valuation_min else None,
            "valuation_max": str(deal_instance.valuation_max) if deal_instance.valuation_max else None,
            "sde_multiple": str(deal_instance.sde_multiple) if deal_instance.sde_multiple else None,
            "revenue_multiple": str(deal_instance.revenue_multiple) if deal_instance.revenue_multiple else None,
            "commission": str(deal_instance.commission) if deal_instance.commission else None,
            "stage": deal_instance.stage or "",
            "priority": deal_instance.priority or "medium",
            "description": deal_instance.description,
            "notes": deal_instance.notes,
            "next_step_days": deal_instance.next_step_days,
            "touches": deal_instance.touches or 0,
            "age_in_stage": deal_instance.age_in_stage or 0,
            "health_score": deal_instance.health_score or 85,
            "owner": deal_instance.owner or "",
            "created_at": deal_instance.created_at or datetime.utcnow()
        }

    # Deals
    async def get_deals(self) -> List[Dict[str, Any]]:
        with self.Session() as session:
            # Get deals with company and latest revenue metric
            deals = session.scalars(
                select(Deal)
                .options(joinedload(Deal.company))
                .order_by(Deal.created_at.desc())
            ).all()
            
            result = []
            for deal in deals:
                # Get latest revenue metric for the company
                revenue_metric = session.scalar(
                    select(CompanyMetric.value)
                    .where(
                        CompanyMetric.company_id == deal.company_id,
                        CompanyMetric.type == 'Revenue'
                    )
                    .order_by(CompanyMetric.fiscal_year.desc().nulls_last())
                    .limit(1)
                )
                revenue = float(revenue_metric) if revenue_metric else 0.0
                company_name = deal.company.name if deal.company else "Unknown Company"
                result.append(self._deal_instance_to_dict(deal, company_name, revenue))
            
            return result

    async def get_deal(self, deal_id: str) -> Optional[Dict[str, Any]]:
        with self.Session() as session:
            deal = session.scalar(
                select(Deal)
                .options(joinedload(Deal.company))
                .where(Deal.id == deal_id)
            )
            
            if not deal:
                return None
            
            # Get latest revenue metric
            revenue_metric = session.scalar(
                select(CompanyMetric.value)
                .where(
                    CompanyMetric.company_id == deal.company_id,
                    CompanyMetric.type == 'Revenue'
                )
                .order_by(CompanyMetric.fiscal_year.desc().nulls_last())
                .limit(1)
            )
            revenue = float(revenue_metric) if revenue_metric else 0.0
            company_name = deal.company.name if deal.company else "Unknown Company"
            return self._deal_instance_to_dict(deal, company_name, revenue)

    async def create_deal(self, deal: Dict[str, Any]) -> Dict[str, Any]:
        company_id = self._get_company_id(deal["company_name"])
        
        with self.Session() as session:
            # Create company_metrics entry if revenue provided
            if deal.get("revenue"):
                # Check if metric already exists for this company and year
                current_year = datetime.utcnow().year
                existing = session.scalar(
                    select(CompanyMetric).where(
                        CompanyMetric.company_id == company_id,
                        CompanyMetric.type == 'Revenue',
                        CompanyMetric.fiscal_year == current_year
                    )
                )
                if not existing:
                    metric = CompanyMetric(
                        company_id=company_id,
                        type='Revenue',
                        value=float(deal["revenue"]),
                        fiscal_year=current_year,
                        created_at=datetime.utcnow()
                    )
                    session.add(metric)
            
            # Create the deal
            deal_instance = Deal(
                company_id=company_id,
                stage=deal["stage"],
                priority=deal.get("priority", "medium"),
                sde=float(deal["sde"]) if deal.get("sde") else None,
                valuation_min=float(deal["valuation_min"]) if deal.get("valuation_min") else None,
                valuation_max=float(deal["valuation_max"]) if deal.get("valuation_max") else None,
                sde_multiple=float(deal["sde_multiple"]) if deal.get("sde_multiple") else None,
                revenue_multiple=float(deal["revenue_multiple"]) if deal.get("revenue_multiple") else None,
                commission=float(deal["commission"]) if deal.get("commission") else None,
                description=deal.get("description"),
                notes=deal.get("notes"),
                next_step_days=deal.get("next_step_days"),
                touches=deal.get("touches", 0),
                age_in_stage=deal.get("age_in_stage", 0),
                health_score=deal.get("health_score", 85),
                owner=deal["owner"],
                created_at=datetime.utcnow()
            )
            session.add(deal_instance)
            session.commit()
            session.refresh(deal_instance)
            deal_id = str(deal_instance.id)
        
        return await self.get_deal(deal_id)

    async def update_deal(self, deal_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not updates:
            return await self.get_deal(deal_id)
        
        with self.Session() as session:
            deal = session.scalar(select(Deal).where(Deal.id == deal_id))
            if not deal:
                return None
            
            # Handle company name separately
            update_data = updates.copy()
            if "company_name" in update_data:
                deal.company_id = self._get_company_id(update_data["company_name"])
                del update_data["company_name"]
            
            # Map and update fields
            field_map = {
                "stage": "stage",
                "priority": "priority",
                "sde": ("sde", lambda v: float(v) if v else None),
                "valuation_min": ("valuation_min", lambda v: float(v) if v else None),
                "valuation_max": ("valuation_max", lambda v: float(v) if v else None),
                "sde_multiple": ("sde_multiple", lambda v: float(v) if v else None),
                "revenue_multiple": ("revenue_multiple", lambda v: float(v) if v else None),
                "commission": ("commission", lambda v: float(v) if v else None),
                "description": "description",
                "notes": "notes",
                "next_step_days": "next_step_days",
                "touches": "touches",
                "age_in_stage": "age_in_stage",
                "health_score": "health_score",
                "owner": "owner"
            }
            
            for key, value in update_data.items():
                if key in field_map:
                    mapping = field_map[key]
                    if isinstance(mapping, tuple):
                        db_key, transform = mapping
                        setattr(deal, db_key, transform(value))
                    else:
                        setattr(deal, mapping, value)
            
            session.commit()
            session.refresh(deal)
        
        return await self.get_deal(deal_id)

    async def delete_deal(self, deal_id: str) -> bool:
        with self.Session() as session:
            deal = session.scalar(select(Deal).where(Deal.id == deal_id))
            if not deal:
                return False
            session.delete(deal)
            session.commit()
            return True

    async def update_deal_notes(self, deal_id: str, notes: str) -> Optional[Dict[str, Any]]:
        with self.Session() as session:
            deal = session.scalar(select(Deal).where(Deal.id == deal_id))
            if not deal:
                return None
            deal.notes = notes
            session.commit()
        return await self.get_deal(deal_id)

    # Contacts
    async def get_contacts(self) -> List[Dict[str, Any]]:
        with self.Session() as session:
            contacts = session.scalars(select(Contact)).all()
            return [{
                "id": str(c.id), "name": c.name, "role": c.role,
                "email": c.email, "phone": c.phone,
                "entity_id": str(c.entity_id), "entity_type": c.entity_type
            } for c in contacts]

    async def get_contacts_by_entity(self, entity_id: str, entity_type: str) -> List[Dict[str, Any]]:
        with self.Session() as session:
            if entity_type == "deal":
                # Get contacts through company
                deal = session.scalar(
                    select(Deal)
                    .options(joinedload(Deal.company))
                    .where(Deal.id == entity_id)
                )
                if not deal or not deal.company:
                    return []
                
                # Get contacts via company_contacts
                company_contacts = session.scalars(
                    select(CompanyContact)
                    .where(CompanyContact.company_id == deal.company_id)
                    .options(joinedload(CompanyContact.contact))
                ).all()
                
                return [{
                    "id": str(cc.contact.id), "name": cc.contact.name, "role": cc.contact_role,
                    "email": cc.contact.email, "phone": cc.contact.phone,
                    "entity_id": entity_id, "entity_type": entity_type
                } for cc in company_contacts]
            else:
                contacts = session.scalars(
                    select(Contact).where(
                        Contact.entity_id == entity_id,
                        Contact.entity_type == entity_type
                    )
                ).all()
                return [{
                    "id": str(c.id), "name": c.name, "role": c.role,
                    "email": c.email, "phone": c.phone,
                    "entity_id": entity_id, "entity_type": entity_type
                } for c in contacts]

    async def create_contact(self, contact: Dict[str, Any]) -> Dict[str, Any]:
        with self.Session() as session:
            contact_instance = Contact(
                name=contact["name"],
                role=contact["role"],
                email=contact.get("email"),
                phone=contact.get("phone"),
                entity_id=contact["entity_id"],
                entity_type=contact["entity_type"],
                created_at=datetime.utcnow()
            )
            session.add(contact_instance)
            session.commit()
            session.refresh(contact_instance)
            return {
                "id": str(contact_instance.id), "name": contact["name"], "role": contact["role"],
                "email": contact.get("email"), "phone": contact.get("phone"),
                "entity_id": contact["entity_id"], "entity_type": contact["entity_type"]
            }

    async def delete_contact(self, contact_id: str) -> bool:
        with self.Session() as session:
            contact = session.scalar(select(Contact).where(Contact.id == contact_id))
            if not contact:
                return False
            session.delete(contact)
            session.commit()
            return True

    # Buying Parties
    async def get_buying_parties(self) -> List[Dict[str, Any]]:
        with self.Session() as session:
            parties = session.scalars(
                select(BuyingParty).order_by(BuyingParty.created_at.desc())
            ).all()
            return [{
                "id": str(p.id), "name": p.name,
                "target_acquisition_min": p.target_acquisition_min,
                "target_acquisition_max": p.target_acquisition_max,
                "budget_min": str(p.budget_min) if p.budget_min else None,
                "budget_max": str(p.budget_max) if p.budget_max else None,
                "timeline": p.timeline, "status": p.status, "notes": p.notes,
                "created_at": p.created_at
            } for p in parties]

    async def get_buying_party(self, party_id: str) -> Optional[Dict[str, Any]]:
        with self.Session() as session:
            party = session.scalar(select(BuyingParty).where(BuyingParty.id == party_id))
            if not party:
                return None
            return {
                "id": str(party.id), "name": party.name,
                "target_acquisition_min": party.target_acquisition_min,
                "target_acquisition_max": party.target_acquisition_max,
                "budget_min": str(party.budget_min) if party.budget_min else None,
                "budget_max": str(party.budget_max) if party.budget_max else None,
                "timeline": party.timeline, "status": party.status, "notes": party.notes,
                "created_at": party.created_at
            }

    async def create_buying_party(self, party: Dict[str, Any]) -> Dict[str, Any]:
        with self.Session() as session:
            party_instance = BuyingParty(
                name=party["name"],
                target_acquisition_min=party.get("target_acquisition_min"),
                target_acquisition_max=party.get("target_acquisition_max"),
                budget_min=float(party["budget_min"]) if party.get("budget_min") else None,
                budget_max=float(party["budget_max"]) if party.get("budget_max") else None,
                timeline=party.get("timeline"),
                status=party.get("status", "evaluating"),
                notes=party.get("notes"),
                created_at=datetime.utcnow()
            )
            session.add(party_instance)
            session.commit()
            session.refresh(party_instance)
            return await self.get_buying_party(str(party_instance.id))

    async def update_buying_party(self, party_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not updates:
            return await self.get_buying_party(party_id)
        
        with self.Session() as session:
            party = session.scalar(select(BuyingParty).where(BuyingParty.id == party_id))
            if not party:
                return None
            
            update_data = updates.copy()
            field_map = {
                "name": "name",
                "target_acquisition_min": "target_acquisition_min",
                "target_acquisition_max": "target_acquisition_max",
                "budget_min": ("budget_min", lambda v: float(v) if v else None),
                "budget_max": ("budget_max", lambda v: float(v) if v else None),
                "timeline": "timeline",
                "status": "status",
                "notes": "notes"
            }
            
            for key, value in update_data.items():
                if key in field_map:
                    mapping = field_map[key]
                    if isinstance(mapping, tuple):
                        db_key, transform = mapping
                        setattr(party, db_key, transform(value))
                    else:
                        setattr(party, mapping, value)
            
            session.commit()
            session.refresh(party)
        
        return await self.get_buying_party(party_id)

    async def delete_buying_party(self, party_id: str) -> bool:
        with self.Session() as session:
            party = session.scalar(select(BuyingParty).where(BuyingParty.id == party_id))
            if not party:
                return False
            session.delete(party)
            session.commit()
            return True

    async def update_buying_party_notes(self, party_id: str, notes: str) -> Optional[Dict[str, Any]]:
        with self.Session() as session:
            party = session.scalar(select(BuyingParty).where(BuyingParty.id == party_id))
            if not party:
                return None
            party.notes = notes
            session.commit()
        return await self.get_buying_party(party_id)

    # Deal-Buyer Matches
    async def get_deal_buyer_matches(self, deal_id: str) -> List[Dict[str, Any]]:
        with self.Session() as session:
            matches = session.scalars(
                select(DealBuyerMatch).where(DealBuyerMatch.deal_id == deal_id)
            ).all()
            return [{
                "id": str(m.id), "deal_id": str(m.deal_id),
                "buying_party_id": str(m.buying_party_id),
                "target_acquisition": m.target_acquisition,
                "budget": str(m.budget) if m.budget else None,
                "status": m.status, "created_at": m.created_at
            } for m in matches]

    async def get_buying_party_matches(self, party_id: str) -> List[Dict[str, Any]]:
        with self.Session() as session:
            matches = session.scalars(
                select(DealBuyerMatch).where(DealBuyerMatch.buying_party_id == party_id)
            ).all()
            return [{
                "id": str(m.id), "deal_id": str(m.deal_id),
                "buying_party_id": str(m.buying_party_id),
                "target_acquisition": m.target_acquisition,
                "budget": str(m.budget) if m.budget else None,
                "status": m.status, "created_at": m.created_at
            } for m in matches]

    async def create_deal_buyer_match(self, match: Dict[str, Any]) -> Dict[str, Any]:
        with self.Session() as session:
            match_instance = DealBuyerMatch(
                deal_id=match["deal_id"],
                buying_party_id=match["buying_party_id"],
                target_acquisition=match.get("target_acquisition"),
                budget=float(match["budget"]) if match.get("budget") else None,
                status=match.get("status", "interested"),
                created_at=datetime.utcnow()
            )
            session.add(match_instance)
            session.commit()
            session.refresh(match_instance)
            return {
                "id": str(match_instance.id), "deal_id": match["deal_id"], "buying_party_id": match["buying_party_id"],
                "target_acquisition": match.get("target_acquisition"), "budget": match.get("budget"),
                "status": match.get("status", "interested"), "created_at": match_instance.created_at
            }

    async def delete_deal_buyer_match(self, match_id: str) -> bool:
        with self.Session() as session:
            match = session.scalar(select(DealBuyerMatch).where(DealBuyerMatch.id == match_id))
            if not match:
                return False
            session.delete(match)
            session.commit()
            return True

    # Activities
    async def get_activities(self) -> List[Dict[str, Any]]:
        with self.Session() as session:
            activities = session.scalars(
                select(Activity).order_by(Activity.created_at.desc())
            ).all()
            return [{
                "id": str(a.id),
                "deal_id": str(a.deal_id) if a.deal_id else None,
                "buying_party_id": str(a.buying_party_id) if a.buying_party_id else None,
                "type": a.type, "title": a.title, "description": a.description,
                "status": a.status, "assigned_to": a.assigned_to,
                "due_date": a.due_date, "completed_at": a.completed_at,
                "created_at": a.created_at
            } for a in activities]

    async def get_activities_by_entity(self, entity_id: str) -> List[Dict[str, Any]]:
        with self.Session() as session:
            activities = session.scalars(
                select(Activity).where(
                    or_(
                        Activity.deal_id == entity_id,
                        Activity.buying_party_id == entity_id
                    )
                ).order_by(Activity.created_at.desc())
            ).all()
            return [{
                "id": str(a.id),
                "deal_id": str(a.deal_id) if a.deal_id else None,
                "buying_party_id": str(a.buying_party_id) if a.buying_party_id else None,
                "type": a.type, "title": a.title, "description": a.description,
                "status": a.status, "assigned_to": a.assigned_to,
                "due_date": a.due_date, "completed_at": a.completed_at,
                "created_at": a.created_at
            } for a in activities]

    async def create_activity(self, activity: Dict[str, Any]) -> Dict[str, Any]:
        with self.Session() as session:
            activity_instance = Activity(
                deal_id=activity.get("deal_id"),
                buying_party_id=activity.get("buying_party_id"),
                type=activity["type"],
                title=activity["title"],
                description=activity.get("description"),
                status=activity.get("status", "pending"),
                assigned_to=activity.get("assigned_to"),
                due_date=activity.get("due_date"),
                created_at=datetime.utcnow()
            )
            session.add(activity_instance)
            session.commit()
            session.refresh(activity_instance)
            return {
                "id": str(activity_instance.id), "deal_id": activity.get("deal_id"), "buying_party_id": activity.get("buying_party_id"),
                "type": activity["type"], "title": activity["title"], "description": activity.get("description"),
                "status": activity.get("status", "pending"), "assigned_to": activity.get("assigned_to"),
                "due_date": activity.get("due_date"), "completed_at": None, "created_at": activity_instance.created_at
            }

    async def update_activity(self, activity_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not updates:
            return await self._get_activity(activity_id)
        
        with self.Session() as session:
            activity = session.scalar(select(Activity).where(Activity.id == activity_id))
            if not activity:
                return None
            
            update_data = updates.copy()
            field_map = {
                "type": "type", "title": "title", "description": "description",
                "status": "status",                 "assigned_to": "assigned_to",
                "due_date": "due_date", "completed_at": "completed_at"
            }
            
            for key, value in update_data.items():
                if key in field_map:
                    setattr(activity, field_map[key], value)
            
            session.commit()
            session.refresh(activity)
        
        return await self._get_activity(activity_id)

    async def _get_activity(self, activity_id: str) -> Optional[Dict[str, Any]]:
        with self.Session() as session:
            activity = session.scalar(select(Activity).where(Activity.id == activity_id))
            if not activity:
                return None
            return {
                "id": str(activity.id),
                "deal_id": str(activity.deal_id) if activity.deal_id else None,
                "buying_party_id": str(activity.buying_party_id) if activity.buying_party_id else None,
                "type": activity.type, "title": activity.title, "description": activity.description,
                "status": activity.status, "assigned_to": activity.assigned_to,
                "due_date": activity.due_date, "completed_at": activity.completed_at,
                "created_at": activity.created_at
            }

    async def delete_activity(self, activity_id: str) -> bool:
        with self.Session() as session:
            activity = session.scalar(select(Activity).where(Activity.id == activity_id))
            if not activity:
                return False
            session.delete(activity)
            session.commit()
            return True

    # Documents
    async def get_documents(self) -> List[Dict[str, Any]]:
        with self.Session() as session:
            documents = session.scalars(
                select(Document).order_by(Document.created_at.desc())
            ).all()
            return [{
                "id": str(d.id),
                "deal_id": str(d.deal_id) if d.deal_id else None,
                "name": d.name, "status": d.status,
                "doc_type": d.doc_type, "created_at": d.created_at
            } for d in documents]

    async def get_documents_by_entity(self, entity_id: str) -> List[Dict[str, Any]]:
        with self.Session() as session:
            # Documents are only linked to deals, not buying parties
            documents = session.scalars(
                select(Document).where(
                    Document.deal_id == entity_id
                ).order_by(Document.created_at.desc())
            ).all()
            return [{
                "id": str(d.id),
                "deal_id": str(d.deal_id) if d.deal_id else None,
                "name": d.name, "status": d.status,
                "doc_type": d.doc_type, "created_at": d.created_at
            } for d in documents]

    async def create_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        with self.Session() as session:
            doc_instance = Document(
                deal_id=document.get("deal_id"),
                name=document["name"],
                status=document.get("status", "draft"),
                doc_type=document.get("doc_type"),
                created_at=datetime.utcnow()
            )
            session.add(doc_instance)
            session.commit()
            session.refresh(doc_instance)
            return {
                "id": str(doc_instance.id), "deal_id": document.get("deal_id"),
                "name": document["name"], "status": document.get("status", "draft"),
                "doc_type": document.get("doc_type"), "created_at": doc_instance.created_at
            }

    async def delete_document(self, document_id: str) -> bool:
        with self.Session() as session:
            document = session.scalar(select(Document).where(Document.id == document_id))
            if not document:
                return False
            session.delete(document)
            session.commit()
            return True

    # Agreements (not supported in local storage, return empty list)
    async def get_buyers_with_signed_nda(self, deal_id: str) -> List[Dict[str, Any]]:
        """Get buying parties that have signed NDAs - placeholder for local storage"""
        return []

    # User authentication methods
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        with self.Session() as session:
            user = session.scalar(select(User).where(User.email == email).limit(1))
            if not user:
                return None
            return {
                "id": str(user.id),
                "email": user.email,
                "encrypted_password": user.encrypted_password,
                "recovery_token": user.recovery_token,
                "recovery_sent_at": user.recovery_sent_at,
                "email_confirmed_at": user.email_confirmed_at,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            }

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        with self.Session() as session:
            user = session.scalar(select(User).where(User.id == user_id).limit(1))
            if not user:
                return None
            return {
                "id": str(user.id),
                "email": user.email,
                "encrypted_password": user.encrypted_password,
                "recovery_token": user.recovery_token,
                "recovery_sent_at": user.recovery_sent_at,
                "email_confirmed_at": user.email_confirmed_at,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            }

    async def get_user_by_recovery_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Get user by recovery token"""
        with self.Session() as session:
            user = session.scalar(select(User).where(User.recovery_token == token).limit(1))
            if not user:
                return None
            return {
                "id": str(user.id),
                "email": user.email,
                "encrypted_password": user.encrypted_password,
                "recovery_token": user.recovery_token,
                "recovery_sent_at": user.recovery_sent_at,
                "email_confirmed_at": user.email_confirmed_at,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            }

    async def create_user(self, email: str, hashed_password: str) -> Dict[str, Any]:
        """Create a new user"""
        import uuid
        with self.Session() as session:
            user_id = str(uuid.uuid4())
            user = User(
                id=user_id,
                email=email,
                encrypted_password=hashed_password,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            return {
                "id": str(user.id),
                "email": user.email,
                "encrypted_password": user.encrypted_password,
                "recovery_token": user.recovery_token,
                "recovery_sent_at": user.recovery_sent_at,
                "email_confirmed_at": user.email_confirmed_at,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            }

    async def update_user_password(self, user_id: str, hashed_password: str) -> bool:
        """Update user password"""
        with self.Session() as session:
            user = session.scalar(select(User).where(User.id == user_id).limit(1))
            if not user:
                return False
            user.encrypted_password = hashed_password
            user.recovery_token = None
            user.recovery_sent_at = None
            user.updated_at = datetime.utcnow()
            session.commit()
            return True

    async def set_recovery_token(self, user_id: str, token: str) -> bool:
        """Set recovery token for password reset"""
        with self.Session() as session:
            user = session.scalar(select(User).where(User.id == user_id).limit(1))
            if not user:
                return False
            user.recovery_token = token
            user.recovery_sent_at = datetime.utcnow()
            user.updated_at = datetime.utcnow()
            session.commit()
            return True