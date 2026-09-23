import os
import glob
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def get_exif_data(image):
    """Returns a dictionary from the exif data of an PIL Image item. Also converts the GPS Tags"""
    exif_data = {}
    info = image._getexif()
    if info:
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "GPSInfo":
                gps_data = {}
                for t in value:
                    sub_decoded = GPSTAGS.get(t, t)
                    gps_data[sub_decoded] = value[t]
                exif_data[decoded] = gps_data
            else:
                exif_data[decoded] = value
    return exif_data

def get_lat_lon(exif_data):
    """Returns the latitude and longitude, if available, from the provided exif_data"""
    lat = None
    lon = None
    if "GPSInfo" in exif_data:
        gps_info = exif_data["GPSInfo"]
        gps_latitude = gps_info.get("GPSLatitude")
        gps_latitude_ref = gps_info.get("GPSLatitudeRef")
        gps_longitude = gps_info.get("GPSLongitude")
        gps_longitude_ref = gps_info.get("GPSLongitudeRef")
        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
            lat = convert_to_degrees(gps_latitude)
            if gps_latitude_ref != "N":
                lat = 0 - lat
            lon = convert_to_degrees(gps_longitude)
            if gps_longitude_ref != "E":
                lon = 0 - lon
    return lat, lon

def convert_to_degrees(value):
    """Helper function to convert the GPS coordinates stored in the EXIF to degress in float format"""
    d0 = value[0][0]
    d1 = value[0][1]
    d = float(d0) / float(d1)

    m0 = value[1][0]
    m1 = value[1][1]
    m = float(m0) / float(m1)

    s0 = value[2][0]
    s1 = value[2][1]
    s = float(s0) / float(s1)

    return d + (m / 60.0) + (s / 3600.0)

data_dir = r"C:\Users\PC\Desktop\mügehoca_digitalphoto_3Bcitymodelling\GuzelyurtIHA_DATA\GuzelyurtIHA_DATA"

img_folders = [os.path.join(data_dir, "img"), os.path.join(data_dir, "img2")]
total_images = 0
valid_gps = 0

print(f"--- Veri Analiz Raporu ---")
print(f"Görüntü dizinleri inceleniyor...")

for folder in img_folders:
    if os.path.exists(folder):
        images = glob.glob(os.path.join(folder, "*.JPG")) + glob.glob(os.path.join(folder, "*.jpg"))
        total_images += len(images)
        for img_path in images:
            try:
                img = Image.open(img_path)
                exif = get_exif_data(img)
                lat, lon = get_lat_lon(exif)
                if lat and lon:
                    valid_gps += 1
            except Exception as e:
                pass

print(f"Toplam Görüntü Sayısı: {total_images}")
print(f"GPS Verisi Bulunan Görüntü Sayısı: {valid_gps}")

gcp_file = os.path.join(data_dir, "NN_Y_X_Z.txt")
if os.path.exists(gcp_file):
    with open(gcp_file, "r") as f:
        lines = f.readlines()
    print(f"\nYer Kontrol Noktası (GCP) Dosyası: Bulundu!")
    print(f"Toplam GCP Sayısı: {len(lines)}")
else:
    print(f"Yer Kontrol Noktası Dosyası bulunamadı.")
