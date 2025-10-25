import tkinter as tk
from tkinter import scrolledtext, ttk
import os
import datetime
import math

class CameraApp:
    """
    A simple simulated camera application using Python's standard libraries.
    This version uses sliders for dynamic user input.
    """
    def __init__(self, root):
        """
        Initializes the camera application UI and sets up the photo directory.
        """
        self.root = root
        self.root.title("Dynamic Camera App")
        self.root.geometry("500x550") # Increased height for sliders
        self.root.configure(bg="#2c3e50")

        # --- Style Configuration for new widgets ---
        style = ttk.Style()
        style.configure("TFrame", background="#2c3e50")
        style.configure(
            "TLabel",
            background="#2c3e50",
            foreground="#ecf0f1",
            font=("Helvetica", 10)
        )
        style.configure(
            "Horizontal.TScale",
            background="#2c3e50",
            troughcolor="#34495e",
            sliderrelief="flat"
        )

        # --- Create a directory for photos if it doesn't exist ---
        # ... (os module part is unchanged)
        self.photo_dir = "photos"
        if not os.path.exists(self.photo_dir):
            os.makedirs(self.photo_dir)
            print(f"Created directory: {self.photo_dir}")

        # --- UI Elements ---
        # Main frame
        main_frame = ttk.Frame(root, padding="20 20 20 20")
        main_frame.pack(expand=True, fill=tk.BOTH)

        # --- Settings Frame for Sliders ---
        settings_frame = ttk.Frame(main_frame, padding="10 10 10 0")
        settings_frame.pack(fill=tk.X, pady=10)
        settings_frame.columnconfigure(1, weight=1)

        # ISO Slider
        iso_label = ttk.Label(settings_frame, text="ISO:")
        iso_label.grid(row=0, column=0, padx=(0, 10), sticky="w")
        self.iso_slider = ttk.Scale(
            settings_frame,
            from_=100,
            to=3200,
            orient=tk.HORIZONTAL,
            style="Horizontal.TScale"
        )
        self.iso_slider.set(800) # Set a default value
        self.iso_slider.grid(row=0, column=1, sticky="ew")

        # Aperture Slider
        aperture_label = ttk.Label(settings_frame, text="Aperture (f/):")
        aperture_label.grid(row=1, column=0, padx=(0, 10), sticky="w")
        self.aperture_slider = ttk.Scale(
            settings_frame,
            from_=1.8,
            to=16.0,
            orient=tk.HORIZONTAL,
            style="Horizontal.TScale"
        )
        self.aperture_slider.set(5.6) # Set a default value
        self.aperture_slider.grid(row=1, column=1, sticky="ew")

        # Shutter Speed Slider (representing the denominator)
        shutter_label = ttk.Label(settings_frame, text="Shutter (1/s):")
        shutter_label.grid(row=2, column=0, padx=(0, 10), sticky="w")
        self.shutter_slider = ttk.Scale(
            settings_frame,
            from_=60,
            to=1000,
            orient=tk.HORIZONTAL,
            style="Horizontal.TScale"
        )
        self.shutter_slider.set(250) # Set a default value
        self.shutter_slider.grid(row=2, column=1, sticky="ew")


        # Capture Button
        self.capture_button = tk.Button(
            main_frame,
            text="📸 Capture Photo",
            font=("Helvetica", 16, "bold"),
            command=self.take_picture,
            bg="#3498db",
            fg="white",
            activebackground="#2980b9",
            activeforeground="white",
            relief="flat",
            borderwidth=0,
            padx=20,
            pady=10,
            cursor="hand2"
        )
        self.capture_button.pack(pady=20)

        # Log display area
        self.log_area = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            font=("Courier New", 10),
            bg="#34495e",
            fg="#ecf0f1",
            borderwidth=0,
            highlightthickness=0
        )
        self.log_area.pack(expand=True, fill=tk.BOTH)
        self.log_message("App started. Adjust settings and click 'Capture'.")

    def take_picture(self):
        """
        Simulates taking a picture using values from the UI sliders.
        """
        try:
            # --- Use 'datetime' to create a unique timestamp ---
            now = datetime.datetime.now()
            timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"IMG_{timestamp}.txt"

            # --- Get metadata from sliders instead of 'random' ---
            iso = int(self.iso_slider.get())
            aperture = round(self.aperture_slider.get(), 1)
            shutter_speed_inv = int(self.shutter_slider.get())
            shutter_speed = 1 / shutter_speed_inv

            # --- Use 'math' for calculations (unchanged) ---
            exposure_value = math.log2((aperture**2) / shutter_speed)


            # --- Prepare the content for the file ---
            file_content = (
                f"--- Simulated Photo --- \n"
                f"Timestamp: {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Location: (Simulated GPS Coords)\n"
                f"\n"
                f"--- Camera Settings ---\n"
                f"ISO: {iso}\n"
                f"Aperture: f/{aperture}\n"
                f"Shutter Speed: 1/{shutter_speed_inv}s\n"
                f"Exposure Value (EV): {round(exposure_value, 2)}\n"
            )

            # --- Use 'os' to create the file path and save the file ---
            file_path = os.path.join(self.photo_dir, filename)

            with open(file_path, "w") as f:
                f.write(file_content)

            self.log_message(f"Success! Photo saved as '{file_path}'")
            self.log_message(f"  - ISO: {iso}, Aperture: f/{aperture}, Shutter: 1/{shutter_speed_inv}s")

        except Exception as e:
            self.log_message(f"Error: Could not save photo. {e}")

    def log_message(self, message):
        """
        Adds a message to the log area in the UI.
        """
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END) # Auto-scroll to the bottom


if __name__ == "__main__":
    # --- Main entry point to start the application ---
    root = tk.Tk()
    app = CameraApp(root)
    root.mainloop()

