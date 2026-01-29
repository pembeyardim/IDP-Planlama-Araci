import streamlit as st
from google import genai
from google.genai import types

# PDF
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
import io

# --------------------------------------------------
# 1. SAYFA AYARLARI
# --------------------------------------------------
st.set_page_config(
    page_title="Işıklı Eğitim Asistanı",
    layout="wide",
    page_icon="🎓"
)

# --------------------------------------------------
# 2. API ANAHTARI
# --------------------------------------------------
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    client = genai.Client(api_key=api_key)
except Exception:
    st.error("API Anahtarı bulunamadı! Streamlit Secrets ayarlarını kontrol edin.")
    st.stop()

# --------------------------------------------------
# 3. MEB DERS LİSTELERİ
# --------------------------------------------------
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
        "Din Kültürü ve Ahlak Bilgisi", "Bilgisayar Bilimi",
        "Görsel Sanatlar/Müzik", "Beden Eğitimi ve Spor",
        "Sağlık Bilgisi ve Trafik Kültürü"
    ]
}

# --------------------------------------------------
# 4. SİSTEM TALİMATI
# --------------------------------------------------
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

# --------------------------------------------------
# 5. PDF OLUŞTURMA FONKSİYONU
# --------------------------------------------------
def create_pdf(plan_text, sinif, ders):
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    story = []

    title = f"{sinif} – {ders}<br/>Işıklı Dijital Pasaport Ders Planı"
    story.append(Paragraph(title, styles["Title"]))
    story.append(Spacer(1, 12))

    for line in plan_text.split("\n"):
        safe_line = line.replace("<", "&lt;").replace(">", "&gt;")
        story.append(Paragraph(safe_line, styles["Normal"]))
        story.append(Spacer(1, 6))

    doc.build(story)
    buffer.seek(0)
    return buffer

# --------------------------------------------------
# 6. ARAYÜZ
# --------------------------------------------------
st.title("🎓 Işıklı Dijital Pasaport Planlama Asistanı")
st.markdown("Kademe ve ders seçimine göre alanlar **canlı** güncellenir.")

col1, col2 = st.columns(2)

with col1:
    sinif_duzeyi = st.selectbox(
        "1. Sınıf Düzeyi Seçin",
        list(MEB_DERSLERI.keys()),
        key="sinif_duzeyi"
    )

with col2:
    ders_listesi = MEB_DERSLERI[sinif_duzeyi]
    secilen_ders = st.selectbox(
        "2. Ders Seçin",
        ["Seçiniz..."] + ders_listesi,
        key=f"ders_{sinif_duzeyi}"
    )

with st.form("plan_form"):
    kazanim = st.text_area(
        "3. Öğrenci Kazanımı / Hedef",
        placeholder="Örn: Hücrenin organellerini ve görevlerini açıklar.",
        height=100
    )
    submit_btn = st.form_submit_button("✨ Planı Oluştur")

# --------------------------------------------------
# 7. YAPAY ZEKA + PDF
# --------------------------------------------------
if submit_btn and kazanim and secilen_ders != "Seçiniz...":

    with st.spinner("Ders planı hazırlanıyor..."):
        try:
            grounding_tool = types.Tool(google_search=types.GoogleSearch())

            config = types.GenerateContentConfig(
                system_instruction=gem_talimatlari,
                tools=[grounding_tool],
                temperature=0.7
            )

            prompt = (
                f"KADEME: {sinif_duzeyi}, "
                f"DERS: {secilen_ders}, "
                f"KAZANIM: {kazanim}. "
                f"Işıklı Dijital Pasaport formatında 2025-2026 için plan hazırla."
            )

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=config
            )

            plan_metni = response.text

            st.success("✅ Ders Planı Hazırlandı")
            st.markdown(plan_metni)

            pdf_buffer = create_pdf(plan_metni, sinif_duzeyi, secilen_ders)

            st.download_button(
                label="📄 PDF olarak indir",
                data=pdf_buffer,
                file_name=f"{sinif_duzeyi}_{secilen_ders}_IDP_Plan.pdf",
                mime="application/pdf"
            )

        except Exception as e:
            st.error(f"Hata oluştu: {e}")

# --------------------------------------------------
# 8. FOOTER
# --------------------------------------------------
st.divider()
st.caption("Işık Okulları Eğitim Teknolojileri Koordinatörlüğü için geliştirilmiştir.")
