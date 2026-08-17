import requests

# Fetch full database (~9MB)
url = "https://raw.githubusercontent.com/drkameleon/complete-hsk-vocabulary/main/complete.json"
dataset = requests.get(url).json()


def query_hsk(dataset, level_tag="new-3"):
    """Query words matching a specific level tag (e.g., 'new-1', 'old-4', 'new-7')."""
    matches = []
    for item in dataset:
        if level_tag in item.get("level", []):
            word = item["simplified"]
            form = item["forms"][0]
            pinyin = form["transcriptions"]["pinyin"]
            meanings = "; ".join(form["meanings"])
            matches.append((word, pinyin, meanings))
    return matches


# Query all HSK 4 words
hsk4_matches = query_hsk(dataset, level_tag="new-4")
print(f"Found {len(hsk4_matches)} HSK 4 words.")
