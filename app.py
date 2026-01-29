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
import re
from datetime import datetime

# --------------------------------------------------
# ONLINE FONT (TÜRKÇE TAM DESTEK)
# --------------------------------------------------
FONT_NAME = "NotoSans"
FONT_REG = "NotoSans-Regular.ttf"
FONT_BOLD = "NotoSans-Bold.ttf"

URL_REG = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf"
URL_BOLD = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Bold.ttf"

if not os.path.exists(FONT_REG):
    urllib.request.urlretrieve(URL_REG, FONT_REG)
if not os.path.exists(FONT_BOLD):
    urllib.request.urlretrieve(URL_BOLD, FONT_BOLD)

pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_REG))
pdfmetrics.registerFont(TTFont(f"{FONT_NAME}-Bold", FONT_BOLD))

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
# API
# --------------------------------------------------
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

# --------------------------------------------------
# SENİN KODLARIN – AYNEN
# --------------------------------------------------
MEB_DERSLERI = {
    "İlkokul": [
        "Türkçe", "Matematik", "Hayat Bilgisi", "Fen Bilimleri (3-4)", 
        "Sosyal Bilgiler (4)", "İngilizce", "Görsel Sanatlar", "Müzik", "Oyun ve Fiziksel Etkinlikler"
    ],
    "Ortaokul": [
        "Türkçe", "Matematik", "Fen Bilimleri", "Sosyal Bilgiler", 
        "T.C. İnkılap Tarihi ve Atatürkçülük", "İngilizce", "Din Kültürü ve Ahlak Bilgisi",
        "Bilişim Teknolojileri ve Yazılım", "Teknoloji ve Tasarım"
    ],
    "Lise (9-12)": [
        "Türk Dili ve Edebiyatı", "Matematik", "Fizik", "Kimya", "Biyoloji", 
        "Tarih", "Coğrafya", "Felsefe", "İngilizce", "Almanca/Fransızca",
        "Sağlık Bilgisi ve Trafik Kültürü", "Bilgisayar Bilimi"
    ]
}

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

ZORUNLU FORMAT:
- Aşağıdaki başlıkları MUTLAKA kullan
- Başlıkları Markdown formatında **KALIN** yaz

KULLANILACAK BAŞLIKLAR:
**Seviye:**
**Ders:**
**Teknoloji Bağlantısı (Neden teknoloji?):**
**Yapılan Ünite / Konu:**
**Kullanılan Araç / Materyal Bilgisi:**
**IDP Vizesi Olan Öğrenci Etkinliği:**
**Sınıf Etkinliği:**

KURUMSAL HAFIZA:
{IDP_ORNEKLERI}

ÖNEMLİ: KISA, ÖZ ve 2024-2025/2026 güncel eğitim teknolojilerini kullanarak cevap ver.
"""

# --------------------------------------------------
# MARKDOWN → PDF (KALIN KORUNUR)
# --------------------------------------------------
def markdown_to_pdf(text, styles):
    elements = []

    for line in text.split("\n"):
        line = line.strip()

        if not line:
            elements.append(Spacer(1, 10))
            continue

        if line.startswith("**") and line.endswith("**"):
            title = line.replace("**", "")
            elements.append(Paragraph(title, styles["bold"]))
            elements.append(Spacer(1, 10))
            continue

        line = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", line)

        if line.startswith("-"):
            line = "• " + line[1:].strip()

        elements.append(Paragraph(line, styles["body"]))
        elements.append(Spacer(1, 6))

    return elements

# --------------------------------------------------
# PDF OLUŞTURMA
# --------------------------------------------------
def create_pdf(plan_text, ders, unite):
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = {
        "bold": ParagraphStyle(
            "bold",
            fontName=f"{FONT_NAME}-Bold",
            fontSize=13,
            leading=16
        ),
        "body": ParagraphStyle(
            "body",
            fontName=FONT_NAME,
            fontSize=11,
            leading=14
        )
    }

    story = []

    logo_data = io.BytesIO(urllib.request.urlopen(LOGO_URL).read())
    story.append(Image(logo_data, width=4*cm, height=4*cm))
    story.append(Spacer(1, 16))

    story.extend(markdown_to_pdf(plan_text, styles))

    doc.build(story)
    buffer.seek(0)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{ders}_{unite}_{timestamp}.pdf".replace(" ", "_")

    return buffer, filename

# --------------------------------------------------
# ARAYÜZ
# --------------------------------------------------
st.title("🎓 Işıklı Dijital Pasaport Planlama Asistanı")

col1, col2 = st.columns(2)

with col1:
    sinif = st.selectbox("Kademe", list(MEB_DERSLERI.keys()))

with col2:
    ders = st.selectbox("Ders", MEB_DERSLERI[sinif])

unite = st.text_input("Ünite / Konu")
kazanim = st.text_area("Kazanım")

if st.button("Planı Oluştur"):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"{sinif} düzeyi {ders} dersi, ünite: {unite}, kazanım: {kazanim}",
        config=types.GenerateContentConfig(
            system_instruction=gem_talimatlari,
            temperature=0.7
        )
    )

    plan_text = response.text
    st.markdown(plan_text)

    pdf_buffer, pdf_name = create_pdf(plan_text, ders, unite)

    st.download_button(
        "📄 PDF olarak indir",
        data=pdf_buffer,
        file_name=pdf_name,
        mime="application/pdf"
    )
