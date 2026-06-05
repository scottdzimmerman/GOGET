"""
convert_image_to_spreadsheet.py

Migrated from Colab notebook: Convert Image to Spreadsheet 2024 10 17
Auto-converted to a Python script. Colab-specific lines
(drive.mount, google.colab imports, shell/magic commands) have been
commented out and flagged; pip installs moved to ../requirements.txt.
"""

# ===== Cell 1 =====
from PIL import Image
# [moved to requirements.txt] !pip install pytesseract
import os

import pytesseract

# ===== Cell 2 =====
# [shell cmd - run manually] !sudo apt install tesseract-ocr
# [shell cmd - run manually] !sudo apt install libtesseract-dev

# ===== Cell 3 =====
# Load the image
image_path = '/content/OGJ Reserves.jpeg'
img = Image.open(image_path)

# Use pytesseract to extract text from the image
text = pytesseract.image_to_string(img)

# Display the extracted text for review
text[:1500]  # Showing the first 1500 characters
