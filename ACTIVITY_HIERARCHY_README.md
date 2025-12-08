# Activity Hierarchy Feature

## Overview

This update adds support for recursive parent-child relationships between activities, allowing you to create hierarchical task structures where activities can have sub-activities.

## Changes Made

### 1. Database Schema Changes

#### New Column: `parent_activity_id`
- **Type**: UUID (nullable)
- **Purpose**: References another activity as the parent
- **Constraint**: Foreign key to `activities.id` with CASCADE delete
- **Constraint**: Check constraint prevents self-referencing (activity cannot be its own parent)
- **Index**: Created for improved query performance on parent lookups

### 2. Model Updates (`api/models.py`)

The `Activity` model now includes:
- `parent_activity_id`: Column to store the parent activity reference
- `parent`: Relationship to access the parent activity
- `children`: Back-populated relationship to access child activities

```python
# Example usage in code:
activity = session.query(Activity).filter(Activity.id == some_id).first()
parent_activity = activity.parent  # Access parent
child_activities = activity.children  # Access all children
```

### 3. Schema Updates (`api/schemas.py`)

All activity schemas now include `parent_activity_id`:
- `ActivityResponseSchema`: Returns `parent_activity_id` in responses
- `ActivityCreateSchema`: Accepts `parent_activity_id` when creating activities
- `ActivityUpdateSchema`: Allows updating `parent_activity_id`

### 4. Storage Layer Updates (`api/storage.py`)

Enhanced with validation logic:

#### Create Activity
- Validates that parent activity exists before creating child
- Returns `parent_activity_id` in response

#### Update Activity
- Validates parent activity exists
- Prevents self-referencing (activity cannot be its own parent)
- Prevents circular references (prevents A → B → C → A scenarios)

#### Get Activities
- All get methods now include `parent_activity_id` in returned data

### 5. Helper Utilities (`activity_helpers.py`)

New utility functions for working with activity hierarchies:

- `get_activity_tree()`: Build a nested tree structure from flat activity list
- `get_activity_descendants()`: Get all descendants of an activity
- `get_activity_ancestors()`: Get all ancestors of an activity
- `get_root_activities()`: Get all top-level activities
- `calculate_activity_depth()`: Calculate how deep an activity is in the hierarchy
- `is_ancestor_of()`: Check if one activity is an ancestor of another

## Running the Migration

### Local Development

1. Ensure your PostgreSQL database is running
2. Run the migration script:

```bash
python apply_parent_activity_migration.py
```

The script will:
- Add the `parent_activity_id` column
- Create the foreign key constraint
- Add the index for performance
- Add the check constraint to prevent self-referencing
- Verify the migration was successful

### Production

Apply the SQL file directly:

```bash
psql -h your-host -U your-user -d your-database -f add_parent_activity_migration.sql
```

Or include it in your deployment pipeline.

## Usage Examples

### Creating Parent-Child Activities

```python
# Create a parent activity
parent_activity = {
    "deal_id": "some-deal-id",
    "type": "milestone",
    "title": "Complete Due Diligence",
    "status": "pending"
}
parent = await storage.create_activity(parent_activity)

# Create child activities
child1 = {
    "deal_id": "some-deal-id",
    "parent_activity_id": parent["id"],
    "type": "task",
    "title": "Review Financial Statements",
    "status": "pending"
}
await storage.create_activity(child1)

child2 = {
    "deal_id": "some-deal-id",
    "parent_activity_id": parent["id"],
    "type": "task",
    "title": "Legal Document Review",
    "status": "pending"
}
await storage.create_activity(child2)
```

### Using Helper Functions

```python
from activity_helpers import get_activity_tree, get_activity_descendants

# Get all activities
activities = await storage.get_activities()

# Build a tree structure
tree = get_activity_tree(activities)

# Get all descendants of a specific activity
descendants = get_activity_descendants(activities, parent_id)

# Get root-level activities only
from activity_helpers import get_root_activities
root_activities = get_root_activities(activities)
```

### API Request Examples

**Create an activity with a parent:**
```json
POST /api/activities
{
  "dealId": "123e4567-e89b-12d3-a456-426614174000",
  "parentActivityId": "987f6543-e21c-12d3-a456-426614174000",
  "type": "task",
  "title": "Sub-task",
  "status": "pending"
}
```

**Update an activity's parent:**
```json
PATCH /api/activities/{id}
{
  "parentActivityId": "new-parent-id"
}
```

## Validation Rules

The following validations are enforced:

1. **Parent Must Exist**: When creating or updating an activity with a parent_activity_id, the parent must exist
2. **No Self-Reference**: An activity cannot be its own parent
3. **No Circular References**: Prevents cycles like A → B → C → A
4. **Cascade Delete**: When a parent activity is deleted, all its children are also deleted

## Future Enhancements (Not Yet Implemented)

Potential features to add in the future:

1. **Maximum Depth Limit**: Enforce a maximum hierarchy depth
2. **Bulk Operations**: Move entire subtrees of activities
3. **Activity Templates**: Create template hierarchies that can be instantiated
4. **Progress Rollup**: Automatically calculate parent progress based on children
5. **API Endpoints**: 
   - `GET /api/activities/{id}/children` - Get direct children
   - `GET /api/activities/{id}/descendants` - Get all descendants
   - `GET /api/activities/{id}/ancestors` - Get ancestors/breadcrumb trail
   - `GET /api/activities/roots` - Get root-level activities only

## Database Rollback

If you need to rollback this migration:

```sql
BEGIN;

-- Remove the check constraint
ALTER TABLE activities DROP CONSTRAINT IF EXISTS chk_not_self_parent;

-- Drop the index
DROP INDEX IF EXISTS idx_activities_parent_activity_id;

-- Drop the foreign key constraint
ALTER TABLE activities DROP CONSTRAINT IF EXISTS fk_parent_activity;

-- Remove the column
ALTER TABLE activities DROP COLUMN IF EXISTS parent_activity_id;

COMMIT;
```

## Testing

Test the feature with these scenarios:

1. ✅ Create an activity without a parent
2. ✅ Create an activity with a valid parent
3. ✅ Try to create an activity with a non-existent parent (should fail)
4. ✅ Try to update an activity to be its own parent (should fail)
5. ✅ Try to create a circular reference (should fail)
6. ✅ Delete a parent activity (children should be deleted via CASCADE)
7. ✅ Query activities and verify parent_activity_id is included

## Notes

- The `parent_activity_id` field is nullable, so existing activities will have `NULL` for this field after migration
- Activities can have either a `deal_id`, `buying_party_id`, or both, independent of the parent relationship
- The cascade delete ensures data integrity when removing parent activities


