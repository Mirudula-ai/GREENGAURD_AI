# File: nitrous.py
import streamlit as st
import pytesseract
from PIL import Image
import fitz
import re
from report_generator import generate_pdf_report
import matplotlib.pyplot as plt

def extract_text(uploaded_file):
    if "pdf" in uploaded_file.type:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        return "\n".join([page.get_text() for page in doc])
    elif "image" in uploaded_file.type:
        image = Image.open(uploaded_file)
        return pytesseract.image_to_string(image)
    elif "text" in uploaded_file.type:
        return uploaded_file.read().decode("utf-8", errors="ignore")
    return ""

def contains_keywords(text, keywords):
    return any(word.lower() in text.lower() for word in keywords)

def nitrous_app():
    st.header("🧪 Nitrous Oxide Emission Estimator")
    uploaded_file = st.file_uploader("Upload fertilizer or chemical usage bill", type=["pdf", "png", "jpg", "jpeg", "txt"])

    if uploaded_file:
        content = extract_text(uploaded_file)
        st.text_area("Extracted Text", content, height=200)

        keywords = ["fertilizer", "n2o", "urea"]
        if contains_keywords(content, keywords):
            matches = re.findall(r"\d+\.?\d*", content)
            units = sum([float(m) for m in matches])
            emission = round(units * 1.65, 4)

            st.success(f"Estimated Nitrous Oxide Emission: {emission} kg CO2 eq")

            filename = generate_pdf_report("Nitrous Oxide Emission Report", units, emission, unit_label="kg", gas_label="kg CO2 eq")
            with open(filename, "rb") as f:
                st.download_button("📄 Download PDF Report", f, file_name=filename)

            fig, ax = plt.subplots()
            ax.bar(["Usage", "Emission"], [units, emission], color=["blue", "green"])
            ax.set_ylabel("kg CO2 eq")
            ax.set_title("Nitrous Oxide Emission Summary")
            st.pyplot(fig)
        else:
            st.warning("No fertilizer/chemical usage detected.")
