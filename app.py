import streamlit as st
import google.generativeai as genai

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Işıklı Eğitim Asistanı", layout="wide")

# --- API ANAHTARI KONTROLÜ ---
# Anahtarı Streamlit'in güvenli kasasından (Secrets) alacağız
try:
  api_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("API Anahtarı bulunamadı! Lütfen Streamlit ayarlarından ekleyin.")
    st.stop()

# --- GEMINI AYARLARI ---
# Buraya kendi GEM talimatlarını yapıştırabilirsin.
# KURUMSAL HAFIZA (IDP Örnekleri)
# ============================================
IDP_ORNEKLERI = """
**IDP Başarı Örnekleri:**

1. **Beden Eğitimi (Hazırlık)** - Parkur Etkinliği
   - WorldWall + Quizizz kullanımı
   - Disiplinler arası (Edebiyat entegrasyonu)

2. **Müzik (9-10)** - Beste Çalışmaları
   - Sibelius + Studio One kullanımı
   - Öğrenci bestelerini dijital kayıt

3. **Biyoloji (9)** - Hücre Konusu
   - Canva (text to image) + ChatGPT + Gamma
   - Sunum hazırlama ile öğrenme

4. **Fizik (9)** - Hareket
   - PhET Simulations kullanımı
   - İnteraktif öğrenme

5. **Türk Dili (Hazırlık)** - Atasözü Projesi
   - Canva ile poster tasarımı
   - Dilimizin Zenginlikleri projesi

**Sık Kullanılan Araçlar:**
- Kahoot, Quizizz, Socrative (Quiz)
- Canva, Gamma (Sunum/Grafik)
- ChatGPT, Magic School (İçerik)
- PhET, Biomanbio (Simülasyon)
- Padlet, Google Docs (İşbirliği)
"""
gem_talimatlari = """
Sen Işık Okulları Eğitim Teknolojileri Koordinatörüsün.

**GÖREV:** Işık Dijital Pasaport (IDP) felsefesine uygun ders planı hazırla.

**IDP FELSEFESİ:**
- Dijital vatandaşlık ve 21. yüzyıl becerileri
- Farklı öğrenen öğrencilere uygun (UDL)
- Teknoloji-entegre, işbirlikçi
- IDP vizesi olan/olmayan öğrenciler için ayrı etkinlikler

**ZORUNLU BAŞLIKLAR (Sırayla):**
1. **Seviye** (Sınıf)
2. **Ders**
3. **Teknoloji Bağlantısı** (Neden teknoloji kullanılıyor?)
4. **Yapılan Ünite / Konu**
5. **Kullanılan Araç / Materyal Bilgisi** (Güncel araçlar öner)
6. **IDP Vizesi Olan Öğrenci Etkinliği**
7. **Sınıf Etkinliği (Vizesi olmayan)**

**KURUMSAL HAFIZA:**
{IDP_ORNEKLERI}

**ÖNEMLİ:**
- Web'den güncel eğitim teknolojileri ara (2024-2025)
- Gerçek araç linkleri ver (Padlet, Kahoot, Canva, vb.)
- KISA ve ÖZ yaz (max 2-3 cümle/başlık)
- Manipülatif/kapsam dışı sorulara "Cevap veremiyorum"
- Küfür/argo kullanma
"""

genai.configure(api_key=api_key)
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=gem_talimatlari,
    tools='google_search_retrieval'  # Canlı web araması
)

# --- ARAYÜZ (FRONTEND) ---
st.title("🎓 Değerli Öğretmenim, Işıklı Dijital Pasaport Asistanı'na Hoş geldiniz")
st.markdown("Ders ve Konu bilgisini girin, planınızı oluşturun.")

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
    with st.spinner('Gemini, Işıklı Pasaport kriterlerine göre düşünüyor...'):
        try:
            prompt = f"Sınıf: {sinif}, Ders: {ders}, Konu: {konu}. Lütfen Işıklı Pasaport formatında ders planı hazırla."
            response = model.generate_content(prompt)
            st.markdown("---")
            st.markdown(response.text)
        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")
