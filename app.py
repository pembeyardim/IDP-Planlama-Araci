import streamlit as st
from google import genai
from google.genai import types

# PDF
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import io
import os
import urllib.request

# --------------------------------------------------
# ONLINE FONT (GOOGLE FONTS – TÜRKÇE UYUMLU)
# --------------------------------------------------
FONT_NAME = "NotoSans"
FONT_FILE = "NotoSans-Regular.ttf"
FONT_URL = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf"

if not os.path.exists(FONT_FILE):
    urllib.request.urlretrieve(FONT_URL, FONT_FILE)

pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_FILE))

# --------------------------------------------------
# LOGO (FMV)
# --------------------------------------------------
LOGO_URL = "https://fmv.edu.tr/Uploads/Gallery/Small/1447073e-282d-45bb-bc8c-04fe04087c89.jpg"

# --------------------------------------------------
# SAYFA AYARLARI
# --------------------------------------------------
st.set_page_config(
    page_title="Işıklı Eğitim Asistanı",
    layout="wide",
    page_icon="🎓"
)

# --------------------------------------------------
# API ANAHTARI
# --------------------------------------------------
try:
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception:
    st.error("API Anahtarı bulunamadı! Streamlit Secrets ayarlarını kontrol edin.")
    st.stop()

# --------------------------------------------------
# MEB DERS LİSTELERİ
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
# SİSTEM TALİMATI (MARKDOWN YOK)
# --------------------------------------------------
gem_talimatlari = """
Sen Işık Okulları Eğitim Teknolojileri Koordinatörüsün.
Işık Dijital Pasaport (IDP) felsefesine uygun ders planı hazırla.

Kurallar:
- Markdown kullanma
- Yıldız, başlık, madde işareti kullanma
- Düz paragraf metni üret
- Türkçe karakterlere dikkat et
- Kısa, net ve öğretmenlerin doğrudan kullanabileceği bir dil kullan
"""

# --------------------------------------------------
# PDF OLUŞTURMA (LOGO + TÜRKÇE + DÜZ METİN)
# --------------------------------------------------
def create_pdf(plan_text, sinif, ders):
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm
    )

    title_style = ParagraphStyle(
        name="Title",
        fontName=FONT_NAME,
        fontSize=16,
        leading=20
    )

    body_style = ParagraphStyle(
        name="Body",
        fontName=FONT_NAME,
        fontSize=11,
        leading=14
    )

    story = []

    # Logo
    logo_data = io.BytesIO(urllib.request.urlopen(LOGO_URL).read())
    logo = Image(logo_data, width=4 * cm, height=4 * cm)
    story.append(logo)
    story.append(Spacer(1, 12))

    # Başlık
    story.append(Paragraph(f"{sinif} – {ders}", title_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Işıklı Dijital Pasaport Ders Planı", title_style))
    story.append(Spacer(1, 20))

    # İçerik
    for line in plan_text.split("\n"):
        story.append(Paragraph(line, body_style))
        story.append(Spacer(1, 8))

    doc.build(story)
    buffer.seek(0)
    return buffer

# --------------------------------------------------
# ARAYÜZ
# --------------------------------------------------
st.title("🎓 Işıklı Dijital Pasaport Planlama Asistanı")
st.write("Kademe ve ders seçimine göre alanlar canlı güncellenir.")

col1, col2 = st.columns(2)

with col1:
    sinif_duzeyi = st.selectbox(
        "1. Sınıf Düzeyi Seçin",
        list(MEB_DERSLERI.keys()),
        key="sinif_duzeyi"
    )

with col2:
    secilen_ders = st.selectbox(
        "2. Ders Seçin",
        ["Seçiniz..."] + MEB_DERSLERI[sinif_duzeyi],
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
# YAPAY ZEKA + PDF
# --------------------------------------------------
if submit_btn and kazanim and secilen_ders != "Seçiniz...":
    with st.spinner("Ders planı hazırlanıyor..."):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=(
                    f"Kademe: {sinif_duzeyi}. "
                    f"Ders: {secilen_ders}. "
                    f"Kazanım: {kazanim}. "
                    f"2025-2026 eğitim yılı için ders planı hazırla."
                ),
                config=types.GenerateContentConfig(
                    system_instruction=gem_talimatlari,
                    temperature=0.7
                )
            )

            plan_metni = response.text

            st.success("✅ Ders Planı Hazırlandı")
            st.text(plan_metni)  # MARKDOWN YOK

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
# FOOTER
# --------------------------------------------------
st.divider()
st.caption("Işık Okulları Eğitim Teknolojileri Koordinatörlüğü için geliştirilmiştir.")
