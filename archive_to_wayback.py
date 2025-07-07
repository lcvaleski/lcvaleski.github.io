#!/usr/bin/env python3
"""
Archive website URLs to the Wayback Machine.
This script submits all important URLs from logan.valeski.org to the Internet Archive.
"""

import os
import time
import requests
from urllib.parse import urljoin

# Base URL from environment variable or default
SITE_URL = os.environ.get('SITE_URL', 'https://logan.valeski.org')

# List of all URLs to archive (relative to the domain)
URLS_TO_ARCHIVE = [
    # Main pages
    '/',
    '/pages/resume.html',
    '/pages/refactor_roadmap.html',
    
    # Blog posts
    '/pages/bike_post/biking_to_class.html',
    '/pages/ellie_post/to_code.html',
    '/pages/boulder_post/boulder.html',
    
    # Hidden navigation pages
    '/pages/chess.html',
    '/pages/syllabus/index.html',
    '/pages/pics.html',
    '/pages/music.html',
    '/pages/scratchpad.html',
    
    # Important assets
    '/assets/favicon.svg',
]

def submit_to_wayback(url):
    """Submit a URL to the Wayback Machine for archiving."""
    wayback_save_url = f"https://web.archive.org/save/{url}"
    
    try:
        print(f"Archiving: {url}")
        response = requests.get(wayback_save_url, timeout=30)
        
        if response.status_code == 200:
            print(f"✓ Successfully archived: {url}")
            return True
        else:
            print(f"✗ Failed to archive {url}: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"✗ Timeout while archiving: {url}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Error archiving {url}: {e}")
        return False

def main():
    """Main function to archive all URLs."""
    print(f"Starting Wayback Machine archival for {SITE_URL}")
    print(f"Total URLs to archive: {len(URLS_TO_ARCHIVE)}")
    print("-" * 50)
    
    successful = 0
    failed = 0
    
    for relative_url in URLS_TO_ARCHIVE:
        # Convert relative URL to absolute
        full_url = urljoin(SITE_URL, relative_url)
        
        # Submit to Wayback Machine
        if submit_to_wayback(full_url):
            successful += 1
        else:
            failed += 1
        
        # Be polite to the Wayback Machine API - wait between requests
        time.sleep(2)
    
    print("-" * 50)
    print(f"Archival complete!")
    print(f"Successfully archived: {successful}/{len(URLS_TO_ARCHIVE)} URLs")
    
    if failed > 0:
        print(f"Failed to archive: {failed} URLs")
        exit(1)

if __name__ == "__main__":
    main()