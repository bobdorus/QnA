import streamlit as st
from snowflake.snowpark.functions import col
import pandas as pd

MIN = 1
MAX = 1099

def get_option_selector(session, q_num):
    options_df = session.table("qna.pro.options").filter(col("Q_NUM") == q_num).toPandas()
    correct_answer_len = len(session.table("qna.pro.question").filter(col("Q_NUM") == q_num).select("CORRECT_ANSWER").collect()[0][0])

    if correct_answer_len == 1:
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

    st.write("Selected options:")
    for option in selected_options:
        st.write(option)

def review_mode(session):
    selected_num = st.session_state.selected_num

    question_container = st.container()

    with question_container:
        question_display(session, selected_num)

        correct_answer = session.table("qna.pro.question").filter(col("Q_NUM") == selected_num).select(col("CORRECT_ANSWER")).collect()[0][0]

        st.subheader("Correct Answer:")
        st.write(correct_answer)

        col1, col2, col3 = st.columns([1, 1, 2])
        prev_button = next_button = None
        with col1:
            if selected_num > MIN:
                prev_button = st.button(f"Previous question ({selected_num - 1})", key=f"prev_{selected_num}")
        with col2:
            if selected_num < MAX:
                next_button = st.button(f"Next question ({selected_num + 1})", key=f"next_{selected_num}")

        empty_col1, empty_col2, empty_col3 = st.columns([1, 1, 2])
        with empty_col1:
            st.empty()
        with empty_col2:
            st.empty()

        user_answer = st.text_input("Enter your answer:", "")
        user_topic = st.text_input("Enter your topic (if any):", "")
        user_comment = st.text_input("Enter your comment (if any):", "")

        submit_button = st.button("Submit Update")

        if prev_button:
            st.session_state.selected_num -= 1
            st.experimental_rerun()
        if next_button:
            st.session_state.selected_num += 1
            st.experimental_rerun()
        if submit_button:
            try:
                session.table("qna.pro.question").update(
                    values={"CORRECT_ANSWER": user_answer, "TOPIC": user_topic, "COMMENT": user_comment},
                    filter=col("Q_NUM") == selected_num
                ).collect()

                session.table("qna.pro.options").update(
                    values={"OPTION": user_answer},
                    filter=(col("Q_NUM") == selected_num) & (col("OPTION") == correct_answer)
                ).collect()

                st.success("Update successful!")
            except Exception as e:
                st.error(f"Update failed: {str(e)}")

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
