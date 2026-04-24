import streamlit as st
import requests
import pandas as pd
import plotly.express as px

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Industrial Data Dashboard", layout="wide")

st.title("📊 Data Visualization Dashboard")

uploaded_file = st.file_uploader("Upload your CSV file")

if uploaded_file:
    files = {"file": uploaded_file.getvalue()}
    res = requests.post(f"{API_URL}/upload", files=files)

    st.success("File uploaded!")

    df = pd.read_csv(uploaded_file)

    st.subheader("Dataset Preview")
    st.dataframe(df.head())

    st.subheader("Select columns for visualization")

    columns = df.columns.tolist()
    x_axis = st.selectbox("X-axis", columns)
    y_axis = st.selectbox("Y-axis", columns)

    chart_type = st.selectbox("Chart Type", ["line", "bar", "scatter"])

    if chart_type == "line":
        fig = px.line(df, x=x_axis, y=y_axis)
    elif chart_type == "bar":
        fig = px.bar(df, x=x_axis, y=y_axis)
    else:
        fig = px.scatter(df, x=x_axis, y=y_axis)

    st.plotly_chart(fig)
    
    st.subheader("📈 Key Metrics")

    col1, col2, col3 = st.columns(3)

    numeric_cols = df.select_dtypes(include='number').columns

    if len(numeric_cols) > 0:
        col = numeric_cols[0]

        col1.metric("Average", round(df[col].mean(), 2))
        col2.metric("Max", df[col].max())
        col3.metric("Min", df[col].min())

    st.sidebar.header("Filters")

    columns = df.columns.tolist()

    filter_col = st.sidebar.selectbox("Select column to filter", columns)

    if df[filter_col].dtype == 'object':
        value = st.sidebar.selectbox("Value", df[filter_col].unique())
        df = df[df[filter_col] == value]
    else:
        min_val = float(df[filter_col].min())
        max_val = float(df[filter_col].max())

        selected_range = st.sidebar.slider(
            "Range",
            min_val,
            max_val,
            (min_val, max_val)
        )

        df = df[(df[filter_col] >= selected_range[0]) & (df[filter_col] <= selected_range[1])]
    
    # Convert date if exists
    for col in df.columns:
        try:
            df[col] = pd.to_datetime(df[col])
        except:
            pass
    
    st.subheader("🚨 Machine Status")

    if "machine_status" in df.columns:
        status_counts = df["machine_status"].value_counts()
        st.bar_chart(status_counts)