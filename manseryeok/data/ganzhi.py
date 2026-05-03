"""60갑자 cycle (sexagenary cycle) and day-pillar epoch.

The cycle repeats every 60 days/years/months. Each entry is a Pillar (Stem+Branch)
where stem advances by 1 every step (mod 10) and branch advances by 1 (mod 12).

Day-pillar epoch:
    1900-01-01 (Gregorian) = 甲戌 (index 10)
    JDN(1900-01-01) = 2415021
    => Day pillar index = (JDN - 2415011) mod 60

The base epoch (index 0 = 甲子) is therefore JDN 2415011 (1899-12-22).

Verified against standard manseryeok references:
- 1992-11-28 → 戊申 (index 44)  [JDN 2448955 - 2415011 = 33944, % 60 = 44]
"""

from __future__ import annotations

from manseryeok.data.branches import BRANCHES, branch_by_index
from manseryeok.data.stems import STEMS, stem_by_index
from manseryeok.types import Branch, Pillar, Stem

# Day-pillar epoch (index 0 = 甲子)
DAY_PILLAR_EPOCH_JDN: int = 2415011  # 1899-12-22 Gregorian
DAY_PILLAR_EPOCH_INDEX: int = 0


def _build_cycle() -> tuple[Pillar, ...]:
    """Build the 60갑자 sequence."""
    return tuple(
        Pillar(stem=STEMS[i % 10], branch=BRANCHES[i % 12], index=i) for i in range(60)
    )


GANZHI_CYCLE: tuple[Pillar, ...] = _build_cycle()


def pillar_from_index(i: int) -> Pillar:
    """Get the Pillar at position i in the 60갑자 cycle (0~59)."""
    return GANZHI_CYCLE[i % 60]


def pillar_from_stem_branch(stem: Stem, branch: Branch) -> Pillar:
    """Find the Pillar combining a given Stem and Branch.

    Raises ValueError if (stem, branch) is not a valid 60갑자 entry
    (e.g., 甲丑 — yang stem with yin branch — never appears).
    """
    for p in GANZHI_CYCLE:
        if p.stem.index == stem.index and p.branch.index == branch.index:
            return p
    raise ValueError(
        f"Invalid ganzhi combination: {stem.char}{branch.char} "
        f"(stem and branch yin/yang must match)"
    )
