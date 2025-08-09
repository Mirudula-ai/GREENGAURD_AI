import streamlit as st
import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import re
from report_generator import generate_pdf_report
import matplotlib.pyplot as plt

def extract_text(uploaded_file):
    file_type = uploaded_file.type
    if "pdf" in file_type:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        return "\n".join([page.get_text() for page in doc])
    elif "image" in file_type:
        image = Image.open(uploaded_file)
        return pytesseract.image_to_string(image)
    elif "text" in file_type:
        return uploaded_file.read().decode("utf-8", errors="ignore")
    return ""

def contains_keywords(text, keywords):
    return any(word.lower() in text.lower() for word in keywords)

def water_usage_app():
    st.header("🚿 Water Usage Emission Estimator")

    uploaded_file = st.file_uploader("Upload water usage bill", type=["pdf", "png", "jpg", "jpeg", "txt"])

    if uploaded_file:
        with st.spinner("Analyzing water usage data..."):
            content = extract_text(uploaded_file)
            st.text_area("Extracted Text", content, height=200)

            keywords = ["water", "litres", "liters", "usage", "consumption"]
            if contains_keywords(content, keywords):
                matches = re.findall(r"\d+\.?\d*", content)
                units = sum([float(m) for m in matches])

                # Water usage emission factor (assumed): 0.0003 kg CO2 per litre
                emission = round(units * 0.0003, 4)

                st.success(f"Estimated Emission from Water Usage: {emission} kg CO2")

                # 🎯 Bar Chart with Two Bars
                fig, ax = plt.subplots()
                ax.bar(["Water Usage (litres)", "Emission (kg CO2)"], [units, emission], color=["blue", "orange"])
                ax.set_title("Water Usage Emission Summary")
                st.pyplot(fig)

                filename = generate_pdf_report(
                    "Water Usage Emission Report", units, emission,
                    unit_label="litres", gas_label="kg CO2"
                )

                with open(filename, "rb") as f:
                    st.download_button("📄 Download PDF Report", f, file_name=filename)
            else:
                st.warning("No water-related keywords found in the uploaded file.")
