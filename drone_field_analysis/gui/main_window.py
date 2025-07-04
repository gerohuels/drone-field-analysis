import tkinter as tk
from tkinter import filedialog, messagebox
from typing import cast
import os
import webbrowser

import folium

from PIL import Image, ImageTk

from ..utils.frame_extractor import extract_frames_with_gps
from ..utils.data_processing import analyze_frame
from ..config.settings import OUTPUT_DIR

class DroneFieldGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Drone Field Analyzer")
        self.mp4_path = tk.StringVar()
        self.srt_path = tk.StringVar()
        self.findings = []

        self.result_images = []
        self.results_canvas = None
        self.results_container = None
        self.show_map_button = None
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Drone Field Analyzer", font=("Helvetica", 16, "bold")).grid(row=0, column=0, columnspan=3, pady=10)

        tk.Label(self, text="MP4 File:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(self, width=40, textvariable=self.mp4_path).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(self, text="Browse", command=self.browse_mp4).grid(row=1, column=2, padx=5, pady=5)

        tk.Label(self, text="SRT File:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(self, width=40, textvariable=self.srt_path).grid(row=2, column=1, padx=5, pady=5)
        tk.Button(self, text="Browse", command=self.browse_srt).grid(row=2, column=2, padx=5, pady=5)

        tk.Button(self, text="Add Files", command=self.show_not_implemented).grid(row=3, column=0, columnspan=3, pady=10)
        tk.Button(self, text="Scan", command=self.scan).grid(row=4, column=0, columnspan=3, pady=10)

        tk.Label(self, text="Found Elements").grid(row=5, column=0, columnspan=3)


        self.results_canvas = tk.Canvas(self, width=400, height=200)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=self.results_canvas.yview)
        self.results_canvas.configure(yscrollcommand=scrollbar.set)

        self.results_canvas.grid(row=6, column=0, columnspan=3, padx=10, pady=5, sticky="nsew")
        scrollbar.grid(row=6, column=3, sticky="ns")

        self.results_container = tk.Frame(self.results_canvas)
        self.results_canvas.create_window((0, 0), window=self.results_container, anchor="nw")
        self.results_container.bind(
            "<Configure>",
            lambda e: self.results_canvas.configure(scrollregion=self.results_canvas.bbox("all"))
        )

        self.show_map_button = tk.Button(
            self,
            text="Show on Map",
            command=self.show_map,
            state="disabled",
        )
        self.show_map_button.grid(row=7, column=0, columnspan=3, pady=10)



    def browse_mp4(self):
        path = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4")])
        if path:
            self.mp4_path.set(path)

    def browse_srt(self):
        path = filedialog.askopenfilename(filetypes=[("SRT files", "*.srt")])
        if path:
            self.srt_path.set(path)

    def show_not_implemented(self):
        tk.messagebox.showinfo("Not Implemented", "This functionality is not implemented yet.")

    def show_full_image(self, img_path: str, description: str, lat, lon) -> None:
        """Open a new window displaying a larger version of the image."""
        top = tk.Toplevel(self)
        top.title("Image Viewer")

        img = Image.open(img_path)
        img = img.resize((600, 600))
        img_photo = cast(tk.PhotoImage, ImageTk.PhotoImage(img))

        img_label = tk.Label(top, image=img_photo)
        img_label.image = img_photo  # keep reference
        img_label.pack()

        info = f"Lat: {lat}\nLon: {lon}\n{description}"
        tk.Label(top, text=info, font=("Arial", 12)).pack(pady=10)

    def add_finding(self, filename: str, description: str, lat, lon):
        entry = {
            "filename": filename,
            "description": description,
            "latitude": lat,
            "longitude": lon,
        }
        self.findings.append(entry)


        thumb = Image.open(filename)
        thumb.thumbnail((100, 100))
        photo = cast(tk.PhotoImage, ImageTk.PhotoImage(thumb))
        self.result_images.append(photo)

        frame = tk.Frame(self.results_container, bd=1, relief="solid", padx=5, pady=5)
        img_label = tk.Label(frame, image=photo, cursor="hand2")
        img_label.pack(side="left")
        img_label.bind(
            "<Button-1>",
            lambda e, p=filename, d=description, la=lat, lo=lon: self.show_full_image(p, d, la, lo),
        )
        text = f"Lat: {lat}\nLon: {lon}\n{description}"
        tk.Label(frame, text=text, justify="left", wraplength=250).pack(side="left", padx=5)

        # ``pack(before=...)`` raises ``TclError`` if the referenced widget is
        # not currently managed by ``pack``. Using ``pack_slaves`` ensures that
        # we only reference widgets already packed, preventing the
        # ``isn't packed`` error reported by some users.
        packed_children = self.results_container.pack_slaves()
        if packed_children:
            frame.pack(fill="x", padx=5, pady=5, before=packed_children[0])
        else:
            frame.pack(fill="x", padx=5, pady=5)


    def show_map(self):
        if not self.findings:
            messagebox.showinfo("No Findings", "No findings to display on the map.")
            return

        map_center = [self.findings[0]["latitude"], self.findings[0]["longitude"]]
        mymap = folium.Map(location=map_center, zoom_start=15)

        for entry in self.findings:
            image_html = f'''
                <div>
                    <strong>{entry["description"]}</strong><br>
                    <img src="{entry["filename"]}" width="200"><br>
                    <small>{entry["filename"]}</small>
                </div>
            '''
            iframe = folium.IFrame(html=image_html, width=220, height=250)
            popup = folium.Popup(iframe, max_width=250)

            tooltip_html = f'<img src="{entry["filename"]}" width="150">'
            tooltip = folium.Tooltip(tooltip_html, parse_html=True)

            folium.Marker(
                location=[entry["latitude"], entry["longitude"]],
                popup=popup,
                tooltip=tooltip,
            ).add_to(mymap)

        output_map = os.path.join(OUTPUT_DIR, "findings_map.html")
        mymap.save(output_map)

        # Use an absolute ``file://`` URL so ``webbrowser`` works reliably
        # across platforms, including macOS.
        abs_map_path = os.path.abspath(output_map)
        webbrowser.open_new_tab(f"file://{abs_map_path}")

        webbrowser.open(output_map)



    def scan(self):
        mp4 = self.mp4_path.get()
        srt = self.srt_path.get()
        if not mp4 or not srt:
            messagebox.showerror("Missing Files", "Please select both MP4 and SRT files before scanning.")
            return

        if self.show_map_button:
            self.show_map_button.config(state="disabled")

        output_dir = OUTPUT_DIR
        try:
            frames_info = extract_frames_with_gps(mp4, srt, output_dir)
            for frame_path, gps in frames_info.items():
                result = analyze_frame(frame_path)
                if result:
                    self.add_finding(
                        frame_path,
                        result["report"],
                        gps.get("latitude"),
                        gps.get("longitude"),
                    )
            messagebox.showinfo("Scan Complete", f"Frames saved to '{output_dir}'")
            if self.show_map_button:
                self.show_map_button.config(state="normal")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

if __name__ == "__main__":
    app = DroneFieldGUI()
    app.mainloop()
