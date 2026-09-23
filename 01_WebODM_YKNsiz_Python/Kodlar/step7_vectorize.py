import os
import numpy as np
import rasterio
import cv2
import geopandas as gpd
from shapely.geometry import Polygon
from rasterstats import zonal_stats

# 1. Dosya Yolları
dsm_path = r"../../WebODM_Outputs/Extracted/odm_dem/dsm.tif"
output_geojson = r"../Sonuclar/Binalar_Gunes_Potansiyeli.geojson"

os.makedirs(os.path.dirname(output_geojson), exist_ok=True)

scale_factor = 0.1 # 10 kat küçült (~2500x2000 px)

print("[BİLGİ] DSM okunuyor (Hızlı bellek yönetimi ile düşük çözünürlükte)...")
with rasterio.open(dsm_path) as src:
    small_w = int(src.width * scale_factor)
    small_h = int(src.height * scale_factor)
    
    # Rasterio ile okurken doğrudan küçült (RAM'i şişirmez)
    dsm_small = src.read(
        1,
        out_shape=(small_h, small_w),
        resampling=rasterio.enums.Resampling.average
    )
    
    # Transform matrisini de ölçekle
    transform_small = src.transform * src.transform.scale(
        (src.width / dsm_small.shape[1]),
        (src.height / dsm_small.shape[0])
    )
    
    crs = src.crs
    nodata = src.nodata

# Nodata maskelemesi
if nodata is not None:
    mask = (dsm_small == nodata) | np.isnan(dsm_small)
else:
    mask = np.isnan(dsm_small)

dsm_clean = np.where(mask, np.nanmin(dsm_small), dsm_small)

print("[BİLGİ] DTM hesaplanıyor (Morfolojik Açılış)...")
# UZAKTAN ALGILAMA DÜZELTMESİ:
# GSD (Örnekleme Aralığı) şu an ~60 cm (0.6 m). 
# Binaları (max 50mx50m) DTM'den silebilmek için kernel boyutu binadan büyük olmalıdır!
# 50m / 0.6m = 83 piksel. Kernel'i (85, 85) yapıyoruz.
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (85, 85))
dtm_small = cv2.morphologyEx(dsm_clean, cv2.MORPH_OPEN, kernel)

print("[BİLGİ] Yükseklik farkı hesaplanıyor...")
z_diff = dsm_clean - dtm_small

print("[BİLGİ] Yükseklik maskesi (3m - 25m) oluşturuluyor...")
# Binaları tespit etmek için 3 metre ile 25 metre arası
bina_maskesi = (z_diff > 3.0) & (z_diff < 25.0)
bina_maskesi = bina_maskesi.astype(np.uint8) * 255

print("[BİLGİ] Gürültüler filtreleniyor...")
# Temizlik
small_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
bina_maskesi = cv2.morphologyEx(bina_maskesi, cv2.MORPH_OPEN, small_kernel)

print("[BİLGİ] Konturlar (Bina Siluetleri) bulunuyor...")
contours, hierarchy = cv2.findContours(bina_maskesi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

polygons = []
for cnt in contours:
    # Konturu basitleştir
    epsilon = 0.01 * cv2.arcLength(cnt, True)
    approx = cv2.approxPolyDP(cnt, epsilon, True)
    
    area = cv2.contourArea(approx)
    # Alan hesabını piksel cinsinden yapıyoruz (küçültülmüş pikseller).
    # Küçültülmüş resimde GSD ~ 60cm = 0.6m. 1 piksel = 0.36m2
    # 50m2 = ~140 piksel, 1000m2 = ~2700 piksel
    if 100 < area < 5000 and len(approx) >= 3:
        geo_coords = []
        for point in approx:
            x, y = point[0]
            # Küçültülmüş transform matrisini kullanarak koordinata çevir
            geo_x, geo_y = rasterio.transform.xy(transform_small, y, x)
            geo_coords.append((geo_x, geo_y))
        
        geo_coords.append(geo_coords[0])
        poly = Polygon(geo_coords)
        if poly.is_valid:
            polygons.append(poly)

print(f"[BİLGİ] {len(polygons)} adet potansiyel bina tespit edildi.")

if len(polygons) == 0:
    print("[HATA] Hiç bina bulunamadı! Eşik değerlerini veya alan hesabını kontrol edin.")
    exit(1)

gdf_binalar = gpd.GeoDataFrame(geometry=polygons, crs=crs)

print("[BİLGİ] Yükseklik ve Güneş Potansiyeli Hesaplanıyor...")
zonal_stats_result = zonal_stats(
    gdf_binalar, 
    dsm_path, 
    stats=['min', 'mean'],
    nodata=nodata
)

bina_id = []
yukseklikler = []
paneller = []
kapasiteler = []

for idx, stat in enumerate(zonal_stats_result):
    h_min = stat['min'] if stat['min'] is not None else 0
    h_mean = stat['mean'] if stat['mean'] is not None else 0
    
    net_h = h_mean - h_min
    if net_h < 3.0: 
        net_h = 3.0 
    
    bina_alani = gdf_binalar.geometry.iloc[idx].area
    kullanilabilir_alan = bina_alani * 0.70
    panel_sayisi = int(kullanilabilir_alan / 1.6)
    kurulu_guc_kwp = panel_sayisi * 0.35
    yillik_uretim_kwh = kurulu_guc_kwp * 1500
    
    bina_id.append(f"Bina_{idx+1}")
    yukseklikler.append(round(net_h, 2))
    paneller.append(panel_sayisi)
    kapasiteler.append(round(yillik_uretim_kwh, 2))

gdf_binalar['Bina_ID'] = bina_id
gdf_binalar['Net_Yukseklik'] = yukseklikler
gdf_binalar['Gunes_Paneli_Sayisi'] = paneller
gdf_binalar['Yillik_Uretim_kWh'] = kapasiteler

gdf_binalar = gdf_binalar.to_crs(epsg=4326)

print(f"[BİLGİ] GeoJSON kaydediliyor: {output_geojson}")
gdf_binalar.to_file(output_geojson, driver='GeoJSON')
print("[BAŞARILI] İşlem tamamlandı!")
