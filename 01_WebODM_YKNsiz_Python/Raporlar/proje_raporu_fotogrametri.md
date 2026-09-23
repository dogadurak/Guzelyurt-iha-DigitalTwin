# Güzelyurt İHA Verileri ile 3B Şehir Modelleme ve Güneş Enerjisi Potansiyeli Analizi
## Proje Süreç Raporu

Bu proje kapsamında, İnsansız Hava Aracı (İHA) ile toplanan 332 adet hava fotoğrafı kullanılarak Güzelyurt bölgesine ait yüksek çözünürlüklü 3 Boyutlu Şehir Modeli üretilmiş; ardından elde edilen sayısal harita verileri üzerinden otomatik bina tespiti ve güneş enerjisi üretim potansiyeli analizi gerçekleştirilmiştir. 

Aşağıda projenin üretim aşamaları ve elde edilen verilerin literatürdeki/teknik anlamları detaylandırılmıştır.

---

### 1. Fotogrametrik Üretim Aşamaları (WebODM İş Akışı)

Projede verilerin işlenmesi için açık kaynaklı ve gelişmiş bir fotogrametri motoru olan WebODM kullanılmıştır. İşlem adımları şu şekildedir:

*   **Özellik Çıkarımı ve Görüntü Yöneltme (Feature Extraction & Alignment - SIFT):** 
    İHA'nın farklı açılardan çektiği her bir fotoğraf bilgisayarlı görü algoritmaları (SIFT) ile taranarak binlerce karakteristik nokta (Keypoint) tespit edilmiştir. İki veya daha fazla fotoğrafta ortak olan noktalar eşleştirilerek "Bağlama Noktaları (Tie Points)" bulunmuş ve kameranın havadaki üç boyutlu konumu ile açısı (Dış Yöneltme Parametreleri) geriye dönük hesaplanmıştır. Bu aşamada "Seyrek Nokta Bulutu (Sparse Point Cloud)" elde edilmiştir.
*   **Yoğun Nokta Bulutu Üretimi (Multi-View Stereo - Dense Point Cloud):**
    Kameraların konumları kesinleştikten sonra, derinlik haritaları (depth maps) çıkartılarak fotoğraflardaki her bir pikselin 3 boyutlu uzaydaki (X, Y, Z) koordinatları hesaplanmıştır. Projemizde yaklaşık 40 milyon noktadan oluşan, arazinin ve yapıların milimetrik bir 3B kopyası olan Yoğun Nokta Bulutu üretilmiştir.
*   **3B Ağ Model (Mesh) ve Doku (Texture) Kaplama:**
    Yoğun nokta bulutundaki dağınık noktalar, Delaunay üçgenlemesi gibi algoritmalarla birbirine bağlanarak kesintisiz bir yüzey modeli (Mesh) oluşturulmuştur. Daha sonra orijinal 2B drone fotoğrafları bu yüzeyin üzerine bir "doku (texture)" olarak kaplanarak fotogerçekçi 3B şehir modeli elde edilmiştir.
*   **Sayısal Yüzey Modeli (DSM - Digital Surface Model) Üretimi:**
    Oluşturulan 3B nokta bulutu ve yüzey modeli üzerinden bir enterpolasyon yapılarak arazinin üstten görünümü yükseklik verisine dönüştürülmüştür. Bu model, binalar ve ağaçlar dahil yeryüzündeki tüm objelerin tepe noktalarının deniz seviyesinden yüksekliğini gösterir.
*   **Ortofoto (Orthophoto) Üretimi:**
    Merkezi perspektiften kaynaklanan fotoğrafik bozulmalar (rölyef kayması vb.) DSM kullanılarak düzeltilmiştir. Böylece her pikselin tam dik açıdan (nadir) bakıldığı, üzerinde alan ve mesafe ölçümü yapılabilen metrik ve yüksek çözünürlüklü 2 Boyutlu Ortofoto Harita oluşturulmuştur.

---

### 2. Üretilen Dosyaların Anlamları (WebODM Çıktıları)

WebODM tarafından üretilen `WebODM_Tum_Sonuclar.zip` paketi ve klasörlerindeki ana verilerin anlamları şöyledir:

*   **`odm_orthophoto.tif` (Ortofoto Harita):**
    Koordinatlı (Georeferenced) ve metrik olarak düzeltilmiş havadan haritadır. Herhangi bir CBS (GIS) yazılımında açıldığında, dünya üzerindeki gerçek konumuna oturur. Üzerinden alan, çevre hesaplamaları ve sayısallaştırma (digitizing) işlemleri yapılabilir.
*   **`dsm.tif` (Sayısal Yüzey Modeli - DSM):**
    Piksel değerleri (renkler) yerine, her pikselinde Z (Yükseklik) değerini metre cinsinden tutan raster veridir. Analiz aşamasında binaların yüksekliklerini bulmak için kullanılan en kritik altlıktır.
*   **`odm_texturing` Klasörü (.obj / .ply):**
    Fotogerçekçi 3B modellerin bulunduğu klasördür. Şehrin doku kaplanmış bu 3B modeli; Blender, MeshLab veya Unity/Unreal Engine gibi oyun motorlarında görselleştirme ve simülasyon amacıyla kullanılabilir.
*   **`odm_georeferencing` Klasörü (.las / .laz):**
    Gerçek dünya koordinatlarına (WGS84 UTM vb.) oturtulmuş nokta bulutlarıdır. Profesyonel haritacılık programlarında lazer tarama (LiDAR) verisi gibi analiz edilebilir, kesit alınabilir.
*   **`odm_report/report.pdf` (Uçuş ve Kalite Raporu):**
    Projenin ne kadar hassas olduğunu, hataların RMS değerlerini, ortalama Yer Örnekleme Aralığını (GSD - Ground Sample Distance) ve örtüşme (overlap) oranlarını gösteren akademik/resmi doğruluk raporudur.

---

### 3. Vektörizasyon ve Analiz Süreci (Python ile Otomasyon)

Fotogrametrik üretimler bittikten sonra, hiçbir manuel çizim yapmadan **Özel Python Algoritmaları** ile aşağıdaki CBS işlemleri yürütülmüştür:

1.  **Görüntü İşleme ve Bina Tespiti (Digitizing):** 
    Yazdığımız Python kodları (OpenCV, Rasterio), Yükseklik Modeli (DSM) verisini inceleyerek, zemin kotu üzerindeki (belirli bir metrenin üstündeki) ani yükseklik sıçramalarını yakalamış ve "Bina Çatı Ayak İzlerini" otomatik olarak poligon (vektör) formatında çıkartmıştır.
2.  **Zonal Statistics ile Yükseklik Çıkarımı:**
    Otomatik bulunan bina poligonları, DSM üzerine bindirilmiştir. Her bir poligonun içine düşen piksellerin Z (Yükseklik) ortalamaları alınarak binaların net yükseklikleri (nDSM) hesaplanmıştır.
3.  **Güneş Enerjisi (Solar) Potansiyeli Modellemesi:**
    Her binanın çatı alanı (m²) hesaplanmış, bacalar/kenar payları çıkarılarak "kullanılabilir alan" bulunmuştur. Güzelyurt bölgesinin Yıllık Ortalama Güneşlenme Süresi ve standart bir güneş paneli verimliliği hesaba katılarak her bir çatının yıllık **kWh cinsinden enerji üretim potansiyeli** formülize edilmiştir.
4.  **GeoJSON Çıktısı (`Binalar_Gunes_Potansiyeli.geojson`):**
    Tüm coğrafi özellikler ve hesaplanan nitelikler (Alan, Yükseklik, Panel Sayısı, Yıllık Enerji) zengin bir mekansal veri tabanı formatı olan GeoJSON olarak kaydedilmiştir. Bu veri, web haritalarında veya QGIS'te anında görselleştirilip sorgulanabilir durumdadır.
