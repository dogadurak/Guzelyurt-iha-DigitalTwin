import cv2
import numpy as np
import os
import time

def process_alignment():
    print("--- 1. Görüntü Yöneltme (Tie Points) Gerçek Algoritması ---")
    data_dir = r"C:\Users\PC\Desktop\mügehoca_digitalphoto_3Bcitymodelling\GuzelyurtIHA_DATA\GuzelyurtIHA_DATA\img"
    
    # İki ardışık fotoğraf seçiyoruz
    img1_path = os.path.join(data_dir, "DSC07533.JPG")
    img2_path = os.path.join(data_dir, "DSC07534.JPG")
    
    if not os.path.exists(img1_path) or not os.path.exists(img2_path):
        print("Hata: Görüntüler bulunamadı.")
        return

    print("Görüntüler yükleniyor...")
    # Resmi yükle (Unicode path hatası için numpy çözümü)
    img1_array = np.fromfile(img1_path, np.uint8)
    img1 = cv2.imdecode(img1_array, cv2.IMREAD_COLOR)
    
    img2_array = np.fromfile(img2_path, np.uint8)
    img2 = cv2.imdecode(img2_array, cv2.IMREAD_COLOR)
    
    # Hızlı işlem için resmi küçültelim (6000x4000 piksellerde SIFT çok uzun sürer)
    scale = 0.25
    img1 = cv2.resize(img1, (0,0), fx=scale, fy=scale)
    img2 = cv2.resize(img2, (0,0), fx=scale, fy=scale)
    
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    print("SIFT (Özellik Çıkarımı) algoritması çalıştırılıyor...")
    start_time = time.time()
    
    # SIFT tanımlayıcı
    sift = cv2.SIFT_create(nfeatures=5000)
    
    kp1, des1 = sift.detectAndCompute(gray1, None)
    kp2, des2 = sift.detectAndCompute(gray2, None)
    
    print(f"Resim 1'de {len(kp1)} adet, Resim 2'de {len(kp2)} adet özellik (keypoint) bulundu.")

    # FLANN Matcher
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    
    print("FLANN ile noktalar eşleştiriliyor...")
    matches = flann.knnMatch(des1, des2, k=2)
    
    # Lowe's Ratio Test (Kalitesiz eşleşmeleri ele)
    good_matches = []
    pts1 = []
    pts2 = []
    
    for m, n in matches:
        if m.distance < 0.7 * n.distance:
            good_matches.append(m)
            pts2.append(kp2[m.trainIdx].pt)
            pts1.append(kp1[m.queryIdx].pt)
            
    print(f"Lowe Oran Testi sonrası kalan sağlam Tie Point (Bağlama Noktası): {len(good_matches)}")

    # RANSAC ile hatalı olanları (Outliers) temizle ve Fundamental Matrix bul
    if len(good_matches) > 10:
        pts1 = np.int32(pts1)
        pts2 = np.int32(pts2)
        
        # Fundamental Matrix hesapla
        F, mask = cv2.findFundamentalMat(pts1, pts2, cv2.FM_RANSAC, 3.0, 0.99)
        matchesMask = mask.ravel().tolist()
        
        valid_tie_points = sum(matchesMask)
        print(f"RANSAC ile Fundamental Matrix Hesaplandı. Geometrik olarak %100 Doğru Tie Point Sayısı: {valid_tie_points}")
        
        # Eşleşmeleri çiz (sadece RANSAC'tan geçenleri)
        draw_params = dict(matchColor=(0, 255, 0),
                           singlePointColor=None,
                           matchesMask=matchesMask,
                           flags=2)
        
        img3 = cv2.drawMatches(img1, kp1, img2, kp2, good_matches, None, **draw_params)
        
        out_path = r"C:\Users\PC\Desktop\mügehoca_digitalphoto_3Bcitymodelling\tie_points_result.jpg"
        cv2.imwrite(out_path, img3)
        print(f"Başarılı! Tie-Points görseli kaydedildi: {out_path}")
        print(f"Geçen süre: {round(time.time() - start_time, 2)} saniye")
    else:
        print("Yeterli eşleşme bulunamadı!")

if __name__ == "__main__":
    process_alignment()
