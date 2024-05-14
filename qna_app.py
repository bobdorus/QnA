import streamlit as st
from snowflake.snowpark.functions import col 

"""
Question:
    # Q_NUM
    # Q_TEXT
    # TOPIC
    # CORRECT_ANSWER
    # COMMENT
"""

def review_mode(q_num, cnx):
    st.subheader("Question Details:")
    selected_num = int(q_num) if q_num and 0 < int(q_num) < 1100 else 1

    my_dataframe = session.table("qna.pro.question")

    # st.dataframe(data=my_dataframe, use_container_width=True)
    pd_df=my_dataframe.to_pandas() 

    st.write(selected_num)
    st.write(pd_df['Q_TEXT'])  # Assuming question_text is fetched from your database
    # st.dataframe(options_df)  # Assuming options_df is a DataFrame with options 
 

    

    # if st.button("Submit"):
    # if selected_option == correct_answer:
    #     st.success("Correct!")
    # else:
    #     st.error(f"Incorrect. The correct answer is: {correct_answer}")
    
    # with st.form("update_form"):
    # new_answer = st.text_input("Enter your answer")
    # new_topic = st.text_input("Enter your topic")
    # new_comment = st.text_area("Enter your comment (if any)")

    # if st.form_submit_button("Submit Update"):
    #     # Code to update the database with the new values
    #     st.success("Update submitted successfully!")

def seq_mode(q_num): 
    st.subheader("Question Details:")
    selected_num = int(q_num) if q_num and 0 < int(q_num) < 1100 else 1

    my_dataframe = session.table("qna.pro.question")

    # st.dataframe(data=my_dataframe, use_container_width=True)
    pd_df=my_dataframe.to_pandas() 

    st.write(selected_num)
    st.write(pd_df['Q_TEXT']) 

def test_mode(q_num): # randomize q value 
    st.subheader("Question Details:")
    selected_num = int(q_num) if q_num and 0 < int(q_num) < 1100 else 1

    my_dataframe = session.table("qna.pro.question")

    # st.dataframe(data=my_dataframe, use_container_width=True)
    pd_df=my_dataframe.to_pandas() 

    st.write(selected_num)
    st.write(pd_df['Q_TEXT']) 

st.title(":snowflake: Question & Answer App :snowflake:")
st.markdown("<style>div.block-container{text-align: center;}</style>", unsafe_allow_html=True) 
st.write(
        """Choose your question or leave it empty which will start with the 1st question.
        """
    )

q_num = st.text_input("Enter your question number:") 
cnx = st.connection('snowflake')
session = cnx.session()
mode = st.radio("Select Mode:", ("Review", "Sequence", "Test"))

if mode == "Review":
    review_mode(q_num, cnx)
elif mode == 'Sequence': 
    seq_mode(q_num, cnx)
elif mode == 'Test': 
    test_mode(q_num, cnx)

