# WebODM (EXIF GPS Destekli) Fotogrametrik Kalite Değerlendirme Raporu

Bu rapor, Güzelyurt (Aksaray) bölgesinde gerçekleştirilen İHA uçuşuna ait fotoğrafların **WebODM (OpenSfM)** altyapısı kullanılarak işlenmesi sonucu elde edilen istatistiklerin SfM (Structure from Motion) fotogrametrik kalite metriklerine göre analizini içermektedir. Mevcut model, Yer Kontrol Noktaları (GCP) kullanılmadan, "GPS-assisted georeferencing" (EXIF GPS destekli SfM/MVS georeferencing) yaklaşımıyla hizalanmıştır.

## 1. Proje ve Veri Özeti
*   **İşlem Süresi:** 3 Saat 47 Dakika
*   **İşlenen Görüntü Sayısı:** 166
*   **Kamera Tipi:** SONY DSC-WX220 (4896 x 3672)
*   **Projeksiyon (Koordinat) Sistemi:** EPSG:32636 (WGS 84 / UTM zone 36N)
*   **Toplam Kapsanan Alan:** ~0.65 $km^2$ (647,821 $m^2$)
*   **Yer Örnekleme Aralığı (GSD - Ground Sample Distance):** **6.09 cm/piksel**
    *   *Akademik Değerlendirme:* 6.09 cm GSD, bina geometrisi ve çatı yüzeylerinin ayrıntılı modellenmesi açısından yüksek mekânsal çözünürlük sağlamaktadır. Bununla birlikte LoD1/LoD2 uygunluğu yalnızca GSD üzerinden belirlenemez ve ayrıca geometrik doğruluk değerlendirmesi gerektirir.

## 2. Nokta Bulutu ve Eşleştirme (Tie Point) Kalitesi
*   **Çıkarılan Bağlama Noktası (Initial Points):** 216,752
*   **Başarıyla Yeniden Üretilen Noktalar (Reconstructed):** 214,499
    *   *Akademik Değerlendirme:* İlk noktaların %98.9'u rekonstrüksiyona dahil edilmiştir (%98.9 reconstruction retention). Bu oran, görüntüler arasındaki eşleşme ve SfM rekonstrüksiyonunun başarılı olduğunu gösteren olumlu bir göstergedir; ancak tek başına geometrik doğruluk ölçütü değildir.
*   **Gözlem Sayısı (Observations):** 923,022
*   **Yoğun Nokta Bulutu (Dense Point Cloud) Miktarı:** **40.295.778 Nokta** (~40.3 Milyon)
    *   *Akademik Değerlendirme:* Yaklaşık 40.3 milyon noktalık yoğun nokta bulutu, yüksek nokta yoğunluğuna işaret etmektedir; ancak nokta sayısı tek başına geometrik doğruluk göstergesi değildir.

## 3. Hata (Error) ve Doğruluk Değerlendirmesi

### A. Reprojection Error (Yeniden İzdüşüm Hatası)
*   **Ortalama Hata (Piksel cinsinden):** **1.16 Piksel**
    *   *Akademik Değerlendirme:* 1.16 px seviyesindeki ortalama reprojection error, görüntü eşleşmelerinin ve bundle adjustment çözümünün makul düzeyde olduğunu göstermektedir. Ancak bu metrik tek başına modelin gerçek arazi doğruluğunu temsil etmez.

### B. GPS Residual (Kalıntı) Değerleri
Drone'un EXIF GPS verisi (priors) ile modelin optimize edilmiş kamera pozisyonları arasındaki farklar (Residuals):
*   **X (Doğu-Batı) Residual:** 0.308 metre
*   **Y (Kuzey-Güney) Residual:** 0.103 metre
*   **Z (Yükseklik) Residual:** 0.170 metre
*   **Ortalama Residual (Mean):** 0.172 metre (~17 cm)
    *   *Akademik Değerlendirme:* Model kamera konumları ile görüntülerde bulunan GPS priors arasındaki residual yaklaşık 17 cm seviyesindedir. Ancak bağımsız YKN (GCP) veya Kontrol Noktası (CP - Check Point) kullanılmadığından bu değer modelin bağımsız mutlak doğruluğu (absolute accuracy) olarak yorumlanmamalıdır. Global yatay ötelemenin sınırlı olması, bazı bağıl ölçümlerde etkisinin düşük olmasını sağlayabilir; ancak alan ve yükseklik ölçümlerinin doğruluğu ayrıca bağımsız kontrol noktalarıyla değerlendirilmelidir.

## 4. Kamera Kalibrasyonu (OpenSfM Kamera Modeli ve Lens Distorsiyon Parametreleri)
Kamera lensinden kaynaklı bozulmalar sistem tarafından optimize edilmiştir:
*   Fokal uzunluk parametresi (normalize edilmiş değer olarak) başlangıçta 0.85 iken, optimizasyon sonrası **0.737** olarak güncellenmiştir (Bu değer fiziksel milimetre ölçüsü değildir).
*   Radyal distorsiyon parametreleri (k1, k2, k3) ve teğetsel parametreler (p1, p2) optimizasyon sürecine dahil edilmiştir.

## Sonuç

**Bu çalışma, GCP kullanılmadan ve görüntülerin EXIF GPS bilgileri kullanılarak gerçekleştirilen bir SfM/MVS rekonstrüksiyonudur. 6.09 cm GSD ve yaklaşık 40.3 milyon yoğun nokta, yüksek mekânsal çözünürlük ve yoğun bir 3B temsil elde edildiğini göstermektedir. 1.16 piksel reprojection error, görüntü eşleştirme ve bundle adjustment açısından makul bir sonuçtur. Bununla birlikte, EXIF GPS ile kamera pozisyonları arasındaki yaklaşık 17 cm'lik residual, bağımsız doğrulama noktaları bulunmadığından modelin mutlak konumsal doğruluğu olarak yorumlanmamalıdır. Gerçek mutlak doğruluğun belirlenmesi için bağımsız Check Point'ler ve/veya yüksek doğruluklu GCP ölçümleri gereklidir.**

*Not: Yeterli sayıda ve uygun dağılımda yüksek doğruluklu GCP kullanılması, mutlak konum doğruluğunun iyileştirilmesini sağlayabilir. İyileşmenin miktarı bağımsız Check Point'ler ile test edilmelidir.*
