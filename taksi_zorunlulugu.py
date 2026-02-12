from abc import ABC, abstractmethod
from typing import Optional, Tuple
from konum import Konum
from durak import Durak
from mesafe_hesaplayici import MesafeHesaplayici


class TaksiZorunlulukKontrolu(ABC):
    """Taksi zorunluluğu kontrolü için soyut temel sınıf"""
    
    @abstractmethod
    def taksi_gerekli_mi(self, konum: Konum, durak: Durak) -> Tuple[bool, float]:
        """
        Taksi kullanımının gerekli olup olmadığını kontrol et
        
        Args:
            konum: Kullanıcının konumu
            durak: En yakın durak
        
        Returns:
            (taksi_gerekli, mesafe_km)
        """
        pass
    
    @abstractmethod
    def kontrol_tipi(self) -> str:
        """Kontrol tipini döndür"""
        pass


class MesafeBazliTaksiKontrolu(TaksiZorunlulukKontrolu):
    """Mesafe bazlı taksi zorunluluğu kontrolü"""
    
    def __init__(self, esik_mesafe_km: float = 3.0):
        """
        Args:
            esik_mesafe_km: Eşik mesafe (km) - bu mesafeden fazla ise taksi zorunlu
        """
        self._esik_mesafe_km = esik_mesafe_km
    
    def taksi_gerekli_mi(self, konum: Konum, durak: Durak) -> Tuple[bool, float]:
        """Mesafe bazlı kontrol"""
        mesafe = MesafeHesaplayici.haversine_mesafe(
            konum.enlem, konum.boylam,
            durak.enlem, durak.boylam
        )
        return mesafe > self._esik_mesafe_km, mesafe
    
    def kontrol_tipi(self) -> str:
        return "Mesafe Bazlı Kontrol"
    
    @property
    def esik_mesafe_km(self) -> float:
        return self._esik_mesafe_km


class SureBazliTaksiKontrolu(TaksiZorunlulukKontrolu):
    """Süre bazlı taksi zorunluluğu kontrolü (yürüyüş süresi çok uzunsa)"""
    
    def __init__(self, maksimum_yurume_suresi_dk: float = 30.0):
        """
        Args:
            maksimum_yurume_suresi_dk: Maksimum yürüyüş süresi (dakika)
        """
        self._maksimum_yurume_suresi_dk = maksimum_yurume_suresi_dk
        self._yurume_hizi_kmh = 5.0  # Ortalama yürüyüş hızı: 5 km/saat
    
    def taksi_gerekli_mi(self, konum: Konum, durak: Durak) -> Tuple[bool, float]:
        """Süre bazlı kontrol"""
        mesafe = MesafeHesaplayici.haversine_mesafe(
            konum.enlem, konum.boylam,
            durak.enlem, durak.boylam
        )
        
        # Yürüyüş süresini hesapla (dakika)
        yurume_suresi = (mesafe / self._yurume_hizi_kmh) * 60
        
        taksi_gerekli = yurume_suresi > self._maksimum_yurume_suresi_dk
        return taksi_gerekli, mesafe
    
    def kontrol_tipi(self) -> str:
        return "Süre Bazlı Kontrol"
    
    @property
    def maksimum_yurume_suresi_dk(self) -> float:
        return self._maksimum_yurume_suresi_dk


class TaksiZorunlulukYoneticisi:
    """Taksi zorunluluğu kontrollerini yöneten sınıf"""
    
    def __init__(self, kontrol_stratejileri: Optional[list] = None):
        """
        Args:
            kontrol_stratejileri: Kontrol stratejileri listesi (varsayılan: mesafe bazlı)
        """
        if kontrol_stratejileri is None:
            # Varsayılan: Mesafe bazlı kontrol (3 km eşik)
            self._kontroller = [MesafeBazliTaksiKontrolu(esik_mesafe_km=3.0)]
        else:
            self._kontroller = kontrol_stratejileri
    
    def taksi_gerekli_mi(self, konum: Konum, durak: Durak) -> Tuple[bool, float, Optional[str]]:
        """
        Tüm kontrolleri uygula - herhangi biri taksi gerektiriyorsa True döndür
        
        Returns:
            (taksi_gerekli, mesafe_km, kontrol_aciklama)
        """
        for kontrol in self._kontroller:
            taksi_gerekli, mesafe = kontrol.taksi_gerekli_mi(konum, durak)
            if taksi_gerekli:
                return True, mesafe, kontrol.kontrol_tipi()
        
        # Hiçbir kontrol taksi gerektirmiyorsa
        if self._kontroller:
            _, mesafe = self._kontroller[0].taksi_gerekli_mi(konum, durak)
            return False, mesafe, None
        
        return False, 0.0, None
    
    def kontrol_ekle(self, kontrol: TaksiZorunlulukKontrolu):
        """Yeni bir kontrol stratejisi ekle"""
        self._kontroller.append(kontrol)
    
    @property
    def kontroller(self) -> list:
        return self._kontroller

