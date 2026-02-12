from typing import List, Dict, Optional
from durak import Durak


class Hat:
    """Hat sınıfı - bir hat üzerindeki duraklar ve bağlantıları temsil eder"""
    
    def __init__(self, hat_id: str, hat_adi: str, tasima_tipi: str):
        self._hat_id = hat_id
        self._hat_adi = hat_adi
        self._tasima_tipi = tasima_tipi  # "bus" veya "tram"
        self._duraklar: List[str] = []  # Durak ID'leri sıralı liste
    
    @property
    def hat_id(self) -> str:
        return self._hat_id
    
    @property
    def hat_adi(self) -> str:
        return self._hat_adi
    
    @property
    def tasima_tipi(self) -> str:
        return self._tasima_tipi
    
    @property
    def duraklar(self) -> List[str]:
        return self._duraklar
    
    def durak_ekle(self, durak_id: str):
        """Hata durak ekle"""
        if durak_id not in self._duraklar:
            self._duraklar.append(durak_id)
    
    def __str__(self) -> str:
        return f"{self._hat_adi} ({self._tasima_tipi})"


class HatYoneticisi:
    """Hat yönetimi için yardımcı sınıf"""
    
    def __init__(self, duraklar: Dict[str, Durak]):
        self._duraklar = duraklar
        self._hatlar: Dict[str, Hat] = {}
        self._hatlari_olustur()
    
    def _hatlari_olustur(self):
        """Duraklardan hatları otomatik oluştur"""
        # Otobüs hatları
        otobus_hatlari = {}
        tramvay_hatlari = {}
        
        for durak_id, durak in self._duraklar.items():
            tasima_tipi = durak.tasima_tipi()
            
            # Her durak için bir hat oluştur (basit yaklaşım)
            # Gerçek uygulamada duraklar arası bağlantılara göre hatlar belirlenir
            if tasima_tipi == "otobüs":
                hat_id = f"hat_{durak_id}"
                if hat_id not in otobus_hatlari:
                    hat = Hat(hat_id, f"Otobüs Hattı - {durak.isim}", "bus")
                    otobus_hatlari[hat_id] = hat
                otobus_hatlari[hat_id].durak_ekle(durak_id)
            elif tasima_tipi == "tramvay":
                hat_id = f"hat_{durak_id}"
                if hat_id not in tramvay_hatlari:
                    hat = Hat(hat_id, f"Tramvay Hattı - {durak.isim}", "tram")
                    tramvay_hatlari[hat_id] = hat
                tramvay_hatlari[hat_id].durak_ekle(durak_id)
        
        self._hatlar.update(otobus_hatlari)
        self._hatlar.update(tramvay_hatlari)
    
    def durak_bilgisi_al(self, durak_id: str, hedef_durak_id: str) -> Optional[Dict]:
        """İki durak arasındaki bağlantı bilgisini getir"""
        durak = self._duraklar.get(durak_id)
        if not durak:
            return None
        
        for sonraki in durak.sonraki_duraklar:
            if sonraki["stopId"] == hedef_durak_id:
                return {
                    "mesafe": sonraki["mesafe"],
                    "sure": sonraki["sure"],
                    "ucret": sonraki["ucret"]
                }
        return None
    
    def aktarma_bilgisi_al(self, durak_id: str) -> Optional[Dict]:
        """Durağın aktarma bilgisini getir"""
        durak = self._duraklar.get(durak_id)
        if not durak:
            return None
        return durak.aktarma
    
    @property
    def hatlar(self) -> Dict[str, Hat]:
        return self._hatlar
    
    def durak_getir(self, durak_id: str) -> Optional[Durak]:
        """ID'ye göre durak getir"""
        return self._duraklar.get(durak_id)
    
    def tum_duraklar(self) -> Dict[str, Durak]:
        """Tüm durakları döndür"""
        return self._duraklar

