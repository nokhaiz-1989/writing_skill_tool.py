import streamlit as st
import pandas as pd

# Set up Streamlit page config
st.set_page_config(page_title="Student Score Analysis", layout="wide")
st.title("📊 Student Score Analysis with Color-Coded Segmentation")

# Color and Segment Mapping
SEGMENTS = {
    "Minimal": {"range": (0, 20), "color": "#FF0000"},           # Red
    "Needs Improvement": {"range": (21, 40), "color": "#FFA500"},# Orange
    "Developing": {"range": (41, 60), "color": "#FFFF00"},       # Yellow
    "Proficient": {"range": (61, 80), "color": "#0000FF"},       # Blue
    "Exemplary": {"range": (81, 100), "color": "#00FF00"}        # Green
}

# Function to determine segment based on score
def get_segment(score):
    for segment, data in SEGMENTS.items():
        low, high = data["range"]
        if low <= score <= high:
            return segment
    return "Invalid"

# Upload Section
st.subheader("📥 Upload Excel File")
uploaded_file = st.file_uploader("Upload Excel file with columns: ID, Score", type=["xlsx"])

if uploaded_file:
    try:
        # Read file
        df = pd.read_excel(uploaded_file)

        # Strip and check columns
        df.columns = df.columns.str.strip()
        if 'ID' not in df.columns or 'Score' not in df.columns:
            st.error("❌ The Excel file must contain 'ID' and 'Score' columns.")
        else:
            # Validate IDs and scores
            valid_ids = df['ID'].apply(lambda x: str(x).startswith("STD-") and len(x) == 7)
            valid_scores = df['Score'].apply(lambda x: isinstance(x, (int, float)) and 0 <= x <= 100)

            if not valid_ids.all():
                st.warning("⚠️ Some IDs do not match the required format 'STD-001' to 'STD-100'.")
            if not valid_scores.all():
                st.warning("⚠️ Some scores are not valid integers between 0 and 100.")

            if valid_ids.all() and valid_scores.all():
                # Assign segments
                df['Segment'] = df['Score'].apply(get_segment)
                df['Color'] = df['Segment'].map(lambda x: SEGMENTS[x]['color'] if x in SEGMENTS else '#FFFFFF')

                st.subheader("📋 Colored Student Segment Table")
                st.dataframe(
                    df.style.apply(
                        lambda x: [f'background-color: {c}' for c in x['Color']], axis=1
                    )
                )

                # Segment Summary
                st.subheader("📈 Segment Count")
                segment_counts = df['Segment'].value_counts().reindex(SEGMENTS.keys(), fill_value=0)
                st.bar_chart(segment_counts)

    except Exception as e:
        st.error(f"❌ Failed to process file: {e}")
