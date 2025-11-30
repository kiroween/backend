from datetime import date


def validate_future_date(unlock_date: date) -> bool:
    """Validate that unlock date is in the future"""
    return unlock_date > date.today()


def calculate_days_remaining(unlock_date: date) -> int:
    """Calculate days remaining until unlock date"""
    return (unlock_date - date.today()).days
