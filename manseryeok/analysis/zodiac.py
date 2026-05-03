"""띠 (Korean zodiac) ↔ 지지 (Earthly branch) mapping.

The zodiac is determined by the Year-pillar's branch:
    子(쥐) 丑(소) 寅(호랑이) 卯(토끼) 辰(용) 巳(뱀)
    午(말) 未(양) 申(원숭이) 酉(닭) 戌(개) 亥(돼지)
"""

from __future__ import annotations

from manseryeok.data.branches import branch_by_zodiac
from manseryeok.types import Branch

ZODIACS: tuple[str, ...] = (
    "쥐",
    "소",
    "호랑이",
    "토끼",
    "용",
    "뱀",
    "말",
    "양",
    "원숭이",
    "닭",
    "개",
    "돼지",
)


def zodiac_from_branch(branch: Branch) -> str:
    """Year branch → Korean zodiac name."""
    return branch.zodiac


def branch_from_zodiac(zodiac: str) -> Branch:
    """Korean zodiac name → year branch."""
    return branch_by_zodiac(zodiac)
