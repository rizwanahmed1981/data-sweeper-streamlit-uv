# -*- coding: utf-8 -*-
# Imports
import streamlit as st #st is the shortcut of streamlit module
import pandas as pd #pd is the shortcut of pandas module
import os  # for file paths
from io import BytesIO  # for file handling
import xlsxwriter  # for Excel file handling

# Set up our App
st.set_page_config(page_title="💿 Data Sweeper", layout="wide")
st.title("💿 Data Sweeper")
st.write("This app Transforms Your Files from CSV to Excell With Built in Data Cleaning and Visualization!")

uploaded_files = st.file_uploader("Upload your files (CSV or Excell):", type=["csv", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()


        if file_ext == ".csv":
            df = pd.read_csv(file)
        elif file_ext == ".xlsx":
            try:
                df = pd.read_excel(file, engine='openpyxl')
            except Exception as e:
                st.error(f"Error reading Excel file: {str(e)}")
                continue
        else:
            st.error(f"Unsupported file type: {file_ext}")
            continue

        # Check if DataFrame is empty
        if df.empty:
            st.error(f"The file {file.name} is empty or could not be read properly.")
            continue

        #Display info about the file
        st.write(f"**File Name: ** {file.name}")
        st.write(f"** File Size: ** {file.size/1024}")

        #show five rows of our data 
        st.write("Preview the Head of the DataFrame")
        st.dataframe(df.head())

        #Options for Date Cleaning
        st.subheader("Data Cleaning Options")
        if st.checkbox(f"Clean Data for {file.name}"):
            col1, col2 = st.columns(2)
 
            with col1:
                if st.button(f"Remove Duplcates from {file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.write("Duplicates Removed")

            with col2:
                if st.button(f"fill Missing Values {file.name}"):
                    # Get numeric columns
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    # Fill numeric columns with mean
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    # Fill non-numeric columns with mode (most frequent value)
                    non_numeric_cols = df.select_dtypes(exclude=['number']).columns
                    for col in non_numeric_cols:
                        df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else '')
                    st.write("Missing Values Have Been Filled")
                    # Show number of missing values after filling
                    st.write("Number of missing values after filling:", df.isnull().sum().sum())
                    # Show updated dataframe
                    st.write("Updated DataFrame Preview:")
                    st.dataframe(df.head())
                    
                    # Store the modified dataframe in session state
                    st.session_state[f'df_{file.name}'] = df

        # Use the modified dataframe from session state if it exists
        if f'df_{file.name}' in st.session_state:
            df = st.session_state[f'df_{file.name}']

        #Choose Specific Columns to Convert
        st.subheader("Select Columns to Convert")
        columns = st.multiselect(f"Choose Columns for {file.name}", df.columns, default=df.columns)
        df = df[columns]


        #Create some Visualizations
        st.subheader("📊 Data visualization")
        if st.checkbox(f"Show Visualization for {file.name}"):
            st.bar_chart(df.select_dtypes(include= 'number').iloc[:,:2])




        #convert the file -> CSV to Excel
        st.subheader("🔃 Conversion Options")
        conversion_type = st.radio(f"Convert {file.name} to:", ["CSV","Excel"], key=file.name)
        if st.button(f"convert {file.name}"):
            buffer = BytesIO()
            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                file_name = file.name.replace(file_ext, ".csv")
                mime_type = "text/csv"

            elif conversion_type == "Excel":
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Sheet1')
                file_name = file.name.replace(file_ext, ".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            buffer.seek(0)

            #Download Button
            st.download_button(
                label=f"⏬ Download {file.name} as {conversion_type}",
                data=buffer,
                file_name=file_name,
                mime=mime_type
            )


st.success("🎈🎉All Files Converted 🎉🎈")