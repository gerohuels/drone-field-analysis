# drone-field-analysis
An app for analyzing drone footage to detect weeds and assess crop health. Visualizes results on a field map.

The application processes `.mp4` video footage of the field along with a corresponding `.srt` file that contains GPS location data from the drone.
It detects and identifies areas with weeds and dry spots in the field, saving frames where such objects are found, along with their GPS coordinates.
All detected objects are visualized on a field map for easy monitoring and analysis. Each marker now opens a popup containing a preview image of the detection for quick review.

The GUI presents a scrollable list of all findings. Clicking a thumbnail opens the full-size frame along with its GPS information.

## Input files
Place your `.mp4` video and matching `.srt` file into the `footage/` folder before running the analysis.

## AI bare spot detection

The `drone_field_analysis/utils/data_processing.py` module demonstrates how to analyze the extracted frames using
the OpenAI API. A frame is sent to the `gpt-4o` model with instructions to look
for large, clearly visible bare soil patches. If the model detects such a bare
spot with high confidence it triggers the `report_bare_spot` function, printing
the estimated location and confidence score.

Set the `OPENAI_API_KEY` environment variable before running this script.

## Running the application

Install the dependencies listed in `requirements.txt` and start the GUI with:

```bash
python main.py
```

### Dependencies

- [OpenAI Python](https://github.com/openai/openai-python) - Access to the GPT models for bare spot detection.
- [OpenCV](https://opencv.org/) - Extracts frames from the drone footage.
- [pysrt](https://github.com/byroot/pysrt) - Parses subtitle files containing GPS coordinates.
- [Pillow](https://python-pillow.org/) - Image loading and thumbnail generation.
- [Folium](https://github.com/python-visualization/folium) - Renders the interactive map with popups.
