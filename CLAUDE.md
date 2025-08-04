# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a personal portfolio website hosted on GitHub Pages at `logan.valeski.org`. It's a static HTML/CSS site with minimal JavaScript, featuring a clean design with projects, blog posts, resume, and hidden navigation elements.

## Development Commands

Since this is a static site with no build process:
- **Run locally**: Open `index.html` in a browser or use a simple HTTP server like `python -m http.server 8000`
- **Deploy**: Push to the `main` branch - GitHub Pages handles deployment automatically
- **No build, test, or lint commands** - edit HTML/CSS files directly

## Architecture and Structure

### Page Organization
- **index.html**: Main landing page with project cards and hidden corner navigation
- **pages/**: All subpages organized by type
  - Blog posts are in subdirectories (e.g., `bike_post/`, `boulder_post/`, `ellie_post/`)
  - Standalone pages are HTML files (e.g., `music.html`, `pics.html`)
  - **archived/**: Contains removed pages that are no longer linked
- **assets/**: Images and icons, with `pics/` subdirectory for photo gallery
- **styles/**: Global CSS (`globals.css`) and page-specific styles (e.g., `syllabus.css`)

### Key Implementation Details

1. **Hidden Navigation**: The homepage has clickable areas in the corners that link to hidden pages:
   - Top-right: Photo gallery
   - Bottom-right: Music player
   - Note: Chess, Syllabus, and Scratchpad pages have been archived and are no longer linked

2. **Consistent Page Structure**: Most pages follow this pattern:
   ```html
   <!DOCTYPE html>
   <html lang="en">
   <head>
       <meta charset="UTF-8">
       <meta name="viewport" content="width=device-width, initial-scale=1.0">
       <link rel="icon" href="../assets/favicon.svg" type="image/svg+xml">
       <title>Page Title</title>
       <style>/* Inline styles */</style>
   </head>
   <body>
       <!-- Content -->
   </body>
   </html>
   ```

3. **Mobile-First Design**: All pages use viewport meta tags and responsive CSS

4. **JavaScript Usage**: Limited to specific features:
   - `music.html`: Shuffle functionality for song list (pages/music.html:195-212)
   - Homepage: Google Analytics tracking

5. **Styling Approach**: 
   - Most pages use inline `<style>` tags for self-contained styling
   - `globals.css` provides shared styles for some pages
   - CSS variables for consistent color schemes
   - **Canonical max-width**: All content areas should use `max-width: 700px` for consistency across posts, pages, and other content

### Common Tasks

- **Adding a new project**: Update the project cards section in `index.html`
- **Creating a blog post**: Create a new directory under `pages/` with an `index.html` file
- **Adding to photo gallery**: Add images to `assets/pics/` and update `pages/pics.html`
- **Updating resume**: Edit `pages/resume.html` directly