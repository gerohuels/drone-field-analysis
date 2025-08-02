# drone-field-analysis
**This app is under development.**

Drone Field Analysis makes it simple for growers to see problem spots in their fields. Just load a drone video and its GPS subtitles and the app will highlight bare soil areas, animals, or weeds. Results are shown as pictures and pins on a map for easy viewing.


## Technical overview

A Python application for analyzing agricultural drone footage to locate bare spots, animals, and weeds in fields. Detected areas are visualized on an interactive map.

**Main menu**

<img width="555" height="555" alt="Screenshot 2025-07-23 at 23 12 57" src="https://github.com/user-attachments/assets/2b1ea278-5c71-4e49-878f-574e7439a24f" />

**Full-size view of a selected  thumbnail**

<img width="555" height="555" alt="Screenshot 2025-07-23 at 23 25 50" src="https://github.com/user-attachments/assets/57f05a28-fcb8-48d8-9484-184016b08476" />

<br>

**Map view showing detections with an open tooltip**

<img width="555" height="555" alt="Screenshot 2025-07-23 at 15 37 44" src="https://github.com/user-attachments/assets/93e63f0d-eee5-42dc-923a-f57e880533be" />


The application processes `.mp4` video footage of the field together with a matching `.srt` file containing GPS location data.
It identifies bare soil patches or animals in the field and saves the matching frames with their coordinates to the `output/` directory.
All detections are also visualized on a field map for easy monitoring and analysis. Each marker opens a popup with an embedded preview image for quick review.

The GUI presents a scrollable list of all findings. Clicking a thumbnail opens the full-size frame along with its GPS information.
Use the **Clear Output** button at any time to remove old results from the output directory.


## Input files
Place your `.mp4` video and matching `.srt` file into the `footage/` folder before running the analysis.


## AI bare spot, animal, and weed detection

The `drone_field_analysis/utils/data_processing.py` module demonstrates how to analyze the extracted frames using a
local language model accessed through [LangChain](https://www.langchain.com/) and served by
[Ollama](https://ollama.com/). Each frame is sent to the selected model with instructions to look
for large, clearly visible bare soil patches, animals, or weeds. If the model detects a
matching object with high confidence it triggers the appropriate reporting function,
printing the estimated location and confidence score.


## Configuration

Ensure an Ollama server is running locally and optionally set the `OLLAMA_MODEL`
environment variable to select a model. All frames and analysis results are
written to the directory defined in `drone_field_analysis/config/settings.py`
(default is `output/`). Adjust this value if you want to store results somewhere
else.

## Running the application

Install the dependencies listed in `requirements.txt` and start the GUI with:

```bash
python main.py
```


## User Flow

1. Launch the program with the command above. The main window opens.
2. Click **Browse** beside *MP4 File* and select your drone video.
3. Click **Browse** beside *SRT File* and choose the matching subtitle file containing GPS data.
4. Choose whether to search for *Bare spots*, *Animals*, or *Weeds* and press **Scan** to analyze each extracted frame.
5. Detected spots appear in the results list as image thumbnails.
6. Click any thumbnail to view the full image with its GPS coordinates. The subtitle's raw GPS
   information is displayed automatically when available.
7. When scanning finishes, press **Show on Map** to open a browser displaying all detections. Enable *Show Flight Path* to visualize the drone's route.
8. Press **Clear Output** to delete all extracted frames and results once you no longer need them.


## Button Guide

- **Browse** – open a file dialog to select the MP4 footage or matching SRT subtitle file.
- **Look For** – drop-down menu to pick whether to search for *Bare spots*, *Animals*, or *Weeds*.
- **Scan** – start the extraction and analysis process for every frame.
- **Show on Map** – open the interactive map of all detections once scanning is complete.
- **Show Flight Path** – toggle drawing the drone's route on the map.
- **Clear Output** – delete everything in the output folder after confirmation.
- Clicking a **thumbnail** in the results list opens the full-sized image with its GPS information.


## Features
The list below highlights the technical capabilities implemented by the application.
  
- Extracts one frame per second from the video, pairing each frame with GPS data from the subtitle file.
- Runs object detection with a local LLM via LangChain and Ollama, returning bounding box coordinates for each finding.
- Draws bounding boxes on the saved frames using OpenCV for easy visual confirmation.
- Stores all metadata in a pandas DataFrame and writes a `results.csv` file for further analysis.
- Processes frames in a background thread to keep the Tkinter interface responsive.
- Presents a scrollable list of thumbnails that open full-size images with detailed location information.
- Generates an interactive Folium map with color-coded markers and optional display of the drone's flight path.
- Provides a button to clear the output directory for a new run.


### Dependencies

- [LangChain](https://www.langchain.com/) & [Ollama](https://ollama.com/) - Local LLM integration for bare spot, animal, and weed detection.
- [OpenCV](https://opencv.org/) - Extracts frames from the drone footage.
- [pysrt](https://github.com/byroot/pysrt) - Parses subtitle files containing GPS coordinates.
- [Pillow](https://python-pillow.org/) - Image loading and thumbnail generation.
- [Folium](https://github.com/python-visualization/folium) - Renders the interactive map with popups.
- [pandas](https://pandas.pydata.org/) - Stores extraction and detection results in a single DataFrame.



### Acknowledgments
This project uses the Pandas library, © The Pandas Development Team, licensed under the BSD 3-Clause License.
