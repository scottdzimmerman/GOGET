"""
extract_field_totals_brazil_powerbi.py

Migrated from Colab notebook: Extract Field Totals from Brazil Bower BI table.ipynb
Auto-converted to a Python script. Colab-specific lines
(drive.mount, google.colab imports, shell/magic commands) have been
commented out and flagged; pip installs moved to ../requirements.txt.
"""

# ===== Cell 1 =====
# import libraries
# [moved to requirements.txt] !pip install pytesseract
import pytesseract
from PIL import Image
import pandas as pd

# ===== Cell 2 =====
# mount google drive
# [colab-only removed] from google.colab import drive
# [colab drive mount removed] drive.mount('/content/drive')

# define folders
goget_country_folder = '/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/Data sets & reports (O&G)/O&G country materials/'
country = 'Brazil (GOGET O&G)/' # change for country you are working on
screenshots = goget_country_folder + country + 'Production 2025/Screenshots/'

# ===== Cell 3 =====
# add screenshots from https://app.powerbi.com/view?r=eyJrIjoiZjZhZDliMTYtOWIyZi00OGY5LWJkYzItOTQ1MzFjZGMzMDNkIiwidCI6IjQ0OTlmNGZmLTI0YTYtNGI0Mi1iN2VmLTEyNGFmY2FkYzkxMyJ9
files = [
    "Jan 2025-1.png",

#    "oil production 2.png",
#    "oil production 3.png",
#    "oil production 4.png",
#    "oil production 5.png"
]

# ===== Cell 4 =====
# correct accents
accent_corrections = {
    "Agua": "Água",
    "Sabia": "Sabiá",
    "Sabiá Bico-De-Osso": "Sabiá Bico-de-Osso",
    "Sabiá da Mata": "Sabiá da Mata",
    "Acaja": "Acajá",
    "Açaja": "Acajá",
    "Araçás": "Araçás",
    "Araçás Leste": "Araçás Leste",
    "Azulao": "Azulão",
    "Camacari": "Camaçari",
    "Canario": "Canário",
    "Pajeu": "Pajeú",
    "Sao": "São"
}

# ===== Cell 5 =====
# extract text from screenshots

all_text = []
for file in files:
    img_path = screenshots + file # prepend the path to the file
    img = Image.open(img_path)
    text = pytesseract.image_to_string(img, lang="eng")  # English OCR still works well
    all_text.append(text)

combined_text = "\n".join(all_text)

# ===== Cell 6 =====
combined_text

# ===== Cell 7 =====
import re

def extract_field_production_final(text, accent_corrections):
    lines = text.splitlines()
    potential_field_names = []
    potential_production_values = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check if the line strictly matches the pattern of a production value
        if re.fullmatch(r'^[,\d]+\.?\d*$', line):
            try:
                value = float(line.replace(",", ""))
                potential_production_values.append(value)
            except ValueError:
                # If conversion fails, even with strict match, treat as potential field name
                potential_field_names.append(line)
        else:
            # If it doesn't strictly match the value pattern, treat as a potential field name
            potential_field_names.append(line)

    # Filter out likely headers and noise from potential field names
    field_names = []
    for name in potential_field_names:
        # Filter out empty strings and common headers/noise observed in the text
        if name and name.lower() not in ['campo', 'petrdleo (bbl/d)', 'producao', 'producao\npetrdleo (bbl/d)', ' ', '\x0c']:
            field_names.append(name)

    # Apply accent corrections to extracted field names
    corrected_field_names = [accent_corrections.get(name, name) for name in field_names]

    # At this point, we have two lists: corrected_field_names and potential_production_values.
    # The challenge is that they are not in corresponding order from the original text.
    # We need to assume a strict sequential pairing after cleaning.

    # Ensure lists have the same length by truncating to the minimum length
    min_len = min(len(corrected_field_names), len(potential_production_values))
    if len(corrected_field_names) != len(potential_production_values):
        print(f"Warning: Mismatch between number of extracted field names ({len(corrected_field_names)}) and production values ({len(potential_production_values)}). Truncating to {min_len}.")

    # Pair the corrected field names and production values based on their order
    extracted_data = list(zip(corrected_field_names[:min_len], potential_production_values[:min_len]))

    return extracted_data

# Apply the final parsing function to the combined_text from first screenshots
extracted_data_final = extract_field_production_final(combined_text, accent_corrections)

# Create a new DataFrame with the final data
df_final = pd.DataFrame(extracted_data_final, columns=["Campo", "Producao_petroleo_bbl_d"])

# ===== Cell 8 =====
# add in additional screenshots and create dataframes for each using the same process
additional_files = [
    "Jan 2025-2.png",
    "Jan 2025-3.png",
    "Jan 2025-4.png",
]

# ===== Cell 9 =====
# extract text from additional screenshots

aditional_text = []
for file in additional_files:
    img_path = screenshots + file # prepend the path to the file
    img = Image.open(img_path)
    text = pytesseract.image_to_string(img, lang="eng")  # English OCR still works well
    aditional_text.append(text)

additional_combined_text = "\n".join(aditional_text)

# ===== Cell 10 =====
# Apply the final parsing function to the combined_text from additonal screenshots
extracted_data_additional = extract_field_production_final(additional_combined_text, accent_corrections)

# Create a new DataFrame with the additional data
df_additional = pd.DataFrame(extracted_data_additional)

# ===== Cell 11 =====
# append df_additional to df_final
df_final = pd.concat([df_final, df_additional], ignore_index=True)

# ===== Cell 12 =====
df_final

# ===== Cell 13 =====
# save df out to a csv in the screenshots folder
df_final.to_csv(screenshots +'oilscreenshotstotable.csv')

# ===== Cell 14 =====
# do the same thing for gas
gas_files = [
    "gas production 1.png",
    "gas production 2.png",
    "gas production 3.png",
    "gas production 4.png"
]

# ===== Cell 15 =====
# extract text from screenshots

gas_text = []
for file in gas_files:
    img_path = screenshots + file # prepend the path to the file
    img = Image.open(img_path)
    text = pytesseract.image_to_string(img, lang="eng")  # English OCR still works well
    gas_text.append(text)

gas_combined_text = "\n".join(gas_text)

# ===== Cell 16 =====
gas_combined_text

# ===== Cell 17 =====
import re

def extract_gas_field_production_revised(text, accent_corrections):
    lines = text.splitlines()
    extracted_data = []
    campo_name = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check if the line contains a potential production value
        value_match = re.search(r'([\d,]+\.?\d*)$', line) # Anchor the regex to the end of the line

        if value_match:
            try:
                value_str = value_match.group(1).replace(",", "")
                value = float(value_str)

                # The part of the line before the number is the field name
                name_part = line[:value_match.start()].strip()

                # If we have a name part from this line, use it. Otherwise, use the accumulated campo_name.
                # This assumes a value is always preceded by its name on the same line, or the previous line(s) built up the name.
                # Given the previous issues, anchoring to the end and taking the preceding text seems more reliable.
                if name_part:
                    campo_name = name_part

                if campo_name:
                    # Apply accent corrections
                    corrected_campo = accent_corrections.get(campo_name, campo_name)
                    extracted_data.append((corrected_campo, value))
                    campo_name = None # Reset after successful pairing
                # If no campo_name and a value is found, it's an unpairable value, ignore for now.

            except ValueError:
                # If conversion fails, treat the whole line as a potential campo name
                if campo_name is None:
                    campo_name = line
                else:
                    campo_name += " " + line # Append to current campo name

        else:
            # If no value found, treat the whole line as a potential campo name or part of one
            if campo_name is None:
                campo_name = line
            else:
                campo_name += " " + line # Append to current campo name

    # A final pass to clean up the extracted data, removing likely headers or noise
    cleaned_data = [(campo, value) for campo, value in extracted_data if "Campo Producao gas" not in campo]

    return cleaned_data

# Apply the revised parsing function
extracted_data_gas_revised = extract_gas_field_production_revised(gas_combined_text, accent_corrections)

# Create a new DataFrame with the revised data
df_gas = pd.DataFrame(extracted_data_gas_revised, columns=["Campo", "Gas production (mil cubic meters/d)"])

# sort df_gas by gas production in descending order
df_gas = df_gas.sort_values(by="Gas production (mil cubic meters/d)", ascending=False)

# Display the resulting DataFrame
display(df_gas)

# ===== Cell 18 =====
# save df out to a csv in the screenshots folder
df_gas.to_csv(screenshots +'gasscreenshotstotable.csv')

# ===== Cell 19 =====
# sort df_gas by gas production
df_gas = df_gas.sort_values(by="Gas production (mil cubic meters/d)", ascending=False)

df_gas

# # Task
# Parse the gas production data from the provided screenshots, which has been combined into the `gas_combined_text` variable. Create a pandas DataFrame named `df_gas` with two columns: "Campo" and "Gas production (mil cubic meters/d)". Ensure that all field names and their corresponding gas production values are correctly extracted and paired in the DataFrame. Explain the parsing logic used.

# ## Analyze the raw gas text patterns
#
# ### Subtask:
# Carefully examine the `gas_combined_text` output, paying close attention to how field names and production values are structured on lines, how multi-line names are handled, and how entries are separated across the different screenshots.

# **Reasoning**:
# To analyze the structure of the combined text from the gas production screenshots, I need to print the `gas_combined_text` variable to the console as the first step.
#

# ===== Cell 20 =====
print(gas_combined_text)

# ## Identify reliable anchors or patterns
#
# ### Subtask:
# Identify reliable anchors or patterns in the `gas_combined_text` that can help reliably distinguish field names from production values and correctly pair them.

# ## Develop a robust gas parsing function
#
# ### Subtask:
# Create a Python function `extract_gas_field_production_final` that takes the `gas_combined_text` and `accent_corrections` as input and returns a list of (Campo, Gas production) tuples.

# **Reasoning**:
# Define the `extract_gas_field_production_final` function as per the instructions, iterating through lines, accumulating potential field names, and pairing with production values when found.
#

# ===== Cell 21 =====
import re

def extract_gas_field_production_final(text, accent_corrections):
    lines = text.splitlines()
    extracted_data = []
    current_campo_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Use a regular expression to search for a pattern that matches the numerical format of production values
        # This regex looks for digits, commas, and an optional decimal part with a period.
        value_match = re.search(r'([\d,]+\.?\d*)', line)

        if value_match:
            try:
                # Extract the matched value string and convert it to float after removing commas
                value_str = value_match.group(1).replace(",", "")
                value = float(value_str)

                # If we have collected campo lines, join them and pair with the value
                if current_campo_lines:
                    campo_name = " ".join(current_campo_lines).strip()
                    if campo_name: # Ensure campo name is not empty after joining
                         # Apply accent corrections if present
                         corrected_campo = accent_corrections.get(campo_name, campo_name)
                         extracted_data.append((corrected_campo, value))
                    current_campo_lines = [] # Reset after pairing

            except ValueError:
                 # If it looked like a value but wasn't, add to potential campo lines
                 current_campo_lines.append(line)

        else:
            # If no value found, add the line to potential campo lines
            current_campo_lines.append(line)

    # After iterating through all lines, we might have remaining campo lines without a value.
    # We will discard these as they don't have corresponding data.

    return extracted_data

# ## Apply the gas parsing function and create dataframe
#
# ### Subtask:
# Apply the `extract_gas_field_production_final` function to process the `gas_combined_text` and create the `df_gas` DataFrame.

# **Reasoning**:
# Apply the parsing function to the combined gas text and create the DataFrame.
#

# ===== Cell 22 =====
# Apply the final parsing function to the gas_combined_text from additional screenshots
extracted_data_gas = extract_gas_field_production_final(gas_combined_text, accent_corrections)

# Create a new DataFrame with the additional data
df_gas = pd.DataFrame(extracted_data_gas, columns=["Campo", "Gas production (mil cubic meters/d)"])

# **Reasoning**:
# Display the head of the created DataFrame to verify the data extraction and structure.
#

# ===== Cell 23 =====
df_gas.head()

# **Reasoning**:
# The DataFrame has been created. However, there are some invalid rows from the header or parsing errors. Filter out these rows and then sort the DataFrame by the gas production values in descending order to complete the subtask and show the result.
#

# ===== Cell 24 =====
# Filter out rows where 'Campo' likely represents a header or invalid entry
df_gas = df_gas[~df_gas['Campo'].str.contains("Campo Producao gas", na=False)]

# sort df_gas by gas production in descending order
df_gas = df_gas.sort_values(by="Gas production (mil cubic meters/d)", ascending=False)

# Display the filtered and sorted DataFrame
df_gas.head()

# ## Validate the `df gas` dataframe
#
# ### Subtask:
# Thoroughly inspect the `df_gas` DataFrame to ensure all field names and their corresponding gas production values are present and correctly paired.

# **Reasoning**:
# Display the entire df_gas DataFrame to visually inspect its contents and verify the parsing and pairing.
#

# ===== Cell 25 =====
display(df_gas)

# **Reasoning**:
# The previous display shows that the parsing logic still has issues, including incomplete field names and incorrect pairings. The current parsing logic which relies on joining lines until a number is found is not robust enough for the observed inconsistencies. A different approach is needed.
#

# ===== Cell 26 =====
import re

def extract_gas_field_production_revised(text, accent_corrections):
    lines = text.splitlines()
    extracted_data = []
    campo_name = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check if the line contains a potential production value
        value_match = re.search(r'([\d,]+\.?\d*)$', line) # Anchor the regex to the end of the line

        if value_match:
            try:
                value_str = value_match.group(1).replace(",", "")
                value = float(value_str)

                # The part of the line before the number is the field name
                name_part = line[:value_match.start()].strip()

                # If we have a name part from this line, use it. Otherwise, use the accumulated campo_name.
                # This assumes a value is always preceded by its name on the same line, or the previous line(s) built up the name.
                # Given the previous issues, anchoring to the end and taking the preceding text seems more reliable.
                if name_part:
                    campo_name = name_part

                if campo_name:
                    # Apply accent corrections
                    corrected_campo = accent_corrections.get(campo_name, campo_name)
                    extracted_data.append((corrected_campo, value))
                    campo_name = None # Reset after successful pairing
                # If no campo_name and a value is found, it's an unpairable value, ignore for now.

            except ValueError:
                # If conversion fails, treat the whole line as a potential campo name
                if campo_name is None:
                    campo_name = line
                else:
                    campo_name += " " + line # Append to current campo name

        else:
            # If no value found, treat the whole line as a potential campo name or part of one
            if campo_name is None:
                campo_name = line
            else:
                campo_name += " " + line # Append to current campo name

    # A final pass to clean up the extracted data, removing likely headers or noise
    cleaned_data = [(campo, value) for campo, value in extracted_data if "Campo Producao gas" not in campo]

    return cleaned_data

# Apply the revised parsing function
extracted_data_gas_revised = extract_gas_field_production_revised(gas_combined_text, accent_corrections)

# Create a new DataFrame with the revised data
df_gas = pd.DataFrame(extracted_data_gas_revised, columns=["Campo", "Gas production (mil cubic meters/d)"])

# sort df_gas by gas production in descending order
df_gas = df_gas.sort_values(by="Gas production (mil cubic meters/d)", ascending=False)

# Display the resulting DataFrame
display(df_gas)

# ## Summary:
#
# ## Summary of Gas Production Data Parsing
#
# ### Data Analysis Key Findings
#
# *   The initial parsing attempt of the `gas_combined_text` variable resulted in an incomplete and incorrectly paired `df_gas` DataFrame, with truncated field names and misassociated production values.
# *   A revised parsing logic, implemented in the `extract_gas_field_production_revised` function, significantly improved extraction and pairing by using a regular expression anchored to the end of lines to identify values and extracting the preceding text as field names.
# *   The revised parsing successfully generated a `df_gas` DataFrame with 126 rows, indicating a more comprehensive extraction of data compared to the initial attempt.
#
# ### Insights or Next Steps
#
# *   The revised parsing function is robust for this specific text structure but may need adjustments for different data formats.
# *   The `df_gas` DataFrame is now ready for further analysis or visualization to identify key gas producing fields.
