"""12지지 관계 — 충(沖)·합(合)·형(刑)·회(會)·파(破)·해(害).

These pairwise/triadic relations between earthly branches are central to
saju interpretation, especially for daily/yearly fortune (운세).

Categories returned in priority order (strongest first):
    회(會) 삼합 — 3 branches forming an elemental bureau (申子辰=수, ...)
    충(沖) — exact opposite branches (子↔午, ...)
    합(合) 육합 — 6 binary harmonies (子丑, 寅亥, ...)
    형(刑) — 3-刑 (寅巳申, 丑戌未) + 自刑 + 子卯 相刑
    파(破) — 6 pairs of weak conflict
    해(害) — 6 pairs of weak harm
    NEUTRAL — none of the above
"""

from __future__ import annotations

from enum import Enum

from manseryeok.types import Branch


class BranchRelation(str, Enum):
    """Pairwise relation between two branches."""

    SAMHAP = "삼합"  # 3-branch elemental bureau (회국)
    CHUNG = "충"  # opposite (沖)
    YUKHAP = "육합"  # binary harmony (合)
    HYEONG = "형"  # punishment (刑)
    PA = "파"  # break (破)
    HAE = "해"  # harm (害)
    NEUTRAL = "일반"


# ── 충 (沖) 6 pairs ─────────────────────────────────────
# Branches 6 apart: (0,6), (1,7), (2,8), (3,9), (4,10), (5,11)
_CHUNG_PAIRS: frozenset[frozenset[int]] = frozenset(
    frozenset({i, i + 6}) for i in range(6)
)


# ── 육합 (六合) 6 pairs ─────────────────────────────────────
# 子丑(0,1), 寅亥(2,11), 卯戌(3,10), 辰酉(4,9), 巳申(5,8), 午未(6,7)
_YUKHAP_PAIRS: frozenset[frozenset[int]] = frozenset({
    frozenset({0, 1}),
    frozenset({2, 11}),
    frozenset({3, 10}),
    frozenset({4, 9}),
    frozenset({5, 8}),
    frozenset({6, 7}),
})


# ── 삼합 (三合) 4 triads, each forming an element bureau ─────────────────
# 申子辰 → 수국, 寅午戌 → 화국, 巳酉丑 → 금국, 亥卯未 → 목국
_SAMHAP_TRIADS: tuple[tuple[frozenset[int], str], ...] = (
    (frozenset({8, 0, 4}), "수국"),  # 申子辰
    (frozenset({2, 6, 10}), "화국"),  # 寅午戌
    (frozenset({5, 9, 1}), "금국"),  # 巳酉丑
    (frozenset({11, 3, 7}), "목국"),  # 亥卯未
)


# ── 형 (刑) ─────────────────────────────────────
# 三刑: 寅巳申 (2,5,8), 丑戌未 (1,10,7) — any 2 of these = 형
# 自刑: 진진(4,4), 오오(6,6), 유유(9,9), 해해(11,11) — same branch
# 相刑: 자묘(0,3) — bidirectional
_HYEONG_THREE: tuple[frozenset[int], ...] = (
    frozenset({2, 5, 8}),  # 寅巳申
    frozenset({1, 10, 7}),  # 丑戌未
)
_HYEONG_SELF: frozenset[int] = frozenset({4, 6, 9, 11})  # 辰午酉亥
_HYEONG_MUTUAL: frozenset[frozenset[int]] = frozenset({frozenset({0, 3})})  # 子卯


# ── 파 (破) 6 pairs ─────────────────────────────────────
# 子酉(0,9), 丑辰(1,4), 寅亥(2,11), 卯午(3,6), 巳申(5,8), 戌未(10,7)
# Note: 寅亥 also is 육합 — when both apply, 합 takes priority
_PA_PAIRS: frozenset[frozenset[int]] = frozenset({
    frozenset({0, 9}),
    frozenset({1, 4}),
    frozenset({2, 11}),
    frozenset({3, 6}),
    frozenset({5, 8}),
    frozenset({10, 7}),
})


# ── 해 (害) 6 pairs ─────────────────────────────────────
# 子未(0,7), 丑午(1,6), 寅巳(2,5), 卯辰(3,4), 申亥(8,11), 酉戌(9,10)
_HAE_PAIRS: frozenset[frozenset[int]] = frozenset({
    frozenset({0, 7}),
    frozenset({1, 6}),
    frozenset({2, 5}),
    frozenset({3, 4}),
    frozenset({8, 11}),
    frozenset({9, 10}),
})


def branch_pair_relation(a: Branch, b: Branch) -> BranchRelation:
    """Pairwise relation between two branches.

    Priority: 충 > 육합 > 형 > 파 > 해 > NEUTRAL.
    삼합 is intentionally excluded here (it's a 3-branch relation; use
    `samhap_member()` to check if two branches are members of the same triad).
    Self-형 (e.g., 辰辰) is returned only if a.index == b.index AND in _HYEONG_SELF.
    """
    pair = frozenset({a.index, b.index})

    if a.index != b.index and pair in _CHUNG_PAIRS:
        return BranchRelation.CHUNG
    if pair in _YUKHAP_PAIRS:
        return BranchRelation.YUKHAP

    # 형 — three flavors
    if a.index == b.index and a.index in _HYEONG_SELF:
        return BranchRelation.HYEONG
    if pair in _HYEONG_MUTUAL:
        return BranchRelation.HYEONG
    for triad in _HYEONG_THREE:
        if a.index in triad and b.index in triad and a.index != b.index:
            return BranchRelation.HYEONG

    if a.index != b.index and pair in _PA_PAIRS:
        return BranchRelation.PA
    if a.index != b.index and pair in _HAE_PAIRS:
        return BranchRelation.HAE
    return BranchRelation.NEUTRAL


def samhap_member(a: Branch, b: Branch) -> str | None:
    """If a and b belong to the same 삼합 triad, return the bureau name (e.g., '수국').

    Two-out-of-three is enough — a 半合 (half-삼합) still implies the bureau.
    """
    if a.index == b.index:
        return None
    for triad, bureau in _SAMHAP_TRIADS:
        if a.index in triad and b.index in triad:
            return bureau
    return None


def samhap_complete(branches: tuple[Branch, ...]) -> str | None:
    """If 3 distinct branches complete a 삼합 triad, return the bureau name."""
    indices = frozenset(b.index for b in branches)
    if len(indices) < 3:
        return None
    for triad, bureau in _SAMHAP_TRIADS:
        if triad.issubset(indices):
            return bureau
    return None
