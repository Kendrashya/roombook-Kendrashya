from datetime import datetime


def overlaps(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
    """True if the time range a overlaps the time range b.

    Times are half-open intervals: a meeting from 10:00 to 11:00 does NOT
    clash with one from 11:00 to 12:00, so touching endpoints do not count
    as an overlap.
    """
    return a_start < b_end and b_start < a_end
