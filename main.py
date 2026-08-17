import argparse
import json
from pathlib import Path
import sys
import urllib.request

DATA_FILE = Path("complete_hsk.json")
DATA_URL = "https://raw.githubusercontent.com/drkameleon/complete-hsk-vocabulary/main/complete.json"


def load_dataset(file_path: Path = DATA_FILE, url: str = DATA_URL) -> list:
    """Load HSK dataset locally, downloading it once if not present."""
    if not file_path.exists():
        print(f"Downloading dataset from {url}...", file=sys.stderr)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as response:
            file_path.write_bytes(response.read())
        print(f"Saved dataset to {file_path.resolve()}", file=sys.stderr)

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def query_hsk(
    dataset: list,
    level: int,
    version: str = "new",
    exclusive: bool = True,
) -> list:
    """Query local HSK dataset by level and version."""
    target_tag = f"{version}-{level}"
    results = []

    for item in dataset:
        levels = item.get("level", [])
        if target_tag in levels:
            if exclusive:
                version_tags = [
                    t for t in levels if t.startswith(f"{version}-")
                ]
                lowest_level = min(int(t.split("-")[1]) for t in version_tags)
                if lowest_level != level:
                    continue

            simplified = item.get("simplified", "")
            form = item.get("forms", [{}])[0]
            pinyin = form.get("transcriptions", {}).get("pinyin", "")
            meanings = form.get("meanings", [])

            results.append(
                {
                    "simplified": simplified,
                    "pinyin": pinyin,
                    "meanings": meanings,
                    "levels": levels,
                }
            )

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Query local HSK vocabulary dataset from the command line."
    )
    parser.add_argument(
        "-l",
        "--level",
        type=int,
        required=True,
        help="HSK level number (1-6 for old, 1-7/9 for new)",
    )
    parser.add_argument(
        "-v",
        "--version",
        choices=["new", "old"],
        default="new",
        help="HSK version: 'new' (3.0) or 'old' (2.0) (default: new)",
    )
    parser.add_argument(
        "--inclusive",
        action="store_true",
        help="Include words introduced in lower levels (default: exclusive)",
    )
    parser.add_argument(
        "-n",
        "--limit",
        type=int,
        default=None,
        help="Limit output to first N words",
    )
    parser.add_argument(
        "-f",
        "--file",
        type=Path,
        default=DATA_FILE,
        help="Path to local cache JSON file",
    )

    args = parser.parse_args()

    dataset = load_dataset(file_path=args.file)
    words = query_hsk(
        dataset,
        level=args.level,
        version=args.version,
        exclusive=not args.inclusive,
    )

    mode = "inclusive" if args.inclusive else "exclusive"
    print(
        f"Found {len(words)} words for HSK {args.level} ({args.version.upper()} / {mode}):\n"
    )

    display_words = words[: args.limit] if args.limit else words
    for i, word in enumerate(display_words, 1):
        meanings_str = ", ".join(word["meanings"])
        print(f"{i:3d}. {word['simplified']} [{word['pinyin']}]: {meanings_str}")


if __name__ == "__main__":
    main()
