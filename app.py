import streamlit as st
from streamlit_drawable_canvas import st_canvas
import fitz
from PIL import Image
import io

st.set_page_config(page_title="Drag & Drop PDF Editor", layout="wide")
st.title("📄 PDF Editor (Drag & Drop)")

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file:
    pdf_bytes = uploaded_file.read()
    pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = pdf_doc[0]  # first page

    # Convert PDF page to image
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    st.subheader("🖌 Drag & Drop on Canvas")
    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=0,
        stroke_color="#000000",
        background_image=img,
        update_streamlit=True,
        height=pix.height,
        width=pix.width,
        drawing_mode="transform",  # allow dragging
        key="canvas",
    )

    # Save when clicked
    if st.button("💾 Save PDF"):
        for obj in canvas_result.json_data["objects"]:
            if obj["type"] == "i-text":  # text box
                x, y = obj["left"], obj["top"]
                pdf_doc[0].insert_text((x, y), obj["text"], fontsize=14, color=(0,0,0))
            elif obj["type"] == "image":  # image box
                x, y = obj["left"], obj["top"]
                w, h = obj["width"], obj["height"]
                rect = fitz.Rect(x, y, x+w, y+h)
                img_bytes = io.BytesIO()
                Image.open(io.BytesIO(obj["src"].encode())).save(img_bytes, format="PNG")
                pdf_doc[0].insert_image(rect, stream=img_bytes.getvalue())

        out = io.BytesIO()
        pdf_doc.save(out)
        st.download_button("⬇️ Download Edited PDF", out.getvalue(),
                           file_name="edited.pdf", mime="application/pdf")
