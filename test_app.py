import streamlit as st
from snowflake.snowpark.session import Session
from snowflake.snowpark.functions import col
import pandas as pd
import datetime

# Initialize Snowflake session
def create_session():
    connection_parameters = {
        "account": st.secrets["snowflake"]["account"],
        "user": st.secrets["snowflake"]["user"],
        "password": st.secrets["snowflake"]["password"],
        "role": st.secrets["snowflake"]["role"],
        "warehouse": st.secrets["snowflake"]["warehouse"],
        "database": st.secrets["snowflake"]["database"],
        "schema": st.secrets["snowflake"]["schema"]
    }
    session = Session.builder.configs(connection_parameters).create()
    return session

session = create_session()

# Example variable for selected number
selected_num = 1

# Fetch data from Snowflake
change_log_df = session.table("QNA_DB.pro.Question").toPandas()

# Display data in Streamlit
st.dataframe(change_log_df)
