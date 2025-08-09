import streamlit as st
import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import re
import matplotlib.pyplot as plt
from datetime import datetime
from report_generator import generate_pdf_report

# --- MODULE DEFINITIONS (rename 'Fuel' to 'Fuel Emission' for clarity) ---
MODULES = {
    "Carbon": {
        "keywords": ["electricity", "power", "kwh", "energy", "consumption", "meter", "total units",
                     "tariff", "reading", "supply", "unit price", "rate", "amount", "charge",
                     "billing period", "account no", "bill no", "meter no"],
        "factor": 0.82,
        "unit": "kWh",
        "gas": "kg CO2"
    },
    "Methane": {
        "keywords": ["biogas", "manure", "livestock", "digestor", "slurry", "methane", "animal",
                     "dung", "biogas produced", "gas volume", "gas yield"],
        "factor": 0.0009,
        "unit": "kg",
        "gas": "kg CH4"
    },
    "Nitrous Oxide": {
        "keywords": ["fertilizer", "n2o", "nitrous", "urea", "ammonium", "application", "soil",
                     "dap", "no3", "nh4", "nitrogen", "fertilizer kg", "manure nitrogen"],
        "factor": 0.0056,
        "unit": "kg",
        "gas": "kg N2O eq"
    },
    "Water Usage": {
        "keywords": ["water", "litre", "liter", "litres", "kl", "kilolitre", "flow", "tank",
                     "meter reading", "irrigation", "consumption", "pump", "meter"],
        "factor": 0.0003,
        "unit": "litres",
        "gas": "kg CO2 eq"
    },
    "Vapor": {
        "keywords": ["vapor", "vapour", "evaporation", "steam", "condensate", "boiler", "evaporator",
                     "tonnes of steam", "steam trap", "flue", "condensation", "latent heat"],
        "factor": 0.007,
        "unit": "m3",
        "gas": "kg CO2"
    },
    "Plant Intake": {
        "keywords": ["tree", "sapling", "planted", "plantation", "afforestation", "reforestation", "trees planted"],
        "factor": -21.77,   # kg CO2 absorbed per tree (use as example; keep negative)
        "unit": "trees",
        "gas": "kg CO2 (absorbed)"
    },
    "Fuel Emission": {
        "keywords": ["diesel", "petrol", "fuel", "volume", "litres", "liter", "ltrs", "qty", "quantity",
                     "density", "unit price", "rate", "amount", "receipt", "nozzle", "tank", "pump", "bunk"],
        "factor": 2.68,   # kg CO2 per litre diesel (approx India avg)
        "unit": "litres",
        "gas": "kg CO2"
    }
}

# Helper --> parse numeric strings robustly (handle commas, dots)
def _parse_number(token: str):
    tok = token.replace(',', '')  # remove thousands separators
    try:
        return float(tok)
    except:
        return None

# Extract numbers in a line (returns list of floats)
def numbers_from_text(s: str):
    tokens = re.findall(r'\d+[.,]?\d*', s)
    nums = []
    for t in tokens:
        v = _parse_number(t)
        if v is not None:
            nums.append(v)
    return nums

# Read text from uploaded file (pdf/image/txt)
def extract_text(uploaded_file):
    file_type = uploaded_file.type.lower() if hasattr(uploaded_file, "type") else ""
    try:
        if "pdf" in file_type:
            raw = uploaded_file.read()
            doc = fitz.open(stream=raw, filetype="pdf")
            return "\n".join([page.get_text() for page in doc])
        elif "image" in file_type or uploaded_file.name.lower().endswith((".png", ".jpg", ".jpeg")):
            image = Image.open(uploaded_file)
            return pytesseract.image_to_string(image)
        elif "text" in file_type or uploaded_file.name.lower().endswith(".txt"):
            return uploaded_file.read().decode("utf-8", errors="ignore")
        else:
            # fallback: try reading and OCR if binary
            try:
                image = Image.open(uploaded_file)
                return pytesseract.image_to_string(image)
            except:
                return uploaded_file.read().decode("utf-8", errors="ignore")
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return ""

# The algorithm:
# - Split file into lines
# - For each line, find which modules' keywords appear (count occurrences)
# - Assign numbers in that line to the module with highest keyword hits (tie -> first)
# - If no numbers in matched line, look +/-2 lines for numbers
def assign_usage_per_module(content: str):
    module_usage = {name: 0.0 for name in MODULES.keys()}
    lines = content.splitlines()
    lowered_lines = [L.lower() for L in lines]

    for idx, line in enumerate(lowered_lines):
        # count keyword matches per module
        module_counts = {}
        for mname, cfg in MODULES.items():
            cnt = 0
            for kw in cfg["keywords"]:
                cnt += line.count(kw.lower())
            if cnt > 0:
                module_counts[mname] = cnt

        if not module_counts:
            continue  # no module keywords on this line

        # choose module with highest count for this line
        chosen_module = max(module_counts.items(), key=lambda x: (x[1], -list(MODULES.keys()).index(x[0])))[0]

        nums = numbers_from_text(line)
        # If no numbers in this exact line, look nearby (prev/next up to 2 lines)
        if not nums:
            for offset in (1, -1, 2, -2):
                nidx = idx + offset
                if 0 <= nidx < len(lowered_lines):
                    nearby_nums = numbers_from_text(lowered_lines[nidx])
                    if nearby_nums:
                        nums = nearby_nums
                        break

        if nums:
            module_usage[chosen_module] += sum(nums)

    return module_usage

# Streamlit UI
def total_dashboard():
    st.header("🌍 Total Emission Dashboard")

    uploaded_file = st.file_uploader("Upload any bill (PDF/Image/TXT)", type=["pdf", "png", "jpg", "jpeg", "txt"])

    if not uploaded_file:
        st.info("Upload a bill to analyze. The dashboard always shows all modules on X-axis but bars appear only for matched items.")
        return

    content = extract_text(uploaded_file)
    if not content.strip():
        st.warning("Could not extract text from this file. Try a clearer scan or a PDF with embedded text.")
        return

    st.text_area("📄 Extracted Text (preview)", content, height=220)

    # assign usage values module-by-module
    module_usage = assign_usage_per_module(content)

    # compute emissions
    module_emission = {}
    for name, usage in module_usage.items():
        factor = MODULES[name]["factor"]
        emission = round(usage * factor, 2)
        # For Plant Intake negative factor is expected (absorption). Keep emission as-is.
        # For safety: clamp tiny negatives due to float noise to 0 for non-plant modules
        if name != "Plant Intake" and emission < 0 and abs(emission) < 1e-6:
            emission = 0.0
        module_emission[name] = emission

    # Build ordered lists for plotting (keep full module order)
    module_names = list(MODULES.keys())
    usage_values = [module_usage.get(n, 0.0) for n in module_names]
    emission_values = [module_emission.get(n, 0.0) for n in module_names]

    # If nothing matched, inform user
    if all(v == 0 for v in usage_values) and all(v == 0 for v in emission_values):
        st.warning("❌ No relevant emission data found in uploaded bill.")
        return

    st.success("✅ Emission calculated for matched modules (see chart below).")

    # Chart
    fig, ax = plt.subplots(figsize=(10, 5))
    x = list(range(len(module_names)))
    ax.bar([i - 0.2 for i in x], usage_values, width=0.4, label="Usage")
    ax.bar([i + 0.2 for i in x], emission_values, width=0.4, label="Emission")
    ax.set_xticks(x)
    ax.set_xticklabels(module_names, rotation=30)
    ax.set_ylabel("Values (module units / emission in kg)")
    ax.set_title("Usage vs Emission by Module")
    ax.legend()

    # Set y-limits so zero is at the bottom (unless negative absorption exists)
    all_vals = usage_values + emission_values
    y_min = min(all_vals)
    y_max = max(all_vals)
    # If plant intake negative, allow bottom to show negative; otherwise bottom = 0
    if y_min < 0:
        ax.set_ylim(bottom=y_min * 1.2, top=max(10, y_max * 1.1))
    else:
        ax.set_ylim(bottom=0, top=max(10, y_max * 1.1))

    st.pyplot(fig)

    # Summary table
    st.subheader("Module results")
    for name in module_names:
        if usage_values[module_names.index(name)] > 0 or emission_values[module_names.index(name)] != 0:
            st.write(f"**{name}** — Usage: `{usage_values[module_names.index(name)]}` {MODULES[name]['unit']} • Emission: `{emission_values[module_names.index(name)]}` {MODULES[name]['gas']}")
        else:
            st.write(f"**{name}** — *No data matched*")

    # PDF download (Total)
    if st.button("📄 Download Total Emission PDF"):
        total_units = sum(usage_values)
        total_emission = sum(emission_values)
        # use ASCII gas label for report to avoid encoding issues
        filename = generate_pdf_report(
            "Total Emission Summary Report",
            total_units,
            total_emission,
            unit_label="units",
            gas_label="kg CO2"
        )
        with open(filename, "rb") as f:
            st.download_button("📥 Download PDF", data=f, file_name=filename, mime="application/pdf")
