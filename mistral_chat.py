from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import streamlit as st
import os

st.title("Mistral Chat")

api_key = os.environ["MISTRAL_API_KEY"]
client = MistralClient(api_key=api_key)

# Initialize the model in session state if it's not already set
if "mistral_model" not in st.session_state:
    st.session_state["mistral_model"] = 'mistral-tiny'

# Always display the dropdown
st.session_state["mistral_model"] = st.selectbox('Select a model', ('mistral-tiny', 'mistral-small', 'mistral-medium'), index=0, key=st.session_state["mistral_model"])

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message.role):  # Use dot notation here
        st.markdown(message.content)  # And here

if prompt := st.chat_input("What is up?"):
    new_message = ChatMessage(role="user", content=prompt)
    st.session_state.messages.append(new_message)
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for response in client.chat_stream(
            model=st.session_state["mistral_model"],
            messages=st.session_state.messages,  # Pass the entire messages list
        ):
            full_response += (response.choices[0].delta.content or "")
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append(ChatMessage(role="assistant", content=full_response))