"""Frame extraction helpers.

This module handles pulling individual frames from drone footage and attaching
GPS information from the matching ``.srt`` subtitle track.  The resulting data
is stored in a ``pandas.DataFrame`` which is later used for analysis and
visualisation.
"""

import logging
import os
import re

import cv2
import pandas as pd
import pysrt

from ..config.settings import OUTPUT_DIR

logger = logging.getLogger(__name__)


def extract_gps_data_from_srt(srt_path):
    """Extract GPS data from an SRT file.

    Parameters
    ----------
    srt_path : str
        Path to the `.srt` subtitle file containing GPS information.

    Returns
    -------
    dict
        Mapping of second (int) -> GPS text (str).
    """
    # ``pysrt`` parses the subtitle file and gives us start/stop times
    subs = pysrt.open(srt_path)
    gps_data = {}
    for sub in subs:
        # Subtitle timings are provided in milliseconds, convert to seconds
        start_sec = int(sub.start.ordinal / 1000)
        gps_data[start_sec] = sub.text.strip()
    return gps_data


def parse_coordinates(gps_text: str):
    """Try to extract latitude and longitude from a line of GPS text.

    The function searches for the first two floating point numbers in the string
    and returns them as ``(lat, lon)`` if found. If parsing fails ``(None, None)``
    is returned.
    """
    # Search the text for floating point numbers that look like
    # latitude and longitude values.
    # The regex captures signed floating point numbers like -12.345
    numbers = re.findall(r"-?\d+\.\d+", gps_text)
    if len(numbers) >= 2:
        return float(numbers[0]), float(numbers[1])
    return None, None


def extract_frames_with_gps(
    video_path: str, srt_path: str, output_folder: str
) -> pd.DataFrame:
    """Save one frame per second of ``video_path`` along with GPS data.

    Returns a ``pandas.DataFrame`` with the columns ``frame`` and ``image_path``
    populated. Additional columns ``object_type``, ``description``,
    ``confidence`` and ``box_parameter`` are included for later population during
    object detection. Latitude/longitude information is also stored for mapping
    purposes.

    Parameters
    ----------
    video_path : str
        Path to the MP4 file.
    srt_path : str
        Path to the SRT file containing GPS data.
    output_folder : str
        Folder where extracted frames will be saved.
    """
    os.makedirs(output_folder, exist_ok=True)

    gps_data = extract_gps_data_from_srt(srt_path)

    vidcap = cv2.VideoCapture(video_path)
    fps = int(vidcap.get(cv2.CAP_PROP_FPS))
    frame_count = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    # Total duration in seconds (integer division avoids partial seconds)
    duration = frame_count // fps

    # Accumulated metadata for each extracted frame
    rows = []

    # Iterate through the video one second at a time and save each frame
    # together with the corresponding GPS information from the subtitle file.
    for sec in range(duration):
        # Jump to the current second in the video and grab a single frame
        vidcap.set(cv2.CAP_PROP_POS_MSEC, sec * 1000)
        success, frame = vidcap.read()
        if success and sec in gps_data:
            filename = os.path.join(output_folder, f"frame_{sec:03d}.jpg")
            cv2.imwrite(filename, frame)
            gps_text = gps_data[sec]
            lat, lon = parse_coordinates(gps_text)
            rows.append(
                {
                    "frame": sec,
                    "image_path": filename,
                    "latitude": lat,
                    "longitude": lon,
                    "gps_text": gps_text,
                    "object_type": None,
                    "report": None,
                    "description": None,
                    "confidence": None,
                    "box_parameter": None,
                    "boxed_image_path": None,
                }
            )
            logger.info("Saved frame %ss -> %s", sec, filename)
            logger.debug("GPS: %s", gps_text)
        else:
            logger.info("Skipping second %s (no frame or no GPS data)", sec)

    # Release the video capture handle when done
    vidcap.release()

    # Convert the collected ``rows`` list into a DataFrame so downstream
    # processing can easily access frame metadata
    df = pd.DataFrame(
        rows,
        columns=[
            "frame",
            "image_path",
            "latitude",
            "longitude",
            "gps_text",
            "object_type",
            "report",
            "description",
            "confidence",
            "box_parameter",
            "boxed_image_path",
        ],
    )
    return df


if __name__ == "__main__":
    VIDEO_FILE = os.path.join("footage", "your_video.mp4")
    SRT_FILE = os.path.join("footage", "your_video.srt")
    extract_frames_with_gps(VIDEO_FILE, SRT_FILE, OUTPUT_DIR)
