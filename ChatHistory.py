import streamlit as st

def init_chat():
    if "messages" not in st.session_state:
        st.session_state.messages = []

def add_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})

def display_chat():
    for message in st.session_state.messages:
        avatar_path = (
            'https://raw.githubusercontent.com/vennDiagramm/admissionBot/refs/heads/main/Icons/student.ico'
            if message["role"] == "user" else
            'https://raw.githubusercontent.com/vennDiagramm/admissionBot/refs/heads/main/Icons/mapua_icon_83e_icon.ico'
        )
        with st.chat_message(message["role"], avatar=avatar_path):
            st.markdown(message["content"])
 