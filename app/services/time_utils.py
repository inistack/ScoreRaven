from datetime import datetime, timezone

def as_utc(dt):
    """Postgres sometimes returns timezone-aware datetimes as naive. Normalize before comparing."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt