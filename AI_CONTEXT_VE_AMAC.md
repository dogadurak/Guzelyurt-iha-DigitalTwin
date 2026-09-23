# 🤖 YENİ AI AJANLARI İÇİN PROJE BAĞLAMI VE AMAÇ BİLDİRGESİ

Merhaba meslektaşım (Diğer AI veya IDE Asistanı)! Bu belge, projeye sonradan dahil olduğunda projenin amacını, mimarisini ve şu ana kadar yapılanları eksiksiz anlaman için yazılmıştır.

## 🎯 Projenin Nihai Amacı
Bu proje, Aksaray / Güzelyurt bölgesinden İHA (Drone) ile toplanan hava fotoğraflarının işlenerek **3 Boyutlu Şehir Modelleri** ve **Güneş Enerjisi Potansiyel Haritaları** üretilmesini kapsayan, "Profesyonel Uzaktan Algılama ve Fotogrametri Uzmanı" perspektifiyle yürütülen **akademik/kıyaslamalı** bir çalışmadır.

Temel vizyonumuz, aynı İHA verisini **3 Farklı Senaryo/Sistem** ile işleyip sonuçlarını (hata raporları, model kalitesi, üretim süreçleri) birbiriyle kıyaslamaktır:

1. **01_WebODM_YKNsiz_Python (TAMAMLANDI)**: Yer Kontrol Noktası (GCP) kullanılmadan, fotoğraflardaki EXIF GPS verisiyle açık kaynaklı WebODM'de işlenen, ardından Python ile (OpenCV, PyDeck) 3B modellere dönüştürülen faz.
2. **02_WebODM_YKNli_Python (SIRADAKİ FAZ)**: Aynı veri setinin bu kez YKN (GCP) noktaları ile WebODM'de işlenmesi, YKN'siz modelle hata/doğruluk analizlerinin kıyaslanması ve tekrar 3B modellenmesi.
3. **03_Agisoft_Metashape (GELECEK FAZ)**: Sektör standardı olan Agisoft Metashape yazılımında YKN'li üretimin yapılması ve açık kaynak (WebODM) ile ticari (Agisoft) sistemlerin kalite/süreç kıyaslamasının akademik düzeyde yapılması.

---

## 📂 Klasör ve Monorepo Mimarisi
Tüm veriler Github'a gönderileceği için her şey modüler ve birbirinden yalıtılmış tutulmaktadır. 

```text
mügehoca_digitalphoto_3Bcitymodelling/
│
├── 01_WebODM_YKNsiz_Python/      # (GCP olmadan üretilen model ve Python kodları)
│   ├── Kodlar/                   # step1_align.py ... step8_3d_city_model.py
│   ├── Raporlar/                 # kalite_raporu_analizi.md, proje_raporu_fotogrametri.md
│   └── Sonuclar/                 # 3B Şehir Modeli HTML'i ve GeoJSON çıktısı
│
├── 02_WebODM_YKNli_Python/       # (YKN verisi entegre edildikten sonraki süreç)
│
└── 03_Agisoft_Metashape/         # (Ticari yazılım kıyaslama süreci)
```

---

## 🛠️ Faz 1'de Neler Yaptık ve Hangi Metodolojileri Kullandık?
Şu ana kadar `01_WebODM_YKNsiz_Python` klasöründe yapılanlar:

1. **Fotogrametrik Üretim**: 166 fotoğraf WebODM'de işlendi, DSM ve Ortofoto elde edildi.
2. **Raporlama Standardı**: Raporlar basit bir metin yerine, fotogrametri terminolojisine uygun (GSD, RMS varyansları, reprojection error, inlier matching vb.) akademik bir dille yazıldı. *(Örn: "%98.9 başarı" gibi yanlış tabirler yerine "nokta rekonstrüksiyon oranı" gibi terimler kullanıldı).*
3. **Zorluk - Bina Tespiti**: Başlangıçta binaları DSM üzerinden tespit etmek için harici sunucular (OSMNX/Overpass API) denendi ancak **Ağ kısıtlamaları (HTTP 406 Not Acceptable / Timeout)** nedeniyle sunucudan veri alınamadı.
4. **Çözüm - Yapay Görme (Computer Vision)**: İnternet bağımlılığını kırmak için **OpenCV** kullanılarak tamamen lokal çalışan bir algoritma yazıldı (`step7_vectorize.py`). 
   * Devasa DSM (25829 x 20021 piksel) bellek (RAM) tasarrufu için Rasterio üzerinden düşük çözünürlükte `out_shape` argümanıyla okundu.
   * `cv2.morphologyEx(cv2.MORPH_OPEN)` ile Sayısal Arazi Modeli (DTM) hesaplanıp ağaçlar/arabalar silindi.
   * `cv2.findContours` ile binaların siluetleri (11 adet) bulundu, `rasterstats (zonal_stats)` ile her binanın minimum ve ortalama yüksekliği tespit edilip gerçek net 3B hacimleri hesaplandı.
5. **Görselleştirme**: Çatı alanlarının %70'ine güneş paneli kurulabileceği varsayımıyla (KWp ve Yıllık Üretim kWh) kapasiteler hesaplandı. `PyDeck` kullanılarak binaların kapasitesine göre renklendirildiği, fare ile sağ-sol eğilebilen `Guzelyurt_3B_Sehir_Modeli.html` etkileşimli haritası üretildi.

---

## 🚀 Senin (Yeni AI) Mevcut Görevin Ne Olacak?
Kullanıcı seninle yeni bir seansta bu klasörü açtığında büyük ihtimalle **02_WebODM_YKNli_Python** aşamasına geçmiş veya **Agisoft** çıktılarını değerlendiriyor olacaktır.

* **DİKKAT 1**: Kullanıcı senden kod yazmanı istediğinde (özellikle DSM, Ortofoto gibi 1-2 GB'lık TIFF dosyaları işlenirken) bellek yönetimine çok dikkat et. Asla tüm diziyi RAM'e doğrudan `src.read(1)` ile sokma; `scale` kullan veya blok/pencere bazlı (windowed) okuma yap.
* **DİKKAT 2**: İnternet tabanlı API'ler (Overpass vb.) güvenlik duvarına takılmaktadır. Olabildiğince lokal algoritmalar (OpenCV, skimage, GDAL vb.) kullan.
* **DİKKAT 3**: Herhangi bir rapor veya metin hazırlarken "pazarlama" dili değil, fotogrametrik ve mühendislik literatürüne uygun (**akademik**) bir dil kullan.

Kolay gelsin!
