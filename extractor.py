import sys
import os
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def get_exif_data(image_path):
    try:
        image = Image.open(image_path)
        # Exif verisi yoksa None doner
        exif_raw = image._getexif()
        if not exif_raw:
            return None

        data = {}
        for tag_id, value in exif_raw.items():
            tag_name = TAGS.get(tag_id, tag_id)
            data[tag_name] = value
        return data
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def get_gps_details(exif_data):
    if "GPSInfo" not in exif_data:
        return None
    
    gps_info = {}
    for key in exif_data["GPSInfo"].keys():
        name = GPSTAGS.get(key, key)
        gps_info[name] = exif_data["GPSInfo"][key]
    return gps_info

def convert_to_degrees(value):
    """
    GPS koordinatlarini (Derece, Dakika, Saniye) ondalik formata cevirir.
    """
    d = float(value[0])
    m = float(value[1])
    s = float(value[2])
    return d + (m / 60.0) + (s / 3600.0)

def main():
    print("Exif Metadata Extraction Tool v1.0")
    print("-" * 35)

    # Kullanicidan dosya yolu al
    image_path = input("Enter image path: ").strip().strip('"')

    if not os.path.exists(image_path):
        print(f"Error: File '{image_path}' not found.")
        sys.exit(1)

    print(f"\nAnalyzing '{image_path}'...\n")
    
    exif_data = get_exif_data(image_path)

    if not exif_data:
        print("No Exif metadata found in this image.")
        sys.exit(0)

    # Temel Bilgiler
    print("--- Device Information ---")
    print(f"Make     : {exif_data.get('Make', 'Unknown')}")
    print(f"Model    : {exif_data.get('Model', 'Unknown')}")
    print(f"Software : {exif_data.get('Software', 'Unknown')}")
    print(f"Date/Time: {exif_data.get('DateTime', 'Unknown')}")

    # GPS Bilgisi
    gps_data = get_gps_details(exif_data)
    
    if gps_data:
        print("\n--- GPS Coordinates ---")
        try:
            lat = convert_to_degrees(gps_data['GPSLatitude'])
            lon = convert_to_degrees(gps_data['GPSLongitude'])
            
            # Referans kontrolu (Guney ve Bati negatif olmalidir)
            if gps_data.get('GPSLatitudeRef') == 'S': lat = -lat
            if gps_data.get('GPSLongitudeRef') == 'W': lon = -lon

            print(f"Latitude : {lat}")
            print(f"Longitude: {lon}")
            print(f"Maps URL : https://www.google.com/maps?q={lat},{lon}")
        except Exception as e:
            print(f"Error decoding GPS data: {e}")
    else:
        print("\n--- GPS Coordinates ---")
        print("No GPS data available.")

if __name__ == "__main__":
    main()