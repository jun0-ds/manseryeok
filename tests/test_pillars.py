"""Saju extraction tests — verified against standard manseryeok references."""

from datetime import datetime, timedelta, timezone

import pytest

from manseryeok import calculate_saju, today_pillars
from manseryeok.analysis import Sipsin, sipsin, wuxing_relation, zodiac_from_branch
from manseryeok.types import WuxingRelation

KST = timezone(timedelta(hours=9))


# ── 검증 케이스 #1 ─────────────────────────────────────
# 1992-11-28 申시 (15:31~17:30) Seoul, 男
# 표준 만세력 결과: 壬申 / 辛亥 / 戊申 / 庚申
def test_1992_11_28_sin_si():
    saju = calculate_saju(birth=datetime(1992, 11, 28, 16, 0))
    assert saju.year.char == "壬申"
    assert saju.month.char == "辛亥"
    assert saju.day.char == "戊申"
    assert saju.hour.char == "庚申"
    assert saju.chars == "壬申辛亥戊申庚申"


def test_day_master_is_day_stem():
    saju = calculate_saju(birth=datetime(1992, 11, 28, 16, 0))
    assert saju.day_master == saju.day.stem


# ── 입춘 경계 ─────────────────────────────────────
def test_iccheun_boundary_before():
    """1990-02-04 04:00 KST is before 입춘 (≈11:11 KST) → 己巳년."""
    saju = calculate_saju(birth=datetime(1990, 2, 4, 4, 0))
    assert saju.year.char == "己巳"


def test_iccheun_boundary_after():
    """1990-02-04 16:00 KST is after 입춘 → 庚午년."""
    saju = calculate_saju(birth=datetime(1990, 2, 4, 16, 0))
    assert saju.year.char == "庚午"


# ── 조자시 (early-zi) 처리 ─────────────────────────────────────
def test_early_zi_advances_day():
    """1992-11-28 23:30 (no solar adj, early_zi=True): 일주 = 다음날 己酉, 시주 甲子."""
    saju = calculate_saju(
        birth=datetime(1992, 11, 28, 23, 30),
        use_solar_time=False,
        early_zi=True,
    )
    assert saju.day.char == "己酉"  # next day's 일주
    assert saju.hour.char == "甲子"  # 子時, 己日 starts 甲子時


def test_late_zi_disabled():
    """If early_zi=False, 23:30 stays on the original day."""
    saju = calculate_saju(
        birth=datetime(1992, 11, 28, 23, 30),
        use_solar_time=False,
        early_zi=False,
    )
    assert saju.day.char == "戊申"  # same-day 일주


# ── 시주 boundary ─────────────────────────────────────
def test_zi_si_at_23_00():
    saju = calculate_saju(
        birth=datetime(1992, 11, 28, 23, 0),
        use_solar_time=False,
        early_zi=True,
    )
    assert saju.hour.branch.char == "子"


def test_chuk_si_at_01_30():
    """01:00~02:59 → 丑時."""
    saju = calculate_saju(
        birth=datetime(1992, 11, 28, 1, 30),
        use_solar_time=False,
    )
    assert saju.hour.branch.char == "丑"


# ── KST aware vs naive ─────────────────────────────────────
def test_kst_aware_equivalent_to_naive():
    naive = calculate_saju(birth=datetime(1992, 11, 28, 16, 0))
    aware = calculate_saju(birth=datetime(1992, 11, 28, 16, 0, tzinfo=KST))
    assert naive.chars == aware.chars


# ── today_pillars ─────────────────────────────────────
def test_today_pillars_returns_three():
    today = today_pillars(now=datetime.now(KST))
    assert today.year is not None
    assert today.month is not None
    assert today.day is not None


# ── analysis 통합 ─────────────────────────────────────
def test_zodiac_from_year_branch():
    saju = calculate_saju(birth=datetime(1992, 11, 28, 16, 0))
    assert zodiac_from_branch(saju.year.branch) == "원숭이"


def test_wuxing_relation_day_to_today():
    """戊(土) → 庚(金) is 상생."""
    from manseryeok.data import stem_by_char
    rel = wuxing_relation(stem_by_char("戊").wuxing, stem_by_char("庚").wuxing)
    assert rel == WuxingRelation.GENERATING


def test_sipsin_day_master_vs_target():
    """일간 戊(陽土) vs 壬(陽水) → 편재 (土가 水를 누름, 陽-陽)."""
    from manseryeok.data import stem_by_char
    ss = sipsin(day_stem=stem_by_char("戊"), target_stem=stem_by_char("壬"))
    assert ss == Sipsin.PYEONJAE


# ── 60갑자 무결성 ─────────────────────────────────────
def test_ganzhi_cycle_length():
    from manseryeok.data import GANZHI_CYCLE
    assert len(GANZHI_CYCLE) == 60
    assert GANZHI_CYCLE[0].char == "甲子"
    assert GANZHI_CYCLE[59].char == "癸亥"


def test_ganzhi_yin_yang_parity():
    """In 60갑자, stem and branch always have matching parity."""
    from manseryeok.data import GANZHI_CYCLE
    for p in GANZHI_CYCLE:
        assert p.stem.index % 2 == p.branch.index % 2


def test_ganzhi_yin_yang_constraint_violation():
    """甲(陽) + 丑(陰) is not a valid 60갑자 entry."""
    from manseryeok.data import branch_by_char, pillar_from_stem_branch, stem_by_char
    with pytest.raises(ValueError):
        pillar_from_stem_branch(stem_by_char("甲"), branch_by_char("丑"))
