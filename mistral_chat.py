from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import streamlit as st
import os

st.title("Mistral Chat")

# Function to reset the state
def reset_state():
    for key in st.session_state:
        del st.session_state[key]

# Get the API key from the environment variables or the user
api_key = os.getenv("MISTRAL_API_KEY")
if not api_key:
    if "api_key" not in st.session_state:
        st.session_state["api_key"] = st.text_input("Enter your API key", type="password")
    api_key = st.session_state["api_key"]
else:
    if expected_password := os.getenv("PASSWORD"):
        password = st.text_input("What's the secret password?", type="password")
        # Check if the entered key matches the expected password
        if password != expected_password:
            api_key = ''
            st.error("Unauthorized access.")
            reset_state()  # This line will reset the script
        else:
            api_key = os.getenv("MISTRAL_API_KEY")

client = MistralClient(api_key=api_key)

# Initialize the model in session state if it's not already set
if "mistral_model" not in st.session_state:
    st.session_state["mistral_model"] = 'mistral-tiny'

# Always display the dropdown
model_options = ('mistral-tiny', 'mistral-small', 'mistral-medium')
st.session_state["mistral_model"] = st.selectbox('Select a model', model_options, index=model_options.index(st.session_state["mistral_model"]), key="model_select")

# Add system prompt input
if "system_prompt" not in st.session_state:
    st.session_state["system_prompt"] = ''
st.text_input('System Prompt', value=st.session_state["system_prompt"], key="system_prompt")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Add system prompt as a ChatMessage if it doesn't exist
if st.session_state["system_prompt"] and not any(message.role == "system" for message in st.session_state.messages):
    st.session_state.messages.insert(0, ChatMessage(role="system", content=st.session_state["system_prompt"]))

for message in st.session_state.messages:
    if message.role != "system":  # Skip system messages for UI
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
