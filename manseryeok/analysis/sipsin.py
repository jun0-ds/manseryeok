"""십신 (Ten gods).

Sipsin classifies the relation between the Day Master (일간) and another stem.
There are 10 categories, derived from two factors:
    1. Wuxing relation (generating/controlling/neutral) between day-master and target
    2. Same yin-yang vs different yin-yang

Categories (from day-master's perspective):
    비견(比肩) — same wuxing, same yin-yang
    겁재(劫財) — same wuxing, different yin-yang
    식신(食神) — day-master generates, same yin-yang
    상관(傷官) — day-master generates, different yin-yang
    편재(偏財) — day-master controls, same yin-yang
    정재(正財) — day-master controls, different yin-yang
    편관(偏官) — controls day-master, same yin-yang  (also 칠살)
    정관(正官) — controls day-master, different yin-yang
    편인(偏印) — generates day-master, same yin-yang
    정인(正印) — generates day-master, different yin-yang
"""

from __future__ import annotations

from enum import Enum

from manseryeok.analysis.wuxing import wuxing_relation
from manseryeok.types import Stem, WuxingRelation, YinYang


class Sipsin(str, Enum):
    BIGYEON = "비견"
    GEOPJAE = "겁재"
    SIKSIN = "식신"
    SANGGWAN = "상관"
    PYEONJAE = "편재"
    JEONGJAE = "정재"
    PYEONGWAN = "편관"
    JEONGGWAN = "정관"
    PYEONIN = "편인"
    JEONGIN = "정인"


def sipsin(*, day_stem: Stem, target_stem: Stem) -> Sipsin:
    """Compute sipsin of target_stem relative to day_stem (일간).

    Args:
        day_stem: 일간 (Day Master).
        target_stem: 비교 대상 천간 (e.g., 오늘 일주의 천간).
    """
    rel = wuxing_relation(day_stem.wuxing, target_stem.wuxing)
    same_yy = day_stem.yin_yang == target_stem.yin_yang

    match rel:
        case WuxingRelation.NEUTRAL:
            return Sipsin.BIGYEON if same_yy else Sipsin.GEOPJAE
        case WuxingRelation.GENERATING:  # day-master 가 살림 — 식상
            return Sipsin.SIKSIN if same_yy else Sipsin.SANGGWAN
        case WuxingRelation.CONTROLLING:  # day-master 가 누름 — 재성
            return Sipsin.PYEONJAE if same_yy else Sipsin.JEONGJAE
        case WuxingRelation.CONTROLLED_BY:  # day-master 가 눌림 — 관성
            return Sipsin.PYEONGWAN if same_yy else Sipsin.JEONGGWAN
        case WuxingRelation.GENERATED_BY:  # day-master 가 받음 — 인성
            return Sipsin.PYEONIN if same_yy else Sipsin.JEONGIN
