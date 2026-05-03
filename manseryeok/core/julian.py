"""Julian Day conversions.

Conventions:
    JD     — Julian Day (continuous, fractional days since 4713 BC noon UT)
    JDN    — Julian Day Number (integer, day starting at noon UT)
    UT     — Universal Time
    KST    — UTC+9

Formulas based on Jean Meeus, "Astronomical Algorithms" (2nd ed., 1998), Ch. 7.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone


def jdn_from_date(year: int, month: int, day: int) -> int:
    """Julian Day Number (integer) for the noon of given Gregorian date.

    Verified: jdn_from_date(2000, 1, 1) == 2451545
              jdn_from_date(1900, 1, 1) == 2415021
              jdn_from_date(1992, 11, 28) == 2448955
    """
    if month <= 2:
        year -= 1
        month += 12
    a = year // 100
    b = 2 - a + a // 4
    return int(math.floor(365.25 * (year + 4716))) + int(math.floor(30.6001 * (month + 1))) + day + b - 1524


def datetime_to_jd(dt: datetime) -> float:
    """Convert datetime to Julian Day (fractional, in UT).

    If dt is naive, it's assumed to be UT (UTC). If timezone-aware, converted to UTC first.
    """
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    jdn = jdn_from_date(dt.year, dt.month, dt.day)
    # JDN starts at noon, so subtract 0.5 to get JD at midnight, then add fractional day
    fractional = (dt.hour + dt.minute / 60 + dt.second / 3600 + dt.microsecond / 3_600_000_000) / 24.0
    return jdn - 0.5 + fractional


def jd_to_datetime(jd: float) -> datetime:
    """Convert Julian Day (UT) back to a naive UTC datetime."""
    jd_plus = jd + 0.5
    z = int(math.floor(jd_plus))
    f = jd_plus - z

    if z < 2299161:
        a = z
    else:
        alpha = int(math.floor((z - 1867216.25) / 36524.25))
        a = z + 1 + alpha - alpha // 4

    b = a + 1524
    c = int(math.floor((b - 122.1) / 365.25))
    d = int(math.floor(365.25 * c))
    e = int(math.floor((b - d) / 30.6001))

    day_frac = b - d - int(math.floor(30.6001 * e)) + f
    day = int(math.floor(day_frac))
    month = e - 1 if e < 14 else e - 13
    year = c - 4716 if month > 2 else c - 4715

    rem = (day_frac - day) * 24.0
    hour = int(math.floor(rem))
    rem = (rem - hour) * 60.0
    minute = int(math.floor(rem))
    rem = (rem - minute) * 60.0
    second = int(math.floor(rem))
    micro = int(round((rem - second) * 1_000_000))
    if micro >= 1_000_000:
        micro -= 1_000_000
        second += 1

    return datetime(year, month, day, hour, minute, second, micro)


def jdn_from_jd(jd: float) -> int:
    """Convert JD to JDN by truncating at the noon boundary."""
    return int(math.floor(jd + 0.5))
