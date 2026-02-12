import json
from typing import Dict, List
from durak import Durak, OtobusDurak, TramvayDurak


class VeriYukleyici:
    """JSON veri dosyasını yükleyip durakları oluşturan sınıf"""
    
    def __init__(self, dosya_yolu: str):
        self._dosya_yolu = dosya_yolu
        self._veri: Dict = {}
        self._duraklar: Dict[str, Durak] = {}
        self._taksi_bilgisi: Dict = {}
    
    def veri_yukle(self) -> bool:
        """JSON dosyasını yükle ve parse et"""
        try:
            with open(self._dosya_yolu, 'r', encoding='utf-8') as dosya:
                self._veri = json.load(dosya)
            return True
        except FileNotFoundError:
            print(f"Hata: {self._dosya_yolu} dosyası bulunamadı!")
            return False
        except json.JSONDecodeError:
            print(f"Hata: {self._dosya_yolu} dosyası geçersiz JSON formatında!")
            return False
    
    def duraklari_olustur(self):
        """JSON verisinden durakları oluştur"""
        if not self._veri:
            return
        
        # Taksi bilgisini kaydet
        self._taksi_bilgisi = self._veri.get("taxi", {})
        
        # Durakları oluştur
        for durak_verisi in self._veri.get("duraklar", []):
            durak_id = durak_verisi["id"]
            tasima_tipi = durak_verisi["type"]
            
            # Taşıma tipine göre uygun sınıfı oluştur
            if tasima_tipi == "bus":
                durak = OtobusDurak(
                    durak_id=durak_id,
                    isim=durak_verisi["name"],
                    enlem=durak_verisi["lat"],
                    boylam=durak_verisi["lon"],
                    son_durak=durak_verisi.get("sonDurak", False)
                )
            elif tasima_tipi == "tram":
                durak = TramvayDurak(
                    durak_id=durak_id,
                    isim=durak_verisi["name"],
                    enlem=durak_verisi["lat"],
                    boylam=durak_verisi["lon"],
                    son_durak=durak_verisi.get("sonDurak", False)
                )
            else:
                continue
            
            # Sonraki durakları ekle
            for sonraki_durak in durak_verisi.get("nextStops", []):
                durak.sonraki_durak_ekle(sonraki_durak)
            
            # Aktarma bilgisini ayarla
            if durak_verisi.get("transfer"):
                durak.aktarma_ayarla(durak_verisi["transfer"])
            
            self._duraklar[durak_id] = durak
    
    @property
    def duraklar(self) -> Dict[str, Durak]:
        return self._duraklar
    
    @property
    def taksi_bilgisi(self) -> Dict:
        return self._taksi_bilgisi
    
    def durak_getir(self, durak_id: str) -> Durak:
        """ID'ye göre durak getir"""
        return self._duraklar.get(durak_id)

