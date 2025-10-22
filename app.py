import streamlit as st
from chatbot import handle_message
from conversation import conversation_history

st.set_page_config(page_title="🍽️ Restaurant Chatbot", page_icon="🍴")

st.title("🍽️ Restaurant Chatbot")

# Initialize user input
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# Input text box
st.session_state.user_input = st.text_input("You:", st.session_state.user_input, key="input")

# Send button
if st.button("Send") and st.session_state.user_input.strip():
    user_message = st.session_state.user_input.strip()
    reply = handle_message(user_message)
    st.session_state.user_input = ""  # clear input after sending

# Display conversation history
st.text_area(
    "Conversation",
    value="\n".join([f"{m['role'].capitalize()}: {m['message']}" for m in conversation_history]),
    height=400
)
