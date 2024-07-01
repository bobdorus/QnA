import streamlit as st
from snowflake.snowpark.functions import col
import pandas as pd
import datetime
import uuid

MIN = 1
MAX = 1100

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

def seq_mode(session, seq_question_num):
    if 'completed_questions' not in st.session_state:
        st.session_state.completed_questions = 0
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    question_container = st.container()

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        prev_button = st.button(f"Prev ({seq_question_num - 1})", key=f"prev_{seq_question_num}") if seq_question_num > MIN else None
    with col2:
        st.empty()
    with col3:
        next_button = st.button(f"Next ({seq_question_num + 1})", key=f"next_{seq_question_num}") if seq_question_num < MAX else None

    if prev_button or next_button:
        if prev_button:
            st.session_state.seq_question_num -= 1
        if next_button:
            st.session_state.seq_question_num += 1
        st.experimental_rerun()  # Rerun only when moving to the next question

    with question_container:
        selected_options = question_display(session, seq_question_num)

    submit_button = st.button("Submit")

    if submit_button:
        st.session_state.completed_questions += 1
        correct_answer = session.table("QNA_DB.pro.question").filter(col("Q_NUM") == seq_question_num).select("CORRECT_ANSWER").collect()[0][0]
        user_answer = ', '.join([option[0] for option in selected_options])  # Take only the first letter of each option
        if user_answer != correct_answer:
            session_id = st.session_state.session_id
            attempt_num = st.session_state.completed_questions
            question_num = seq_question_num
            incorrect_answer = user_answer
            session.sql(f"""
                INSERT INTO Session_Metrics (session_id, attempt_num, question_num, incorrect_answer)
                VALUES ('{session_id}', {attempt_num}, {question_num}, '{incorrect_answer}')
            """).collect()
        else:
            st.session_state.score += 1
        st.experimental_rerun()  # Rerun only when moving to the next question

    st.text(f"Questions Completed: {st.session_state.completed_questions}")
    st.text(f"Score: {st.session_state.score}")

def reset_seq_state():
    st.session_state.seq_question_num = MIN
    st.session_state.completed_questions = 0
    st.session_state.score = 0
    st.session_state.selected_options = []  # Ensure selected options are cleared

st.title(":snowflake: Sequence Mode :snowflake:")
st.markdown("<style>div.block-container{text-align: center;}</style>", unsafe_allow_html=True)

# Initialize session state
if 'seq_question_num' not in st.session_state:
    reset_seq_state()

# Text input for question number
q_num = st.text_input("Enter your question number:", value="1", key="q_num_input")
change_question_button = st.button("Change Question")

# Connection to Snowflake
cnx = st.connection('snowflake')
session = cnx.session()

if change_question_button:
    try:
        q_num_int = int(q_num)
        if MIN <= q_num_int <= MAX:
            if q_num_int >= st.session_state.seq_question_num:
                st.session_state.seq_question_num = q_num_int
                st.experimental_rerun()
            else:
                st.warning(f"Please enter a question number not lower than the current display number ({st.session_state.seq_question_num}).")
        else:
            st.warning(f"Please enter a question number between {MIN} and {MAX}.")
    except ValueError:
        st.warning("Please enter a valid integer for the question number.")

seq_mode(session, st.session_state.seq_question_num)
