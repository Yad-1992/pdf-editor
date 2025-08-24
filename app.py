# streamlit-pdf-editor/app.py
# Minimal Sejda-like "Add Text Box" PDF editor
# Tech: Streamlit + PyMuPDF (fitz) + streamlit-drawable-canvas + Pillow
# Focus: Upload PDF → pick page → draw rectangle → type text → apply → download

import os, io, tempfile, shutil, atexit
import streamlit as st
from PIL import Image
import numpy as np
from streamlit_drawable_canvas import st_canvas
import fitz  # PyMuPDF

st.set_page_config(page_title="Sejda-like PDF Text Tool", page_icon="📝", layout="wide")

# ---------- Helpers ----------
def make_temp_area():
    if "tmp_dir" not in st.session_state or not st.session_state.get("tmp_dir"):
        st.session_state.tmp_dir = tempfile.mkdtemp(prefix="pdfedit_")
    return st.session_state.tmp_dir

def cleanup_all():
    try:
        if "doc" in st.session_state and st.session_state.doc:
            try: 
                st.session_state.doc.close()
            except: 
                pass
            st.session_state.doc = None
        if "tmp_dir" in st.session_state and st.session_state.tmp_dir and os.path.isdir(st.session_state.tmp_dir):
            shutil.rmtree(st.session_state.tmp_dir, ignore_errors=True)
        for k in ["tmp_dir","pdf_path","num_pages","page_index","last_canvas","edited_bytes"]:
            st.session_state.pop(k, None)
    except: 
        pass

atexit.register(cleanup_all)

def save_bytes_to_tmp(uploaded_file, dst_dir):
    dst = os.path.join(dst_dir, uploaded_file.name)
    with open(dst, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return dst

def page_pixmap(page, zoom=2.0):
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return img, zoom, (pix.width, pix.height)

def apply_textbox_to_pdf(pdf_doc, page_idx, rect_px, zoom, text, font_size_pt):
    x, y, w, h = rect_px
    x0 = x / zoom
    y0 = y / zoom
    x1 = (x + w) / zoom
    y1 = (y + h) / zoom
    r = fitz.Rect(x0, y0, x1, y1)
    page = pdf_doc.load_page(page_idx)
    page.insert_textbox(
        r,
        text if text else "",
        fontsize=float(font_size_pt),
        fontname="helv",
        align=0,
        color=(0, 0, 0),
    )
    if pdf_doc.is_dirty:
        pdf_doc.saveIncr()

def get_pdf_bytes(pdf_doc):
    buf = io.BytesIO()
    pdf_doc.save(buf)
    buf.seek(0)
    return buf.getvalue()

# ---------- Sidebar (Toolbar) ----------
st.sidebar.title("🧰 Tools")
tool = st.sidebar.radio("Toolbox", ["Add Text Box"], index=0)
text_to_add = st.sidebar.text_area("Text", placeholder="Type text here…", height=120)
font_size = st.sidebar.number_input("Font size (pt)", min_value=6, max_value=96, value=16, step=1)
apply_btn = st.sidebar.button("Apply to PDF")
download_btn_placeholder = st.sidebar.empty()
st.sidebar.markdown("---")
reset_btn = st.sidebar.button("Reset & Delete Temp Files", type="secondary")

# ---------- Upload ----------
st.title("Sejda-like PDF Editor (Text Box)")
uploaded = st.file_uploader("Upload PDF (≤ 50 MB)", type=["pdf"])
if reset_btn:
    cleanup_all()
    st.success("Reset done. Temp files deleted.")

if uploaded:
    if uploaded.size and uploaded.size > 50 * 1024 * 1024:
        st.error("File too large. Please upload ≤ 50 MB.")
        st.stop()
    tmp = make_temp_area()
    if "pdf_path" not in st.session_state:
        st.session_state.pdf_path = save_bytes_to_tmp(uploaded, tmp)
        st.session_state.doc = fitz.open(st.session_state.pdf_path)
        st.session_state.num_pages = st.session_state.doc.page_count
        st.session_state.page_index = 0
        st.session_state.last_canvas = None

# ---------- Editor UI ----------
if "doc" in st.session_state and st.session_state.doc:
    doc = st.session_state.doc
    num_pages = st.session_state.num_pages
    col1, col2 = st.columns([1, 3])

    with col1:
        st.subheader("Pages")
        page_idx = st.number_input("Page # (1-based)", min_value=1, max_value=num_pages, value=st.session_state.page_index + 1, step=1)
        st.session_state.page_index = page_idx - 1
        page = doc.load_page(st.session_state.page_index)
        st.caption(f"Page size (pts): {int(page.rect.width)} × {int(page.rect.height)}")

    with col2:
        st.subheader("Preview & Draw")
        bg_img, zoom, (img_w, img_h) = page_pixmap(page, zoom=2.0)
        bg_np = np.array(bg_img)  # 🔥 FIX: convert PIL → numpy
        canvas_result = st_canvas(
            background_image=bg_np,
            update_streamlit=True,
            fill_color="rgba(0, 0, 0, 0.0)",
            stroke_width=2,
            stroke_color="#00A3FF",
            background_color="#FFFFFF",
            height=img_h,
            width=img_w,
            drawing_mode="rect" if tool == "Add Text Box" else "transform",
            key=f"canvas_{st.session_state.page_index}",
        )
        st.session_state.last_canvas = canvas_result

    # ---------- Apply ----------
    if apply_btn:
        objs = (st.session_state.last_canvas.json_data or {}).get("objects", []) if st.session_state.last_canvas else []
        rect_obj = None
        for o in objs[::-1]:
            if o.get("type") == "rect":
                rect_obj = o
                break
        if not rect_obj:
            st.warning("Draw a rectangle first.")
        else:
            left = float(rect_obj.get("left", 0))
            top = float(rect_obj.get("top", 0))
            width = float(rect_obj.get("width", 0)) * float(rect_obj.get("scaleX", 1))
            height = float(rect_obj.get("height", 0)) * float(rect_obj.get("scaleY", 1))
            apply_textbox_to_pdf(
                pdf_doc=doc,
                page_idx=st.session_state.page_index,
                rect_px=(left, top, width, height),
                zoom=zoom,
                text=text_to_add,
                font_size_pt=font_size,
            )
            st.success("Text placed.")
            page = doc.load_page(st.session_state.page_index)
            bg_img, _, _ = page_pixmap(page, zoom=2.0)
            st.image(bg_img, caption="Updated preview")

    # ---------- Download ----------
    with st.sidebar:
        if st.button("Prepare Download"):
            st.session_state.edited_bytes = get_pdf_bytes(doc)
            st.success("Ready to download.")
        if "edited_bytes" in st.session_state and st.session_state.edited_bytes:
            download_btn_placeholder.download_button(
                label="⬇️ Download Edited PDF",
                data=st.session_state.edited_bytes,
                file_name="edited.pdf",
                mime="application/pdf",
            )

    st.markdown("_Privacy_: Files live only in a temp folder during your session.")
else:
    st.info("Upload a PDF to start.")

# ---------- Limitations ----------
with st.expander("Limitations & ideas"):
    st.markdown(
        """
- Streamlit is not live editing inside the PDF (we render page → image).
- Fonts: only Helvetica now.
- Add text color, bold/italic, undo, signatures in future.
- Files stay only in temp dir during session.
"""
    )
