from datetime import date


def parse_iso_date(value: str | None) -> date | None:
    """Parse a 'YYYY-MM-DD' string into a date, returning None when absent/invalid."""
    if not value:
        return None
    try:
        return date.fromisoformat(value.strip()[:10])
    except ValueError:
        return None
