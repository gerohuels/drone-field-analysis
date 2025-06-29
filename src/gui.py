import tkinter as tk
from tkinter import messagebox

class DroneFieldGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Drone Field Analyzer")
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Drone Field Analyzer", font=("Helvetica", 16, "bold")).grid(row=0, column=0, columnspan=3, pady=10)

        tk.Label(self, text="MP4 File:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(self, width=40).grid(row=1, column=1, padx=5, pady=5, columnspan=2)

        tk.Label(self, text="SRT File:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(self, width=40).grid(row=2, column=1, padx=5, pady=5, columnspan=2)

        tk.Button(self, text="Add Files", command=self.show_not_implemented).grid(row=3, column=0, columnspan=3, pady=10)
        tk.Button(self, text="Scan", command=self.show_not_implemented).grid(row=4, column=0, columnspan=3, pady=10)

        tk.Label(self, text="Found Elements").grid(row=5, column=0, columnspan=3)
        tk.Listbox(self, width=60, height=10).grid(row=6, column=0, columnspan=3, padx=10, pady=5)

    def show_not_implemented(self):
        tk.messagebox.showinfo("Not Implemented", "This functionality is not implemented yet.")

if __name__ == "__main__":
    app = DroneFieldGUI()
    app.mainloop()