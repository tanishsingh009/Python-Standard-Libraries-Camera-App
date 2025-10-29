import tkinter as tk
from tkinter import ttk, scrolledtext, Toplevel
import os
import datetime
import math
import shutil  # --- NEW: Import shutil for moving files ---

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
        self.root.title("Tanish's Camera App")
        self.root.geometry("450x700")
        self.root.configure(bg='#2c3e50')

        # --- Style ---
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#2c3e50')
        style.configure('TButton', background='#3498db', foreground='white', font=('Arial', 10, 'bold'))
        style.map('TButton', background=[('active', '#2980b9')])
        style.configure('TLabel', background='#2c3e50', foreground='#ecf0f1', font=('Arial', 10))
        style.configure('Horizontal.TScale', background='#2c3e50')
        
        # --- Photo Directories ---
        self.photo_dir = "photos"
        self.recycle_bin_dir = "recycle_bin" # --- NEW: Recycle Bin Path ---
        
        if not os.path.exists(self.photo_dir):
            os.makedirs(self.photo_dir)
        if not os.path.exists(self.recycle_bin_dir): # --- NEW: Create Recycle Bin ---
            os.makedirs(self.recycle_bin_dir)
            
        self.last_image_path = None # To store the path of the most recent photo
        
        # --- Main Frame ---
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill="both", expand=True)

        # --- Title ---
        title_label = ttk.Label(main_frame, text="Camera Settings", font=("Arial", 16, 'bold'), foreground='#3498db')
        title_label.pack(pady=10)

        # --- Settings Frame ---
        settings_frame = ttk.Frame(main_frame)
        settings_frame.pack(pady=10, fill="x")

        # --- Sliders ---
        self.iso_slider = self.create_slider(settings_frame, "ISO", 100, 3200, 0)
        self.aperture_slider = self.create_slider(settings_frame, "Aperture (f/)", 1.8, 22.0, 1, is_float=True)
        self.shutter_slider = self.create_slider(settings_frame, "Shutter (1/s)", 1, 4000, 2)
        
        # --- Buttons Frame ---
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20, fill='x', side='bottom')

        # --- Capture Button ---
        self.capture_button = ttk.Button(
            button_frame, 
            text="📸 Capture Photo", 
            command=self.take_picture,
            style='TButton'
        )
        self.capture_button.pack(side='left', fill='x', expand=True, padx=5)

        # --- NEW: Gallery Button (replaces Show Last Photo) ---
        self.gallery_button = ttk.Button(
            button_frame,
            text="🖼️ Open Gallery",
            command=self.open_gallery, # Connects to the new gallery function
            style='TButton'
        )
        self.gallery_button.pack(side='left', fill='x', expand=True, padx=5) # Changed to 'left'

        # --- NEW: Recycle Bin Button ---
        self.recycle_bin_button = ttk.Button(
            button_frame,
            text="♻️ Recycle Bin",
            command=self.open_recycle_bin,
            style='TButton'
        )
        self.recycle_bin_button.pack(side='left', fill='x', expand=True, padx=5) # Changed to 'left'

        # --- Log Area ---
        log_label = ttk.Label(main_frame, text="Log:", font=("Arial", 12, 'bold'))
        log_label.pack(pady=(10,0), anchor='w')
        
        self.log_area = scrolledtext.ScrolledText(
            main_frame, 
            wrap=tk.WORD, 
            height=10, 
            bg='#1c1c1c', 
            fg='#ecf0f1',
            font=("Consolas", 9)
        )
        self.log_area.pack(pady=10, fill="both", expand=True)
        self.log_message("App started. 'photos' directory is ready.")

    def create_slider(self, parent, text, from_, to, row, is_float=False):
        ttk.Label(parent, text=f"{text}:").grid(row=row, column=0, sticky='w', padx=10, pady=5)
        
        var = tk.DoubleVar() if is_float else tk.IntVar()
        var.set(from_)
        
        label = ttk.Label(parent, text=f"{from_:.1f}" if is_float else f"{from_}", width=6)
        label.grid(row=row, column=2, sticky='e', padx=10)

        def update_label(val):
            if is_float:
                label.config(text=f"{float(val):.1f}")
            else:
                label.config(text=f"{int(float(val))}")

        slider = ttk.Scale(
            parent,
            from_=from_,
            to=to,
            orient="horizontal",
            variable=var,
            command=update_label
        )
        slider.grid(row=row, column=1, sticky='we', padx=10)
        parent.grid_columnconfigure(1, weight=1) # Make slider fill space
        return var

    def log_message(self, message):
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, f"{datetime.datetime.now().strftime('%H:%M:%S')}: {message}\n")
        self.log_area.config(state=tk.DISABLED)
        self.log_area.see(tk.END) # Auto-scroll

    def take_picture(self):
        try:
            # --- 1. Get current time from 'datetime' ---
            now = datetime.datetime.now()
            timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
            
            # --- 2. Get values from 'tkinter' sliders ---
            iso = self.iso_slider.get()
            aperture = round(self.aperture_slider.get(), 1)
            shutter_speed_inv = self.shutter_slider.get()
            
            # --- 3. Use 'math' to calculate exposure ---
            shutter_speed = 1 / shutter_speed_inv
            # Use max(aperture, 0.1) to avoid log(0) if aperture is 0
            exposure_value = math.log2((max(aperture, 0.1)**2) / shutter_speed)

            # --- 4. Prepare the metadata content ---
            file_content = f"""
            Photo Metadata
            --------------------
            Timestamp: {now.strftime("%Y-%m-%d %H:%M:%S")}
            ISO: {iso}
            Aperture: f/{aperture}
            Shutter Speed: 1/{shutter_speed_inv} s
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
                # You might need to change this path to a font on your system
                font_path = "arial.ttf"
                font_large = ImageFont.truetype(font_path, 40)
                font_medium = ImageFont.truetype(font_path, 24)
                font_small = ImageFont.truetype(font_path, 18)
            except IOError:
                self.log_message("Arial font not found. Using default font.")
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
            
            # --- 9. Store this as the last image path ---
            self.last_image_path = file_path_jpg

        except Exception as e:
            self.log_message(f"Error: {e}")

    # --- NEW: Function to open the full gallery ---
    def open_gallery(self):
        gallery_window = Toplevel(self.root)
        gallery_window.title("Photo Gallery")
        gallery_window.geometry("800x600")
        gallery_window.configure(bg="#1c1c1c")

        # --- Create a scrollable area ---
        main_frame = tk.Frame(gallery_window, bg="#1c1c1c")
        main_frame.pack(fill="both", expand=1)

        canvas = tk.Canvas(main_frame, bg="#1c1c1c")
        canvas.pack(side="left", fill="both", expand=1)

        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)
        
        # This frame will contain all the thumbnails
        scrollable_frame = tk.Frame(canvas, bg="#1c1c1c")

        # Add the scrollable frame to the canvas
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # Update the scrollregion when the frame's size changes
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # --- Load photos ---
        try:
            # Get all .jpg files, sort by most recent first
            photo_files = [f for f in os.listdir(self.photo_dir) if f.endswith('.jpg')]
            photo_files.sort(key=lambda x: os.path.getmtime(os.path.join(self.photo_dir, x)), reverse=True)

            if not photo_files:
                tk.Label(scrollable_frame, text="No photos yet. Click 'Capture' first.", 
                         bg='#1c1c1c', fg='white', font=('Arial', 14)).pack(pady=20, padx=20)
                return

            # Keep a list of image references to prevent garbage collection
            self.thumbnail_refs = [] 

            for filename in photo_files:
                file_path = os.path.join(self.photo_dir, filename)
                
                # --- Create Thumbnail ---
                img = Image.open(file_path)
                img.thumbnail((200, 200)) # Resize to max 200x200
                img_tk = ImageTk.PhotoImage(img)
                
                # Store reference
                self.thumbnail_refs.append(img_tk)

                # --- Create a frame for each photo ---
                thumb_frame = tk.Frame(scrollable_frame, bg="#2c3e50", bd=2, relief="groove")
                thumb_frame.pack(pady=10, padx=10, fill="x")

                # Create a clickable label
                # Use lambda to pass the specific file_path to the command
                img_label = tk.Label(
                    thumb_frame, 
                    image=img_tk, 
                    bg='#2c3e50',
                    cursor="hand2"
                )
                img_label.pack(pady=5)
                img_label.bind("<Button-1>", lambda e, p=file_path: self.show_full_image(p))

                # Add filename label
                name_label = tk.Label(
                    thumb_frame, 
                    text=filename, 
                    bg='#2c3e50', 
                    fg='white', 
                    font=('Arial', 9)
                )
                name_label.pack(pady=(0, 5))

                # --- NEW: Delete Button ---
                delete_button = ttk.Button(
                    thumb_frame,
                    text="Delete",
                    command=lambda p=file_path, f=thumb_frame: self.delete_photo(p, f)
                )
                delete_button.pack(pady=5)

        except Exception as e:
            tk.Label(scrollable_frame, text=f"Error loading gallery: {e}", 
                     bg='#1c1c1c', fg='red').pack(pady=20, padx=20)

    # --- NEW: Function to show a single full-size image ---
    def show_full_image(self, file_path):
        image_window = Toplevel(self.root)
        image_window.title(os.path.basename(file_path))
        image_window.configure(bg="#1c1c1c")

        try:
            img = Image.open(file_path)
            
            # Optional: Resize if too large for screen, maintaining aspect ratio
            max_size = (900, 700)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            img_tk = ImageTk.PhotoImage(img)
            
            img_label = tk.Label(image_window, image=img_tk, bg='#1c1c1c')
            
            # Keep a reference!
            img_label.image = img_tk 
            
            img_label.pack(padx=10, pady=10)
        
        except Exception as e:
            tk.Label(image_window, text=f"Error opening image: {e}", 
                     bg='#1c1c1c', fg='red').pack(pady=20, padx=20)

    # --- NEW: Function to delete a photo (move to recycle bin) ---
    def delete_photo(self, file_path, thumb_frame):
        try:
            base_name = os.path.basename(file_path)
            txt_name = base_name.replace('.jpg', '_METADATA.txt')
            txt_path = os.path.join(self.photo_dir, txt_name)

            # Move .jpg to recycle bin
            shutil.move(file_path, os.path.join(self.recycle_bin_dir, base_name))
            
            # Move .txt to recycle bin (if it exists)
            if os.path.exists(txt_path):
                shutil.move(txt_path, os.path.join(self.recycle_bin_dir, txt_name))
            
            self.log_message(f"Moved to recycle bin: {base_name}")
            
            # Remove the thumbnail from the gallery window
            thumb_frame.destroy()
            
        except Exception as e:
            self.log_message(f"Error deleting {file_path}: {e}")

    # --- NEW: Function to open the recycle bin ---
    def open_recycle_bin(self):
        recycle_window = Toplevel(self.root)
        recycle_window.title("Recycle Bin")
        recycle_window.geometry("800x600")
        recycle_window.configure(bg="#1c1c1c")

        # --- Create a scrollable area (same as gallery) ---
        main_frame = tk.Frame(recycle_window, bg="#1c1c1c")
        main_frame.pack(fill="both", expand=1)
        canvas = tk.Canvas(main_frame, bg="#1c1c1c")
        canvas.pack(side="left", fill="both", expand=1)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollable_frame = tk.Frame(canvas, bg="#1c1c1c")
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # --- Load photos from recycle bin ---
        try:
            photo_files = [f for f in os.listdir(self.recycle_bin_dir) if f.endswith('.jpg')]
            photo_files.sort(key=lambda x: os.path.getmtime(os.path.join(self.recycle_bin_dir, x)), reverse=True)

            if not photo_files:
                tk.Label(scrollable_frame, text="Recycle Bin is empty.", 
                         bg='#1c1c1c', fg='white', font=('Arial', 14)).pack(pady=20, padx=20)
                return

            self.recycle_thumbnail_refs = [] # Separate list for recycle bin

            for filename in photo_files:
                file_path = os.path.join(self.recycle_bin_dir, filename)
                
                img = Image.open(file_path)
                img.thumbnail((200, 200))
                img_tk = ImageTk.PhotoImage(img)
                self.recycle_thumbnail_refs.append(img_tk)

                thumb_frame = tk.Frame(scrollable_frame, bg="#2c3e50", bd=2, relief="groove")
                thumb_frame.pack(pady=10, padx=10, fill="x")

                img_label = tk.Label(thumb_frame, image=img_tk, bg='#2c3e50')
                img_label.pack(pady=5)

                name_label = tk.Label(thumb_frame, text=filename, bg='#2c3e50', fg='white', font=('Arial', 9))
                name_label.pack(pady=(0, 5))

                # --- Button Frame for Restore/Delete ---
                btn_frame = tk.Frame(thumb_frame, bg="#2c3e50")
                btn_frame.pack(pady=5)

                # --- Restore Button ---
                restore_button = ttk.Button(
                    btn_frame,
                    text="Restore",
                    command=lambda p=file_path, f=thumb_frame: self.restore_photo(p, f)
                )
                restore_button.pack(side="left", padx=5)
                
                # --- Delete Permanently Button ---
                delete_perm_button = ttk.Button(
                    btn_frame,
                    text="Delete Permanently",
                    command=lambda p=file_path, f=thumb_frame: self.delete_permanently(p, f)
                )
                delete_perm_button.pack(side="left", padx=5)

        except Exception as e:
            tk.Label(scrollable_frame, text=f"Error loading recycle bin: {e}", 
                     bg='#1c1c1c', fg='red').pack(pady=20, padx=20)

    # --- NEW: Function to restore a photo ---
    def restore_photo(self, file_path, thumb_frame):
        try:
            base_name = os.path.basename(file_path)
            txt_name = base_name.replace('.jpg', '_METADATA.txt')
            txt_path = os.path.join(self.recycle_bin_dir, txt_name)

            # Move .jpg back to photos
            shutil.move(file_path, os.path.join(self.photo_dir, base_name))
            
            # Move .txt back to photos (if it exists)
            if os.path.exists(txt_path):
                shutil.move(txt_path, os.path.join(self.photo_dir, txt_name))
            
            self.log_message(f"Restored: {base_name}")
            thumb_frame.destroy()
            
        except Exception as e:
            self.log_message(f"Error restoring {file_path}: {e}")

    # --- NEW: Function to delete permanently ---
    def delete_permanently(self, file_path, thumb_frame):
        try:
            base_name = os.path.basename(file_path)
            txt_name = base_name.replace('.jpg', '_METADATA.txt')
            txt_path = os.path.join(self.recycle_bin_dir, txt_name)

            # Delete .jpg
            os.remove(file_path)
            
            # Delete .txt (if it exists)
            if os.path.exists(txt_path):
                os.remove(txt_path)
            
            self.log_message(f"Permanently deleted: {base_name}")
            thumb_frame.destroy()
            
        except Exception as e:
            self.log_message(f"Error permanently deleting {file_path}: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
