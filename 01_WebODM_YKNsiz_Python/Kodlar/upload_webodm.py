import os
import glob
import requests
import sys
import json
from requests_toolbelt.multipart.encoder import MultipartEncoder

URL = "http://localhost:8080"
USERNAME = "ai_agent"
PASSWORD = "aipassword123"

print("Giriş yapılıyor...")
resp = requests.post(f"{URL}/api/token-auth/", data={"username": USERNAME, "password": PASSWORD})
if resp.status_code != 200:
    print("Giriş başarısız:", resp.text)
    sys.exit(1)
token = resp.json()["token"]
headers = {"Authorization": f"JWT {token}"}

print("İşlemci düğümü (Node) aranıyor...")
resp = requests.get(f"{URL}/api/nodes/", headers=headers)
nodes = resp.json()
if not nodes:
    print("Bağlı işlemci düğümü bulunamadı!")
    sys.exit(1)
node_id = nodes[0]["id"]
print(f"Node bulundu (ID: {node_id})")

print("Guzelyurt_IHA projesi oluşturuluyor...")
resp = requests.post(f"{URL}/api/projects/", headers=headers, json={"name": "Guzelyurt_IHA"})
if resp.status_code in (200, 201):
    project_id = resp.json()["id"]
    print(f"Proje oluşturuldu (ID: {project_id})")
else:
    # Eğer proje zaten varsa onu bulalım
    resp = requests.get(f"{URL}/api/projects/", headers=headers)
    projects = resp.json()
    project_id = None
    for p in projects:
        if p["name"] == "Guzelyurt_IHA":
            project_id = p["id"]
            break
    if project_id:
        print(f"Mevcut proje bulundu (ID: {project_id})")
    else:
        print("Proje oluşturulamadı.")
        sys.exit(1)

image_dir = r"c:\Users\PC\Desktop\mügehoca_digitalphoto_3Bcitymodelling\GuzelyurtIHA_DATA\GuzelyurtIHA_DATA"
gcp_file = os.path.join(image_dir, "NN_Y_X_Z.txt")

images = glob.glob(os.path.join(image_dir, "*.JPG"))
if not images:
    images = glob.glob(os.path.join(image_dir, "*.jpg"))
print(f"Toplam {len(images)} fotoğraf ve GCP dosyası bulundu.")

print("Dosyalar WebODM'e yükleniyor... Bu işlem biraz sürebilir.")
tuple_fields = []
tuple_fields.append(('options', json.dumps([{"name": "name", "value": "Otomatik Islem"}])) )

for img in images:
    tuple_fields.append(('images', (os.path.basename(img), open(img, 'rb'), 'image/jpeg')))

tuple_fields.append(('images', ('NN_Y_X_Z.txt', open(gcp_file, 'rb'), 'text/plain')))

m = MultipartEncoder(fields=tuple_fields)
headers['Content-Type'] = m.content_type

task_url = f"{URL}/api/projects/{project_id}/tasks/"
print(f"POST isteği gönderiliyor: {task_url}")
resp = requests.post(task_url, headers=headers, data=m)

if resp.status_code in (200, 201):
    print("İşlem başarıyla başlatıldı!")
    print(resp.json())
else:
    print("Hata:", resp.status_code)
    print(resp.text)
