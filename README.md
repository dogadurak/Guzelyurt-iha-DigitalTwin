# Güzelyurt İHA Digital Twin (Fotogrametri & 3B Şehir Modelleme)

Bu proje, Güzelyurt (Aksaray) bölgesinde insansız hava araçları (İHA/Drone) ile çekilen fotoğrafların işlenerek fotogrametrik haritalarının çıkarılmasını, binaların otomatik sayısallaştırılmasını (vektörizasyon) ve Güneş Enerjisi Potansiyeli analizini kapsayan kapsamlı bir **3B Şehir Modelleme (Digital Twin)** çalışmasıdır.

## Proje Klasör Yapısı (Monorepo)

Projemiz 3 farklı yaklaşım ile geliştirilmiştir ve karmaşıklığı önlemek için aşağıdaki gibi 3 ana klasöre ayrılmıştır:

### 1. `01_WebODM_YKNsiz_Python` (Mevcut Aşama)
*   WebODM ve OpenSfM motoru kullanılarak, sadece drone'un EXIF (GPS) verisiyle oluşturulmuş modeldir.
*   Yer Kontrol Noktası (YKN) kullanılmadan elde edilen bağıl ve mutlak RMS hataları incelenmiştir.
*   **İçerik:** Python sayısallaştırma kodları, Zonal Statistics güneş analizi, İnteraktif 3B Şehir Modeli HTML'i ve Kalite/Hata analiz raporları bu klasördedir.

### 2. `02_WebODM_YKNli_Python` (Gelecek Aşama)
*   WebODM'de GCP Interface kullanılarak araziden toplanan YKN (Yer Kontrol Noktası) koordinatlarının modele dahil edilmesiyle oluşturulacak "Milimetrik Hassasiyetli" modeldir.

### 3. `03_Agisoft_Metashape` (Gelecek Aşama)
*   Aynı veri setinin klasik masaüstü yazılımı olan Agisoft Metashape ile üretilmiş versiyonu ve hata raporları yer alacaktır.

*(Not: Ham drone fotoğrafları, yüzlerce MB'lık TIF haritaları ve Nokta Bulutu (LAZ/OBJ) dosyaları boyut limitleri sebebiyle GitHub'a yüklenmemiştir (.gitignore).* 
