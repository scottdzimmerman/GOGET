"""
parse_gfw_download.py

Migrated from Colab notebook: Parse GFW Download.ipynb
Auto-converted to a Python script. Colab-specific lines
(drive.mount, google.colab imports, shell/magic commands) have been
commented out and flagged; pip installs moved to ../requirements.txt.
"""

# ===== Cell 1 =====
import pandas as pd

# mount google drive, load in files
# [colab-only removed] from google.colab import drive
# [colab drive mount removed] drive.mount('/content/drive')

# define offshore infa
gfw_infa = pd.read_csv('/content/drive/MyDrive/GOGET q1 2026/GFW/sar_fixed_infrastructure_202510.csv')

# ===== Cell 2 =====
# check columns
gfw_infa.columns

# ===== Cell 3 =====
# check format of gfw_infa detection_date
gfw_infa['detection_date'].head()

# filter for rdetection dates in 2023 or more recent
gfw_infa_recent = gfw_infa[gfw_infa['detection_date'] >= '2023-01-01']

# ===== Cell 4 =====
# print length of recent and full
print(len(gfw_infa_recent))
print(len(gfw_infa))

# ===== Cell 5 =====
# check format of gfw_infa confidence
gfw_infa['label_confidence'].head()

# ===== Cell 6 =====
# keep only high confidence
gfw_infa_recent_high = gfw_infa_recent[gfw_infa_recent['label_confidence'] == 'high']

print(len(gfw_infa))
print(len(gfw_infa_recent))
print(len(gfw_infa_recent_high))

# ===== Cell 7 =====
# check format of gfw_infa detection_date
gfw_infa['label'].unique()

# ===== Cell 8 =====
gfw_infa_recent_high_oil = gfw_infa_recent_high[gfw_infa_recent_high['label'] == 'oil']

print(len(gfw_infa_recent_high))
print(len(gfw_infa_recent_high_oil))

# ===== Cell 9 =====
# keep only unique structure_id
gfw_infa_recent_high_oil = gfw_infa_recent_high_oil.drop_duplicates(subset=['structure_id'])

print(len(gfw_infa_recent_high_oil))

# ===== Cell 10 =====
# save out gfw_infa_recent_high_oil
gfw_infa_recent_high_oil.to_csv('/content/drive/MyDrive/GOGET q1 2026/GFW/gfw_infa_recent_high_oil.csv', index=False)
