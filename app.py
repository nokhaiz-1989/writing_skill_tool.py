import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

st.set_page_config(page_title="Student Performance Analyzer", layout="wide")
st.title("📘 Student Performance Segmentation and Analysis")

# Segment and Color Mapping
SEGMENTS = {
    "Minimal": {"range": (0, 20), "color": "#FF0000"},
    "Needs Improvement": {"range": (21, 40), "color": "#FFA500"},
    "Developing": {"range": (41, 60), "color": "#FFFF00"},
    "Proficient": {"range": (61, 80), "color": "#0000FF"},
    "Exemplary": {"range": (81, 100), "color": "#00FF00"}
}
SEGMENT_LABELS = list(SEGMENTS.keys())

# Assign segment based on score
def assign_segment(score):
    for segment, data in SEGMENTS.items():
        if data['range'][0] <= score <= data['range'][1]:
            return segment
    return "Invalid"

# Upload Diagnostic Test
st.header("📥 Step 1: Upload Diagnostic Scores")
diagnostic_file = st.file_uploader("Upload Excel file with columns: ID and Score", type=["xlsx"])

if diagnostic_file:
    try:
        df = pd.read_excel(diagnostic_file)
        df.columns = df.columns.str.strip()
        if 'ID' not in df.columns or 'Score' not in df.columns:
            st.error("Excel must have 'ID' and 'Score' columns.")
        else:
            df = df[['ID', 'Score']]
            df['Valid_ID'] = df['ID'].apply(lambda x: isinstance(x, str) and x.startswith("STD-") and x[4:].isdigit())
            df['Valid_Score'] = df['Score'].apply(lambda x: isinstance(x, (int, float)) and 0 <= x <= 100)

            if not df['Valid_ID'].all() or not df['Valid_Score'].all():
                st.error("Some IDs or scores are invalid.")
            else:
                df['Diagnostic'] = df['Score']
                df['Segment'] = df['Diagnostic'].apply(assign_segment)
                df['Color'] = df['Segment'].map(lambda x: SEGMENTS[x]['color'])
                st.subheader("🎨 Diagnostic Segmentation")
                st.dataframe(df[['ID', 'Diagnostic', 'Segment']].style.apply(lambda x: [f'background-color: {df.loc[x.name, "Color"]}']*3, axis=1))

                st.subheader("📊 Diagnostic Segment Summary")
                diag_counts = df['Segment'].value_counts().reindex(SEGMENT_LABELS, fill_value=0)
                st.bar_chart(diag_counts)

                # Activity Upload
                st.header("📘 Step 2: Upload Scores for 9 Activities")
                activity_scores = []
                for i in range(1, 10):
                    file = st.file_uploader(f"Upload Activity {i} (ID, Score)", type=["xlsx"], key=f"activity_{i}")
                    if file:
                        temp_df = pd.read_excel(file)
                        temp_df.columns = temp_df.columns.str.strip()
                        if 'ID' in temp_df.columns and 'Score' in temp_df.columns:
                            temp_df = temp_df[['ID', 'Score']]
                            temp_df.rename(columns={'Score': f'Activity_{i}'}, inplace=True)
                            activity_scores.append(temp_df)

                # Merge Activities with Main
                for a_df in activity_scores:
                    df = pd.merge(df, a_df, on='ID', how='left')

                # Upload Post-Test
                st.header("📘 Step 3: Upload Post-Test Scores")
                post_file = st.file_uploader("Upload Post-Test File (ID, Score)", type=["xlsx"], key="post")
                if post_file:
                    post_df = pd.read_excel(post_file)
                    post_df.columns = post_df.columns.str.strip()
                    if 'ID' in post_df.columns and 'Score' in post_df.columns:
                        post_df = post_df[['ID', 'Score']].rename(columns={'Score': 'Post_Test'})
                        df = pd.merge(df, post_df, on='ID', how='left')
                        df['Post_Segment'] = df['Post_Test'].apply(assign_segment)

                        # Post Summary
                        st.subheader("📘 Post-Test Summary")
                        post_counts = df['Post_Segment'].value_counts().reindex(SEGMENT_LABELS, fill_value=0)
                        st.bar_chart(post_counts)

                        # Comparison
                        st.header("📈 Step 4: Comparative Visualization")
                        compare_df = pd.DataFrame({
                            'Diagnostic': diag_counts,
                            'Post-Test': post_counts
                        })
                        st.bar_chart(compare_df)

                        # Activity High/Low Bar Chart
                        st.subheader("📉 Activity-wise Segment Counts")
                        act_summary = {'Minimal': [], 'Exemplary': []}
                        for col in [f'Activity_{i}' for i in range(1, 10)]:
                            if col in df.columns:
                                act_summary['Minimal'].append((df[col] <= 20).sum())
                                act_summary['Exemplary'].append((df[col] >= 81).sum())
                            else:
                                act_summary['Minimal'].append(0)
                                act_summary['Exemplary'].append(0)
                        act_df = pd.DataFrame(act_summary, index=[f'Activity_{i}' for i in range(1, 10)])
                        st.line_chart(act_df)

                        # Heatmap for Student Shift
                        st.subheader("🔥 Student Segment Shifts: Diagnostic → Post-Test")
                        shift_matrix = pd.crosstab(df['Segment'], df['Post_Segment'])
                        fig, ax = plt.subplots(figsize=(8, 6))
                        sns.heatmap(shift_matrix, annot=True, fmt='d', cmap="YlGnBu", ax=ax)
                        st.pyplot(fig)

                        st.success("🎉 GOOD WORK")

    except Exception as e:
        st.error(f"❌ Error: {e}")
