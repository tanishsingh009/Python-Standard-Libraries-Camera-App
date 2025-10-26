import tkinter as tk
from tkinter import ttk, scrolledtext, Toplevel
import os
import datetime
import math

# --- NEW: Import the Pillow library ---
# You must install this first: pip install Pillow
try:
    from PIL import Image, ImageDraw, ImageFont, ImageTk
except ImportError:
    print("Error: The 'Pillow' library is required to run this app.")
    print("Please install it by running: pip install Pillow")
    exit()

# --- NEW: Import the OpenCV library ---
# You must install this first: pip install opencv-python
try:
    import cv2
except ImportError:
    print("Error: The 'opencv-python' library is required to run this app.")
    print("Please install it by running: pip install opencv-python")
    exit()


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulated Camera App")
        self.root.geometry("450x650") # Made window taller
        self.root.configure(bg='#2c3e50') # Dark blue-grey background

        # Store the path to the last photo taken
        self.last_image_path = None

        # --- Create a directory for photos ---
        self.photo_dir = "photos"
        if not os.path.exists(self.photo_dir):
            os.makedirs(self.photo_dir)

        # --- Main Frame ---
        main_frame = tk.Frame(root, bg='#2c3e50')
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # --- Title ---
        title_label = tk.Label(main_frame, text="Camera Settings", font=("Arial", 20, "bold"), bg='#2c3e50', fg='#ecf0f1')
        title_label.pack(pady=10)

        # --- Settings Frame for Sliders ---
        settings_frame = ttk.Frame(main_frame, style='TFrame')
        settings_frame.pack(pady=10, fill="x")

        # Style for frames and labels
        style = ttk.Style()
        style.configure('TFrame', background='#34495e')
        style.configure('TLabel', background='#34495e', foreground='#ecf0f1', font=("Arial", 12))

        # --- ISO Slider ---
        iso_frame = ttk.Frame(settings_frame, style='TFrame')
        iso_frame.pack(fill='x', padx=10, pady=5)
        iso_label = ttk.Label(iso_frame, text="ISO:", style='TLabel')
        iso_label.pack(side="left", padx=5)
        self.iso_slider = ttk.Scale(iso_frame, from_=100, to=3200, orient="horizontal", length=300)
        self.iso_slider.set(800)
        self.iso_slider.pack(side="right", padx=10, fill='x', expand=True)

        # --- Aperture Slider ---
        ap_frame = ttk.Frame(settings_frame, style='TFrame')
        ap_frame.pack(fill='x', padx=10, pady=5)
        ap_label = ttk.Label(ap_frame, text="Aperture (f/):", style='TLabel')
        ap_label.pack(side="left", padx=5)
        self.aperture_slider = ttk.Scale(ap_frame, from_=1.8, to=16.0, orient="horizontal", length=300)
        self.aperture_slider.set(5.6)
        self.aperture_slider.pack(side="right", padx=10, fill='x', expand=True)

        # --- Shutter Speed Slider ---
        sh_frame = ttk.Frame(settings_frame, style='TFrame')
        sh_frame.pack(fill='x', padx=10, pady=5)
        sh_label = ttk.Label(sh_frame, text="Shutter (1/s):", style='TLabel')
        sh_label.pack(side="left", padx=5)
        self.shutter_slider = ttk.Scale(sh_frame, from_=60, to=1000, orient="horizontal", length=300)
        self.shutter_slider.set(250)
        self.shutter_slider.pack(side="right", padx=10, fill='x', expand=True)

        # --- Button Frame ---
        button_frame = tk.Frame(main_frame, bg='#2c3e50')
        button_frame.pack(pady=10, fill='x')

        # --- Capture Button ---
        self.capture_button = tk.Button(button_frame, text="📸 Capture Photo",
                                        font=("Arial", 14, "bold"),
                                        bg='#3498db', fg='#ffffff',
                                        activebackground='#2980b9', activeforeground='#ffffff',
                                        relief='flat', borderwidth=0,
                                        command=self.take_picture)
        self.capture_button.pack(side="left", fill='x', expand=True, padx=5)

        # --- NEW: Gallery Button ---
        self.gallery_button = tk.Button(button_frame, text="🖼️ Show Last Photo",
                                        font=("Arial", 14, "bold"),
                                        bg='#2ecc71', fg='#ffffff',
                                        activebackground='#27ae60', activeforeground='#ffffff',
                                        relief='flat', borderwidth=0,
                                        command=self.show_last_photo)
        self.gallery_button.pack(side="right", fill='x', expand=True, padx=5)

        # --- Log Display ---
        self.log_area = scrolledtext.ScrolledText(main_frame, height=10, width=50,
                                                  bg='#1c1c1c', fg='#ecf0f1',
                                                  font=("Courier New", 10),
                                                  relief='flat', borderwidth=0)
        self.log_area.pack(pady=10, fill="both", expand=True)
        self.log_message("App started. 'photos' directory is ready.")

    def log_message(self, message):
        self.log_area.insert(tk.END, f"{message}\n")
        self.log_area.see(tk.END) # Auto-scroll

    def take_picture(self):
        try:
            # --- 1. Get current time from 'datetime' ---
            now = datetime.datetime.now()
            timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
            pretty_timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
            
            # --- 2. Get values from 'tkinter' sliders ---
            iso = int(self.iso_slider.get())
            aperture = round(self.aperture_slider.get(), 1)
            shutter_speed_inv = int(self.shutter_slider.get())
            
            # --- 3. Use 'math' to calculate exposure ---
            shutter_speed = 1 / shutter_speed_inv
            # Use max(aperture, 0.1) to avoid log(0) if aperture is 0
            exposure_value = math.log2((max(aperture, 0.1)**2) / shutter_speed)

            # --- 4. Prepare the metadata content ---
            file_content = f"""--- Simulated Photo Metadata ---
Timestamp: {pretty_timestamp}
Filename: IMG_{timestamp}.jpg

--- Camera Settings ---
ISO: {iso}
Aperture: f/{aperture}
Shutter Speed: 1/{shutter_speed_inv}s
Exposure Value (EV): {exposure_value:.2f}
"""
            # --- 5. Save the .txt file ---
            filename_txt = f"IMG_{timestamp}_METADATA.txt"
            file_path_txt = os.path.join(self.photo_dir, filename_txt)
            with open(file_path_txt, "w") as f:
                f.write(file_content)
            
            self.log_message(f"Saved metadata: {filename_txt}")

            # --- 6. NEW: Capture a REAL photo from the webcam ---
            filename_jpg = f"IMG_{timestamp}.jpg"
            file_path_jpg = os.path.join(self.photo_dir, filename_jpg)
            
            # Connect to the default webcam (usually 0)
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                self.log_message("Error: Could not open webcam.")
                return

            # Read one frame from the webcam
            ret, frame = cap.read()
            
            # Release the webcam immediately
            cap.release() 
            
            if not ret:
                self.log_message("Error: Could not read frame from webcam.")
                return

            # --- 7. NEW: Convert webcam frame to Pillow Image ---
            # OpenCV uses BGR color, Pillow uses RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Create a Pillow image from the webcam frame
            img = Image.fromarray(frame_rgb)
            
            # Resize the image to our 800x600 standard size
            # This ensures the text fits, regardless of your webcam's resolution
            img = img.resize((800, 600), Image.Resampling.LANCZOS)

            # --- 8. Draw metadata text on the REAL photo ---
            draw = ImageDraw.Draw(img)

            # Try to load a nice font, fall back to default
            try:
                # You might need to change "Arial.ttf" to a font on your system
                # e.g., "Verdana.ttf" on Windows, or "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" on Linux
                font_large = ImageFont.truetype("Arial.ttf", 40)
                font_medium = ImageFont.truetype("Arial.ttf", 24)
                font_small = ImageFont.truetype("Arial.ttf", 18)
            except IOError:
                self.log_message("Arial.ttf not found. Using default font.")
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()

            # Draw text on the image
            draw.text((400, 280), "SIMULATED PHOTO", fill='#ecf0f1', font=font_large, anchor="mm")
            
            draw.text((20, 20), f"IMG_{timestamp}.jpg", fill='#3498db', font=font_medium)
            draw.text((20, 70), f"ISO: {iso}", fill='#ecf0f1', font=font_small)
            draw.text((20, 95), f"Aperture: f/{aperture}", fill='#ecf0f1', font=font_small)
            draw.text((20, 120), f"Shutter: 1/{shutter_speed_inv}s", fill='#ecf0f1', font=font_small)
            draw.text((20, 145), f"EV: {exposure_value:.2f}", fill='#ecf0f1', font=font_small)
            
            # --- THIS LINE IS NOW FIXED ---
            draw.text((780, 580), "Tanish's Camera App", fill='#7f8c8d', font=font_small, anchor="rs")

            # Save the image
            img.save(file_path_jpg)
            self.log_message(f"Saved image: {filename_jpg}")
            
            # Store this as the last image
            self.last_image_path = file_path_jpg


        except Exception as e:
            self.log_message(f"Error: {e}")
            print(f"Error details: {e}")

    def show_last_photo(self):
        # --- NEW: Function to show the last photo in a new window ---
        
        if not self.last_image_path:
            self.log_message("No photo taken yet. Click 'Capture' first.")
            return

        try:
            # Create a new Toplevel window
            gallery_window = Toplevel(self.root)
            gallery_window.title(os.path.basename(self.last_image_path))
            gallery_window.configure(bg='#1c1c1c')

            # Load the image using Pillow
            img = Image.open(self.last_image_path)
            
            # Resize image to a thumbnail for display
            img.thumbnail((800, 600)) # Maintain aspect ratio

            # Convert the Pillow image to a Tkinter image
            img_tk = ImageTk.PhotoImage(img)

            # Display the image in a label
            img_label = tk.Label(gallery_window, image=img_tk, bg='#1c1c1c')
            
            # VERY IMPORTANT: Keep a reference to the image
            # or it will be garbage-collected and won't appear!
            img_label.image = img_tk 
            img_label.pack(padx=10, pady=10)

        except Exception as e:
            self.log_message(f"Error opening gallery: {e}")
            print(f"Error details: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()

