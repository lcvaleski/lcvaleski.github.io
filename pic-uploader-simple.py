#!/usr/bin/env python3
import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
import subprocess
import os
import re
from pathlib import Path
from PIL import Image, ImageTk
import threading

class PicUploader:
    def __init__(self, root):
        self.root = root
        self.root.title("Pic Uploader")
        self.root.geometry("400x500")
        self.root.configure(bg='#f3f3f3')

        # Get the script directory
        self.base_dir = Path(__file__).parent
        self.pics_dir = self.base_dir / "assets" / "pics"
        self.pics_html = self.base_dir / "pages" / "pics.html"

        # Create main frame
        self.create_widgets()

    def create_widgets(self):
        # Title
        title = tk.Label(
            self.root,
            text="Pic Uploader",
            font=('Arial', 20, 'bold'),
            bg='#f3f3f3',
            fg='#333'
        )
        title.pack(pady=20)

        # Image preview frame
        self.preview_frame = tk.Frame(
            self.root,
            bg='white',
            relief=tk.RIDGE,
            bd=2,
            width=350,
            height=250
        )
        self.preview_frame.pack(pady=10, padx=25)
        self.preview_frame.pack_propagate(False)

        # Preview label
        self.preview_label = tk.Label(
            self.preview_frame,
            text="📸\nNo image selected",
            font=('Arial', 14),
            bg='white',
            fg='#999'
        )
        self.preview_label.pack(expand=True)

        # Button frame
        button_frame = tk.Frame(self.root, bg='#f3f3f3')
        button_frame.pack(pady=20)

        # Select button
        self.select_btn = tk.Button(
            button_frame,
            text="Select Image",
            font=('Arial', 12),
            bg='#2196F3',
            fg='white',
            padx=20,
            pady=10,
            command=self.select_image,
            relief=tk.FLAT,
            cursor='hand2'
        )
        self.select_btn.pack(side=tk.LEFT, padx=5)

        # Upload button (initially disabled)
        self.upload_btn = tk.Button(
            button_frame,
            text="Upload & Push",
            font=('Arial', 12),
            bg='#4CAF50',
            fg='white',
            padx=20,
            pady=10,
            command=self.upload_image,
            relief=tk.FLAT,
            state=tk.DISABLED,
            cursor='hand2'
        )
        self.upload_btn.pack(side=tk.LEFT, padx=5)

        # Status label
        self.status_label = tk.Label(
            self.root,
            text="Select an image to upload",
            font=('Arial', 11),
            bg='#f3f3f3',
            fg='#666',
            height=2
        )
        self.status_label.pack(pady=10)

        # Progress label
        self.progress_label = tk.Label(
            self.root,
            text="",
            font=('Arial', 10),
            bg='#f3f3f3',
            fg='#666',
            height=3,
            wraplength=350
        )
        self.progress_label.pack(pady=5)

        self.selected_file = None

    def select_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.gif *.webp *.svg"),
                ("All files", "*.*")
            ]
        )

        if file_path:
            self.selected_file = Path(file_path)
            self.show_preview(self.selected_file)
            self.upload_btn.config(state=tk.NORMAL)
            self.status_label.config(text=f"Selected: {self.selected_file.name}")

    def show_preview(self, image_path):
        try:
            # Load and resize image for preview
            img = Image.open(image_path)
            # Calculate aspect ratio
            img.thumbnail((320, 220), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            # Update preview
            self.preview_label.configure(image=photo, text="")
            self.preview_label.image = photo  # Keep reference
        except Exception as e:
            self.preview_label.configure(
                image='',
                text=f"📸\n{image_path.name}\n(Preview unavailable)"
            )

    def upload_image(self):
        if not self.selected_file:
            return

        # Disable buttons during upload
        self.upload_btn.config(state=tk.DISABLED)
        self.select_btn.config(state=tk.DISABLED)

        # Process in separate thread
        thread = threading.Thread(target=self.process_image)
        thread.daemon = True
        thread.start()

    def update_status(self, message, color='#666'):
        self.root.after(0, lambda: self.status_label.configure(text=message, fg=color))

    def update_progress(self, message):
        self.root.after(0, lambda: self.progress_label.configure(text=message))

    def process_image(self):
        try:
            file_path = self.selected_file

            self.update_status("📤 Processing...", '#1976d2')
            self.update_progress("Step 1/4: Copying image...")

            # Copy image to assets/pics
            filename = file_path.name
            dest_path = self.pics_dir / filename

            # Handle duplicate filenames
            if dest_path.exists():
                base = file_path.stem
                ext = file_path.suffix
                counter = 1
                while dest_path.exists():
                    filename = f"{base}_{counter}{ext}"
                    dest_path = self.pics_dir / filename
                    counter += 1

            shutil.copy2(file_path, dest_path)

            self.update_progress("Step 2/4: Updating HTML...")

            # Update pics.html
            self.update_html(filename)

            self.update_progress("Step 3/4: Committing to git...")

            # Git operations
            self.git_operations(filename)

            self.update_progress("Step 4/4: Pushing to GitHub...")

            self.update_status(f"✅ {filename} uploaded successfully!", '#4caf50')
            self.update_progress("Complete! Image is now live on GitHub Pages.")

            # Re-enable buttons
            self.root.after(0, lambda: self.upload_btn.config(state=tk.DISABLED))
            self.root.after(0, lambda: self.select_btn.config(state=tk.NORMAL))

            # Clear selection
            self.selected_file = None

            # Reset preview after 3 seconds
            self.root.after(3000, self.reset_preview)

        except Exception as e:
            self.update_status(f"❌ Error: {str(e)}", '#d32f2f')
            self.update_progress("")
            # Re-enable buttons on error
            self.root.after(0, lambda: self.upload_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.select_btn.config(state=tk.NORMAL))

    def update_html(self, filename):
        # Read the HTML file
        with open(self.pics_html, 'r', encoding='utf-8') as f:
            html = f.read()

        # Create alt text from filename
        alt_text = Path(filename).stem.replace('_', ' ').replace('-', ' ')

        # Create the new img tag
        new_img_tag = f'        <img src="../assets/pics/{filename}" alt="{alt_text}">'

        # Find the image container and add new image at the top
        pattern = r'(<div class="image-container">\s*)'
        replacement = rf'\1\n{new_img_tag}'

        html = re.sub(pattern, replacement, html)

        # Write back
        with open(self.pics_html, 'w', encoding='utf-8') as f:
            f.write(html)

    def git_operations(self, filename):
        # Change to repo directory
        os.chdir(self.base_dir)

        # Git add
        subprocess.run(['git', 'add', f'assets/pics/{filename}'], check=True)
        subprocess.run(['git', 'add', 'pages/pics.html'], check=True)

        # Git commit
        commit_message = f'Added pic: {filename}'
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)

        # Git push
        subprocess.run(['git', 'push'], check=True)

    def reset_preview(self):
        self.preview_label.configure(
            image='',
            text="📸\nNo image selected"
        )
        self.preview_label.image = None

if __name__ == "__main__":
    root = tk.Tk()
    app = PicUploader(root)
    root.mainloop()