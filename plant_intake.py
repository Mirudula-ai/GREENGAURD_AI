import streamlit as st
import pytesseract
from PIL import Image
import fitz  
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

def plant_intake_app():
    st.header("🌿 Plant Intake Estimator (CO2 Absorption)")

    uploaded_file = st.file_uploader("Upload relevant document (PDF/Image/TXT)", type=["pdf", "png", "jpg", "jpeg", "txt"])

    if uploaded_file:
        with st.spinner("Processing file and detecting sapling/plant intake..."):
            content = extract_text(uploaded_file)
            st.text_area("Extracted Text", content, height=200)

            keywords = ["sapling", "tree", "planted", "green cover"]
            if contains_keywords(content, keywords):
                numbers = re.findall(r"\d+\.?\d*", content)
                saplings = sum([float(num) for num in numbers])

                # IPCC-estimated CO2 absorption: 21.77 kg/year per sapling
                absorbed = round(saplings * 21.77, 2)

                st.success(f"Estimated CO2 Absorbed: {absorbed} kg CO2 by {saplings} saplings")

                filename = generate_pdf_report(
                    "Plant Intake Report", saplings, absorbed,
                    unit_label="saplings", gas_label="kg CO2 absorbed"
                )

                with open(filename, "rb") as f:
                    st.download_button("📄 Download PDF Report", f, file_name=filename)

                # Visualization
                fig, ax = plt.subplots()
                ax.bar(["Saplings", "CO2 Absorbed"], [saplings, absorbed], color=["#4CAF50", "#2E7D32"])
                ax.set_title("Plant Intake Overview")
                st.pyplot(fig)
            else:
                st.warning("This document does not appear to contain sapling or plantation data.")
