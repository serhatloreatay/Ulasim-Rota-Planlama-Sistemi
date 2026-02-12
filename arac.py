from abc import ABC, abstractmethod
from typing import Optional


class Arac(ABC):
    """Araç için soyut temel sınıf"""
    
    def __init__(self, arac_id: str, isim: str):
        self._arac_id = arac_id
        self._isim = isim
    
    @property
    def arac_id(self) -> str:
        return self._arac_id
    
    @property
    def isim(self) -> str:
        return self._isim
    
    @abstractmethod
    def arac_tipi(self) -> str:
        """Araç tipini döndür (otobüs, tramvay, taksi)"""
        pass
    
    @abstractmethod
    def ucret_hesapla(self, mesafe: Optional[float] = None, 
                     durak_bilgisi: Optional[dict] = None) -> float:
        """Ücret hesapla - her araç tipi kendi hesaplama mantığını kullanır"""
        pass
    
    def __str__(self) -> str:
        return f"{self._isim} ({self.arac_tipi()})"


class Otobus(Arac):
    """Otobüs araç sınıfı"""
    
    def __init__(self, arac_id: str = "otobus_1", isim: str = "Otobüs"):
        super().__init__(arac_id, isim)
    
    def arac_tipi(self) -> str:
        return "otobüs"
    
    def ucret_hesapla(self, mesafe: Optional[float] = None, 
                     durak_bilgisi: Optional[dict] = None) -> float:
        """Otobüs ücreti durak bilgisinden hesaplanır"""
        if durak_bilgisi and "ucret" in durak_bilgisi:
            return durak_bilgisi["ucret"]
        return 0.0


class Tramvay(Arac):
    """Tramvay araç sınıfı"""
    
    def __init__(self, arac_id: str = "tramvay_1", isim: str = "Tramvay"):
        super().__init__(arac_id, isim)
    
    def arac_tipi(self) -> str:
        return "tramvay"
    
    def ucret_hesapla(self, mesafe: Optional[float] = None, 
                     durak_bilgisi: Optional[dict] = None) -> float:
        """Tramvay ücreti durak bilgisinden hesaplanır"""
        if durak_bilgisi and "ucret" in durak_bilgisi:
            return durak_bilgisi["ucret"]
        return 0.0


class TaksiArac(Arac):
    """Taksi araç sınıfı"""
    
    def __init__(self, arac_id: str = "taksi_1", isim: str = "Taksi",
                 acilis_ucreti: float = 10.0, km_basina_ucret: float = 4.0):
        super().__init__(arac_id, isim)
        self._acilis_ucreti = acilis_ucreti
        self._km_basina_ucret = km_basina_ucret
    
    def arac_tipi(self) -> str:
        return "taksi"
    
    def ucret_hesapla(self, mesafe: Optional[float] = None, 
                     durak_bilgisi: Optional[dict] = None) -> float:
        """Taksi ücreti mesafeye göre hesaplanır"""
        if mesafe is not None:
            return self._acilis_ucreti + (mesafe * self._km_basina_ucret)
        return 0.0
    
    @property
    def acilis_ucreti(self) -> float:
        return self._acilis_ucreti
    
    @property
    def km_basina_ucret(self) -> float:
        return self._km_basina_ucret

