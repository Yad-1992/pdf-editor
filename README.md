# streamlit-pdf-editor

Minimal Sejda-like PDF editor (Text Box only).  
Tech: Streamlit + PyMuPDF (fitz) + streamlit-drawable-canvas.

## Features
- Upload PDF (≤ 50 MB)
- Pick page
- Draw rectangle to place a text box
- Type text + font size
- Apply to PDF
- Download edited PDF
- Temp cleanup button

## Run locally
python -m venv .venv
. .venv/Scripts/activate   # Windows
# or: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py

## Deploy (Streamlit Community Cloud)
- Push repo to GitHub
- New app → pick this repo → set entrypoint: `app.py`

## Deploy (Render)
- New Web Service → Build Command: `pip install -r requirements.txt`
- Start Command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

## Notes
- Coordinates mapped via render zoom (image px → PDF pts).
- Assumes standard PDF points (letter 612x792) if needed; actual size read from page.
- Streamlit isn’t live-in-PDF; we preview as images then write with PyMuPDF.
