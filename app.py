import streamlit as st
from carbon import carbon_app
from methane import methane_app
from nitrous import nitrous_app
from vapor import vapor_app
from water_usage import water_usage_app
from plant_intake import plant_intake_app
from total_dashboard import total_dashboard
import pytesseract
import shutil

path = shutil.which("tesseract")
if path:
    pytesseract.pytesseract.tesseract_cmd = path
else:
    st.error("Tesseract not found on server—OCR will not work.")

st.set_page_config(page_title="GREEN GAURD AI", layout="centered")

# Sidebar navigation
st.sidebar.title("🌿 GreenGuard AI")
option = st.sidebar.radio("Choose a Module:", [
    "🏠 Home",
    "🏆 Total emission",
    "⚡ Carbon Emission",
    "💨 Methane Emission",
    "☘ Nitrous Oxide Emission",
    "💧 Vapor Emission",
    "🚿 Water Usage Emission",
    "🌱 Plant Intake"
])

# Home page with styled boxes
if option == "🏠 Home":
    st.title("🌿 GreenGuard AI")
    st.subheader("Real-Time AI-powered emissions tracking platform. ")

    # Top motivational quote (big, bold, attractive)
    st.markdown("""
    <div style="text-align:center;font-size:28px;font-weight:bold;color:#2e7d32;margin-bottom:20px;">
    🌎 " LEAVE ONLY FOOTPRINTS,NOT EMISSION."
    </div>
    """, unsafe_allow_html=True)

    # Intro box
    st.markdown("""
    <div style="background-color:#e8f5e9;padding:15px;border-radius:10px;">
    <b>GreenGuard AI</b> is a <b>real-time, AI-powered emissions tracking platform</b> that uses 
    <b>OCR technology</b> to read your utility bills, fuel receipts, and industrial records — instantly calculating your environmental footprint.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")
    
    # Total emission box
    st.markdown("""
    <div style="background-color:#e3f2fd;padding:15px;border-radius:10px;">
    <h4>📊 Total Emission</h4>
    <p><b>The most versatile module</b> — calculates emissions from <b>any source</b>, including:</p>
    <ul>
        <li>Household electricity</li>
        <li>Diesel bills</li>
        <li>Transportation fuel</li>
    </ul>
    Perfect for <b>personal and business use</b>.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")

    # Industry modules box
    st.markdown("""
    <div style="background-color:#fff3e0;padding:15px;border-radius:10px;">
    <h4>🏭 Industry-Only Modules</h4>
    <p>Specialized modules for <b>manufacturing, agriculture, and energy sectors</b>:</p>
    <ul>
        <li>⚡ Carbon Emission</li>
        <li>💨 Methane Emission</li>
        <li>☘ Nitrous Oxide Emission</li>
        <li>💧 Vapor Emission</li>
        <li>🚿 Water Usage</li>
        <li>🌱 Plant Intake</li>
    </ul>
    These use <b>scientifically accurate</b> emission factors for precision monitoring.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")

    # Why use box
    st.markdown("""
    <div style="background-color:#f3e5f5;padding:15px;border-radius:10px;">
    <h4>🌎 Why Use GreenGuard AI?</h4>
    Together, these modules provide a <b>complete picture</b> of your environmental impact,
    helping you make <b>informed, eco-friendly decisions</b>.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")

    # Bottom motivational quote (big, bold, attractive)
    st.markdown("""
    <div style="text-align:center;font-size:28px;font-weight:bold;color:#1565c0;margin-top:20px;">
    🏆 "ZERO CARBON, 100% PROGRESS."
    </div>
    """, unsafe_allow_html=True)

# Other modules unchanged
elif option == "🏆 Total emission":
    total_dashboard()
elif option == "⚡ Carbon Emission":
    carbon_app()
elif option == "💨 Methane Emission":
    methane_app()
elif option == "☘ Nitrous Oxide Emission":
    nitrous_app()
elif option == "💧 Vapor Emission":
    vapor_app()
elif option == "🚿 Water Usage Emission":
    water_usage_app()
elif option == "🌱 Plant Intake":
    plant_intake_app()
