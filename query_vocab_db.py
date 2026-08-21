import io
import os
import re
import sys
import urllib.request
import zipfile
import pandas as pd

# --- STEP 1: Download CC-CEDICT ---
dict_file = "cedict_ts.u8"
if not os.path.exists(dict_file):
    print("Downloading CC-CEDICT archive...")
    url_dict = (
        "https://www.mdbg.net/chinese/export/cedict/cedict_1_0_ts_utf-8_mdbg.zip"
    )
    try:
        req = urllib.request.Request(
            url_dict, headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req) as response:
            with zipfile.ZipFile(io.BytesIO(response.read())) as z:
                z.extractall()
        print("CC-CEDICT extracted successfully.")
    except Exception as e:
        print(f"Error fetching CC-CEDICT: {e}", file=sys.stderr)
        sys.exit(1)

# --- STEP 2: Download SUBTLEX-CH Dataset (PLOS ONE Source) ---
freq_file = "SUBTLEX-CH-WF.txt"
if not os.path.exists(freq_file):
    print("Downloading SUBTLEX-CH dataset...")
    url_freq = "https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0010729.s002&type=supplementary"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/zip, application/octet-stream, */*",
    }

    try:
        req = urllib.request.Request(url_freq, headers=headers)
        with urllib.request.urlopen(req) as response:
            content = response.read()

        with zipfile.ZipFile(io.BytesIO(content)) as z:
            target_file = "SUBTLEX-CH-WF"
            if target_file not in z.namelist():
                target_file = [
                    f for f in z.namelist() if "SUBTLEX-CH-WF" in f
                ][0]

            with z.open(target_file) as src, open(freq_file, "wb") as dst:
                dst.write(src.read())

        print("SUBTLEX-CH downloaded and extracted successfully.")

    except Exception as e:
        print(
            f"Error fetching SUBTLEX-CH: {e}. Exiting script.", file=sys.stderr
        )
        sys.exit(1)

# --- STEP 3: Parse CC-CEDICT (UTF-8) ---
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

# Deduplicate dictionary entries per simplified word
df_dict_grouped = (
    df_dict.groupby("simp")
    .agg(
        {
            "trad": "first",
            "pinyin": lambda x: " / ".join(x.unique()),
            "definition": lambda x: " | ".join(x.unique()),
        }
    )
    .reset_index()
)

# --- STEP 4: Parse SUBTLEX-CH (GB18030) & Merge ---
try:
    # Skip top 2 metadata header lines
    df_freq = pd.read_csv(
        freq_file, sep="\t", skiprows=2, encoding="gb18030", engine="python"
    )

    # Clean header whitespace
    df_freq.columns = df_freq.columns.str.strip()

    # Identify frequency column name
    freq_col = (
        "W/million"
        if "W/million" in df_freq.columns
        else df_freq.columns[2]
    )

    # Merge grouped dictionary with frequency stats
    df = pd.merge(
        df_dict_grouped, df_freq, left_on="simp", right_on="Word", how="inner"
    )

    # Ensure numeric frequency and sort descending
    df[freq_col] = pd.to_numeric(df[freq_col], errors="coerce")
    df = df.sort_values(by=freq_col, ascending=False)

    # --- EXAMPLE QUERY ---
    print("\n--- TOP 10 HIGH-FREQUENCY WORDS CONTAINING '心' ---")
    xin_words = df[df["simp"].str.contains("心")][
        ["simp", "pinyin", freq_col, "definition"]
    ]
    print(xin_words.head(10).to_string(index=False))

except Exception as e:
    print(f"Error processing analysis query: {e}", file=sys.stderr)
    sys.exit(1)
