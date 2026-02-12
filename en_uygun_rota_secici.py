from typing import List, Optional, Tuple
from konum import Konum
from rota import Rota
from rota_secenekleri import RotaSecenekleriUretici
from cuzdan import Cuzdan
from odeme import OdemeYontemi, NakitOdeme, KrediKartiOdeme, KentkartOdeme


class EnUygunRotaSecici:
    """En uygun rotayı seçen sınıf - maliyet, süre ve bakiye kontrolü"""
    
    def __init__(self, rota_secenekleri_uretici: RotaSecenekleriUretici):
        self._rota_secenekleri_uretici = rota_secenekleri_uretici
    
    def en_uygun_rotayi_bul(self, baslangic_konum: Konum, hedef_konum: Konum,
                           cuzdan: Cuzdan, odeme_yontemi: str = "nakit",
                           oncelik: str = "maliyet") -> Tuple[Optional[Rota], List[Tuple[str, Rota, bool]]]:
        """
        En uygun rotayı bul
        
        Args:
            baslangic_konum: Başlangıç konumu
            hedef_konum: Hedef konum
            cuzdan: Kullanıcı cüzdanı
            odeme_yontemi: Ödeme yöntemi ("nakit", "kredi_karti", "kentkart")
            oncelik: Öncelik ("maliyet", "sure", "aktarma")
        
        Returns:
            (en_uygun_rota, [(strateji_adi, rota, odeme_yapilabilir), ...])
        """
        # Tüm rota seçeneklerini al
        tum_secenekler = self._rota_secenekleri_uretici.tum_rota_secenekleri_olustur(
            baslangic_konum, hedef_konum
        )
        
        # Her seçenek için ödeme kontrolü yap
        secenekler_analiz = []
        for strateji_adi, rota in tum_secenekler:
            if rota:
                # Komisyon dahil toplam tutarı hesapla
                odeme_yontemi_obj = self._odeme_yontemi_olustur(odeme_yontemi)
                komisyonlu_tutar = odeme_yontemi_obj.komisyonlu_tutar_hesapla(rota.toplam_ucret)
                
                # Ödeme yapılabilir mi?
                odeme_yapilabilir = cuzdan.odeme_yapabilir_mi(komisyonlu_tutar, odeme_yontemi)
                
                secenekler_analiz.append((strateji_adi, rota, odeme_yapilabilir))
            else:
                secenekler_analiz.append((strateji_adi, None, False))
        
        # En uygun rotayı seç
        en_uygun_rota = self._en_iyi_rotayi_sec(secenekler_analiz, oncelik, cuzdan, odeme_yontemi)
        
        return en_uygun_rota, secenekler_analiz
    
    def _odeme_yontemi_olustur(self, odeme_yontemi: str) -> OdemeYontemi:
        """Ödeme yöntemi nesnesi oluştur"""
        if odeme_yontemi == "nakit":
            return NakitOdeme()
        elif odeme_yontemi == "kredi_karti":
            return KrediKartiOdeme()
        elif odeme_yontemi == "kentkart":
            return KentkartOdeme()
        return NakitOdeme()
    
    def _en_iyi_rotayi_sec(self, secenekler: List[Tuple[str, Optional[Rota], bool]],
                          oncelik: str, cuzdan: Cuzdan, odeme_yontemi: str) -> Optional[Rota]:
        """En iyi rotayı seç"""
        # Önce ödeme yapılabilir rotaları filtrele
        uygun_rotalar = [(ad, rota, odeme_yapilabilir) 
                         for ad, rota, odeme_yapilabilir in secenekler
                         if rota and odeme_yapilabilir]
        
        if not uygun_rotalar:
            # Hiçbir rota için yeterli bakiye yok, en ucuzunu göster
            uygun_rotalar = [(ad, rota, odeme_yapilabilir) 
                            for ad, rota, odeme_yapilabilir in secenekler
                            if rota]
        
        if not uygun_rotalar:
            return None
        
        # Önceliğe göre sırala
        if oncelik == "maliyet":
            uygun_rotalar.sort(key=lambda x: x[1].toplam_ucret)
        elif oncelik == "sure":
            uygun_rotalar.sort(key=lambda x: x[1].toplam_sure)
        elif oncelik == "aktarma":
            uygun_rotalar.sort(key=lambda x: (x[1].aktarma_sayisi, x[1].toplam_ucret))
        
        return uygun_rotalar[0][1]  # En iyi rota
    
    def detayli_analiz(self, baslangic_konum: Konum, hedef_konum: Konum,
                      cuzdan: Cuzdan, odeme_yontemi: str) -> dict:
        """
        Detaylı rota analizi - tüm seçenekleri karşılaştır
        
        Returns:
            Analiz sonuçları dict
        """
        tum_secenekler = self._rota_secenekleri_uretici.tum_rota_secenekleri_olustur(
            baslangic_konum, hedef_konum
        )
        
        odeme_yontemi_obj = self._odeme_yontemi_olustur(odeme_yontemi)
        
        analiz = {
            "secenekler": [],
            "en_ucuz": None,
            "en_hizli": None,
            "en_az_aktarma": None,
            "odeme_yapilabilir": []
        }
        
        for strateji_adi, rota in tum_secenekler:
            if rota:
                komisyonlu_tutar = odeme_yontemi_obj.komisyonlu_tutar_hesapla(rota.toplam_ucret)
                odeme_yapilabilir = cuzdan.odeme_yapabilir_mi(komisyonlu_tutar, odeme_yontemi)
                
                secenek_bilgi = {
                    "strateji": strateji_adi,
                    "mesafe": rota.toplam_mesafe,
                    "sure": rota.toplam_sure,
                    "ucret": rota.toplam_ucret,
                    "komisyonlu_ucret": komisyonlu_tutar,
                    "aktarma_sayisi": rota.aktarma_sayisi,
                    "odeme_yapilabilir": odeme_yapilabilir,
                    "rota": rota
                }
                
                analiz["secenekler"].append(secenek_bilgi)
                
                if odeme_yapilabilir:
                    analiz["odeme_yapilabilir"].append(secenek_bilgi)
        
        # En iyileri bul
        if analiz["secenekler"]:
            analiz["en_ucuz"] = min(analiz["secenekler"], key=lambda x: x["ucret"])
            analiz["en_hizli"] = min(analiz["secenekler"], key=lambda x: x["sure"])
            analiz["en_az_aktarma"] = min(analiz["secenekler"], 
                                         key=lambda x: (x["aktarma_sayisi"], x["ucret"]))
        
        return analiz

