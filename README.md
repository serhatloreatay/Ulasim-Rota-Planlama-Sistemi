# Ulasim-Rota-Planlama-Sistemi

Bu proje, şehir içi ulaşımda **duraklar**, **hatlar** ve **taksi zorunluluğu** gibi koşulları dikkate alarak yolcular için en uygun rotayı hesaplayan bir **Python tabanlı rota planlama sistemidir**.

Yolcu; başlangıç ve varış konumunu seçtiğinde sistem:
- Müsait hatları ve durakları inceler,
- Gerekirse aktarma ve indirimleri uygular,
- Taksi zorunlu bölgeleri hesaba katar,
- Toplam mesafe ve/veya maliyete göre **en uygun rotayı** bulmaya çalışır.

---

## Kurulum

1. Bu projeyi klonla veya indir:
   ```bash
   git clone https://github.com/serhatloreatay/Ulasim-Rota-Planlama-Sistemi.git
   cd Ulasim-Rota-Planlama-Sistemi
   ```

2. Python 3 yüklü olduğundan emin ol:
   ```bash
   python --version
   ```
   veya
   ```bash
   py --version
   ```

Ek bir kütüphane gerekmiyorsa, standart Python kurulumu yeterlidir.

---

## Çalıştırma

Ana arayüzü başlatmak için:

```bash
python arayuz.py
```

Windows’ta Python komutu farklıysa:

```bash
py arayuz.py
```

Program açıldıktan sonra:
- Başlangıç ve varış durak/konum bilgilerini gir,
- Gerekli seçenekleri işaretle,
- Sistem sana uygun rota ve ilgili bilgileri (mesafe, ücret vs.) gösterir.

---

## Proje Yapısı

Projede yer alan temel Python dosyaları:

- `arayuz.py`  
  Uygulamanın giriş noktası ve kullanıcıyla etkileşimi yöneten ana arayüz.

- `hat.py`  
  Ulaşım hatlarını (örneğin otobüs hattı vb.) temsil eder; hat numarası, durak listesi gibi bilgiler içerir.

- `durak.py`  
  Durakları modelleyen sınıfları/fonksiyonları barındırır.

- `konum.py`  
  Koordinat veya konum bilgilerinin tutulduğu ve işlendiği yapı.

- `rota.py`  
  Hesaplanan rotaların yapısını ve özelliklerini tanımlar.

- `en_uygun_rota_secici.py`  
  Farklı rota seçeneklerini değerlendirip **en uygun rotayı** seçen algoritmalar.

- `rota_secenekleri.py`  
  Kullanıcıya sunulacak alternatif rota kombinasyonlarını üretir.

- `mesafe_hesaplayici.py`  
  İki konum arasındaki mesafeyi (ve varsa süre vb.) hesaplar.

- `aktarma_indirimi.py`  
  Aktarma yapılan hatlar için uygulanacak indirim kurallarını içerir.

- `taksi.py` ve `taksi_zorunlulugu.py`  
  Taksi ile gidilmesi gereken bölümleri ve taksi ücretlendirmesini yönetir.

- `yolcu.py`  
  Yolcunun cüzdanı, bakiyesi ve tercihleri gibi bilgileri temsil eder.

- `cuzdan.py`, `odeme.py`, `veri_yukleyici.py`  
  Ödeme işlemleri, bakiye yönetimi ve sistem verilerinin yüklenmesinden sorumlu yardımcı modüller.

---

## Lisans

Bu proje için ayrı bir lisans belirtilmemiştir. Eğitim ve proje amaçlı kullanılabilir.
