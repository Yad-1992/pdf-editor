import streamlit as st
from streamlit_drawable_canvas import st_canvas
import fitz
from PIL import Image
import numpy as np
import io

st.set_page_config(page_title="Drag & Drop PDF Editor", layout="wide")
st.title("📄 PDF Editor (Drag & Drop)")

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file:
    # Read PDF
    pdf_bytes = uploaded_file.read()
    pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = pdf_doc[0]  # first page only for demo

    # Convert page to image
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    img_array = np.array(img)  # ✅ Must be numpy array for st_canvas

    st.subheader("🖌 Drag & Drop on Canvas")
    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=2,
        stroke_color="#000000",
        background_image=img_array,  # ✅ numpy array
        update_streamlit=True,
        height=img_array.shape[0],
        width=img_array.shape[1],
        drawing_mode="transform",  # ✅ allows drag/drop
        key="canvas",
    )

    if st.button("💾 Save PDF"):
        # Insert objects into PDF
        for obj in canvas_result.json_data["objects"]:
            if obj["type"] == "i-text":
                x, y = obj["left"], obj["top"]
                pdf_doc[0].insert_text((x, y), obj["text"], fontsize=14, color=(0,0,0))
            elif obj["type"] == "rect":
                x, y, w, h = obj["left"], obj["top"], obj["width"], obj["height"]
                rect = fitz.Rect(x, y, x+w, y+h)
                pdf_doc[0].draw_rect(rect, color=(1,0,0), width=2)

        # Save edited PDF
        out = io.BytesIO()
        pdf_doc.save(out)
        st.download_button("⬇️ Download Edited PDF",
                           out.getvalue(),
                           file_name="edited.pdf",
                           mime="application/pdf")
