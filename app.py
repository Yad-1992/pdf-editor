import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
import numpy as np
import io

st.set_page_config(page_title="PDF Editor", layout="wide")
st.title("📝 Simple PDF Editor (Drag & Drop Text & Images)")

# Upload PDF
uploaded_pdf = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_pdf:
    reader = PdfReader(uploaded_pdf)
    first_page = reader.pages[0]

    # Render page as white background
    width, height = 800, 1000
    background = np.ones((height, width, 3), dtype=np.uint8) * 255

    st.subheader("Edit Page (Drag & Drop)")
    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=2,
        stroke_color="#000000",
        background_image=background,
        update_streamlit=True,
        height=height,
        width=width,
        drawing_mode="transform",  # ✅ drag + resize + move
        key="canvas",
    )

    # Add text
    text_input = st.text_input("Add Text")
    if text_input and canvas_result.json_data:
        st.write("📌 Drag text box where you want it")
        st.json(canvas_result.json_data)

    # Add image
    uploaded_img = st.file_uploader("Insert Image", type=["png", "jpg", "jpeg"])
    if uploaded_img:
        img = Image.open(uploaded_img).convert("RGB")
        st.image(img, caption="Image to insert", width=150)

    # Export to PDF
    if st.button("💾 Save Edited PDF"):
        writer = PdfWriter()
        writer.add_page(first_page)

        output = io.BytesIO()
        writer.write(output)
        st.download_button("⬇ Download PDF", data=output.getvalue(), file_name="edited.pdf")
