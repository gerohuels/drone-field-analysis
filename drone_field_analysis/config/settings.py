"""Configuration settings for Drone Field Analysis."""

import os

# Folder to store extracted frames and analysis results
# This directory will be created automatically if it does not exist.
OUTPUT_DIR = "output"

# Text file containing the object(s) the user wants to search for
SEARCH_TARGET_FILE = os.path.join(os.path.dirname(__file__), "search_target.txt")
