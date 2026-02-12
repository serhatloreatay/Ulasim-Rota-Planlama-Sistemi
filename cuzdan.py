from typing import Optional


class Cuzdan:
    """Kullanıcı cüzdanı - ödeme yöntemlerine göre bakiyeleri tutar"""
    
    def __init__(self, nakit: float = 0.0, kredi_karti_limiti: float = 0.0, 
                 kentkart_bakiyesi: float = 0.0):
        """
        Args:
            nakit: Nakit para miktarı (TL)
            kredi_karti_limiti: Kredi kartı limiti (TL)
            kentkart_bakiyesi: Kentkart bakiyesi (TL)
        """
        self._nakit = nakit
        self._kredi_karti_limiti = kredi_karti_limiti
        self._kentkart_bakiyesi = kentkart_bakiyesi
    
    @property
    def nakit(self) -> float:
        return self._nakit
    
    @property
    def kredi_karti_limiti(self) -> float:
        return self._kredi_karti_limiti
    
    @property
    def kentkart_bakiyesi(self) -> float:
        return self._kentkart_bakiyesi
    
    def nakit_ekle(self, miktar: float):
        """Nakit ekle"""
        self._nakit += miktar
    
    def nakit_cikar(self, miktar: float) -> bool:
        """Nakit çıkar - yeterli bakiye varsa"""
        if self._nakit >= miktar:
            self._nakit -= miktar
            return True
        return False
    
    def kredi_karti_kullan(self, miktar: float) -> bool:
        """Kredi kartı kullan - limit kontrolü"""
        if self._kredi_karti_limiti >= miktar:
            self._kredi_karti_limiti -= miktar
            return True
        return False
    
    def kentkart_kullan(self, miktar: float) -> bool:
        """Kentkart kullan - bakiye kontrolü"""
        if self._kentkart_bakiyesi >= miktar:
            self._kentkart_bakiyesi -= miktar
            return True
        return False
    
    def toplam_bakiye(self) -> float:
        """Toplam kullanılabilir bakiye"""
        return self._nakit + self._kredi_karti_limiti + self._kentkart_bakiyesi
    
    def odeme_yapabilir_mi(self, tutar: float, odeme_yontemi: str) -> bool:
        """
        Belirtilen ödeme yöntemi ile ödeme yapılabilir mi?
        
        Args:
            tutar: Ödenecek tutar
            odeme_yontemi: "nakit", "kredi_karti", "kentkart"
        
        Returns:
            True if ödeme yapılabilir
        """
        if odeme_yontemi == "nakit":
            return self._nakit >= tutar
        elif odeme_yontemi == "kredi_karti":
            return self._kredi_karti_limiti >= tutar
        elif odeme_yontemi == "kentkart":
            return self._kentkart_bakiyesi >= tutar
        return False
    
    def __str__(self) -> str:
        return (f"Cüzdan - Nakit: {self._nakit:.2f} TL, "
                f"Kredi Kartı: {self._kredi_karti_limiti:.2f} TL, "
                f"Kentkart: {self._kentkart_bakiyesi:.2f} TL")

