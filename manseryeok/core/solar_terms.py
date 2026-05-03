"""24 절기 — Korean solar terms.

Each solar term occurs when the Sun's apparent ecliptic longitude reaches a
specific multiple of 15°. The 24 terms in calendar order (Korean tradition,
starting from 입춘 — month-pillar boundary):

    Index  Name      Lon°    Role
    0      입춘 立春   315     寅月 (정월) 시작 + 년주 경계
    1      우수 雨水   330     중기
    2      경칩 驚蟄   345     卯月 시작
    3      춘분 春分   0       중기
    4      청명 淸明   15      辰月 시작
    5      곡우 穀雨   30      중기
    6      입하 立夏   45      巳月
    7      소만 小滿   60
    8      망종 芒種   75      午月
    9      하지 夏至   90
    10     소서 小暑   105     未月
    11     대서 大暑   120
    12     입추 立秋   135     申月
    13     처서 處暑   150
    14     백로 白露   165     酉月
    15     추분 秋分   180
    16     한로 寒露   195     戌月
    17     상강 霜降   210
    18     입동 立冬   225     亥月
    19     소설 小雪   240
    20     대설 大雪   255     子月
    21     동지 冬至   270
    22     소한 小寒   285     丑月
    23     대한 大寒   300

Even-indexed entries (0, 2, 4, ...) are 절기(節氣) — month-pillar boundaries.
Odd-indexed entries are 중기(中氣) — informational only.

The year-pillar boundary is 입춘 (315°): before 입춘 is the previous lunar year.
"""

from __future__ import annotations

import math

from manseryeok.core.solar import sun_apparent_longitude

# (한글, 한자, 황경°)
SOLAR_TERM_NAMES: tuple[tuple[str, str, float], ...] = (
    ("입춘", "立春", 315.0),
    ("우수", "雨水", 330.0),
    ("경칩", "驚蟄", 345.0),
    ("춘분", "春分", 0.0),
    ("청명", "淸明", 15.0),
    ("곡우", "穀雨", 30.0),
    ("입하", "立夏", 45.0),
    ("소만", "小滿", 60.0),
    ("망종", "芒種", 75.0),
    ("하지", "夏至", 90.0),
    ("소서", "小暑", 105.0),
    ("대서", "大暑", 120.0),
    ("입추", "立秋", 135.0),
    ("처서", "處暑", 150.0),
    ("백로", "白露", 165.0),
    ("추분", "秋分", 180.0),
    ("한로", "寒露", 195.0),
    ("상강", "霜降", 210.0),
    ("입동", "立冬", 225.0),
    ("소설", "小雪", 240.0),
    ("대설", "大雪", 255.0),
    ("동지", "冬至", 270.0),
    ("소한", "小寒", 285.0),
    ("대한", "大寒", 300.0),
)

# Average mean solar motion (deg/day)
_MEAN_DAILY_MOTION = 360.0 / 365.2422


def _normalize_lon_diff(actual: float, target: float) -> float:
    """Signed shortest-arc difference target - actual (degrees), in (-180, 180]."""
    d = (target - actual) % 360.0
    if d > 180.0:
        d -= 360.0
    return d


def solar_term_jd(year: int, term_index: int) -> float:
    """Julian Day (UT) when the Sun reaches the apparent longitude for the
    given solar term in the given Gregorian year.

    Args:
        year: Gregorian year (1900-2100 supported).
        term_index: 0~23 in calendar order (0 = 입춘).

    Returns:
        JD (UT) accurate to within ~1 minute for 1900-2100.

    Note: For term_index = 3 (춘분, 0°), the result lies near the spring equinox
    of the same Gregorian year. For terms 0~2 (입춘 ~ 경칩), the result is in
    the early part of the same year (Feb-March).
    """
    if not (0 <= term_index < 24):
        raise ValueError(f"term_index must be in 0..23, got {term_index}")

    target_lon = SOLAR_TERM_NAMES[term_index][2]

    # Initial guess: the average position of this term in the year.
    # Term 0 (입춘) typically falls around Feb 4 → day-of-year ~35.
    # Each term advances ~15.218 days on average.
    approx_doy = 35.0 + term_index * (365.2422 / 24.0)
    # Adjust for terms whose solar-longitude target wraps past 360° back to 0+
    # (terms 3 onwards stay in the same Gregorian year regardless).
    jd = jdn_from_year_doy(year, approx_doy)

    # Newton-style iteration: longitude moves ~0.9856°/day
    for _ in range(20):
        lon = sun_apparent_longitude(jd)
        diff = _normalize_lon_diff(lon, target_lon)
        if abs(diff) < 1e-5:
            break
        jd += diff / _MEAN_DAILY_MOTION
    return jd


def jdn_from_year_doy(year: int, doy: float) -> float:
    """Approximate JD given Gregorian year and day-of-year (1-based, fractional)."""
    from manseryeok.core.julian import jdn_from_date

    jdn_jan1 = jdn_from_date(year, 1, 1)
    return jdn_jan1 - 0.5 + (doy - 1.0)


# Expose helper for the average daily motion (used in tests/diagnostics)
MEAN_DAILY_MOTION_DEG = _MEAN_DAILY_MOTION
