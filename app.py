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
    st.error("API Anahtarı bulunamadı! Lütfen Streamlit Secrets ayarlarını kontrol edin.")
    st.stop()

# --- 3. MEB MAARİF MODELİ DERS LİSTELERİ ---
# Listeleri eksiksiz ve branş bazlı güncelledim
MEB_DERSLERI = {
    "İlkokul": [
        "Türkçe", "Matematik", "Hayat Bilgisi", "Fen Bilimleri", 
        "Sosyal Bilgiler", "İngilizce", "Din Kültürü ve Ahlak Bilgisi",
        "Görsel Sanatlar", "Müzik", "Oyun ve Fiziki Etkinlikler"
    ],
    "Ortaokul": [
        "Türkçe", "Matematik", "Fen Bilimleri", "Sosyal Bilgiler", 
        "T.C. İnkılap Tarihi ve Atatürkçülük", "İngilizce", 
        "Din Kültürü ve Ahlak Bilgisi", "Bilişim Teknolojileri ve Yazılım", 
        "Teknoloji ve Tasarım", "Müzik", "Görsel Sanatlar", "Beden Eğitimi ve Spor"
    ],
    "Lise (9-12)": [
        "Türk Dili ve Edebiyatı", "Matematik", "Fizik", "Kimya", "Biyoloji", 
        "Tarih", "Coğrafya", "Felsefe", "İngilizce", "İkinci Yabancı Dil",
        "Din Kültürü ve Ahlak Bilgisi", "Bilgisayar Bilimi", "Görsel Sanatlar/Müzik",
        "Beden Eğitimi ve Spor", "Sağlık Bilgisi ve Trafik Kültürü"
    ]
}

# --- 4. SİSTEM TALİMATI ---
IDP_ORNEKLERI = """
- Beden Eğitimi: WorldWall + Quizizz
- Müzik: Sibelius + Studio One
- Biyoloji: Canva + ChatGPT + Gamma
- Fizik: PhET Simulations
- Türk Dili: Canva Poster
"""

gem_talimatlari = f"""
Sen Işık Okulları Eğitim Teknolojileri Koordinatörüsün.
GÖREV: Işık Dijital Pasaport (IDP) felsefesine uygun ders planı hazırla.
KURUMSAL HAFIZA: {IDP_ORNEKLERI}
ÖNEMLİ: KISA, ÖZ ve 2024-2026 güncel eğitim teknolojilerini kullan.
"""

# --- 5. ARAYÜZ (DINAMIK SEÇİM) ---
st.title("🎓 Işıklı Dijital Pasaport Planlama Asistanı")
st.markdown("Ders ve kademe seçimini yaptığınızda liste anında güncellenir.")

# SEÇİMLER FORMUN DIŞINDA (Canlı Güncelleme İçin)
col1, col2 = st.columns(2)

with col1:
    sinif_duzeyi = st.selectbox("1. Sınıf Düzeyi Seçin", list(MEB_DERSLERI.keys()))

with col2:
    # Seçilen kademeye göre liste anında yenilenir
    ders_listesi = MEB_DERSLERI[sinif_duzeyi]
    secilen_ders = st.selectbox("2. Ders Seçin", ders_listesi)

# Kazanım ve Buton için form kullanabiliriz
with st.form("plan_detay_form"):
    kazanim = st.text_area(
        "3. Öğrenci Kazanımı / Hedef", 
        placeholder="Örn: Hücrenin organellerini ve görevlerini açıklar.",
        height=100
    )
    submit_btn = st.form_submit_button("Planı Oluştur ✨")

# --- 6. YAPAY ZEKA VE SEARCH MANTIĞI ---
if submit_btn and kazanim:
    with st.spinner(f'"{secilen_ders}" için araştırma yapılıyor...'):
        try:
            grounding_tool = types.Tool(google_search=types.GoogleSearch())
            config = types.GenerateContentConfig(
                system_instruction=gem_talimatlari,
                tools=[grounding_tool],
                temperature=0.7
            )

            prompt = (f"KADEME: {sinif_duzeyi}, DERS: {secilen_ders}, KAZANIM: {kazanim}. "
                      f"Bu ders için Işıklı Pasaport formatında güncel (2025-2026) bir plan hazırla.")
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=config,
            )

            st.markdown("---")
            st.success(f"✅ {sinif_duzeyi} - {secilen_ders} Planı Hazırlandı")
            st.markdown(response.text)

            # Kaynakça
            metadata = response.candidates[0].grounding_metadata
            if metadata and metadata.grounding_chunks:
                with st.expander("🔍 Yararlanılan Kaynaklar"):
                    unique_links = {chunk.web.uri: chunk.web.title for chunk in metadata.grounding_chunks if chunk.web}
                    for uri, title in unique_links.items():
                        st.markdown(f"🔗 [{title}]({uri})")

        except Exception as e:
            st.error(f"Hata oluştu: {str(e)}")

st.divider()
st.caption("Işık Okulları Eğitim Teknolojileri Koordinatörlüğü")

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