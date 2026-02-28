"""
Photo-Intel — EXIF Metadata & GPS Extractor

Extracts embedded metadata from images including device info,
timestamps, and GPS coordinates. Useful for OSINT analysis
and digital forensics.

Usage:
    python extractor.py photo.jpg
    python extractor.py photo.jpg --json
    python extractor.py photos/ --batch
"""

import sys
import os
import json
import argparse
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


def extract_exif(image_path):
    """Read EXIF data from image, return as a clean dict."""
    try:
        img = Image.open(image_path)
        raw = img._getexif()
        if not raw:
            return None

        data = {}
        for tag_id, value in raw.items():
            tag_name = TAGS.get(tag_id, str(tag_id))
            # skip binary blobs that aren't useful
            if isinstance(value, bytes) and len(value) > 100:
                continue
            data[tag_name] = value
        return data
    except Exception as e:
        print(f"[!] Error reading {image_path}: {e}")
        return None


def parse_gps(exif_data):
    """Extract and parse GPS info from EXIF data."""
    if "GPSInfo" not in exif_data:
        return None

    gps_raw = {}
    for key, val in exif_data["GPSInfo"].items():
        tag = GPSTAGS.get(key, key)
        gps_raw[tag] = val

    try:
        lat = dms_to_decimal(gps_raw["GPSLatitude"])
        lon = dms_to_decimal(gps_raw["GPSLongitude"])

        if gps_raw.get("GPSLatitudeRef") == "S":
            lat = -lat
        if gps_raw.get("GPSLongitudeRef") == "W":
            lon = -lon

        altitude = None
        if "GPSAltitude" in gps_raw:
            altitude = float(gps_raw["GPSAltitude"])

        return {
            "latitude": round(lat, 6),
            "longitude": round(lon, 6),
            "altitude": altitude,
            "maps_url": f"https://www.google.com/maps?q={lat},{lon}",
        }
    except (KeyError, TypeError, ZeroDivisionError):
        return None


def dms_to_decimal(dms):
    """Convert (degrees, minutes, seconds) tuple to decimal."""
    d = float(dms[0])
    m = float(dms[1])
    s = float(dms[2])
    return d + (m / 60.0) + (s / 3600.0)


def build_report(image_path, exif_data):
    """Build a structured report dict from EXIF data."""
    report = {
        "file": os.path.basename(image_path),
        "device": {
            "make": str(exif_data.get("Make", "unknown")).strip(),
            "model": str(exif_data.get("Model", "unknown")).strip(),
            "software": str(exif_data.get("Software", "unknown")).strip(),
        },
        "capture": {
            "datetime": str(exif_data.get("DateTime", "unknown")),
            "exposure": str(exif_data.get("ExposureTime", "unknown")),
            "iso": str(exif_data.get("ISOSpeedRatings", "unknown")),
            "focal_length": str(exif_data.get("FocalLength", "unknown")),
        },
        "image": {
            "width": exif_data.get("ExifImageWidth", "unknown"),
            "height": exif_data.get("ExifImageHeight", "unknown"),
            "orientation": str(exif_data.get("Orientation", "unknown")),
        },
        "gps": parse_gps(exif_data),
    }
    return report


def print_report(report):
    """Pretty print a single image report."""
    print(f"\n  File: {report['file']}")
    print("-" * 45)

    print("  Device:")
    print(f"    Make:      {report['device']['make']}")
    print(f"    Model:     {report['device']['model']}")
    print(f"    Software:  {report['device']['software']}")

    print("  Capture:")
    print(f"    Date/Time: {report['capture']['datetime']}")
    print(f"    Exposure:  {report['capture']['exposure']}")
    print(f"    ISO:       {report['capture']['iso']}")

    print("  Image:")
    print(f"    Size:      {report['image']['width']}x{report['image']['height']}")

    if report["gps"]:
        print("  GPS:")
        print(f"    Lat:       {report['gps']['latitude']}")
        print(f"    Lon:       {report['gps']['longitude']}")
        if report["gps"]["altitude"]:
            print(f"    Altitude:  {report['gps']['altitude']}m")
        print(f"    Maps:      {report['gps']['maps_url']}")
    else:
        print("  GPS:       not available")

    print("-" * 45)


def analyze_image(image_path, as_json=False):
    """Analyze a single image and display results."""
    exif = extract_exif(image_path)
    if not exif:
        print(f"[!] No EXIF data found in {image_path}")
        return None

    report = build_report(image_path, exif)

    if as_json:
        print(json.dumps(report, indent=2, default=str))
    else:
        print_report(report)

    return report


def main():
    parser = argparse.ArgumentParser(description="Photo-Intel — EXIF & GPS Extractor")
    parser.add_argument("path", help="image file or directory")
    parser.add_argument("--json", action="store_true", help="output as JSON")
    parser.add_argument("--batch", action="store_true",
                        help="process all images in a directory")
    args = parser.parse_args()

    if args.batch and os.path.isdir(args.path):
        extensions = (".jpg", ".jpeg", ".png", ".tiff")
        files = [os.path.join(args.path, f) for f in os.listdir(args.path)
                 if f.lower().endswith(extensions)]

        if not files:
            print(f"[!] No image files found in {args.path}")
            sys.exit(1)

        print(f"[*] Scanning {len(files)} image(s) in {args.path}...\n")

        results = []
        for f in sorted(files):
            r = analyze_image(f, args.json)
            if r:
                results.append(r)

        print(f"\n[+] Processed {len(results)}/{len(files)} images with EXIF data.")

    elif os.path.isfile(args.path):
        analyze_image(args.path, args.json)

    else:
        print(f"[!] Path not found: {args.path}")
        sys.exit(1)


if __name__ == "__main__":
    main()  