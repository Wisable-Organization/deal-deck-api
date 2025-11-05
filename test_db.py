#!/usr/bin/env python3
"""Test script to check database directly"""
import asyncio
import os
from api.storage import Storage

async def main():
    storage = Storage()
    
    print("=== Testing Deals ===")
    deals = await storage.get_deals()
    print(f"Total deals: {len(deals)}")
    for deal in deals:
        print(f"  - {deal.companyName} (ID: {deal.id}, Stage: {deal.stage})")
    
    # Find TechFlow
    techflow = [d for d in deals if 'TechFlow' in d.companyName]
    if techflow:
        tech_id = techflow[0].id
        print(f"\n=== Testing Buyer Matches for TechFlow (ID: {tech_id}) ===")
        
        # Get buyer matches
        matches = await storage.get_deal_buyer_matches(tech_id)
        print(f"Number of matches: {len(matches)}")
        for match in matches:
            print(f"  Match ID: {match.id}")
            print(f"    Buying Party ID: {match.buyingPartyId}")
            print(f"    Status: {match.status}")
            
            # Get the buying party
            party = await storage.get_buying_party(match.buyingPartyId)
            if party:
                print(f"    Party Name: {party.name}")
            else:
                print(f"    Party: NOT FOUND")
    
    print("\n=== Testing All Buying Parties ===")
    parties = await storage.get_buying_parties()
    print(f"Total parties: {len(parties)}")
    for party in parties:
        print(f"  - {party.name} (ID: {party.id})")

if __name__ == "__main__":
    asyncio.run(main())
