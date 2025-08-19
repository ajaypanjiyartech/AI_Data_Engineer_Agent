import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(page_title="AI Data Engineer Agent", layout="wide")

st.title("⚡ AI Data Engineer Agent")

# Tabs for different tools
tab1, tab2 = st.tabs(["📊 Data Validation & Processing", "📝 Text Comparison Tool"])

# -------------------------
# TAB 1: DATA VALIDATION
# -------------------------
with tab1:
    # File type selector
    file_type = st.selectbox(
        "Select File Type",
        ["csv", "parquet", "json"],
        help="Choose the type of file you want to upload"
    )

    # File uploader (dynamic extensions)
    extensions = {"csv": ["csv"], "parquet": ["parquet"], "json": ["json"]}
    uploaded_file = st.file_uploader(f"Upload {file_type.upper()} file", type=extensions[file_type])

    if uploaded_file:
        # Read file based on selection
        try:
            if file_type == "csv":
                df = pd.read_csv(uploaded_file)
            elif file_type == "parquet":
                df = pd.read_parquet(uploaded_file)
            elif file_type == "json":
                df = pd.read_json(uploaded_file, lines=True)  # handles JSONL too
            st.success(f"✅ {file_type.upper()} file uploaded successfully!")
        except Exception as e:
            st.error(f"❌ Error reading file: {e}")
            st.stop()

        # Preview dataset
        st.subheader("Preview of Dataset")
        st.dataframe(df.head())

        # Checkbox options
        st.subheader("Select Validation Checks")
        check_missing = st.checkbox("Check Missing Values")
        check_duplicates = st.checkbox("Check Duplicate Rows")
        check_outliers = st.checkbox("Check Outliers (IQR)")

        report = {}

        # Missing values check
        if check_missing:
            missing_report = df.isnull().sum()
            report["Missing Values"] = missing_report[missing_report > 0].to_dict()

        # Duplicates check
        if check_duplicates:
            duplicate_count = df.duplicated().sum()
            report["Duplicate Rows"] = duplicate_count

        # Outliers check
        if check_outliers:
            numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns
            outlier_summary = {}
            for col in numeric_cols:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                outliers = df[(df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))][col]
                if not outliers.empty:
                    outlier_summary[col] = len(outliers)
            report["Outliers"] = outlier_summary

        # Display report
        if report:
            st.subheader("📊 Data Validation Report")
            for key, value in report.items():
                st.write(f"**{key}:**", value)

            # Fixing section
            st.subheader("⚒️ Fix Data Issues")
            if check_missing and "Missing Values" in report:
                if st.button("Fill Missing with Mean (numeric only)"):
                    for col in df.select_dtypes(include=["int64", "float64"]).columns:
                        df[col].fillna(df[col].mean(), inplace=True)
                    st.success("✅ Missing values filled with mean!")

            if check_duplicates and "Duplicate Rows" in report:
                if st.button("Remove Duplicate Rows"):
                    df.drop_duplicates(inplace=True)
                    st.success("✅ Duplicates removed!")

            if check_outliers and "Outliers" in report:
                if st.button("Remove Outliers"):
                    for col in report["Outliers"].keys():
                        Q1 = df[col].quantile(0.25)
                        Q3 = df[col].quantile(0.75)
                        IQR = Q3 - Q1
                        df = df[(df[col] >= (Q1 - 1.5 * IQR)) & (df[col] <= (Q3 + 1.5 * IQR))]
                    st.success("✅ Outliers removed!")

            # Download final processed report
            st.subheader("📥 Download Processed Data")
            if file_type == "csv":
                output = df.to_csv(index=False).encode("utf-8")
                st.download_button("Download CSV", output, "processed_dataset.csv", "text/csv")
            elif file_type == "parquet":
                output = df.to_parquet(index=False)
                st.download_button("Download Parquet", output, "processed_dataset.parquet")
            elif file_type == "json":
                output = df.to_json(orient="records", lines=True).encode("utf-8")
                st.download_button("Download JSON", output, "processed_dataset.json", "application/json")

# -------------------------
# TAB 2: TEXT COMPARISON TOOL
# -------------------------
with tab2:
    st.subheader("Text Comparison Tool")

    # Load your local HTML file from text-comparison-tool folder
    try:
        with open("text-comparison-tool/index.html", "r", encoding="utf-8") as f:
            html_code = f.read()
        components.html(html_code, height=800, scrolling=True)
    except FileNotFoundError:
        st.error("⚠️ Text Comparison Tool files not found. Please place 'index.html' inside 'text-comparison-tool' folder.")
