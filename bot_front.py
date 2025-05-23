import bot_back as back
from ChatHistory import init_chat, add_message, display_chat
import streamlit as st

# Function to handle GUI
def main():
    # Streamlit set up
    st.set_page_config(page_title="MMCMate", page_icon="Icons/mapua_icon_83e_icon.ico")
    st.title("MMCMate :books:")
    st.write("Hello, how may I help you?")

    # Provide the path to your database file here
    db_path = r"database\databasefinalnjud.db" #

    # --- Sidebar (Chat History Overview) ---
    with st.sidebar:
        st.title("📜 Chat History")
        if "messages" in st.session_state and st.session_state.messages:
            for idx, msg in enumerate(st.session_state.messages):
                label = f"🧑‍🎓 {msg['content'][:30]}..." if msg["role"] == "user" else f"🤖 {msg['content'][:30]}..."
                with st.expander(label):
                    st.markdown(msg["content"])
        else:
            st.info("No chat history yet!")

    # --- Handle main chat conversation ---
    back.handle_conversation(db_path)


# To run main
if __name__ == "__main__":
    main()
