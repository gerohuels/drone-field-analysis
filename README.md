# drone-field-analysis
An app for analyzing drone footage to detect weeds and assess crop health. Visualizes results on a field map.

The application processes `.mp4` video footage of the field along with a corresponding `.srt` file that contains GPS location data from the drone.
It detects and identifies areas with weeds and dry spots in the field, saving frames where such objects are found, along with their GPS coordinates.
All detected objects are visualized on a field map for easy monitoring and analysis.

## Input files
Place your `.mp4` video and matching `.srt` file into the `footage/` folder before running the analysis.
