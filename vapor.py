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

def vapor_app():
    st.header("💨 Vapor Emission Estimator")

    uploaded_file = st.file_uploader("Upload vapor-related utility bill", type=["pdf", "png", "jpg", "jpeg", "txt"])

    if uploaded_file:
        with st.spinner("Analyzing vapor usage data..."):
            content = extract_text(uploaded_file)
            st.text_area("Extracted Text", content, height=200)

            keywords = ["vapor", "steam", "cubic meters", "m3"]
            if contains_keywords(content, keywords):
                matches = re.findall(r"\d+\.?\d*", content)
                units = sum([float(m) for m in matches])

                # Assumed emission factor for industrial vapor: 0.0004 kg CO2 per cubic meter
                emission = round(units * 0.0004, 4)

                st.success(f"Estimated Emission from Vapor Usage: {emission} kg CO2")

                # 🎯 Bar Chart with Two Bars
                fig, ax = plt.subplots()
                ax.bar(["Vapor Usage (m³)", "Emission (kg CO2)"], [units, emission], color=["skyblue", "green"])
                ax.set_title("Vapor Usage Emission Summary")
                st.pyplot(fig)

                filename = generate_pdf_report(
                    "Vapor Emission Report", units, emission,
                    unit_label="m³", gas_label="kg CO2"
                )

                with open(filename, "rb") as f:
                    st.download_button("📄 Download PDF Report", f, file_name=filename)
            else:
                st.warning("No vapor-related keywords found in the uploaded bill.")
