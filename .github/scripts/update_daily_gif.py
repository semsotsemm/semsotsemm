"""Select the profile GIF by weekday in Moscow; no external dependencies."""

from datetime import datetime
from pathlib import Path
import re
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
ASSETS_REVISION = "main"
BASE_URL = f"https://raw.githubusercontent.com/semsotsemm/readme-assets/{ASSETS_REVISION}"
PATTERN = re.compile(r"<!-- daily-gif:start -->.*?<!-- daily-gif:end -->", re.DOTALL)


def animation_for_day(weekday: int) -> int:
    """Monday = 0; Friday shows GIF 5; Saturday and Sunday show GIF 6."""
    if not 0 <= weekday <= 6:
        raise ValueError("weekday must be between 0 and 6")
    return min(weekday + 1, 6)


def update_readme(content: str, weekday: int) -> str:
    if len(PATTERN.findall(content)) != 1:
        raise ValueError("README must contain exactly one daily-gif marker pair")
    number = animation_for_day(weekday)
    width = 360 if number == 1 else 270
    replacement = (
        "<!-- daily-gif:start -->\n"
        f'  <img src="{BASE_URL}/{number}.gif" width="{width}" '
        f'alt="Profile animation {number}">\n'
        "<!-- daily-gif:end -->"
    )
    return PATTERN.sub(lambda _: replacement, content)


def main() -> None:
    readme = ROOT / "README.md"
    with readme.open(encoding="utf-8", newline="") as stream:
        original = stream.read()
    newline = "\r\n" if "\r\n" in original else "\n"
    local_time = datetime.now(ZoneInfo("Europe/Moscow"))
    updated = update_readme(original, local_time.weekday()).replace("\r\n", "\n")
    updated = updated.replace("\n", newline)
    if updated != original:
        with readme.open("w", encoding="utf-8", newline="") as stream:
            stream.write(updated)
    print(f"Moscow date: {local_time.date()}; GIF: {animation_for_day(local_time.weekday())}")


if __name__ == "__main__":
    main()
