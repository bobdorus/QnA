import streamlit as st
from snowflake.snowpark.functions import col
import pandas as pd
import random


def get_option_selector(session, q_num):
    options_df = session.table("qna.pro.options").filter(col("Q_NUM") == q_num).toPandas()
    correct_answer_len = len(session.table("qna.pro.question").filter(col("Q_NUM") == q_num).select("CORRECT_ANSWER").collect()[0][0])

    if correct_answer_len == 1:
        # Single select
        selected_option = st.radio("Select an option", [f"{option.upper()}: {text}" for option, text in zip(options_df["OPTION"], options_df["TEXT"])])
        selected_options = [selected_option]
    else:
        # Multiple select
        selected_options = st.multiselect("Select one or more options", [f"{option.upper()}: {text}" for option, text in zip(options_df["OPTION"], options_df["TEXT"])])

    return selected_options


def question_display(q_num, session):
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

    selected_options = get_option_selector(session, selected_num)

    # Display the selected options
    st.write("Selected options:")
    for option in selected_options:
        st.write(option)

    return selected_options



def review_mode(q_num, session):
    with st.container():  # Creates a container for Review mode
        question_display(q_num, session)
        selected_num = int(q_num) if q_num and 0 < int(q_num) < 1100 else 1

        # Get the correct answer from the question table
        correct_answer = session.table("qna.pro.question").filter(col("Q_NUM") == selected_num).select(col("CORRECT_ANSWER")).collect()[0][0]

        # Display the correct answer
        st.subheader("Correct Answer:")
        st.write(correct_answer)

        # Get user's answer and topic input
        user_answer = st.text_input("Enter your answer:", "")
        user_topic = st.text_input("Enter your topic (if any):", "")
        user_comment = st.text_input("Enter your comment (if any):", "")

        # Submit button
        if st.button("Submit Update"):
            # Update the question table with user's answer, topic, and comment
            session.table("qna.pro.question").update(
                values={"CORRECT_ANSWER": user_answer, "TOPIC": user_topic, "COMMENT": user_comment},
                filter=col("Q_NUM") == selected_num
            ).collect()

            # Update the options table with user's answer
            session.table("qna.pro.options").update(
                values={"OPTION": user_answer},
                filter=(col("Q_NUM") == selected_num) & (col("OPTION") == correct_answer)
            ).collect()

            st.success("Update successful!")

def seq_mode(q_num, session):
    with st.container():  # Creates a container for Sequence mode
        question_display(q_num, session)

def test_mode(q_num, session):
    with st.container():  # Creates a container for Test mode
        question_display(q_num, session)

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