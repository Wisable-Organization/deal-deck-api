"""
Helper utilities for working with recursive activity relationships.

This module provides utility functions for managing parent-child activity relationships,
including retrieving activity hierarchies and validating activity structures.
"""

from typing import List, Dict, Any, Optional


def get_activity_tree(activities: List[Dict[str, Any]], parent_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Build a hierarchical tree structure from a flat list of activities.
    
    Args:
        activities: A flat list of activity dictionaries
        parent_id: The parent activity ID to start from (None for root activities)
    
    Returns:
        A list of activities with nested 'children' arrays
    
    Example:
        >>> activities = [
        ...     {"id": "1", "title": "Main Task", "parent_activity_id": None},
        ...     {"id": "2", "title": "Subtask 1", "parent_activity_id": "1"},
        ...     {"id": "3", "title": "Subtask 2", "parent_activity_id": "1"},
        ... ]
        >>> tree = get_activity_tree(activities)
        >>> print(tree[0]['children'])  # Will contain subtasks 1 and 2
    """
    tree = []
    
    for activity in activities:
        if activity.get("parent_activity_id") == parent_id:
            activity_copy = activity.copy()
            children = get_activity_tree(activities, activity["id"])
            if children:
                activity_copy["children"] = children
            tree.append(activity_copy)
    
    return tree


def get_activity_descendants(activities: List[Dict[str, Any]], activity_id: str) -> List[Dict[str, Any]]:
    """
    Get all descendants (children, grandchildren, etc.) of a given activity.
    
    Args:
        activities: A flat list of activity dictionaries
        activity_id: The ID of the parent activity
    
    Returns:
        A flat list of all descendant activities
    
    Example:
        >>> activities = [
        ...     {"id": "1", "title": "Main Task", "parent_activity_id": None},
        ...     {"id": "2", "title": "Subtask 1", "parent_activity_id": "1"},
        ...     {"id": "3", "title": "Sub-subtask", "parent_activity_id": "2"},
        ... ]
        >>> descendants = get_activity_descendants(activities, "1")
        >>> len(descendants)  # Returns 2 (both subtask 1 and sub-subtask)
        2
    """
    descendants = []
    
    # Find direct children
    for activity in activities:
        if activity.get("parent_activity_id") == activity_id:
            descendants.append(activity)
            # Recursively find descendants of this child
            descendants.extend(get_activity_descendants(activities, activity["id"]))
    
    return descendants


def get_activity_ancestors(activities: List[Dict[str, Any]], activity_id: str) -> List[Dict[str, Any]]:
    """
    Get all ancestors (parent, grandparent, etc.) of a given activity.
    
    Args:
        activities: A flat list of activity dictionaries
        activity_id: The ID of the child activity
    
    Returns:
        A list of ancestor activities, ordered from immediate parent to root
    
    Example:
        >>> activities = [
        ...     {"id": "1", "title": "Main Task", "parent_activity_id": None},
        ...     {"id": "2", "title": "Subtask 1", "parent_activity_id": "1"},
        ...     {"id": "3", "title": "Sub-subtask", "parent_activity_id": "2"},
        ... ]
        >>> ancestors = get_activity_ancestors(activities, "3")
        >>> [a["title"] for a in ancestors]  # Returns ["Subtask 1", "Main Task"]
        ['Subtask 1', 'Main Task']
    """
    ancestors = []
    
    # Find the activity
    activity = next((a for a in activities if a["id"] == activity_id), None)
    if not activity:
        return ancestors
    
    # Traverse up the tree
    parent_id = activity.get("parent_activity_id")
    while parent_id:
        parent = next((a for a in activities if a["id"] == parent_id), None)
        if not parent:
            break
        ancestors.append(parent)
        parent_id = parent.get("parent_activity_id")
    
    return ancestors


def get_root_activities(activities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Get all root activities (activities without a parent).
    
    Args:
        activities: A flat list of activity dictionaries
    
    Returns:
        A list of root activities
    
    Example:
        >>> activities = [
        ...     {"id": "1", "title": "Main Task 1", "parent_activity_id": None},
        ...     {"id": "2", "title": "Main Task 2", "parent_activity_id": None},
        ...     {"id": "3", "title": "Subtask", "parent_activity_id": "1"},
        ... ]
        >>> roots = get_root_activities(activities)
        >>> len(roots)  # Returns 2
        2
    """
    return [a for a in activities if not a.get("parent_activity_id")]


def calculate_activity_depth(activities: List[Dict[str, Any]], activity_id: str) -> int:
    """
    Calculate the depth of an activity in the hierarchy (0 for root activities).
    
    Args:
        activities: A flat list of activity dictionaries
        activity_id: The ID of the activity
    
    Returns:
        The depth of the activity (0 for root, 1 for children of root, etc.)
    
    Example:
        >>> activities = [
        ...     {"id": "1", "title": "Main Task", "parent_activity_id": None},
        ...     {"id": "2", "title": "Subtask", "parent_activity_id": "1"},
        ...     {"id": "3", "title": "Sub-subtask", "parent_activity_id": "2"},
        ... ]
        >>> calculate_activity_depth(activities, "3")  # Returns 2
        2
    """
    ancestors = get_activity_ancestors(activities, activity_id)
    return len(ancestors)


def is_ancestor_of(activities: List[Dict[str, Any]], ancestor_id: str, descendant_id: str) -> bool:
    """
    Check if one activity is an ancestor of another.
    
    Args:
        activities: A flat list of activity dictionaries
        ancestor_id: The ID of the potential ancestor
        descendant_id: The ID of the potential descendant
    
    Returns:
        True if ancestor_id is an ancestor of descendant_id, False otherwise
    
    Example:
        >>> activities = [
        ...     {"id": "1", "title": "Main Task", "parent_activity_id": None},
        ...     {"id": "2", "title": "Subtask", "parent_activity_id": "1"},
        ...     {"id": "3", "title": "Sub-subtask", "parent_activity_id": "2"},
        ... ]
        >>> is_ancestor_of(activities, "1", "3")  # Returns True
        True
        >>> is_ancestor_of(activities, "3", "1")  # Returns False
        False
    """
    ancestors = get_activity_ancestors(activities, descendant_id)
    return any(a["id"] == ancestor_id for a in ancestors)


