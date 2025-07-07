"""Tkinter GUI for interacting with the drone field analysis pipeline."""

import logging
import tkinter as tk

from tkinter import filedialog, messagebox
from typing import cast
import os
import webbrowser
import base64

import folium

from PIL import Image, ImageTk, ImageDraw
import pandas as pd

from ..utils.frame_extractor import extract_frames_with_gps
from ..utils.data_processing import analyze_frame
from ..config.settings import OUTPUT_DIR

logger = logging.getLogger(__name__)


class DroneFieldGUI(tk.Tk):
    """Main application window."""

    def __init__(self):
        """Initialize the GUI and set up default state."""
        super().__init__()
        self.title("Drone Field Analyzer")
        self.mp4_path = tk.StringVar()
        self.srt_path = tk.StringVar()
        # Store metadata and detection results for each extracted frame
        self.data = pd.DataFrame(
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
            ]
        )

        # Hold references to thumbnail images to prevent garbage collection
        self.result_images = []
        # Widgets created during setup
        self.results_canvas = None
        self.results_container = None
        self.show_map_button = None
        self.create_widgets()

    def create_widgets(self):
        """Create all Tkinter widgets used in the main window."""
        tk.Label(
            self, text="Drone Field Analyzer", font=("Helvetica", 16, "bold")
        ).grid(row=0, column=0, columnspan=3, pady=10)

        tk.Label(self, text="MP4 File:").grid(
            row=1, column=0, sticky="e", padx=5, pady=5
        )
        tk.Entry(self, width=40, textvariable=self.mp4_path).grid(
            row=1, column=1, padx=5, pady=5
        )
        tk.Button(self, text="Browse", command=self.browse_mp4).grid(
            row=1, column=2, padx=5, pady=5
        )

        tk.Label(self, text="SRT File:").grid(
            row=2, column=0, sticky="e", padx=5, pady=5
        )
        tk.Entry(self, width=40, textvariable=self.srt_path).grid(
            row=2, column=1, padx=5, pady=5
        )
        tk.Button(self, text="Browse", command=self.browse_srt).grid(
            row=2, column=2, padx=5, pady=5
        )
        tk.Button(self, text="Scan", command=self.scan).grid(
            row=4, column=0, columnspan=3, pady=10
        )
        tk.Label(self, text="Found Elements").grid(row=5, column=0, columnspan=3)

        self.results_canvas = tk.Canvas(self, width=400, height=200)
        scrollbar = tk.Scrollbar(
            self, orient="vertical", command=self.results_canvas.yview
        )
        self.results_canvas.configure(yscrollcommand=scrollbar.set)

        self.results_canvas.grid(
            row=6, column=0, columnspan=3, padx=10, pady=5, sticky="nsew"
        )
        scrollbar.grid(row=6, column=3, sticky="ns")

        self.results_container = tk.Frame(self.results_canvas)
        self.results_canvas.create_window(
            (0, 0), window=self.results_container, anchor="nw"
        )
        self.results_container.bind(
            "<Configure>",
            lambda e: self.results_canvas.configure(
                scrollregion=self.results_canvas.bbox("all")
            ),
        )

        self.show_map_button = tk.Button(
            self,
            text="Show on Map",
            command=self.show_map,
            state="disabled",
        )
        self.show_map_button.grid(row=7, column=0, columnspan=3, pady=10)

        self.show_path_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            self,
            text="Show Flight Path",
            variable=self.show_path_var,
        ).grid(row=8, column=0, columnspan=3)

    def browse_mp4(self):
        """Prompt the user to select an MP4 file."""
        path = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4")])
        if path:
            self.mp4_path.set(path)

    def browse_srt(self):
        """Prompt the user to select an SRT subtitle file."""
        path = filedialog.askopenfilename(filetypes=[("SRT files", "*.srt")])
        if path:
            self.srt_path.set(path)


    def show_full_image(
        self,
        img_path: str,
        report: str,
        confidence: float,
        lat,
        lon,
        gps_text: str = "",
    ) -> None:
        """Display a larger preview of a detection.

        Parameters
        ----------
        img_path:
            Path to the image file to display.
        report:
            Text describing the detected bare spot.
        confidence:
            Confidence score returned by the detection model.
        lat, lon:
            GPS coordinates associated with the frame.
        gps_text:
            Raw GPS text from the subtitle track.
        """
        top = tk.Toplevel(self)
        top.title("Image Viewer")

        with Image.open(img_path) as img:
            img = img.resize((600, 600))
            img_photo = cast(tk.PhotoImage, ImageTk.PhotoImage(img))

        img_label = tk.Label(top, image=img_photo)
        img_label.image = img_photo  # keep reference
        img_label.pack()

        info_lines = []
        if gps_text:
            info_lines.append(f"GPS: {gps_text}")
        info_lines.append(f"Report: {report}")
        info_lines.append(f"Confidence: {confidence:.2f}")
        info = "\n".join(info_lines)
        tk.Label(top, text=info, font=("Arial", 12)).pack(pady=10)

    def add_finding(self, row):
        """Insert a detected bare spot into the results list."""
        filename = row.get("boxed_image_path") or row["image_path"]
        report = row.get("report") or ""
        confidence = row.get("confidence")
        object_type = row.get("object_type")
        lat = row["latitude"]
        lon = row["longitude"]
        gps_text = row["gps_text"]

        with Image.open(filename) as thumb_img:
            thumb_img.thumbnail((100, 100))
            photo = cast(tk.PhotoImage, ImageTk.PhotoImage(thumb_img))
        self.result_images.append(photo)

        #Klick on full thumbnail for full-image
        frame = tk.Frame(self.results_container, bd=1, relief="solid", padx=5, pady=5)
        img_label = tk.Label(frame, image=photo, cursor="hand2")
        img_label.pack(side="left")
        img_label.bind(
            "<Button-1>",
            lambda e, p=filename, r=report, c=confidence, la=lat, lo=lon, g=gps_text: self.show_full_image(
                p, r, c, la, lo, g
            ),
        )
        text = f"Report: {report}\nFinding: {object_type}"
        tk.Label(frame, text=text, justify="left", wraplength=250).pack(
            side="left", padx=5
        )

        packed_children = self.results_container.pack_slaves()
        if packed_children:
            frame.pack(fill="x", padx=5, pady=5, before=packed_children[0])
        else:
            frame.pack(fill="x", padx=5, pady=5)

    def show_map(self):
        """Open a browser map visualizing all detections."""

        found_df = self.data.dropna(subset=["object_type"])
        if found_df.empty:
            messagebox.showinfo("No Findings", "No findings to display on the map.")
            return

        if not self.data.empty:
            first_point = self.data.sort_values("frame").iloc[0]
            map_center = [first_point.get("latitude"), first_point.get("longitude")]
        else:
            first_point = found_df.iloc[0]
            map_center = [first_point.get("latitude"), first_point.get("longitude")]

        mymap = folium.Map(location=map_center, zoom_start=15)

        for _, entry in found_df.iterrows():
            image_path = entry.get("boxed_image_path") or entry["image_path"]
            image_file = os.path.basename(image_path)
            
            # 🔧 Read image and convert to base64
            try:
                with open(image_path, "rb") as img_file:
                    img_base64 = base64.b64encode(img_file.read()).decode("utf-8")
            except Exception as e:
                logger.error("Failed to load image %s: %s", image_path, e)
                img_base64 = ""

            # 🖼️ Create HTML content with base64 image embedded
            report_text = entry.get("report", "")
            image_html = f"""
                <div>
                    <strong>{report_text}</strong><br>
                    <img src="data:image/jpeg;base64,{img_base64}" width="200">
                </div>
            """
            iframe = folium.IFrame(html=image_html, width=220, height=250)
            popup = folium.Popup(iframe, max_width=250)

            # Tooltip as plain text only (image in tooltip not reliable)
            tooltip = entry.get("object_type", "")
            folium.Marker(
                location=[entry["latitude"], entry["longitude"]],
                popup=popup,
                tooltip=tooltip,
                icon=folium.Icon(color="beige"),
            ).add_to(mymap)

        self.add_flight_path(mymap)

        output_map = os.path.join(OUTPUT_DIR, "findings_map.html")
        mymap.save(output_map)

        abs_map_path = os.path.abspath(output_map)
        webbrowser.open_new_tab(f"file://{abs_map_path}")

    def add_flight_path(self, mymap):
        """Add a polyline showing the drone's path to ``mymap`` if enabled."""
        if not self.data.empty and self.show_path_var.get():
            path_points = []
            for _, info in self.data.sort_values("frame").iterrows():
                lat = info.get("latitude")
                lon = info.get("longitude")
                if pd.notna(lat) and pd.notna(lon):
                    path_points.append((lat, lon))
            if len(path_points) >= 2:
                folium.PolyLine(
                    path_points,
                    color="blue",
                    weight=2,
                    opacity=0.7,
                ).add_to(mymap)

    def scan(self):
        """Run frame extraction and bare spot detection."""
        mp4 = self.mp4_path.get()
        srt = self.srt_path.get()
        if not mp4 or not srt:
            messagebox.showerror(
                "Missing Files", "Please select both MP4 and SRT files before scanning."
            )
            return

        if self.show_map_button:
            # Disable map button until the scan has completed
            self.show_map_button.config(state="disabled")

        output_dir = OUTPUT_DIR
        try:
            self.data = extract_frames_with_gps(mp4, srt, output_dir)
            for idx, row in self.data.iterrows():
                result = analyze_frame(row["image_path"])
                if result:
                    self.data.at[idx, "object_type"] = result["object_type"]
                    self.data.at[idx, "report"] = result["report"]
                    self.data.at[idx, "description"] = result["description"]
                    self.data.at[idx, "confidence"] = result["confidence"]
                    self.data.at[idx, "box_parameter"] = result.get("box_parameter")
                    boxed_path = row["image_path"]
                    if result.get("box_parameter"):
                        try:
                            img = Image.open(row["image_path"])
                            draw = ImageDraw.Draw(img)
                            # Outline the detected region on the image
                            draw.rectangle(
                                tuple(result["box_parameter"]), outline="blue", width=5
                            )
                            # Save boxed image next to the original frame
                            boxed_path = (
                                row["image_path"].rsplit(".", 1)[0] + "_boxed.jpg"
                            )
                            img.save(boxed_path)
                        except Exception as e:
                            logger.error("Failed to draw box on %s: %s", row["image_path"], e)
                            boxed_path = row["image_path"]
                    self.data.at[idx, "boxed_image_path"] = boxed_path
                    # Insert the detection into the on-screen results list
                    self.add_finding(self.data.loc[idx])
            messagebox.showinfo("Scan Complete", f"Frames saved to '{output_dir}'")
            if self.show_map_button:
                # Enable map button once processing is finished
                self.show_map_button.config(state="normal")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))


if __name__ == "__main__":
    app = DroneFieldGUI()
    app.mainloop()
