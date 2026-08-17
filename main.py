import json
from pathlib import Path
import urllib.request

DATA_FILE = Path("complete_hsk.json")
DATA_URL = "https://raw.githubusercontent.com/drkameleon/complete-hsk-vocabulary/main/complete.json"


def load_dataset(file_path: Path = DATA_FILE, url: str = DATA_URL) -> list:
    """Load HSK dataset locally, downloading it once if not present."""
    if not file_path.exists():
        print(f"Downloading dataset from {url}...")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as response:
            file_path.write_bytes(response.read())
        print(f"Saved dataset to {file_path.resolve()}")
    else:
        print(f"Loading cached dataset from {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def query_hsk(
    dataset: list,
    level: int,
    version: str = "new",
    exclusive_only: bool = True,
) -> list:
    """Query local HSK dataset by level.

    :param level: Target level (e.g., 3, 4)
    :param version: 'new' (HSK 3.0) or 'old' (HSK 2.0)
    :param exclusive_only: If True, returns words belonging exclusively to this level,
                           excluding words introduced in earlier levels.
    """
    target_tag = f"{version}-{level}"
    results = []

    for item in dataset:
        levels = item.get("level", [])
        if target_tag in levels:
            if exclusive_only:
                # Find the lowest level tag assigned to this entry for the target version
                version_tags = [
                    t for t in levels if t.startswith(f"{version}-")
                ]
                lowest_level = min(int(t.split("-")[1]) for t in version_tags)
                if lowest_level != level:
                    continue

            simplified = item.get("simplified")
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


# 1. Initialize dataset (downloads once (~9MB), reuses local file afterwards)
dataset = load_dataset()

# 2. Query exclusive HSK 3 words (HSK 3.0)
hsk3_words = query_hsk(dataset, level=3, version="new", exclusive_only=True)

print(f"\nFound {len(hsk3_words)} exclusive HSK 3 words:")
for word in hsk3_words[:5]:
    print(
        f"{word['simplified']} ({word['pinyin']}): {', '.join(word['meanings'])}"
    )
