"""대운(大運) — 10년 단위 운 기둥.

대운은 생년월일·성별·월주·절기로 *한 번* 산출되며 평생 불변(시퀀스 고정).
"지금 몇 대운인가"만 현재 나이로 인덱싱한다(Daeun.at_age).

알고리즘:
    1. 순역: 년간 음양 × 성별 — 양남·음녀 = 순행, 음남·양녀 = 역행.
    2. 대운수(첫 대운 시작 나이): 출생에서 (순행)다음 / (역행)이전 节气(월경계 절기)까지
       일수 ÷ 3, 반올림 (3일 = 1년의 표준 약식 환산). 최소 1.
    3. 시퀀스: 월주 다음(순행)/이전(역행) 간지부터 60갑자를 10년씩.

대운수 환산 관례(3일=1년, 나머지 월수 세분 등)는 유파마다 다르다 — 본 구현은 round(일수/3)의
정수 나이 약식. 더 세밀한 관례가 필요하면 start_age 산출만 교체하면 된다.
"""

from __future__ import annotations

from datetime import datetime

from manseryeok.core.julian import datetime_to_jd
from manseryeok.core.pillars import _ensure_kst_aware, calculate_saju
from manseryeok.core.solar_terms import solar_term_jd
from manseryeok.core.solar_time import KST_TIMEZONE, SEOUL_LONGITUDE_DEG
from manseryeok.data.ganzhi import pillar_from_index
from manseryeok.types import Daeun, DaeunPeriod, YinYang

_MALE_TOKENS = frozenset({"M", "MALE", "MAN", "남", "남자"})


def _is_male(gender: str | bool) -> bool:
    if isinstance(gender, bool):
        return gender
    return str(gender).strip().upper() in _MALE_TOKENS


def daeun(
    *,
    birth: datetime,
    gender: str | bool,
    longitude_deg: float = SEOUL_LONGITUDE_DEG,
    use_solar_time: bool = True,
    early_zi: bool = True,
    count: int = 9,
) -> Daeun:
    """대운 시퀀스를 산출한다 (평생 고정).

    Args:
        birth: 출생 datetime (KST naive 허용).
        gender: 'M'/'F'/'남'/'여' 또는 bool(남=True).
        count: 산출할 대운 개수 (기본 9 → 약 90년 커버).
    """
    birth = _ensure_kst_aware(birth)
    birth_jd = datetime_to_jd(birth)
    saju = calculate_saju(
        birth=birth,
        longitude_deg=longitude_deg,
        use_solar_time=use_solar_time,
        early_zi=early_zi,
    )

    male = _is_male(gender)
    year_yang = saju.year.stem.yin_yang is YinYang.YANG
    forward = year_yang == male  # 양남·음녀 = 순행

    # 출생 전후 가장 가까운 节气(월경계, even-indexed term) JD — 3년 창으로 경계 커버
    year = birth.astimezone(KST_TIMEZONE).year
    boundaries = sorted(
        solar_term_jd(y, i * 2)
        for y in (year - 1, year, year + 1)
        for i in range(12)
    )
    prev_jd = max(j for j in boundaries if j <= birth_jd)
    next_jd = min(j for j in boundaries if j > birth_jd)

    span_days = (next_jd - birth_jd) if forward else (birth_jd - prev_jd)
    start_age = max(1, round(span_days / 3.0))  # 3일 = 1년 (약식)

    step = 1 if forward else -1
    periods = tuple(
        DaeunPeriod(
            start_age=start_age + 10 * k,
            pillar=pillar_from_index((saju.month.index + step * (k + 1)) % 60),
        )
        for k in range(count)
    )
    return Daeun(start_age=start_age, forward=forward, periods=periods)


__all__ = ["daeun"]
