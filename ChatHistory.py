import streamlit as st
import json
import os
from datetime import datetime
import uuid

class ChatHistoryManager:
    def __init__(self, storage_dir="chat_history"): 
        self.storage_dir = storage_dir
        self.ensure_storage_directory()
    
    def ensure_storage_directory(self):
        """Create storage directory if it doesn't exist"""
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
    
    def generate_chat_id(self):
        """Generate a unique chat ID"""
        return str(uuid.uuid4())[:8]
    
    def get_chat_filename(self, chat_id):
        """Generate filename for a chat session"""
        return os.path.join(self.storage_dir, f"chat_{chat_id}.json")
    
    def save_chat_session(self, chat_id, messages, title=None):
        """Save current chat session to JSON file"""
        try:
            chat_data = {
                "chat_id": chat_id,
                "title": title or f"Chat {chat_id}",
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "messages": messages
            }
            
            filename = self.get_chat_filename(chat_id)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(chat_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            st.error(f"Error saving chat: {str(e)}")
            return False
    
    def load_chat_session(self, chat_id):
        """Load a specific chat session from JSON file"""
        try:
            filename = self.get_chat_filename(chat_id)
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            st.error(f"Error loading chat: {str(e)}")
            return None
    
    def get_all_chat_sessions(self):
        """Get list of all saved chat sessions"""
        try:
            chat_sessions = []
            for filename in os.listdir(self.storage_dir):
                if filename.startswith("chat_") and filename.endswith(".json"):
                    chat_id = filename.replace("chat_", "").replace(".json", "")
                    chat_data = self.load_chat_session(chat_id)
                    if chat_data:
                        chat_sessions.append({
                            "chat_id": chat_id,
                            "title": chat_data.get("title", f"Chat {chat_id}"),
                            "created_at": chat_data.get("created_at"),
                            "last_updated": chat_data.get("last_updated"),
                            "message_count": len(chat_data.get("messages", []))
                        })
            
            # Sort by last updated (most recent first)
            chat_sessions.sort(key=lambda x: x["last_updated"], reverse=True)
            return chat_sessions
        except Exception as e:
            st.error(f"Error getting chat sessions: {str(e)}")
            return []
    
    def delete_chat_session(self, chat_id):
        """Delete a specific chat session"""
        try:
            filename = self.get_chat_filename(chat_id)
            if os.path.exists(filename):
                os.remove(filename)
                return True
            return False
        except Exception as e:
            st.error(f"Error deleting chat: {str(e)}")
            return False
    
    def export_chat_to_json(self, chat_id):
        """Export a chat session as downloadable JSON"""
        chat_data = self.load_chat_session(chat_id)
        if chat_data:
            return json.dumps(chat_data, indent=2, ensure_ascii=False)
        return None

# Initialize the chat history manager
@st.cache_resource
def get_chat_manager():
    return ChatHistoryManager()

def init_chat():
    """Initialize chat session"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "current_chat_id" not in st.session_state:
        st.session_state.current_chat_id = None
    
    if "chat_manager" not in st.session_state:
        st.session_state.chat_manager = get_chat_manager()

def add_message(role, content):
    """Add message to current session"""
    st.session_state.messages.append({"role": role, "content": content})
    
    # Auto-save every few messages
    if len(st.session_state.messages) % 5 == 0:
        auto_save_current_chat()

def display_chat():
    """Display current chat messages"""
    for message in st.session_state.messages:
        avatar_path = (
            'https://raw.githubusercontent.com/vennDiagramm/admissionBot/refs/heads/main/Icons/student.ico'
            if message["role"] == "user" else
            'https://raw.githubusercontent.com/vennDiagramm/admissionBot/refs/heads/main/Icons/mapua_icon_83e_icon.ico'
        )
        with st.chat_message(message["role"], avatar=avatar_path):
            st.markdown(message["content"])

def start_new_chat():
    """Start a new chat session"""
    # Save current chat if it has messages
    if st.session_state.messages:
        save_current_chat()
    
    # Reset for new chat
    st.session_state.messages = []
    st.session_state.current_chat_id = st.session_state.chat_manager.generate_chat_id()

def save_current_chat(title=None):
    """Save current chat session"""
    if st.session_state.messages and st.session_state.current_chat_id:
        return st.session_state.chat_manager.save_chat_session(
            st.session_state.current_chat_id,
            st.session_state.messages,
            title
        )
    return False

def auto_save_current_chat():
    """Auto-save current chat (creates new chat ID if none exists)"""
    if not st.session_state.current_chat_id:
        st.session_state.current_chat_id = st.session_state.chat_manager.generate_chat_id()
    
    if st.session_state.messages:
        st.session_state.chat_manager.save_chat_session(
            st.session_state.current_chat_id,
            st.session_state.messages
        )

def load_chat_session(chat_id):
    """Load a specific chat session"""
    chat_data = st.session_state.chat_manager.load_chat_session(chat_id)
    if chat_data:
        st.session_state.messages = chat_data.get("messages", [])
        st.session_state.current_chat_id = chat_id
        return True
    return False

def get_chat_sessions():
    """Get all available chat sessions"""
    return st.session_state.chat_manager.get_all_chat_sessions()

def delete_chat_session(chat_id):
    """Delete a specific chat session"""
    return st.session_state.chat_manager.delete_chat_session(chat_id)

def export_chat_session(chat_id):
    """Export chat session as JSON"""
    return st.session_state.chat_manager.export_chat_to_json(chat_id)