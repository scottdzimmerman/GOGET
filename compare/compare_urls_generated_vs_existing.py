"""
compare_urls_generated_vs_existing.py

Migrated from Colab notebook: Compare URLs Generated vs Existing 2024 02 15
Auto-converted to a Python script. Colab-specific lines
(drive.mount, google.colab imports, shell/magic commands) have been
commented out and flagged; pip installs moved to ../requirements.txt.
"""

# ===== Cell 1 =====
import pandas as pd
from urllib.parse import urlparse, parse_qs, urlencode, unquote

def normalize_url(url):
    if pd.isnull(url) or not isinstance(url, str):
        return None  # Return None or some default value for invalid or missing URLs

    # Parse the URL
    parsed_url = urlparse(url)

    # Normalize the scheme and netloc
    scheme = 'https' if parsed_url.scheme in ['http', 'https'] else parsed_url.scheme
    netloc = parsed_url.netloc.lstrip('www.')

    # Sort query parameters
    query = urlencode(sorted(parse_qs(parsed_url.query, keep_blank_values=True).items()), doseq=True)

    # Remove trailing slash and decode percent-encoded characters, including parentheses
    path = unquote(parsed_url.path.rstrip('/'))

    # Reassemble the URL
    normalized_url = urlparse('')._replace(scheme=scheme, netloc=netloc, path=path, query=query).geturl()

    return normalized_url

def compare_urls(url1, url2):
    normalized_url1 = normalize_url(url1)
    normalized_url2 = normalize_url(url2)
    if normalized_url1 is None or normalized_url2 is None:
        return False  # Consider missing or invalid URLs as not matching
    return normalized_url1 == normalized_url2

# Load the CSV file
df = pd.read_csv('/content/GOGET 2024 Update_ Name Changes - Main data.csv')  # Adjust the path as necessary

# Iterate over rows and compare URLs
matches = []
for index, row in df.iterrows():
    url1 = row["Wiki URL - 2024 02 15 on GOGET Main"]
    url2 = row["2024-02-15 Wiki URL (Generated)"]
    matches.append(compare_urls(url1, url2))

# Add the comparison results to the DataFrame
df['URLs Match'] = matches

# Save the results back to a new CSV file
df.to_csv('/content/GOGET 2024 Update_ Name Changes - Main data 2024 02 15.csv', index=False)
