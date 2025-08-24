import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import io
import os
from streamlit_drawable_canvas import st_canvas

# Function to convert PDF page to image for preview
def pdf_page_to_image(doc, page_num):
    page = doc.load_page(page_num)
    pix = page.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return img

# Main app
st.title("Streamlit PDF Editor")
st.write("Upload a PDF and use tools to edit. Inspired by Sejda's features.")

# Upload PDF
uploaded_file = st.file_uploader("Upload PDF", type="pdf")
if uploaded_file:
    # Save uploaded file temporarily
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    doc = fitz.open("temp.pdf")
    num_pages = len(doc)
    
    # Select page to edit
    page_num = st.sidebar.selectbox("Select Page", range(1, num_pages + 1)) - 1
    current_page = doc.load_page(page_num)
    
    # Preview current page
    st.subheader("Page Preview")
    img = pdf_page_to_image(doc, page_num)
    st.image(img, use_column_width=True)
    
    # Sidebar tools (like Sejda's menu)
    tool = st.sidebar.selectbox("Choose Tool", [
        "Add Text Box", "Add Text", "Edit Text", "Add Image", "Add Shape", 
        "Add Form Field", "Annotate", "Add Signature", "Whiteout", 
        "Find and Replace", "Save & Download"
    ])
    
    if tool == "Add Text Box":
        st.sidebar.subheader("Add Text Box (Drag to Place)")
        text = st.sidebar.text_input("Text to Add")
        font_size = st.sidebar.slider("Font Size", 8, 72, 12)
        # Canvas for dragging text box
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",  # Orange fill for text box
            stroke_width=2,
            stroke_color="black",
            background_image=img,
            update_streamlit=True,
            height=img.height // 2,
            width=img.width // 2,
            drawing_mode="rect",
            key="canvas",
        )
        if canvas_result.json_data:
            objects = canvas_result.json_data["objects"]
            if objects and text:
                # Get last drawn rectangle
                rect = objects[-1]
                x, y = rect["left"] * 2, rect["top"] * 2  # Scale up (canvas is half-size)
                width, height = rect["width"] * 2, rect["height"] * 2
                pdf_rect = fitz.Rect(x, y, x + width, y + height)
                if st.sidebar.button("Apply Text Box"):
                    current_page.insert_textbox(pdf_rect, text, fontsize=font_size)
                    st.success("Text box added!")
    
    elif tool == "Add Text":
        text = st.sidebar.text_input("Text to Add")
        x = st.sidebar.number_input("X Position (0-612 for letter size)", 0, 612, 100)
        y = st.sidebar.number_input("Y Position (0-792 for letter size)", 0, 792, 100)
        font_size = st.sidebar.slider("Font Size", 8, 72, 12)
        if st.sidebar.button("Apply"):
            current_page.insert_text((x, y), text, fontsize=font_size)
            st.success("Text added!")
    
    elif tool == "Edit Text":
        st.sidebar.warning("Editing existing text requires selecting blocks (advanced). For simplicity, use 'Find and Replace'.")
    
    elif tool == "Add Image":
        img_file = st.sidebar.file_uploader("Upload Image", type=["png", "jpg"])
        if img_file:
            img = Image.open(img_file)
            x, y = st.sidebar.number_input("X"), st.sidebar.number_input("Y")
            width = st.sidebar.number_input("Width", 10, 500, 100)
            if st.sidebar.button("Apply"):
                img_path = "temp_img.png"
                img.save(img_path)
                rect = fitz.Rect(x, y, x + width, y + img.height * (width / img.width))
                current_page.insert_image(rect, filename=img_path)
                os.remove(img_path)
                st.success("Image added!")
    
    elif tool == "Add Shape":
        shape_type = st.sidebar.selectbox("Shape", ["Rectangle", "Ellipse"])
        x1, y1 = st.sidebar.number_input("X1"), st.sidebar.number_input("Y1")
        x2, y2 = st.sidebar.number_input("X2"), st.sidebar.number_input("Y2")
        color = st.sidebar.color_picker("Fill Color")
        if st.sidebar.button("Apply"):
            draw = current_page.new_shape()
            if shape_type == "Rectangle":
                draw.draw_rect(fitz.Rect(x1, y1, x2, y2))
            else:
                draw.draw_oval(fitz.Rect(x1, y1, x2, y2))
            draw.finish(fill=fitz.utils.getColor(color[1:]))
            draw.commit()
            st.success("Shape added!")
    
    elif tool == "Add Form Field":
        field_type = st.sidebar.selectbox("Field Type", ["Text", "Checkbox"])
        name = st.sidebar.text_input("Field Name")
        x, y = st.sidebar.number_input("X"), st.sidebar.number_input("Y")
        if st.sidebar.button("Apply"):
            rect = fitz.Rect(x, y, x+200, y+20)
            if field_type == "Text":
                annot = current_page.add_textbox_annot(rect, name)
            else:
                annot = current_page.add_checkbox_annot(rect)
            st.success("Form field added!")
    
    elif tool == "Annotate":
        annot_text = st.sidebar.text_input("Annotation Text")
        x, y = st.sidebar.number_input("X"), st.sidebar.number_input("Y")
        if st.sidebar.button("Apply"):
            rect = fitz.Rect(x, y, x+200, y+50)
            current_page.add_freetext_annot(rect, annot_text)
            st.success("Annotation added!")
    
    elif tool == "Add Signature":
        sig_img = st.sidebar.file_uploader("Upload Signature Image", type=["png", "jpg"])
        if sig_img:
            x, y = st.sidebar.number_input("X"), st.sidebar.number_input("Y")
            width = 100
            if st.sidebar.button("Apply"):
                img_path = "temp_sig.png"
                Image.open(sig_img).save(img_path)
                rect = fitz.Rect(x, y, x + width, y + 50)
                current_page.insert_image(rect, filename=img_path)
                os.remove(img_path)
                st.success("Signature added!")
    
    elif tool == "Whiteout":
        x1, y1 = st.sidebar.number_input("X1"), st.sidebar.number_input("Y1")
        x2, y2 = st.sidebar.number_input("X2"), st.sidebar.number_input("Y2")
        if st.sidebar.button("Apply"):
            draw = current_page.new_shape()
            draw.draw_rect(fitz.Rect(x1, y1, x2, y2))
            draw.finish(fill=(1,1,1))  # White fill
            draw.commit()
            st.success("Whiteout applied!")
    
    elif tool == "Find and Replace":
        find = st.sidebar.text_input("Find Text")
        replace = st.sidebar.text_input("Replace With")
        if st.sidebar.button("Apply"):
            for page in doc:
                areas = page.search_for(find)
                for rect in areas:
                    page.add_redact_annot(rect)
                    page.apply_redactions()
                    page.insert_text(rect.tl, replace)
            st.success("Replaced occurrences!")
    
    # Save and Download
    if st.button("Save & Download Edited PDF"):
        output = io.BytesIO()
        doc.save(output)
        st.download_button("Download PDF", output.getvalue(), "edited.pdf")
    
    # Clean up
    doc.close()
    os.remove("temp.pdf")
else:
    st.info("Upload a PDF to start editing.")
