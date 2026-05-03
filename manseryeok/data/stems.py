"""10 천간 (heavenly stems).

Order: 甲 乙 丙 丁 戊 己 庚 辛 壬 癸
"""

from __future__ import annotations

from manseryeok.types import Stem, Wuxing, YinYang

# Ordered tuple — index = position in 60-cycle
STEMS: tuple[Stem, ...] = (
    Stem(char="甲", kr="갑", index=0, wuxing=Wuxing.WOOD, yin_yang=YinYang.YANG),
    Stem(char="乙", kr="을", index=1, wuxing=Wuxing.WOOD, yin_yang=YinYang.YIN),
    Stem(char="丙", kr="병", index=2, wuxing=Wuxing.FIRE, yin_yang=YinYang.YANG),
    Stem(char="丁", kr="정", index=3, wuxing=Wuxing.FIRE, yin_yang=YinYang.YIN),
    Stem(char="戊", kr="무", index=4, wuxing=Wuxing.EARTH, yin_yang=YinYang.YANG),
    Stem(char="己", kr="기", index=5, wuxing=Wuxing.EARTH, yin_yang=YinYang.YIN),
    Stem(char="庚", kr="경", index=6, wuxing=Wuxing.METAL, yin_yang=YinYang.YANG),
    Stem(char="辛", kr="신", index=7, wuxing=Wuxing.METAL, yin_yang=YinYang.YIN),
    Stem(char="壬", kr="임", index=8, wuxing=Wuxing.WATER, yin_yang=YinYang.YANG),
    Stem(char="癸", kr="계", index=9, wuxing=Wuxing.WATER, yin_yang=YinYang.YIN),
)

_BY_CHAR: dict[str, Stem] = {s.char: s for s in STEMS}
_BY_KR: dict[str, Stem] = {s.kr: s for s in STEMS}


def stem_by_index(i: int) -> Stem:
    return STEMS[i % 10]


def stem_by_char(char: str) -> Stem:
    return _BY_CHAR[char]


def stem_by_kr(kr: str) -> Stem:
    return _BY_KR[kr]
