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
# ONLINE FONT (UNICODE – TÜRKÇE TAM DESTEK)
# --------------------------------------------------
FONT_NAME = "NotoSans"
FONT_FILE = "NotoSans-Regular.ttf"
FONT_BOLD_FILE = "NotoSans-Bold.ttf"

FONT_URL = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf"
FONT_BOLD_URL = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Bold.ttf"

if not os.path.exists(FONT_FILE):
    urllib.request.urlretrieve(FONT_URL, FONT_FILE)
if not os.path.exists(FONT_BOLD_FILE):
    urllib.request.urlretrieve(FONT_BOLD_URL, FONT_BOLD_FILE)

pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_FILE))
pdfmetrics.registerFont(TTFont(f"{FONT_NAME}-Bold", FONT_BOLD_FILE))

# --------------------------------------------------
# LOGO
# --------------------------------------------------
LOGO_URL = "https://fmv.edu.tr/Uploads/Gallery/Small/1447073e-282d-45bb-bc8c-04fe04087c89.jpg"

# --------------------------------------------------
# SAYFA
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
# DERSLER
# --------------------------------------------------
MEB_DERSLERI = {
    "Ortaokul": ["Fen Bilimleri", "Matematik", "Türkçe"],
    "Lise (9-12)": ["Biyoloji", "Fizik", "Kimya", "Türk Dili ve Edebiyatı"]
}

# --------------------------------------------------
# MARKDOWN → PDF PARSER
# --------------------------------------------------
def markdown_to_pdf_elements(text, styles):
    elements = []

    for line in text.split("\n"):
        line = line.strip()
        if not line:
            elements.append(Spacer(1, 8))
            continue

        # ## Başlık
        if line.startswith("##"):
            content = line.replace("##", "").strip()
            elements.append(Paragraph(content, styles["h2"]))
            elements.append(Spacer(1, 12))
            continue

        # **Kalın**
        line = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", line)

        # - Madde
        if line.startswith("-"):
            line = "• " + line[1:].strip()

        elements.append(Paragraph(line, styles["body"]))
        elements.append(Spacer(1, 6))

    return elements

# --------------------------------------------------
# PDF
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
        "h2": ParagraphStyle(
            "h2",
            fontName=f"{FONT_NAME}-Bold",
            fontSize=15,
            leading=18
        ),
        "body": ParagraphStyle(
            "body",
            fontName=FONT_NAME,
            fontSize=11,
            leading=14
        )
    }

    story = []

    # Logo
    logo_data = io.BytesIO(urllib.request.urlopen(LOGO_URL).read())
    story.append(Image(logo_data, width=4*cm, height=4*cm))
    story.append(Spacer(1, 16))

    story.extend(markdown_to_pdf_elements(plan_text, styles))

    doc.build(story)
    buffer.seek(0)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{ders}_{unite}_{timestamp}.pdf".replace(" ", "_")

    return buffer, filename

# --------------------------------------------------
# ARAYÜZ
# --------------------------------------------------
st.title("🎓 Işıklı Dijital Pasaport Planlama Asistanı")

sinif = st.selectbox("Kademe", list(MEB_DERSLERI.keys()))
ders = st.selectbox("Ders", MEB_DERSLERI[sinif])
unite = st.text_input("Ünite Adı")
kazanim = st.text_area("Kazanım")

if st.button("Planı Oluştur"):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"{ders} dersi {unite} ünitesi için IDP ders planı hazırla.",
        config=types.GenerateContentConfig(temperature=0.7)
    )

    plan = response.text
    st.markdown(plan)

    pdf_buffer, pdf_name = create_pdf(plan, ders, unite)

    st.download_button(
        "📄 PDF indir",
        data=pdf_buffer,
        file_name=pdf_name,
        mime="application/pdf"
    )
