from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from konum import Konum
from rota import Rota, RotaAdimi, RotaHesaplayici
from hat import HatYoneticisi
from taksi import Taksi
from mesafe_hesaplayici import MesafeHesaplayici


class RotaStratejisi(ABC):
    """Rota stratejisi için soyut temel sınıf - Strategy Pattern"""
    
    @abstractmethod
    def rota_olustur(self, baslangic_konum: Konum, hedef_konum: Konum,
                    hat_yoneticisi: HatYoneticisi, taksi: Taksi) -> Optional[Rota]:
        """Rota oluştur"""
        pass
    
    @abstractmethod
    def strateji_adi(self) -> str:
        """Strateji adını döndür"""
        pass
    
    @abstractmethod
    def izin_verilen_tasima_tipleri(self) -> List[str]:
        """İzin verilen taşıma tiplerini döndür"""
        pass


class SadeceOtobusStratejisi(RotaStratejisi):
    """Sadece otobüs kullanarak rota oluştur"""
    
    def rota_olustur(self, baslangic_konum: Konum, hedef_konum: Konum,
                    hat_yoneticisi: HatYoneticisi, taksi: Taksi) -> Optional[Rota]:
        """Sadece otobüs durakları kullanarak rota oluştur"""
        return self._rota_olustur_tek_tip(baslangic_konum, hedef_konum, 
                                          hat_yoneticisi, taksi, "otobus")
    
    def strateji_adi(self) -> str:
        return "Sadece Otobüs"
    
    def izin_verilen_tasima_tipleri(self) -> List[str]:
        return ["otobus"]
    
    def _rota_olustur_tek_tip(self, baslangic_konum: Konum, hedef_konum: Konum,
                              hat_yoneticisi: HatYoneticisi, taksi: Taksi,
                              tasima_tipi: str) -> Optional[Rota]:
        """Tek taşıma tipi ile rota oluştur"""
        # En yakın durakları bul (sadece belirtilen tip)
        baslangic_durak_id, baslangic_mesafe = self._en_yakin_durak_bul_tip(
            baslangic_konum, hat_yoneticisi, tasima_tipi
        )
        hedef_durak_id, hedef_mesafe = self._en_yakin_durak_bul_tip(
            hedef_konum, hat_yoneticisi, tasima_tipi
        )
        
        if not baslangic_durak_id or not hedef_durak_id:
            return None
        
        adimlar: List[RotaAdimi] = []
        
        # Başlangıç konumundan durağa
        adimlar.extend(self._konumdan_duraga(baslangic_konum, baslangic_durak_id, 
                                            baslangic_mesafe, hat_yoneticisi, taksi))
        
        # Duraklar arası (sadece belirtilen tip)
        durak_arasi_rota = self._durak_arasi_rota_bul_tip(
            baslangic_durak_id, hedef_durak_id, hat_yoneticisi, tasima_tipi
        )
        if durak_arasi_rota:
            adimlar.extend(durak_arasi_rota)
        else:
            return None  # Rota bulunamadı
        
        # Hedef duraktan konuma
        adimlar.extend(self._durakdan_konuma(hedef_durak_id, hedef_konum, 
                                            hedef_mesafe, hat_yoneticisi, taksi))
        
        return self._rota_olustur(adimlar)
    
    def _en_yakin_durak_bul_tip(self, konum: Konum, hat_yoneticisi: HatYoneticisi,
                                tasima_tipi: str) -> Tuple[Optional[str], float]:
        """Belirli tip durak bul"""
        en_yakin_id = None
        en_kisa_mesafe = float('inf')
        
        for durak_id, durak in hat_yoneticisi.tum_duraklar().items():
            if durak.tasima_tipi() == tasima_tipi:
                mesafe = MesafeHesaplayici.haversine_mesafe(
                    konum.enlem, konum.boylam,
                    durak.enlem, durak.boylam
                )
                if mesafe < en_kisa_mesafe:
                    en_kisa_mesafe = mesafe
                    en_yakin_id = durak_id
        
        return en_yakin_id, en_kisa_mesafe
    
    def _durak_arasi_rota_bul_tip(self, baslangic_id: str, hedef_id: str,
                                  hat_yoneticisi: HatYoneticisi, tasima_tipi: str) -> Optional[List[RotaAdimi]]:
        """Belirli tip ile durak arası rota bul"""
        from collections import deque
        
        ziyaret_edildi = set()
        kuyruk = deque([(baslangic_id, [])])
        
        while kuyruk:
            mevcut_id, yol = kuyruk.popleft()
            
            if mevcut_id == hedef_id:
                return self._yolu_adimlara_cevir(yol, hat_yoneticisi)
            
            if mevcut_id in ziyaret_edildi:
                continue
            
            ziyaret_edildi.add(mevcut_id)
            durak = hat_yoneticisi.durak_getir(mevcut_id)
            
            if not durak or durak.tasima_tipi() != tasima_tipi:
                continue
            
            for sonraki in durak.sonraki_duraklar:
                sonraki_id = sonraki["stopId"]
                sonraki_durak = hat_yoneticisi.durak_getir(sonraki_id)
                if sonraki_durak and sonraki_durak.tasima_tipi() == tasima_tipi:
                    if sonraki_id not in ziyaret_edildi:
                        yeni_yol = yol + [(mevcut_id, sonraki_id, sonraki)]
                        kuyruk.append((sonraki_id, yeni_yol))
        
        return None
    
    def _konumdan_duraga(self, konum: Konum, durak_id: str, mesafe: float,
                        hat_yoneticisi: HatYoneticisi, taksi: Taksi) -> List[RotaAdimi]:
        """Konumdan durağa ulaşım adımları"""
        adimlar = []
        if mesafe > 3.0:  # Taksi zorunlu
            taksi_ucret = taksi.ucret_hesapla(mesafe)
            adimlar.append(RotaAdimi(
                baslangic="konum", hedef=durak_id, ulasim_tipi="taksi",
                mesafe=mesafe, sure=mesafe * 2, ucret=taksi_ucret,
                aciklama=f"Taksi ile {durak_id} durağına"
            ))
        else:
            adimlar.append(RotaAdimi(
                baslangic="konum", hedef=durak_id, ulasim_tipi="yurume",
                mesafe=mesafe, sure=mesafe * 12, ucret=0.0,
                aciklama=f"Yürüyerek {durak_id} durağına"
            ))
        return adimlar
    
    def _durakdan_konuma(self, durak_id: str, konum: Konum, mesafe: float,
                         hat_yoneticisi: HatYoneticisi, taksi: Taksi) -> List[RotaAdimi]:
        """Duraktan konuma ulaşım adımları"""
        adimlar = []
        if mesafe > 3.0:  # Taksi zorunlu
            taksi_ucret = taksi.ucret_hesapla(mesafe)
            adimlar.append(RotaAdimi(
                baslangic=durak_id, hedef="konum", ulasim_tipi="taksi",
                mesafe=mesafe, sure=mesafe * 2, ucret=taksi_ucret,
                aciklama=f"Taksi ile hedef konuma"
            ))
        else:
            adimlar.append(RotaAdimi(
                baslangic=durak_id, hedef="konum", ulasim_tipi="yurume",
                mesafe=mesafe, sure=mesafe * 12, ucret=0.0,
                aciklama=f"Yürüyerek hedef konuma"
            ))
        return adimlar
    
    def _yolu_adimlara_cevir(self, yol: List, hat_yoneticisi: HatYoneticisi) -> List[RotaAdimi]:
        """Yol listesini RotaAdimi listesine çevir"""
        adimlar = []
        for adim in yol:
            baslangic_id, hedef_id, bilgi = adim
            tasima_tipi = "otobus" if "bus" in baslangic_id else "tramvay"
            adimlar.append(RotaAdimi(
                baslangic=baslangic_id, hedef=hedef_id, ulasim_tipi=tasima_tipi,
                mesafe=bilgi["mesafe"], sure=bilgi["sure"], ucret=bilgi["ucret"],
                aciklama=f"{tasima_tipi.capitalize()}: {baslangic_id} -> {hedef_id}"
            ))
        return adimlar
    
    def _rota_olustur(self, adimlar: List[RotaAdimi]) -> Rota:
        """RotaAdimi listesinden Rota oluştur"""
        toplam_mesafe = sum(adim.mesafe for adim in adimlar)
        toplam_sure = sum(adim.sure for adim in adimlar)
        toplam_ucret = sum(adim.ucret for adim in adimlar)
        aktarma_sayisi = sum(1 for adim in adimlar if adim.ulasim_tipi == "aktarma")
        return Rota(adimlar=adimlar, toplam_mesafe=toplam_mesafe,
                   toplam_sure=toplam_sure, toplam_ucret=toplam_ucret,
                   aktarma_sayisi=aktarma_sayisi)


class SadeceTramvayStratejisi(SadeceOtobusStratejisi):
    """Sadece tramvay kullanarak rota oluştur"""
    
    def rota_olustur(self, baslangic_konum: Konum, hedef_konum: Konum,
                    hat_yoneticisi: HatYoneticisi, taksi: Taksi) -> Optional[Rota]:
        """Sadece tramvay durakları kullanarak rota oluştur"""
        return self._rota_olustur_tek_tip(baslangic_konum, hedef_konum,
                                          hat_yoneticisi, taksi, "tramvay")
    
    def strateji_adi(self) -> str:
        return "Sadece Tramvay"
    
    def izin_verilen_tasima_tipleri(self) -> List[str]:
        return ["tramvay"]


class OtobusTramvayAktarmaStratejisi(RotaStratejisi):
    """Otobüs + Tramvay aktarması ile rota oluştur"""
    
    def rota_olustur(self, baslangic_konum: Konum, hedef_konum: Konum,
                    hat_yoneticisi: HatYoneticisi, taksi: Taksi) -> Optional[Rota]:
        """Aktarma içeren rota oluştur"""
        # Mevcut RotaHesaplayici'yi kullan (aktarma destekli)
        rota_hesaplayici = RotaHesaplayici(hat_yoneticisi, taksi)
        rota = rota_hesaplayici.en_uygun_rota_bul(baslangic_konum, hedef_konum)
        
        # Sadece aktarma içeren rotaları filtrele
        if rota and rota.aktarma_sayisi > 0:
            return rota
        return None
    
    def strateji_adi(self) -> str:
        return "Otobüs + Tramvay Aktarması"
    
    def izin_verilen_tasima_tipleri(self) -> List[str]:
        return ["otobus", "tramvay"]


class TaksiKombinasyonStratejisi(RotaStratejisi):
    """Taksi + Otobüs veya Tramvay kombinasyonu"""
    
    def rota_olustur(self, baslangic_konum: Konum, hedef_konum: Konum,
                    hat_yoneticisi: HatYoneticisi, taksi: Taksi) -> Optional[Rota]:
        """Taksi ile başlayan kombinasyon rota oluştur"""
        # En yakın durakları bul
        baslangic_durak_id, baslangic_mesafe = self._en_yakin_durak_bul(
            baslangic_konum, hat_yoneticisi
        )
        hedef_durak_id, hedef_mesafe = self._en_yakin_durak_bul(
            hedef_konum, hat_yoneticisi
        )
        
        if not baslangic_durak_id or not hedef_durak_id:
            return None
        
        adimlar: List[RotaAdimi] = []
        
        # Başlangıçtan durağa - MUTLAKA taksi
        taksi_ucret = taksi.ucret_hesapla(baslangic_mesafe)
        adimlar.append(RotaAdimi(
            baslangic="konum", hedef=baslangic_durak_id, ulasim_tipi="taksi",
            mesafe=baslangic_mesafe, sure=baslangic_mesafe * 2, ucret=taksi_ucret,
            aciklama=f"Taksi ile {baslangic_durak_id} durağına"
        ))
        
        # Duraklar arası toplu taşıma - kendi implementasyonumuzu kullan
        durak_arasi_rota = self._durak_arasi_rota_bul_genel(
            baslangic_durak_id, hedef_durak_id, hat_yoneticisi
        )
        if durak_arasi_rota:
            adimlar.extend(durak_arasi_rota)
        else:
            # Duraklar arası da taksi
            durak_arasi_mesafe = MesafeHesaplayici.haversine_mesafe(
                hat_yoneticisi.durak_getir(baslangic_durak_id).enlem,
                hat_yoneticisi.durak_getir(baslangic_durak_id).boylam,
                hat_yoneticisi.durak_getir(hedef_durak_id).enlem,
                hat_yoneticisi.durak_getir(hedef_durak_id).boylam
            )
            taksi_ucret = taksi.ucret_hesapla(durak_arasi_mesafe)
            adimlar.append(RotaAdimi(
                baslangic=baslangic_durak_id, hedef=hedef_durak_id,
                ulasim_tipi="taksi", mesafe=durak_arasi_mesafe,
                sure=durak_arasi_mesafe * 2, ucret=taksi_ucret,
                aciklama=f"Taksi ile {baslangic_durak_id} -> {hedef_durak_id}"
            ))
        
        # Hedef duraktan konuma
        if hedef_mesafe > 3.0:
            taksi_ucret = taksi.ucret_hesapla(hedef_mesafe)
            adimlar.append(RotaAdimi(
                baslangic=hedef_durak_id, hedef="konum", ulasim_tipi="taksi",
                mesafe=hedef_mesafe, sure=hedef_mesafe * 2, ucret=taksi_ucret,
                aciklama=f"Taksi ile hedef konuma"
            ))
        else:
            adimlar.append(RotaAdimi(
                baslangic=hedef_durak_id, hedef="konum", ulasim_tipi="yurume",
                mesafe=hedef_mesafe, sure=hedef_mesafe * 12, ucret=0.0,
                aciklama=f"Yürüyerek hedef konuma"
            ))
        
        toplam_mesafe = sum(adim.mesafe for adim in adimlar)
        toplam_sure = sum(adim.sure for adim in adimlar)
        toplam_ucret = sum(adim.ucret for adim in adimlar)
        aktarma_sayisi = sum(1 for adim in adimlar if adim.ulasim_tipi == "aktarma")
        
        return Rota(adimlar=adimlar, toplam_mesafe=toplam_mesafe,
                    toplam_sure=toplam_sure, toplam_ucret=toplam_ucret,
                    aktarma_sayisi=aktarma_sayisi)
    
    def strateji_adi(self) -> str:
        return "Taksi + Otobüs/Tramvay Kombinasyonu"
    
    def izin_verilen_tasima_tipleri(self) -> List[str]:
        return ["taksi", "otobus", "tramvay"]
    
    def _en_yakin_durak_bul(self, konum: Konum, hat_yoneticisi: HatYoneticisi) -> Tuple[Optional[str], float]:
        """En yakın durağı bul"""
        en_yakin_id = None
        en_kisa_mesafe = float('inf')
        
        for durak_id, durak in hat_yoneticisi.tum_duraklar().items():
            mesafe = MesafeHesaplayici.haversine_mesafe(
                konum.enlem, konum.boylam,
                durak.enlem, durak.boylam
            )
            if mesafe < en_kisa_mesafe:
                en_kisa_mesafe = mesafe
                en_yakin_id = durak_id
        
        return en_yakin_id, en_kisa_mesafe
    
    def _durak_arasi_rota_bul_genel(self, baslangic_id: str, hedef_id: str,
                                    hat_yoneticisi: HatYoneticisi) -> Optional[List[RotaAdimi]]:
        """Genel durak arası rota bul (aktarma dahil)"""
        from collections import deque
        
        ziyaret_edildi = set()
        kuyruk = deque([(baslangic_id, [])])
        
        while kuyruk:
            mevcut_id, yol = kuyruk.popleft()
            
            if mevcut_id == hedef_id:
                return self._yolu_adimlara_cevir_genel(yol, hat_yoneticisi)
            
            if mevcut_id in ziyaret_edildi:
                continue
            
            ziyaret_edildi.add(mevcut_id)
            durak = hat_yoneticisi.durak_getir(mevcut_id)
            
            if not durak:
                continue
            
            # Sonraki duraklara git
            for sonraki in durak.sonraki_duraklar:
                sonraki_id = sonraki["stopId"]
                if sonraki_id not in ziyaret_edildi:
                    yeni_yol = yol + [(mevcut_id, sonraki_id, sonraki)]
                    kuyruk.append((sonraki_id, yeni_yol))
            
            # Aktarma yap
            if durak.aktarma:
                aktarma_id = durak.aktarma["transferStopId"]
                if aktarma_id not in ziyaret_edildi:
                    aktarma_bilgisi = {
                        "transferSure": durak.aktarma["transferSure"],
                        "transferUcret": durak.aktarma["transferUcret"]
                    }
                    yeni_yol = yol + [(mevcut_id, aktarma_id, aktarma_bilgisi, True)]
                    kuyruk.append((aktarma_id, yeni_yol))
        
        return None
    
    def _yolu_adimlara_cevir_genel(self, yol: List, hat_yoneticisi: HatYoneticisi) -> List[RotaAdimi]:
        """Yol listesini RotaAdimi listesine çevir (aktarma dahil)"""
        adimlar = []
        for adim in yol:
            if len(adim) == 4 and adim[3]:  # Aktarma
                baslangic_id, hedef_id, aktarma_bilgisi, _ = adim
                adimlar.append(RotaAdimi(
                    baslangic=baslangic_id, hedef=hedef_id, ulasim_tipi="aktarma",
                    mesafe=0, sure=aktarma_bilgisi["transferSure"],
                    ucret=aktarma_bilgisi["transferUcret"],
                    aciklama=f"Aktarma: {baslangic_id} -> {hedef_id}"
                ))
            else:  # Normal durak geçişi
                baslangic_id, hedef_id, bilgi = adim
                tasima_tipi = "otobus" if "bus" in baslangic_id else "tramvay"
                adimlar.append(RotaAdimi(
                    baslangic=baslangic_id, hedef=hedef_id, ulasim_tipi=tasima_tipi,
                    mesafe=bilgi["mesafe"], sure=bilgi["sure"], ucret=bilgi["ucret"],
                    aciklama=f"{tasima_tipi.capitalize()}: {baslangic_id} -> {hedef_id}"
                ))
        return adimlar


class SadeceTaksiStratejisi(RotaStratejisi):
    """Sadece taksi kullanarak rota oluştur"""
    
    def rota_olustur(self, baslangic_konum: Konum, hedef_konum: Konum,
                    hat_yoneticisi: HatYoneticisi, taksi: Taksi) -> Optional[Rota]:
        """Sadece taksi ile direkt rota"""
        mesafe = MesafeHesaplayici.haversine_mesafe(
            baslangic_konum.enlem, baslangic_konum.boylam,
            hedef_konum.enlem, hedef_konum.boylam
        )
        
        taksi_ucret = taksi.ucret_hesapla(mesafe)
        taksi_sure = mesafe * 2  # Yaklaşık 2 dk/km
        
        adim = RotaAdimi(
            baslangic="konum",
            hedef="konum",
            ulasim_tipi="taksi",
            mesafe=mesafe,
            sure=taksi_sure,
            ucret=taksi_ucret,
            aciklama="Taksi ile direkt gidiş"
        )
        
        return Rota(
            adimlar=[adim],
            toplam_mesafe=mesafe,
            toplam_sure=taksi_sure,
            toplam_ucret=taksi_ucret,
            aktarma_sayisi=0
        )
    
    def strateji_adi(self) -> str:
        return "Sadece Taksi"
    
    def izin_verilen_tasima_tipleri(self) -> List[str]:
        return ["taksi"]


class RotaSecenekleriUretici:
    """Farklı rota seçeneklerini üreten sınıf - Factory Pattern"""
    
    def __init__(self, hat_yoneticisi: HatYoneticisi, taksi: Taksi):
        self._hat_yoneticisi = hat_yoneticisi
        self._taksi = taksi
        self._stratejiler = [
            SadeceOtobusStratejisi(),
            SadeceTramvayStratejisi(),
            OtobusTramvayAktarmaStratejisi(),
            TaksiKombinasyonStratejisi(),
            SadeceTaksiStratejisi()
        ]
    
    def tum_rota_secenekleri_olustur(self, baslangic_konum: Konum, 
                                     hedef_konum: Konum) -> List[Tuple[str, Optional[Rota]]]:
        """
        Tüm rota seçeneklerini oluştur
        
        Returns:
            [(strateji_adi, rota), ...] listesi
        """
        secenekler = []
        
        for strateji in self._stratejiler:
            rota = strateji.rota_olustur(
                baslangic_konum, hedef_konum,
                self._hat_yoneticisi, self._taksi
            )
            secenekler.append((strateji.strateji_adi(), rota))
        
        return secenekler
    
    def strateji_ekle(self, strateji: RotaStratejisi):
        """Yeni bir rota stratejisi ekle"""
        self._stratejiler.append(strateji)
    
    @property
    def stratejiler(self) -> List[RotaStratejisi]:
        return self._stratejiler

