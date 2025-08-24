import streamlit as st
import pymupdf  # PyMuPDF
from PIL import Image
import io

st.set_page_config(page_title="PDF Editor", layout="wide")
st.title("📄 Simple PDF Editor (Text + Image)")

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file:
    # Load PDF
    pdf_bytes = uploaded_file.read()
    pdf_doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")

    # Page selector
    page_num = st.number_input("Select page", 1, len(pdf_doc), 1)
    page = pdf_doc[page_num - 1]

    # Render preview as image
    pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2))  # zoom
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    st.image(img, caption=f"Page {page_num}", use_container_width=True)

    # Options for editing
    st.subheader("✏️ Add Text")
    text = st.text_input("Enter text")
    x = st.number_input("X position", 0, 2000, 50)
    y = st.number_input("Y position", 0, 2000, 50)

    if st.button("Insert Text"):
        page.insert_text((x, y), text, fontsize=14, color=(0, 0, 0))
        st.success("Text added ✅")

    st.subheader("🖼️ Add Image")
    img_file = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"])
    if img_file and st.button("Insert Image"):
        img_bytes = img_file.read()
        rect = pymupdf.Rect(x, y, x + 100, y + 100)
        page.insert_image(rect, stream=img_bytes)
        st.success("Image added ✅")

    # Export PDF
    if st.button("💾 Save & Download PDF"):
        output = io.BytesIO()
        pdf_doc.save(output)
        st.download_button("Download Edited PDF", output.getvalue(),
                           file_name="edited.pdf", mime="application/pdf")
