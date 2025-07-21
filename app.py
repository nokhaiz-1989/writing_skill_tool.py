import streamlit as st
import pandas as pd

# Page setup
st.set_page_config(page_title="Student Score Segmentation", layout="centered")
st.title("📘 Student Score Upload & Segmentation")
st.write("Upload an Excel file with Student IDs and Scores.")

# Segment definition with color mapping
SEGMENTS = {
    "Minimal": {"range": (0, 20), "color": "#FF0000"},           # Red
    "Needs Improvement": {"range": (21, 40), "color": "#FFA500"},# Orange
    "Developing": {"range": (41, 60), "color": "#FFFF00"},       # Yellow
    "Proficient": {"range": (61, 80), "color": "#0000FF"},       # Blue
    "Exemplary": {"range": (81, 100), "color": "#00FF00"}        # Green
}

# Function to determine segment
def assign_segment(score):
    for segment, detail in SEGMENTS.items():
        if detail["range"][0] <= score <= detail["range"][1]:
            return segment
    return "Invalid"

# Upload file
uploaded_file = st.file_uploader("📂 Upload Excel File (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)

        # Clean and validate columns
        df.columns = df.columns.str.strip()
        if 'ID' not in df.columns or 'Score' not in df.columns:
            st.error("❌ Excel must contain columns: 'ID' and 'Score'")
        else:
            # Validate ID format and score range
            df['Valid_ID'] = df['ID'].apply(lambda x: isinstance(x, str) and x.startswith("STD-") and x[4:].isdigit())
            df['Valid_Score'] = df['Score'].apply(lambda x: isinstance(x, (int, float)) and 0 <= x <= 100)

            if not df['Valid_ID'].all() or not df['Valid_Score'].all():
                st.error("❌ Invalid ID format or score outside 0–100 range.")
            else:
                # Assign segments and colors
                df['Segment'] = df['Score'].apply(assign_segment)
                df['Color'] = df['Segment'].map(lambda seg: SEGMENTS[seg]['color'] if seg in SEGMENTS else "#FFFFFF")

                # Display styled DataFrame
                st.success("✅ GOOD WORK")
                st.dataframe(df[['ID', 'Score', 'Segment']].style.apply(
                    lambda row: [f"background-color: {df.at[row.name, 'Color']}"]*3, axis=1
                ))

    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
