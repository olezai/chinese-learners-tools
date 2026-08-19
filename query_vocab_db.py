import io
import os
import re
import sys
import urllib.request
import zipfile
import pandas as pd

# --- STEP 1: Download and Unzip CC-CEDICT ---
url = "https://www.mdbg.net/chinese/export/cedict/cedict_1_0_ts_utf-8_mdbg.zip"
dict_file = "cedict_ts.u8"

if not os.path.exists(dict_file):
    print("Downloading CC-CEDICT archive...")
    try:
        # Add a User-Agent header to prevent automated request blocks
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as response:
            zip_content = response.read()

        with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
            z.extractall()
        print("Download and extraction successful.")
    except Exception as e:
        print(f"Error downloading or extracting dictionary: {e}", file=sys.stderr)
        sys.exit(1)

# --- STEP 2: Parse CC-CEDICT into DataFrame ---
pattern = re.compile(r"^(\S+)\s+(\S+)\s+\[(.*?)\]\s+/(.*)/$")
entries = []

try:
    with open(dict_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                continue
            match = pattern.match(line.strip())
            if match:
                trad, simp, pinyin, defs = match.groups()
                entries.append(
                    {
                        "simp": simp,
                        "trad": trad,
                        "pinyin": pinyin,
                        "definition": defs,
                    }
                )
except Exception as e:
    print(f"Error reading {dict_file}: {e}", file=sys.stderr)
    sys.exit(1)

df_dict = pd.DataFrame(entries)

# --- STEP 3: Merge with SUBTLEX-CH & Query ---
# Assumes SUBTLEX-CH-WF.xlsx is in the working directory
try:
    df_freq = pd.read_excel("SUBTLEX-CH-WF.xlsx")
    df = pd.merge(
        df_dict, df_freq, left_on="simp", right_on="Word", how="inner"
    ).sort_values(by="W_Million", ascending=False)

    # Example Query: Words with '心' (xīn)
    xin_words = df[df["simp"].str.contains("心")][
        ["simp", "pinyin", "W_Million", "definition"]
    ]
    print(xin_words.head(10))

except FileNotFoundError:
    print(
        "Notice: SUBTLEX-CH-WF.xlsx not found. Running queries on CC-CEDICT dictionary alone."
    )
    xin_words = df_dict[df_dict["simp"].str.contains("心")]
    print(xin_words.head(10))
