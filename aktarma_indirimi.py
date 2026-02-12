from abc import ABC, abstractmethod
from typing import Optional, List


class AktarmaIndirimi(ABC):
    """Aktarma indirimi için soyut temel sınıf - Strategy Pattern"""
    
    @abstractmethod
    def indirim_uygula(self, baslangic_tipi: str, hedef_tipi: str, 
                      mevcut_ucret: float) -> float:
        """
        Aktarma indirimini uygula
        
        Args:
            baslangic_tipi: Başlangıç taşıma tipi ("otobus" veya "tramvay")
            hedef_tipi: Hedef taşıma tipi ("otobus" veya "tramvay")
            mevcut_ucret: Mevcut aktarma ücreti
        
        Returns:
            İndirimli ücret (negatif olabilir - teşvik için)
        """
        pass
    
    @abstractmethod
    def indirim_tipi(self) -> str:
        """İndirim tipini döndür"""
        pass


class OtobusTramvayIndirimi(AktarmaIndirimi):
    """Otobüsten tramvaya geçişte indirim"""
    
    def __init__(self, indirim_orani: float = 0.5):
        """
        Args:
            indirim_orani: İndirim oranı (0.0 - 1.0 arası, örn: 0.5 = %50 indirim)
        """
        self._indirim_orani = indirim_orani
    
    def indirim_uygula(self, baslangic_tipi: str, hedef_tipi: str, 
                      mevcut_ucret: float) -> float:
        """Otobüsten tramvaya geçişte indirim uygula"""
        if baslangic_tipi == "otobus" and hedef_tipi == "tramvay":
            indirim_miktari = mevcut_ucret * self._indirim_orani
            return mevcut_ucret - indirim_miktari
        return mevcut_ucret
    
    def indirim_tipi(self) -> str:
        return "Otobüs → Tramvay İndirimi"
    
    @property
    def indirim_orani(self) -> float:
        return self._indirim_orani


class TramvayOtobusIndirimi(AktarmaIndirimi):
    """Tramvaydan otobüse geçişte indirim"""
    
    def __init__(self, indirim_orani: float = 0.3):
        """
        Args:
            indirim_orani: İndirim oranı (0.0 - 1.0 arası)
        """
        self._indirim_orani = indirim_orani
    
    def indirim_uygula(self, baslangic_tipi: str, hedef_tipi: str, 
                      mevcut_ucret: float) -> float:
        """Tramvaydan otobüse geçişte indirim uygula"""
        if baslangic_tipi == "tramvay" and hedef_tipi == "otobus":
            indirim_miktari = mevcut_ucret * self._indirim_orani
            return mevcut_ucret - indirim_miktari
        return mevcut_ucret
    
    def indirim_tipi(self) -> str:
        return "Tramvay → Otobüs İndirimi"
    
    @property
    def indirim_orani(self) -> float:
        return self._indirim_orani


class NegatifUcretIndirimi(AktarmaIndirimi):
    """Teşvik amaçlı negatif ücret (para iadesi) mekanizması"""
    
    def __init__(self, teşvik_miktari: float = 1.0):
        """
        Args:
            teşvik_miktari: Teşvik miktarı (TL) - bu kadar para iadesi yapılır
        """
        self._tesvik_miktari = teşvik_miktari
    
    def indirim_uygula(self, baslangic_tipi: str, hedef_tipi: str, 
                      mevcut_ucret: float) -> float:
        """
        Otobüsten tramvaya geçişte teşvik uygula (negatif ücret)
        Negatif değer = para iadesi
        """
        if baslangic_tipi == "otobus" and hedef_tipi == "tramvay":
            # Mevcut ücretten teşvik miktarını çıkar
            # Eğer sonuç negatif olursa, bu para iadesi anlamına gelir
            return mevcut_ucret - self._tesvik_miktari
        return mevcut_ucret
    
    def indirim_tipi(self) -> str:
        return "Otobüs → Tramvay Teşvik (Negatif Ücret)"
    
    @property
    def tesvik_miktari(self) -> float:
        return self._tesvik_miktari


class AktarmaIndirimYoneticisi:
    """Aktarma indirimlerini yöneten sınıf"""
    
    def __init__(self):
        self._indirimler: List[AktarmaIndirimi] = []
        self._varsayilan_indirimleri_ekle()
    
    def _varsayilan_indirimleri_ekle(self):
        """Varsayılan indirim stratejilerini ekle"""
        # Otobüsten tramvaya geçişte %50 indirim
        self._indirimler.append(OtobusTramvayIndirimi(indirim_orani=0.5))
        
        # Teşvik amaçlı negatif ücret (isteğe bağlı)
        # self._indirimler.append(NegatifUcretIndirimi(teşvik_miktari=1.0))
    
    def indirim_ekle(self, indirim: AktarmaIndirimi):
        """Yeni bir indirim stratejisi ekle"""
        self._indirimler.append(indirim)
    
    def indirim_hesapla(self, baslangic_tipi: str, hedef_tipi: str, 
                        mevcut_ucret: float) -> tuple[float, Optional[str]]:
        """
        Tüm indirim stratejilerini uygula ve en iyi sonucu döndür
        
        Returns:
            (indirimli_ucret, indirim_aciklama)
        """
        en_iyi_ucret = mevcut_ucret
        uygulanan_indirim = None
        
        for indirim in self._indirimler:
            yeni_ucret = indirim.indirim_uygula(baslangic_tipi, hedef_tipi, mevcut_ucret)
            
            # En düşük ücreti (en fazla indirim) seç
            if yeni_ucret < en_iyi_ucret:
                en_iyi_ucret = yeni_ucret
                uygulanan_indirim = indirim.indirim_tipi()
        
        return en_iyi_ucret, uygulanan_indirim
    
    @property
    def indirimler(self) -> List[AktarmaIndirimi]:
        return self._indirimler

