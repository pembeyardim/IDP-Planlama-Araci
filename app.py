import streamlit as st
from google import genai
from google.genai import types

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Işıklı Eğitim Asistanı", layout="wide", page_icon="🎓")

# --- API ANAHTARI KONTROLÜ ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("API Anahtarı bulunamadı! Lütfen Streamlit secrets (GOOGLE_API_KEY) ekleyin.")
    st.stop()

# --- YENİ SDK İSTEMCİSİ (CLIENT) ---
client = genai.Client(api_key=api_key)

# --- KURUMSAL HAFIZA VE TALİMATLAR ---
IDP_ORNEKLERI = """
1. Beden Eğitimi (Hazırlık) - WorldWall + Quizizz
2. Müzik (9-10) - Sibelius + Studio One
3. Biyoloji (9) - Canva + ChatGPT + Gamma
4. Fizik (9) - PhET Simulations
5. Türk Dili (Hazırlık) - Canva Poster Tasarımı
"""

gem_talimatlari = f"""
Sen Işık Okulları Eğitim Teknolojileri Koordinatörüsün.
GÖREV: Işık Dijital Pasaport (IDP) felsefesine uygun ders planı hazırla.
IDP FELSEFESİ: Dijital vatandaşlık, UDL uyumlu, teknoloji entegreli.

ZORUNLU BAŞLIKLAR:
1. Seviye 2. Ders 3. Teknoloji Bağlantısı 4. Yapılan Ünite 5. Kullanılan Araç Bilgisi 
6. IDP Vizesi Olan Öğrenci Etkinliği 7. Sınıf Etkinliği (Vizesiz)

KURUMSAL HAFIZA:
{IDP_ORNEKLERI}
"""

# --- ARAYÜZ ---
st.title("🎓 Işıklı Dijital Pasaport Asistanı")
st.markdown("Ders ve Konu bilgisini girin, planınızı güncel Web verileriyle oluşturun.")

with st.form("plan_form"):
    col1, col2 = st.columns(2)
    with col1:
        sinif = st.selectbox("Sınıf Düzeyi", ["İlkokul", "Ortaokul", "Lise (9-12)"])
        ders = st.text_input("Ders Adı", placeholder="Örn: Matematik")
    with col2:
        konu = st.text_input("Konu / Kazanım", placeholder="Örn: Sürdürülebilirlik")
    
    submit_btn = st.form_submit_button("Planı Oluştur ✨")

# --- SONUÇ ALANI ---
if submit_btn and ders and konu:
    with st.spinner('Gemini, güncel eğitim araçlarını tarıyor...'):
        try:
            # Google Search Tool Tanımlama
            grounding_tool = types.Tool(google_search=types.GoogleSearch())
            
            # İçerik Yapılandırması (Sistem Talimatı Buraya Eklenir)
            config = types.GenerateContentConfig(
                system_instruction=gem_talimatlari,
                tools=[grounding_tool],
                temperature=0.7
            )

            prompt = f"Sınıf: {sinif}, Ders: {ders}, Konu: {konu}. Işıklı Pasaport formatında, 2024-2025 güncel araçlarını içeren bir plan hazırla."
            
            # Yanıt Üretme
            response = client.models.generate_content(
                model="gemini-2.5-flash", # En güncel model
                contents=prompt,
                config=config,
            )

            st.markdown("---")
            # Yanıt içeriğini bastırma (Grounding metadata varsa alt bilgi olarak eklenebilir)
            st.markdown(response.text)
            
            if response.candidates[0].grounding_metadata:
                 with st.expander("Kaynaklar ve Arama Bilgisi"):
                     st.write("Bu yanıt Google Arama sonuçları ile desteklenmiştir.")

        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")

# --- ETKİLEŞİMLİ SON ---
st.info("💡 Not: Planı beğendiyseniz kopyalayıp ders defterinize ekleyebilirsiniz.")