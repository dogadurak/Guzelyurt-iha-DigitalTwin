# WebODM (YKN'siz / GPS Destekli) Fotogrametrik Kalite ve Hata Analizi Raporu

Bu rapor, Güzelyurt (Aksaray) bölgesinde gerçekleştirilen İHA uçuşuna ait fotoğrafların **WebODM (OpenSfM)** altyapısı kullanılarak işlenmesi sonucu elde edilen istatistiklerin "Uzaktan Algılama" (Remote Sensing) standartlarına göre analizini içermektedir. Mevcut model, Yer Kontrol Noktaları (YKN/GCP) kullanılmadan, doğrudan drone'un EXIF verisindeki GPS koordinatlarına dayanılarak (RTK/PPK veya standart GPS) hizalanmıştır.

## 1. Proje ve Veri Özeti
*   **İşlem Süresi:** 3 Saat 47 Dakika
*   **İşlenen Görüntü Sayısı:** 166
*   **Kamera Tipi:** SONY DSC-WX220 (4896 x 3672)
*   **Projeksiyon (Koordinat) Sistemi:** EPSG:32636 (WGS 84 / UTM zone 36N)
*   **Toplam Kapsanan Alan:** ~0.65 $km^2$ (647,821 $m^2$)
*   **Yer Örnekleme Aralığı (GSD - Ground Sample Distance):** **6.09 cm/piksel**
    *   *Uzman Yorumu:* Modeldeki 1 pikselin arazide 6 cm'ye denk geldiğini gösterir. Bir şehir modellemesi (LoD1/LoD2) ve güneş paneli tespiti için 6 cm'lik GSD, dünya literatür standartlarında (5-10 cm) oldukça ideal ve yüksek çözünürlüklü bir değerdir.

## 2. Nokta Bulutu ve Eşleştirme (Tie Point) Kalitesi
*   **Çıkarılan Bağlama Noktası (Initial Points):** 216,752
*   **Başarıyla Yeniden Üretilen Noktalar (Reconstructed):** 214,499 (%98.9 Başarı Oranı)
*   **Gözlem Sayısı (Observations):** 923,022
*   **Yoğun Nokta Bulutu (Dense Point Cloud) Miktarı:** **40.295.778 Nokta** (~40 Milyon)
    *   *Uzman Yorumu:* OpenSfM algoritması, fotoğraflardaki ortak noktaları (Tie Points) %98.9 gibi mükemmel bir oranla eşleştirmiştir. Toplamda 40 milyonluk yoğun nokta bulutu üretilmesi, binaların ve topoğrafyanın geometrik yapısının (çatı eğimleri, kalkan duvarlar) milimetrik olarak modellenebildiğini kanıtlamaktadır. Agisoft raporuyla kıyaslarken en çok bakılacak yer burasıdır.

## 3. Hata (Error) ve Doğruluk Analizi
Bir fotogrametri projesinde iç ve dış yöneltmelerin ne kadar başarılı olduğu, hata metrikleri ile ölçülür.

### A. Reprojection Error (Yeniden İzdüşüm Hatası)
*   **Hata Payı (Piksel cinsinden):** **1.16 Piksel**
    *   *Uzman Yorumu:* Algoritmanın hesapladığı 3B noktanın, 2B fotoğraftaki asıl yerine olan uzaklığıdır. Literatürde 1 pikselin altı (veya 1-1.5 arası) "Kabul Edilebilir/Başarılı" sayılır. 1.16 piksel, YKN (GCP) olmayan bir model için oldukça kararlı bir kamera kalibrasyonu (Bundle Block Adjustment) yapıldığını gösterir.

### B. Mutlak Konum Doğruluğu (Absolute Geolocation Error - GPS)
Drone'un GPS verisi ile modelin oturduğu yer arasındaki sapma miktarları (RMSE):
*   **X (Doğu-Batı) Hatası:** 0.308 metre (30.8 cm)
*   **Y (Kuzey-Güney) Hatası:** 0.103 metre (10.3 cm)
*   **Z (Yükseklik) Hatası:** 0.170 metre (17.0 cm)
*   **Ortalama Ortalama Hata (Mean Error):** 0.172 metre (~17 cm)
    *   *Uzman Yorumu:* Sisteme hiçbir manuel Yer Kontrol Noktası (YKN) **girilmemesine rağmen**, model arazide sadece ortalama **17 cm'lik** bir hata ile oturmuştur. Standart bir drone GPS'i (RTK/PPK olmayan) için bu doğruluk payı muazzamdır. Şehir plancılığında (LoD1/LoD2) ve güneş potansiyeli (çatı alanı hesaplama) gibi bağıl alan analizlerinde bu kadarlık bir mutlak sapma sonucu etkilemez (çünkü alan değişmez, sadece dünya üzerindeki konumu 17 cm kayar).

## 4. Kamera Kalibrasyonu (Brown Algoritması)
Kamera lensinden kaynaklı bükülmeler (Radyal ve Teğetsel distorsiyon) sistem tarafından otomatik optimize edilmiştir:
*   Fokal Uzaklık (f) başlangıçta 0.85 iken, optimizasyon sonrası **0.737** olarak hesaplanmıştır.
*   Radyal distorsiyon parametreleri (k1, k2, k3) başarıyla düzeltilmiştir. (Agisoft ile karşılaştırıldığında Agisoft'un fokal uzaklık ve k parametrelerindeki çözüm yeteneği ile OpenSfM'in yeteneği yarışabilir düzeydedir).

## Sonuç ve Akademik Değerlendirme
Elde edilen sonuçlar, **YKN (GCP) desteği olmaksızın** "Direct Georeferencing" (Doğrudan Jeoreferanslandırma) metoduyla üretilebilecek en kaliteli modellerden birini temsil etmektedir. 6 cm GSD, 40 Milyon nokta bulutu ve ~17 cm RMS GPS hatası; güneş enerjisi ve akıllı şehir uygulamaları (3B City Modelling) için fazlasıyla yeterli bir geometrik doğruluk sağlamıştır. 

Projenin devamında, YKN'lerin (Ground Control Points) sisteme dahil edilmesiyle (GCP Interface), X, Y ve Z eksenindeki ~17 cm'lik GPS sapmasının **1-3 cm aralığına (milimetrik hassasiyete)** düşürülmesi öngörülmektedir. Ancak mevcut form, akademik bir çalışmanın veri analizleri ve binaların göreceli (bağıl) yükseklik (DSM-DTM) hesaplamaları için tam tutarlılıktadır.
