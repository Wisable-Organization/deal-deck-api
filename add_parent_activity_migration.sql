-- Migration: Add parent_activity_id to activities table for recursive relationships
-- This enables activities to have parent-child relationships (1-to-many)

BEGIN;

-- Add the parent_activity_id column to the activities table
ALTER TABLE activities 
ADD COLUMN parent_activity_id UUID;

-- Add foreign key constraint that references the same table
ALTER TABLE activities 
ADD CONSTRAINT fk_parent_activity 
FOREIGN KEY (parent_activity_id) 
REFERENCES activities(id) 
ON DELETE CASCADE;

-- Create an index for better performance when querying by parent
CREATE INDEX idx_activities_parent_activity_id 
ON activities(parent_activity_id);

-- Optional: Add a check constraint to prevent an activity from being its own parent
ALTER TABLE activities 
ADD CONSTRAINT chk_not_self_parent 
CHECK (id != parent_activity_id);

COMMIT;


