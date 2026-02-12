from abc import ABC, abstractmethod
from typing import List, Optional, Dict


class Durak(ABC):
    """Durak için soyut temel sınıf"""
    
    def __init__(self, durak_id: str, isim: str, enlem: float, boylam: float, son_durak: bool):
        self._durak_id = durak_id
        self._isim = isim
        self._enlem = enlem
        self._boylam = boylam
        self._son_durak = son_durak
        self._sonraki_duraklar: List[Dict] = []
        self._aktarma: Optional[Dict] = None
    
    @property
    def durak_id(self) -> str:
        return self._durak_id
    
    @property
    def isim(self) -> str:
        return self._isim
    
    @property
    def enlem(self) -> float:
        return self._enlem
    
    @property
    def boylam(self) -> float:
        return self._boylam
    
    @property
    def son_durak(self) -> bool:
        return self._son_durak
    
    @property
    def sonraki_duraklar(self) -> List[Dict]:
        return self._sonraki_duraklar
    
    @property
    def aktarma(self) -> Optional[Dict]:
        return self._aktarma
    
    def sonraki_durak_ekle(self, durak_bilgisi: Dict):
        """Sonraki durağı ekle"""
        self._sonraki_duraklar.append(durak_bilgisi)
    
    def aktarma_ayarla(self, aktarma_bilgisi: Dict):
        """Aktarma bilgisini ayarla"""
        self._aktarma = aktarma_bilgisi
    
    @abstractmethod
    def tasima_tipi(self) -> str:
        """Taşıma tipini döndür (otobüs veya tramvay)"""
        pass
    
    @abstractmethod
    def ucret_hesapla(self, hedef_durak_id: str) -> float:
        """Belirli bir durağa gidiş ücretini hesapla"""
        pass
    
    @abstractmethod
    def sure_hesapla(self, hedef_durak_id: str) -> float:
        """Belirli bir durağa gidiş süresini hesapla"""
        pass
    
    def __str__(self) -> str:
        return f"{self._isim} ({self.tasima_tipi()})"


class OtobusDurak(Durak):
    """Otobüs durağı sınıfı"""
    
    def __init__(self, durak_id: str, isim: str, enlem: float, boylam: float, son_durak: bool):
        super().__init__(durak_id, isim, enlem, boylam, son_durak)
    
    def tasima_tipi(self) -> str:
        return "otobüs"
    
    def ucret_hesapla(self, hedef_durak_id: str) -> float:
        """Otobüs durağından hedef durağa ücret hesapla"""
        for sonraki in self._sonraki_duraklar:
            if sonraki["stopId"] == hedef_durak_id:
                return sonraki["ucret"]
        return 0.0
    
    def sure_hesapla(self, hedef_durak_id: str) -> float:
        """Otobüs durağından hedef durağa süre hesapla"""
        for sonraki in self._sonraki_duraklar:
            if sonraki["stopId"] == hedef_durak_id:
                return sonraki["sure"]
        return 0.0


class TramvayDurak(Durak):
    """Tramvay durağı sınıfı"""
    
    def __init__(self, durak_id: str, isim: str, enlem: float, boylam: float, son_durak: bool):
        super().__init__(durak_id, isim, enlem, boylam, son_durak)
    
    def tasima_tipi(self) -> str:
        return "tramvay"
    
    def ucret_hesapla(self, hedef_durak_id: str) -> float:
        """Tramvay durağından hedef durağa ücret hesapla"""
        for sonraki in self._sonraki_duraklar:
            if sonraki["stopId"] == hedef_durak_id:
                return sonraki["ucret"]
        return 0.0
    
    def sure_hesapla(self, hedef_durak_id: str) -> float:
        """Tramvay durağından hedef durağa süre hesapla"""
        for sonraki in self._sonraki_duraklar:
            if sonraki["stopId"] == hedef_durak_id:
                return sonraki["sure"]
        return 0.0

