"""
pe_map_parse.py

Migrated from Colab notebook: PE Map Parse
Auto-converted to a Python script. Colab-specific lines
(drive.mount, google.colab imports, shell/magic commands) have been
commented out and flagged; pip installs moved to ../requirements.txt.
"""

# ===== Cell 1 =====
import json
import csv
from shapely.geometry import shape, Point, Polygon, MultiPolygon

# Import data, define output
input_filepath = '/content/PE Map, geojson.json'  # Path to the input JSON file
output_csv_filepath = 'output.csv'  # Path to the output CSV file
columns_to_remove = ['last_edited_user', 'last_edited_date']  # List the keys/columns you want to remove

# ===== Cell 2 =====

def calculate_centroid(geometry):
    """Calculate and return the centroid of a given geometry."""
    if geometry is None:
        return None  # Handle None before trying to use the shape function
    try:
        shapely_geom = shape(geometry)
        centroid = shapely_geom.centroid
        return {'type': 'Point', 'coordinates': [centroid.x, centroid.y]}
    except (ValueError, TypeError):
        print("Invalid geometry provided.")
        return None

def remove_columns_and_calculate_centroids(input_file, output_file, columns_to_remove):
    # Load the JSON data from file
    with open(input_file, 'r') as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return

    # Process the correct JSON structure
    if isinstance(data, dict) and "features" in data:
        data = data["features"]
    else:
        print("JSON does not contain 'features' key or is not a dictionary")
        return

    csv_data = []
    for item in data:
        if not isinstance(item, dict):
            print("Skipping item, expected dict, got:", type(item))
            continue

        # Remove specified columns
        cleaned_item = {key: value for key, value in item.items() if key not in columns_to_remove}

        # Calculate centroid if geometry is valid and exists
        if 'geometry' in item and isinstance(item['geometry'], dict):
            centroid = calculate_centroid(item['geometry'])
            if centroid:
                cleaned_item['centroid'] = f"{centroid['coordinates'][0]}, {centroid['coordinates'][1]}"
            else:
                cleaned_item['centroid'] = "Invalid geometry"
        else:
            cleaned_item['centroid'] = "No geometry"

        csv_data.append(cleaned_item)

    # Write to CSV file
    if csv_data:
        field_names = list(set(key for item in csv_data for key in item))
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=field_names)
            writer.writeheader()
            writer.writerows(csv_data)
    else:
        print("No data to write to CSV.")


remove_columns_and_calculate_centroids(input_filepath, output_csv_filepath, columns_to_remove)

# ===== Cell 3 =====
remove_columns_and_calculate_centroids(input_filepath, output_csv_filepath, columns_to_remove)

# ===== Cell 4 =====
remove_columns_and_calculate_centroids(input_filepath, output_csv_filepath, columns_to_remove)
