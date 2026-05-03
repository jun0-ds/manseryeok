# manseryeok

한국식 만세력·사주 Python 라이브러리. **외부 의존성 0**, 1900-2100 절기 데이터, 진태양시·조자시 표준.

## 설계 원칙

- **Pure Python** (3.12+) — 표준 라이브러리만 (`datetime`, `dataclasses`)
- **타입 안전** — frozen dataclass + 풀 타입힌트
- **데이터·산술·해석 분리** — `data/`(lookup) ↔ `core/`(산술) ↔ `analysis/`(해석)
- **검증 가능** — 절기 데이터 출처 명시, 표준 만세력 케이스 통과

## 기준

| 항목 | 기준 |
|---|---|
| 입력 달력 | **양력** (음력 변환은 v0.2.0 이후) |
| 자시 처리 | **조자시(早子時)** — 23:00~24:00은 다음 날 자시 (현대 사주 표준) |
| 시간 보정 | **진태양시** — 출생지 경도 + 균시차 |
| 절기 데이터 | 1900-2100 (KASI 결과 기반) |
| 일주 기준점 | 1900-01-01 양력 = **갑술(甲戌)** 일 |

## 빠른 시작

```python
from datetime import datetime
from manseryeok import calculate_saju

saju = calculate_saju(
    birth=datetime(1992, 11, 28, 16, 0),  # 양력 + 申시 (16:00)
    longitude_deg=126.978,                  # 출생지 경도 (Seoul default)
    use_solar_time=True,
    early_zi=True,
)

print(saju.year)   # Pillar(stem='壬', branch='申', ...)
print(saju.month)  # Pillar(stem='辛', branch='亥', ...)
print(saju.day)    # Pillar(stem='戊', branch='申', ...)
print(saju.hour)   # Pillar(stem='庚', branch='申', ...)
```

## 분석

```python
from manseryeok.analysis import wuxing_relation, sipsin, zodiac_from_branch

# 오행 관계 (상생/상극/비화)
rel = wuxing_relation(saju.day.stem_wuxing, today.day.stem_wuxing)

# 십신 (일간 vs 천간)
ss = sipsin(day_stem=saju.day.stem, target_stem=today.day.stem)

# 띠
zodiac = zodiac_from_branch(saju.year.branch)  # "원숭이"
```

## Inspired by

[sajupy](https://github.com/0ssw1/sajupy) — 처음부터 다시 설계함 (외부 의존성 제거, 타입 안전 강화, 데이터 출처 명시).

## License

MIT
