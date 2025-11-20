#!/usr/bin/env python3
import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
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
            text="Drop Image Here",
            font=('Arial', 20, 'bold'),
            bg='#f3f3f3',
            fg='#333'
        )
        title.pack(pady=20)

        # Drop zone
        self.drop_frame = tk.Frame(
            self.root,
            bg='white',
            relief=tk.RIDGE,
            bd=2,
            width=350,
            height=300
        )
        self.drop_frame.pack(pady=10, padx=25, fill=tk.BOTH, expand=True)
        self.drop_frame.pack_propagate(False)

        # Drop zone label
        self.drop_label = tk.Label(
            self.drop_frame,
            text="📸\nDrag & Drop\nImage Here",
            font=('Arial', 16),
            bg='white',
            fg='#999'
        )
        self.drop_label.pack(expand=True)

        # Status label
        self.status_label = tk.Label(
            self.root,
            text="Ready to upload",
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

        # Enable drag and drop
        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind('<<Drop>>', self.handle_drop)
        self.drop_frame.dnd_bind('<<DragEnter>>', self.on_drag_enter)
        self.drop_frame.dnd_bind('<<DragLeave>>', self.on_drag_leave)

    def on_drag_enter(self, event):
        self.drop_frame.configure(bg='#e8f4f8')
        self.drop_label.configure(bg='#e8f4f8')

    def on_drag_leave(self, event):
        self.drop_frame.configure(bg='white')
        self.drop_label.configure(bg='white')

    def handle_drop(self, event):
        self.drop_frame.configure(bg='white')
        self.drop_label.configure(bg='white')

        # Get the file path
        file_path = event.data.strip()
        # Handle paths with spaces (they come wrapped in {})
        if file_path.startswith('{') and file_path.endswith('}'):
            file_path = file_path[1:-1]

        # Process in separate thread to avoid blocking UI
        thread = threading.Thread(target=self.process_image, args=(file_path,))
        thread.daemon = True
        thread.start()

    def update_status(self, message, color='#666'):
        self.root.after(0, lambda: self.status_label.configure(text=message, fg=color))

    def update_progress(self, message):
        self.root.after(0, lambda: self.progress_label.configure(text=message))

    def process_image(self, file_path):
        try:
            # Validate file
            file_path = Path(file_path)
            if not file_path.exists():
                self.update_status("❌ File not found", '#d32f2f')
                return

            # Check if it's an image
            valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'}
            if file_path.suffix.lower() not in valid_extensions:
                self.update_status("❌ Not a valid image file", '#d32f2f')
                return

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

            # Show preview of uploaded image
            self.show_preview(dest_path)

            self.update_status(f"✅ {filename} uploaded successfully!", '#4caf50')
            self.update_progress("Complete! Image is now live on GitHub Pages.")

        except Exception as e:
            self.update_status(f"❌ Error: {str(e)}", '#d32f2f')
            self.update_progress("")

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

    def show_preview(self, image_path):
        try:
            # Load and resize image for preview
            img = Image.open(image_path)
            img.thumbnail((200, 150), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            # Update drop label to show preview
            self.root.after(0, lambda: self.drop_label.configure(
                image=photo,
                text=""
            ))
            self.drop_label.image = photo  # Keep reference

            # Reset after 3 seconds
            self.root.after(3000, self.reset_drop_zone)
        except:
            pass  # Fail silently if preview doesn't work

    def reset_drop_zone(self):
        self.drop_label.configure(
            image='',
            text="📸\nDrag & Drop\nImage Here"
        )
        self.drop_label.image = None

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = PicUploader(root)
    root.mainloop()