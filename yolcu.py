from abc import ABC, abstractmethod


class Yolcu(ABC):
    """Yolcu için soyut temel sınıf"""
    
    def __init__(self, isim: str):
        self._isim = isim
    
    @property
    def isim(self) -> str:
        return self._isim
    
    @abstractmethod
    def yolcu_tipi(self) -> str:
        """Yolcu tipini döndür"""
        pass
    
    @abstractmethod
    def indirim_orani(self) -> float:
        """İndirim oranını döndür (0.0 - 1.0 arası, örn: 0.2 = %20 indirim)"""
        pass
    
    def indirimli_ucret_hesapla(self, normal_ucret: float) -> float:
        """İndirimli ücreti hesapla"""
        indirim_miktari = normal_ucret * self.indirim_orani()
        return normal_ucret - indirim_miktari
    
    def __str__(self) -> str:
        return f"{self._isim} ({self.yolcu_tipi()})"


class GenelYolcu(Yolcu):
    """Genel yolcu sınıfı (indirim yok)"""
    
    def __init__(self, isim: str = "Genel Yolcu"):
        super().__init__(isim)
    
    def yolcu_tipi(self) -> str:
        return "Genel"
    
    def indirim_orani(self) -> float:
        return 0.0


class NormalYolcu(GenelYolcu):
    """Normal yolcu sınıfı (GenelYolcu ile aynı)"""
    pass


class OgrenciYolcu(Yolcu):
    """Öğrenci yolcu sınıfı"""
    
    def __init__(self, isim: str = "Öğrenci"):
        super().__init__(isim)
    
    def yolcu_tipi(self) -> str:
        return "Öğrenci"
    
    def indirim_orani(self) -> float:
        return 0.3  # %30 indirim


class OgretmenYolcu(Yolcu):
    """Öğretmen yolcu sınıfı"""
    
    def __init__(self, isim: str = "Öğretmen"):
        super().__init__(isim)
    
    def yolcu_tipi(self) -> str:
        return "Öğretmen"
    
    def indirim_orani(self) -> float:
        return 0.25  # %25 indirim


class YasliYolcu(Yolcu):
    """65 yaş üstü yolcu sınıfı"""
    
    def __init__(self, isim: str = "65 Yaş Üstü"):
        super().__init__(isim)
    
    def yolcu_tipi(self) -> str:
        return "65 Yaş Üstü"
    
    def indirim_orani(self) -> float:
        return 0.35  # %35 indirim

