# Fotogrametri ve Uzaktan Algılama: Aşama 1 Öğrenme Notları

Bu doküman, Güzelyurt 3B Şehir Modeli projesinin **YKN'siz (GCP-Free) Aşama 1** sürecinde yaşadığımız sorunları, bu sorunların arkasındaki teorik nedenleri ve profesyonellerin (bizim) bu sorunları nasıl çözdüğünü anlaman için hazırlanmıştır. Hızla ilerlerken konudan kopmaman ve tez sunumunda hocana her şeyi bilimsel olarak açıklayabilmen için altın değerindedir.

---

## 1. Devasa Veriler ve RAM Taşması (MemoryError)
- **Ne Yaşadık?** İlk yazdığımız kodlar 25.000 x 20.000 piksellik (yaklaşık 500 Milyon piksel) TIF dosyalarını (DSM) okumaya çalışırken bilgisayar kilitlendi ve bellek (MemoryError) hatası verdi.
- **Neden Oldu?** Uçuş kalitesi (GSD - Yer Örnekleme Aralığı) yaklaşık 6 cm'ye kadar düştüğü için dosya boyutları çok büyüdü. Hiçbir standart bilgisayarın RAM'i bu kadar büyük bir matrisi tek seferde hafızada tutamaz.
- **Profesyoneller Nasıl Çözer?** "Downsampling" (Ölçek Küçültme). Görüntü işleme kütüphanesi (Rasterio) ile veriyi ham haliyle okumak yerine `scale_factor = 0.1` (10 kat küçülterek) okuduk. Böylece analizleri 6 cm GSD yerine **60 cm GSD** ile (RAM'i hiç yormadan) saniyeler içinde tamamladık. Bina gibi büyük kütleleri bulmak için 60 cm fazlasıyla yeterlidir.

## 2. Ağaçların Bina Zannedilmesi (Filtreleme Hataları)
- **Ne Yaşadık?** DTM (Arazi Modeli) ile DSM (Yüzey Modeli) arasındaki farkı alıp "3 metreden yüksek olan yerleri kes" dediğimizde, haritada devasa ağaç kümeleri de bina olarak algılandı. (Bina sayımız 586'ya fırlamıştı).
- **Neden Oldu?** Algoritma neyin bina neyin ağaç olduğunu bilemez. Yüksekliği 5 metre olan bir çam ağacı ile 5 metrelik tek katlı bir evin Z (Yükseklik) verisi tamamen aynıdır.
- **Profesyoneller Nasıl Çözer?** Spektral İndeks (Bant Matematiği) kullanımı. Elimizde Kızılötesi (NIR) bant olmadığı için NDVI (Bitki İndeksi) kullanamadık. Bunun yerine elimizdeki RGB Ortofotoyu kullanarak **VARI (Görünür Atmosferik Direnç İndeksi)** hesapladık:
  > `VARI = (Yeşil - Kırmızı) / (Yeşil + Kırmızı - Mavi)`
  Bu formül ağaçları (yeşil klorofil) beyaz parlatır, binaları karartır. Parlayan pikselleri "Ağaç" olarak etiketledik ve onları yükseklik maskesinden sildik. Bu sayede 170 adet devasa sahte binayı çöpe attık.

## 3. Binaların Tırtıklı ve Erimiş (Blob) Görünmesi
- **Ne Yaşadık?** Başlangıçta binaların sınırları amip gibi, kenarları erimiş ve yamuk yumuktu (Özellikle HTML haritada binalar eriyen peynir gibi görünüyordu).
- **Neden Oldu?** Piksel tabanlı eşikleme (Thresholding) yapıldığında sınırlar kare şeklindeki piksellerin zikzaklarını (Gürültü/Noise) taşır. 
- **Profesyoneller Nasıl Çözer?** Geometrik Düzenleme (Regularization). Bilgisayarlı Görü (OpenCV) kütüphanesinden `cv2.minAreaRect` (Minimum Alanlı Döndürülmüş Dikdörtgen) algoritmasını kullandık. Bu algoritma o amorf piksellerin dışından geçen en kusursuz ve en dar dörtgeni çizer. Böylece tüm binaları cetvelle çizilmiş gibi düzgün prizmalara dönüştürdük.

## 4. Renklerin Yanlış Çıkması (Tüm Haritanın Kırmızı Olması)
- **Ne Yaşadık?** Tüm işlemleri mükemmel yapsak da HTML haritasında tüm binalar kırmızı (Sıfır Potansiyel) çıktı.
- **Neden Oldu?** Tipik bir "Veri Şeması (Data Schema)" hatası (Yazılım Acemiliği). Kodun 7. adımında hesapladığımız güneş enerjisini `Yillik_Uretim_kWh` sütununa kaydettik. Ama 8. adımdaki HTML çizen kod, `Gunes_Uretimi_kWh` adlı (olmayan) eski bir sütun adını aradı. Bulamayınca herkesin değerini 0 sandı.
- **Profesyoneller Nasıl Çözer?** Veri ardışık düzenlerinde (Data Pipeline) sütun isimleri statik olmalıdır. Kodu düzelttik ve veriyi EPSG:32636 (Metre birimi) koordinat sistemine çekerek gerçek "Çatı Alanı (m²)" hesabını Tooltip'e ekledik. Böylece renkler (Yeşil-Sarı-Kırmızı) kusursuz çalıştı.

## 5. "Gerçek 3B Model" ile "CBS (GIS) Kutu Modeli" Arasındaki Fark
- **PyDeck HTML Haritamız (CBS Modeli):** Analitik bir gösterimdir. Literatürde buna **LOD1 (Detay Seviyesi 1) Blok Model** denir. Mühendislikte alan, hacim ve güneş paneli kapasitesi hesaplamak için binaların gerçek mimari girintileri çıkıntıları soyutlanıp "matematiksel kutulara" dönüştürülür. Bu bir hata değil, uluslararası bir standarttır.
- **WebODM (Gerçek 3B Model):** Binaların çatısını, kiremitlerini, pencerelerini gösteren milyonlarca üçgenden oluşan devasa yapıdır (LOD3 / Mesh). Senin `.bat` dosyasına tıklayarak açtığın, dönen, fotogerçekçi 163 MB'lık model budur.

---

> [!TIP]
> **Hoca Bunu Soracaktır:** "Neden binalarınız kutu gibi görünüyor?"
> **Cevabın:** "Hocam Güneş Enerjisi potansiyel hesabı ve çatı alanı analizi yapabilmek için binaları otomatik vektörize ederek LOD1 (Level of Detail 1) Kentsel Blok Modellemesine tabi tuttuk. Gerçek fotogrametrik 3B model (Mesh) görsel sunumumuzda mevcuttur, Python kodumuz ise kentsel analiz (CBS) kısmıdır."
