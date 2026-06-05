"""
name_matching.py

Migrated from Colab notebook: Name Matching 2024 12 23
Auto-converted to a Python script. Colab-specific lines
(drive.mount, google.colab imports, shell/magic commands) have been
commented out and flagged; pip installs moved to ../requirements.txt.
"""

# ===== Cell 1 =====
import pandas as pd
# [moved to requirements.txt] !pip install fuzzywuzzy
# [moved to requirements.txt] !pip install python-Levenshtein

from fuzzywuzzy import fuzz, process
from fuzzywuzzy import fuzz, process

# ===== Cell 2 =====
def fuzzy_match_names(list1, list2, threshold=90):
    """
    Perform fuzzy matching between two lists of names and return matches above a similarity threshold.

    :param list1: List of names to compare from.
    :param list2: List of names to compare against.
    :param threshold: Minimum similarity score to consider a match (default: 80).
    :return: A dictionary where keys are names from list1 and values are best matches from list2 with scores.
    """
    matches = {}

    for name in list1:
        best_match, score = process.extractOne(name, list2, scorer=fuzz.token_sort_ratio)
        if score >= threshold:
            matches[name] = (best_match, score)

    return matches

if __name__ == "__main__":
    # File paths
    file1 = "/content/2024 03 18 Rystad Reference Sheet (Main).xlsx - Texas Unmatch (1).csv"
    file2 = "/content/2024 03 18 Rystad Reference Sheet (Main).xlsx - 2024 12 23 Owners.csv"

    # Load CSVs into pandas DataFrames
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    # Assuming you want to match on a column named 'Name'
    list1 = df1['Owner'].tolist()
    list2 = df2['Owner'].tolist()

    # Perform fuzzy matching
    matches = fuzzy_match_names(list1, list2)

    # Print matches
    for name, (match, score) in matches.items():
        print(f"{name} -> {match} (Score: {score})")

# ===== Cell 3 =====
# save matches as a csv
matches_df = pd.DataFrame(list(matches.items()), columns=['Name', 'Match'])
matches_df.to_csv('matches.csv', index=False)
