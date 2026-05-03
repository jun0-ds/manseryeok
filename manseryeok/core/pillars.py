"""사주팔자 추출 — 4 pillars from a birth datetime.

Algorithm (in order):
    1. Apply true-solar-time correction (KST → birth-location apparent time)
    2. Apply early-zi rule: hours 23:00~24:00 belong to next day's 子時
    3. Year pillar: determined by 입춘 (315°) — before 입춘, use previous year
    4. Month pillar: determined by the 12 节气 boundaries (even-indexed terms)
    5. Day pillar: JDN offset from epoch (1900-01-01 = 甲戌, JDN 2415021)
    6. Hour pillar: hour-branch from local time + hour-stem via 五子遁
"""

from __future__ import annotations

from datetime import datetime, timedelta

from manseryeok.core.julian import datetime_to_jd, jdn_from_date
from manseryeok.core.solar_terms import solar_term_jd
from manseryeok.core.solar_time import KST_TIMEZONE, SEOUL_LONGITUDE_DEG, true_solar_time
from manseryeok.data.branches import branch_by_index
from manseryeok.data.ganzhi import (
    DAY_PILLAR_EPOCH_INDEX,
    DAY_PILLAR_EPOCH_JDN,
    pillar_from_index,
    pillar_from_stem_branch,
)
from manseryeok.data.stems import stem_by_index
from manseryeok.types import Saju, TodayPillars


# ── 시간 → 시지 매핑 (조자시 적용) ─────────────────────────────────────
# 23:00~00:59 → 子(0), 01:00~02:59 → 丑(1), ..., 21:00~22:59 → 亥(11)
def _hour_branch_index(hour: int, minute: int) -> int:
    """Map (hour, minute) to branch index in early-zi convention."""
    h = hour + minute / 60.0
    # 子時: 23:00~00:59
    if h >= 23.0:
        return 0
    if h < 1.0:
        return 0
    # 丑時 from 01:00
    return int((h + 1.0) // 2)


# ── 五子遁 (시간 천간) ─────────────────────────────────────
# Day-stem index → starting hour-stem index (子시의 천간)
# 갑/기일(0,5) → 갑子시(0), 을/경일(1,6) → 병子시(2),
# 병/신일(2,7) → 무子시(4), 정/임일(3,8) → 경子시(6),
# 무/계일(4,9) → 임子시(8)
_HOUR_STEM_OFFSET_BY_DAY_STEM: tuple[int, ...] = (0, 2, 4, 6, 8, 0, 2, 4, 6, 8)


# ── 五虎遁 (월 천간) ─────────────────────────────────────
# Year-stem index → starting month-stem index (寅월의 천간)
# 갑/기年(0,5) → 병寅(2), 을/경年(1,6) → 무寅(4),
# 병/신年(2,7) → 경寅(6), 정/임年(3,8) → 임寅(8),
# 무/계年(4,9) → 갑寅(0)
_MONTH_STEM_OFFSET_BY_YEAR_STEM: tuple[int, ...] = (2, 4, 6, 8, 0, 2, 4, 6, 8, 0)


def _apply_early_zi(local_dt: datetime, *, early_zi: bool) -> datetime:
    """If hour ≥ 23 and early_zi, advance the date by 1 day (Day pillar uses
    next day's date). Hour-branch logic still maps 23:00~00:59 → 子."""
    if early_zi and local_dt.hour >= 23:
        return local_dt + timedelta(days=1)
    return local_dt


# ── Year-pillar boundary: 입춘 (315°) ─────────────────────────────────────
def _year_pillar_year(birth_jd_ut: float, gregorian_year: int) -> int:
    """Determine the 'lunar year' for year-pillar purposes by JD (UT) comparison.

    If birth_jd_ut is before 입춘 of its Gregorian year (UT), use the previous year.
    """
    iccheun_jd = solar_term_jd(gregorian_year, 0)  # term 0 = 입춘 (UT JD)
    if birth_jd_ut < iccheun_jd:
        return gregorian_year - 1
    return gregorian_year


def _year_pillar_index(year: int) -> int:
    """60갑자 index for the given year-pillar year.

    Reference: year 1900 (lunar, after 입춘) = 庚子 → index 36.
    Then index = (36 + (year - 1900)) % 60.
    """
    return (36 + (year - 1900)) % 60


# ── Month-pillar boundary ─────────────────────────────────────
def _month_pillar_indices(birth_jd_ut: float, gregorian_year: int) -> tuple[int, int]:
    """Return (month_branch_index, month_offset_from_寅) for the given birth JD (UT).

    The 12 节气 (even-indexed terms 0, 2, 4, ..., 22) define month boundaries.
    Term 0 (입춘) starts 寅月; term 2 (경칩) starts 卯月; ...
    """
    boundaries: list[tuple[float, int]] = []  # (term_jd, branch_index)
    branch_seq = (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0, 1)  # 寅卯辰巳午未申酉戌亥子丑

    # Cover preceding and following Gregorian years to handle year boundaries
    for offset_year in (gregorian_year - 1, gregorian_year, gregorian_year + 1):
        for i in range(12):
            term_idx = i * 2
            jd = solar_term_jd(offset_year, term_idx)
            boundaries.append((jd, branch_seq[i]))

    boundaries.sort()
    active_branch = boundaries[0][1]
    for jd, br in boundaries:
        if jd <= birth_jd_ut:
            active_branch = br
        else:
            break

    offset_from_in = (active_branch - 2) % 12
    return active_branch, offset_from_in


def _month_pillar_index(year_stem_index: int, month_offset_from_in: int, month_branch_index: int) -> int:
    """Compute the 60갑자 index of the month pillar."""
    start_stem = _MONTH_STEM_OFFSET_BY_YEAR_STEM[year_stem_index]
    month_stem = (start_stem + month_offset_from_in) % 10
    # Find the 60갑자 entry matching this (stem, branch)
    return _index_from_stem_branch(month_stem, month_branch_index)


# ── Day-pillar (JDN-based) ─────────────────────────────────────
def _day_pillar_index(local_dt: datetime) -> int:
    """60갑자 index for the day pillar at (year, month, day) of local_dt."""
    jdn = jdn_from_date(local_dt.year, local_dt.month, local_dt.day)
    return (jdn - DAY_PILLAR_EPOCH_JDN + DAY_PILLAR_EPOCH_INDEX) % 60


# ── Hour-pillar ─────────────────────────────────────
def _hour_pillar_index(day_stem_index: int, hour_branch_index: int) -> int:
    """Compute the 60갑자 index of the hour pillar."""
    start_stem = _HOUR_STEM_OFFSET_BY_DAY_STEM[day_stem_index]
    hour_stem = (start_stem + hour_branch_index) % 10
    return _index_from_stem_branch(hour_stem, hour_branch_index)


# ── 60갑자 index from (stem, branch) ─────────────────────────────────────
def _index_from_stem_branch(stem_idx: int, branch_idx: int) -> int:
    """Find i in 0..59 such that i % 10 == stem_idx and i % 12 == branch_idx.

    Yin/yang pairing constraint: stem and branch must have the same parity.
    """
    stem_idx = stem_idx % 10
    branch_idx = branch_idx % 12
    if (stem_idx % 2) != (branch_idx % 2):
        raise ValueError(
            f"Invalid stem/branch parity: stem={stem_idx} (parity {stem_idx % 2}), "
            f"branch={branch_idx} (parity {branch_idx % 2})"
        )
    # CRT-style: find i such that i ≡ stem_idx (mod 10), i ≡ branch_idx (mod 12)
    for k in range(6):  # 60 / 10 = 6 candidates
        i = stem_idx + 10 * k
        if i % 12 == branch_idx:
            return i
    raise AssertionError("unreachable")


# ── Public API ─────────────────────────────────────


def _ensure_kst_aware(dt: datetime) -> datetime:
    """Treat naive datetime as KST."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=KST_TIMEZONE)
    return dt


def calculate_saju(
    *,
    birth: datetime,
    longitude_deg: float = SEOUL_LONGITUDE_DEG,
    use_solar_time: bool = True,
    early_zi: bool = True,
) -> Saju:
    """Compute 사주 (4 pillars) from a birth datetime.

    Args:
        birth: KST-aware or naive datetime (naive is treated as KST).
        longitude_deg: Birth-location longitude in degrees East (default Seoul).
        use_solar_time: Apply Equation of Time + longitude correction (default True).
        early_zi: Treat 23:00~24:00 as next day's 子時 (default True, modern standard).

    Returns:
        Saju with year/month/day/hour pillars.
    """
    birth = _ensure_kst_aware(birth)
    birth_jd_ut = datetime_to_jd(birth)

    # Local time (진태양시 if enabled, else KST clock time)
    if use_solar_time:
        local_dt = true_solar_time(birth, longitude_deg)
    else:
        local_dt = birth.astimezone(KST_TIMEZONE).replace(tzinfo=None)

    # Early-zi: advance date if local hour ≥ 23 (day-pillar uses next day)
    day_dt = _apply_early_zi(local_dt, early_zi=early_zi)

    # Year pillar (UT-based 입춘 comparison)
    yp_year = _year_pillar_year(birth_jd_ut, local_dt.year)
    year_pillar = pillar_from_index(_year_pillar_index(yp_year))

    # Month pillar (UT-based 절기 comparison)
    month_branch, month_offset = _month_pillar_indices(birth_jd_ut, local_dt.year)
    month_pillar = pillar_from_index(
        _month_pillar_index(year_pillar.stem.index, month_offset, month_branch)
    )

    # Day pillar (local-date based, with early-zi advance)
    day_pillar = pillar_from_index(_day_pillar_index(day_dt))

    # Hour pillar (local clock hour + day-stem)
    hour_branch_idx = _hour_branch_index(local_dt.hour, local_dt.minute)
    hour_pillar = pillar_from_index(_hour_pillar_index(day_pillar.stem.index, hour_branch_idx))

    return Saju(year=year_pillar, month=month_pillar, day=day_pillar, hour=hour_pillar)


def today_pillars(
    *,
    now: datetime,
    longitude_deg: float = SEOUL_LONGITUDE_DEG,
    use_solar_time: bool = True,
    early_zi: bool = True,
) -> TodayPillars:
    """Compute today's year/month/day pillars (no hour pillar)."""
    now = _ensure_kst_aware(now)
    now_jd_ut = datetime_to_jd(now)

    if use_solar_time:
        local_dt = true_solar_time(now, longitude_deg)
    else:
        local_dt = now.astimezone(KST_TIMEZONE).replace(tzinfo=None)

    day_dt = _apply_early_zi(local_dt, early_zi=early_zi)

    yp_year = _year_pillar_year(now_jd_ut, local_dt.year)
    year_pillar = pillar_from_index(_year_pillar_index(yp_year))

    month_branch, month_offset = _month_pillar_indices(now_jd_ut, local_dt.year)
    month_pillar = pillar_from_index(
        _month_pillar_index(year_pillar.stem.index, month_offset, month_branch)
    )

    day_pillar = pillar_from_index(_day_pillar_index(day_dt))

    return TodayPillars(year=year_pillar, month=month_pillar, day=day_pillar)


# Re-export pillar_from_stem_branch for tests
__all__ = ["calculate_saju", "today_pillars"]
