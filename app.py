import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
import numpy as np
import io

st.set_page_config(page_title="PDF Drag & Drop Editor", layout="wide")
st.title("📑 PDF Editor with Drag & Drop Toolbar")

# Upload PDF
uploaded_pdf = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_pdf:
    reader = PdfReader(uploaded_pdf)
    first_page = reader.pages[0]

    # White background placeholder (instead of real render for now)
    width, height = 800, 1000
    background = np.ones((height, width, 3), dtype=np.uint8) * 255

    # --- Toolbar Options ---
    st.sidebar.header("✏️ Tools")
    tool = st.sidebar.radio("Choose Tool", ["Select/Move", "Draw", "Text Box", "Insert Image"])

    stroke_color = st.sidebar.color_picker("Stroke Color", "#000000")
    stroke_width = st.sidebar.slider("Stroke Width", 1, 5, 2)

    # --- Canvas ---
    st.subheader("Drag & Drop Editor")
    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_image=background,
        update_streamlit=True,
        height=height,
        width=width,
        drawing_mode="transform" if tool == "Select/Move" else "freedraw",
        key="canvas",
    )

    # --- Add Text ---
    if tool == "Text Box":
        text_input = st.text_input("Enter Text")
        if text_input:
            st.info("📌 Drag text box on PDF where needed")

    # --- Add Image ---
    if tool == "Insert Image":
        uploaded_img = st.file_uploader("Choose an image", type=["png", "jpg", "jpeg"])
        if uploaded_img:
            img = Image.open(uploaded_img).convert("RGB")
            st.image(img, caption="Image ready to insert", width=150)
            st.info("📌 Drag image box on PDF where needed")

    # --- Export PDF ---
    if st.button("💾 Save PDF"):
        writer = PdfWriter()
        writer.add_page(first_page)  # TODO: merge drawings
        output = io.BytesIO()
        writer.write(output)
        st.download_button("⬇ Download PDF", data=output.getvalue(), file_name="edited.pdf")
