import os
import cv2
import numpy as np
import geopandas as gpd
from shapely.geometry import Polygon
import rasterio
from rasterstats import zonal_stats
from rasterio.features import shapes
import warnings

# Uyarıları gizle
warnings.filterwarnings("ignore")

def detect_buildings_from_ortho_and_dsm(ortho_path, dsm_path):
    print("--- 7. Sayısallaştırma ve Bina Tespiti ---")
    print(f"Ortofoto yükleniyor: {ortho_path}")
    print(f"Yükseklik Modeli (DSM) yükleniyor: {dsm_path}")
    
    # Gerçek veri yolları mevcut mu kontrol et
    if not os.path.exists(ortho_path) or not os.path.exists(dsm_path):
        print("[UYARI] Gerçek WebODM çıktıları bulunamadı. Şimdilik sentetik/örnek analiz modu çalıştırılıyor...")
        return generate_synthetic_solar_data()

    # 1. DSM (Yükseklik) üzerinden Binaları Çıkartma
    # Mantık: DSM üzerindeki keskin yükseklik farkları (zemin vs çatı) binaları verir.
    with rasterio.open(dsm_path) as src_dsm:
        dsm_data = src_dsm.read(1)
        transform = src_dsm.transform
        crs = src_dsm.crs
        
        # Geçersiz verileri (NoData) filtrele
        nodata = src_dsm.nodata
        if nodata is not None:
            dsm_data = np.where(dsm_data == nodata, np.nan, dsm_data)

    # Basit bir eşikleme (Threshold) ile yerden 3 metre ve daha yüksek olan yapıları bina kabul edelim
    # (Örnek olarak zeminin minimum kotuna göre hesaplıyoruz)
    zemin_kotu = np.nanpercentile(dsm_data, 5) # En düşük %5'lik dilim genelde zemindir
    bina_maskesi = (dsm_data > (zemin_kotu + 3.0)).astype(np.uint8)

    print(f"Zemin kotu tahmini: {zemin_kotu:.2f} metre. Zemin +3m üzerindeki alanlar bina olarak maskelendi.")

    # OpenCV ile maskeyi temizleme (Gürültüleri/Ağaçları elemek için morfolojik işlemler)
    kernel = np.ones((5, 5), np.uint8)
    bina_maskesi_temiz = cv2.morphologyEx(bina_maskesi, cv2.MORPH_OPEN, kernel) # Küçük noktaları sil
    bina_maskesi_temiz = cv2.morphologyEx(bina_maskesi_temiz, cv2.MORPH_CLOSE, kernel) # Çatıdaki boşlukları doldur

    # 2. Vektörizasyon (Raster Maskeyi Poligonlara Çevirme)
    print("Vektörizasyon yapılıyor (Poligonlar oluşturuluyor)...")
    polygons = []
    
    for geom, value in shapes(bina_maskesi_temiz, mask=(bina_maskesi_temiz==1), transform=transform):
        poly = Polygon(geom["coordinates"][0])
        # Çok küçük poligonları (örn: arabalar, ağaçlar) eleyelim (Alan < 30 metrekare)
        if poly.area > 30:
            polygons.append(poly)
            
    print(f"Toplam {len(polygons)} adet potansiyel bina çatısı tespit edildi.")

    # GeoDataFrame oluştur
    gdf = gpd.GeoDataFrame({'Bina_ID': range(1, len(polygons) + 1)}, geometry=polygons, crs=crs)

    # 3. Yükseklik Ataması (Zonal Statistics)
    print("Zonal Statistics ile Çatı Yükseklikleri Hesaplanıyor...")
    dsm_stats = zonal_stats(gdf, dsm_data, affine=transform, stats=['mean', 'max'], nodata=np.nan)
    
    gdf['Zemin_Kot'] = zemin_kotu
    gdf['Cati_Ort_Kot'] = [stat['mean'] for stat in dsm_stats]
    gdf['Net_Yukseklik'] = gdf['Cati_Ort_Kot'] - gdf['Zemin_Kot']

    # 4. Güneş Paneli Potansiyeli Hesaplama
    calculate_solar_potential(gdf)

    return gdf

def generate_synthetic_solar_data():
    """Gerçek veri henüz yoksa sistemi test etmek için sahte/sentetik veri üretir."""
    print("Sentetik (Test) verisi ile Güneş Paneli Potansiyeli hesaplanıyor...")
    poly1 = Polygon([(619147, 4239226), (619157, 4239226), (619157, 4239216), (619147, 4239216)])
    poly2 = Polygon([(619160, 4239200), (619180, 4239200), (619180, 4239190), (619160, 4239190)])
    
    gdf = gpd.GeoDataFrame({'Bina_ID': [1, 2]}, geometry=[poly1, poly2], crs="EPSG:32636")
    gdf['Zemin_Kot'] = [1450.0, 1450.0]
    gdf['Cati_Ort_Kot'] = [1462.5, 1458.0]
    gdf['Net_Yukseklik'] = gdf['Cati_Ort_Kot'] - gdf['Zemin_Kot']
    
    calculate_solar_potential(gdf)
    return gdf

def calculate_solar_potential(gdf):
    print("--- Güneş Paneli Potansiyeli Hesaplanıyor ---")
    
    # Güzelyurt ortalama yıllık güneşlenme baz alınmıştır
    # 1 m2 panel ortalama 330W (0.33 kW) güç üretir.
    PANEL_ALANI = 1.6 # m2
    PANEL_GUCU = 0.33 # kW
    KULLANILABILIR_CATI_ORANI = 0.70 # Çatının %70'ine panel döşenebilir (bacalar, kenar boşlukları)
    YILLIK_GUNES_SAATI = 1600 # Güzelyurt bölgesi için tahmini saat
    SISTEM_VERIMLILIGI = 0.80 # İnvertör, kablo, sıcaklık kayıpları sonrası verim

    # Hesaplamalar
    gdf['Cati_Alani_m2'] = gdf.area
    gdf['Kullanilabilir_Alan_m2'] = gdf['Cati_Alani_m2'] * KULLANILABILIR_CATI_ORANI
    
    # Kaç panel sığar?
    gdf['Maks_Panel_Sayisi'] = np.floor(gdf['Kullanilabilir_Alan_m2'] / PANEL_ALANI)
    
    # Kurulu Güç (kWp)
    gdf['Kurulu_Guc_kWp'] = gdf['Maks_Panel_Sayisi'] * PANEL_GUCU
    
    # Yıllık Enerji Üretimi (kWh/Yıl)
    # Formül: Kurulu Güç * Yıllık Güneşlenme * Verimlilik
    gdf['Yillik_Uretim_kWh'] = gdf['Kurulu_Guc_kWp'] * YILLIK_GUNES_SAATI * SISTEM_VERIMLILIGI

    print(f"Toplam tespit edilen çatı alanı: {gdf['Cati_Alani_m2'].sum():.2f} m2")
    print(f"Bölgedeki binaların Yıllık Toplam Güneş Enerjisi Üretim Potansiyeli: {gdf['Yillik_Uretim_kWh'].sum():.2f} kWh/Yıl")

    # Çıktıyı kaydet
    out_file = r"C:\Users\PC\Desktop\mügehoca_digitalphoto_3Bcitymodelling\Binalar_Gunes_Potansiyeli.geojson"
    gdf.to_file(out_file, driver='GeoJSON')
    print(f"Güneş Paneli Analiz Sonuçları GeoJSON olarak kaydedildi: {out_file}")

if __name__ == "__main__":
    # WebODM işlemi bittiğinde oluşacak gerçek dosya yolları:
    orto_path = r"C:\Users\PC\Desktop\mügehoca_digitalphoto_3Bcitymodelling\WebODM_Outputs\odm_orthophoto.tif"
    dsm_path = r"C:\Users\PC\Desktop\mügehoca_digitalphoto_3Bcitymodelling\WebODM_Outputs\dsm.tif"
    
    result_gdf = detect_buildings_from_ortho_and_dsm(orto_path, dsm_path)
    print("İşlem Başarıyla Tamamlandı!")
