"""
iran_coordinate_conversion.py

Migrated from Colab notebook: Iran Coordinate conversion for Norah 2024 09 25.ipynb
Auto-converted to a Python script. Colab-specific lines
(drive.mount, google.colab imports, shell/magic commands) have been
commented out and flagged; pip installs moved to ../requirements.txt.
"""

# ===== Cell 1 =====
# [moved to requirements.txt] pip install utm

# ===== Cell 2 =====
import utm

# UTM coordinates: Easting, Northing, Zone number, Hemisphere (True for Northern)
easting = 740400  # in meters, change this for each entry
northing = 3549800  # in meters, change this for each entry
zone_number = 38  # Iraq mostly falls in zone 38N - leave this

# Convert UTM to latitude and longitude
latitude, longitude = utm.to_latlon(easting, northing, zone_number, northern=True)

# Output the result
print(f"Latitude: {latitude}, Longitude: {longitude}")
