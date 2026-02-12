from typing import Optional


class Konum:
    """Konum sınıfı - enlem ve boylam bilgilerini tutar"""
    
    def __init__(self, enlem: float, boylam: float, isim: Optional[str] = None):
        self._enlem = enlem
        self._boylam = boylam
        self._isim = isim
    
    @property
    def enlem(self) -> float:
        return self._enlem
    
    @property
    def boylam(self) -> float:
        return self._boylam
    
    @property
    def isim(self) -> Optional[str]:
        return self._isim
    
    def __str__(self) -> str:
        if self._isim:
            return f"{self._isim} ({self._enlem}, {self._boylam})"
        return f"({self._enlem}, {self._boylam})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Konum):
            return False
        return (abs(self._enlem - other._enlem) < 0.0001 and 
                abs(self._boylam - other._boylam) < 0.0001)

