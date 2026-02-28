# Photo-Intel

EXIF metadata and GPS extraction tool for digital images. Pulls out device info, capture settings, timestamps, and GPS coordinates then gives you a direct Google Maps link to the location.

Useful for OSINT investigations, digital forensics, or just checking what data your phone embeds in every photo you take.

## How It Works

Digital cameras and phones store metadata inside image files using the EXIF standard. This includes the device model, date/time, camera settings, and sometimes GPS coordinates. Most people dont realize this data exists. Social media platforms strip it on upload, but images shared directly (email, messaging, file transfer) keep everything.

This tool reads that metadata and presents it in a readable format.

## Usage

**Single image:**

    python extractor.py photo.jpg

**JSON output:**

    python extractor.py photo.jpg --json

**Batch mode scan an entire folder:**

    python extractor.py photos/ --batch

## Installation

    git clone https://github.com/Emirzonee/Photo-Intel-Tool.git
    cd Photo-Intel-Tool
    pip install -r requirements.txt

## What It Extracts

| Category | Fields |
|----------|--------|
| Device   | Make, Model, Software |
| Capture  | Date/Time, Exposure, ISO, Focal Length |
| Image    | Width, Height, Orientation |
| GPS      | Latitude, Longitude, Altitude, Google Maps URL |

## Important Notes

- Platforms like WhatsApp, Instagram, and Twitter strip EXIF data on upload so this tool wont find GPS in social media downloads
- Works with images taken directly from a camera or phone (JPEG, TIFF)
- PNG files rarely contain EXIF data
- This tool is for educational and authorized use only

## Project Structure

    Photo-Intel-Tool/
    |- extractor.py       # Main script
    |- requirements.txt   # Dependencies (Pillow)
    |- .gitignore
    |- LICENSE
    |- README.md

## License

MIT