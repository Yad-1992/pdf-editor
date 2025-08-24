import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PyPDF2 import PdfReader
from pdf2image import convert_from_bytes
from pdf_lib import PDFDocument, rgb
from PIL import Image

st.title("📝 PDF Editor with Drag & Drop")

uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])

if uploaded_pdf:
    pdf_bytes = uploaded_pdf.read()
    images = convert_from_bytes(pdf_bytes)

    page_number = st.number_input("Page Number", 1, len(images), 1)
    bg = images[page_number-1]

    st.write("Drag text or image on canvas")

    # Drawable Canvas
    canvas = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=2,
        background_image=bg,
        height=bg.height,
        width=bg.width,
        drawing_mode="textbox",  # or "transform"
        key="canvas",
    )

    # Save edits into PDF
    if st.button("Save & Download PDF"):
        pdf_out = PDFDocument.load(pdf_bytes)
        page = pdf_out.pages[page_number-1]

        if canvas.json_data is not None:
            for obj in canvas.json_data["objects"]:
                if obj["type"] == "textbox":
                    x, y = obj["left"], bg.height - obj["top"]
                    text = obj["text"]
                    page.draw_text(text, x=x, y=y, size=12, color=rgb(0, 0, 1))

        out_bytes = pdf_out.save()
        st.download_button("Download Edited PDF", out_bytes,
                           file_name="edited.pdf", mime="application/pdf")
