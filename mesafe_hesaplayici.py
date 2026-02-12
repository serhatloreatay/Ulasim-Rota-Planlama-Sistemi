import math
from typing import Tuple


class MesafeHesaplayici:
    """Mesafe hesaplama yardımcı sınıfı"""
    
    @staticmethod
    def haversine_mesafe(enlem1: float, boylam1: float, 
                         enlem2: float, boylam2: float) -> float:
        """
        Haversine formülü ile iki nokta arasındaki mesafeyi hesapla (km)
        """
        # Dünya yarıçapı (km)
        R = 6371.0
        
        # Dereceyi radyana çevir
        lat1_rad = math.radians(enlem1)
        lat2_rad = math.radians(enlem2)
        delta_lat = math.radians(enlem2 - enlem1)
        delta_lon = math.radians(boylam2 - boylam1)
        
        # Haversine formülü
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        mesafe = R * c
        return mesafe
    
    @staticmethod
    def en_yakin_durak_bul(durak_listesi: list, enlem: float, boylam: float) -> Tuple[str, float]:
        """
        Verilen koordinatlara en yakın durağı bul
        Returns: (durak_id, mesafe_km)
        """
        en_yakin_durak_id = None
        en_kisa_mesafe = float('inf')
        
        for durak_id, durak in durak_listesi.items():
            mesafe = MesafeHesaplayici.haversine_mesafe(
                enlem, boylam,
                durak.enlem, durak.boylam
            )
            
            if mesafe < en_kisa_mesafe:
                en_kisa_mesafe = mesafe
                en_yakin_durak_id = durak_id
        
        return en_yakin_durak_id, en_kisa_mesafe

