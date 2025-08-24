import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import io

st.set_page_config(page_title="PDF Editor", layout="wide")
st.title("📄 Simple PDF Editor (Text + Image)")

# --- Upload PDF ---
pdf_file = st.file_uploader("Upload PDF", type=["pdf"])

if pdf_file:
    pdf_bytes = pdf_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    # Page selection
    page_number = st.number_input("Select Page", min_value=1, max_value=len(doc), value=1)
    page = doc[page_number - 1]

    # --- Insert Text ---
    st.subheader("➕ Add Text")
    text = st.text_input("Enter text")
    x = st.number_input("X Position", 0, 1000, 50)
    y = st.number_input("Y Position", 0, 1000, 50)

    if st.button("Insert Text"):
        page.insert_text((x, y), text, fontsize=12, color=(0, 0, 0))
        st.success("Text inserted ✅")

    # --- Insert Image ---
    st.subheader("🖼️ Add Image")
    img_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
    if img_file:
        img = Image.open(img_file)
        rect_x = st.number_input("Image X", 0, 1000, 50)
        rect_y = st.number_input("Image Y", 0, 1000, 100)
        width = st.number_input("Image Width", 50, 1000, 100)
        height = st.number_input("Image Height", 50, 1000, 100)

        if st.button("Insert Image"):
            rect = fitz.Rect(rect_x, rect_y, rect_x + width, rect_y + height)
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="PNG")
            page.insert_image(rect, stream=img_bytes.getvalue())
            st.success("Image inserted ✅")

    # --- Save & Download ---
    output = io.BytesIO()
    doc.save(output)
    doc.close()

    st.download_button("💾 Download Edited PDF", data=output.getvalue(),
                       file_name="edited.pdf", mime="application/pdf")
