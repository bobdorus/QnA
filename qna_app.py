import streamlit as st
from snowflake.snowpark.functions import col
import pandas as pd
import datetime

MIN = 1
MAX = 1099

TOPICS = [
    "Overview and Architecture",
    "Virtual Warehouse",
    "Storage and Protection",
    "Data Loading and Unloading",
    "Semi-structured Data",
    "Snowflake Account and Security",
    "Snowflake Performance and Tuning"
]

def get_option_selector(session, q_num):
    options_df = session.table("qna.pro.options").filter(col("Q_NUM") == q_num).toPandas()
    correct_answer = session.table("qna.pro.question").filter(col("Q_NUM") == q_num).select("CORRECT_ANSWER").collect()[0][0]

    options_df["TEXT"] = options_df["TEXT"].str.strip()  # Remove leading and trailing spaces

    if len(correct_answer) == 1:
        selected_option = st.radio("Select an option", [f"{option}: {text}" for option, text in zip(options_df["OPTION"], options_df["TEXT"])])
        selected_options = [selected_option]
    else:
        selected_options = st.multiselect("Select one or more options", [f"{option}: {text}" for option, text in zip(options_df["OPTION"], options_df["TEXT"])])

    return selected_options

def question_display(session, q_num):
    st.subheader("Question Details:")

    my_dataframe = session.table("qna.pro.question").filter(col("Q_NUM") == q_num)
    if my_dataframe.count() == 0:
        st.warning("Question not found.")
        return

    pd_df = my_dataframe.toPandas()
    st.markdown(f'<b style="font-size:24px; color:#42f587;">NO. {q_num}</b>', unsafe_allow_html=True)
    st.write(pd_df['Q_TEXT'][0])

    selected_options = get_option_selector(session, q_num)

    return selected_options

def get_current_user_id(session):
    user_id_query = session.sql("SELECT CURRENT_USER()").collect()
    return user_id_query[0][0]

def update_section(session, selected_num, selected_options, correct_answer):
    st.subheader("Update the answer for question:")
    st.text("Selected Options:")
    for option in selected_options:
        st.write(option)

    user_answer = ', '.join([option[0] for option in selected_options])  # Take only the first letter of each option
    st.text(f"Current Correct Answer: {correct_answer}")

    user_topic = st.multiselect("Enter your topic (if any):", TOPICS, key="user_topic")
    user_topic = ', '.join(user_topic)
    user_comment = st.text_input("Enter your comment (if any):", "", key="user_comment")
    user_id = get_current_user_id(session)
    st.text(f"User ID: {user_id}")

    submit_button = st.button("Submit Update")

    if submit_button:
        try:
            # Check if it's the first update
            corrected_answer_query = session.table("QNA.pro.Question_Corrected").filter(col("Q_NUM") == selected_num).select("CORRECT_ANSWER")
            if corrected_answer_query.count() > 0:
                correct_answer_old = corrected_answer_query.collect()[0][0]
            else:
                correct_answer_old = correct_answer

            # Update question_corrected table
            session.table("QNA.pro.Question_Corrected").filter(col("Q_NUM") == selected_num).update(
                {"CORRECT_ANSWER": user_answer, "TOPIC": user_topic, "COMMENT": user_comment}
            ).collect()

            # Log the update in the UPDATE_LOG_TBL
            session.table("QNA.pro.UPDATE_LOG_TBL").insert(
                values={
                    "Q_NUM": selected_num,
                    "Q_TIMESTAMP": datetime.datetime.now(),
                    "Q_TEXT": session.table("QNA.pro.question").filter(col("Q_NUM") == selected_num).select("Q_TEXT").collect()[0][0],
                    "USER_ID": user_id,
                    "CORRECT_ANSWER_OLD": correct_answer_old,
                    "CORRECT_ANSWER_NEW": user_answer,
                    "COMMENT": user_comment
                }
            ).collect()

            st.success("Update successful!")
        except Exception as e:
            st.error(f"Update failed: {str(e)}")

    # Display change log
    st.subheader("Change Log")
    change_log_df = session.table("QNA.pro.UPDATE_LOG_TBL").filter(col("Q_NUM") == selected_num).toPandas()
    st.dataframe(change_log_df)

def review_mode(session):
    selected_num = st.session_state.selected_num

    question_container = st.container()

    with question_container:
        selected_options = question_display(session, selected_num)

        correct_answer = session.table("qna.pro.question").filter(col("Q_NUM") == selected_num).select("CORRECT_ANSWER").collect()[0][0]
        formatted_correct_answer = ""
        # Format the correct answer
        if len(correct_answer) > 1:
            formatted_correct_answer = ', '.join([f"<b>{char}</b>" for char in correct_answer])
        else:
            formatted_correct_answer = f"<b>{correct_answer}</b>"
        
        st.subheader("Correct Answer:")
        st.markdown(formatted_correct_answer, unsafe_allow_html=True)

        # Initialize buttons to None
        prev_button = None
        next_button = None

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if selected_num > MIN:
                prev_button = st.button(f"Prev ({selected_num - 1})", key=f"prev_{selected_num}")
        with col2:
            st.empty()
        with col3:
            if selected_num < MAX:
                next_button = st.button(f"Next ({selected_num + 1})", key=f"next_{selected_num}")

        if prev_button or next_button:
            if prev_button:
                st.session_state.selected_num -= 1
            if next_button:
                st.session_state.selected_num += 1
            st.session_state.user_topic = []
            st.session_state.user_comment = ""
            st.experimental_rerun()

        update_section(session, selected_num, selected_options, formatted_correct_answer)

def seq_mode(session):
    pass

def test_mode(session):
    pass

st.title(":snowflake: Question & Answer App :snowflake:")
st.markdown("<style>div.block-container{text-align: center;}</style>", unsafe_allow_html=True)
st.write("Choose your question or leave it empty to start with the 1st question.")

q_num = st.text_input("Enter your question number:", value="1", key="q_num_input")
change_question_button = st.button("Change Question")

if change_question_button:
    try:
        q_num_int = int(q_num)
        if MIN <= q_num_int <= MAX:
            st.session_state.selected_num = q_num_int
            st.session_state.user_topic = []
            st.session_state.user_comment = ""
            st.experimental_rerun()
        else:
            st.warning(f"Please enter a question number between {MIN} and {MAX}.")
    except ValueError:
        st.warning("Please enter a valid integer for the question number.")

cnx = st.connection('snowflake')
session = cnx.session()

if 'selected_num' not in st.session_state:
    st.session_state.selected_num = MIN

mode = st.radio("Select Mode:", ("Review", "Sequence", "Test"))

if mode == "Review":
    review_mode(session)
elif mode == "Sequence":
    seq_mode(session)
elif mode == "Test":
    test_mode(session)
