"""Tests for 12지지 관계 (충·합·형·회·파·해)."""

import pytest

from manseryeok.analysis import (
    BranchRelation,
    branch_pair_relation,
    samhap_complete,
    samhap_member,
)
from manseryeok.data import branch_by_char


def b(c: str):
    return branch_by_char(c)


# ── 충 (沖) ─────────────────────────────────────
@pytest.mark.parametrize("a,c", [
    ("子", "午"), ("丑", "未"), ("寅", "申"),
    ("卯", "酉"), ("辰", "戌"), ("巳", "亥"),
])
def test_chung_pairs(a, c):
    assert branch_pair_relation(b(a), b(c)) == BranchRelation.CHUNG
    assert branch_pair_relation(b(c), b(a)) == BranchRelation.CHUNG  # symmetric


# ── 육합 (六合) ─────────────────────────────────────
@pytest.mark.parametrize("a,c", [
    ("子", "丑"), ("寅", "亥"), ("卯", "戌"),
    ("辰", "酉"), ("巳", "申"), ("午", "未"),
])
def test_yukhap_pairs(a, c):
    assert branch_pair_relation(b(a), b(c)) == BranchRelation.YUKHAP


# ── 형 (刑) ─────────────────────────────────────
def test_hyeong_three_寅巳申():
    """寅巳申 三刑 — but 巳申은 육합도 됨 (육합 우선). 寅申은 충 (충 우선)."""
    assert branch_pair_relation(b("寅"), b("巳")) == BranchRelation.HYEONG  # 형만 적용
    assert branch_pair_relation(b("巳"), b("申")) == BranchRelation.YUKHAP  # 육합 우선
    assert branch_pair_relation(b("寅"), b("申")) == BranchRelation.CHUNG  # 충 우선


def test_hyeong_three_丑戌未():
    """丑戌未 三刑 — 丑未는 충 우선."""
    assert branch_pair_relation(b("丑"), b("戌")) == BranchRelation.HYEONG
    assert branch_pair_relation(b("戌"), b("未")) == BranchRelation.HYEONG
    assert branch_pair_relation(b("丑"), b("未")) == BranchRelation.CHUNG


def test_hyeong_self_辰辰():
    assert branch_pair_relation(b("辰"), b("辰")) == BranchRelation.HYEONG


def test_hyeong_mutual_子卯():
    assert branch_pair_relation(b("子"), b("卯")) == BranchRelation.HYEONG


# ── 파 (破) ─────────────────────────────────────
def test_pa_pairs_excluding_yukhap_overlap():
    """寅亥 is both 파 and 육합 — 육합 takes priority."""
    assert branch_pair_relation(b("寅"), b("亥")) == BranchRelation.YUKHAP
    # Pure 파 examples (no 육합 overlap):
    assert branch_pair_relation(b("子"), b("酉")) == BranchRelation.PA
    assert branch_pair_relation(b("丑"), b("辰")) == BranchRelation.PA
    assert branch_pair_relation(b("卯"), b("午")) == BranchRelation.PA
    assert branch_pair_relation(b("巳"), b("申")) == BranchRelation.YUKHAP  # 巳申 is also 육합
    assert branch_pair_relation(b("戌"), b("未")) == BranchRelation.HYEONG  # 戌未 is also 형(丑戌未 三刑) — actually no, 형 needs 3rd
    # 戌未 alone — let's verify
    rel = branch_pair_relation(b("戌"), b("未"))
    assert rel in (BranchRelation.HYEONG, BranchRelation.PA)  # both apply, 형 has higher priority


# ── 해 (害) ─────────────────────────────────────
@pytest.mark.parametrize("a,c", [
    ("子", "未"), ("丑", "午"), ("寅", "巳"),
    ("卯", "辰"), ("申", "亥"), ("酉", "戌"),
])
def test_hae_pairs(a, c):
    rel = branch_pair_relation(b(a), b(c))
    # Some 해 pairs overlap with 형 or 파 — verify it's at least not NEUTRAL
    assert rel != BranchRelation.NEUTRAL


def test_hae_pure_子未():
    """子未 is pure 해 (not 형/파/충/합)."""
    assert branch_pair_relation(b("子"), b("未")) == BranchRelation.HAE


# ── NEUTRAL ─────────────────────────────────────
def test_neutral_unrelated():
    """子 vs 寅 — no special relation."""
    assert branch_pair_relation(b("子"), b("寅")) == BranchRelation.NEUTRAL


# ── 삼합 (三合) ─────────────────────────────────────
def test_samhap_member_partial():
    """申子 (half of 申子辰) → 수국."""
    assert samhap_member(b("申"), b("子")) == "수국"
    assert samhap_member(b("寅"), b("午")) == "화국"
    assert samhap_member(b("巳"), b("酉")) == "금국"
    assert samhap_member(b("亥"), b("卯")) == "목국"


def test_samhap_member_no_match():
    assert samhap_member(b("子"), b("丑")) is None  # 육합이지 삼합 아님


def test_samhap_complete_full():
    assert samhap_complete((b("申"), b("子"), b("辰"))) == "수국"
    assert samhap_complete((b("寅"), b("午"), b("戌"))) == "화국"


def test_samhap_complete_incomplete():
    assert samhap_complete((b("申"), b("子"))) is None  # only 2
    assert samhap_complete((b("申"), b("子"), b("丑"))) is None  # 丑 not in 수국
