"""True solar time correction.

Korean Standard Time (KST) is UTC+9, anchored to the meridian at 135°E (Akashi,
Japan). For accurate saju calculation, we want **true solar time** at the
**birth location** — i.e., the moment the Sun is at its apparent local position.

True solar time = Mean solar time at birth-longitude + Equation of Time
                = KST + (longitude_deg - 135) * 4 minutes + EoT

Equation of Time (EoT): the discrepancy between mean solar time and
apparent (true) solar time — caused by Earth's elliptical orbit and axial tilt.
Range ≈ ±16 minutes throughout the year.

Default longitude: 126.978°E (Seoul). For a person born in Seoul,
the correction is approximately:
    (126.978 - 135) * 4 ≈ -32 minutes (KST is ~32 min ahead of Seoul solar time)
    + EoT (varies, ±16 min)
"""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone

from manseryeok.core.julian import datetime_to_jd
from manseryeok.core.solar import sun_apparent_longitude, sun_mean_longitude

# Korean Standard Time anchor
KST_REFERENCE_LONGITUDE_DEG = 135.0
KST_TIMEZONE = timezone(timedelta(hours=9))

# Default longitude — Seoul, Republic of Korea
SEOUL_LONGITUDE_DEG = 126.978


def equation_of_time_minutes(jd: float) -> float:
    """Equation of Time (in minutes), Meeus Ch. 28 simplified.

    Returns: minutes by which apparent solar time leads mean solar time.
             Positive → sun ahead of clock; Negative → behind.
    """
    l0 = sun_mean_longitude(jd)
    alpha = _sun_apparent_right_ascension(jd)
    # Both in degrees — diff is mean - apparent in deg, convert to minutes (×4)
    e_deg = l0 - 0.0057183 - alpha
    # Normalize to (-180, 180]
    e_deg = ((e_deg + 180.0) % 360.0) - 180.0
    return e_deg * 4.0


def _sun_apparent_right_ascension(jd: float) -> float:
    """Sun's apparent right ascension (degrees). Helper for EoT.

    Uses obliquity of ecliptic ≈ 23.4392911° (J2000) — sufficient precision.
    """
    lon = sun_apparent_longitude(jd)
    eps = 23.4392911  # mean obliquity at J2000
    lon_rad = math.radians(lon)
    eps_rad = math.radians(eps)
    y = math.cos(eps_rad) * math.sin(lon_rad)
    x = math.cos(lon_rad)
    alpha = math.degrees(math.atan2(y, x))
    return alpha % 360.0


def true_solar_time(
    kst_dt: datetime, longitude_deg: float = SEOUL_LONGITUDE_DEG
) -> datetime:
    """Convert a KST datetime to true solar time at the given longitude.

    Args:
        kst_dt: Naive or KST-aware datetime in Korean Standard Time.
        longitude_deg: Birth-location longitude in degrees East. Default Seoul.

    Returns:
        Naive datetime representing true solar time at birth location.
    """
    # Treat naive as KST
    if kst_dt.tzinfo is None:
        kst_aware = kst_dt.replace(tzinfo=KST_TIMEZONE)
    else:
        kst_aware = kst_dt.astimezone(KST_TIMEZONE)

    jd_kst = datetime_to_jd(kst_aware)

    # Longitude correction (minutes)
    lon_correction_min = (longitude_deg - KST_REFERENCE_LONGITUDE_DEG) * 4.0
    eot_min = equation_of_time_minutes(jd_kst)

    total_offset = timedelta(minutes=lon_correction_min + eot_min)
    return (kst_aware + total_offset).replace(tzinfo=None)
