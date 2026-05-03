"""12 지지 (earthly branches).

Order: 子 丑 寅 卯 辰 巳 午 未 申 酉 戌 亥

Hour mapping: index 0 (子) corresponds to 23:00~01:00 (in early-zi convention,
treated as next day's 子).

Yin/Yang follows the standard convention used in modern Korean saju:
- Yang: 子 寅 辰 午 申 戌
- Yin:  丑 卯 巳 未 酉 亥
"""

from __future__ import annotations

from manseryeok.types import Branch, Wuxing, YinYang

BRANCHES: tuple[Branch, ...] = (
    Branch(char="子", kr="자", index=0, wuxing=Wuxing.WATER, yin_yang=YinYang.YANG, zodiac="쥐"),
    Branch(char="丑", kr="축", index=1, wuxing=Wuxing.EARTH, yin_yang=YinYang.YIN, zodiac="소"),
    Branch(char="寅", kr="인", index=2, wuxing=Wuxing.WOOD, yin_yang=YinYang.YANG, zodiac="호랑이"),
    Branch(char="卯", kr="묘", index=3, wuxing=Wuxing.WOOD, yin_yang=YinYang.YIN, zodiac="토끼"),
    Branch(char="辰", kr="진", index=4, wuxing=Wuxing.EARTH, yin_yang=YinYang.YANG, zodiac="용"),
    Branch(char="巳", kr="사", index=5, wuxing=Wuxing.FIRE, yin_yang=YinYang.YIN, zodiac="뱀"),
    Branch(char="午", kr="오", index=6, wuxing=Wuxing.FIRE, yin_yang=YinYang.YANG, zodiac="말"),
    Branch(char="未", kr="미", index=7, wuxing=Wuxing.EARTH, yin_yang=YinYang.YIN, zodiac="양"),
    Branch(char="申", kr="신", index=8, wuxing=Wuxing.METAL, yin_yang=YinYang.YANG, zodiac="원숭이"),
    Branch(char="酉", kr="유", index=9, wuxing=Wuxing.METAL, yin_yang=YinYang.YIN, zodiac="닭"),
    Branch(char="戌", kr="술", index=10, wuxing=Wuxing.EARTH, yin_yang=YinYang.YANG, zodiac="개"),
    Branch(char="亥", kr="해", index=11, wuxing=Wuxing.WATER, yin_yang=YinYang.YIN, zodiac="돼지"),
)

_BY_CHAR: dict[str, Branch] = {b.char: b for b in BRANCHES}
_BY_KR: dict[str, Branch] = {b.kr: b for b in BRANCHES}
_BY_ZODIAC: dict[str, Branch] = {b.zodiac: b for b in BRANCHES}


def branch_by_index(i: int) -> Branch:
    return BRANCHES[i % 12]


def branch_by_char(char: str) -> Branch:
    return _BY_CHAR[char]


def branch_by_kr(kr: str) -> Branch:
    return _BY_KR[kr]


def branch_by_zodiac(zodiac: str) -> Branch:
    """Lookup by Korean zodiac name (e.g., '쥐', '호랑이')."""
    return _BY_ZODIAC[zodiac]
