import streamlit as st
from snowflake.snowpark.session import Session
from snowflake.snowpark.functions import col
import pandas as pd
import datetime
change_log_df = session.table("QNA_DB.pro.Question").filter(col("Q_NUM") == selected_num).toPandas()
st.dataframe(change_log_df)