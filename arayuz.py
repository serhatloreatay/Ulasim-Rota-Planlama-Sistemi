import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Optional, List
from konum import Konum
from yolcu import Yolcu, GenelYolcu, OgrenciYolcu, YasliYolcu, OgretmenYolcu
from rota import RotaHesaplayici, Rota
from taksi import Taksi
from veri_yukleyici import VeriYukleyici
from hat import HatYoneticisi
from rota_secenekleri import RotaSecenekleriUretici
from cuzdan import Cuzdan
from en_uygun_rota_secici import EnUygunRotaSecici


class UlasimArayuzu:
    """Toplu taşıma sistemi kullanıcı arayüzü"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🚌 İzmit Toplu Taşıma Rota Planlayıcı")
        self.root.geometry("1000x900")
        self.root.configure(bg="#f0f4f8")
        
        # Modern renk paleti
        self.renkler = {
            "ana": "#2c3e50",
            "ikincil": "#3498db",
            "basari": "#27ae60",
            "uyari": "#f39c12",
            "hata": "#e74c3c",
            "arka_plan": "#f0f4f8",
            "beyaz": "#ffffff",
            "acik_gri": "#ecf0f1",
            "koyu_gri": "#34495e"
        }
        
        # Modern tema ayarları
        self._modern_tema_ayarla()
        
        # Veri yükleme
        import os
        # Dosya adını bul (encoding sorunları için)
        dosya_yolu = None
        for f in os.listdir('.'):
            if f.endswith('.txt') and ('VER' in f.upper() or 'SET' in f.upper() or 'PROLAB' in f.upper()):
                dosya_yolu = f
                break
        
        if not dosya_yolu:
            messagebox.showerror("Hata", "Veri dosyası bulunamadı!")
            return
        
        self.veri_yukleyici = VeriYukleyici(dosya_yolu)
        if not self.veri_yukleyici.veri_yukle():
            messagebox.showerror("Hata", f"Veri dosyası yüklenemedi!\nDosya: {dosya_yolu}")
            return
        
        self.veri_yukleyici.duraklari_olustur()
        self.hat_yoneticisi = HatYoneticisi(self.veri_yukleyici.duraklar)
        
        # Taksi bilgisi
        taksi_bilgi = self.veri_yukleyici.taksi_bilgisi
        self.taksi = Taksi(
            acilis_ucreti=taksi_bilgi.get("openingFee", 10),
            km_basina_ucret=taksi_bilgi.get("costPerKm", 4)
        )
        
        # Rota hesaplayıcı
        self.rota_hesaplayici = RotaHesaplayici(self.hat_yoneticisi, self.taksi)
        
        # Rota seçenekleri üretici
        self.rota_secenekleri_uretici = RotaSecenekleriUretici(self.hat_yoneticisi, self.taksi)
        
        # En uygun rota seçici
        self.en_uygun_rota_secici = EnUygunRotaSecici(self.rota_secenekleri_uretici)
        
        # Arayüzü oluştur
        self._arayuzu_olustur()
    
    def _modern_tema_ayarla(self):
        """Modern tema ve stil ayarları"""
        style = ttk.Style()
        style.theme_use("clam")
        
        # Modern buton stili
        style.configure("Modern.TButton",
                       padding=10,
                       font=("Segoe UI", 10, "bold"),
                       background=self.renkler["ikincil"],
                       foreground="white",
                       borderwidth=0,
                       focuscolor="none")
        style.map("Modern.TButton",
                 background=[("active", "#2980b9"), ("pressed", "#21618c")])
        
        # Başlık stili
        style.configure("Baslik.TLabel",
                       font=("Segoe UI", 20, "bold"),
                       foreground=self.renkler["ana"],
                       background=self.renkler["arka_plan"])
        
        # Frame stili
        style.configure("Modern.TLabelframe",
                       background=self.renkler["beyaz"],
                       borderwidth=2,
                       relief="flat")
        style.configure("Modern.TLabelframe.Label",
                       font=("Segoe UI", 11, "bold"),
                       foreground=self.renkler["ana"],
                       background=self.renkler["beyaz"])
    
    def _arayuzu_olustur(self):
        """Arayüz bileşenlerini oluştur"""
        # Ana frame
        ana_frame = tk.Frame(self.root, bg=self.renkler["arka_plan"], padx=20, pady=20)
        ana_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Başlık frame (gradient efekti için)
        baslik_frame = tk.Frame(ana_frame, bg=self.renkler["ikincil"], height=80)
        baslik_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        baslik_frame.grid_propagate(False)
        
        # Başlık
        baslik = tk.Label(baslik_frame, 
                         text="🚌 İzmit Toplu Taşıma Rota Planlayıcı",
                         font=("Segoe UI", 22, "bold"),
                         bg=self.renkler["ikincil"],
                         fg="white",
                         pady=20)
        baslik.pack()
        
        # Konum bilgileri frame
        konum_frame = ttk.LabelFrame(ana_frame, text="📍 Konum Bilgileri", 
                                     style="Modern.TLabelframe", padding="15")
        konum_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        konum_frame.configure(style="Modern.TLabelframe")
        
        # Başlangıç konumu
        baslangic_label = tk.Label(konum_frame, text="🚩 Başlangıç Konumu:", 
                                   font=("Segoe UI", 10, "bold"),
                                   bg=self.renkler["beyaz"], fg=self.renkler["koyu_gri"])
        baslangic_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        ttk.Label(konum_frame, text="Enlem:", font=("Segoe UI", 9)).grid(row=1, column=0, sticky=tk.W, padx=5)
        self.baslangic_enlem = tk.Entry(konum_frame, width=18, font=("Segoe UI", 10),
                                       relief="flat", bg=self.renkler["acik_gri"],
                                       borderwidth=1, highlightthickness=1,
                                       highlightbackground=self.renkler["ikincil"])
        self.baslangic_enlem.grid(row=1, column=1, padx=5, pady=5)
        self.baslangic_enlem.insert(0, "40.78259")  # Örnek değer
        
        ttk.Label(konum_frame, text="Boylam:", font=("Segoe UI", 9)).grid(row=1, column=2, sticky=tk.W, padx=(15, 0))
        self.baslangic_boylam = tk.Entry(konum_frame, width=18, font=("Segoe UI", 10),
                                         relief="flat", bg=self.renkler["acik_gri"],
                                         borderwidth=1, highlightthickness=1,
                                         highlightbackground=self.renkler["ikincil"])
        self.baslangic_boylam.grid(row=1, column=3, padx=5, pady=5)
        self.baslangic_boylam.insert(0, "29.94628")  # Örnek değer
        
        # Hedef konumu
        hedef_label = tk.Label(konum_frame, text="🎯 Hedef Konumu:", 
                              font=("Segoe UI", 10, "bold"),
                              bg=self.renkler["beyaz"], fg=self.renkler["koyu_gri"])
        hedef_label.grid(row=2, column=0, sticky=tk.W, pady=(15, 10))
        
        # Hedef tipi seçimi
        ttk.Label(konum_frame, text="Hedef Tipi:", font=("Segoe UI", 9)).grid(row=3, column=0, sticky=tk.W, padx=5)
        self.hedef_tipi = ttk.Combobox(konum_frame, values=["Koordinat", "Durak Adı"], 
                                       state="readonly", width=18, font=("Segoe UI", 9))
        self.hedef_tipi.grid(row=3, column=1, padx=5, pady=5)
        self.hedef_tipi.current(0)  # Koordinat seçili
        self.hedef_tipi.bind("<<ComboboxSelected>>", self._hedef_tipi_degisti)
        
        # Koordinat girişi
        ttk.Label(konum_frame, text="Enlem:", font=("Segoe UI", 9)).grid(row=4, column=0, sticky=tk.W, padx=5)
        self.hedef_enlem = tk.Entry(konum_frame, width=18, font=("Segoe UI", 10),
                                    relief="flat", bg=self.renkler["acik_gri"],
                                    borderwidth=1, highlightthickness=1,
                                    highlightbackground=self.renkler["ikincil"])
        self.hedef_enlem.grid(row=4, column=1, padx=5, pady=5)
        self.hedef_enlem.insert(0, "40.7635")  # Örnek değer
        
        ttk.Label(konum_frame, text="Boylam:", font=("Segoe UI", 9)).grid(row=4, column=2, sticky=tk.W, padx=(15, 0))
        self.hedef_boylam = tk.Entry(konum_frame, width=18, font=("Segoe UI", 10),
                                     relief="flat", bg=self.renkler["acik_gri"],
                                     borderwidth=1, highlightthickness=1,
                                     highlightbackground=self.renkler["ikincil"])
        self.hedef_boylam.grid(row=4, column=3, padx=5, pady=5)
        self.hedef_boylam.insert(0, "29.9387")  # Örnek değer
        
        # Durak seçimi
        durak_listesi = [durak.isim for durak in self.veri_yukleyici.duraklar.values()]
        self.hedef_durak = ttk.Combobox(konum_frame, values=durak_listesi, 
                                       state="readonly", width=40, font=("Segoe UI", 9))
        self.hedef_durak.grid(row=4, column=1, columnspan=3, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.hedef_durak.grid_remove()  # Başlangıçta gizli
        
        # Yolcu bilgileri frame
        yolcu_frame = ttk.LabelFrame(ana_frame, text="👤 Yolcu Bilgileri", 
                                    style="Modern.TLabelframe", padding="15")
        yolcu_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(yolcu_frame, text="Yolcu Tipi:", font=("Segoe UI", 9)).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.yolcu_tipi = ttk.Combobox(yolcu_frame, 
                                      values=["Genel", "Öğrenci", "Öğretmen", "65 Yaş Üstü"], 
                                      state="readonly", width=25, font=("Segoe UI", 9))
        self.yolcu_tipi.grid(row=0, column=1, padx=5, pady=5)
        self.yolcu_tipi.current(0)  # Genel seçili
        
        # Cüzdan bilgileri frame
        cuzdan_frame = ttk.LabelFrame(ana_frame, text="💳 Cüzdan Bilgileri", 
                                     style="Modern.TLabelframe", padding="15")
        cuzdan_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(cuzdan_frame, text="Nakit (TL):", font=("Segoe UI", 9)).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.nakit = tk.Entry(cuzdan_frame, width=18, font=("Segoe UI", 10),
                             relief="flat", bg=self.renkler["acik_gri"],
                             borderwidth=1, highlightthickness=1,
                             highlightbackground=self.renkler["ikincil"])
        self.nakit.grid(row=0, column=1, padx=5, pady=5)
        self.nakit.insert(0, "100")
        
        ttk.Label(cuzdan_frame, text="Kredi Kartı Limiti (TL):", font=("Segoe UI", 9)).grid(row=0, column=2, sticky=tk.W, padx=(15, 0))
        self.kredi_karti = tk.Entry(cuzdan_frame, width=18, font=("Segoe UI", 10),
                                    relief="flat", bg=self.renkler["acik_gri"],
                                    borderwidth=1, highlightthickness=1,
                                    highlightbackground=self.renkler["ikincil"])
        self.kredi_karti.grid(row=0, column=3, padx=5, pady=5)
        self.kredi_karti.insert(0, "500")
        
        ttk.Label(cuzdan_frame, text="Kentkart Bakiyesi (TL):", font=("Segoe UI", 9)).grid(row=1, column=0, sticky=tk.W, padx=5, pady=(10, 0))
        self.kentkart = tk.Entry(cuzdan_frame, width=18, font=("Segoe UI", 10),
                                relief="flat", bg=self.renkler["acik_gri"],
                                borderwidth=1, highlightthickness=1,
                                highlightbackground=self.renkler["ikincil"])
        self.kentkart.grid(row=1, column=1, padx=5, pady=(10, 5))
        self.kentkart.insert(0, "50")
        
        ttk.Label(cuzdan_frame, text="Ödeme Yöntemi:", font=("Segoe UI", 9)).grid(row=1, column=2, sticky=tk.W, padx=(15, 0), pady=(10, 0))
        self.odeme_yontemi = ttk.Combobox(cuzdan_frame, values=["Nakit", "Kredi Kartı", "Kentkart"], 
                                          state="readonly", width=18, font=("Segoe UI", 9))
        self.odeme_yontemi.grid(row=1, column=3, padx=5, pady=(10, 5))
        self.odeme_yontemi.current(0)  # Nakit seçili
        
        # Butonlar
        buton_frame = tk.Frame(ana_frame, bg=self.renkler["arka_plan"])
        buton_frame.grid(row=4, column=0, columnspan=2, pady=15)
        
        # Ana buton (büyük ve vurgulu)
        ana_buton = tk.Button(buton_frame, 
                             text="✨ En Uygun Rotayı Bul",
                             command=self._en_uygun_rotayi_bul,
                             font=("Segoe UI", 11, "bold"),
                             bg=self.renkler["basari"],
                             fg="white",
                             relief="flat",
                             padx=20,
                             pady=12,
                             cursor="hand2",
                             activebackground="#229954",
                             activeforeground="white")
        ana_buton.pack(side=tk.LEFT, padx=5)
        
        # Diğer butonlar
        buton2 = tk.Button(buton_frame,
                          text="🔍 Rota Hesapla",
                          command=self._rota_hesapla,
                          font=("Segoe UI", 10),
                          bg=self.renkler["ikincil"],
                          fg="white",
                          relief="flat",
                          padx=15,
                          pady=10,
                          cursor="hand2",
                          activebackground="#2980b9",
                          activeforeground="white")
        buton2.pack(side=tk.LEFT, padx=5)
        
        buton3 = tk.Button(buton_frame,
                          text="📊 Tüm Seçenekleri Göster",
                          command=self._tum_secenekleri_goster,
                          font=("Segoe UI", 10),
                          bg=self.renkler["uyari"],
                          fg="white",
                          relief="flat",
                          padx=15,
                          pady=10,
                          cursor="hand2",
                          activebackground="#d68910",
                          activeforeground="white")
        buton3.pack(side=tk.LEFT, padx=5)
        
        buton4 = tk.Button(buton_frame,
                          text="💰 Fiyat Karşılaştır",
                          command=self._fiyat_karsilastir,
                          font=("Segoe UI", 10),
                          bg=self.renkler["koyu_gri"],
                          fg="white",
                          relief="flat",
                          padx=15,
                          pady=10,
                          cursor="hand2",
                          activebackground="#2c3e50",
                          activeforeground="white")
        buton4.pack(side=tk.LEFT, padx=5)
        
        buton5 = tk.Button(buton_frame,
                          text="🗑️ Temizle",
                          command=self._temizle,
                          font=("Segoe UI", 10),
                          bg=self.renkler["hata"],
                          fg="white",
                          relief="flat",
                          padx=15,
                          pady=10,
                          cursor="hand2",
                          activebackground="#c0392b",
                          activeforeground="white")
        buton5.pack(side=tk.LEFT, padx=5)
        
        # Sonuçlar frame
        sonuc_frame = ttk.LabelFrame(ana_frame, text="📋 Rota Detayları", 
                                     style="Modern.TLabelframe", padding="15")
        sonuc_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Özet bilgiler (modern text widget)
        self.ozet_text = scrolledtext.ScrolledText(sonuc_frame, 
                                                  height=20, 
                                                  width=90, 
                                                  wrap=tk.WORD,
                                                  font=("Consolas", 10),
                                                  bg="#ffffff",
                                                  fg="#2c3e50",
                                                  relief="flat",
                                                  borderwidth=2,
                                                  highlightthickness=1,
                                                  highlightbackground=self.renkler["ikincil"],
                                                  padx=10,
                                                  pady=10)
        self.ozet_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Grid ağırlıkları
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        ana_frame.columnconfigure(0, weight=1)
        ana_frame.rowconfigure(5, weight=1)
        sonuc_frame.columnconfigure(0, weight=1)
        sonuc_frame.rowconfigure(0, weight=1)
    
    def _hedef_tipi_degisti(self, event=None):
        """Hedef tipi değiştiğinde arayüzü güncelle"""
        if self.hedef_tipi.get() == "Koordinat":
            # Koordinat girişlerini göster
            self.hedef_enlem.grid()
            self.hedef_boylam.grid()
            self.hedef_durak.grid_remove()
        else:
            # Durak seçimini göster
            self.hedef_enlem.grid_remove()
            self.hedef_boylam.grid_remove()
            self.hedef_durak.grid()
    
    def _hedef_konumu_al(self) -> Optional[Konum]:
        """Hedef konumu al (koordinat veya durak adından)"""
        try:
            if self.hedef_tipi.get() == "Koordinat":
                try:
                    hedef_enlem_str = self.hedef_enlem.get().strip() if hasattr(self.hedef_enlem, 'get') else ""
                    hedef_boylam_str = self.hedef_boylam.get().strip() if hasattr(self.hedef_boylam, 'get') else ""
                    
                    if not hedef_enlem_str or not hedef_boylam_str:
                        return None
                    
                    hedef_enlem = float(hedef_enlem_str)
                    hedef_boylam = float(hedef_boylam_str)
                    return Konum(hedef_enlem, hedef_boylam, "Hedef")
                except (ValueError, AttributeError, tk.TclError):
                    return None
            else:
                # Durak adından konum bul
                try:
                    durak_adi = self.hedef_durak.get().strip() if hasattr(self.hedef_durak, 'get') else ""
                    if not durak_adi:
                        return None
                    for durak_id, durak in self.veri_yukleyici.duraklar.items():
                        if durak.isim == durak_adi:
                            return Konum(durak.enlem, durak.boylam, durak.isim)
                    return None
                except (AttributeError, tk.TclError):
                    return None
        except Exception:
            return None
    
    def _en_uygun_rotayi_bul(self):
        """En uygun rotayı bul (cüzdan ve ödeme kontrolü ile)"""
        try:
            # Konum bilgilerini al
            try:
                baslangic_enlem_str = (self.baslangic_enlem.get() or "").strip()
                baslangic_boylam_str = (self.baslangic_boylam.get() or "").strip()
                
                if not baslangic_enlem_str or not baslangic_boylam_str:
                    messagebox.showerror("Hata", "Lütfen başlangıç konum bilgilerini girin!")
                    return
                
                baslangic_enlem = float(baslangic_enlem_str)
                baslangic_boylam = float(baslangic_boylam_str)
            except (ValueError, AttributeError, tk.TclError) as e:
                messagebox.showerror("Hata", f"Başlangıç konum bilgilerinde hata: {str(e)}")
                return
            baslangic_konum = Konum(baslangic_enlem, baslangic_boylam, "Başlangıç")
            
            hedef_konum = self._hedef_konumu_al()
            if not hedef_konum:
                if self.hedef_tipi.get() == "Koordinat":
                    messagebox.showerror("Hata", "Lütfen geçerli hedef konum koordinatlarını girin!")
                else:
                    messagebox.showerror("Hata", "Lütfen bir durak seçin!")
                return
            
            # Cüzdan bilgilerini al
            try:
                nakit_str = (self.nakit.get() or "").strip() or "0"
                kredi_karti_str = (self.kredi_karti.get() or "").strip() or "0"
                kentkart_str = (self.kentkart.get() or "").strip() or "0"
                
                nakit = float(nakit_str) if nakit_str else 0.0
                kredi_karti = float(kredi_karti_str) if kredi_karti_str else 0.0
                kentkart = float(kentkart_str) if kentkart_str else 0.0
            except (ValueError, AttributeError, tk.TclError) as e:
                messagebox.showerror("Hata", f"Cüzdan bilgilerinde hata: {str(e)}")
                return
            cuzdan = Cuzdan(nakit=nakit, kredi_karti_limiti=kredi_karti, 
                           kentkart_bakiyesi=kentkart)
            
            # Ödeme yöntemi
            odeme_yontemi_map = {
                "Nakit": "nakit",
                "Kredi Kartı": "kredi_karti",
                "Kentkart": "kentkart"
            }
            odeme_yontemi = odeme_yontemi_map.get(self.odeme_yontemi.get(), "nakit")
            
            # En uygun rotayı bul
            en_uygun_rota, tum_secenekler = self.en_uygun_rota_secici.en_uygun_rotayi_bul(
                baslangic_konum, hedef_konum, cuzdan, odeme_yontemi, "maliyet"
            )
            
            # Sonuçları göster
            self._en_uygun_rota_goster(en_uygun_rota, tum_secenekler, cuzdan, odeme_yontemi)
        
        except ValueError as e:
            messagebox.showerror("Hata", f"Geçersiz sayısal değer: {str(e)}\nLütfen tüm alanları kontrol edin!")
        except AttributeError as e:
            messagebox.showerror("Hata", f"Arayüz hatası: {str(e)}")
        except Exception as e:
            messagebox.showerror("Hata", f"Bir hata oluştu: {str(e)}")
            import traceback
            print(traceback.format_exc())
    
    def _en_uygun_rota_goster(self, en_uygun_rota: Optional[Rota], 
                             tum_secenekler: List, cuzdan: Cuzdan, odeme_yontemi: str):
        """En uygun rota sonuçlarını göster - detaylı format"""
        self.ozet_text.delete(1.0, tk.END)
        
        # Başlangıç konumuna en yakın durak
        try:
            baslangic_enlem = float(self.baslangic_enlem.get())
            baslangic_boylam = float(self.baslangic_boylam.get())
            baslangic_konum = Konum(baslangic_enlem, baslangic_boylam, "Başlangıç")
            
            from mesafe_hesaplayici import MesafeHesaplayici
            en_yakin_durak_id, mesafe = self.rota_hesaplayici._en_yakin_durak_bul(
                baslangic_konum.enlem, baslangic_konum.boylam
            )
            
            if en_yakin_durak_id:
                durak = self.hat_yoneticisi.durak_getir(en_yakin_durak_id)
                mesafe_metre = mesafe * 1000
                self.ozet_text.insert(tk.END, "🔴 KULLANICI KONUMUNA EN YAKIN DURAK:\n")
                self.ozet_text.insert(tk.END, f"📍 {durak.isim} ({mesafe_metre:.0f} m)\n")
                if mesafe <= 3.0:
                    self.ozet_text.insert(tk.END, f"🚶 Yürüme = 0 TL\n")
                else:
                    taksi_ucret = self.taksi.ucret_hesapla(mesafe)
                    self.ozet_text.insert(tk.END, f"🚕 Taksi = {taksi_ucret:.2f} TL\n")
                self.ozet_text.insert(tk.END, "\n" + "=" * 70 + "\n\n")
        except:
            pass
        
        # En uygun rota detayları
        if en_uygun_rota:
            self.ozet_text.insert(tk.END, "🔵 ROTA DETAYLARI:\n\n")
            self._detayli_rota_goster(en_uygun_rota)
            
            # Toplam
            self.ozet_text.insert(tk.END, "\n" + "=" * 70 + "\n")
            self.ozet_text.insert(tk.END, "📊 TOPLAM:\n")
            self.ozet_text.insert(tk.END, f"💰 Ücret: {en_uygun_rota.toplam_ucret:.2f} TL\n")
            
            # Yolcu indirimi varsa göster
            yolcu_tipi = self.yolcu_tipi.get()
            if yolcu_tipi != "Genel":
                from yolcu import OgrenciYolcu, OgretmenYolcu, YasliYolcu
                yolcu_map = {
                    "Öğrenci": OgrenciYolcu(),
                    "Öğretmen": OgretmenYolcu(),
                    "65 Yaş Üstü": YasliYolcu()
                }
                yolcu = yolcu_map.get(yolcu_tipi)
                if yolcu:
                    indirimli_ucret = yolcu.indirimli_ucret_hesapla(en_uygun_rota.toplam_ucret)
                    indirim_miktari = en_uygun_rota.toplam_ucret - indirimli_ucret
                    indirim_yuzdesi = yolcu.indirim_orani() * 100
                    self.ozet_text.insert(tk.END, f"   ({yolcu_tipi} %{indirim_yuzdesi:.0f} → {indirimli_ucret:.2f} TL)\n")
            
            self.ozet_text.insert(tk.END, f"⏱️  Süre: {en_uygun_rota.toplam_sure:.1f} dk\n")
            self.ozet_text.insert(tk.END, f"📏 Mesafe: {en_uygun_rota.toplam_mesafe:.2f} km\n")
            self.ozet_text.insert(tk.END, f"🔄 Aktarma Sayısı: {en_uygun_rota.aktarma_sayisi}\n")
        
        # Alternatif rotalar
        self.ozet_text.insert(tk.END, "\n" + "=" * 70 + "\n")
        self.ozet_text.insert(tk.END, "🌳 ALTERNATİF ROTALAR:\n\n")
        self._alternatif_rotalari_goster(tum_secenekler, cuzdan, odeme_yontemi)
    
    def _detayli_rota_goster(self, rota: Rota):
        """Detaylı rota gösterimi - örnek çıktı formatına uygun"""
        yolcu_tipi = self.yolcu_tipi.get()
        
        for i, adim in enumerate(rota.adimlar, 1):
            # Başlangıç ve hedef
            baslangic = adim.baslangic if adim.baslangic != "konum" else "Konum"
            hedef = adim.hedef if adim.hedef != "konum" else "Konum"
            
            # Durak isimlerini al
            if adim.baslangic != "konum":
                baslangic_durak = self.hat_yoneticisi.durak_getir(adim.baslangic)
                baslangic = baslangic_durak.isim if baslangic_durak else adim.baslangic
            
            if adim.hedef != "konum":
                hedef_durak = self.hat_yoneticisi.durak_getir(adim.hedef)
                hedef = hedef_durak.isim if hedef_durak else adim.hedef
            
            # İkon seçimi
            if adim.ulasim_tipi == "otobus":
                ikon = "🚌"
                tasima_adi = "Otobüs"
            elif adim.ulasim_tipi == "tramvay":
                ikon = "🚊"
                tasima_adi = "Tramvay"
            elif adim.ulasim_tipi == "taksi":
                ikon = "🚕"
                tasima_adi = "Taksi"
            elif adim.ulasim_tipi == "aktarma":
                ikon = "🔄"
                tasima_adi = "Aktarma"
            else:
                ikon = "🚶"
                tasima_adi = "Yürüme"
            
            self.ozet_text.insert(tk.END, f"{i}. {baslangic} → {hedef} ({ikon} {tasima_adi})\n")
            
            # Süre
            self.ozet_text.insert(tk.END, f"   ⏱️  Süre: {adim.sure:.0f} dk\n")
            
            # Ücret
            if adim.ucret > 0:
                ucret_metni = f"   💰 Ücret: {adim.ucret:.2f} TL"
                
                # Yolcu indirimi göster
                if yolcu_tipi != "Genel" and adim.ulasim_tipi in ["otobus", "tramvay", "aktarma"]:
                    from yolcu import OgrenciYolcu, OgretmenYolcu, YasliYolcu
                    yolcu_map = {
                        "Öğrenci": OgrenciYolcu(),
                        "Öğretmen": OgretmenYolcu(),
                        "65 Yaş Üstü": YasliYolcu()
                    }
                    yolcu = yolcu_map.get(yolcu_tipi)
                    if yolcu:
                        indirimli = yolcu.indirimli_ucret_hesapla(adim.ucret)
                        indirim_yuzdesi = yolcu.indirim_orani() * 100
                        ucret_metni += f" ({yolcu_tipi} %{indirim_yuzdesi:.0f} → {indirimli:.2f} TL)"
                
                self.ozet_text.insert(tk.END, ucret_metni + "\n")
            elif adim.ucret == 0:
                self.ozet_text.insert(tk.END, f"   💰 Ücret: 0 TL\n")
            else:
                # Negatif ücret (teşvik)
                self.ozet_text.insert(tk.END, f"   💰 Teşvik: {abs(adim.ucret):.2f} TL iade\n")
            
            # Mesafe (varsa)
            if adim.mesafe > 0:
                self.ozet_text.insert(tk.END, f"   📏 Mesafe: {adim.mesafe:.2f} km\n")
            
            self.ozet_text.insert(tk.END, "\n")
    
    def _alternatif_rotalari_goster(self, tum_secenekler: List, cuzdan: Cuzdan, odeme_yontemi: str):
        """Alternatif rotaları detaylı göster"""
        from odeme import NakitOdeme, KrediKartiOdeme, KentkartOdeme
        
        odeme_yontemi_map = {
            "nakit": NakitOdeme(),
            "kredi_karti": KrediKartiOdeme(),
            "kentkart": KentkartOdeme()
        }
        odeme_obj = odeme_yontemi_map.get(odeme_yontemi, NakitOdeme())
        
        alternatif_aciklamalari = {
            "Sadece Taksi": "Daha hızlı, ancak maliyetli",
            "Sadece Otobüs": "Daha uygun maliyetli, ancak daha uzun sürebilir",
            "Sadece Tramvay": "Rahat ve dengeli bir ulaşım seçeneği",
            "Otobüs + Tramvay Aktarması": "Aktarma ile entegre ulaşım - en az aktarmalı rota",
            "Taksi + Otobüs/Tramvay Kombinasyonu": "Daha hızlı, ancak maliyetli"
        }
        
        for secenek in tum_secenekler:
            # Handle both 2-value and 3-value tuples
            if len(secenek) == 3:
                strateji_adi, rota, odeme_yapilabilir = secenek
            elif len(secenek) == 2:
                strateji_adi, rota = secenek
                # Calculate payment status if not provided
                if rota:
                    komisyonlu_tutar = odeme_obj.komisyonlu_tutar_hesapla(rota.toplam_ucret)
                    odeme_yapilabilir = cuzdan.odeme_yapabilir_mi(komisyonlu_tutar, odeme_yontemi)
                else:
                    odeme_yapilabilir = False
                    komisyonlu_tutar = 0.0
            else:
                continue  # Skip invalid entries
            if rota:
                durum_ikon = "✓" if odeme_yapilabilir else "✗"
                durum_metin = "Ödeme Yapılabilir" if odeme_yapilabilir else "Yetersiz Bakiye"
                
                # Calculate komisyonlu_tutar if not already calculated (for 3-value tuples)
                if len(secenek) == 3:
                    komisyonlu_tutar = odeme_obj.komisyonlu_tutar_hesapla(rota.toplam_ucret)
                
                self.ozet_text.insert(tk.END, f"💎 {strateji_adi}\n")
                self.ozet_text.insert(tk.END, f"   {durum_ikon} {durum_metin}\n")
                self.ozet_text.insert(tk.END, f"   💰 Ücret: {rota.toplam_ucret:.2f} TL")
                if odeme_yontemi != "nakit":
                    self.ozet_text.insert(tk.END, f" (Komisyon dahil: {komisyonlu_tutar:.2f} TL)")
                self.ozet_text.insert(tk.END, "\n")
                self.ozet_text.insert(tk.END, f"   ⏱️  Süre: {rota.toplam_sure:.1f} dk\n")
                self.ozet_text.insert(tk.END, f"   📏 Mesafe: {rota.toplam_mesafe:.2f} km\n")
                self.ozet_text.insert(tk.END, f"   🔄 Aktarma: {rota.aktarma_sayisi}\n")
                
                aciklama = alternatif_aciklamalari.get(strateji_adi, "")
                if aciklama:
                    self.ozet_text.insert(tk.END, f"   📝 {aciklama}\n")
                
                self.ozet_text.insert(tk.END, "\n")
            else:
                self.ozet_text.insert(tk.END, f"💎 {strateji_adi}\n")
                self.ozet_text.insert(tk.END, f"   ⚠ Bu rota seçeneği mevcut değil.\n\n")
    
    def _rota_hesapla(self):
        """Rota hesaplama işlemini gerçekleştir"""
        try:
            # Konum bilgilerini al
            try:
                baslangic_enlem_str = (self.baslangic_enlem.get() or "").strip()
                baslangic_boylam_str = (self.baslangic_boylam.get() or "").strip()
                
                if not baslangic_enlem_str or not baslangic_boylam_str:
                    messagebox.showerror("Hata", "Lütfen başlangıç konum bilgilerini girin!")
                    return
                
                baslangic_enlem = float(baslangic_enlem_str)
                baslangic_boylam = float(baslangic_boylam_str)
            except (ValueError, AttributeError, tk.TclError) as e:
                messagebox.showerror("Hata", f"Başlangıç konum bilgilerinde hata: {str(e)}")
                return
            baslangic_konum = Konum(baslangic_enlem, baslangic_boylam, "Başlangıç")
            
            hedef_konum = self._hedef_konumu_al()
            if not hedef_konum:
                if self.hedef_tipi.get() == "Koordinat":
                    messagebox.showerror("Hata", "Lütfen geçerli hedef konum koordinatlarını girin!")
                else:
                    messagebox.showerror("Hata", "Lütfen bir durak seçin!")
                return
            
            # Yolcu tipi
            yolcu_tipi_secim = self.yolcu_tipi.get()
            yolcu_tipi_map = {
                "Genel": "genel",
                "Öğrenci": "ogrenci",
                "Öğretmen": "ogretmen",
                "65 Yaş Üstü": "yasli"
            }
            yolcu_tipi = yolcu_tipi_map.get(yolcu_tipi_secim, "genel")
            
            # Rota hesapla
            rota = self.rota_hesaplayici.en_uygun_rota_bul(
                baslangic_konum, hedef_konum, yolcu_tipi
            )
            
            if rota:
                # Tüm seçenekleri al
                tum_secenekler = self.rota_secenekleri_uretici.tum_rota_secenekleri_olustur(
                    baslangic_konum, hedef_konum
                )
                
                # Cüzdan bilgileri (varsayılan)
                cuzdan = Cuzdan(nakit=1000, kredi_karti_limiti=5000, kentkart_bakiyesi=500)
                
                # Detaylı gösterim
                self._en_uygun_rota_goster(rota, tum_secenekler, cuzdan, "nakit")
            else:
                messagebox.showwarning("Uyarı", "Rota bulunamadı!")
                self.ozet_text.delete(1.0, tk.END)
                self.ozet_text.insert(tk.END, "Rota bulunamadı. Lütfen geçerli konumlar girin.")
        
        except ValueError as e:
            messagebox.showerror("Hata", f"Geçersiz sayısal değer: {str(e)}\nLütfen tüm alanları kontrol edin!")
        except AttributeError as e:
            messagebox.showerror("Hata", f"Arayüz hatası: {str(e)}")
        except Exception as e:
            messagebox.showerror("Hata", f"Bir hata oluştu: {str(e)}")
            import traceback
            print(traceback.format_exc())
    
    def _rota_goster(self, rota: Rota, yolcu_tipi: str):
        """Rota bilgilerini göster"""
        self.ozet_text.delete(1.0, tk.END)
        
        # Özet bilgiler
        self.ozet_text.insert(tk.END, "=" * 70 + "\n")
        self.ozet_text.insert(tk.END, "ROTA ÖZETİ\n")
        self.ozet_text.insert(tk.END, "=" * 70 + "\n\n")
        
        self.ozet_text.insert(tk.END, f"Yolcu Tipi: {yolcu_tipi}\n")
        self.ozet_text.insert(tk.END, f"Toplam Mesafe: {rota.toplam_mesafe:.2f} km\n")
        self.ozet_text.insert(tk.END, f"Toplam Süre: {rota.toplam_sure:.1f} dakika\n")
        self.ozet_text.insert(tk.END, f"Toplam Ücret: {rota.toplam_ucret:.2f} TL\n")
        self.ozet_text.insert(tk.END, f"Aktarma Sayısı: {rota.aktarma_sayisi}\n")
        self.ozet_text.insert(tk.END, "\n" + "-" * 70 + "\n\n")
        
        # Detaylı adımlar
        self.ozet_text.insert(tk.END, "DETAYLI ROTA ADIMLARI:\n\n")
        
        for i, adim in enumerate(rota.adimlar, 1):
            self.ozet_text.insert(tk.END, f"Adım {i}: {adim.aciklama}\n")
            self.ozet_text.insert(tk.END, f"  → Ulaşım Tipi: {adim.ulasim_tipi.upper()}\n")
            if adim.mesafe > 0:
                self.ozet_text.insert(tk.END, f"  → Mesafe: {adim.mesafe:.2f} km\n")
            self.ozet_text.insert(tk.END, f"  → Süre: {adim.sure:.1f} dakika\n")
            
            # Ücret bilgisi - indirim varsa göster
            if adim.orijinal_ucret is not None and adim.orijinal_ucret != adim.ucret:
                # İndirim uygulandı
                if adim.ucret < 0:
                    self.ozet_text.insert(tk.END, f"  → Ücret: {adim.orijinal_ucret:.2f} TL → "
                                         f"Teşvik: {abs(adim.ucret):.2f} TL iade\n")
                else:
                    indirim_miktari = adim.orijinal_ucret - adim.ucret
                    self.ozet_text.insert(tk.END, f"  → Ücret: {adim.orijinal_ucret:.2f} TL "
                                         f"(İndirim: -{indirim_miktari:.2f} TL) = {adim.ucret:.2f} TL\n")
                if adim.indirim_aciklama:
                    self.ozet_text.insert(tk.END, f"  → {adim.indirim_aciklama}\n")
            elif adim.ucret > 0:
                self.ozet_text.insert(tk.END, f"  → Ücret: {adim.ucret:.2f} TL\n")
            elif adim.ucret < 0:
                self.ozet_text.insert(tk.END, f"  → Teşvik: {abs(adim.ucret):.2f} TL iade\n")
            self.ozet_text.insert(tk.END, "\n")
        
        self.ozet_text.insert(tk.END, "=" * 70 + "\n")
    
    def _fiyat_karsilastir(self):
        """Farklı yolcu tipleri için fiyat karşılaştırması yap"""
        try:
            # Konum bilgilerini al
            try:
                baslangic_enlem_str = (self.baslangic_enlem.get() or "").strip()
                baslangic_boylam_str = (self.baslangic_boylam.get() or "").strip()
                
                if not baslangic_enlem_str or not baslangic_boylam_str:
                    messagebox.showerror("Hata", "Lütfen başlangıç konum bilgilerini girin!")
                    return
                
                baslangic_enlem = float(baslangic_enlem_str)
                baslangic_boylam = float(baslangic_boylam_str)
            except (ValueError, AttributeError, tk.TclError) as e:
                messagebox.showerror("Hata", f"Başlangıç konum bilgilerinde hata: {str(e)}")
                return
            baslangic_konum = Konum(baslangic_enlem, baslangic_boylam, "Başlangıç")
            
            hedef_konum = self._hedef_konumu_al()
            if not hedef_konum:
                if self.hedef_tipi.get() == "Koordinat":
                    messagebox.showerror("Hata", "Lütfen geçerli hedef konum koordinatlarını girin!")
                else:
                    messagebox.showerror("Hata", "Lütfen bir durak seçin!")
                return
            
            # Tüm yolcu tipleri için rota hesapla
            yolcu_tipleri = {
                "Genel": "genel",
                "Öğrenci": "ogrenci",
                "Öğretmen": "ogretmen",
                "65 Yaş Üstü": "yasli"
            }
            
            self.ozet_text.delete(1.0, tk.END)
            self.ozet_text.insert(tk.END, "=" * 70 + "\n")
            self.ozet_text.insert(tk.END, "FİYAT KARŞILAŞTIRMASI\n")
            self.ozet_text.insert(tk.END, "=" * 70 + "\n\n")
            
            rotalar = {}
            for yolcu_adi, yolcu_kodu in yolcu_tipleri.items():
                rota = self.rota_hesaplayici.en_uygun_rota_bul(
                    baslangic_konum, hedef_konum, yolcu_kodu
                )
                if rota:
                    rotalar[yolcu_adi] = rota
            
            if not rotalar:
                self.ozet_text.insert(tk.END, "Rota bulunamadı!\n")
                return
            
            # Karşılaştırma tablosu
            self.ozet_text.insert(tk.END, f"{'Yolcu Tipi':<20} {'Ücret (TL)':<15} {'İndirim':<15} {'Süre (dk)':<15}\n")
            self.ozet_text.insert(tk.END, "-" * 70 + "\n")
            
            genel_ucret = rotalar.get("Genel", None)
            if genel_ucret:
                genel_ucret = genel_ucret.toplam_ucret
            
            for yolcu_adi in ["Genel", "Öğrenci", "Öğretmen", "65 Yaş Üstü"]:
                if yolcu_adi in rotalar:
                    rota = rotalar[yolcu_adi]
                    indirim = 0.0
                    if genel_ucret and yolcu_adi != "Genel":
                        indirim = ((genel_ucret - rota.toplam_ucret) / genel_ucret) * 100
                    
                    indirim_str = f"%{indirim:.1f}" if indirim > 0 else "-"
                    self.ozet_text.insert(tk.END, 
                        f"{yolcu_adi:<20} {rota.toplam_ucret:<15.2f} {indirim_str:<15} {rota.toplam_sure:<15.1f}\n")
            
            self.ozet_text.insert(tk.END, "\n" + "=" * 70 + "\n")
            self.ozet_text.insert(tk.END, f"\nToplam Mesafe: {list(rotalar.values())[0].toplam_mesafe:.2f} km\n")
            self.ozet_text.insert(tk.END, f"Aktarma Sayısı: {list(rotalar.values())[0].aktarma_sayisi}\n")
        
        except ValueError as e:
            messagebox.showerror("Hata", f"Geçersiz sayısal değer: {str(e)}\nLütfen tüm alanları kontrol edin!")
        except AttributeError as e:
            messagebox.showerror("Hata", f"Arayüz hatası: {str(e)}")
        except Exception as e:
            messagebox.showerror("Hata", f"Bir hata oluştu: {str(e)}")
            import traceback
            print(traceback.format_exc())
    
    def _tum_secenekleri_goster(self):
        """Tüm rota seçeneklerini göster"""
        try:
            # Konum bilgilerini al
            try:
                baslangic_enlem_str = (self.baslangic_enlem.get() or "").strip()
                baslangic_boylam_str = (self.baslangic_boylam.get() or "").strip()
                
                if not baslangic_enlem_str or not baslangic_boylam_str:
                    messagebox.showerror("Hata", "Lütfen başlangıç konum bilgilerini girin!")
                    return
                
                baslangic_enlem = float(baslangic_enlem_str)
                baslangic_boylam = float(baslangic_boylam_str)
            except (ValueError, AttributeError, tk.TclError) as e:
                messagebox.showerror("Hata", f"Başlangıç konum bilgilerinde hata: {str(e)}")
                return
            baslangic_konum = Konum(baslangic_enlem, baslangic_boylam, "Başlangıç")
            
            hedef_konum = self._hedef_konumu_al()
            if not hedef_konum:
                if self.hedef_tipi.get() == "Koordinat":
                    messagebox.showerror("Hata", "Lütfen geçerli hedef konum koordinatlarını girin!")
                else:
                    messagebox.showerror("Hata", "Lütfen bir durak seçin!")
                return
            
            # Tüm rota seçeneklerini oluştur
            secenekler = self.rota_secenekleri_uretici.tum_rota_secenekleri_olustur(
                baslangic_konum, hedef_konum
            )
            
            # Cüzdan bilgileri (varsayılan)
            cuzdan = Cuzdan(nakit=1000, kredi_karti_limiti=5000, kentkart_bakiyesi=500)
            
            self.ozet_text.delete(1.0, tk.END)
            self.ozet_text.insert(tk.END, "=" * 70 + "\n")
            self.ozet_text.insert(tk.END, "TÜM ROTA SEÇENEKLERİ - DETAYLI KARŞILAŞTIRMA\n")
            self.ozet_text.insert(tk.END, "=" * 70 + "\n\n")
            
            # Her seçenek için detaylı gösterim
            for i, (strateji_adi, rota) in enumerate(secenekler, 1):
                self.ozet_text.insert(tk.END, f"\n{'=' * 70}\n")
                self.ozet_text.insert(tk.END, f"{i}. {strateji_adi}\n")
                self.ozet_text.insert(tk.END, f"{'=' * 70}\n\n")
                
                if rota:
                    # En yakın durak
                    try:
                        from mesafe_hesaplayici import MesafeHesaplayici
                        en_yakin_durak_id, mesafe = self.rota_hesaplayici._en_yakin_durak_bul(
                            baslangic_konum.enlem, baslangic_konum.boylam
                        )
                        
                        if en_yakin_durak_id:
                            durak = self.hat_yoneticisi.durak_getir(en_yakin_durak_id)
                            mesafe_metre = mesafe * 1000
                            self.ozet_text.insert(tk.END, f"🔴 En Yakın Durak: {durak.isim} ({mesafe_metre:.0f} m)\n")
                            if mesafe <= 3.0:
                                self.ozet_text.insert(tk.END, f"🚶 Yürüme = 0 TL\n\n")
                            else:
                                taksi_ucret = self.taksi.ucret_hesapla(mesafe)
                                self.ozet_text.insert(tk.END, f"🚕 Taksi = {taksi_ucret:.2f} TL\n\n")
                    except:
                        pass
                    
                    # Rota detayları
                    self.ozet_text.insert(tk.END, "🔵 Rota Detayları:\n\n")
                    self._detayli_rota_goster(rota)
                    
                    # Toplam
                    self.ozet_text.insert(tk.END, "\n📊 Toplam:\n")
                    self.ozet_text.insert(tk.END, f"   💰 Ücret: {rota.toplam_ucret:.2f} TL\n")
                    
                    # Yolcu indirimi varsa göster
                    yolcu_tipi = self.yolcu_tipi.get()
                    if yolcu_tipi != "Genel":
                        from yolcu import OgrenciYolcu, OgretmenYolcu, YasliYolcu
                        yolcu_map = {
                            "Öğrenci": OgrenciYolcu(),
                            "Öğretmen": OgretmenYolcu(),
                            "65 Yaş Üstü": YasliYolcu()
                        }
                        yolcu = yolcu_map.get(yolcu_tipi)
                        if yolcu:
                            indirimli_ucret = yolcu.indirimli_ucret_hesapla(rota.toplam_ucret)
                            indirim_yuzdesi = yolcu.indirim_orani() * 100
                            self.ozet_text.insert(tk.END, f"   ({yolcu_tipi} %{indirim_yuzdesi:.0f} → {indirimli_ucret:.2f} TL)\n")
                    
                    self.ozet_text.insert(tk.END, f"   ⏱️  Süre: {rota.toplam_sure:.1f} dk\n")
                    self.ozet_text.insert(tk.END, f"   📏 Mesafe: {rota.toplam_mesafe:.2f} km\n")
                    self.ozet_text.insert(tk.END, f"   🔄 Aktarma: {rota.aktarma_sayisi}\n")
                else:
                    self.ozet_text.insert(tk.END, "  ⚠ Bu rota seçeneği mevcut değil.\n")
            
            self.ozet_text.insert(tk.END, "\n" + "=" * 70 + "\n")
        
        except ValueError as e:
            messagebox.showerror("Hata", f"Geçersiz sayısal değer: {str(e)}\nLütfen tüm alanları kontrol edin!")
        except AttributeError as e:
            messagebox.showerror("Hata", f"Arayüz hatası: {str(e)}")
        except Exception as e:
            messagebox.showerror("Hata", f"Bir hata oluştu: {str(e)}")
            import traceback
            print(traceback.format_exc())
    
    def _temizle(self):
        """Arayüzü temizle"""
        self.baslangic_enlem.delete(0, tk.END)
        self.baslangic_boylam.delete(0, tk.END)
        self.hedef_enlem.delete(0, tk.END)
        self.hedef_boylam.delete(0, tk.END)
        self.yolcu_tipi.current(0)
        self.ozet_text.delete(1.0, tk.END)


def main():
    """Ana fonksiyon"""
    root = tk.Tk()
    app = UlasimArayuzu(root)
    root.mainloop()


if __name__ == "__main__":
    main()

