from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from durak import Durak
from konum import Konum
from taksi import Taksi
from mesafe_hesaplayici import MesafeHesaplayici
from hat import HatYoneticisi
from aktarma_indirimi import AktarmaIndirimYoneticisi
from taksi_zorunlulugu import TaksiZorunlulukYoneticisi


@dataclass
class RotaAdimi:
    """Rota adımı - her bir ulaşım segmentini temsil eder"""
    baslangic: str  # Başlangıç durak ID veya "konum"
    hedef: str  # Hedef durak ID veya "konum"
    ulasim_tipi: str  # "yurume", "taksi", "otobus", "tramvay", "aktarma"
    mesafe: float  # km
    sure: float  # dakika
    ucret: float  # TL
    aciklama: str = ""
    indirim_aciklama: Optional[str] = None  # Uygulanan indirim açıklaması
    orijinal_ucret: Optional[float] = None  # İndirim öncesi ücret


@dataclass
class Rota:
    """Tam rota bilgisi"""
    adimlar: List[RotaAdimi]
    toplam_mesafe: float
    toplam_sure: float
    toplam_ucret: float
    aktarma_sayisi: int
    
    def __str__(self) -> str:
        return f"Rota: {len(self.adimlar)} adım, {self.toplam_sure:.1f} dk, {self.toplam_ucret:.2f} TL"


class RotaHesaplayici:
    """Rota hesaplama sınıfı - en uygun rotayı bulur"""
    
    ESIK_MESAFE_KM = 3.0  # 3 km eşik değeri
    
    def __init__(self, hat_yoneticisi: HatYoneticisi, taksi: Taksi,
                 aktarma_indirim_yoneticisi: Optional[AktarmaIndirimYoneticisi] = None,
                 taksi_zorunluluk_yoneticisi: Optional[TaksiZorunlulukYoneticisi] = None):
        self._hat_yoneticisi = hat_yoneticisi
        self._taksi = taksi
        self._aktarma_indirim_yoneticisi = aktarma_indirim_yoneticisi or AktarmaIndirimYoneticisi()
        self._taksi_zorunluluk_yoneticisi = taksi_zorunluluk_yoneticisi or TaksiZorunlulukYoneticisi()
    
    def en_uygun_rota_bul(self, baslangic_konum: Konum, hedef_konum: Konum,
                         yolcu_tipi: Optional[str] = None) -> Optional[Rota]:
        """
        Başlangıç ve hedef konum arasında en uygun rotayı bul
        
        Args:
            baslangic_konum: Başlangıç konumu (enlem, boylam)
            hedef_konum: Hedef konum (enlem, boylam)
            yolcu_tipi: Yolcu tipi (indirim hesaplaması için)
        
        Returns:
            En uygun rota veya None
        """
        # En yakın durakları bul
        baslangic_durak_id, baslangic_mesafe = self._en_yakin_durak_bul(
            baslangic_konum.enlem, baslangic_konum.boylam
        )
        hedef_durak_id, hedef_mesafe = self._en_yakin_durak_bul(
            hedef_konum.enlem, hedef_konum.boylam
        )
        
        if not baslangic_durak_id or not hedef_durak_id:
            return None
        
        # Rota adımlarını oluştur
        adimlar: List[RotaAdimi] = []
        
        # 1. Başlangıç konumundan en yakın durağa
        baslangic_durak = self._hat_yoneticisi.durak_getir(baslangic_durak_id)
        taksi_gerekli, mesafe, kontrol_aciklama = self._taksi_zorunluluk_yoneticisi.taksi_gerekli_mi(
            baslangic_konum, baslangic_durak
        )
        
        if taksi_gerekli:
            # Taksi kullan (zorunlu)
            taksi_ucret = self._taksi.ucret_hesapla(mesafe)
            taksi_sure = mesafe * 2  # Yaklaşık 2 dk/km
            aciklama = f"Taksi ile {baslangic_durak_id} durağına (Zorunlu - {kontrol_aciklama})"
            adimlar.append(RotaAdimi(
                baslangic="konum",
                hedef=baslangic_durak_id,
                ulasim_tipi="taksi",
                mesafe=mesafe,
                sure=taksi_sure,
                ucret=taksi_ucret,
                aciklama=aciklama
            ))
        else:
            # Yürüyerek
            yurume_sure = mesafe * 12  # Yaklaşık 12 dk/km (yürüyüş)
            adimlar.append(RotaAdimi(
                baslangic="konum",
                hedef=baslangic_durak_id,
                ulasim_tipi="yurume",
                mesafe=mesafe,
                sure=yurume_sure,
                ucret=0.0,
                aciklama=f"Yürüyerek {baslangic_durak_id} durağına ({mesafe:.2f} km)"
            ))
        
        # 2. Duraklar arası toplu taşıma rotası
        toplu_tasima_rota = self._durak_arasi_rota_bul(
            baslangic_durak_id, hedef_durak_id
        )
        if toplu_tasima_rota:
            adimlar.extend(toplu_tasima_rota)
        else:
            # Direkt rota bulunamadı, taksi kullan
            durak_arasi_mesafe = MesafeHesaplayici.haversine_mesafe(
                self._hat_yoneticisi.durak_getir(baslangic_durak_id).enlem,
                self._hat_yoneticisi.durak_getir(baslangic_durak_id).boylam,
                self._hat_yoneticisi.durak_getir(hedef_durak_id).enlem,
                self._hat_yoneticisi.durak_getir(hedef_durak_id).boylam
            )
            taksi_ucret = self._taksi.ucret_hesapla(durak_arasi_mesafe)
            taksi_sure = durak_arasi_mesafe * 2
            adimlar.append(RotaAdimi(
                baslangic=baslangic_durak_id,
                hedef=hedef_durak_id,
                ulasim_tipi="taksi",
                mesafe=durak_arasi_mesafe,
                sure=taksi_sure,
                ucret=taksi_ucret,
                aciklama=f"Taksi ile {baslangic_durak_id} -> {hedef_durak_id}"
            ))
        
        # 3. Hedef duraktan hedef konuma
        hedef_durak = self._hat_yoneticisi.durak_getir(hedef_durak_id)
        taksi_gerekli, mesafe, kontrol_aciklama = self._taksi_zorunluluk_yoneticisi.taksi_gerekli_mi(
            hedef_konum, hedef_durak
        )
        
        if taksi_gerekli:
            # Taksi kullan (zorunlu)
            taksi_ucret = self._taksi.ucret_hesapla(mesafe)
            taksi_sure = mesafe * 2
            aciklama = f"Taksi ile hedef konuma (Zorunlu - {kontrol_aciklama})"
            adimlar.append(RotaAdimi(
                baslangic=hedef_durak_id,
                hedef="konum",
                ulasim_tipi="taksi",
                mesafe=mesafe,
                sure=taksi_sure,
                ucret=taksi_ucret,
                aciklama=aciklama
            ))
        else:
            # Yürüyerek
            yurume_sure = mesafe * 12
            adimlar.append(RotaAdimi(
                baslangic=hedef_durak_id,
                hedef="konum",
                ulasim_tipi="yurume",
                mesafe=mesafe,
                sure=yurume_sure,
                ucret=0.0,
                aciklama=f"Yürüyerek hedef konuma ({mesafe:.2f} km)"
            ))
        
        # Toplam değerleri hesapla
        toplam_mesafe = sum(adim.mesafe for adim in adimlar)
        toplam_sure = sum(adim.sure for adim in adimlar)
        toplam_ucret = sum(adim.ucret for adim in adimlar)
        aktarma_sayisi = sum(1 for adim in adimlar if adim.ulasim_tipi == "aktarma")
        
        # Yolcu indirimi uygula (eğer belirtilmişse)
        if yolcu_tipi:
            indirim_orani = self._indirim_orani_al(yolcu_tipi)
            toplam_ucret = toplam_ucret * (1 - indirim_orani)
        
        return Rota(
            adimlar=adimlar,
            toplam_mesafe=toplam_mesafe,
            toplam_sure=toplam_sure,
            toplam_ucret=toplam_ucret,
            aktarma_sayisi=aktarma_sayisi
        )
    
    def _en_yakin_durak_bul(self, enlem: float, boylam: float) -> Tuple[Optional[str], float]:
        """En yakın durağı bul"""
        en_yakin_id = None
        en_kisa_mesafe = float('inf')
        
        # Tüm durakları kontrol et
        for durak_id, durak in self._hat_yoneticisi.tum_duraklar().items():
            mesafe = MesafeHesaplayici.haversine_mesafe(
                enlem, boylam,
                durak.enlem, durak.boylam
            )
            if mesafe < en_kisa_mesafe:
                en_kisa_mesafe = mesafe
                en_yakin_id = durak_id
        
        return en_yakin_id, en_kisa_mesafe
    
    def _durak_arasi_rota_bul(self, baslangic_durak_id: str, 
                              hedef_durak_id: str) -> Optional[List[RotaAdimi]]:
        """
        İki durak arasındaki en kısa rotayı bul (Dijkstra benzeri algoritma)
        """
        # Basit BFS/DFS yaklaşımı
        from collections import deque
        
        ziyaret_edildi = set()
        kuyruk = deque([(baslangic_durak_id, [])])
        
        while kuyruk:
            mevcut_durak_id, yol = kuyruk.popleft()
            
            if mevcut_durak_id == hedef_durak_id:
                # Rota bulundu, adımları oluştur
                return self._yolu_adimlara_cevir(yol)
            
            if mevcut_durak_id in ziyaret_edildi:
                continue
            
            ziyaret_edildi.add(mevcut_durak_id)
            mevcut_durak = self._hat_yoneticisi.durak_getir(mevcut_durak_id)
            
            if not mevcut_durak:
                continue
            
            # Sonraki duraklara git
            for sonraki in mevcut_durak.sonraki_duraklar:
                sonraki_id = sonraki["stopId"]
                if sonraki_id not in ziyaret_edildi:
                    yeni_yol = yol + [(mevcut_durak_id, sonraki_id, sonraki)]
                    kuyruk.append((sonraki_id, yeni_yol))
            
            # Aktarma yap
            if mevcut_durak.aktarma:
                aktarma_id = mevcut_durak.aktarma["transferStopId"]
                if aktarma_id not in ziyaret_edildi:
                    # Aktarma bilgisini tuple olarak ekle
                    aktarma_bilgisi = {
                        "transferSure": mevcut_durak.aktarma["transferSure"],
                        "transferUcret": mevcut_durak.aktarma["transferUcret"]
                    }
                    yeni_yol = yol + [(mevcut_durak_id, aktarma_id, aktarma_bilgisi, True)]
                    kuyruk.append((aktarma_id, yeni_yol))
        
        return None
    
    def _yolu_adimlara_cevir(self, yol: List[Tuple]) -> List[RotaAdimi]:
        """Yol listesini RotaAdimi listesine çevir"""
        adimlar = []
        onceki_tasima_tipi = None  # Aktarma indirimi için önceki taşıma tipini takip et
        
        for adim in yol:
            if len(adim) == 4 and adim[3]:  # Aktarma
                baslangic_id, hedef_id, aktarma_bilgisi, _ = adim
                if aktarma_bilgisi:
                    # Başlangıç ve hedef durakların taşıma tiplerini belirle
                    baslangic_durak = self._hat_yoneticisi.durak_getir(baslangic_id)
                    hedef_durak = self._hat_yoneticisi.durak_getir(hedef_id)
                    
                    baslangic_tipi = baslangic_durak.tasima_tipi() if baslangic_durak else None
                    hedef_tipi = hedef_durak.tasima_tipi() if hedef_durak else None
                    
                    orijinal_ucret = aktarma_bilgisi["transferUcret"]
                    
                    # Aktarma indirimi uygula
                    indirimli_ucret, indirim_aciklama = self._aktarma_indirim_yoneticisi.indirim_hesapla(
                        baslangic_tipi or "", hedef_tipi or "", orijinal_ucret
                    )
                    
                    # Açıklama oluştur
                    aciklama = f"Aktarma: {baslangic_id} -> {hedef_id}"
                    if indirim_aciklama:
                        aciklama += f" ({indirim_aciklama})"
                    
                    adimlar.append(RotaAdimi(
                        baslangic=baslangic_id,
                        hedef=hedef_id,
                        ulasim_tipi="aktarma",
                        mesafe=0,
                        sure=aktarma_bilgisi["transferSure"],
                        ucret=indirimli_ucret,
                        aciklama=aciklama,
                        indirim_aciklama=indirim_aciklama,
                        orijinal_ucret=orijinal_ucret
                    ))
                    
                    onceki_tasima_tipi = hedef_tipi
            else:  # Normal durak geçişi
                baslangic_id, hedef_id, bilgi = adim
                tasima_tipi = "otobus" if "bus" in baslangic_id else "tramvay"
                adimlar.append(RotaAdimi(
                    baslangic=baslangic_id,
                    hedef=hedef_id,
                    ulasim_tipi=tasima_tipi,
                    mesafe=bilgi["mesafe"],
                    sure=bilgi["sure"],
                    ucret=bilgi["ucret"],
                    aciklama=f"{tasima_tipi.capitalize()}: {baslangic_id} -> {hedef_id}"
                ))
                onceki_tasima_tipi = tasima_tipi
        
        return adimlar
    
    def _indirim_orani_al(self, yolcu_tipi: str) -> float:
        """Yolcu tipine göre indirim oranı"""
        indirimler = {
            "ogrenci": 0.3,
            "ogretmen": 0.25,
            "yasli": 0.35,
            "genel": 0.0
        }
        return indirimler.get(yolcu_tipi.lower(), 0.0)

