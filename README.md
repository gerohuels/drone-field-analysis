# drone-field-analysis
**This app is under development.**

A Python application for analyzing agricultural drone footage to locate bare spots and animals in fields. Detected areas are visualized on an interactive map.

![Main menu screenshot](https://github.com/user-attachments/assets/3411ca3e-d507-4cae-9685-a223fbc913ef)

**Main menu screenshot**

![Full-size view of a selected thumbnail](https://github.com/user-attachments/assets/b7257ed3-f23f-4f6c-b358-dbb9129e6eb5)

**Full-size view of a selected thumbnail**

![Map view showing detections with an open tooltip](https://github.com/user-attachments/assets/10dbed14-80cc-4109-a7cd-b34165f31edb)

**Map view showing detections with an open tooltip**


The application processes `.mp4` video footage of the field along with a corresponding `.srt` file that contains GPS location data from the drone.
It can identify bare soil patches or animals in the field, saving frames where such areas are found along with their GPS coordinates.
All detections are visualized on a field map for easy monitoring and analysis. Each marker opens a popup containing a preview image for quick review.

The GUI presents a scrollable list of all findings. Clicking a thumbnail opens the full-size frame along with its GPS information.

## Input files
Place your `.mp4` video and matching `.srt` file into the `footage/` folder before running the analysis.

## AI bare spot and animal detection

The `drone_field_analysis/utils/data_processing.py` module demonstrates how to analyze the extracted frames using
the OpenAI API. Each frame is sent to the `gpt-4o` model with instructions to look
for large, clearly visible bare soil patches or animals. If the model detects a
matching object with high confidence it triggers the appropriate reporting function,
printing the estimated location and confidence score.

Set the `OPENAI_API_KEY` environment variable before running this script.

## Running the application

Install the dependencies listed in `requirements.txt` and start the GUI with:

```bash
python main.py
```

## User Flow

1. Launch the program with the command above. The main window opens.
2. Click **Browse** beside *MP4 File* and select your drone video.
3. Click **Browse** beside *SRT File* and choose the matching subtitle file containing GPS data.
4. Choose whether to search for *Bare spots*, *Animals* or *Both* and press **Scan** to analyze each extracted frame.
5. Detected spots appear in the **Found Elements** list as image thumbnails.
6. Click any thumbnail to view the full image with its GPS coordinates. The subtitle's raw GPS
   information is displayed automatically when available.
7. When scanning finishes, press **Show on Map** to open a browser displaying all detections. Enable *Show Flight Path* to visualize the drone's route.

## Features

- Extracts one frame per second from the footage and stores its GPS location.
- Uses the OpenAI GPT-4o model to spot large bare soil areas or animals depending on the selected option.
- Optionally draws a bounding box around each detection on the saved frame.
- Scrollable interface with thumbnails and descriptions of all findings.
- Interactive map showing detections and the drone's flight path.
- Drop-down menu lets you search for **Bare spots**, **Animals** or **Both**.

### Dependencies

- [OpenAI Python](https://github.com/openai/openai-python) - Access to the GPT models for bare spot and animal detection.
- [OpenCV](https://opencv.org/) - Extracts frames from the drone footage.
- [pysrt](https://github.com/byroot/pysrt) - Parses subtitle files containing GPS coordinates.
- [Pillow](https://python-pillow.org/) - Image loading and thumbnail generation.
- [Folium](https://github.com/python-visualization/folium) - Renders the interactive map with popups.
- [pandas](https://pandas.pydata.org/) - Stores extraction and detection results in a single DataFrame.

## Known Bugs

- Bounding boxes drawn around detected objects are sometimes imprecise.

## Potential Next Features

- Detecting weeds

### Acknowledgments
This project uses the Pandas library, © The Pandas Development Team, licensed under the BSD 3-Clause License.
