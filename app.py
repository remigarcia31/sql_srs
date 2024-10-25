import streamlit as st
import pandas as pd
import duckdb


data = {"a": [1, 2, 3], "b": [4, 5, 6]}
df = pd.DataFrame(data)

tab1, tab2, tab3 = st.tabs(["Page 1", "Page 2", "Page 3"])

with tab1:
    sql_query = st.text_area(label="Entrez votre requête")
    st.write(f"Votre requête : {sql_query}")
    result = duckdb.query(sql_query).df()
    st.dataframe(result)

with tab2:
    st.write("Hello world")

with tab3:
    st.write("Hello world")