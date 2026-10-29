"""Generate a small, animated SVG from live Streak Stats data (stdlib only)."""

from datetime import date
from html import escape
import json
from pathlib import Path
import time
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "profile" / "streak.svg"
SOURCE = "https://streak-stats.demolab.com/?user=semsotsemm&type=json&timezone=Europe%2FMoscow"
MONTHS = (
    "января", "февраля", "марта", "апреля", "мая", "июня",
    "июля", "августа", "сентября", "октября", "ноября", "декабря",
)


def format_date(value):
    if not value:
        return "—"
    day = date.fromisoformat(value)
    return f"{day.day} {MONTHS[day.month - 1]} {day.year}"


def validate_stats(stats):
    if not isinstance(stats, dict) or stats.get("mode") != "daily":
        raise ValueError("Expected daily streak statistics")
    counts = [stats["totalContributions"]]
    format_date(stats["firstContribution"])
    for key in ("currentStreak", "longestStreak"):
        streak = stats[key]
        counts.append(streak["length"])
        start, end = streak["start"], streak["end"]
        format_date(start)
        format_date(end)
        if start and end and date.fromisoformat(start) > date.fromisoformat(end):
            raise ValueError(f"Invalid {key} date range")
    if any(type(number) is not int or number < 0 for number in counts):
        raise ValueError("Contribution counts must be non-negative integers")
    return stats


def date_lines(x, start, end=None):
    first = escape(format_date(start))
    second = escape("— " + format_date(end) if end else "— настоящее время")
    if not start:
        second = ""
    return (
        f'<text class="dates" x="{x}" y="179">{first}</text>\n'
        f'<text class="dates" x="{x}" y="197">{second}</text>'
    )


def render(stats):
    stats = validate_stats(stats)
    total = stats["totalContributions"]
    current = stats["currentStreak"]
    longest = stats["longestStreak"]
    # Accent elements share one slow colour cycle; text and background stay still.
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="220" viewBox="0 0 600 220" role="img" aria-labelledby="title desc">
  <title id="title">GitHub contribution streak — semsotsemm</title>
  <desc id="desc">Всего вкладов: {total}. Текущая серия: {current["length"]}. Самая длинная серия: {longest["length"]}.</desc>
  <defs>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="1.2" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <style>
    text {{ font-family: "Segoe UI", Arial, sans-serif; text-anchor: middle; }}
    .number {{ font-size: 32px; font-weight: 700; }}
    .label {{ fill: #f0f6fc; font-size: 13px; }}
    .dates {{ fill: #a0a8b4; font-size: 12px; }}
    .accent-fill {{ fill: #58a6ff; animation: rainbow-fill 12s linear infinite; }}
    .accent-stroke {{ stroke: #58a6ff; animation: rainbow-stroke 12s linear infinite; }}
    @keyframes rainbow-fill {{
      0%,100% {{ fill: #58a6ff; }} 20% {{ fill: #bc8cff; }}
      40% {{ fill: #ff7eb6; }} 60% {{ fill: #f2cc60; }} 80% {{ fill: #56d8b3; }}
    }}
    @keyframes rainbow-stroke {{
      0%,100% {{ stroke: #58a6ff; }} 20% {{ stroke: #bc8cff; }}
      40% {{ stroke: #ff7eb6; }} 60% {{ stroke: #f2cc60; }} 80% {{ stroke: #56d8b3; }}
    }}
    @media (prefers-reduced-motion: reduce) {{
      .accent-fill, .accent-stroke {{ animation: none; }}
    }}
  </style>
  <rect width="600" height="220" rx="20" fill="#0d1117"/>
  <path d="M200 32V201 M400 32V201" stroke="#30363d" stroke-width="1"/>
  <text class="number accent-fill" x="100" y="90" filter="url(#glow)">{total}</text>
  <text class="label" x="100" y="148">Total Contributions</text>
  {date_lines(100, stats["firstContribution"])}
  <circle class="accent-stroke" cx="300" cy="82" r="43" fill="none" stroke-width="5" stroke-dasharray="250 21" transform="rotate(-76 300 82)" filter="url(#glow)"/>
  <path class="accent-fill" d="M301 20C305 25 310 28 307 34C306 38 299 40 295 36C291 32 295 28 297 25C297 29 298 31 300 31C303 30 302 24 301 20Z" filter="url(#glow)"/>
  <text class="number" x="300" y="93" fill="#f0f6fc">{current["length"]}</text>
  <text class="label" x="300" y="148" font-weight="700">Current Streak</text>
  {date_lines(300, current["start"], current["end"])}
  <text class="number accent-fill" x="500" y="90" filter="url(#glow)">{longest["length"]}</text>
  <text class="label" x="500" y="148">Longest Streak</text>
  {date_lines(500, longest["start"], longest["end"])}
</svg>
'''


def fetch_stats():
    request = Request(SOURCE, headers={"User-Agent": "semsotsemm-profile", "Accept": "application/json"})
    for attempt in range(3):
        try:
            with urlopen(request, timeout=25) as response:
                return validate_stats(json.load(response))
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2)


def main():
    # Write only after a valid response: a service outage must not erase the card.
    content = render(fetch_stats())
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != content:
        temporary = OUTPUT.with_suffix(".tmp")
        temporary.write_text(content, encoding="utf-8", newline="\n")
        temporary.replace(OUTPUT)
    print(f"Updated {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
