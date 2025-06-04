
import streamlit as st
import pandas as pd
import re
from docx import Document

# Reference price sheet
price_sheet = {
    "CLUB CHAIR": 40, "OTTOMAN": 30, "CHAIR & OTTOMAN": 60, "LOVESEAT / CHAISE": 75,
    "SOFA UP TO: 7'": 75, "SOFA UP TO: 8'": 100, "SOFA UP TO: 9'": 125, "SOFA UP TO: 10'": 150,
    "SIDE TABLE / NIGHTSTAND": 30, "COCKTAIL TABLE UP TO 48\"": 50
}

def extract_items_from_excel(uploaded_file):
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip().str.upper()
    items = []
    for _, row in df.iterrows():
        name = str(row.get("ITEM", row.get("DESCRIPTION", ""))).upper()
        qty = int(row.get("QUANTITY", row.get("QTY", 1)))
        items.append((name, qty))
    return items

def extract_items_from_word(uploaded_file):
    doc = Document(uploaded_file)
    lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    items = []
    for line in lines:
        match = re.match(r"(\d+)\s*[-–]\s*(.+)", line.strip())
        if match:
            qty = int(match.group(1))
            name = match.group(2).strip().upper()
            items.append((name, qty))
    return items

def map_item_category(name):
    name = name.upper()
    if "SOFA" in name:
        if "10" in name:
            return "SOFA UP TO: 10'"
        elif "9" in name:
            return "SOFA UP TO: 9'"
        elif "8" in name:
            return "SOFA UP TO: 8'"
        else:
            return "SOFA UP TO: 7'"
    elif "LOVESEAT" in name or "CHAISE" in name:
        return "LOVESEAT / CHAISE"
    elif "OTTOMAN" in name:
        return "OTTOMAN"
    elif "CHAIR" in name:
        return "CLUB CHAIR"
    elif "SIDE TABLE" in name or "NIGHTSTAND" in name:
        return "SIDE TABLE / NIGHTSTAND"
    elif "COFFEE TABLE" in name or "COCKTAIL" in name:
        return "COCKTAIL TABLE UP TO 48\""
    else:
        return "CLUB CHAIR"

st.title("📄 Furniture Charges Calculator (Excel/Word Upload Only)")

uploaded_file = st.file_uploader("Upload a furniture list (Excel or Word)", type=["xls", "xlsx", "docx"])

if uploaded_file:
    if uploaded_file.name.endswith((".xls", ".xlsx")):
        item_list = extract_items_from_excel(uploaded_file)
    elif uploaded_file.name.endswith(".docx"):
        item_list = extract_items_from_word(uploaded_file)
    else:
        st.error("Unsupported file format.")

    if item_list:
        furniture_data = []
        for name, qty in item_list:
            category = map_item_category(name)
            unit_price = price_sheet.get(category, 40)
            furniture_data.append([name, qty, category, unit_price, 1])  # Default 1 month

        df = pd.DataFrame(furniture_data, columns=[
            "Item", "Quantity", "Rate Category", "Unit Price", "Storage Duration (Months)"
        ])

        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

        if st.button("Calculate Charges"):
            edited_df["Receiving Total"] = edited_df["Quantity"] * edited_df["Unit Price"]
            edited_df["Storage Total"] = edited_df["Quantity"] * edited_df["Unit Price"] * edited_df["Storage Duration (Months)"]
            st.subheader("Results")
            st.dataframe(edited_df, use_container_width=True)
            st.markdown(f"**Total Receiving Charges:** ${edited_df['Receiving Total'].sum():,.2f}")
            st.markdown(f"**Total Storage Charges:** ${edited_df['Storage Total'].sum():,.2f}")
