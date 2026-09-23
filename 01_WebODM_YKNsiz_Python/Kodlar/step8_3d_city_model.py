import json
import pydeck as pdk
import geopandas as gpd

# 1. GeoJSON Dosyasını Oku
geojson_path = r"../Sonuclar/Binalar_Gunes_Potansiyeli.geojson"
print(f"[BİLGİ] {geojson_path} dosyası okunuyor...")
gdf = gpd.read_file(geojson_path)

# Veriyi kontrol et, Net_Yukseklik veya Gunes_Uretimi_kWh sütunlarındaki NaN değerleri 0 yap
if 'Net_Yukseklik' in gdf.columns:
    gdf['Net_Yukseklik'] = gdf['Net_Yukseklik'].fillna(10) # Bulunamayanlara varsayılan 10m
else:
    gdf['Net_Yukseklik'] = 10

if 'Yillik_Uretim_kWh' in gdf.columns:
    gdf['Yillik_Uretim_kWh'] = gdf['Yillik_Uretim_kWh'].fillna(0)

# Çatı Alanını EPSG:32636 (Metre) cinsinden hesaplayıp ekle (Tooltip için)
gdf['Alan_m2'] = gdf.to_crs(epsg=32636).area.round(1)

# 2. PyDeck için uygun formata (JSON) dönüştür
# PyDeck, doğrudan geopandas verilerini alabilir, ama koordinat sisteminin EPSG:4326 (WGS84 Enlem/Boylam) olması gerekir!
print("[BİLGİ] Koordinat sistemi WGS84 (EPSG:4326)'e dönüştürülüyor...")
gdf = gdf.to_crs(epsg=4326)

# Haritanın merkez noktasını bul (Kamera açısı için)
center_lon = gdf.geometry.centroid.x.mean()
center_lat = gdf.geometry.centroid.y.mean()

# Renklendirme mantığı (Güneş potansiyeline göre renk verelim: Yeşil=İyi, Sarı=Orta, Kırmızı=Düşük)
def get_color(row):
    potansiyel = row.get('Yillik_Uretim_kWh', 0)
    if potansiyel > 50000:
        return [0, 255, 0, 220]  # Yeşil (Çok iyi)
    elif potansiyel > 20000:
        return [255, 255, 0, 220] # Sarı (Orta)
    else:
        return [255, 0, 0, 220]   # Kırmızı (Düşük)

gdf['fill_color'] = gdf.apply(get_color, axis=1)

# 3. PyDeck Layer (Katman) Oluştur
print("[BİLGİ] 3B Şehir Modeli Katmanı oluşturuluyor...")
layer = pdk.Layer(
    "GeoJsonLayer",
    gdf,
    opacity=0.9,
    stroked=True,
    filled=True,
    extruded=True, # 3 BOYUTLU YAP!
    wireframe=False, # Daha temiz kutu görünümü için
    get_elevation="Net_Yukseklik", # Akademik doğruluk için 1:1 gerçek yükseklik
    get_fill_color="fill_color",
    get_line_color=[100, 100, 100],
    pickable=True, # Tıklanabilir olsun
)

# 4. Kamera Açısını Ayarla
view_state = pdk.ViewState(
    latitude=center_lat,
    longitude=center_lon,
    zoom=16,
    pitch=50, # Kamerayı eğerek 3B görünümü sağla
    bearing=0
)

# 5. Haritayı Oluştur ve HTML Olarak Kaydet
print("[BİLGİ] İnteraktif HTML Haritası kaydediliyor...")
tooltip = {
    "html": "<b>Bina ID:</b> {Bina_ID}<br/>"
            "<b>Çatı Alanı:</b> {Alan_m2} m²<br/>"
            "<b>Yükseklik:</b> {Net_Yukseklik} m<br/>"
            "<b>Yıllık Güneş Potansiyeli:</b> {Yillik_Uretim_kWh} kWh",
    "style": {"background": "rgba(50,50,50,0.9)", "color": "white", "font-family": '"Helvetica Neue", Arial', "z-index": "10000"}
}

r = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip=tooltip,
    map_style='light' # Arkada açık renkli bir harita altlığı
)

r.to_html(r"../Sonuclar/Guzelyurt_3B_Sehir_Modeli.html")
print("[BAŞARILI] Harita başarıyla oluşturuldu! Lütfen 'Sonuclar/Guzelyurt_3B_Sehir_Modeli.html' dosyasına çift tıklayıp açın.")
