import streamlit as st
from google import genai
from google.genai import types

# --- 1. SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Işıklı Eğitim Asistanı", layout="wide", page_icon="🎓")

# --- 2. API ANAHTARI VE CLIENT KURULUMU ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    client = genai.Client(api_key=api_key)
except Exception:
    st.error("API Anahtarı bulunamadı! Lütfen Streamlit Secrets (GOOGLE_API_KEY) ayarlarını kontrol edin.")
    st.stop()

# --- 3. MEB MAARİF MODELİ DERS LİSTELERİ ---
MEB_DERSLERI = {
    "İlkokul": [
        "Türkçe", "Matematik", "Hayat Bilgisi", "Fen Bilimleri", 
        "Sosyal Bilgiler", "İngilizce", "Din Kültürü ve Ahlak Bilgisi",
        "Görsel Sanatlar", "Müzik", "Oyun ve Fiziki Etkinlikler", "İnsan Hakları, Yurttaşlık ve Demokrasi"
    ],
    "Ortaokul": [
        "Türkçe", "Matematik", "Fen Bilimleri", "Sosyal Bilgiler", 
        "T.C. İnkılap Tarihi ve Atatürkçülük", "İngilizce", "Din Kültürü ve Ahlak Bilgisi",
        "Bilişim Teknolojileri ve Yazılım", "Teknoloji ve Tasarım", "Görsel Sanatlar", "Müzik", "Beden Eğitimi ve Spor"
    ],
    "Lise (9-12)": [
        "Türk Dili ve Edebiyatı", "Matematik", "Fizik", "Kimya", "Biyoloji", 
        "Tarih", "Coğrafya", "Felsefe", "İngilizce", "İkinci Yabancı Dil (Almanca/Fransızca)",
        "Din Kültürü ve Ahlak Bilgisi", "Beden Eğitimi ve Spor", "Görsel Sanatlar/Müzik",
        "Bilgisayar Bilimi / Bilişim Teknolojileri", "Sağlık Bilgisi ve Trafik Kültürü"
    ]
}

# --- 4. KURUMSAL HAFIZA VE SİSTEM TALİMATI ---
IDP_ORNEKLERI = """
- Beden Eğitimi: WorldWall + Quizizz (Disiplinler arası)
- Müzik: Sibelius + Studio One (Dijital kayıt)
- Biyoloji: Canva + ChatGPT + Gamma (Yapay Zeka Sunum)
- Fizik: PhET Simulations (İnteraktif Laboratuvar)
- Türk Dili: Canva Poster (Dilimizin Zenginlikleri)
"""

gem_talimatlari = f"""
Sen Işık Okulları Eğitim Teknolojileri Koordinatörüsün.
GÖREV: Işık Dijital Pasaport (IDP) felsefesine uygun, Türkiye Yüzyılı Maarif Modeli kazanımlarıyla uyumlu ders planı hazırla.

IDP FELSEFESİ:
- Dijital vatandaşlık, 21. yy becerileri, UDL (Farklılaştırılmış öğretim).
- Teknoloji süs değil, öğrenme aracıdır.

ZORUNLU BAŞLIKLAR:
1. Seviye
2. Ders
3. Teknoloji Bağlantısı (Neden teknoloji?)
4. Yapılan Ünite / Konu
5. Kullanılan Araç / Materyal Bilgisi (Güncel araçlar öner)
6. IDP Vizesi Olan Öğrenci Etkinliği (Cihaz kullanım serbest)
7. Sınıf Etkinliği (Vizesi olmayan, işbirlikçi/etkileşimli)

KURUMSAL HAFIZA:
{IDP_ORNEKLERI}

ÖNEMLİ: KISA, ÖZ ve 2024-2025/2026 güncel eğitim teknolojilerini kullanarak cevap ver.
"""

# --- 5. ARAYÜZ (FRONTEND) ---
st.title("🎓 Işıklı Dijital Pasaport Planlama Asistanı")
st.markdown("MEB Maarif Modeli derslerini seçin ve kazanımı yazarak IDP uyumlu planınızı oluşturun.")

with st.form("plan_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        # Dinamik Seçim Kutuları
        sinif_duzeyi = st.selectbox("Sınıf Düzeyi", list(MEB_DERSLERI.keys()))
        ders_listesi = MEB_DERSLERI[sinif_duzeyi]
        secilen_ders = st.selectbox("Ders Adı", ders_listesi)
        
    with col2:
        # Kazanım Girişi
        kazanim = st.text_area(
            "Öğrenci Kazanımı / Hedef", 
            placeholder="Örn: Maddenin hal değişimini deneyle açıklar.",
            height=100
        )
    
    submit_btn = st.form_submit_button("Planı ve Teknolojileri Oluştur ✨")

# --- 6. YAPAY ZEKA VE SEARCH MANTIĞI ---
if submit_btn and kazanim:
    with st.spinner(f'"{secilen_ders}" için güncel eğitim teknolojileri taranıyor...'):
        try:
            # Google Search Aracı
            grounding_tool = types.Tool(google_search=types.GoogleSearch())
            
            # Konfigürasyon
            config = types.GenerateContentConfig(
                system_instruction=gem_talimatlari,
                tools=[grounding_tool],
                temperature=0.7
            )

            # Prompt
            prompt = (f"Sınıf: {sinif_duzeyi}, Ders: {secilen_ders}, Kazanım: {kazanim}. "
                      f"Bu kazanımı Işıklı Pasaport kriterlerine göre planla. "
                      f"2024-2026 arası güncel araçları bulmak için web araması yap.")
            
            # Yanıt Üretme
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=config,
            )

            # Ekrana Yazdırma
            st.markdown("---")
            st.success(f"Ders Planı Taslağı Hazırlandı")
            st.markdown(response.text)

            # --- 7. DETAYLI KAYNAKÇA ---
            metadata = response.candidates[0].grounding_metadata
            if metadata:
                with st.expander("🔍 Kullanılan Kaynaklar ve Web Aramaları", expanded=False):
                    if metadata.web_search_queries:
                        st.subheader("Yapılan Aramalar")
                        for q in metadata.web_search_queries:
                            st.write(f"- {q}")
                    
                    st.divider()
                    
                    if metadata.grounding_chunks:
                        st.subheader("Yararlanılan Web Siteleri")
                        unique_links = {}
                        for chunk in metadata.grounding_chunks:
                            if chunk.web:
                                unique_links[chunk.web.uri] = chunk.web.title
                        
                        for uri, title in unique_links.items():
                            st.markdown(f"🔗 [{title}]({uri})")

        except Exception as e:
            st.error(f"Bir hata oluştu: {str(e)}")

# --- 8. FOOTER ---
st.divider()
st.caption("Işık Okulları Eğitim Teknolojileri Koordinatörlüğü için geliştirilmiştir.")