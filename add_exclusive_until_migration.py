#!/usr/bin/env python3
"""
Apply the exclusive_until migration to add listing agreement exclusivity date to deals
"""

import sys
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

# Database connection
db_url = "postgresql://jor.gbh:root@localhost:5432/deal-deck"

def apply_migration():
    """Apply the exclusive_until migration"""
    engine = create_engine(db_url, poolclass=NullPool)

    print("🗄️  Connecting to local PostgreSQL database...")

    with engine.connect() as conn:
        print("📝 Adding exclusive_until column to deals table...")
        try:
            # Add the listing_agreement_exclusivity_until column
            conn.execute(text("""
                ALTER TABLE deals
                ADD COLUMN listing_agreement_exclusivity_until TIMESTAMP WITH TIME ZONE;
            """))
            conn.commit()
            print("✅ Migration completed successfully!")
        except Exception as e:
            conn.rollback()
            print(f"❌ Migration failed: {e}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    # Verify the migration
    print("\n🔍 Verifying migration...")
    with engine.connect() as conn:
        # Check if the column was added
        result = conn.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'deals'
            AND column_name = 'listing_agreement_exclusivity_until'
        """))
        column_info = result.fetchone()

        if column_info:
            print(f"   ✓ Column 'listing_agreement_exclusivity_until' added successfully")
            print(f"     - Data type: {column_info[1]}")
            print(f"     - Nullable: {column_info[2]}")
        else:
            print("   ❌ Column 'exclusive_until' not found!")
            sys.exit(1)

        # Check deals table structure
        result = conn.execute(text("SELECT COUNT(*) as count FROM deals"))
        deals_count = result.fetchone()[0]
        print(f"\n   Total deals in table: {deals_count}")

if __name__ == "__main__":
    apply_migration()