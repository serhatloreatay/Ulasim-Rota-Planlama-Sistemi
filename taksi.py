import math
from abc import ABC, abstractmethod


class UlasimAraci(ABC):
    """Ulaşım aracı için soyut temel sınıf"""
    
    @abstractmethod
    def mesafe_hesapla(self, baslangic_enlem: float, baslangic_boylam: float,
                       hedef_enlem: float, hedef_boylam: float) -> float:
        """İki nokta arasındaki mesafeyi hesapla (km)"""
        pass
    
    @abstractmethod
    def ucret_hesapla(self, mesafe: float) -> float:
        """Mesafeye göre ücret hesapla"""
        pass


class Taksi(UlasimAraci):
    """Taksi sınıfı"""
    
    def __init__(self, acilis_ucreti: float, km_basina_ucret: float):
        self._acilis_ucreti = acilis_ucreti
        self._km_basina_ucret = km_basina_ucret
    
    def mesafe_hesapla(self, baslangic_enlem: float, baslangic_boylam: float,
                       hedef_enlem: float, hedef_boylam: float) -> float:
        """
        Haversine formülü ile iki nokta arasındaki mesafeyi hesapla (km)
        """
        # Dünya yarıçapı (km)
        R = 6371.0
        
        # Dereceyi radyana çevir
        lat1_rad = math.radians(baslangic_enlem)
        lat2_rad = math.radians(hedef_enlem)
        delta_lat = math.radians(hedef_enlem - baslangic_enlem)
        delta_lon = math.radians(hedef_boylam - baslangic_boylam)
        
        # Haversine formülü
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        mesafe = R * c
        return mesafe
    
    def ucret_hesapla(self, mesafe: float) -> float:
        """
        Taksi ücreti hesapla: Açılış ücreti + (Mesafe × km başına ücret)
        """
        return self._acilis_ucreti + (mesafe * self._km_basina_ucret)
    
    @property
    def acilis_ucreti(self) -> float:
        return self._acilis_ucreti
    
    @property
    def km_basina_ucret(self) -> float:
        return self._km_basina_ucret

