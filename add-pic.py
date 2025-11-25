#!/usr/bin/env python3
import sys
import shutil
import subprocess
import re
from pathlib import Path

def add_pic(file_path, caption=None, tags=None):
    # Setup paths
    base_dir = Path(__file__).parent
    pics_dir = base_dir / "assets" / "pics"
    pics_html = base_dir / "pages" / "pics.html"

    # Validate input
    source = Path(file_path.strip())
    if not source.exists():
        print(f"❌ File not found: {source}")
        return 1

    # Check if it's an image
    valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'}
    if source.suffix.lower() not in valid_extensions:
        print(f"❌ Not an image file: {source.suffix}")
        return 1

    # Copy to assets/pics
    filename = source.name
    dest = pics_dir / filename

    # Handle duplicates
    if dest.exists():
        base = source.stem
        ext = source.suffix
        counter = 1
        while dest.exists():
            filename = f"{base}_{counter}{ext}"
            dest = pics_dir / filename
            counter += 1
        print(f"📝 Renamed to avoid conflict: {filename}")

    print(f"📸 Copying {filename}...")
    shutil.copy2(source, dest)

    # Update HTML
    print("📝 Updating pics.html...")
    with open(pics_html, 'r') as f:
        html = f.read()

    # Create alt text
    alt_text = Path(filename).stem.replace('_', ' ').replace('-', ' ')

    # Add new image with optional caption and tags
    tags_attr = f' data-tags="{tags}"' if tags else ''

    if caption:
        new_content = f'''        <div class="pic-item"{tags_attr}>
            <img src="../assets/pics/{filename}" alt="{alt_text}">
            <p class="caption">{caption}</p>
        </div>'''
    else:
        if tags:
            new_content = f'''        <div class="pic-item"{tags_attr}>
            <img src="../assets/pics/{filename}" alt="{alt_text}">
        </div>'''
        else:
            new_content = f'        <img src="../assets/pics/{filename}" alt="{alt_text}">'

    pattern = r'(<div class="image-container">\s*)'
    html = re.sub(pattern, rf'\1\n{new_content}', html)

    with open(pics_html, 'w') as f:
        f.write(html)

    # Git operations
    print("🔧 Committing...")
    subprocess.run(['git', 'add', f'assets/pics/{filename}'], cwd=base_dir, check=True)
    subprocess.run(['git', 'add', 'pages/pics.html'], cwd=base_dir, check=True)
    subprocess.run(['git', 'commit', '-m', f'Added pic: {filename}'], cwd=base_dir, check=True)

    print("🚀 Pushing...")
    subprocess.run(['git', 'push'], cwd=base_dir, check=True)

    print(f"✅ Done! {filename} is live")
    return 0

if __name__ == "__main__":
    # Prompt for image path
    print("📸 Add a picture to your site")
    print("Drag an image file here and press Enter (or type the path):")
    image_path = input("> ").strip()

    if not image_path:
        print("❌ No file provided")
        sys.exit(1)

    # Remove quotes if present (from dragging files)
    if image_path.startswith('"') and image_path.endswith('"'):
        image_path = image_path[1:-1]
    elif image_path.startswith("'") and image_path.endswith("'"):
        image_path = image_path[1:-1]

    # Handle escaped spaces (replace '\ ' with ' ')
    image_path = image_path.replace('\\ ', ' ')

    # Ask for optional caption
    print("\n💬 Caption (optional, press Enter to skip):")
    caption = input("> ").strip()

    if not caption:
        caption = None

    # Ask for optional tags
    print("\n🏷️  Tags (optional, comma-separated, press Enter to skip):")
    print("   Examples: travel, food, family, nature, nyc, boulder")
    tags_input = input("> ").strip()

    tags = None
    if tags_input:
        # Clean up tags - remove extra spaces and make lowercase
        tags = ','.join([tag.strip().lower() for tag in tags_input.split(',')])

    sys.exit(add_pic(image_path, caption, tags))