from abc import ABC, abstractmethod


class OdemeYontemi(ABC):
    """Ödeme yöntemi için soyut temel sınıf"""
    
    def __init__(self, yontem_adi: str):
        self._yontem_adi = yontem_adi
    
    @property
    def yontem_adi(self) -> str:
        return self._yontem_adi
    
    @abstractmethod
    def odeme_yap(self, tutar: float) -> bool:
        """Ödeme işlemini gerçekleştir"""
        pass
    
    @abstractmethod
    def komisyon_orani(self) -> float:
        """Komisyon oranını döndür (0.0 - 1.0 arası)"""
        pass
    
    def komisyonlu_tutar_hesapla(self, tutar: float) -> float:
        """Komisyon dahil toplam tutarı hesapla"""
        komisyon = tutar * self.komisyon_orani()
        return tutar + komisyon
    
    def __str__(self) -> str:
        return f"{self._yontem_adi}"


class NakitOdeme(OdemeYontemi):
    """Nakit ödeme sınıfı"""
    
    def __init__(self):
        super().__init__("Nakit")
    
    def odeme_yap(self, tutar: float) -> bool:
        """Nakit ödeme - komisyon yok"""
        return True
    
    def komisyon_orani(self) -> float:
        return 0.0  # Nakit ödemede komisyon yok


class KrediKartiOdeme(OdemeYontemi):
    """Kredi kartı ödeme sınıfı"""
    
    def __init__(self, kart_numarasi: str = ""):
        super().__init__("Kredi Kartı")
        self._kart_numarasi = kart_numarasi
    
    def odeme_yap(self, tutar: float) -> bool:
        """Kredi kartı ödeme işlemi"""
        # Gerçek uygulamada banka API'si ile iletişim kurulur
        return True
    
    def komisyon_orani(self) -> float:
        return 0.02  # %2 komisyon


class KentkartOdeme(OdemeYontemi):
    """Kentkart ödeme sınıfı"""
    
    def __init__(self, kart_numarasi: str = ""):
        super().__init__("Kentkart")
        self._kart_numarasi = kart_numarasi
    
    def odeme_yap(self, tutar: float) -> bool:
        """Kentkart ödeme işlemi"""
        # Gerçek uygulamada Kentkart sistemi ile iletişim kurulur
        return True
    
    def komisyon_orani(self) -> float:
        return 0.0  # Kentkart'ta komisyon yok

