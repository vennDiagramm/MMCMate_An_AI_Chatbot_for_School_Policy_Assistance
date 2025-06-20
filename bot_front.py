import bot_back as back
from ChatHistory import (
    init_chat, add_message, display_chat, start_new_chat, 
    save_current_chat, load_chat_session, get_chat_sessions, 
    delete_chat_session, export_chat_session
)
import streamlit as st
from datetime import datetime
import os

# Function to handle GUI
def main():
    # Streamlit set up
    st.set_page_config(page_title="MMCMate", page_icon="Icons/mapua_icon_83e_icon.ico")
    st.title("MMCMate :books:")
    st.write("Hello, how may I help you?")

    # Initialize chat system
    init_chat()

    # Path to the database
    db_path = os.path.join("database", "databasefinalnjud.db")

    # --- Sidebar (For chat history) ---
    with st.sidebar:
        st.title("📜 Chat History")
        
        # -- Chat management buttons --
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🆕 New Chat", use_container_width=True):
                start_new_chat()
                st.rerun()
        
        with col2:
            if st.button("💾 Save Chat", use_container_width=True):
                if st.session_state.messages:
                    # Option to add a custom title
                    if "show_title_input" not in st.session_state:
                        st.session_state.show_title_input = True
                else:
                    st.warning("No messages to save!")
        
        # -- Title input for saving --
        if getattr(st.session_state, 'show_title_input', False):
            title = st.text_input("Chat Title (optional):", key="chat_title")
            col_save, col_cancel = st.columns(2)
            with col_save:
                if st.button("Save", key="save_confirm"):
                    if save_current_chat(title if title else None):
                        st.success("Chat saved!")
                        st.session_state.show_title_input = False
                        st.rerun()
                    else:
                        st.error("Failed to save chat!")
            with col_cancel:
                if st.button("Cancel", key="save_cancel"):
                    st.session_state.show_title_input = False
                    st.rerun()
        
        st.divider()
        
        # -- Display saved chats --
        saved_chats = get_chat_sessions()
        
        if saved_chats:
            st.subheader("💬 Saved Conversations")
            
            for chat in saved_chats:
                with st.expander(f"📝 {chat['title']}", expanded=False):
                    st.write(f"**Messages:** {chat['message_count']}")
                    st.write(f"**Created:** {datetime.fromisoformat(chat['created_at']).strftime('%Y-%m-%d %H:%M')}")
                    
                    # Action buttons for each chat
                    col_load, col_export, col_delete = st.columns(3)
                    
                    with col_load:
                        if st.button("📂 Load", key=f"load_{chat['chat_id']}"):
                            if load_chat_session(chat['chat_id']):
                                st.success("Chat loaded!")
                                st.rerun()
                            else:
                                st.error("Failed to load chat!")
                    
                    with col_export:
                        json_data = export_chat_session(chat['chat_id'])
                        if json_data:
                            st.download_button(
                                label="📥 JSON",
                                data=json_data,
                                file_name=f"chat_{chat['chat_id']}.json",
                                mime="application/json",
                                key=f"export_{chat['chat_id']}"
                            )
                    
                    with col_delete:
                        if st.button("🗑️ Del", key=f"delete_{chat['chat_id']}"):
                            if delete_chat_session(chat['chat_id']):
                                st.success("Chat deleted!")
                                st.rerun()
                            else:
                                st.error("Failed to delete chat!")
        
        # Current session info
        st.divider()
        if st.session_state.messages:
            st.write(f"**Current Session:** {len(st.session_state.messages)} messages")
            if hasattr(st.session_state, 'current_chat_id') and st.session_state.current_chat_id:
                st.write(f"**Chat ID:** {st.session_state.current_chat_id}")
        else:
            st.info("Start a conversation to see session info!")

    # --- Main chat area ---
    # Only display existing chat history, new messages are handled in handle_conversation
    display_chat()
    
    # Handle new messages (this will add and display new messages)
    back.handle_conversation(db_path)

# To run main
if __name__ == "__main__":
    main()