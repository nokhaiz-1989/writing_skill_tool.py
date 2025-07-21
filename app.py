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

# Function to convert DataFrame to Excel bytes
def to_excel_bytes(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

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
                fig, ax = plt.subplots(figsize=(12, 8))
                ax.bar(diag_counts.index, diag_counts.values, color=[SEGMENTS[seg]['color'] for seg in SEGMENT_LABELS])
                ax.set_ylabel("Number of Students", fontsize=14)
                ax.set_title("Diagnostic Segment Distribution", fontsize=14)
                ax.tick_params(axis='x', labelsize=14)
                ax.tick_params(axis='y', labelsize=14)
                st.pyplot(fig)

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

                        st.subheader("📘 Post-Test Summary")
                        post_counts = df['Post_Segment'].value_counts().reindex(SEGMENT_LABELS, fill_value=0)
                        fig2, ax2 = plt.subplots(figsize=(12, 8))
                        ax2.bar(post_counts.index, post_counts.values, color=[SEGMENTS[seg]['color'] for seg in SEGMENT_LABELS])
                        ax2.set_ylabel("Number of Students", fontsize=14)
                        ax2.set_title("Post-Test Segment Distribution", fontsize=14)
                        ax2.tick_params(axis='x', labelsize=14)
                        ax2.tick_params(axis='y', labelsize=14)
                        st.pyplot(fig2)

                        st.header("📈 Step 4: Comparative Visualization")
                        compare_df = pd.DataFrame({
                            'Diagnostic': diag_counts,
                            'Post-Test': post_counts
                        })
                        compare_df.index.name = "Segment"
                        compare_df = compare_df.loc[SEGMENT_LABELS]
                        fig3, ax3 = plt.subplots(figsize=(12, 8))
                        compare_df.plot(kind='bar', color=['gray', 'black'], ax=ax3)
                        ax3.set_ylabel("Number of Students", fontsize=14)
                        ax3.set_title("Comparison: Diagnostic vs Post-Test", fontsize=14)
                        ax3.tick_params(axis='x', labelsize=14)
                        ax3.tick_params(axis='y', labelsize=14)
                        st.pyplot(fig3)

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
                        fig4, ax4 = plt.subplots(figsize=(12, 8))
                        act_df.plot(kind='line', ax=ax4)
                        ax4.set_ylabel("Number of Students", fontsize=14)
                        ax4.set_title("Activity-wise Segment Counts", fontsize=14)
                        ax4.tick_params(axis='x', labelsize=14)
                        ax4.tick_params(axis='y', labelsize=14)
                        st.pyplot(fig4)

                        st.subheader("🔥 Student Segment Shifts: Diagnostic → Post-Test")
                        shift_matrix = pd.crosstab(df['Segment'], df['Post_Segment'])
                        fig5, ax5 = plt.subplots(figsize=(12, 8))
                        sns.heatmap(shift_matrix, annot=True, fmt='d', cmap="YlGnBu", ax=ax5)
                        st.pyplot(fig5)

                        st.download_button(
                            label="📥 Download Final Data as Excel",
                            data=to_excel_bytes(df),
                            file_name="student_performance_summary.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

                        st.success("🎉 GOOD WORK")

    except Exception as e:
        st.error(f"❌ Error: {e}")
