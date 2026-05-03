"""Apparent solar longitude.

Based on Jean Meeus, "Astronomical Algorithms" (2nd ed., 1998), Ch. 25
("Solar Coordinates"). Truncated low-precision form — accuracy ≈ ±0.01°
(≈ ±15 minutes in solar-term timing). Sufficient for saju calculation
where solar-term precision of a few minutes is well within boundary safety.

For higher precision, would require full VSOP87 series — but that adds
~3000 lines of coefficients with no practical benefit for saju.
"""

from __future__ import annotations

import math

J2000_JD = 2451545.0
JULIAN_CENTURY_DAYS = 36525.0


def _norm_360(deg: float) -> float:
    """Normalize an angle (degrees) to [0, 360)."""
    x = deg % 360.0
    if x < 0:
        x += 360.0
    return x


def sun_mean_longitude(jd: float) -> float:
    """Mean longitude of the Sun (degrees), Meeus 25.2."""
    t = (jd - J2000_JD) / JULIAN_CENTURY_DAYS
    l0 = 280.46646 + 36000.76983 * t + 0.0003032 * t * t
    return _norm_360(l0)


def sun_mean_anomaly(jd: float) -> float:
    """Mean anomaly of the Sun (degrees), Meeus 25.3."""
    t = (jd - J2000_JD) / JULIAN_CENTURY_DAYS
    m = 357.52911 + 35999.05029 * t - 0.0001537 * t * t
    return _norm_360(m)


def sun_apparent_longitude(jd: float) -> float:
    """Apparent longitude of the Sun (degrees), Meeus 25.4 + nutation correction.

    Returns a value in [0, 360).
    """
    t = (jd - J2000_JD) / JULIAN_CENTURY_DAYS
    l0 = sun_mean_longitude(jd)
    m = sun_mean_anomaly(jd)
    m_rad = math.radians(m)

    # Equation of center (Meeus 25.4)
    c = (
        (1.914602 - 0.004817 * t - 0.000014 * t * t) * math.sin(m_rad)
        + (0.019993 - 0.000101 * t) * math.sin(2 * m_rad)
        + 0.000289 * math.sin(3 * m_rad)
    )

    l_true = l0 + c

    # Apparent longitude (Meeus 25.8) — aberration + nutation simplification
    omega = 125.04 - 1934.136 * t
    l_app = l_true - 0.00569 - 0.00478 * math.sin(math.radians(omega))

    return _norm_360(l_app)
