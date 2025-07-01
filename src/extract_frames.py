import cv2
import os
import pysrt


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
    subs = pysrt.open(srt_path)
    gps_data = {}
    for sub in subs:
        start_sec = int(sub.start.ordinal / 1000)
        gps_data[start_sec] = sub.text.strip()
    return gps_data


def extract_frames_with_gps(video_path: str, srt_path: str, output_folder: str) -> None:
    """Save one frame per second of ``video_path`` along with GPS data.

    The ``-> None`` return annotation means this function does not
    return any value. It simply writes frames to disk and prints
    messages during processing.

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
    duration = frame_count // fps

    for sec in range(duration):
        vidcap.set(cv2.CAP_PROP_POS_MSEC, sec * 1000)
        success, frame = vidcap.read()
        if success and sec in gps_data:
            filename = os.path.join(output_folder, f"frame_{sec:03d}.jpg")
            cv2.imwrite(filename, frame)
            print(f"Saved frame {sec}s -> {filename}")
            print(f"GPS: {gps_data[sec]}")
        else:
            print(f"Skipping second {sec} (no frame or no GPS data)")

    vidcap.release()


if __name__ == "__main__":
    VIDEO_FILE = os.path.join("footage", "your_video.mp4")
    SRT_FILE = os.path.join("footage", "your_video.srt")
    OUTPUT_DIR = "output"

    extract_frames_with_gps(VIDEO_FILE, SRT_FILE, OUTPUT_DIR)
