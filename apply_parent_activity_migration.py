#!/usr/bin/env python3
"""
Apply the parent_activity_id migration to add recursive relationships to activities
"""

import sys
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

# Database connection
db_url = "postgresql://jor.gbh:root@localhost:5432/deal-deck"

def apply_migration():
    """Apply the parent_activity_id migration SQL script"""
    engine = create_engine(db_url, poolclass=NullPool)
    
    print("🗄️  Connecting to local PostgreSQL database...")
    
    # Read the migration file
    migration_file = 'add_parent_activity_migration.sql'
    try:
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
    except FileNotFoundError:
        print(f"❌ Migration file '{migration_file}' not found!")
        sys.exit(1)
    
    with engine.connect() as conn:
        print("📝 Executing migration script to add parent_activity_id column...")
        try:
            # Execute the entire migration script
            conn.execute(text(migration_sql))
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
            WHERE table_name = 'activities' 
            AND column_name = 'parent_activity_id'
        """))
        column_info = result.fetchone()
        
        if column_info:
            print(f"   ✓ Column 'parent_activity_id' added successfully")
            print(f"     - Data type: {column_info[1]}")
            print(f"     - Nullable: {column_info[2]}")
        else:
            print("   ❌ Column 'parent_activity_id' not found!")
            sys.exit(1)
        
        # Check foreign key constraint
        result = conn.execute(text("""
            SELECT constraint_name
            FROM information_schema.table_constraints
            WHERE table_name = 'activities' 
            AND constraint_name = 'fk_parent_activity'
        """))
        fk_info = result.fetchone()
        
        if fk_info:
            print(f"   ✓ Foreign key constraint 'fk_parent_activity' created")
        else:
            print("   ⚠️  Foreign key constraint 'fk_parent_activity' not found")
        
        # Check index
        result = conn.execute(text("""
            SELECT indexname
            FROM pg_indexes
            WHERE tablename = 'activities' 
            AND indexname = 'idx_activities_parent_activity_id'
        """))
        idx_info = result.fetchone()
        
        if idx_info:
            print(f"   ✓ Index 'idx_activities_parent_activity_id' created")
        else:
            print("   ⚠️  Index 'idx_activities_parent_activity_id' not found")
        
        # Check activities table structure
        result = conn.execute(text("SELECT COUNT(*) as count FROM activities"))
        activities_count = result.fetchone()[0]
        print(f"\n   Total activities in table: {activities_count}")

if __name__ == "__main__":
    apply_migration()


