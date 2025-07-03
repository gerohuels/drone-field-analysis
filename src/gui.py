import tkinter as tk
from tkinter import filedialog, messagebox

from extract_frames import extract_frames_with_gps
from ai import analyze_frame

class DroneFieldGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Drone Field Analyzer")
        self.mp4_path = tk.StringVar()
        self.srt_path = tk.StringVar()
        self.findings = []
        self.results_list = None
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
        self.results_list = tk.Listbox(self, width=60, height=10)
        self.results_list.grid(row=6, column=0, columnspan=3, padx=10, pady=5)

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

    def add_finding(self, filename: str, description: str, lat, lon):
        entry = {
            "filename": filename,
            "description": description,
            "latitude": lat,
            "longitude": lon,
        }
        self.findings.append(entry)
        self.results_list.delete(0, tk.END)
        for item in reversed(self.findings):
            text = f"{item['filename']} | {item['latitude']} {item['longitude']} | {item['description']}"
            self.results_list.insert(tk.END, text)

    def scan(self):
        mp4 = self.mp4_path.get()
        srt = self.srt_path.get()
        if not mp4 or not srt:
            messagebox.showerror("Missing Files", "Please select both MP4 and SRT files before scanning.")
            return

        output_dir = "output"
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
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

if __name__ == "__main__":
    app = DroneFieldGUI()
    app.mainloop()
