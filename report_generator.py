from fpdf import FPDF
from datetime import datetime

def generate_pdf_report(title, units, emission, unit_label="units", gas_label="kg CO2"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename = f"{title.replace(' ', '_')}_{timestamp.replace(':','-').replace(' ', '_')}.pdf"

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16)
    pdf.cell(200, 10, txt="GreenGuard AI", ln=1, align="C")

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=title, ln=1, align="C")
    pdf.cell(200, 10, txt=f"Generated on: {timestamp}", ln=1, align="C")

    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, f"Total Units Detected: {units} {unit_label}")
    pdf.multi_cell(0, 10, f"Estimated Emissions: {emission} {gas_label}")

    try:
        pdf.output(filename)
    except UnicodeEncodeError:
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, "⚠ Unicode characters were removed due to encoding issues.")
        pdf.output(filename, 'F')
    return filename
