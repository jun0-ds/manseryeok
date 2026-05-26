"""대운(大運) 산출 테스트 — 순역·시퀀스·대운수·인덱싱·결정성."""

from __future__ import annotations

from datetime import datetime

from manseryeok import YinYang, calculate_saju, daeun


def test_suyeok_yang_year():
    # 2024 = 甲辰 (년간 甲 = 양). 양남 순행 / 양녀 역행.
    s = calculate_saju(birth=datetime(2024, 6, 15, 12, 0))
    assert s.year.stem.yin_yang is YinYang.YANG
    assert daeun(birth=datetime(2024, 6, 15, 12, 0), gender="M").forward is True
    assert daeun(birth=datetime(2024, 6, 15, 12, 0), gender="F").forward is False


def test_suyeok_yin_year():
    # 2025 = 乙巳 (년간 乙 = 음). 음남 역행 / 음녀 순행.
    s = calculate_saju(birth=datetime(2025, 6, 15, 12, 0))
    assert s.year.stem.yin_yang is YinYang.YIN
    assert daeun(birth=datetime(2025, 6, 15, 12, 0), gender="M").forward is False
    assert daeun(birth=datetime(2025, 6, 15, 12, 0), gender="F").forward is True


def test_sequence_steps_from_month_pillar():
    """각 대운 간지 = 월주 ± (k+1), 시작 나이 = 대운수 + 10k."""
    birth = datetime(1992, 10, 29, 5, 0)
    s = calculate_saju(birth=birth)
    for gender in ("M", "F"):
        d = daeun(birth=birth, gender=gender, count=9)
        step = 1 if d.forward else -1
        assert len(d.periods) == 9
        for k, p in enumerate(d.periods):
            assert p.pillar.index == (s.month.index + step * (k + 1)) % 60
            assert p.start_age == d.start_age + 10 * k


def test_start_age_plausible():
    for g in ("M", "F"):
        d = daeun(birth=datetime(1992, 10, 29, 5, 0), gender=g)
        assert 1 <= d.start_age <= 10, f"대운수 비현실적: {d.start_age}"


def test_at_age_indexing():
    d = daeun(birth=datetime(1992, 10, 29, 5, 0), gender="F")
    assert d.at_age(d.start_age - 1) is None
    assert d.at_age(d.start_age) is d.periods[0]
    assert d.at_age(d.start_age + 5) is d.periods[0]
    assert d.at_age(d.start_age + 10) is d.periods[1]


def test_deterministic():
    a = daeun(birth=datetime(1992, 10, 29, 5, 0), gender="F")
    b = daeun(birth=datetime(1992, 10, 29, 5, 0), gender="F")
    assert a == b


def test_bool_gender_accepted():
    assert daeun(birth=datetime(2024, 6, 15, 12, 0), gender=True).forward is True  # 남=True
    assert daeun(birth=datetime(2024, 6, 15, 12, 0), gender=False).forward is False
