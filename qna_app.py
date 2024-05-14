import streamlit as st
from snowflake.snowpark.functions import col
import pandas as pd
import random

"""
Question:
    # Q_NUM
    # Q_TEXT
    # TOPIC
    # CORRECT_ANSWER
    # COMMENT
"""


def review_mode(q_num, session):
    with st.container():  # Creates a container for Review mode
        st.subheader("Question Details:")
        selected_num = int(q_num) if q_num and 0 < int(q_num) < 1100 else 1

        my_dataframe = session.table("qna.pro.question").filter(col("Q_NUM") == selected_num)

        # Handling missing question
        if my_dataframe.count() == 0:
            st.warning("Question not found.")
            return  # Exit the function to prevent errors

        pd_df = my_dataframe.toPandas()
        st.write(selected_num)
        st.write(pd_df['Q_TEXT'][0])

        options_df = session.table("qna.pro.options").filter(col("Q_NUM") == selected_num).toPandas()
        st.dataframe(options_df)

def seq_mode(q_num, session):
    with st.container():  # Creates a container for Sequence mode
        st.write("implement later")

def test_mode(q_num, session):
    with st.container():  # Creates a container for Test mode
        st.write("implement later")

# Main App
st.title(":snowflake: Question & Answer App :snowflake:")
st.markdown("<style>div.block-container{text-align: center;}</style>", unsafe_allow_html=True)
st.write("Choose your question or leave it empty to start with the 1st question.")

q_num = st.text_input("Enter your question number:")

# Snowflake Connection (outside the mode selection)
cnx = st.connection('snowflake')
session = cnx.session()

mode = st.radio("Select Mode:", ("Review", "Sequence", "Test"))

if mode == "Review":
    review_mode(q_num, session)
elif mode == "Sequence":
    seq_mode(q_num, session)
elif mode == "Test":
    test_mode(q_num, session)