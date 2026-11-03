from database import notifications as get_notifications

def for_user(user_id: int):
    """Load the current user's persisted in-app notices."""
    return get_notifications(user_id)
