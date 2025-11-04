import streamlit as st
from bot import respond_to_user

st.set_page_config(page_title="Restaurant Chatbot", page_icon="🍽️", layout="centered")

st.title("ServeSmart: Your Smart Dining Companion")
st.caption("Ask me anything about our restaurant - menu, offers, booking, or timings!")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Type your message here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    response = respond_to_user(prompt)

    st.session_state.messages.append({"role": "assistant", "content": response})

    with st.chat_message("assistant"):
        st.markdown(response)

        if "menu" in prompt.lower():
            try:
                with open("menu.pdf", "rb") as file:
                    st.download_button(
                        label="Click here to download",
                        data=file,
                        file_name="menu.pdf",
                        mime="application/pdf"
                    )
            except FileNotFoundError:
                st.warning(" Menu file not found. Please place 'menu.pdf' in the same folder.")
